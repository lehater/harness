#!/usr/bin/env python3
"""Validate the provider adapter boundary without making a live model call."""
from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from adapters.copilot_live_calibration_evaluator import (
    _model_payload,
    _parse_model_response,
)
from live_calibration import (
    build_live_calibration_request,
    evaluate_live_calibration_run,
)

CORPUS = yaml.safe_load(
    (ROOT / "spec/semantic-derivation/calibration-corpus-v1.yaml").read_text(
        encoding="utf-8"
    )
)
PROTOCOL = yaml.safe_load(
    (ROOT / "spec/semantic-derivation/live-calibration-protocol-v1.yaml").read_text(
        encoding="utf-8"
    )
)
EVALUATOR = {
    "version": 1,
    "kind": "harness-semantic-evaluator-descriptor",
    "id": "github-copilot-gpt-5.3-codex",
    "provider": "github-copilot",
    "model": "gpt-5.3-codex",
    "model_version": "UNREPORTED",
    "configuration": {
        "requested_model": "gpt-5.3-codex",
        "copilot_cli_version": "1.0.86",
        "provider_timeout_seconds": 150,
    },
    "adapter": {
        "id": "process-json",
        "version": "1",
        "provider_adapter": {
            "id": "github-copilot-cli-live-calibration",
            "version": "1",
        },
    },
}

request = build_live_calibration_request(
    corpus=CORPUS,
    protocol=PROTOCOL,
    evaluator=EVALUATOR,
    run_id="ADAPTER-BOUNDARY-1",
)
process_request = {
    "version": 1,
    "kind": "harness-live-semantic-evaluator-request",
    "request_id": request["request_id"],
    "run_id": request["run_id"],
    "protocol": request["protocol"],
    "evaluator": EVALUATOR,
    "cases": request["cases"],
}

model_payload = _model_payload(process_request)
assert set(model_payload) == {
    "protocol_instruction",
    "cases",
    "response_contract",
}
assert len(model_payload["cases"]) == len(CORPUS["cases"])
for case in model_payload["cases"]:
    assert set(case) == {"case_request_id", "source", "target", "relation"}

rendered = json.dumps(model_payload, ensure_ascii=False)
assert "expected_status" not in rendered
assert "mutation_class" not in rendered
for canonical in (case["id"] for case in CORPUS["cases"]):
    assert canonical not in rendered

valid_results = [
    {"case_request_id": case["case_request_id"], "status": "ACCEPTED"}
    for case in request["cases"]
]
valid_envelope = {
    "version": 1,
    "kind": "harness-live-semantic-evaluator-response",
    "results": valid_results,
}
parsed = _parse_model_response(json.dumps(valid_envelope))
assert parsed["results"] == valid_results

for malformed in (
    "not json",
    '{"version":1,"kind":"wrong","results":[]}',
    '{"version":1,"kind":"harness-live-semantic-evaluator-response"}',
):
    try:
        _parse_model_response(malformed)
    except ValueError:
        pass
    else:
        raise AssertionError(f"malformed provider response accepted: {malformed}")

def evaluate(results):
    run = {
        "version": 1,
        "kind": "harness-live-semantic-calibration-run",
        "run_id": request["run_id"],
        "request_id": request["request_id"],
        "state": "COMPLETED",
        "results": results,
    }
    return evaluate_live_calibration_run(
        corpus=CORPUS,
        protocol=PROTOCOL,
        evaluator=EVALUATOR,
        run=run,
    )

missing = evaluate(valid_results[:-1])
assert missing["status"] == "INCOMPLETE"

duplicate_results = copy.deepcopy(valid_results)
duplicate_results.append(copy.deepcopy(valid_results[0]))
duplicate = evaluate(duplicate_results)
assert duplicate["status"] == "INVALID"
assert duplicate["findings"][0]["code"] == "LIVE_CALIBRATION_DUPLICATE_RESULT"

unknown_results = copy.deepcopy(valid_results)
unknown_results[0]["case_request_id"] = "LCCASE-UNKNOWN"
unknown = evaluate(unknown_results)
assert unknown["status"] == "INVALID"
assert unknown["findings"][0]["code"] == "LIVE_CALIBRATION_UNKNOWN_CASE_BINDING"

invalid_status_results = copy.deepcopy(valid_results)
invalid_status_results[0]["status"] = "MAYBE"
invalid_status = evaluate(invalid_status_results)
assert invalid_status["status"] == "INVALID"
assert invalid_status["findings"][0]["code"] == "LIVE_CALIBRATION_VERDICT_INVALID"

print("GitHub Copilot live calibration adapter boundary: PASS")
