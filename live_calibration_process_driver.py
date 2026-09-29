#!/usr/bin/env python3
"""Scenario Suite external-process adapter for live semantic calibration."""
from __future__ import annotations

import copy
import hashlib
import json
import os
import subprocess
from pathlib import Path
from typing import Any

from live_calibration import (
    build_live_calibration_request,
    evaluate_live_calibration_run,
)
from scenario_drivers import scenario_driver

EXECUTABLE_ENV = "HARNESS_LIVE_CALIBRATION_EXECUTABLE"
TIMEOUT_ENV = "HARNESS_LIVE_CALIBRATION_TIMEOUT_SECONDS"


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _timeout_seconds() -> float:
    raw = os.environ.get(TIMEOUT_ENV, "60")
    try:
        value = float(raw)
    except ValueError as exc:
        raise ValueError(f"{TIMEOUT_ENV} must be a positive number") from exc
    if value <= 0:
        raise ValueError(f"{TIMEOUT_ENV} must be a positive number")
    return value


def _effective_evaluator(
    evaluator: dict[str, Any],
    *,
    executable: Path | None,
    timeout_seconds: float,
) -> dict[str, Any]:
    result = copy.deepcopy(evaluator)
    adapter = result.setdefault("adapter", {})
    if adapter.get("id") != "process-json" or adapter.get("version") != "1":
        raise ValueError(
            "process live calibration driver requires adapter "
            "id=process-json version=1"
        )
    adapter["transport"] = "stdio-json-v1"
    adapter["timeout_seconds"] = timeout_seconds
    adapter["executable_sha256"] = (
        _file_sha256(executable)
        if executable is not None and executable.is_file()
        else None
    )
    return result


_NO_RESULTS = object()


def _run_record(
    request: dict[str, Any],
    *,
    state: str,
    results: Any = _NO_RESULTS,
) -> dict[str, Any]:
    return {
        "version": 1,
        "kind": "harness-live-semantic-calibration-run",
        "run_id": request["run_id"],
        "request_id": request["request_id"],
        "state": state,
        "results": [] if results is _NO_RESULTS else results,
    }


@scenario_driver("semantic.live_calibration.execute_process")
def execute_live_calibration_process(
    *,
    corpus: dict[str, Any],
    protocol: dict[str, Any],
    evaluator: dict[str, Any],
    run_id: str,
) -> dict[str, Any]:
    timeout = _timeout_seconds()
    raw_executable = os.environ.get(EXECUTABLE_ENV)
    executable = (
        Path(raw_executable).expanduser().resolve()
        if isinstance(raw_executable, str) and raw_executable
        else None
    )
    effective = _effective_evaluator(
        evaluator,
        executable=executable,
        timeout_seconds=timeout,
    )

    request = build_live_calibration_request(
        corpus=corpus,
        protocol=protocol,
        evaluator=effective,
        run_id=run_id,
    )
    execution: dict[str, Any] = {
        "boundary": "EXTERNAL_PROCESS",
        "transport": "stdio-json-v1",
        "timeout_seconds": timeout,
        "executable_sha256": effective["adapter"]["executable_sha256"],
    }

    if executable is None or not executable.is_file():
        run = _run_record(request, state="UNAVAILABLE")
        execution["state"] = "UNAVAILABLE"
    else:
        payload = {
            "version": 1,
            "kind": "harness-live-semantic-evaluator-request",
            "request_id": request["request_id"],
            "run_id": request["run_id"],
            "protocol": copy.deepcopy(request["protocol"]),
            "evaluator": copy.deepcopy(effective),
            "cases": copy.deepcopy(request["cases"]),
        }
        try:
            completed = subprocess.run(
                [str(executable)],
                input=json.dumps(payload, ensure_ascii=False),
                text=True,
                capture_output=True,
                timeout=timeout,
                check=False,
            )
        except subprocess.TimeoutExpired:
            run = _run_record(request, state="INTERRUPTED")
            execution["state"] = "INTERRUPTED"
        except OSError as exc:
            run = _run_record(request, state="UNAVAILABLE")
            execution["state"] = "UNAVAILABLE"
            execution["error_type"] = exc.__class__.__name__
        else:
            execution["returncode"] = completed.returncode
            if completed.returncode != 0:
                run = _run_record(request, state="FAILED")
                execution["state"] = "FAILED"
            else:
                try:
                    response = json.loads(completed.stdout)
                except json.JSONDecodeError:
                    response = None
                valid_envelope = (
                    isinstance(response, dict)
                    and response.get("version") == 1
                    and response.get("kind")
                    == "harness-live-semantic-evaluator-response"
                )
                run = _run_record(
                    request,
                    state="COMPLETED",
                    results=(
                        response.get("results")
                        if valid_envelope
                        else None
                    ),
                )
                execution["state"] = "COMPLETED"
                execution["response"] = (
                    "VALID_ENVELOPE" if valid_envelope else "MALFORMED"
                )
                if valid_envelope and isinstance(response.get("provenance"), dict):
                    execution["provider_provenance"] = copy.deepcopy(
                        response["provenance"]
                    )

    evaluation = evaluate_live_calibration_run(
        corpus=corpus,
        protocol=protocol,
        evaluator=effective,
        run=run,
    )
    return {**evaluation, "execution": execution}
