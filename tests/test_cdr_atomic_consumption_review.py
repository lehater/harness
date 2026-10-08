#!/usr/bin/env python3
"""Atomic CDR claim-to-output consumption remains non-authoritative."""
from __future__ import annotations

import copy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from evals.cdr_atomic_consumption_review import review_atomic_needs, TESTS

case = {
    "id": "PREP-TEST",
    "target": {
        "capability": "demo.target",
        "output_obligations": [
            {"id": "O-1"}, {"id": "O-2"}, {"id": "O-3"}
        ],
    },
    "provider_catalog": [{
        "capability": "demo.source",
        "evidence_status": "CONTRACT_ONLY",
        "semantic_surface": ["RESEARCH ATOMIC OWNED-EXPORT CANDIDATE [A-1]: Source defines independent meaning"],
        "source_scope": {
            "claim_ids": ["A-1"],
            "claim_role": "UNACCEPTED_OWNED_EXPORT_CANDIDATE",
            "selection_scope_partial": True,
        },
    }],
}
prediction = {
    "status": "RESOLVED",
    "input_needs": [{
        "obligation": "O-1", "provider": "demo.source", "claim_index": 0,
        "consumption_rationale": "Unverified model argument about target input",
    }, {
        "obligation": "O-2", "provider": "demo.source", "claim_index": 0,
        "consumption_rationale": "Unverified second model argument about target input",
    }],
    "unresolved_obligations": [],
}
delegations = [{
    "source_capability": "demo.source", "claim_id": "A-DELEGATE",
    "delegates_to_capability": "demo.target",
}]
result = review_atomic_needs(case, prediction, delegations)
assert result["status"] == "REVIEW_REQUIRED_NONAUTHORITATIVE"
assert result["model_status_preserved"] == "RESOLVED"
assert result["unaccounted_obligations"] == ["O-3"]
assert result["per_obligation"][2]["status"] == "UNACCOUNTED_NO_NONAPPLICABILITY_JUSTIFICATION"
assert result["per_obligation"][0]["candidate_needs"][0]["atomic_claim_id"] == "A-1"
assert result["per_obligation"][0]["candidate_needs"][0]["related_delegation_claim_ids"] == ["A-DELEGATE"]
assert result["per_obligation"][0]["candidate_needs"][0]["semantic_directness_decision"] == "UNREVIEWED"
assert {x["test"] for x in result["per_obligation"][0]["candidate_needs"][0]["test_results"]} == set(TESTS)
assert all(x["result"] == "NOT_INDEPENDENTLY_VERIFIED" for x in result["per_obligation"][0]["candidate_needs"][0]["test_results"])
assert result["automatic_writeback_allowed"] is False
assert result["independent_target_acceptance_proven"] is False
assert result == review_atomic_needs(case, prediction, delegations)

unresolved = copy.deepcopy(prediction)
unresolved["status"] = "UNRESOLVED"
unresolved["unresolved_obligations"] = ["O-3"]
unresolved_result = review_atomic_needs(case, unresolved, delegations)
assert unresolved_result["unaccounted_obligations"] == []
assert unresolved_result["per_obligation"][2]["status"] == "UNRESOLVED_NO_PROVEN_PROVIDER"

bad = copy.deepcopy(prediction)
bad["input_needs"][0]["claim_index"] = 42
try:
    review_atomic_needs(case, bad, delegations)
except ValueError:
    pass
else:
    raise AssertionError("unbound atomic citation accepted")
print("CDR atomic need-to-output coverage review: PASS")
