#!/usr/bin/env python3
"""Artifact semantic acceptance above Harness Core.

This module deliberately keeps semantic acceptance outside Core. It validates a
candidate artifact realization against an artifact-specific contract and emits
generated acceptance evidence. Engineering Coverage may consume semantic claims
only from accepted evaluations when such evidence exists.

The contract is intentionally small and artifact-skill-owned. It is not a
universal engineering ontology.
"""
from __future__ import annotations

from collections import defaultdict, deque
from typing import Any


def semantic_key(item: dict[str, Any]) -> tuple[str, str | None]:
    return (item.get("kind", ""), item.get("subject"))


def _source_index(sources: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        item["id"]: item
        for item in sources.get("semantic_assertions", []) or []
        if isinstance(item, dict) and isinstance(item.get("id"), str) and item["id"]
    }


def evaluate_artifact(
    contract: dict[str, Any],
    sources: dict[str, Any],
    candidate: dict[str, Any],
) -> dict[str, Any]:
    """Evaluate one candidate artifact against its semantic production contract.

    Deterministic checks intentionally cover only machine-addressable semantics.
    Interpretive review can be supplied by the candidate as semantic_review with
    status ACCEPTED/REJECTED when the contract requires it.
    """
    expected = contract.get("obligations", []) or []
    assertions = candidate.get("semantic_assertions", []) or []
    source_assertions = sources.get("semantic_assertions", []) or []
    source_by_id = _source_index(sources)

    findings: list[dict[str, Any]] = []
    satisfied: list[str] = []

    for obligation in expected:
        obligation_id = obligation["id"]
        kind = obligation.get("kind")
        matches = [
            assertion
            for assertion in assertions
            if kind is None or assertion.get("kind") == kind
        ]

        subject = obligation.get("subject")
        if subject is not None:
            matches = [a for a in matches if a.get("subject") == subject]

        subjects = obligation.get("subjects")
        if subjects is not None:
            present = {a.get("subject") for a in matches}
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

        required_values = obligation.get("required_values")
        if required_values is not None:
            present_values = {
                a.get("semantic_value")
                for a in matches
                if a.get("semantic_value") is not None
            }
            missing_values = sorted(set(required_values) - present_values)
            if missing_values:
                findings.append(
                    {
                        "code": "MISSING_VALUES",
                        "obligation": obligation_id,
                        "values": missing_values,
                    }
                )
                continue

        if len(matches) < obligation.get("min_count", 1):
            findings.append(
                {"code": "MISSING_OBLIGATION", "obligation": obligation_id}
            )
            continue

        satisfied.append(obligation_id)

    allowed_authority = contract.get("authority")
    allowed_kinds = set(contract.get("owned_assertion_kinds", []) or [])

    seen: dict[tuple[str, str | None], dict[str, Any]] = {}
    for assertion in assertions:
        assertion_id = assertion.get("id", "<unknown>")
        kind = assertion.get("kind")

        if allowed_kinds and kind not in allowed_kinds:
            findings.append(
                {
                    "code": "WRONG_AUTHORITY_OWNERSHIP",
                    "assertion": assertion_id,
                    "kind": kind,
                }
            )

        derived_from = assertion.get("derived_from", []) or []
        is_new_decision = assertion.get("decision_authority") == allowed_authority
        if not derived_from and not is_new_decision:
            findings.append(
                {"code": "INVENTED_ASSERTION", "assertion": assertion_id}
            )

        for source_id in derived_from:
            source = source_by_id.get(source_id)
            if source is None:
                findings.append(
                    {
                        "code": "UNKNOWN_PROVENANCE",
                        "assertion": assertion_id,
                        "source": source_id,
                    }
                )
                continue

            if (
                semantic_key(source) == semantic_key(assertion)
                and source.get("semantic_value") is not None
                and assertion.get("semantic_value") != source.get("semantic_value")
            ):
                findings.append(
                    {
                        "code": "SOURCE_FIDELITY_VIOLATION",
                        "assertion": assertion_id,
                        "source": source_id,
                    }
                )

        key = semantic_key(assertion)
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
            if semantic_key(assertion) != semantic_key(source):
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

    for compatibility in contract.get("compatibility_obligations", []) or []:
        obligation_id = compatibility["id"]
        left_kind = compatibility.get("left_kind")
        right_kind = compatibility.get("right_kind")
        left = [a for a in assertions if a.get("kind") == left_kind]
        right = [a for a in source_assertions if a.get("kind") == right_kind]
        right_subjects = {a.get("subject") for a in right}
        missing = sorted(
            {
                a.get("subject")
                for a in left
                if a.get("subject") is not None
                and a.get("subject") not in right_subjects
            }
        )
        if missing:
            findings.append(
                {
                    "code": "INCOMPATIBLE_CONSUMER_CONTRACT",
                    "obligation": obligation_id,
                    "subjects": missing,
                }
            )

    review = candidate.get("semantic_review")
    if contract.get("requires_semantic_review"):
        if not isinstance(review, dict) or review.get("status") != "ACCEPTED":
            findings.append({"code": "SEMANTIC_REVIEW_REQUIRED"})
    if isinstance(review, dict) and review.get("status") == "REJECTED":
        findings.append(
            {
                "code": "SEMANTIC_REVIEW_REJECTED",
                "reason": review.get("reason"),
            }
        )

    accepted = not findings
    return {
        "version": 1,
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


def evaluation_index(
    project_docs: list[dict[str, Any]],
) -> dict[tuple[str | None, str | None], dict[str, Any]]:
    """Index generated semantic evaluations by (artifact, capability)."""
    result: dict[tuple[str | None, str | None], dict[str, Any]] = {}
    for doc in project_docs:
        if doc.get("kind") == "harness-artifact-semantic-evaluation":
            result[(doc.get("artifact"), doc.get("capability"))] = doc
        for item in doc.get("semantic_evaluations", []) or []:
            if not isinstance(item, dict):
                continue
            if item.get("kind") != "harness-artifact-semantic-evaluation":
                continue
            result[(item.get("artifact"), item.get("capability"))] = item
    return result


def accepted_claims_for(
    evaluations: dict[tuple[str | None, str | None], dict[str, Any]],
    artifact: str,
    capability: str,
) -> set[str] | None:
    """Return accepted claims, or None when no evaluation exists (legacy mode)."""
    evaluation = evaluations.get((artifact, capability))
    if evaluation is None:
        evaluation = evaluations.get((artifact, None))
    if evaluation is None:
        return None
    if evaluation.get("status") != "ACCEPTED":
        return set()
    return set(evaluation.get("semantic_claims", {}).get("accepted", []) or [])


def rejected_semantic_providers(
    project_docs: list[dict[str, Any]],
) -> dict[str, list[str]]:
    """Return capabilities whose provider has explicit REJECTED semantic evidence."""
    evaluations = evaluation_index(project_docs)
    result: dict[str, list[str]] = defaultdict(list)

    for doc in project_docs:
        for artifact in doc.get("artifacts", []) or []:
            if not isinstance(artifact, dict) or not artifact.get("id"):
                continue
            artifact_id = artifact["id"]
            for capability in artifact.get("provides", []) or []:
                evaluation = evaluations.get((artifact_id, capability))
                if evaluation is None:
                    evaluation = evaluations.get((artifact_id, None))
                if evaluation is not None and evaluation.get("status") != "ACCEPTED":
                    result[capability].append(artifact_id)

        for binding in doc.get("bindings", []) or []:
            if not isinstance(binding, dict) or not binding.get("artifact"):
                continue
            artifact_id = binding["artifact"]
            for capability in binding.get("provides", []) or []:
                evaluation = evaluations.get((artifact_id, capability))
                if evaluation is None:
                    evaluation = evaluations.get((artifact_id, None))
                if evaluation is not None and evaluation.get("status") != "ACCEPTED":
                    result[capability].append(artifact_id)

    return {k: sorted(set(v)) for k, v in result.items()}


def semantic_invalidation_closure(
    engineering_graph: dict[str, Any],
    rejected_capabilities: set[str],
) -> dict[str, list[str]]:
    """Propagate semantic invalidation through production prerequisites.

    This is intentionally capability-granular. Assertion-level provenance can
    narrow the closure later without changing the acceptance invariant.
    """
    dependents: dict[str, set[str]] = defaultdict(set)
    for authority in engineering_graph.get("authorities", []) or []:
        for production in authority.get("produces", []) or []:
            if not isinstance(production, dict) or not production.get("capability"):
                continue
            capability = production["capability"]
            for requirement in production.get("requires", []) or []:
                upstream = (
                    requirement
                    if isinstance(requirement, str)
                    else requirement.get("capability")
                )
                if upstream:
                    dependents[upstream].add(capability)

    reasons: dict[str, set[str]] = {
        capability: {capability} for capability in rejected_capabilities
    }
    queue = deque(sorted(rejected_capabilities))
    while queue:
        upstream = queue.popleft()
        for dependent in dependents.get(upstream, set()):
            inherited = reasons[upstream]
            before = set(reasons.get(dependent, set()))
            after = before | inherited
            if after != before:
                reasons[dependent] = after
                queue.append(dependent)

    return {cap: sorted(values) for cap, values in reasons.items()}


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
