#!/usr/bin/env python3
"""Experimental grounding/proof preflight tests; no LLM accuracy asserted."""
from __future__ import annotations

import copy
from pathlib import Path
import sys

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from evals.dependency_resolution_calibration import score, validate
from evals.dependency_resolution_evidence import assess_case, assess_predictions
from evals.dependency_resolution_process_driver import build_blinded_request
import evals.adapters.copilot_dependency_resolution_evaluator as copilot

ROOT_CASES = ROOT / "spec" / "dependency-resolution"


def load(name: str):
    return yaml.safe_load((ROOT_CASES / name).read_text(encoding="utf-8"))


inputs = load("adversarial-inputs-v1.yaml")
oracle = load("adversarial-oracle-v1.yaml")
assert validate(inputs, oracle)["cases"] == 6
assert all(v["review_status"] == "AUTHOR_DRAFT" for v in oracle["cases"])
ids = {v["id"] for v in inputs["cases"]}
assert not ids.intersection({v["id"] for v in load("holdout-inputs-v1.yaml")["cases"]})
assert not ids.intersection({v["id"] for v in load("calibration-inputs-v1.yaml")["cases"]})

request = build_blinded_request(inputs, run_id="PROOF-SMOKE", adapter_binding={"id": "test"})
assert request["evidence_contract"] == "source-grounded-v1"
rendered = repr(request)
for secret in ("expected_requires", "baseline_requires", "expected_status", "review_status", "ADV-01"):
    assert secret not in rendered, secret
prompt = copilot._prompt(request)
assert "claim_index" in prompt and "PLANNED_CONTRACT" in prompt
assert "expected_requires" not in prompt

# Oracle-derived predictions exercise the scorer, not any model inference.
predictions = {
    "version": 1,
    "kind": "harness-dependency-resolution-predictions",
    "cases": [],
}
for case in inputs["cases"]:
    expected = next(v for v in oracle["cases"] if v["id"] == case["id"])
    providers = {p["capability"]: p for p in case["provider_catalog"]}
    claimed = []
    for need in expected["expected_direct_needs"]:
        provider = providers[need["provider"]]
        claimed.append({
            **need,
            "claim_index": 0,
            "basis": ("PLANNED_CONTRACT" if provider["evidence_status"] == "CONTRACT_ONLY"
                      else "DIRECT_ACCEPTED"),
            "consumption_rationale": (
                f"The quoted source claim constrains {need['obligation']} "
                "and is consumed in the described output contract."
            ),
        })
    predictions["cases"].append({
        "id": case["id"],
        "status": expected["expected_status"],
        "proposed_requires": list(expected["expected_requires"]),
        "input_needs": claimed,
        "unresolved_obligations": list(expected["expected_unresolved_obligations"]),
    })
baseline = score(inputs, oracle, predictions)
assert baseline["status"] == "MATCHES_DRAFT_ORACLE", baseline
proof = baseline["evidence_assessment"]
assert proof["status"] == "REVIEW_REQUIRED"  # ADV-04 planned VAT provider.
assert proof["automatic_writeback_allowed"] is False
assert proof["semantic_entailment_verified"] is False
assert next(x for x in proof["cases"] if x["id"] == "ADV-04")["provisional_requires"] == [
    "adversarial.future-vat-policy"
]
assert next(x for x in proof["cases"] if x["id"] == "ADV-03")["status"] == (
    "REFERENCED_NOT_SEMANTICALLY_VERIFIED"
)

def assert_invalid(prediction):
    observation = score(inputs, oracle, prediction)
    assert observation["status"] == "DIFFERS_OR_INCOMPLETE", observation
    assert observation["evidence_assessment"]["status"] == "INVALID", observation


bad = copy.deepcopy(predictions)
bad["cases"][0]["input_needs"][0]["claim_index"] = 999
assert_invalid(bad)

bad = copy.deepcopy(predictions)
bad["cases"][1]["input_needs"][0]["basis"] = "PLANNED_CONTRACT"
assert_invalid(bad)

bad = copy.deepcopy(predictions)
bad["cases"][4]["input_needs"][0]["consumption_rationale"] = "similar"
assert_invalid(bad)

bad = copy.deepcopy(predictions)
bad["cases"][5]["proposed_requires"] = ["adversarial.inventory-domain-state", "adversarial.stock-request-metrics"]
assert_invalid(bad)

# Regression from HLD-01 repeated Copilot run: a related generic user choice
# must NOT be silently adoption-eligible as a consent-enforcement provider.
holdout = next(x for x in load("holdout-inputs-v1.yaml")["cases"] if x["id"] == "HLD-01")
false_edge = {
    "status": "UNRESOLVED",
    "proposed_requires": ["holdout.partner-field-contract", "holdout.product-sharing-intent"],
    "input_needs": [
        {"obligation": "encode-partner-message", "provider": "holdout.partner-field-contract",
         "claim_index": 0, "basis": "DIRECT_ACCEPTED",
         "consumption_rationale": "The accepted payload fields govern the structure of partner messages."},
        {"obligation": "enforce-release-consent", "provider": "holdout.product-sharing-intent",
         "claim_index": 0, "basis": "DIRECT_ACCEPTED",
         "consumption_rationale": "User sharing choice is related to the consent enforcement obligation."},
    ],
    "unresolved_obligations": ["enforce-release-consent"],
}
result = assess_case(holdout, false_edge)
assert result["status"] == "REVIEW_REQUIRED"
assert "holdout.product-sharing-intent" not in result["adoption_eligible_requires"]
assert any(x["code"] == "DIRECT_EDGE_FOR_UNRESOLVED_OBLIGATION" for x in result["review_required"])
assert result["automatic_writeback_allowed"] is False

# A grounded citation cannot prove semantic entailment: the checker must
# preserve this limitation rather than falsely claim deterministic truth.
result = assess_case(
    inputs["cases"][1], predictions["cases"][1]
)
assert result["semantic_entailment_verified"] is False
print("dependency resolution evidence-grounding preflight: PASS")
