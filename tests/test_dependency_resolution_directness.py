#!/usr/bin/env python3
"""Source echo / existing transitive access are review signals, not edges."""
from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from evals.project_discovery_directness import audit_additions

productions = {
    "x.product": {"requires": []},
    "x.domain": {"requires": [{"capability": "x.product"}]},
    "x.model-context": {"requires": [{"capability": "x.domain"}]},
    "x.tactical": {"requires": [
        {"capability": "x.model-context"}, {"capability": "x.product"}
    ]},
}
case = {
    "target": {
        "output_obligations": [
            {"id": "mc", "description": "Source-selected model context scope",
             "source": {"capability": "x.model-context"}},
            {"id": "ds", "description": "Source-selected strategic section",
             "source": {"capability": "x.domain"}},
        ],
    },
}
result = {
    "proposed_requires": ["x.product", "x.model-context", "x.domain"],
    "input_needs": [
        {"obligation": "ds", "provider": "x.domain"},
        {"obligation": "mc", "provider": "x.model-context"},
    ],
}
old = {"x.product", "x.model-context"}
audit = audit_additions(case, result, existing_requires=old, productions=productions)
assert len(audit) == 1
x = audit[0]
assert x["provider"] == "x.domain"
assert x["status"] == "DIRECTNESS_UNPROVEN"
assert x["source_echo_obligations"] == ["ds"]
assert x["non_echo_obligations"] == []
assert x["existing_transitive_paths"] == [["x.model-context", "x.domain"]]
assert "SUPPLIER_TEXT_COPIED_INTO_TARGET_OBLIGATION" in x["reasons"]
assert "NO_NON_ECHO_DIRECT_CONSUMPTION_EVIDENCE" in x["reasons"]
assert x["requires_independent_review"]
assert x["automatic_writeback_allowed"] is False

# New neutral target prevents self-citation by construction but cannot
# magically establish the *necessity* of the strategic direct edge.
neutral = {"target": {"output_obligations": [
    {"id": "neutral-tactical-output", "description": "Operator test paraphrase"}
]}}
result_neutral = {
    "proposed_requires": result["proposed_requires"],
    "input_needs": [{"obligation": "neutral-tactical-output", "provider": "x.domain"}],
}
audited = audit_additions(
    neutral, result_neutral, existing_requires=old, productions=productions
)[0]
assert audited["source_echo_obligations"] == []
assert audited["non_echo_obligations"] == ["neutral-tactical-output"]
assert "SUPPLIER_TEXT_COPIED_INTO_TARGET_OBLIGATION" not in audited["reasons"]
assert audited["existing_transitive_paths"] == [["x.model-context", "x.domain"]]
assert audited["status"] == "DIRECTNESS_UNPROVEN"

# A modeled upstream path, without a source-echo, is never a deterministic
# reason to remove an accepted direct prerequisite either.
no_paths = audit_additions(
    neutral, result_neutral,
    existing_requires={"x.product"},
    productions=productions,
)[0]
assert no_paths["existing_transitive_paths"] == []
assert no_paths["status"] == "DIRECTNESS_UNPROVEN"

assert audit_additions(
    neutral,
    {"proposed_requires": sorted(old), "input_needs": []},
    existing_requires=old,
    productions=productions,
) == []
from evals.project_discovery_directness_review import (
    CONTRACT, REQUIRED_TESTS, review_packets, validate_review_record
)

packet_case = {
    "id": "REVIEW-01",
    "target": {
        "capability": "x.tactical",
        "output_obligations": [
            {"id": "ds", "description": "Preserve the strategic meaning used in the scope.",
             "source": {"capability": "x.domain", "path": "docs/domain.md", "heading": "DS-01"}},
            {"id": "mc", "description": "Maintain the distinct domain-level semantic invariant.",
             "source": {"capability": "x.model-context", "path": "docs/context.md", "heading": "MC-01"}},
        ],
    },
    "provider_catalog": [
        {"capability": "x.domain", "evidence_status": "ACCEPTED_EVIDENCE",
         "semantic_surface": ["Accepted strategic domain distinction governed by DS-01."]},
        {"capability": "x.model-context", "evidence_status": "ACCEPTED_EVIDENCE",
         "semantic_surface": ["Accepted model context invariant for the domain distinction."]},
        {"capability": "x.product", "evidence_status": "ACCEPTED_EVIDENCE",
         "semantic_surface": ["Accepted business behavior requiring an invariant."]},
    ],
}
packet_prediction = {
    "proposed_requires": ["x.domain", "x.model-context", "x.product"],
    "input_needs": [
        {"obligation": "ds", "provider": "x.domain", "claim_index": 0,
         "consumption_rationale": "This strategic claim defines the selected DS scope."},
        {"obligation": "mc", "provider": "x.domain", "claim_index": 0,
         "consumption_rationale": "The same strategic statement may constrain the target."},
        {"obligation": "mc", "provider": "x.model-context", "claim_index": 0,
         "consumption_rationale": "This accepted context statement covers model meaning."},
    ],
}
review_audit = audit_additions(
    packet_case, packet_prediction,
    existing_requires=old, productions=productions,
)
packet_list = review_packets(
    packet_case, packet_prediction, accepted_requires=old,
    productions=productions, directness_audit=review_audit,
    source_snapshot="a" * 40,
    target_formulation_authority="ACCEPTED_SOURCE_EXCERPTS",
)
assert len(packet_list) == 1
packet = packet_list[0]
assert packet["contract"] == CONTRACT
assert packet["target_capability"] == "x.tactical"
assert packet["provider"] == "x.domain"
assert packet["existing_transitive_paths"] == [["x.model-context", "x.domain"]]
assert {x["target_obligation_id"] for x in packet["individual_need_evidence"]} == {"ds", "mc"}
mc = next(x for x in packet["individual_need_evidence"]
          if x["target_obligation_id"] == "mc")
assert mc["provider_claim_index"] == 0
assert mc["other_retained_direct_claims_for_same_obligation"][0]["provider"] == "x.model-context"
assert mc["other_retained_direct_claims_for_same_obligation"][0]["accepted_semantic_sufficiency"] == "UNDETERMINED"
assert mc["target_obligation_provenance"]["capability"] == "x.model-context"
assert packet["review_tests"] == list(REQUIRED_TESTS)
assert packet["review_state"] == "AWAITING_INDEPENDENT_ADJUDICATION"
assert packet["automatic_writeback_allowed"] is False

# The independent-review record is an input from an authorized reviewer, not
# model-supplied text. Pure consistency tests cannot validate its semantics.
review = {
    "contract": CONTRACT,
    "case_id": packet["case_id"],
    "target_capability": packet["target_capability"],
    "provider": packet["provider"],
    "source_snapshot": packet["source_snapshot"],
    "reviewer_role": "TARGET_AUTHORITY_OWNER",
    "reviewer_id": "fixture-independent-reviewer",
    "independent_of_evaluator": True,
    "reviewed_target_contract": "ACCEPTED_INDEPENDENTLY",
    "conclusion": "INDETERMINATE",
    "tests": [
        {"test": name, "finding": "INCONCLUSIVE",
         "evidence": "Fixture reviewer has insufficient accepted source evidence to decide necessity."}
        for name in REQUIRED_TESTS
    ],
}
# Source-echo output obligations cannot be self-certified by a review
# record as independently accepted. A truly separate accepted target contract
# is a prerequisite for even recording a complete review decision.
source_echo_review = validate_review_record(packet, review)
assert source_echo_review["status"] == "INVALID"
assert "SOURCE_ECHO_UNRESOLVED" in source_echo_review["failures"]
assert "NO_INDEPENDENT_ACCEPTED_TARGET_SCOPE" in source_echo_review["failures"]
independent_packet = {
    **packet,
    "source_echo_obligations": [],
    "obligation_formulation_authority": "ACCEPTED_INDEPENDENT_TARGET_SCOPE",
}
valid = validate_review_record(independent_packet, review)
assert valid["status"] == "RECORDED_FOR_GOVERNANCE_REVIEW"
assert valid["semantic_correctness_independently_verified_by_code"] is False
assert valid["graph_mutation_authorized"] is False

for key, bad_value in (
    ("source_snapshot", "b" * 40),
    ("reviewed_target_contract", "MODEL_PARAPHRASE"),
    ("independent_of_evaluator", False),
    ("reviewer_id", ""),
):
    altered = dict(review, **{key: bad_value})
    assert validate_review_record(independent_packet, altered)["status"] == "INVALID", key
partial = dict(review, tests=review["tests"][:2])
assert validate_review_record(independent_packet, partial)["status"] == "INVALID"
inconsistent = dict(review, conclusion="DIRECT_REQUIRED")
assert validate_review_record(independent_packet, inconsistent)["status"] == "INVALID"

neutral_packet_case = {
    **packet_case,
    "target": {
        **packet_case["target"],
        "output_obligations": [
            {"id": "mc", "description": "Neutral operational model invariant to investigate."}
        ],
    },
}
neutral_packet_prediction = {
    **packet_prediction,
    "input_needs": [need for need in packet_prediction["input_needs"]
                    if need["obligation"] == "mc"],
}
neutral_audit = audit_additions(
    neutral_packet_case, neutral_packet_prediction,
    existing_requires=old, productions=productions,
)
neutral_review = review_packets(
    neutral_packet_case, neutral_packet_prediction, accepted_requires=old,
    productions=productions, directness_audit=neutral_audit,
    source_snapshot="a" * 40,
    target_formulation_authority="EXPERIMENTAL_OPERATOR_PARAPHRASE_NOT_ACCEPTED",
)[0]
assert neutral_review["individual_need_evidence"][0]["target_obligation_provenance"] == {
    "type": "EXPERIMENTAL_OPERATOR_PARAPHRASE_NOT_ACCEPTED"
}
assert neutral_review["independent_target_obligation_reviewed"] is False
assert neutral_review["candidate_directness"] == "UNDETERMINED"
assert "NO_INDEPENDENT_ACCEPTED_TARGET_SCOPE" in validate_review_record(
    neutral_review, review
)["failures"]

print("dependency resolution directness confound audit: PASS")
