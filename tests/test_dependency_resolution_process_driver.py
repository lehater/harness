#!/usr/bin/env python3
"""Request-binding and failure-mode tests for the experimental CDR process driver."""
from __future__ import annotations

import os
from pathlib import Path
import sys
import tempfile

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from evals.dependency_resolution_process_driver import (
    EXECUTABLE_ENV, TIMEOUT_ENV, build_blinded_request,
    execute_dependency_resolution_process,
)

DATA = ROOT / "spec" / "dependency-resolution"
inputs = yaml.safe_load((DATA / "calibration-inputs-v1.yaml").read_text(encoding="utf-8"))
oracle = yaml.safe_load((DATA / "calibration-oracle-v1.yaml").read_text(encoding="utf-8"))

request = build_blinded_request(inputs, run_id="SMOKE", adapter_binding={"id": "fixture"})
assert request["cases"] and len(request["cases"]) == 6
assert all("id" not in case and "declared_requires" not in case and
           "expected_requires" not in case and "baseline_requires" not in case
           for case in request["cases"])
assert "expected_requires" not in repr(request) and "expected_status" not in repr(request)
assert request["request_id"] != build_blinded_request(
    inputs, run_id="SMOKE-2", adapter_binding={"id": "fixture"}
)["request_id"]

old_exec = os.environ.get(EXECUTABLE_ENV)
old_timeout = os.environ.get(TIMEOUT_ENV)
os.environ[TIMEOUT_ENV] = "5"
try:
    os.environ.pop(EXECUTABLE_ENV, None)
    assert execute_dependency_resolution_process(
        inputs=inputs, oracle=oracle, run_id="SMOKE"
    )["status"] == "UNAVAILABLE"

    with tempfile.TemporaryDirectory() as root:
        path = Path(root) / "evaluator.py"
        # Controlled fake evaluator: case-specific mapping proves transport, not
        # agent reasoning, oracle independence or semantic quality.
        source = '''#!/usr/bin/env python3
import json
import sys

req = json.load(sys.stdin)
truth = {
    "demo.edit-application": (
        "RESOLVED", ["demo.product-edit-policy", "demo.resource-domain"],
        [("enforce-product-edit-policy", "demo.product-edit-policy"),
         ("preserve-domain-validity", "demo.resource-domain")], []),
    "demo.edit-interaction": (
        "RESOLVED", ["demo.product-edit-policy", "demo.edit-operation"],
        [("represent-denial", "demo.product-edit-policy"),
         ("invoke-operation", "demo.edit-operation")], []),
    "demo.delete-application": (
        "RESOLVED", ["demo.delete-product-policy", "demo.delete-task"],
        [("enforce-delete-policy", "demo.delete-product-policy"),
         ("implement-delete-task", "demo.delete-task")], []),
    "demo.partner-export": (
        "UNRESOLVED", ["demo.partner-message-contract"],
        [("preserve-message-shape", "demo.partner-message-contract")],
        ["enforce-consent"]),
    "prep.preparation-information-model": (
        "RESOLVED", ["prep.model-context-strategy", "prep.product-capabilities"],
        [("define-current-preparation-information", "prep.model-context-strategy"),
         ("define-relationship-meaning", "prep.product-capabilities"),
         ("exclude-learner-conclusions", "prep.model-context-strategy")], []),
    "prep.recorded-activity-history-model": (
        "RESOLVED", ["prep.model-context-strategy", "prep.product-capabilities"],
        [("distinguish-history", "prep.model-context-strategy"),
         ("preserve-temporal-context", "prep.product-capabilities"),
         ("preserve-historical-meaning", "prep.product-capabilities")], []),
}
results = []
for case in req["cases"]:
    status, deps, needs, unresolved = truth[case["target"]["capability"]]
    results.append({
        "case_request_id": case["case_request_id"],
        "status": status,
        "proposed_requires": deps,
        "input_needs": [{"obligation": ob, "provider": p} for ob, p in needs],
        "unresolved_obligations": unresolved,
    })
print(json.dumps({
    "version": 1,
    "kind": "harness-dependency-resolution-evaluator-response",
    "request_id": req["request_id"],
    "results": results,
}))
'''
        path.write_text(source, encoding="utf-8")
        path.chmod(0o700)
        os.environ[EXECUTABLE_ENV] = str(path)
        result = execute_dependency_resolution_process(
            inputs=inputs, oracle=oracle, run_id="SMOKE"
        )
        assert result["status"] == "MATCHES_DRAFT_ORACLE", result
        assert result["calibration_claim"] == "NOT_ESTABLISHED"
        assert result["independence"] == "UNVERIFIED"
        assert result["execution"]["state"] == "COMPLETED"
        assert len(result["model_results"]) == 6
        assert result["model_results"][0]["case_request_id"]
        assert result["bound_predictions"]["cases"][0]["id"] == "CDR-01"
        assert "expected_requires" not in repr(result["model_results"])

        bad = Path(root) / "bad.py"
        bad.write_text(source.replace(
            '"request_id": req["request_id"]',
            '"request_id": "STALE"'), encoding="utf-8")
        bad.chmod(0o700)
        os.environ[EXECUTABLE_ENV] = str(bad)
        result = execute_dependency_resolution_process(
            inputs=inputs, oracle=oracle, run_id="SMOKE"
        )
        assert result["status"] == "INVALID"
        assert result["code"] == "REQUEST_BINDING_MISMATCH"

        malformed = Path(root) / "malformed.py"
        malformed.write_text("#!/usr/bin/env python3\\nprint('not json')\\n".replace(
            "\\n", "\n"), encoding="utf-8")
        malformed.chmod(0o700)
        os.environ[EXECUTABLE_ENV] = str(malformed)
        result = execute_dependency_resolution_process(
            inputs=inputs, oracle=oracle, run_id="SMOKE"
        )
        assert result["code"] == "MALFORMED_EVALUATOR_RESPONSE"

finally:
    if old_exec is None:
        os.environ.pop(EXECUTABLE_ENV, None)
    else:
        os.environ[EXECUTABLE_ENV] = old_exec
    if old_timeout is None:
        os.environ.pop(TIMEOUT_ENV, None)
    else:
        os.environ[TIMEOUT_ENV] = old_timeout

print("dependency resolution external process driver: PASS")
