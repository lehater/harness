#!/usr/bin/env python3
"""Validate the behavioral-evaluation substrate without a live model call."""
from __future__ import annotations

import copy
import json
import sys
import tempfile
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from behavioral_eval import (
    BehavioralEvalError,
    ProcessExecutionAdapter,
    build_execution_request,
    build_run_record,
    execute_case,
    load_agent_descriptor,
    load_case,
    normalize_result,
    score_result,
    write_run_record,
)

INTEGRATION = ROOT / "spec" / "behavioral-eval-integration"
CASE = INTEGRATION / "case.yaml"
DESCRIPTOR = INTEGRATION / "agent-descriptor.yaml"
STUB = INTEGRATION / "stub-agent.py"

binding = load_case(CASE)
descriptor, descriptor_sha = load_agent_descriptor(DESCRIPTOR)
request = build_execution_request(binding, run_id="SUBSTRATE-REQUEST-1", agent_descriptor=descriptor, agent_descriptor_sha256=descriptor_sha)
rendered = json.dumps(request, sort_keys=True)
assert "oracle_ref" not in rendered
assert "pass_criteria" not in rendered
assert "oracle_sha256" not in rendered
assert "previous_runs" not in rendered

adapter = ProcessExecutionAdapter(sys.executable, [str(STUB)], timeout_seconds=5)
response = adapter.execute(request, agent_descriptor=descriptor)
assert response["run_status"] == "COMPLETED", response
assert response["provenance"]["fresh_home"] is True
assert response["provenance"]["isolated_working_directory"] is True
normalized = normalize_result(binding, response)
assert normalized["capability_partition"] == [["E1", "E2"]]
assert score_result(binding, normalized)["status"] == "PASS"

record = build_run_record(binding, run_id="SUBSTRATE-REQUEST-1", agent_descriptor=descriptor, agent_descriptor_sha256=descriptor_sha, response=response)
assert record["started_from_clean_context"] is True
assert record["run_status"] == "COMPLETED"
assert record["correctness"]["status"] == "PASS"
assert record["record_sha256"]

with tempfile.TemporaryDirectory(prefix="behavioral-eval-record-") as temp:
    path = Path(temp) / "run.json"
    write_run_record(path, record)
    try:
        write_run_record(path, record)
    except FileExistsError:
        pass
    else:
        raise AssertionError("run record overwrite must fail")
    records = execute_case(binding, adapter=adapter, agent_descriptor=descriptor, agent_descriptor_sha256=descriptor_sha, output_dir=Path(temp) / "runs")
    assert len(records) == 1 and records[0]["correctness"]["status"] == "PASS"

for mode, expected in (("malformed", "INVALID"), ("reasoning", "INVALID"), ("fail", "EXECUTION_ERROR"), ("incomplete", "INCOMPLETE")):
    response = ProcessExecutionAdapter(sys.executable, [str(STUB), "--mode", mode], timeout_seconds=5).execute(request, agent_descriptor=descriptor)
    assert response["run_status"] == expected, (mode, response)

bad_case = copy.deepcopy(binding.case)
bad_case.pop("oracle_ref")
with tempfile.TemporaryDirectory(prefix="behavioral-eval-case-") as temp:
    path = Path(temp) / "case.yaml"
    path.write_text(yaml.safe_dump(bad_case, sort_keys=False), encoding="utf-8")
    try:
        load_case(path)
    except BehavioralEvalError as exc:
        assert "oracle_ref" in str(exc)
    else:
        raise AssertionError("case missing oracle_ref was accepted")

print("behavioral eval substrate: PASS")
