#!/usr/bin/env python3
"""Validate live-calibration execution through a Scenario Suite external driver."""
from __future__ import annotations
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scenario_suite import load_driver_modules, run_scenario

fixture = ROOT / "spec" / "live-calibration-integration" / "process-evaluator.py"
scenario = ROOT / "spec" / "live-calibration-integration" / "process-execution.yaml"

os.environ["HARNESS_LIVE_CALIBRATION_EXECUTABLE"] = str(fixture)
os.environ["HARNESS_LIVE_CALIBRATION_TIMEOUT_SECONDS"] = "5"
load_driver_modules(["live_calibration_process_driver"])
result = run_scenario(scenario)
assert result.status == "PASSED", result.as_dict()
print("live calibration external process driver: PASS")
