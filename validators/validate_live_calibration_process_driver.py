#!/usr/bin/env python3
"""Validate live-calibration execution through a Scenario Suite external driver."""
from __future__ import annotations
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scenario_suite import load_driver_modules, run_scenario

INTEGRATION = ROOT / "spec" / "live-calibration-integration"
load_driver_modules(["live_calibration_process_driver"])


def run(name: str, executable: Path, timeout: str = "5"):
    os.environ["HARNESS_LIVE_CALIBRATION_EXECUTABLE"] = str(executable)
    os.environ["HARNESS_LIVE_CALIBRATION_TIMEOUT_SECONDS"] = timeout
    result = run_scenario(INTEGRATION / name)
    assert result.status == "PASSED", result.as_dict()
    return result


first = run("process-execution.yaml", INTEGRATION / "process-evaluator.py")
second = run("process-execution.yaml", INTEGRATION / "process-evaluator-alt.py")

first_obs = first.steps[0]["observations"]
second_obs = second.steps[0]["observations"]
assert first_obs["executable_sha256"] != second_obs["executable_sha256"]
assert first_obs["evaluator_fingerprint"] != second_obs["evaluator_fingerprint"]

run("process-unavailable.yaml", INTEGRATION / "does-not-exist")
run("process-timeout.yaml", INTEGRATION / "process-timeout.py", "0.05")
run("process-failed.yaml", INTEGRATION / "process-failed.py")
run("process-malformed.yaml", INTEGRATION / "process-malformed.py")

print("live calibration external process driver: PASS")
