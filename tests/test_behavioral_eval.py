#!/usr/bin/env python3
"""Validate the behavioral-evaluation substrate without a live model call."""
from __future__ import annotations

import copy
import json
import shutil
import sys
import tempfile
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from evals.behavioral_eval import (
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

E04_TEMPLATE = (
    ROOT
    / "spec"
    / "behavioral-evals"
    / "first-wave"
    / "cases"
    / "td-boot-e04"
    / "case.yaml.tmpl"
)


class BootstrapSequenceAdapter:
    def __init__(self) -> None:
        self.requests: list[dict] = []

    def execute(self, request: dict, *, agent_descriptor: dict) -> dict:
        del agent_descriptor
        self.requests.append(copy.deepcopy(request))
        model = {
            "authorities": [{"id": "PAYMENT-DESIGN"}],
            "artifacts": [{
                "id": "PAYMENT-API",
                "authority": "PAYMENT-DESIGN",
                "path": "docs/payment-api.md",
                "provides": ["payment.idempotency-contract"],
                "depends_on": [],
            }],
            "questions": [],
        }
        from harness.project_model.target_state import evaluate_target_state
        target = evaluate_target_state(
            request["repository_fixture"]["reviewed_design_profile"],
            model,
        )
        return {
            "version": 1,
            "kind": "harness-agent-behavioral-eval-response",
            "run_status": "COMPLETED",
            "output": {"core_model": model, "target_state": target},
            "provenance": {
                "fresh_home": True,
                "isolated_working_directory": True,
            },
        }


with tempfile.TemporaryDirectory(prefix="behavioral-e04-sequence-") as temp:
    temp_root = Path(temp)
    shutil.copytree(E04_TEMPLATE.parent, temp_root / "case")
    e04_runtime = temp_root / "case" / "case.yaml"
    e04_runtime.write_text(
        (temp_root / "case" / "case.yaml.tmpl")
        .read_text(encoding="utf-8")
        .replace("__HARNESS_REVISION__", "a" * 40),
        encoding="utf-8",
    )
    e04_binding = load_case(e04_runtime)
    sequence_adapter = BootstrapSequenceAdapter()
    sequence_records = execute_case(
        e04_binding,
        adapter=sequence_adapter,
        agent_descriptor=descriptor,
        agent_descriptor_sha256=descriptor_sha,
        output_dir=temp_root / "runs",
    )
    assert len(sequence_records) == 2
    assert all(item["correctness"]["status"] == "PASS" for item in sequence_records)
    assert sequence_records[0]["execution_context"]["phase"] == "bootstrap"
    assert sequence_records[1]["execution_context"]["phase"] == "reconcile-existing"
    assert (
        sequence_records[1]["derived_input_binding"]["prior_run_record_sha256"]
        == sequence_records[0]["record_sha256"]
    )
    assert sequence_records[1]["derived_input_binding"]["core_model_sha256"]
    second_fixture = sequence_adapter.requests[1]["repository_fixture"]
    assert second_fixture["existing_project"]["harness_realization"] == (
        "current-and-usable"
    )
    assert second_fixture["existing_project"]["current_harness_realization"]

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
