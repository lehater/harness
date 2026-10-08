#!/usr/bin/env python3
"""Blinded Copilot CLI provider adapter for experimental Dependency Resolution.

This module receives one request-bound, label-free discovery payload from the
operator-selected process driver. It never reads the expert oracle. Copilot is
run in a fresh restricted CLI session with no repository instructions or tools.
Execution provenance is observational; it is not independent attestation.
"""
from __future__ import annotations

from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import uuid
from typing import Any

# The process adapter runs with a fresh working directory. The versioned
# repository source bridge must remain importable without changing CWD.
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from harness.assurance.adapters.copilot_live_calibration_evaluator import (
    _sanitized_env,
    _observed_cli_version,
    _parse_copilot_jsonl,
    _resolved_model_from_session,
)

CLI_VERSION = "1.0.86"
MODEL = "auto"
RESPONSE_KIND = "harness-dependency-resolution-evaluator-response"
REQUEST_KIND = "harness-dependency-resolution-evaluator-request"
PROTOCOL_INSTRUCTION = """Resolve direct semantic prerequisite Capabilities for each target production.
Work only from the target's output obligations and the available provider public
knowledge. Do not assume any known current target requires; they are intentionally
hidden. For every explicit output obligation, identify the directly consumed public
knowledge and owning provider Capability. Ignore topic similarity, chronology,
file co-location, mere reachability and operating/tooling dependencies.
A direct source can remain required even where a transitive path also exists.
Do not invent accepted semantics or missing providers. If a material need lacks a
justified provider, set status UNRESOLVED and include the obligation id in
unresolved_obligations. CONTRACT_ONLY providers can justify provisional dependency
planning only, not claims about accepted semantic atoms.
Return only one JSON object with a top-level results array; omit version and kind, which the adapter owns. No markdown, no private chain-of-thought.
For EVERY case, return ALL FIVE keys EXACTLY:
1. case_request_id: unchanged opaque case request identifier;
2. status: RESOLVED or UNRESOLVED;
3. proposed_requires: array of directly required CapabilityIds (use [] when none);
4. input_needs: array of supported direct needs (use [] when none);
5. unresolved_obligations: array of unresolved output obligation IDs (use [] when none).
Never omit unresolved_obligations, even for a RESOLVED case.
Only a complete five-key object for each supplied case is valid.
Do not create dependencies not justified by direct consumption.
The model must not use any external tools or examine local files.
"""


def _blinded_model_payload(request: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(request, dict) or request.get("version") != 1:
        raise ValueError("invalid dependency evaluator request")
    if request.get("kind") != REQUEST_KIND:
        raise ValueError("unexpected dependency evaluator request kind")
    cases = request.get("cases")
    if not isinstance(cases, list) or not cases:
        raise ValueError("missing blinded dependency cases")
    allowed = {"case_request_id", "target", "provider_catalog", "known_uncertainties"}
    result = []
    for case in cases:
        if not isinstance(case, dict) or set(case) != allowed:
            raise ValueError("unexpected case data; potential label leakage")
        if not isinstance(case.get("case_request_id"), str):
            raise ValueError("missing opaque case id")
        target = case.get("target")
        if not isinstance(target, dict) or "requires" in target or "declared_requires" in target:
            raise ValueError("target source contains a direct-edge label")
        result.append(case)
    grounded = request.get("evidence_contract") == "source-grounded-v1"
    coverage = request.get("coverage_contract", "legacy") == "source-traceability-v1"
    if request.get("coverage_contract", "legacy") not in ("legacy", "source-traceability-v1"):
        raise ValueError("unsupported coverage protocol")
    if request.get("evidence_contract", "legacy") not in ("legacy", "source-grounded-v1"):
        raise ValueError("unsupported evidence contract")
    proof_instruction = (
        "SOURCE-GROUNDED PROOF IS REQUIRED. For every input_needs entry, provide "
        "claim_index (zero-based index of an exact semantic_surface claim from "
        "the matching provider), consumption_rationale (15+ characters explaining "
        "why that claim directly constrains THIS obligation), and basis: "
        "DIRECT_ACCEPTED for ACCEPTED_EVIDENCE or PLANNED_CONTRACT for CONTRACT_ONLY. "
        "Do not cite a general permission to choose, intent, informational logging, "
        "topic resemblance, notification, or telemetry as proof of an enforcement "
        "rule. If no source claim governs the requested rule, keep it UNRESOLVED; "
        "omit the context-only provider edge. Do not reinterpret or strengthen "
        "the cited provider statement. Never fabricate claim indices. "
        "Claims tied to still-unresolved obligations are subject to review and "
        "cannot be accepted automatically."
    ) if grounded else ""
    coverage_instruction = (
        "SOURCE COVERAGE REVIEW IS REQUIRED. For every case the target contains "
        "upstream_constraint_candidates, an exhaustive inventory of accepted "
        "Product Capability statements within this reviewed product artifact. "
        "Report EXACTLY one coverage_assessments record per requirement_id, "
        "including UNTRACED candidates. Each record must contain requirement_id, "
        "disposition DIRECT_CONSTRAINT or CONTEXT_ONLY or UNDECIDED, and a "
        "nontrivial rationale. DIRECT_CONSTRAINT means a product statement "
        "directly constrains the target's stated tactical semantic obligations "
        "AND you have proposed the provider as a direct requires with a cited "
        "input_need; do not confuse broad application behavior with domain "
        "semantics. CONTEXT_ONLY means product behavior is relevant background "
        "but not independently consumed by the scoped tactical output. "
        "UNDECIDED means semantic applicability needs authoritative review. "
        "Do not omit candidate records or silently mark applicability proven. "
        "This review does not establish completeness or permit graph removals."
    ) if coverage else ""
    return {
        "instruction": PROTOCOL_INSTRUCTION + proof_instruction + "\n" + coverage_instruction,
        "evidence_contract": request.get("evidence_contract", "legacy"),
        "coverage_contract": request.get("coverage_contract", "legacy"),
        "cases": result,
        "response_schema": {
            "results": [
                {
                    "case_request_id": "opaque case_request_id from the input",
                    "status": "RESOLVED | UNRESOLVED",
                    "proposed_requires": ["CapabilityIds directly consumed"],
                    "input_needs": [
                        ({
                            "obligation": "output obligation id",
                            "provider": "CapabilityId",
                            "claim_index": "zero-based index into provider semantic_surface",
                            "basis": "DIRECT_ACCEPTED | PLANNED_CONTRACT",
                            "consumption_rationale": "Why this exact claim directly constrains the target obligation",
                        } if grounded else {
                            "obligation": "output obligation id",
                            "provider": "CapabilityId",
                        })
                    ],
                    "unresolved_obligations": ["unresolved obligation ids"],
                    **({
                        "coverage_assessments": [
                            {"requirement_id": "each accepted candidate requirement_id",
                             "disposition": "DIRECT_CONSTRAINT | CONTEXT_ONLY | UNDECIDED",
                             "rationale": "Source-grounded reason for the applicability judgement"}
                        ]
                    } if coverage else {}),
                }
            ],
            "output": (
                "Return exactly one JSON object with results. Each result MUST "
                "include case_request_id, status, proposed_requires, input_needs, "
                "unresolved_obligations and, for this source-traceability-v1 "
                "protocol, coverage_assessments covering EVERY candidate exactly once. "
                "Use [] for empty arrays. The adapter owns outer version/kind."
                if coverage else
                "Exactly one JSON object with a top-level results array. Every case "
                "MUST have case_request_id, status, proposed_requires, input_needs "
                "and unresolved_obligations; empty arrays MUST be []."
            ),
        },
    }


def _prompt(request: dict[str, Any]) -> str:
    return json.dumps(_blinded_model_payload(request), ensure_ascii=False, separators=(",", ":"))


def _validate_model_results(
    model_result: Any, request: dict[str, Any]
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Validate model-owned judgments, normalize only the adapter-owned envelope.

    The model is responsible for result values and opaque case bindings, while
    the trusted adapter owns the wire protocol version and kind. No semantic
    predictions or missing cases are repaired or inferred here.
    """
    if not isinstance(model_result, dict):
        raise ValueError("Copilot must return a JSON object")
    results = model_result.get("results")
    if not isinstance(results, list):
        raise ValueError(
            "Copilot must return a results array; observed keys="
            + repr(sorted(str(k) for k in model_result))
        )
    cases = request["cases"]
    expected = {case["case_request_id"] for case in cases}
    if len(results) != len(expected):
        raise ValueError(
            f"Copilot result count mismatch: expected {len(expected)}, got {len(results)}"
        )
    observed: set[str] = set()
    for i, item in enumerate(results):
        if not isinstance(item, dict):
            raise ValueError(f"Copilot result #{i} is not an object")
        binding = item.get("case_request_id")
        if not isinstance(binding, str) or binding not in expected or binding in observed:
            raise ValueError(f"Copilot result #{i} has missing, unknown or duplicate case binding")
        observed.add(binding)
        if item.get("status") not in {"RESOLVED", "UNRESOLVED"}:
            raise ValueError(f"Copilot result #{i} has invalid status")
        if not isinstance(item.get("proposed_requires"), list):
            raise ValueError(f"Copilot result #{i} missing proposed_requires list")
        if not isinstance(item.get("input_needs"), list):
            raise ValueError(f"Copilot result #{i} missing input_needs list")
        if not isinstance(item.get("unresolved_obligations"), list):
            raise ValueError(f"Copilot result #{i} missing unresolved_obligations list")
        if request.get("coverage_contract", "legacy") == "source-traceability-v1":
            target = next(c["target"] for c in cases if c["case_request_id"] == binding)
            expected_requirements = {
                c["requirement_id"] for c in target["upstream_constraint_candidates"]
            }
            observed_records = item.get("coverage_assessments")
            if not isinstance(observed_records, list):
                raise ValueError(f"Copilot result #{i} missing coverage_assessments list")
            collected: set[str] = set()
            for record in observed_records:
                if not isinstance(record, dict):
                    raise ValueError(f"Copilot result #{i} malformed coverage assessment")
                requirement_id = record.get("requirement_id")
                if (
                    not isinstance(requirement_id, str)
                    or requirement_id not in expected_requirements
                    or requirement_id in collected
                ):
                    raise ValueError(f"Copilot result #{i} unknown/duplicate requirement assessment")
                collected.add(requirement_id)
                if record.get("disposition") not in (
                    "DIRECT_CONSTRAINT", "CONTEXT_ONLY", "UNDECIDED",
                ):
                    raise ValueError(f"Copilot result #{i} invalid coverage disposition")
                if not isinstance(record.get("rationale"), str) or len(record["rationale"].strip()) < 15:
                    raise ValueError(f"Copilot result #{i} missing coverage rationale")
            if collected != expected_requirements:
                raise ValueError(
                    f"Copilot result #{i} incomplete coverage_assessments: "
                    f"expected {len(expected_requirements)} got {len(collected)}"
                )
    envelope = {
        "adapter_owned_protocol": True,
        "model_supplied_version": model_result.get("version", "OMITTED"),
        "model_supplied_kind": model_result.get("kind", "OMITTED"),
        "adapter_envelope_normalized": (
            model_result.get("version") != 1 or model_result.get("kind") != RESPONSE_KIND
        ),
    }
    return results, envelope


def _invoke_copilot_once(executable: str, prompt: str) -> tuple[Any, dict[str, Any]]:
    """One tool-free, fresh-session Copilot invocation, without any oracle."""
    session_id = str(uuid.uuid4())
    with tempfile.TemporaryDirectory(prefix="harness-cdr-copilot-") as directory:
        root = Path(directory)
        home = root / "home"
        work = root / "work"
        home.mkdir()
        work.mkdir()
        env = _sanitized_env(home)
        observed_version = _observed_cli_version(executable, env)
        if observed_version != CLI_VERSION:
            raise RuntimeError(
                f"Copilot CLI mismatch expected={CLI_VERSION} actual={observed_version}"
            )
        command = [
            executable,
            "-p", prompt,
            f"--model={MODEL}",
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
            command, cwd=work, env=env, text=True, capture_output=True,
            timeout=105, check=False,
        )
        if completed.returncode:
            raise RuntimeError(
                f"Copilot CLI failed ({completed.returncode}): "
                f"{completed.stderr.strip()[:1600]}"
            )
        model_text, observed_model = _parse_copilot_jsonl(completed.stdout)
        resolved_model = _resolved_model_from_session(home) or observed_model
        if not resolved_model:
            raise RuntimeError("Copilot resolved model is not observable")
        try:
            model_result = json.loads(model_text)
        except json.JSONDecodeError as exc:
            raise ValueError("Copilot result must be strict JSON") from exc
    return model_result, {
        "requested_model": MODEL,
        "resolved_model": resolved_model,
        "observed_cli_version": observed_version,
        "client_session_id": session_id,
    }


def _invoke_model(request: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    """Validate complete model-owned rows; retry one schema error with feedback.

    The retry is a new complete, blinded model invocation. No defaults,
    patches, inferred edges, previous model predictions or oracle labels are
    supplied. An invalid second response fails closed.
    """
    executable = os.environ.get("HARNESS_COPILOT_EXECUTABLE", "copilot")
    blinded_prompt = _prompt(request)
    schema_errors: list[str] = []
    invocation_metadata: list[dict[str, Any]] = []
    for attempt in range(2):
        prompt = blinded_prompt
        if schema_errors:
            prompt += (
                "\nSCHEMA RETRY: The previous complete response was rejected: "
                + schema_errors[-1]
                + ". Return a NEW complete answer for every original case, "
                  "with all five mandatory fields. Use [] for empty arrays. "
                  "Do not treat this feedback as semantic evidence. "
                  "Do not guess unresolved facts or change the source claims."
            )
        model_result, info = _invoke_copilot_once(executable, prompt)
        invocation_metadata.append(info)
        try:
            results, model_envelope = _validate_model_results(model_result, request)
        except ValueError as exc:
            error = str(exc)
            schema_errors.append(error)
            if attempt == 1:
                raise ValueError(
                    "Copilot schema rejected after 2 fresh attempts: "
                    + "; ".join(schema_errors)
                ) from exc
            continue
        provenance = {
            "provider": "github-copilot",
            "requested_model": MODEL,
            "resolved_model": info["resolved_model"],
            "observed_cli_version": info["observed_cli_version"],
            "client_session_id": info["client_session_id"],
            "completed_at": datetime.now(timezone.utc).isoformat(),
            "fresh_home": True,
            "custom_instructions_disabled": True,
            "builtin_mcps_disabled": True,
            "no_available_tools": True,
            "independence": "UNVERIFIED",
            "model_envelope": model_envelope,
            "coverage_contract": request.get("coverage_contract", "legacy"),
            "invocation_attempts": len(invocation_metadata),
            "schema_retry_errors": schema_errors,
            "attempt_session_ids": [m["client_session_id"] for m in invocation_metadata],
            "attempt_resolved_models": [m["resolved_model"] for m in invocation_metadata],
        }
        return {"results": results}, provenance
    raise RuntimeError("unreachable: Copilot attempts exhausted")


def evaluate_request(request: dict[str, Any]) -> dict[str, Any]:
    # Explicitly build a label-free prompt before invoking provider.
    _blinded_model_payload(request)
    output, provenance = _invoke_model(request)
    # The trusted bridge binds the reply to its actual request rather than
    # asking the model to self-attest request identity.
    return {
        "version": 1,
        "kind": RESPONSE_KIND,
        "request_id": request["request_id"],
        "results": output["results"],
        "provenance": provenance,
    }


def main() -> int:
    try:
        request = json.load(sys.stdin)
        response = evaluate_request(request)
        json.dump(response, sys.stdout, ensure_ascii=False)
        sys.stdout.write("\n")
        return 0
    except Exception as exc:
        print(f"Copilot CDR adapter: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
