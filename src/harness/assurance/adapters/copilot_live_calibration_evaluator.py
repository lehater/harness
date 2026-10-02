#!/usr/bin/env python3
"""GitHub Copilot CLI adapter for blinded live semantic calibration."""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

CLI_ENV = "HARNESS_COPILOT_EXECUTABLE"
DEFAULT_CLI = "copilot"
_ALLOWED_CASE_FIELDS = {"case_request_id", "source", "target", "relation"}
_VERSION_RE = re.compile(r"(?<!\d)(\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?)(?!\d)")


def _require_mapping(value: Any, where: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{where} must be a mapping")
    return value


def _model_payload(request: dict[str, Any]) -> dict[str, Any]:
    if request.get("version") != 1:
        raise ValueError("evaluator request version must be 1")
    if request.get("kind") != "harness-live-semantic-evaluator-request":
        raise ValueError("unexpected evaluator request kind")

    protocol = _require_mapping(request.get("protocol"), "protocol")
    instruction = protocol.get("instruction")
    if not isinstance(instruction, str) or not instruction:
        raise ValueError("protocol instruction must be a non-empty string")

    cases = request.get("cases")
    if not isinstance(cases, list) or not cases:
        raise ValueError("evaluator request requires cases")

    blinded: list[dict[str, Any]] = []
    for index, case in enumerate(cases):
        case = _require_mapping(case, f"case {index}")
        if set(case) != _ALLOWED_CASE_FIELDS:
            raise ValueError(
                f"case {index} must contain only blinded semantic fields"
            )
        blinded.append({key: case[key] for key in (
            "case_request_id", "source", "target", "relation"
        )})

    return {
        "protocol_instruction": instruction,
        "cases": blinded,
        "response_contract": {
            "version": 1,
            "kind": "harness-live-semantic-evaluator-response",
            "results": {
                "one_result_per_input_case": True,
                "fields": {
                    "case_request_id": "copy exactly from the input case",
                    "status": ["ACCEPTED", "REJECTED"],
                    "rationale": "optional brief audit rationale; no private chain-of-thought",
                    "findings": "optional JSON array",
                },
            },
            "output": "Return exactly one JSON object and no markdown or surrounding text.",
        },
    }


def _prompt(request: dict[str, Any]) -> str:
    payload = _model_payload(request)
    return (
        "Perform only the semantic classification described by this JSON input. "
        "Do not infer hidden labels or use external tools. "
        "Return exactly the requested JSON response object.\n"
        + json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    )


def _parse_model_response(raw: str) -> dict[str, Any]:
    try:
        response = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError("Copilot response must be strict JSON") from exc
    if not isinstance(response, dict):
        raise ValueError("Copilot response must be a JSON object")
    if response.get("version") != 1:
        raise ValueError("Copilot response version must be 1")
    if response.get("kind") != "harness-live-semantic-evaluator-response":
        raise ValueError("unexpected Copilot response kind")
    if not isinstance(response.get("results"), list):
        raise ValueError("Copilot response results must be a list")
    return response


def _parse_copilot_jsonl(raw: str) -> tuple[str, str | None]:
    messages: list[str] = []
    resolved_model: str | None = None
    for line in raw.splitlines():
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError("Copilot JSONL contained a non-JSON line") from exc
        if not isinstance(event, dict):
            raise ValueError("Copilot JSONL event must be a JSON object")
        data = event.get("data")
        if not isinstance(data, dict):
            data = {}
        event_type = event.get("type")
        if event_type == "assistant.message":
            content = data.get("content")
            if isinstance(content, str) and content.strip():
                messages.append(content.strip())
        elif event_type == "assistant.turn_start":
            model = data.get("model")
            if isinstance(model, str) and model:
                resolved_model = model
        elif event_type == "session.shutdown":
            model = data.get("currentModel")
            if isinstance(model, str) and model:
                resolved_model = model

    if len(messages) != 1:
        raise ValueError(
            "Copilot JSONL must contain exactly one non-empty assistant message"
        )
    return messages[0], resolved_model


def _resolved_model_from_session(home: Path) -> str | None:
    resolved_model: str | None = None
    for source in (home / ".copilot").rglob("events.jsonl"):
        for line in source.read_text(encoding="utf-8").splitlines():
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            if not isinstance(event, dict):
                continue
            data = event.get("data")
            if not isinstance(data, dict):
                continue
            event_type = event.get("type")
            if event_type == "assistant.turn_start":
                model = data.get("model")
                if isinstance(model, str) and model:
                    resolved_model = model
            elif event_type == "session.shutdown":
                model = data.get("currentModel")
                if isinstance(model, str) and model:
                    resolved_model = model
    return resolved_model


def _sanitized_env(home: Path) -> dict[str, str]:
    allowed = (
        "PATH",
        "GITHUB_TOKEN",
        "COPILOT_GITHUB_TOKEN",
        "GH_TOKEN",
        "HTTPS_PROXY",
        "HTTP_PROXY",
        "NO_PROXY",
        "SSL_CERT_FILE",
        "NODE_EXTRA_CA_CERTS",
    )
    env = {key: os.environ[key] for key in allowed if key in os.environ}
    env.update(
        {
            "HOME": str(home),
            "COPILOT_HOME": str(home / ".copilot"),
            "XDG_CONFIG_HOME": str(home / ".config"),
            "XDG_CACHE_HOME": str(home / ".cache"),
            "COPILOT_AUTO_UPDATE": "false",
            "COPILOT_MCP_TOOL_CACHE": "false",
        }
    )
    return env


def _observed_cli_version(executable: str, env: dict[str, str]) -> str:
    completed = subprocess.run(
        [executable, "--version"],
        text=True,
        capture_output=True,
        check=False,
        env=env,
        timeout=15,
    )
    if completed.returncode != 0:
        raise RuntimeError(
            f"Copilot CLI version probe failed with exit {completed.returncode}"
        )
    rendered = f"{completed.stdout}\n{completed.stderr}"
    match = _VERSION_RE.search(rendered)
    if not match:
        raise RuntimeError("Copilot CLI version was not parseable")
    return match.group(1)


def _invoke_copilot(
    request: dict[str, Any],
) -> tuple[str, dict[str, Any]]:
    evaluator = _require_mapping(request.get("evaluator"), "evaluator")
    if evaluator.get("provider") != "github-copilot":
        raise ValueError("Copilot adapter requires provider=github-copilot")

    model = evaluator.get("model")
    if not isinstance(model, str) or not model:
        raise ValueError("evaluator model must be a non-empty string")

    configuration = _require_mapping(
        evaluator.get("configuration"),
        "evaluator configuration",
    )
    requested_model = configuration.get("requested_model")
    if requested_model != model:
        raise ValueError("requested_model must equal evaluator model")

    expected_cli_version = configuration.get("copilot_cli_version")
    if not isinstance(expected_cli_version, str) or not expected_cli_version:
        raise ValueError("copilot_cli_version must be a non-empty string")

    timeout_seconds = configuration.get("provider_timeout_seconds", 150)
    if not isinstance(timeout_seconds, (int, float)) or timeout_seconds <= 0:
        raise ValueError("provider_timeout_seconds must be positive")

    executable = os.environ.get(CLI_ENV, DEFAULT_CLI)
    session_id = str(uuid.uuid4())

    with tempfile.TemporaryDirectory(
        prefix="harness-copilot-live-calibration-"
    ) as temp:
        root = Path(temp)
        home = root / "home"
        work = root / "work"
        home.mkdir()
        work.mkdir()
        env = _sanitized_env(home)
        observed_cli_version = _observed_cli_version(executable, env)
        if observed_cli_version != expected_cli_version:
            raise RuntimeError(
                "Copilot CLI version mismatch: "
                f"expected {expected_cli_version}, observed {observed_cli_version}"
            )

        command = [
            executable,
            "-p",
            _prompt(request),
            f"--model={model}",
            "--output-format=json",
            f"--session-id={session_id}",
            "--stream=off",
            "--no-ask-user",
            "--available-tools=ask_user",
            "--disable-builtin-mcps",
            "--no-custom-instructions",
            "--no-auto-update",
            "--no-remote",
            "--no-remote-export",
            "--no-experimental",
        ]
        completed = subprocess.run(
            command,
            cwd=work,
            env=env,
            text=True,
            capture_output=True,
            check=False,
            timeout=float(timeout_seconds),
        )
        if completed.returncode != 0:
            stderr = completed.stderr.strip().replace("\n", " ")[:2000]
            raise RuntimeError(
                f"Copilot CLI failed with exit {completed.returncode}: {stderr}"
            )

        model_response, stream_model = _parse_copilot_jsonl(completed.stdout)
        session_model = _resolved_model_from_session(home)
        resolved_model = session_model or stream_model
        if not resolved_model:
            raise RuntimeError("Copilot resolved model was not observable")

    provenance = {
        "version": 1,
        "kind": "harness-github-copilot-execution-provenance",
        "provider": "github-copilot",
        "requested_model": model,
        "resolved_model": resolved_model,
        "resolved_model_source": "copilot-cli-session-events",
        "observed_cli_version": observed_cli_version,
        "client_session_id": session_id,
        "completed_at": datetime.now(timezone.utc).isoformat(),
        "execution": {
            "fresh_copilot_home": True,
            "isolated_working_directory": True,
            "custom_instructions_disabled": True,
            "builtin_mcps_disabled": True,
            "remote_session_disabled": True,
            "available_tools": ["ask_user"],
            "ask_user_disabled": True,
        },
    }
    return model_response, provenance


def evaluate_request(request: dict[str, Any]) -> dict[str, Any]:
    # Constructing this payload is also the fail-closed proof that canonical
    # labels and label-bearing case ids never reach the model prompt.
    _model_payload(request)
    raw, provenance = _invoke_copilot(request)
    response = _parse_model_response(raw)
    response["provenance"] = provenance
    return response


def main() -> int:
    try:
        request = json.load(sys.stdin)
        if not isinstance(request, dict):
            raise ValueError("stdin request must be a JSON object")
        response = evaluate_request(request)
        json.dump(response, sys.stdout, ensure_ascii=False)
        sys.stdout.write("\n")
        return 0
    except Exception as exc:
        print(
            f"Copilot live calibration adapter failed: "
            f"{exc.__class__.__name__}: {exc}",
            file=sys.stderr,
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    'Any',
    'CLI_ENV',
    'DEFAULT_CLI',
    'Path',
    '_model_payload',
    '_parse_copilot_jsonl',
    '_parse_model_response',
    'annotations',
    'datetime',
    'evaluate_request',
    'json',
    'main',
    'os',
    're',
    'subprocess',
    'sys',
    'tempfile',
    'timezone',
    'uuid',
]
