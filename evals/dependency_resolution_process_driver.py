"""Read-only external-process adapter for experimental Capability Dependency Resolution.

Operator-selected via Scenario Suite --driver-module; scenarios cannot choose
an executable. A local process is NOT a security sandbox or an independent oracle.
"""
from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from typing import Any

from harness.application.scenario_drivers import scenario_driver
from evals.dependency_resolution_calibration import validate, score
from evals.dependency_resolution_evidence import assess_predictions

EXECUTABLE_ENV = "HARNESS_CDR_EVALUATOR_EXECUTABLE"
TIMEOUT_ENV = "HARNESS_CDR_EVALUATOR_TIMEOUT_SECONDS"
RESULT_KIND = "harness-dependency-resolution-evaluator-response"


def _digest(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return "sha256:" + hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _timeout() -> float:
    raw = os.environ.get(TIMEOUT_ENV, "60")
    try:
        value = float(raw)
    except ValueError as exc:
        raise ValueError("CDR evaluator timeout must be numeric") from exc
    if not 0 < value <= 300:
        raise ValueError("CDR evaluator timeout must be between 0 and 300 seconds")
    return value


def build_blinded_request(inputs: dict[str, Any], *, run_id: str,
                          adapter_binding: dict[str, Any]) -> dict[str, Any]:
    """Construct case requests without target edges, case labels or expert oracle."""
    if not isinstance(run_id, str) or not run_id.strip():
        raise ValueError("CDR run_id required")
    if not isinstance(inputs, dict) or inputs.get("version") != 1:
        raise ValueError("invalid CDR discovery corpus")
    cases = inputs.get("cases")
    if not isinstance(cases, list) or not cases:
        raise ValueError("CDR discovery cases required")
    forbidden = {"declared_requires", "baseline_requires", "expected_requires",
                 "expected_direct_needs", "expert_oracle", "expected_status"}
    for item in cases:
        if not isinstance(item, dict) or not isinstance(item.get("id"), str):
            raise ValueError("invalid CDR case")
        if forbidden & set(item) or forbidden & set(item.get("target", {})):
            raise ValueError("CDR source contains hidden target edges or labels")
    request_id = _digest({
        "run_id": run_id,
        "corpus": inputs,
        "protocol": "capability-dependency-resolution/1",
        "adapter": adapter_binding,
    })
    blinded = []
    for index, case in enumerate(cases):
        blinded.append({
            "case_request_id": _digest({"request_id": request_id, "index": index}),
            "target": copy.deepcopy(case["target"]),
            "provider_catalog": copy.deepcopy(case["provider_catalog"]),
            "known_uncertainties": copy.deepcopy(case.get("known_uncertainties", [])),
        })
    return {
        "version": 1,
        "kind": "harness-dependency-resolution-evaluator-request",
        "request_id": request_id,
        "run_id": run_id,
        "protocol_id": "capability-dependency-resolution/1",
        "evidence_contract": inputs.get("evidence_contract", "legacy"),
        "cases": blinded,
    }


def _invalid(code: str, *, execution: dict[str, Any]) -> dict[str, Any]:
    return {
        "status": "INVALID",
        "code": code,
        "calibration_claim": "NOT_ESTABLISHED",
        "independence": "UNVERIFIED",
        "execution": execution,
    }


def _validate_discovery_inputs(inputs: dict[str, Any]) -> None:
    if inputs.get("version") != 1 or inputs.get("kind") != "harness-dependency-resolution-calibration-inputs":
        raise ValueError("invalid discovery inputs kind/version")
    if inputs.get("evidence_contract") != "source-grounded-v1":
        raise ValueError("project discovery requires the source-grounded proof contract")
    cases = inputs.get("cases")
    if not isinstance(cases, list) or not cases:
        raise ValueError("discovery cases required")
    ids = set()
    for item in cases:
        cid = item.get("id")
        if not isinstance(cid, str) or not cid or cid in ids:
            raise ValueError("discovery case ids missing or duplicated")
        ids.add(cid)
        forbidden = {"declared_requires", "baseline_requires", "expected_requires",
                     "expected_direct_needs", "expert_oracle", "expected_status"}
        if forbidden.intersection(item) or forbidden.intersection(item.get("target", {})):
            raise ValueError("target dependency or scoring labels leaked into discovery")
        target = item["target"]
        obligations = target["output_obligations"]
        if not isinstance(obligations, list) or not obligations:
            raise ValueError("missing target output obligations")
        if len({x["id"] for x in obligations}) != len(obligations):
            raise ValueError("duplicate target obligation")
        providers = item["provider_catalog"]
        if not isinstance(providers, list) or not providers:
            raise ValueError("missing accepted provider catalog")
        if len({x["capability"] for x in providers}) != len(providers):
            raise ValueError("duplicate provider")
        if target["capability"] in {x["capability"] for x in providers}:
            raise ValueError("self-provider in discovery")


@scenario_driver("dependency.calibration.execute_process")
@scenario_driver("dependency.discovery.execute_process")
def execute_dependency_resolution_process(
    *, inputs: dict[str, Any], run_id: str, oracle: dict[str, Any] | None = None
) -> dict[str, Any]:
    """Run a blinded evaluator; score only when a separately authored oracle exists.

    Without oracle, this is an unscored read-only project discovery, not a
    calibration result. Existing execution and request binding are unchanged.
    """
    try:
        if oracle is None:
            _validate_discovery_inputs(inputs)
        else:
            validate(inputs, oracle)
    except (KeyError, ValueError, TypeError) as exc:
        return _invalid("INVALID_DISCOVERY_INPUTS", execution={"error": str(exc)})
    timeout = _timeout()
    configured = os.environ.get(EXECUTABLE_ENV, "")
    executable = Path(configured).expanduser().resolve() if configured else None
    executable_hash = None
    if executable is not None and executable.is_file():
        executable_hash = hashlib.sha256(executable.read_bytes()).hexdigest()
    adapter = {
        "id": "process-json-v1",
        "executable_sha256": executable_hash,
        "timeout_seconds": timeout,
    }
    request = build_blinded_request(inputs, run_id=run_id, adapter_binding=adapter)
    execution = {
        "boundary": "EXTERNAL_PROCESS",
        "executable_sha256": executable_hash,
        "request_id": request["request_id"],
    }
    if executable is None or not executable.is_file():
        return {
            "status": "UNAVAILABLE",
            "calibration_claim": "NOT_ESTABLISHED",
            "independence": "UNVERIFIED",
            "execution": execution,
        }
    try:
        # CWD isolation prevents accidental relative-path corpus reads; it is
        # not a filesystem sandbox. Operator is responsible for real isolation.
        with tempfile.TemporaryDirectory(prefix="harness-cdr-evaluator-") as cwd:
            completed = subprocess.run(
                ([sys.executable, str(executable)] if executable.suffix == ".py" else [str(executable)]),
                input=json.dumps(request, ensure_ascii=False),
                text=True,
                capture_output=True,
                cwd=cwd,
                timeout=timeout,
                check=False,
            )
    except subprocess.TimeoutExpired:
        return _invalid("EVALUATOR_TIMEOUT", execution=execution)
    except OSError as exc:
        return _invalid("EVALUATOR_UNAVAILABLE", execution={**execution, "error_type": type(exc).__name__})
    if completed.returncode != 0:
        # Provide a bounded, credential-redacted diagnostic so a real provider
        # failure is actionable instead of an opaque subprocess exit code.
        import re
        detail = completed.stderr.strip().replace("\n", " ")[:1800]
        for key in ("GITHUB_TOKEN", "GH_TOKEN", "COPILOT_GITHUB_TOKEN"):
            secret = os.environ.get(key)
            if secret:
                detail = detail.replace(secret, "[REDACTED]")
        detail = re.sub(
            r"\b(?:gh[pousr]_[A-Za-z0-9_]+|github_pat_[A-Za-z0-9_]+)\b",
            "[REDACTED]", detail,
        )
        return _invalid("EVALUATOR_FAILED", execution={
            **execution, "returncode": completed.returncode,
            "error_detail": detail or "No stderr produced",
        })
    try:
        response = json.loads(completed.stdout)
    except (json.JSONDecodeError, TypeError):
        return _invalid("MALFORMED_EVALUATOR_RESPONSE", execution=execution)
    if not isinstance(response, dict) or response.get("version") != 1 or response.get("kind") != RESULT_KIND:
        return _invalid("MALFORMED_EVALUATOR_RESPONSE", execution=execution)
    if response.get("request_id") != request["request_id"]:
        return _invalid("REQUEST_BINDING_MISMATCH", execution=execution)
    results = response.get("results")
    if not isinstance(results, list):
        return _invalid("MALFORMED_EVALUATOR_RESULTS", execution=execution)
    bindings = {item["case_request_id"]: index for index, item in enumerate(request["cases"])}
    if len(results) != len(bindings):
        return _invalid("INCOMPLETE_EVALUATOR_RESULTS", execution=execution)
    observed: dict[str, Any] = {}
    for item in results:
        if not isinstance(item, dict):
            return _invalid("MALFORMED_EVALUATOR_RESULTS", execution=execution)
        bid = item.get("case_request_id")
        if not isinstance(bid, str) or bid not in bindings or bid in observed:
            return _invalid("UNKNOWN_OR_DUPLICATE_CASE_BINDING", execution=execution)
        if any(k in item for k in ("id", "expected_status", "baseline_requires")):
            return _invalid("EVALUATOR_LABEL_ECHO", execution=execution)
        observed[bid] = item
    remapped = []
    for bid, index in sorted(bindings.items(), key=lambda pair: pair[1]):
        item = observed[bid]
        remapped.append({
            "id": inputs["cases"][index]["id"],
            "status": item.get("status"),
            "proposed_requires": item.get("proposed_requires"),
            "input_needs": item.get("input_needs"),
            "unresolved_obligations": item.get("unresolved_obligations"),
        })
    predictions = {
        "version": 1,
        "kind": "harness-dependency-resolution-predictions",
        "cases": remapped,
    }
    try:
        if oracle is not None:
            evaluation = score(inputs, oracle, predictions)
        else:
            assessment = assess_predictions(inputs, predictions)
            evaluation = {
                "status": ("DISCOVERY_REQUIRES_REVIEW"
                           if assessment["status"] != "INVALID" else "INVALID"),
                "calibration_claim": "NOT_APPLICABLE_NO_ORACLE",
                "oracle_is_expert_validated": False,
                "evidence_assessment": assessment,
                "source_snapshot": inputs.get("source_snapshot"),
                "edge_comparison": None,
                "automatic_writeback_allowed": False,
            }
    except (KeyError, ValueError, TypeError) as exc:
        return _invalid("INVALID_EVALUATOR_PREDICTIONS",
                        execution={**execution, "error": str(exc)})
    provider_provenance = response.get("provenance")
    if not isinstance(provider_provenance, dict):
        provider_provenance = None
    return {
        **evaluation,
        # Keep the unmodified model-supplied result rows for independent review.
        # Their content is evidence only; scoring still uses the validated and
        # case-bound projection above, never these untrusted rows directly.
        "model_results": copy.deepcopy(results),
        "bound_predictions": predictions,
        "independence": "UNVERIFIED",
        "execution": {**execution, "state": "COMPLETED", "provider_provenance": provider_provenance},
    }
