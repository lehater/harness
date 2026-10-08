#!/usr/bin/env python3
"""Smoke and mutation tests for experimental CDR calibration integration."""
from __future__ import annotations

import copy
from pathlib import Path
import sys

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from harness.application.scenario_suite import load_driver_modules, run_scenario
from evals.dependency_resolution_calibration import validate, score

FIXTURES = ROOT / "spec" / "dependency-resolution"
def read(filename: str):
    return yaml.safe_load((FIXTURES / filename).read_text(encoding="utf-8"))

inputs = read("calibration-inputs-v1.yaml")
oracle = read("calibration-oracle-v1.yaml")
predictions = read("predictions-fixture-v1.yaml")

assert validate(inputs, oracle)["status"] == "VALID"
baseline = score(inputs, oracle, predictions)
assert baseline["status"] == "MATCHES_DRAFT_ORACLE"
assert baseline["calibration_claim"] == "NOT_ESTABLISHED"
assert not baseline["oracle_is_expert_validated"]

broken = copy.deepcopy(predictions)
broken["cases"][2]["proposed_requires"].remove("demo.delete-product-policy")
assert score(inputs, oracle, broken)["edge_comparison"]["false_negative"] == 1

unknown = copy.deepcopy(predictions)
unknown["cases"][3]["status"] = "RESOLVED"
assert score(inputs, oracle, unknown)["status"] == "DIFFERS_OR_INCOMPLETE"

leaked = copy.deepcopy(inputs)
leaked["cases"][0]["declared_requires"] = ["demo.product-edit-policy"]
try:
    validate(leaked, oracle)
except ValueError:
    pass
else:
    raise AssertionError("Phase A target-edge leakage must be rejected")

load_driver_modules(["evals.dependency_resolution_scenario_driver"])
result = run_scenario(FIXTURES / "scenarios" / "calibration-scoring.yaml")
assert result.status == "PASSED", result.as_dict()
print("dependency resolution experimental calibration: PASS")
