from __future__ import annotations
from typing import Any


def _key(item: dict[str, Any]) -> tuple[str, str | None]:
    return (item.get("kind", ""), item.get("subject"))


def evaluate(
    contract: dict[str, Any],
    sources: dict[str, Any],
    candidate: dict[str, Any],
) -> dict[str, Any]:
    expected = contract.get("obligations", []) or []
    assertions = candidate.get("semantic_assertions", []) or []
    source_assertions = sources.get("semantic_assertions", []) or []
    source_by_id = {
        item["id"]: item
        for item in source_assertions
        if isinstance(item, dict) and item.get("id")
    }

    findings: list[dict[str, Any]] = []
    satisfied: list[str] = []

    for obligation in expected:
        obligation_id = obligation["id"]
        matches = [
            assertion
            for assertion in assertions
            if assertion.get("kind") == obligation.get("kind")
        ]
        subject = obligation.get("subject")
        if subject is not None:
            matches = [
                assertion
                for assertion in matches
                if assertion.get("subject") == subject
            ]

        subjects = obligation.get("subjects")
        if subjects is not None:
            present = {assertion.get("subject") for assertion in matches}
            missing = sorted(set(subjects) - present)
            if missing:
                findings.append(
                    {
                        "code": "MISSING_SUBJECTS",
                        "obligation": obligation_id,
                        "subjects": missing,
                    }
                )
                continue

        if len(matches) < obligation.get("min_count", 1):
            findings.append(
                {
                    "code": "MISSING_OBLIGATION",
                    "obligation": obligation_id,
                }
            )
            continue
        satisfied.append(obligation_id)

    allowed_authority = contract.get("authority")
    allowed_kinds = set(contract.get("owned_assertion_kinds", []) or [])

    seen: dict[tuple[str, str | None], dict[str, Any]] = {}
    for assertion in assertions:
        assertion_id = assertion.get("id", "<unknown>")

        if allowed_kinds and assertion.get("kind") not in allowed_kinds:
            findings.append(
                {
                    "code": "WRONG_AUTHORITY_OWNERSHIP",
                    "assertion": assertion_id,
                    "kind": assertion.get("kind"),
                }
            )

        derived_from = assertion.get("derived_from", []) or []
        is_new_decision = assertion.get("decision_authority") == allowed_authority
        if not derived_from and not is_new_decision:
            findings.append(
                {
                    "code": "INVENTED_ASSERTION",
                    "assertion": assertion_id,
                }
            )

        for source_id in derived_from:
            if source_id not in source_by_id:
                findings.append(
                    {
                        "code": "UNKNOWN_PROVENANCE",
                        "assertion": assertion_id,
                        "source": source_id,
                    }
                )
                continue

            source = source_by_id[source_id]
            if _key(source) == _key(assertion) and source.get("semantic_value") is not None:
                if assertion.get("semantic_value") != source.get("semantic_value"):
                    findings.append(
                        {
                            "code": "SOURCE_FIDELITY_VIOLATION",
                            "assertion": assertion_id,
                            "source": source_id,
                        }
                    )

        key = _key(assertion)
        if key in seen:
            previous = seen[key]
            if previous.get("semantic_value") != assertion.get("semantic_value"):
                findings.append(
                    {
                        "code": "INTERNAL_CONTRADICTION",
                        "assertions": [previous.get("id"), assertion_id],
                    }
                )
        else:
            seen[key] = assertion

    for assertion in assertions:
        for source in source_assertions:
            if _key(assertion) != _key(source):
                continue
            if source.get("semantic_value") is None:
                continue
            if assertion.get("semantic_value") == source.get("semantic_value"):
                continue
            if source.get("id") in (assertion.get("derived_from", []) or []):
                continue
            findings.append(
                {
                    "code": "CROSS_ARTIFACT_CONTRADICTION",
                    "assertion": assertion.get("id"),
                    "source": source.get("id"),
                }
            )

    accepted = not findings
    return {
        "kind": "harness-artifact-semantic-evaluation",
        "artifact": candidate.get("id"),
        "capability": candidate.get("capability"),
        "status": "ACCEPTED" if accepted else "REJECTED",
        "obligations": {
            "expected": [item["id"] for item in expected],
            "satisfied": satisfied,
        },
        "findings": findings,
        "semantic_claims": {
            "accepted": contract.get("semantic_claims", []) if accepted else []
        },
    }


def coverage_proof_available(
    production_claims: list[str],
    evaluation: dict[str, Any],
    accepted_claim: str,
) -> bool:
    return (
        evaluation.get("status") == "ACCEPTED"
        and accepted_claim in production_claims
        and accepted_claim
        in evaluation.get("semantic_claims", {}).get("accepted", [])
    )
