"""Bounded atomic claim -> target-output review packets, never graph authority.

Accepted document text and an operator's chosen source quote do not prove
that source export directly and materially constrains a target output.
An omitted obligation cannot be reported RESOLVED without an explicit
nonapplicability rationale (not represented in the current provider response).
"""
from __future__ import annotations

import hashlib
import json
from typing import Any


TESTS = (
    "TARGET_OWNED_OUTPUT_AND_ACCEPTED_SCOPE",
    "CLAIM_PRODUCER_OWNERSHIP_VERIFIED",
    "MATERIAL_RULE_CONSUMED_BY_THIS_OUTPUT",
    "SOURCE_OUTPUT_PRECEDES_TARGET_OUTPUT",
    "DIRECT_CHANGE_SENSITIVITY",
    "INTERMEDIATE_PUBLIC_CONTRACT_MEDIATION",
    "INDEPENDENT_AUTHORITY_ADJUDICATION",
)


def review_atomic_needs(case: dict[str, Any], prediction: dict[str, Any],
                        delegations: list[dict[str, Any]]) -> dict[str, Any]:
    providers = {r["capability"]: r for r in case["provider_catalog"]}
    output_ids = [x["id"] for x in case["target"]["output_obligations"]]
    needs = prediction["input_needs"]
    unresolved = set(prediction["unresolved_obligations"])
    rows = []
    unaccounted = []
    for oid in output_ids:
        mapped = []
        for need in needs:
            if need["obligation"] != oid:
                continue
            provider = providers[need["provider"]]
            scope = provider["source_scope"]
            index = need["claim_index"]
            claim_ids = scope.get("claim_ids", [])
            if (scope.get("claim_role") != "UNACCEPTED_OWNED_EXPORT_CANDIDATE"
                    or type(index) is not int or index < 0 or index >= len(claim_ids)
                    or index >= len(provider["semantic_surface"])):
                raise ValueError("replayed need not bound to atomic output claim")
            related_delegations = [
                d for d in delegations if
                d["source_capability"] == need["provider"] and
                d["delegates_to_capability"] == case["target"]["capability"]
            ]
            mapped.append({
                "provider": need["provider"],
                "atomic_claim_id": claim_ids[index],
                "claim_index": index,
                "exact_source_claim": provider["semantic_surface"][index],
                "consumption_rationale_model_only": need["consumption_rationale"],
                "provider_cites_target_as_distinct_export_owner": bool(related_delegations),
                "related_delegation_claim_ids": [
                    d["claim_id"] for d in related_delegations
                ],
                "semantic_directness_decision": "UNREVIEWED",
                "test_results": [
                    {"test": test, "result": "NOT_INDEPENDENTLY_VERIFIED"}
                    for test in TESTS
                ],
                "automatic_writeback_allowed": False,
            })
        if mapped:
            status = ("CANDIDATE_NEEDS_WITH_UNRESOLVED_OUTPUT"
                      if oid in unresolved else "MODEL_CANDIDATE_NOT_AUTHORITY_PROOF")
        elif oid in unresolved:
            status = "UNRESOLVED_NO_PROVEN_PROVIDER"
        else:
            status = "UNACCOUNTED_NO_NONAPPLICABILITY_JUSTIFICATION"
            unaccounted.append(oid)
        rows.append({
            "obligation_id": oid, "status": status,
            "candidate_needs": mapped,
            "target_output_independently_accepted": False,
        })
    result = {
        "kind": "harness-cdr-atomic-output-consumption-review",
        "version": 1,
        "case_id": case["id"],
        "target": case["target"]["capability"],
        "model_status_preserved": prediction["status"],
        "unaccounted_obligations": unaccounted,
        "per_obligation": rows,
        "semantic_claim_ownership_verified": False,
        "independent_target_acceptance_proven": False,
        "directness_semantically_adjudicated": False,
        "automatic_writeback_allowed": False,
        "status": "REVIEW_REQUIRED_NONAUTHORITATIVE",
    }
    serialized = json.dumps(result, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return {**result, "evidence_fingerprint_sha256": hashlib.sha256(serialized).hexdigest()}
