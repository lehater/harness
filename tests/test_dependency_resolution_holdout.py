#!/usr/bin/env python3
"""Deterministic holdout corpus integrity, label separation and mutation tests.

The oracle-derived predictions below are a TEST FIXTURE FOR THE SCORER ONLY,
not a claim that any real agent resolved the unseen cases or that labels are true.
"""
from __future__ import annotations

import copy
from pathlib import Path
import sys

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from evals.dependency_resolution_calibration import score, validate
from evals.dependency_resolution_process_driver import build_blinded_request

DATA = ROOT / "spec" / "dependency-resolution"


def load(name):
    return yaml.safe_load((DATA / name).read_text(encoding="utf-8"))


inputs = load("holdout-inputs-v1.yaml")
oracle = load("holdout-oracle-v1.yaml")
seed = load("calibration-inputs-v1.yaml")

assert validate(inputs, oracle)["cases"] == 7
assert all(x["review_status"] == "AUTHOR_DRAFT" for x in oracle["cases"])
assert len({c["id"] for c in inputs["cases"]} & {c["id"] for c in seed["cases"]}) == 0
assert all(not c.get("known_uncertainties") for c in inputs["cases"])
assert {c["id"] for c in inputs["cases"]} == {
    "HLD-01", "HLD-02", "HLD-03", "HLD-04",
    "HLD-05", "HLD-06", "HLD-07",
}
request = build_blinded_request(
    inputs,
    run_id="HOLDOUT-BLINDNESS-TEST",
    adapter_binding={"id": "test-only"},
)
assert len(request["cases"]) == 7
rendered = repr(request)
for forbidden in (
    "baseline_requires", "expected_requires", "expected_direct_needs",
    "review_status", "expected_status", "HLD-01", "HLD-06",
):
    assert forbidden not in rendered, forbidden

# This is deliberately built from expert-authored draft labels in the TEST.
# It is NEVER passed to the provider and NEVER counts as LLM calibration.
predictions = {
    "version": 1,
    "kind": "harness-dependency-resolution-predictions",
    "cases": [
        {
            "id": item["id"],
            "status": item["expected_status"],
            "proposed_requires": list(item["expected_requires"]),
            "input_needs": list(item["expected_direct_needs"]),
            "unresolved_obligations": list(item["expected_unresolved_obligations"]),
        }
        for item in oracle["cases"]
    ],
}
baseline = score(inputs, oracle, predictions)
assert baseline["status"] == "MATCHES_DRAFT_ORACLE"
assert baseline["oracle_is_expert_validated"] is False
assert baseline["calibration_claim"] == "NOT_ESTABLISHED"

wrong = copy.deepcopy(predictions)
wrong["cases"][5]["input_needs"].pop()
assert score(inputs, oracle, wrong)["status"] == "DIFFERS_OR_INCOMPLETE"
assert score(inputs, oracle, wrong)["cases"][5]["missing_direct_needs"]

wrong = copy.deepcopy(predictions)
wrong["cases"][6]["proposed_requires"] = ["holdout.domain-sales-status"]
report = score(inputs, oracle, wrong)
assert report["status"] == "DIFFERS_OR_INCOMPLETE"
assert report["edge_comparison"]["false_positive"] == 1

wrong = copy.deepcopy(predictions)
wrong["cases"][0]["status"] = "RESOLVED"
assert not score(inputs, oracle, wrong)["cases"][0]["status_correct"]

wrong = copy.deepcopy(predictions)
wrong["cases"][1]["unresolved_obligations"] = []
assert not score(inputs, oracle, wrong)["cases"][1]["unresolved_correct"]

print("dependency resolution holdout integrity: PASS")
