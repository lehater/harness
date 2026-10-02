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

import argparse
import json
from collections import defaultdict, deque
from pathlib import Path
from typing import Any

import yaml

from harness import CoreError


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
    applied_dispositions: list[dict[str, Any]] = []

    expected_by_id = {
        item.get("id"): item
        for item in expected
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }
    dispositions: dict[tuple[str, str | None], dict[str, Any]] = {}
    for item in candidate.get("semantic_dispositions", []) or []:
        if not isinstance(item, dict):
            findings.append({"code": "INVALID_SEMANTIC_DISPOSITION"})
            continue
        obligation_id = item.get("obligation")
        subject = item.get("subject")
        status = item.get("status")
        rationale = item.get("rationale")
        if (
            not isinstance(obligation_id, str)
            or obligation_id not in expected_by_id
            or (subject is not None and (not isinstance(subject, str) or not subject))
            or status not in {"NOT_APPLICABLE", "DEFERRED", "QUESTION"}
            or not isinstance(rationale, str)
            or not rationale.strip()
        ):
            findings.append(
                {
                    "code": "INVALID_SEMANTIC_DISPOSITION",
                    "obligation": obligation_id,
                    **({"subject": subject} if subject is not None else {}),
                }
            )
            continue
        key = (obligation_id, subject)
        if key in dispositions:
            findings.append(
                {
                    "code": "DUPLICATE_SEMANTIC_DISPOSITION",
                    "obligation": obligation_id,
                    **({"subject": subject} if subject is not None else {}),
                }
            )
            continue
        dispositions[key] = item

    def disposition_for(
        obligation_id: str,
        subject: str | None = None,
    ) -> dict[str, Any] | None:
        return dispositions.get((obligation_id, subject))

    def apply_disposition(
        obligation_id: str,
        subject: str | None = None,
    ) -> str | None:
        item = disposition_for(obligation_id, subject)
        if item is None:
            return None
        status = item["status"]
        applied = {
            "obligation": obligation_id,
            "status": status,
            "rationale": item["rationale"],
        }
        if subject is not None:
            applied["subject"] = subject
        applied_dispositions.append(applied)
        if status == "NOT_APPLICABLE":
            return "SATISFIED"
        findings.append(
            {
                "code": (
                    "OBLIGATION_DEFERRED"
                    if status == "DEFERRED"
                    else "OBLIGATION_QUESTION"
                ),
                "obligation": obligation_id,
                **({"subject": subject} if subject is not None else {}),
                "rationale": item["rationale"],
            }
        )
        return "OPEN"

    assertion_ids_by_kind: dict[str, set[str]] = defaultdict(set)
    for assertion in assertions:
        kind = assertion.get("kind")
        assertion_id = assertion.get("id")
        if isinstance(kind, str) and isinstance(assertion_id, str) and assertion_id:
            assertion_ids_by_kind[kind].add(assertion_id)

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

        required_subjects: set[str] = set()
        subjects = obligation.get("subjects")
        if subjects is not None:
            required_subjects.update(subjects)
        subjects_from_kind = obligation.get("subjects_from_kind")
        if subjects_from_kind is not None:
            required_subjects.update(
                assertion_ids_by_kind.get(subjects_from_kind, set())
            )

        if required_subjects:
            present = {
                a.get("subject")
                for a in matches
                if isinstance(a.get("subject"), str) and a.get("subject")
            }
            missing: list[str] = []
            open_disposition = False
            for missing_subject in sorted(required_subjects - present):
                disposition_state = apply_disposition(
                    obligation_id,
                    missing_subject,
                )
                if disposition_state == "SATISFIED":
                    continue
                if disposition_state == "OPEN":
                    open_disposition = True
                    continue
                missing.append(missing_subject)
            for present_subject in sorted(required_subjects & present):
                if disposition_for(obligation_id, present_subject) is not None:
                    findings.append(
                        {
                            "code": "OBLIGATION_DISPOSITION_CONFLICT",
                            "obligation": obligation_id,
                            "subject": present_subject,
                        }
                    )
            if missing:
                findings.append(
                    {
                        "code": "MISSING_SUBJECTS",
                        "obligation": obligation_id,
                        "subjects": missing,
                    }
                )
            if missing or open_disposition:
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

        if not required_subjects and len(matches) < obligation.get("min_count", 1):
            disposition_state = apply_disposition(obligation_id)
            if disposition_state == "SATISFIED":
                satisfied.append(obligation_id)
                continue
            if disposition_state == "OPEN":
                continue
            findings.append(
                {"code": "MISSING_OBLIGATION", "obligation": obligation_id}
            )
            continue

        if matches and disposition_for(obligation_id) is not None:
            findings.append(
                {
                    "code": "OBLIGATION_DISPOSITION_CONFLICT",
                    "obligation": obligation_id,
                }
            )
            continue

        satisfied.append(obligation_id)

    allowed_authority = contract.get("authority")
    allowed_kinds = set(contract.get("owned_assertion_kinds", []) or [])
    allowed_source_authorities = set(
        contract.get("allowed_source_authorities", []) or []
    )
    requires_source_authority = bool(contract.get("requires_source_authority"))
    requires_assertion_authority = bool(
        contract.get("requires_assertion_authority")
    )

    seen: dict[tuple[str, str | None], dict[str, Any]] = {}
    for assertion in assertions:
        assertion_id = assertion.get("id", "<unknown>")
        kind = assertion.get("kind")
        assertion_authority = assertion.get("decision_authority")

        if requires_assertion_authority and (
            not isinstance(assertion_authority, str)
            or not assertion_authority.strip()
        ):
            findings.append(
                {
                    "code": "MISSING_DECISION_AUTHORITY",
                    "assertion": assertion_id,
                }
            )
        elif (
            isinstance(assertion_authority, str)
            and assertion_authority
            and allowed_authority is not None
            and assertion_authority != allowed_authority
        ):
            findings.append(
                {
                    "code": "WRONG_AUTHORITY_OWNERSHIP",
                    "assertion": assertion_id,
                    "authority": assertion_authority,
                    "expected_authority": allowed_authority,
                }
            )

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

            source_authority = source.get("decision_authority")
            if requires_source_authority and (
                not isinstance(source_authority, str)
                or not source_authority.strip()
            ):
                findings.append(
                    {
                        "code": "UNKNOWN_SOURCE_AUTHORITY",
                        "assertion": assertion_id,
                        "source": source_id,
                    }
                )
            elif (
                allowed_source_authorities
                and isinstance(source_authority, str)
                and source_authority
                and source_authority not in allowed_source_authorities
            ):
                findings.append(
                    {
                        "code": "SOURCE_AUTHORITY_VIOLATION",
                        "assertion": assertion_id,
                        "source": source_id,
                        "source_authority": source_authority,
                        "allowed_source_authorities": sorted(
                            allowed_source_authorities
                        ),
                    }
                )

            if (
                semantic_key(source) == semantic_key(assertion)
                and isinstance(source_authority, str)
                and source_authority
                and isinstance(assertion_authority, str)
                and assertion_authority
                and source_authority != assertion_authority
            ):
                findings.append(
                    {
                        "code": "CROSS_AUTHORITY_OWNERSHIP_CONFLICT",
                        "assertion": assertion_id,
                        "source": source_id,
                        "assertion_authority": assertion_authority,
                        "source_authority": source_authority,
                    }
                )

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

    required_review_checks = set(
        contract.get("required_semantic_review_checks", []) or []
    )
    if required_review_checks:
        completed_checks = set()
        if isinstance(review, dict):
            checks = review.get("checks", []) or []
            if isinstance(checks, list):
                completed_checks = {
                    value for value in checks
                    if isinstance(value, str) and value
                }
        missing_review_checks = sorted(
            required_review_checks - completed_checks
        )
        if missing_review_checks:
            findings.append(
                {
                    "code": "SEMANTIC_REVIEW_CHECKS_MISSING",
                    "checks": missing_review_checks,
                }
            )
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
            "dispositions": applied_dispositions,
        },
        "findings": findings,
        "semantic_claims": {
            "accepted": contract.get("semantic_claims", []) if accepted else []
        },
    }


def evaluation_index(
    project_docs: list[dict[str, Any]],
) -> dict[tuple[str | None, str | None], dict[str, Any]]:
    """Index one current semantic evaluation per (artifact, capability)."""
    result: dict[tuple[str | None, str | None], dict[str, Any]] = {}

    def add(evaluation: dict[str, Any]) -> None:
        key = (evaluation.get("artifact"), evaluation.get("capability"))
        if key in result:
            artifact, capability = key
            raise CoreError(
                "duplicate current semantic evaluation: "
                f"artifact={artifact!r}, capability={capability!r}"
            )
        result[key] = evaluation

    for doc in project_docs:
        if doc.get("kind") == "harness-artifact-semantic-evaluation":
            add(doc)
        for item in doc.get("semantic_evaluations", []) or []:
            if not isinstance(item, dict):
                continue
            if item.get("kind") != "harness-artifact-semantic-evaluation":
                continue
            add(item)
    return result


class CoverageAssuranceView:
    """Published read-only Assurance projection for Engineering Coverage."""

    def __init__(
        self,
        provider_dispositions: dict[tuple[object, object], str],
        evaluated_capabilities: set[str],
        accepted_claims_by_capability: dict[str, set[str]],
    ) -> None:
        self._provider_dispositions = dict(provider_dispositions)
        self._evaluated_capabilities = set(evaluated_capabilities)
        self._accepted_claims_by_capability = {
            capability: set(claims)
            for capability, claims in accepted_claims_by_capability.items()
        }

    def provider_disposition(self, artifact: str, capability: str) -> str:
        """Return ACCEPTED, REJECTED, or UNEVALUATED for one provider."""

        exact = (artifact, capability)
        fallback = (artifact, None)
        if exact in self._provider_dispositions:
            return self._provider_dispositions[exact]
        if fallback in self._provider_dispositions:
            return self._provider_dispositions[fallback]
        return "UNEVALUATED"

    def capability_evaluated(self, capability: str) -> bool:
        return capability in self._evaluated_capabilities

    def evaluated_capabilities(self) -> set[str]:
        return set(self._evaluated_capabilities)

    def accepted_claims(self, capability: str) -> set[str]:
        return set(self._accepted_claims_by_capability.get(capability, set()))

    def accepted_claims_by_capability(self) -> dict[str, set[str]]:
        return {
            capability: set(claims)
            for capability, claims in self._accepted_claims_by_capability.items()
        }


def coverage_assurance_view(
    project_docs: list[dict[str, Any]],
) -> CoverageAssuranceView:
    """Project current semantic evidence into the published Coverage view."""

    provider_dispositions: dict[tuple[object, object], str] = {}
    evaluated_capabilities: set[str] = set()
    accepted_claims: dict[str, set[str]] = {}

    for key, evaluation in evaluation_index(project_docs).items():
        provider_dispositions[key] = (
            "ACCEPTED" if evaluation.get("status") == "ACCEPTED" else "REJECTED"
        )
        capability = evaluation.get("capability")
        if not isinstance(capability, str) or not capability:
            continue
        evaluated_capabilities.add(capability)
        if evaluation.get("status") == "ACCEPTED":
            accepted_claims.setdefault(capability, set()).update(
                evaluation.get("semantic_claims", {}).get("accepted", []) or []
            )

    return CoverageAssuranceView(
        provider_dispositions,
        evaluated_capabilities,
        accepted_claims,
    )


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


def coverage_invalidation_closure(
    engineering_graph: dict[str, Any],
    invalid_capabilities: set[str],
) -> dict[str, list[str]]:
    """Published Assurance invalidation projection for Coverage consumers."""

    return semantic_invalidation_closure(engineering_graph, invalid_capabilities)


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


def load(path: str | Path) -> dict[str, Any]:
    value = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a mapping")
    return value


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Evaluate candidate artifact semantic acceptance"
    )
    parser.add_argument("contract")
    parser.add_argument("sources")
    parser.add_argument("candidate")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    result = evaluate_artifact(
        load(args.contract),
        load(args.sources),
        load(args.candidate),
    )
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(yaml.safe_dump(result, sort_keys=False, allow_unicode=True))
    return 0 if result["status"] == "ACCEPTED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
