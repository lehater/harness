"""Experimental reference-and-adoption preflight for Dependency Resolution.

This checks only the provenance and structural consistency of a model's
direct-consumption claims, NOT whether the cited statement semantically
entails the target obligation. No project graph mutations are authorized.
"""
from __future__ import annotations

from typing import Any

CONTRACT = "source-grounded-v1"
DIRECT = "DIRECT_ACCEPTED"
PLANNED = "PLANNED_CONTRACT"


def assess_case(case: dict[str, Any], prediction: dict[str, Any]) -> dict[str, Any]:
    """Assess optional source-grounded-v1 prediction proof for one blind case."""
    providers = {p["capability"]: p for p in case["provider_catalog"]}
    obligations = {o["id"] for o in case["target"]["output_obligations"]}
    unresolved = set(prediction.get("unresolved_obligations", []))
    needs = prediction.get("input_needs", [])
    proposed = prediction.get("proposed_requires", [])
    issues: list[dict[str, str]] = []
    review: list[dict[str, str]] = []
    verified_refs: list[dict[str, Any]] = []
    provisional: set[str] = set()
    eligible: set[str] = set()
    mapped: set[str] = set()

    if not isinstance(needs, list) or not isinstance(proposed, list) or not isinstance(
        prediction.get("unresolved_obligations"), list
    ):
        return {
            "status": "INVALID", "issues": [{"code": "MALFORMED_PREDICTION"}],
            "review_required": [], "referenced_claims": [],
            "adoption_eligible_requires": [], "provisional_requires": [],
            "automatic_writeback_allowed": False,
        }
    if any(not isinstance(value, str) for value in proposed + list(unresolved)):
        issues.append({"code": "INVALID_IDENTIFIER"})
    if any(x not in obligations for x in unresolved):
        issues.append({"code": "UNKNOWN_UNRESOLVED_OBLIGATION"})
    for i, need in enumerate(needs):
        if not isinstance(need, dict):
            issues.append({"code": "MALFORMED_NEED", "item": str(i)})
            continue
        obligation = need.get("obligation")
        provider_id = need.get("provider")
        if obligation not in obligations or provider_id not in providers:
            issues.append({"code": "UNKNOWN_OBLIGATION_OR_PROVIDER", "item": str(i)})
            continue
        mapped.add(provider_id)
        provider = providers[provider_id]
        index = need.get("claim_index")
        surface = provider.get("semantic_surface")
        if (type(index) is not int or not isinstance(surface, list)
            or index < 0 or index >= len(surface)
            or not isinstance(surface[index], str) or not surface[index].strip()):
            issues.append({"code": "INVALID_CLAIM_REFERENCE", "item": str(i)})
            continue
        rationale = need.get("consumption_rationale")
        if not isinstance(rationale, str) or len(rationale.strip()) < 15:
            issues.append({"code": "MISSING_CONSUMPTION_RATIONALE", "item": str(i)})
            continue
        expected_basis = (
            DIRECT if provider.get("evidence_status") == "ACCEPTED_EVIDENCE"
            else PLANNED if provider.get("evidence_status") == "CONTRACT_ONLY"
            else None
        )
        if need.get("basis") != expected_basis or expected_basis is None:
            issues.append({"code": "INVALID_EVIDENCE_BASIS", "item": str(i)})
            continue

        verified_refs.append({
            "obligation": obligation, "provider": provider_id,
            "claim_index": index, "claim_text": surface[index],
            "basis": expected_basis,
            "consumption_rationale": rationale,
        })
        if expected_basis == PLANNED:
            provisional.add(provider_id)
            review.append({
                "code": "UNACCEPTED_PROVIDER_CONTRACT",
                "provider": provider_id, "obligation": obligation,
            })
        elif obligation in unresolved:
            # Do not let a partially related accepted statement override an
            # acknowledged missing rule. The model may suggest the edge, but
            # cannot present it as accepted for topology adoption.
            review.append({
                "code": "DIRECT_EDGE_FOR_UNRESOLVED_OBLIGATION",
                "provider": provider_id, "obligation": obligation,
            })
        else:
            eligible.add(provider_id)

    if set(proposed) != mapped:
        issues.append({"code": "PROPOSED_EDGES_NOT_BACKED_BY_NEEDS"})
    if len(proposed) != len(set(proposed)):
        issues.append({"code": "DUPLICATE_PROPOSED_EDGE"})
    # A provider with any unresolved or contract-only evidence cannot be
    # automatically upgraded to a fully accepted, adoption-eligible source.
    blocked = provisional | {r["provider"] for r in review}
    eligible -= blocked
    if issues:
        status = "INVALID"
    elif review:
        status = "REVIEW_REQUIRED"
    else:
        status = "REFERENCED_NOT_SEMANTICALLY_VERIFIED"
    return {
        "status": status,
        "issues": issues,
        "review_required": review,
        "referenced_claims": verified_refs,
        "adoption_eligible_requires": sorted(eligible),
        "provisional_requires": sorted(provisional),
        # All graph writes remain disabled even if refs are well-formed.
        "automatic_writeback_allowed": False,
        "semantic_entailment_verified": False,
    }


def assess_predictions(inputs: dict[str, Any], predictions: dict[str, Any]) -> dict[str, Any]:
    if inputs.get("evidence_contract") != CONTRACT:
        return {
            "status": "LEGACY_NOT_EVIDENCE_ASSESSED",
            "automatic_writeback_allowed": False,
        }
    cases = {c["id"]: c for c in inputs["cases"]}
    findings: list[dict[str, Any]] = []
    overall = "REFERENCED_NOT_SEMANTICALLY_VERIFIED"
    for prediction in predictions.get("cases", []):
        cid = prediction.get("id")
        if cid not in cases:
            findings.append({"id": cid, "status": "INVALID", "issues": [{"code": "UNKNOWN_CASE"}]})
            overall = "INVALID"
            continue
        result = assess_case(cases[cid], prediction)
        findings.append({"id": cid, **result})
        if result["status"] == "INVALID":
            overall = "INVALID"
        elif result["status"] == "REVIEW_REQUIRED" and overall != "INVALID":
            overall = "REVIEW_REQUIRED"
    if len(findings) != len(cases):
        overall = "INVALID"
    return {
        "status": overall,
        "cases": findings,
        "automatic_writeback_allowed": False,
        "semantic_entailment_verified": False,
    }
