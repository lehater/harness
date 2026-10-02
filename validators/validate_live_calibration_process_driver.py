#!/usr/bin/env python3
"""Validate live-calibration execution through a Scenario Suite external driver."""
from __future__ import annotations
import os
import hashlib
import importlib
import tempfile
from unittest.mock import patch
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scenario_suite import load_driver_modules, run_scenario

INTEGRATION = ROOT / "spec" / "live-calibration-integration"
load_driver_modules(["live_calibration_process_driver"])


def run(name: str, executable: Path, timeout: str = "5"):
    os.environ.pop("HARNESS_LIVE_CALIBRATION_MODULE", None)
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

evidence = first_obs["evaluation"]
assert evidence["run_id"] == "PROCESS-RUN-1"
assert evidence["evaluator"]["adapter"]["executable_sha256"]
assert len(evidence["predictions"]) == 10
assert evidence["calibration"]["confusion"]["false_negative"] == 5

run("process-unavailable.yaml", INTEGRATION / "does-not-exist")
run("process-timeout.yaml", INTEGRATION / "process-timeout.py", "0.05")
run("process-failed.yaml", INTEGRATION / "process-failed.py")
run("process-malformed.yaml", INTEGRATION / "process-malformed.py")

# Exercise real module subprocess transport using deterministic existing fixtures.
import live_calibration_process_driver as driver
real_run = driver.subprocess.run
with tempfile.TemporaryDirectory() as directory:
    root = Path(directory)
    sys.path.insert(0, directory)
    try:
        def invoke_module(argv, **kwargs):
            assert argv == [sys.executable, "-m", "fixture_adapter"]
            assert kwargs["text"] and kwargs["capture_output"]
            assert "shell" not in kwargs
            return real_run(argv, cwd=root, **kwargs)

        def module_run(scenario, fixture, timeout="5"):
            source = root / "fixture_adapter.py"
            source.write_bytes((INTEGRATION / fixture).read_bytes())
            importlib.invalidate_caches()
            os.environ["HARNESS_LIVE_CALIBRATION_MODULE"] = "fixture_adapter"
            os.environ["HARNESS_LIVE_CALIBRATION_TIMEOUT_SECONDS"] = timeout
            with patch.object(driver.subprocess, "run", side_effect=invoke_module):
                result = run_scenario(INTEGRATION / scenario)
            assert result.status == "PASSED", result.as_dict()
            observations = result.steps[0].get("observations")
            if observations is None:
                return None
            assert observations["executable_sha256"] == hashlib.sha256(source.read_bytes()).hexdigest()
            return observations

        one = module_run("process-execution.yaml", "process-evaluator.py")
        two = module_run("process-execution.yaml", "process-evaluator-alt.py")
        assert one["evaluator_fingerprint"] != two["evaluator_fingerprint"]
        assert one["evaluation"]["evaluator"]["adapter"]["module_identity"] == "fixture_adapter"
        module_run("process-timeout.yaml", "process-timeout.py", "0.05")
        module_run("process-failed.yaml", "process-failed.py")
        module_run("process-malformed.yaml", "process-malformed.py")
        os.environ["HARNESS_LIVE_CALIBRATION_MODULE"] = "missing_fixture_adapter"
        result = run_scenario(INTEGRATION / "process-unavailable.yaml")
        assert result.status == "PASSED", result.as_dict()
    finally:
        sys.path.remove(directory)
        os.environ.pop("HARNESS_LIVE_CALIBRATION_MODULE", None)

print("live calibration external process driver: PASS")
