#!/usr/bin/env python3
"""Source routing is a deduplicated reviewer queue, never an ownership verdict."""
from __future__ import annotations

import copy
import hashlib
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from evals.project_discovery_snapshot import DiscoveryError
from evals.project_target_responsibility_routing import (
    TRACKS, EFFECTS, build_routing_worksheet, validate_unaccepted_review_draft,
)

SHA = "a" * 40
SOURCE_HASH = "b" * 64

def unit(local: str, heading: str | None, role: str, kind: str, *,
         path: str="docs/accepted.md", text: str | None=None):
    statement = text or f"Accepted source meaning about {local} for the reader."
    uid = hashlib.sha256(
        (path + "\n" + str(heading) + "\n" + local + "\n" + statement).encode()
    ).hexdigest()[:20]
    return {
        "source_unit_id": uid, "source_path": path,
        "source_sha256": SOURCE_HASH, "source_heading": heading,
        "source_local_id": local, "source_provider": "x.accepted",
        "review_revision": 1, "scope_role": role,
        "source_text": statement, "source_unit_kind": kind,
        "candidate_obligations_with_same_source_section": (
            ["X-OBLIGATION"] if heading and heading.startswith("MC-") else []
        ),
        "unit_semantic_disposition": "UNREVIEWED",
        "output_obligation_fulfilment_verified": False,
        "target_authority_approved": False,
    }

pi = unit("0", "MC-01 Preparation Information", "MODEL_CONTEXT",
          "ACCEPTED_SOURCE_SECTION_STATEMENT")
rh = unit("1", "MC-02 Recorded Activity History", "MODEL_CONTEXT",
          "ACCEPTED_SOURCE_SECTION_STATEMENT")
cross = unit("2", "TR-01 Preparation Information and Recorded Activity History",
             "CROSS_CONTEXT", "ACCEPTED_SOURCE_SECTION_STATEMENT")
consumer = unit("3", "Consumers", "APPLICATION_SEPARATION",
                "ACCEPTED_SOURCE_SECTION_STATEMENT")
p1 = unit("REQ-1", None, "PRODUCT_CONSTRAINTS",
          "ACCEPTED_PRODUCT_REQUIREMENT", path="docs/product.yaml")
p2 = unit("REQ-2", None, "PRODUCT_CONSTRAINTS",
          "ACCEPTED_PRODUCT_REQUIREMENT", path="docs/product.yaml")
non_goal = unit("NON_GOAL-01", None, "PRODUCT_CONSTRAINTS",
                "PRODUCT_NON_GOAL", path="docs/product.yaml")
source_cases = [
    {"target_capability": "x.pi", "status": "PENDING_SEMANTIC_SCOPE_REVIEW",
     "source_units": [pi, cross, consumer, p1, p2, non_goal],
     "source_unit_count": 6, "accepted_target_contract_established": False,
     "semantic_completeness_established": False},
    {"target_capability": "x.rh", "status": "PENDING_SEMANTIC_SCOPE_REVIEW",
     "source_units": [rh, cross, consumer, p1, p2, non_goal],
     "source_unit_count": 6, "accepted_target_contract_established": False,
     "semantic_completeness_established": False},
]
inventory = {
    "kind": "harness-cdr-target-scope-coverage-inventory",
    "status": "PENDING_INDEPENDENT_TARGET_SCOPE_REVIEW",
    "source_snapshot": SHA, "cases": source_cases,
    "complete_target_output_semantics_proven": False,
    "independent_authority_review_performed": False,
    "automatic_writeback_allowed": False,
}
hypotheses = {
    "kind": "harness-cdr-product-routing-hypotheses",
    "status": "OPERATOR_DRAFT_NOT_ACCEPTED",
    "source_commit": SHA, "automatic_writeback_allowed": False,
    "product_requirements": [
        {"requirement_id": "REQ-1",
         "candidate_tracks": ["PREPARATION_INFORMATION", "APPLICATION_DESIGN"],
         "review_question": "Which semantic or application owner must satisfy this accepted requirement?",
         "status": "CANDIDATE_NOT_ACCEPTED"},
        {"requirement_id": "REQ-2",
         "candidate_tracks": ["RECORDED_ACTIVITY_HISTORY", "SHARED_CROSS_CONTEXT"],
         "review_question": "How does the accepted requirement constrain historical facts or their cross-context references?",
         "status": "CANDIDATE_NOT_ACCEPTED"},
    ],
}
report = build_routing_worksheet(inventory, product_proposals=hypotheses)
assert report["status"] == "PENDING_INDEPENDENT_RESPONSIBILITY_REVIEW"
assert report["distinct_source_unit_count"] == 7
assert report["duplicated_across_targets"] == 5
assert report["accepted_product_requirement_count"] == 2
assert report["unit_semantics_reviewed"] == 0
assert report["independent_responsibility_adjudication_performed"] is False
assert report["all_target_output_obligations_covered"] is False
assert report["automatic_writeback_allowed"] is False
assert set(report["per_source_unit_route_set"]) == set(TRACKS)
assert set(report["per_source_unit_effect_set"]) == set(EFFECTS)
m = {v["source_unit_id"]: v for v in report["source_units"]}
assert m[pi["source_unit_id"]]["provisional_responsibility_tracks"] == ["PREPARATION_INFORMATION"]
assert m[rh["source_unit_id"]]["provisional_responsibility_tracks"] == ["RECORDED_ACTIVITY_HISTORY"]
assert m[cross["source_unit_id"]]["provisional_responsibility_tracks"] == ["SHARED_CROSS_CONTEXT"]
assert m[consumer["source_unit_id"]]["semantic_route"] == "UNDETERMINED"
assert m[consumer["source_unit_id"]]["provisional_responsibility_tracks"] == [
    "APPLICATION_DESIGN", "SHARED_CROSS_CONTEXT"
]
assert m[p1["source_unit_id"]]["provisional_responsibility_tracks"] == [
    "PREPARATION_INFORMATION", "APPLICATION_DESIGN"
]
assert m[p1["source_unit_id"]]["hint_is_semantic_evidence"] is False
assert m[non_goal["source_unit_id"]]["semantic_effect"] == "UNDETERMINED"
assert len(m[cross["source_unit_id"]]["seen_by_target_capabilities"]) == 2
assert m[pi["source_unit_id"]]["seen_by_target_capabilities"] == ["x.pi"]
assert report["source_snapshot"] == SHA

# A drafted row may cover one source unit or all of them, but cannot
# claim the independent target obligation contract was accepted.
def review_row(v):
    return {
        "source_unit_id": v["source_unit_id"],
        "source_sha256": v["source_sha256"],
        "source_provider": v["source_provider"],
        "proposed_route": "UNDETERMINED",
        "proposed_effect": "UNDETERMINED",
        "affected_targets": list(v["seen_by_target_capabilities"]),
        "rationale": "A source-cited reviewer still needs to determine semantic ownership.",
        "state": "NEEDS_AUTHORITY_REVIEW",
    }

draft_review = {
    "kind": "harness-cdr-source-routing-review-draft",
    "status": "OPERATOR_DRAFT_NOT_ACCEPTED", "source_snapshot": SHA,
    "automatic_writeback_allowed": False,
    "assessments": [review_row(v) for v in report["source_units"]],
}
full = validate_unaccepted_review_draft(report, draft_review)
assert full["status"] == "DRAFT_COMPLETE_FOR_REVIEW"
assert full["rows_present"] == 7
assert full["independent_authority_review_performed"] is False
assert full["target_output_contract_accepted"] is False
assert full["automatic_writeback_allowed"] is False
partial = copy.deepcopy(draft_review)
partial["assessments"].pop()
assert validate_unaccepted_review_draft(report, partial)["status"] == "DRAFT_PARTIAL_FOR_REVIEW"

def must_fail(action, expected):
    try:
        action()
    except DiscoveryError as error:
        assert expected in str(error), str(error)
    else:
        raise AssertionError("Expected hard failure: " + expected)

tampered = copy.deepcopy(inventory)
tampered["cases"][1]["source_units"][1]["source_text"] = "Different semantic claim with reused ID!"
must_fail(lambda: build_routing_worksheet(tampered), "inconsistent source provenance")
tampered = copy.deepcopy(inventory)
tampered["cases"][0]["source_units"][0]["unit_semantic_disposition"] = "ACCEPTED"
must_fail(lambda: build_routing_worksheet(tampered), "prematurely adjudicated")
tampered = copy.deepcopy(inventory)
tampered["cases"][1]["source_units"].append(copy.deepcopy(cross))
tampered["cases"][1]["source_unit_count"] += 1
must_fail(lambda: build_routing_worksheet(tampered), "duplicate/invalid")
tampered = copy.deepcopy(hypotheses)
tampered["product_requirements"].pop()
must_fail(lambda: build_routing_worksheet(inventory, product_proposals=tampered), "cover every")
tampered = copy.deepcopy(hypotheses)
tampered["product_requirements"].append(copy.deepcopy(tampered["product_requirements"][0]))
must_fail(lambda: build_routing_worksheet(inventory, product_proposals=tampered), "duplicate product")
tampered = copy.deepcopy(hypotheses)
tampered["product_requirements"][0]["status"] = "ACCEPTED"
must_fail(lambda: build_routing_worksheet(inventory, product_proposals=tampered), "assert acceptance")
tampered = copy.deepcopy(hypotheses)
tampered["source_commit"] = "0" * 40
must_fail(lambda: build_routing_worksheet(inventory, product_proposals=tampered), "not pinned")
tampered = copy.deepcopy(draft_review)
tampered["assessments"][0]["source_sha256"] = "f" * 64
must_fail(lambda: validate_unaccepted_review_draft(report, tampered), "identity mismatch")
tampered = copy.deepcopy(draft_review)
tampered["assessments"][0]["state"] = "ACCEPTED"
must_fail(lambda: validate_unaccepted_review_draft(report, tampered), "self-adjudication")
tampered = copy.deepcopy(draft_review)
tampered["assessments"].append(copy.deepcopy(tampered["assessments"][0]))
must_fail(lambda: validate_unaccepted_review_draft(report, tampered), "duplicate reviewed")
print("dependency resolution source responsibility routing: PASS")
