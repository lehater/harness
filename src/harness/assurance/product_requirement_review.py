"""Machine-addressable accounting for Product Requirements semantic review.

This checks completeness/consistency of an interpretive review; it cannot decide
whether prose has the correct meaning. The reviewer remains accountable for that.
"""
from __future__ import annotations
from typing import Any

PRODUCT_ROLES = {"PRODUCT_BEHAVIOR", "PRODUCT_CONSTRAINT"}
SOURCE_ROLES = {
    "PRODUCT_REQUIREMENT", "PRODUCT_CONSTRAINT",
    "ACCEPTANCE_CRITERION", "VERIFICATION_OBLIGATION",
    "NON_GOAL", "CONTEXT", "DOWNSTREAM_DECISION", "QUESTION", "DUPLICATE",
}
SOURCE_PRODUCT_ROLES = {"PRODUCT_REQUIREMENT", "PRODUCT_CONSTRAINT"}


def evaluate_product_requirement_boundary(
    review: dict[str, Any] | None,
    assertions: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Require explicit one-to-one *normative obligation* accounting.

    Independent TEST cases, input fields and metadata states do not imply
    independent product requirements. Contract-group identities must be unique.
    """
    if not isinstance(review, dict):
        return [{"code": "PRODUCT_REQUIREMENT_BOUNDARY_REVIEW_REQUIRED"}]
    rows = review.get("requirement_classifications")
    dispositions = review.get("source_dispositions")
    if not isinstance(rows, list) or not isinstance(dispositions, list) or not dispositions:
        return [{"code": "PRODUCT_REQUIREMENT_BOUNDARY_REVIEW_REQUIRED"}]

    ids = [a.get("id") for a in assertions if isinstance(a, dict)]
    valid_ids = {i for i in ids if isinstance(i, str) and i}
    findings: list[dict[str, Any]] = []
    if len(valid_ids) != len(assertions) or len(valid_ids) != len(ids):
        findings.append({"code": "INVALID_PRODUCT_REQUIREMENT_ASSERTION_IDS"})
    by_id: dict[str, dict[str, Any]] = {}
    used_obligations: dict[str, str] = {}
    for row in rows:
        if not isinstance(row, dict):
            findings.append({"code": "INVALID_PRODUCT_REQUIREMENT_CLASSIFICATION"})
            continue
        rid, role, group = row.get("assertion"), row.get("role"), row.get("obligation")
        rationale = row.get("rationale")
        if (not isinstance(rid, str) or rid not in valid_ids
                or rid in by_id or role not in PRODUCT_ROLES
                or not isinstance(group, str) or not group.strip()
                or not isinstance(rationale, str) or not rationale.strip()):
            findings.append({"code": "INVALID_PRODUCT_REQUIREMENT_CLASSIFICATION", "assertion": rid})
            continue
        by_id[rid] = row
        other = used_obligations.get(group)
        if other is not None:
            findings.append({
                "code": "PRODUCT_REQUIREMENT_FRAGMENTED_OBLIGATION",
                "obligation": group, "assertions": [other, rid],
            })
        used_obligations[group] = rid
    for rid in sorted(valid_ids - set(by_id)):
        findings.append({"code": "PRODUCT_REQUIREMENT_CLASSIFICATION_MISSING", "assertion": rid})

    source_names: set[str] = set()
    covered: set[str] = set()
    for item in dispositions:
        if not isinstance(item, dict):
            findings.append({"code": "INVALID_PRODUCT_SOURCE_DISPOSITION"})
            continue
        sid, role = item.get("source"), item.get("disposition")
        refs, rationale = item.get("assertions"), item.get("rationale")
        if (not isinstance(sid, str) or not sid.strip() or sid in source_names
                or role not in SOURCE_ROLES or not isinstance(refs, list)
                or any(not isinstance(ref, str) or ref not in valid_ids for ref in refs)
                or not isinstance(rationale, str) or not rationale.strip()):
            findings.append({"code": "INVALID_PRODUCT_SOURCE_DISPOSITION", "source": sid})
            continue
        source_names.add(sid)
        if role in SOURCE_PRODUCT_ROLES:
            if not refs:
                findings.append({"code": "PRODUCT_SOURCE_WITHOUT_REQUIREMENT", "source": sid})
            covered.update(refs)
        elif refs:
            findings.append({"code": "NONPRODUCT_SOURCE_PROMOTED", "source": sid, "disposition": role, "assertions": refs})
    for rid in sorted(valid_ids - covered):
        findings.append({"code": "PRODUCT_REQUIREMENT_UNGROUNDED_IN_REVIEW", "assertion": rid})
    return findings
