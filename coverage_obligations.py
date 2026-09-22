#!/usr/bin/env python3
"""Generic subject-obligation derivation and proof for Engineering Coverage."""
from __future__ import annotations
from typing import Any
import re

from coverage_planner import (
    _coverage_extended_scope,
    capability_claim_index,
    capability_realization,
    concern_proofs,
    declared_capability_claim_index,
    semantic_evaluation_required_claims,
)
from semantic_acceptance import evaluation_index


TERMINAL_STATES = {"COVERED", "NOT_APPLICABLE", "DEFERRED"}


def derive_subject_inventory_disposition(
    disposition: dict[str, Any] | None,
    *,
    consumer: str,
    scope: str,
) -> dict[str, Any]:
    """Require an explicit subject-inventory decision when no obligation contract exists."""
    row: dict[str, Any]
    if disposition is None:
        row = {
            "concern": "meta.subject-inventory",
            "subject": "__accepted_scope__",
            "state": "MISSING",
            "action": "DECLARE_SUBJECT_INVENTORY",
            "reason": (
                "Coverage cannot prove subject/scope completeness without either "
                "a subject-obligation contract or an explicit subject-inventory disposition"
            ),
        }
    else:
        if not isinstance(disposition, dict):
            raise ValueError("subject_inventory disposition must be a mapping")
        state = disposition.get("state")
        rationale = str(disposition.get("rationale", "")).strip()
        if state not in {"REQUIRED", "NOT_APPLICABLE", "DEFERRED", "QUESTION"}:
            raise ValueError(f"invalid subject_inventory state: {state}")
        if state == "REQUIRED":
            row = {
                "concern": "meta.subject-inventory",
                "subject": "__accepted_scope__",
                "state": "MISSING",
                "action": "DEFINE_SUBJECT_OBLIGATIONS",
                "reason": (
                    rationale
                    or "subject inventory is required but no subject-obligation contract was supplied"
                ),
            }
        elif state in {"NOT_APPLICABLE", "DEFERRED"}:
            if not rationale:
                raise ValueError(f"subject_inventory {state} requires rationale")
            row = {
                "concern": "meta.subject-inventory",
                "subject": "__accepted_scope__",
                "state": state,
                "action": "NONE",
                "reason": rationale,
            }
        else:
            question = disposition.get("question")
            if not rationale:
                raise ValueError("subject_inventory QUESTION requires rationale")
            if not isinstance(question, str) or not question:
                raise ValueError("subject_inventory QUESTION requires question")
            row = {
                "concern": "meta.subject-inventory",
                "subject": "__accepted_scope__",
                "state": "BLOCKED",
                "action": "RESOLVE_QUESTIONS",
                "reason": rationale,
                "questions": [question],
            }

    remaining = [] if row["state"] in TERMINAL_STATES else [row]
    return {
        "kind": "harness-derived-subject-obligation-evaluation",
        "consumer": consumer,
        "scope": scope,
        "source_validation": None,
        "rows": [row],
        "remaining_work": remaining,
        "completion_ready": not remaining,
    }


def _accepted_requirement_ids(source: dict[str, Any]) -> set[str]:
    """Extract accepted atomic requirement identities from an adapted canonical source."""
    if source.get("kind") == "harness-markdown-scope-source":
        text = source.get("text", "")
        if not isinstance(text, str):
            raise ValueError("markdown scope source text must be a string")
        status_match = re.search(r"(?im)^Status:\s*:?\s*`?([^\n`]+)`?\.?\s*$", text)
        if not status_match or "accepted" not in status_match.group(1).lower():
            return set()
        return {
            match.group("id")
            for match in re.finditer(
                r"(?m)^\s*-\s+\[(?P<id>[A-Z][A-Z0-9_.-]+)\]\s+",
                text,
            )
        }

    content = source.get("content", {}) or {}
    requirements = content.get("requirements", []) or []
    result: set[str] = set()
    for item in requirements:
        if not isinstance(item, dict):
            continue
        requirement_id = item.get("id")
        if item.get("status") == "ACCEPTED" and isinstance(requirement_id, str) and requirement_id:
            result.add(requirement_id)
    return result

def validate_subject_obligations(
    obligations: dict[str, Any],
    source: dict[str, Any],
    *,
    consumer: str,
    scope: str,
) -> dict[str, Any]:
    if obligations.get("version") != 1:
        raise ValueError("subject obligations version must be 1")
    if obligations.get("kind") != "harness-coverage-subject-obligations":
        raise ValueError("unexpected subject obligations kind")
    if obligations.get("consumer") != consumer:
        raise ValueError(
            f"subject obligations consumer mismatch: {obligations.get('consumer')} != {consumer}"
        )
    if obligations.get("scope") != scope:
        raise ValueError(
            f"subject obligations scope mismatch: {obligations.get('scope')} != {scope}"
        )

    accepted = _accepted_requirement_ids(source)
    classified: set[str] = set()
    seen_instances: set[tuple[str, str]] = set()

    for item in obligations.get("subjects", []) or []:
        if not isinstance(item, dict):
            raise ValueError("subject obligation must be a mapping")
        subject = item.get("subject")
        concerns = item.get("concerns", []) or []
        refs = item.get("requirement_refs", []) or []
        state = item.get("state", "REQUIRED")
        if not isinstance(subject, str) or not subject:
            raise ValueError("subject obligation subject is required")
        if state not in {"REQUIRED", "NOT_APPLICABLE", "DEFERRED", "QUESTION"}:
            raise ValueError(f"invalid subject obligation state: {state}")
        if state != "REQUIRED" and not str(item.get("rationale", "")).strip():
            raise ValueError(f"{state} subject obligation {subject} requires rationale")
        if not isinstance(concerns, list) or not concerns:
            raise ValueError(f"subject obligation {subject} must declare concerns")
        if not isinstance(refs, list) or not refs:
            raise ValueError(f"subject obligation {subject} must reference accepted requirements")
        for concern in concerns:
            if not isinstance(concern, str) or not concern:
                raise ValueError(f"subject obligation {subject} has invalid concern")
            key = (concern, subject)
            if key in seen_instances:
                raise ValueError(f"duplicate subject obligation instance: {concern}/{subject}")
            seen_instances.add(key)
        unknown = set(refs) - accepted
        if unknown:
            raise ValueError(
                f"subject obligation {subject} references unknown/non-accepted requirements: {sorted(unknown)}"
            )
        classified.update(refs)

    for item in obligations.get("excluded_requirements", []) or []:
        if not isinstance(item, dict):
            raise ValueError("excluded requirement must be a mapping")
        requirement_id = item.get("requirement")
        rationale = str(item.get("rationale", "")).strip()
        if requirement_id not in accepted:
            raise ValueError(
                f"excluded requirement is unknown/non-accepted: {requirement_id}"
            )
        if not rationale:
            raise ValueError(f"excluded requirement {requirement_id} requires rationale")
        classified.add(requirement_id)

    unclassified = sorted(accepted - classified)
    return {
        "accepted_requirement_count": len(accepted),
        "classified_requirement_count": len(classified & accepted),
        "unclassified_requirements": unclassified,
        "source_complete": not unclassified,
    }


def derive_subject_obligation_rows(
    *,
    obligations: dict[str, Any],
    source: dict[str, Any],
    graph: dict[str, Any],
    project_docs: list[dict[str, Any]],
    proof_contract: dict[str, Any],
    capability_bindings: dict[str, Any],
    consumer: str,
    scope: str,
    scope_roots: list[str] | None = None,
    extension_capabilities: set[str] | None = None,
) -> dict[str, Any]:
    validation = validate_subject_obligations(
        obligations, source, consumer=consumer, scope=scope
    )
    proofs = concern_proofs(proof_contract)
    strict_claims = semantic_evaluation_required_claims(proof_contract)
    declared = declared_capability_claim_index(capability_bindings, project_docs)
    usable_claims = capability_claim_index(
        capability_bindings,
        project_docs,
        required_evaluation_claims=strict_claims,
    )
    evaluations = evaluation_index(project_docs)
    evaluated_capabilities = {
        evaluation.get("capability")
        for evaluation in evaluations.values()
        if isinstance(evaluation.get("capability"), str)
        and evaluation.get("capability")
    }
    accepted_evaluation_claims: dict[str, set[str]] = {}
    for evaluation in evaluations.values():
        capability = evaluation.get("capability")
        if (
            isinstance(capability, str)
            and capability
            and evaluation.get("status") == "ACCEPTED"
        ):
            accepted_evaluation_claims.setdefault(capability, set()).update(
                evaluation.get("semantic_claims", {}).get("accepted", []) or []
            )
    realization = capability_realization(
        project_docs,
        consumer,
        scope_roots,
        extension_capabilities,
    )
    realized_caps = set(realization["usable"])
    provided_caps = set(realization["provided"])
    scoped_caps = _coverage_extended_scope(
        graph,
        consumer,
        scope_roots,
        extension_capabilities,
    )

    producer_by_capability: dict[str, str] = {}
    production_by_capability: dict[str, dict[str, Any]] = {}
    for authority in graph.get("authorities", []) or []:
        if not isinstance(authority, dict) or not authority.get("id"):
            continue
        for production in authority.get("produces", []) or []:
            if isinstance(production, str):
                producer_by_capability[production] = authority["id"]
                production_by_capability[production] = {
                    "capability": production,
                    "requires": [],
                }
            elif isinstance(production, dict) and production.get("capability"):
                producer_by_capability[production["capability"]] = authority["id"]
                production_by_capability[production["capability"]] = production

    rows: list[dict[str, Any]] = []
    if validation["unclassified_requirements"]:
        rows.append(
            {
                "concern": "meta.subject-inventory",
                "subject": "__accepted_scope__",
                "state": "MISSING",
                "action": "CLASSIFY_ACCEPTED_SCOPE",
                "requirement_refs": validation["unclassified_requirements"],
                "reason": "accepted requirements exist without a subject or explicit exclusion",
            }
        )

    for item in obligations.get("subjects", []) or []:
        subject = item["subject"]
        requirement_refs = sorted(set(item.get("requirement_refs", []) or []))
        declared_state = item.get("state", "REQUIRED")

        for concern in item.get("concerns", []) or []:
            base = {
                "concern": concern,
                "subject": subject,
                "requirement_refs": requirement_refs,
                "obligation_provenance": item.get("provenance", []) or [],
            }
            if declared_state in {"NOT_APPLICABLE", "DEFERRED"}:
                rows.append(
                    {
                        **base,
                        "state": declared_state,
                        "action": "NONE",
                        "reason": item["rationale"],
                    }
                )
                continue
            if declared_state == "QUESTION":
                question_ids = (
                    [item["question"]]
                    if isinstance(item.get("question"), str) and item.get("question")
                    else []
                )
                rows.append(
                    {
                        **base,
                        "state": "BLOCKED",
                        "action": "RESOLVE_QUESTIONS",
                        "reason": item["rationale"],
                        "questions": question_ids,
                    }
                )
                continue

            accepted_claims = sorted(proofs.get(concern, set()))
            if not accepted_claims:
                rows.append(
                    {
                        **base,
                        "state": "BLOCKED",
                        "action": "MODEL_PROOF_CONTRACT",
                        "reason": "concern has no accepted semantic-claim proof contract",
                    }
                )
                continue

            matching_declared: list[tuple[str, dict[str, str]]] = []
            for cap, claims in declared.items():
                if cap not in scoped_caps:
                    continue
                for claim in claims:
                    if (
                        claim["claim"] in accepted_claims
                        and claim.get("subject") == subject
                    ):
                        matching_declared.append((cap, claim))

            semantic_invalid_caps = sorted(
                {
                    cap
                    for cap, _claim in matching_declared
                    if cap in provided_caps and cap in realization.get("semantic_invalid", {})
                }
            )
            if semantic_invalid_caps:
                rows.append(
                    {
                        **base,
                        "state": "BLOCKED",
                        "action": "REVALIDATE_SEMANTICS",
                        "accepted_semantic_claims": accepted_claims,
                        "capabilities": semantic_invalid_caps,
                        "causes": {
                            cap: realization["semantic_invalid"][cap]
                            for cap in semantic_invalid_caps
                        },
                    }
                )
                continue

            blocked_questions = sorted(
                {
                    question
                    for cap, _claim in matching_declared
                    if cap in provided_caps and cap not in realized_caps
                    for question in realization.get("blocked", {}).get(cap, [])
                }
            )
            if blocked_questions:
                rows.append(
                    {
                        **base,
                        "state": "BLOCKED",
                        "action": "RESOLVE_QUESTIONS",
                        "accepted_semantic_claims": accepted_claims,
                        "questions": blocked_questions,
                    }
                )
                continue

            exact_proofs = []
            for cap, claims in usable_claims.items():
                if cap not in scoped_caps or cap not in realized_caps:
                    continue
                for claim in claims:
                    if (
                        claim["claim"] in accepted_claims
                        and claim.get("subject") == subject
                    ):
                        exact_proofs.append(
                            {
                                "claim": claim["claim"],
                                "subject": subject,
                                "capability": cap,
                            }
                        )
            if exact_proofs:
                rows.append(
                    {
                        **base,
                        "state": "COVERED",
                        "action": "NONE",
                        "proof_instances": exact_proofs,
                    }
                )
                continue

            strict_accepted = set(accepted_claims) & strict_claims
            if strict_accepted:
                matching_provided = sorted(
                    {
                        cap
                        for cap, claim in matching_declared
                        if cap in provided_caps
                        and claim["claim"] in strict_accepted
                    }
                )
                unevaluated = sorted(
                    cap for cap in matching_provided
                    if cap not in evaluated_capabilities
                )
                if unevaluated:
                    rows.append(
                        {
                            **base,
                            "state": "MISSING",
                            "action": "VALIDATE_SEMANTICS",
                            "accepted_semantic_claims": accepted_claims,
                            "capabilities": unevaluated,
                            "reason": (
                                "This subject concern requires explicit semantic "
                                "acceptance evidence; provider existence alone is insufficient."
                            ),
                        }
                    )
                    continue

                insufficient = sorted(
                    cap
                    for cap in matching_provided
                    if not (
                        accepted_evaluation_claims.get(cap, set())
                        & strict_accepted
                    )
                )
                if insufficient:
                    rows.append(
                        {
                            **base,
                            "state": "BLOCKED",
                            "action": "REVALIDATE_SEMANTICS",
                            "accepted_semantic_claims": accepted_claims,
                            "capabilities": insufficient,
                            "causes": {},
                            "reason": (
                                "Semantic evaluation exists but does not accept any "
                                "claim that can prove this subject concern."
                            ),
                        }
                    )
                    continue

            candidates = []
            for cap, claim in matching_declared:
                if cap in provided_caps:
                    continue
                production = production_by_capability.get(cap, {})
                prerequisites = []
                for requirement in production.get("requires", []) or []:
                    upstream = (
                        requirement
                        if isinstance(requirement, str)
                        else requirement.get("capability")
                    )
                    if upstream:
                        prerequisites.append(upstream)
                missing_prerequisites = sorted(
                    prerequisite
                    for prerequisite in prerequisites
                    if prerequisite not in realized_caps
                )
                direct_questions = realization.get("direct_blockers", {}).get(cap, [])
                candidates.append(
                    {
                        "capability": cap,
                        "claim": claim["claim"],
                        "subject": subject,
                        "authority": producer_by_capability.get(cap),
                        "knowledge_kind": production.get("knowledge_kind"),
                        "requires": sorted(prerequisites),
                        "missing_prerequisites": missing_prerequisites,
                        "questions": direct_questions,
                        "ready": not missing_prerequisites and not direct_questions,
                    }
                )

            if candidates:
                ready_candidates = [candidate for candidate in candidates if candidate["ready"]]
                candidate_questions = sorted(
                    {
                        question
                        for candidate in candidates
                        for question in candidate.get("questions", [])
                    }
                )
                action = (
                    "PRODUCE_CAPABILITY"
                    if ready_candidates
                    else (
                        "RESOLVE_QUESTIONS"
                        if candidate_questions
                        else "WAIT_FOR_PREREQUISITES"
                    )
                )
                rows.append(
                    {
                        **base,
                        "state": "MISSING",
                        "action": action,
                        "accepted_semantic_claims": accepted_claims,
                        "production_candidates": candidates,
                        "ready_production_candidates": ready_candidates,
                        **({"questions": candidate_questions} if candidate_questions else {}),
                        "reason": "required subject has declared subject-scoped proof capability that is not realized",
                    }
                )
                continue

            rows.append(
                {
                    **base,
                    "state": "MISSING",
                    "action": "MODEL_PRODUCTION_CONTRACT",
                    "accepted_semantic_claims": accepted_claims,
                    "reason": "required subject has no in-scope subject-scoped proof contract",
                }
            )

    remaining = [row for row in rows if row["state"] not in TERMINAL_STATES]
    return {
        "kind": "harness-derived-subject-obligation-evaluation",
        "consumer": consumer,
        "scope": scope,
        "source_validation": validation,
        "rows": rows,
        "remaining_work": remaining,
        "completion_ready": not remaining,
    }
