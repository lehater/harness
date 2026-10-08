"""Generate independent directness review packets from already-blind evidence.

A packet is a list of QUESTIONS backed by cited, accepted claims, not a new
oracle, evaluator instruction, semantic verdict or permission to alter graph.
It is generated only after the evaluator finishes and graph reconciliation
begins; never supplied back as target context to the evaluated agent.
"""
from __future__ import annotations

from typing import Any

CONTRACT = "independent-directness-review-v1"
REQUIRED_TESTS = (
    "INDEPENDENT_TARGET_OUTPUT_OBLIGATION",
    "MATERIAL_ACCEPTED_RULE_CONSUMPTION",
    "INTERMEDIATE_CONTRACT_SUFFICIENCY",
    "DIRECT_PROVIDER_CHANGE_SENSITIVITY",
    "AUTHORITY_REVIEW_AND_REVISION",
)


def review_packets(
    case: dict[str, Any],
    prediction: dict[str, Any],
    *,
    accepted_requires: set[str],
    productions: dict[str, dict[str, Any]],
    directness_audit: list[dict[str, Any]],
    source_snapshot: str,
    target_formulation_authority: str,
) -> list[dict[str, Any]]:
    """Represent what a reviewer must actually decide for each proposed ADD.

    NOTE: Claim existence is checked upstream, not semantic entailment.
    The packet deliberately does not fill a review verdict from model prose.
    """
    by_provider = {p["capability"]: p for p in case["provider_catalog"]}
    obligations = {
        o["id"]: o for o in case["target"]["output_obligations"]
    }
    predicted_needs = prediction.get("input_needs", [])
    kept = sorted(accepted_requires & set(prediction["proposed_requires"]))
    records = []
    for audit in directness_audit:
        supplier = audit["provider"]
        evidence = []
        for need in predicted_needs:
            if need.get("provider") != supplier:
                continue
            ob = obligations[need["obligation"]]
            claim = by_provider[supplier]["semantic_surface"][need["claim_index"]]
            alternative_citations = []
            for other in predicted_needs:
                if other.get("obligation") != need["obligation"]:
                    continue
                if other.get("provider") not in kept:
                    continue
                competing = by_provider[other["provider"]]
                alternative_citations.append({
                    "provider": other["provider"],
                    "claim_index": other["claim_index"],
                    "claim_text": competing["semantic_surface"][other["claim_index"]],
                    "evaluator_rationale": other.get("consumption_rationale", ""),
                    "accepted_semantic_sufficiency": "UNDETERMINED",
                })
            evidence.append({
                "target_obligation_id": ob["id"],
                "target_obligation_text": ob["description"],
                "target_obligation_provenance": (
                    ob.get("source", {})
                    if isinstance(ob.get("source"), dict)
                    else {"type": target_formulation_authority}
                ),
                "provider_claim_index": need["claim_index"],
                "provider_claim_text": claim,
                "provider_evidence_status": by_provider[supplier]["evidence_status"],
                "evaluator_rationale": need.get("consumption_rationale", ""),
                "other_retained_direct_claims_for_same_obligation": alternative_citations,
                "review_questions": [
                    {
                        "test": "INDEPENDENT_TARGET_OUTPUT_OBLIGATION",
                        "question": (
                            "Was the specific tactical output obligation accepted by "
                            "its owning Authority independently of this provider's text?"
                        ),
                    },
                    {
                        "test": "MATERIAL_ACCEPTED_RULE_CONSUMPTION",
                        "question": (
                            "What distinct governed rule or invariant from this "
                            "provider must this output actually preserve? The "
                            "provider's mention of the same topic is insufficient."
                        ),
                    },
                    {
                        "test": "INTERMEDIATE_CONTRACT_SUFFICIENCY",
                        "question": (
                            "Could the accepted meaning from retained immediate "
                            "providers fully discharge this exact obligation? "
                            "Review cited alternative claims and the accepted "
                            "intermediate provider public contract, not just paths."
                        ),
                    },
                    {
                        "test": "DIRECT_PROVIDER_CHANGE_SENSITIVITY",
                        "question": (
                            "Identify a concrete change to the direct candidate's "
                            "accepted semantic contract that would require a change "
                            "to this target despite the retained intermediates' "
                            "accepted contracts remaining unchanged."
                        ),
                    },
                    {
                        "test": "AUTHORITY_REVIEW_AND_REVISION",
                        "question": (
                            "Which owning Authority approves this target obligation "
                            "and the directness judgment, against which immutable "
                            "source revision? Is reviewer independent of evaluator?"
                        ),
                    },
                ],
            })
        records.append({
            "contract": CONTRACT,
            "case_id": case["id"],
            "target_capability": case["target"]["capability"],
            "provider": supplier,
            "source_snapshot": source_snapshot,
            "obligation_formulation_authority": target_formulation_authority,
            "kept_existing_direct_providers": kept,
            "existing_transitive_paths": audit["existing_transitive_paths"],
            "source_echo_obligations": audit["source_echo_obligations"],
            "individual_need_evidence": evidence,
            "review_tests": list(REQUIRED_TESTS),
            "review_state": "AWAITING_INDEPENDENT_ADJUDICATION",
            "independent_target_obligation_reviewed": False,
            "intermediate_semantic_sufficiency_reviewed": False,
            "candidate_directness": "UNDETERMINED",
            "semantic_entailment_verified": False,
            "automatic_writeback_allowed": False,
        })
    return records


def validate_review_record(
    packet: dict[str, Any], review: dict[str, Any]
) -> dict[str, Any]:
    """Check review *process completeness*, never assert semantic correctness.

    Only a separately performed owner-authorized assessment, explicitly pinned
    to the packet, may be recorded. A structurally complete record is NOT a
    merge permission, graph update, or automatically approved dependency.
    """
    failures = []
    if review.get("contract") != CONTRACT:
        failures.append("WRONG_REVIEW_CONTRACT")
    for key in ("case_id", "target_capability", "provider", "source_snapshot"):
        if review.get(key) != packet.get(key):
            failures.append("MISMATCH_" + key.upper())
    if review.get("reviewer_role") not in ("TARGET_AUTHORITY_OWNER", "AUTHORIZED_SEMANTIC_REVIEWER"):
        failures.append("MISSING_AUTHORIZED_REVIEW_ROLE")
    reviewer = review.get("reviewer_id")
    if not isinstance(reviewer, str) or len(reviewer.strip()) < 3:
        failures.append("MISSING_REVIEWER_ID")
    if review.get("independent_of_evaluator") is not True:
        failures.append("NO_REVIEWER_INDEPENDENCE_ATTESTATION")
    if review.get("reviewed_target_contract") != "ACCEPTED_INDEPENDENTLY":
        failures.append("TARGET_OBLIGATION_NOT_ACCEPTED_INDEPENDENTLY")
    statements = review.get("tests")
    if not isinstance(statements, list):
        statements = []
    found = set()
    for row in statements:
        if not isinstance(row, dict) or row.get("test") not in REQUIRED_TESTS:
            failures.append("INVALID_REVIEW_TEST")
            continue
        name = row["test"]
        if name in found:
            failures.append("DUPLICATE_REVIEW_TEST")
        found.add(name)
        if row.get("finding") not in ("SUPPORTS_DIRECT", "SUPPORTS_INHERITED", "INCONCLUSIVE"):
            failures.append("INVALID_REVIEW_FINDING")
        if not isinstance(row.get("evidence"), str) or len(row["evidence"].strip()) < 35:
            failures.append("MISSING_SUBSTANTIVE_REVIEW_EVIDENCE")
    if found != set(REQUIRED_TESTS):
        failures.append("INCOMPLETE_REVIEW_TESTS")
    conclusion = review.get("conclusion")
    if conclusion not in ("DIRECT_REQUIRED", "INHERITED_SUFFICIENT", "NOT_DIRECT", "INDETERMINATE"):
        failures.append("INVALID_REVIEW_CONCLUSION")
    if conclusion == "DIRECT_REQUIRED" and any(
        row.get("finding") != "SUPPORTS_DIRECT"
        for row in statements if isinstance(row, dict)
    ):
        failures.append("DIRECT_CONCLUSION_CONFLICTS_WITH_REVIEW_FINDINGS")
    if conclusion in ("INHERITED_SUFFICIENT", "NOT_DIRECT") and any(
        row.get("finding") != "SUPPORTS_INHERITED"
        for row in statements if isinstance(row, dict)
    ):
        failures.append("INDIRECT_CONCLUSION_CONFLICTS_WITH_REVIEW_FINDINGS")
    return {
        "status": "RECORDED_FOR_GOVERNANCE_REVIEW" if not failures else "INVALID",
        "failures": sorted(set(failures)),
        "semantic_correctness_independently_verified_by_code": False,
        "graph_mutation_authorized": False,
    }
