#!/usr/bin/env python3
"""Non-provider regression for pre-existing four synthetic CDR holdouts."""
from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from evals.cdr_direction_holdout import build, reconcile

fixture = build(ROOT)
req, source = fixture["request"], fixture["inputs"]
assert len(req["cases"]) == len(source["cases"]) == 4
assert [x["id"] for x in source["cases"]] == [f"CDR-{n:02d}" for n in range(1, 5)]
assert req["request_id"] == build(ROOT)["request"]["request_id"]
assert "baseline_requires" not in json.dumps(req)
assert "expected_requires" not in json.dumps(req)
assert "expected_direct_needs" not in json.dumps(req)
assert "review_status" not in json.dumps(req)
assert all("requires" not in c["target"] for c in req["cases"])
assert fixture["authority_acceptance"] is False

reply = {
    "kind": "harness-dependency-resolution-evaluator-response",
    "version": 1,
    "request_id": req["request_id"],
    "provenance": {"provider": "synthetic-test-only"},
    "results": [
        {"case_request_id": case["case_request_id"],
         "status": "UNRESOLVED",
         "proposed_requires": [],
         "input_needs": [],
         "unresolved_obligations": [ob["id"] for ob in case["target"]["output_obligations"]]}
        for case in req["cases"]
    ],
}
result = reconcile(ROOT, inputs=source, request=req, response=reply)
assert result["status"] == "UNVERIFIED_AUTHOR_DRAFT_COMPARISON"
assert result["comparison"]["status"] == "DIFFERS_OR_INCOMPLETE"
assert result["comparison"]["oracle_is_expert_validated"] is False
assert result["automatic_writeback_allowed"] is False
assert result["comparison"]["calibration_claim"] == "NOT_ESTABLISHED"
assert len(result["comparison"]["cases"]) == 4

# A known direct-and-transitive supplier pair is represented as model claims
# without promoting operator-authored expectations to accepted ground truth.
test_case = copy.deepcopy(reply)
t = req["cases"][2]
test_case["results"][2] = {
    "case_request_id": t["case_request_id"],
    "status": "RESOLVED",
    "proposed_requires": ["demo.delete-product-policy", "demo.delete-task"],
    "input_needs": [
        {"obligation": "enforce-delete-policy", "provider": "demo.delete-product-policy"},
        {"obligation": "implement-delete-task", "provider": "demo.delete-task"},
    ],
    "unresolved_obligations": [],
}
matched = reconcile(ROOT, inputs=source, request=req, response=test_case)
assert matched["comparison"]["cases"][2]["status"] == "MATCHES_DRAFT_ORACLE"
assert matched["comparison"]["oracle_is_expert_validated"] is False

for field in ["request", "response"]:
    bad = copy.deepcopy(req if field == "request" else reply)
    bad["request_id"] = "bad"
    try:
        reconcile(ROOT, inputs=source,
                  request=bad if field == "request" else req,
                  response=bad if field == "response" else reply)
    except ValueError:
        pass
    else:
        raise AssertionError(f"{field} mismatched request must be rejected")

incomplete = copy.deepcopy(reply)
incomplete["results"].pop()
try:
    reconcile(ROOT, inputs=source, request=req, response=incomplete)
except ValueError:
    pass
else:
    raise AssertionError("incomplete response should fail")
print("CDR authored synthetic directional holdout: PASS")
