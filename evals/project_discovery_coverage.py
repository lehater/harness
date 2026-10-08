"""Check model coverage of source-derived upstream applicability candidates.

The model must account for every accepted Product Capability statement, but
its classification is always UNADJUDICATED. No automatic dependency removals
or promotions result from this inventory or from the model's reasons.
"""
from __future__ import annotations

from typing import Any

COVERAGE_CONTRACT = "source-traceability-v1"
DISPOSITIONS = {"DIRECT_CONSTRAINT", "CONTEXT_ONLY", "UNDECIDED"}


def assess_coverage(inputs: dict[str, Any], predictions: dict[str, Any]) -> dict[str, Any]:
    if inputs.get("coverage_contract", "legacy") != COVERAGE_CONTRACT:
        return {
            "status": "LEGACY_NOT_APPLICABLE",
            "semantic_applicability_adjudicated": False,
            "complete_output_obligation_coverage_established": False,
            "automatic_writeback_allowed": False,
        }
    cases = inputs.get("cases", [])
    outputs = predictions.get("cases", [])
    if not isinstance(cases, list) or not isinstance(outputs, list):
        return {
            "status": "INVALID",
            "issues": [{"code": "INVALID_CASES"}],
            "automatic_writeback_allowed": False,
            "semantic_applicability_adjudicated": False,
        }
    by_case = {c.get("id"): c for c in cases if isinstance(c, dict)}
    if len(by_case) != len(cases):
        return {
            "status": "INVALID",
            "issues": [{"code": "DUPLICATE_INPUT_CASE"}],
            "automatic_writeback_allowed": False,
            "semantic_applicability_adjudicated": False,
        }
    seen: set[str] = set()
    findings: list[dict[str, Any]] = []
    invalid = False
    for result in outputs:
        cid = result.get("id") if isinstance(result, dict) else None
        if cid not in by_case or cid in seen:
            invalid = True
            findings.append({"id": cid, "status": "INVALID",
                             "issues": [{"code": "INVALID_CASE_BINDING"}]})
            continue
        seen.add(cid)
        target = by_case[cid].get("target", {})
        candidates = target.get("upstream_constraint_candidates", [])
        expected = {
            c["requirement_id"]: c for c in candidates if isinstance(c, dict)
        }
        records = result.get("coverage_assessments")
        issues: list[dict[str, str]] = []
        seen_reqs: set[str] = set()
        disposition_counts = {key: 0 for key in sorted(DISPOSITIONS)}
        if not isinstance(records, list) or len(records) != len(expected):
            issues.append({"code": "INCOMPLETE_REQUIREMENT_COVERAGE"})
            records = records if isinstance(records, list) else []
        for assessment in records:
            if not isinstance(assessment, dict):
                issues.append({"code": "INVALID_COVERAGE_ROW"})
                continue
            req_id = assessment.get("requirement_id")
            if not isinstance(req_id, str) or req_id not in expected or req_id in seen_reqs:
                issues.append({"code": "UNKNOWN_OR_DUPLICATE_REQUIREMENT"})
                continue
            seen_reqs.add(req_id)
            disposition = assessment.get("disposition")
            if disposition not in DISPOSITIONS:
                issues.append({"code": "INVALID_DISPOSITION"})
                continue
            disposition_counts[disposition] += 1
            rationale = assessment.get("rationale")
            if not isinstance(rationale, str) or len(rationale.strip()) < 15:
                issues.append({"code": "MISSING_APPLICABILITY_RATIONALE"})
                continue
            if disposition == "DIRECT_CONSTRAINT":
                provider = expected[req_id]["provider"]
                needs = result.get("input_needs", [])
                if provider not in result.get("proposed_requires", []):
                    issues.append({"code": "DIRECT_CONSTRAINT_WITHOUT_EDGE"})
                elif not isinstance(needs, list) or not any(
                    isinstance(need, dict) and need.get("provider") == provider
                    and need.get("claim_index") == expected[req_id]["claim_index"]
                    for need in needs
                ):
                    issues.append({"code": "DIRECT_CONSTRAINT_WITHOUT_EXACT_SOURCE_NEED"})
        if seen_reqs != set(expected):
            issues.append({"code": "MISSING_REQUIREMENT_IDS"})
        if issues:
            invalid = True
        findings.append({
            "id": cid,
            "status": "INVALID" if issues else "UNADJUDICATED_APPLICABILITY",
            "issues": issues,
            "accepted_candidates_inventoried": len(expected),
            "strategically_traced": sum(
                x.get("traceability") == "EXPLICIT_STRATEGIC_DERIVATION"
                for x in expected.values()
            ),
            "untraced_requires_review": sum(
                x.get("traceability") == "UNADJUDICATED_ACCEPTED_PRODUCT_REQUIREMENT"
                for x in expected.values()
            ),
            "model_dispositions": disposition_counts,
            "semantic_applicability_adjudicated": False,
            "automatic_writeback_allowed": False,
        })
    if seen != set(by_case):
        invalid = True
    return {
        "status": "INVALID" if invalid else "REVIEW_REQUIRED",
        "cases": findings,
        "complete_input_inventory_assessed_by_model": not invalid,
        "complete_output_obligation_coverage_established": False,
        "semantic_applicability_adjudicated": False,
        "automatic_writeback_allowed": False,
    }
