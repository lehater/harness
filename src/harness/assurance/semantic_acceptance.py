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

from harness.project_model.core import CoreError


def semantic_key(item: dict[str, Any]) -> tuple[str, str | None]:
    return (item.get("kind", ""), item.get("subject"))


def _source_index(sources: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        item["id"]: item
        for item in sources.get("semantic_assertions", []) or []
        if isinstance(item, dict) and isinstance(item.get("id"), str) and item["id"]
    }


def _evaluate_independent_obligation_accounting(
    review: dict[str, Any] | None,
    assertions: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Validate semantic-review accounting for independently losable obligations.

    Semantic judgement owns identification of the obligations and whether one is
    collapsed/missing. Once identified, Harness deterministically validates that
    ACCOUNTED obligations reference existing, non-shared semantic assertions.
    """
    if not isinstance(review, dict):
        return [{"code": "INDEPENDENT_OBLIGATION_REVIEW_REQUIRED"}]

    items = review.get("independent_obligations")
    if not isinstance(items, list) or not items:
        return [{"code": "INDEPENDENT_OBLIGATION_REVIEW_REQUIRED"}]

    assertion_ids = {
        item.get("id")
        for item in assertions
        if isinstance(item, dict)
        and isinstance(item.get("id"), str)
        and item.get("id")
    }
    findings: list[dict[str, Any]] = []
    seen_obligations: set[str] = set()
    accounted_by_assertion: dict[str, set[str]] = defaultdict(set)
    status_codes = {
        "COLLAPSED": "INDEPENDENT_OBLIGATION_COLLAPSED",
        "MISSING": "INDEPENDENT_OBLIGATION_MISSING",
        "QUESTION": "INDEPENDENT_OBLIGATION_QUESTION",
    }

    for index, item in enumerate(items):
        if not isinstance(item, dict):
            findings.append(
                {
                    "code": "INVALID_INDEPENDENT_OBLIGATION_ACCOUNTING",
                    "index": index,
                }
            )
            continue

        obligation_id = item.get("id")
        status = item.get("status")
        refs = item.get("assertions", []) or []
        if (
            not isinstance(obligation_id, str)
            or not obligation_id
            or obligation_id in seen_obligations
            or status not in {"ACCOUNTED", "COLLAPSED", "MISSING", "QUESTION"}
            or not isinstance(refs, list)
            or any(not isinstance(ref, str) or not ref for ref in refs)
        ):
            findings.append(
                {
                    "code": "INVALID_INDEPENDENT_OBLIGATION_ACCOUNTING",
                    "index": index,
                    **(
                        {"obligation": obligation_id}
                        if isinstance(obligation_id, str) and obligation_id
                        else {}
                    ),
                }
            )
            continue
        seen_obligations.add(obligation_id)

        unknown = sorted(set(refs) - assertion_ids)
        if unknown:
            findings.append(
                {
                    "code": "UNKNOWN_INDEPENDENT_OBLIGATION_ASSERTION",
                    "obligation": obligation_id,
                    "assertions": unknown,
                }
            )

        if status == "ACCOUNTED":
            if not refs:
                findings.append(
                    {
                        "code": "INDEPENDENT_OBLIGATION_MISSING",
                        "obligation": obligation_id,
                    }
                )
                continue
            for ref in sorted(set(refs) & assertion_ids):
                accounted_by_assertion[ref].add(obligation_id)
            continue

        rationale = item.get("rationale")
        if not isinstance(rationale, str) or not rationale.strip():
            findings.append(
                {
                    "code": "INVALID_INDEPENDENT_OBLIGATION_ACCOUNTING",
                    "obligation": obligation_id,
                }
            )
            continue
        findings.append(
            {
                "code": status_codes[status],
                "obligation": obligation_id,
                **({"assertions": refs} if refs else {}),
                "rationale": rationale,
            }
        )

    for assertion_id, obligation_ids in sorted(accounted_by_assertion.items()):
        if len(obligation_ids) <= 1:
            continue
        findings.append(
            {
                "code": "INDEPENDENT_OBLIGATIONS_COLLAPSED",
                "assertion": assertion_id,
                "obligations": sorted(obligation_ids),
            }
        )

    return findings




def _evaluate_observable_realization_applicability(
    review: dict[str, Any] | None,
    assertions: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Validate semantic-review classification of observable realization needs."""
    if not isinstance(review, dict):
        return [{"code": "OBSERVABLE_REALIZATION_REVIEW_REQUIRED"}]
    items = review.get("observable_realization_obligations")
    if not isinstance(items, list):
        return [{"code": "OBSERVABLE_REALIZATION_REVIEW_REQUIRED"}]

    assertion_ids = {
        item.get("id")
        for item in assertions
        if isinstance(item, dict)
        and isinstance(item.get("id"), str)
        and item.get("id")
    }
    findings: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    seen_assertions: set[str] = set()

    for index, item in enumerate(items):
        if not isinstance(item, dict):
            findings.append(
                {"code": "INVALID_OBSERVABLE_REALIZATION_REVIEW", "index": index}
            )
            continue
        item_id = item.get("id")
        assertion_id = item.get("assertion")
        category = item.get("category")
        status = item.get("status")
        if (
            not isinstance(item_id, str)
            or not item_id
            or item_id in seen_ids
            or not isinstance(assertion_id, str)
            or not assertion_id
            or assertion_id in seen_assertions
            or assertion_id not in assertion_ids
            or category not in {"ACTION", "STATE", "DISTINCTION"}
            or status not in {"REQUIRED", "NOT_APPLICABLE", "QUESTION"}
        ):
            findings.append(
                {
                    "code": "INVALID_OBSERVABLE_REALIZATION_REVIEW",
                    "index": index,
                    **(
                        {"assertion": assertion_id}
                        if isinstance(assertion_id, str) and assertion_id
                        else {}
                    ),
                }
            )
            continue
        seen_ids.add(item_id)
        seen_assertions.add(assertion_id)

        if status == "REQUIRED":
            continue
        rationale = item.get("rationale")
        if not isinstance(rationale, str) or not rationale.strip():
            findings.append(
                {
                    "code": "INVALID_OBSERVABLE_REALIZATION_REVIEW",
                    "assertion": assertion_id,
                }
            )
        elif status == "QUESTION":
            findings.append(
                {
                    "code": "OBSERVABLE_REALIZATION_QUESTION",
                    "source": assertion_id,
                    "rationale": rationale,
                }
            )

    return findings

def _evaluate_interaction_role_coherence(
    review: dict[str, Any] | None,
    candidate: dict[str, Any],
) -> list[dict[str, Any]]:
    """Validate review-selected cross-context interaction role contracts.

    Semantic review owns the applicability judgement. Once it marks a concept as
    requiring materially distinct roles, Harness checks only machine-addressable
    role structure and the specific facets/transitions the review marked material.
    """
    if not isinstance(review, dict):
        return [{"code": "INTERACTION_ROLE_REVIEW_REQUIRED"}]

    requirements = review.get("interaction_role_requirements")
    if not isinstance(requirements, list):
        return [{"code": "INTERACTION_ROLE_REVIEW_REQUIRED"}]

    roles_value = candidate.get("interaction_roles", []) or []
    findings: list[dict[str, Any]] = []
    if not isinstance(roles_value, list):
        return [{"code": "INVALID_INTERACTION_ROLES"}]

    role_index: dict[str, dict[str, Any]] = {}
    allowed_facets = {
        "entry",
        "exit",
        "transitions",
        "side_effects",
        "forbidden_side_effects",
        "observable_distinction",
    }

    for index, role in enumerate(roles_value):
        if not isinstance(role, dict):
            findings.append({"code": "INVALID_INTERACTION_ROLE", "index": index})
            continue
        role_id = role.get("id")
        if not isinstance(role_id, str) or not role_id or role_id in role_index:
            findings.append(
                {
                    "code": "INVALID_INTERACTION_ROLE",
                    "index": index,
                    **(
                        {"role": role_id}
                        if isinstance(role_id, str) and role_id
                        else {}
                    ),
                }
            )
            continue

        valid = True
        for field in ("concept_ref", "meaning", "entry", "exit", "observable_distinction"):
            value = role.get(field)
            if not isinstance(value, str) or not value.strip():
                findings.append(
                    {
                        "code": "INTERACTION_ROLE_FIELD_REQUIRED",
                        "role": role_id,
                        "field": field,
                    }
                )
                valid = False
        for field in ("side_effects", "forbidden_side_effects"):
            value = role.get(field)
            if not isinstance(value, list) or any(
                not isinstance(item, str) or not item.strip() for item in value
            ):
                findings.append(
                    {
                        "code": "INTERACTION_ROLE_FIELD_INVALID",
                        "role": role_id,
                        "field": field,
                    }
                )
                valid = False

        transitions = role.get("transitions")
        if not isinstance(transitions, list):
            findings.append(
                {
                    "code": "INTERACTION_ROLE_FIELD_INVALID",
                    "role": role_id,
                    "field": "transitions",
                }
            )
            valid = False
        else:
            for transition_index, transition in enumerate(transitions):
                if (
                    not isinstance(transition, dict)
                    or not isinstance(transition.get("to"), str)
                    or not transition.get("to")
                ):
                    findings.append(
                        {
                            "code": "INVALID_INTERACTION_ROLE_TRANSITION",
                            "role": role_id,
                            "index": transition_index,
                        }
                    )
                    valid = False

        if valid:
            role_index[role_id] = role

    seen_concepts: set[str] = set()
    for index, requirement in enumerate(requirements):
        if not isinstance(requirement, dict):
            findings.append(
                {"code": "INVALID_INTERACTION_ROLE_REQUIREMENT", "index": index}
            )
            continue

        concept = requirement.get("concept")
        status = requirement.get("status")
        rationale = requirement.get("rationale")
        if (
            not isinstance(concept, str)
            or not concept
            or concept in seen_concepts
            or status not in {"REQUIRED", "NOT_REQUIRED", "QUESTION"}
            or not isinstance(rationale, str)
            or not rationale.strip()
        ):
            findings.append(
                {
                    "code": "INVALID_INTERACTION_ROLE_REQUIREMENT",
                    "index": index,
                    **(
                        {"concept": concept}
                        if isinstance(concept, str) and concept
                        else {}
                    ),
                }
            )
            continue
        seen_concepts.add(concept)

        if status == "QUESTION":
            findings.append(
                {
                    "code": "INTERACTION_ROLE_QUESTION",
                    "concept": concept,
                    "rationale": rationale,
                }
            )
            continue
        if status == "NOT_REQUIRED":
            continue

        required_roles = requirement.get("roles")
        if (
            not isinstance(required_roles, list)
            or len(required_roles) < 2
            or any(not isinstance(role_id, str) or not role_id for role_id in required_roles)
            or len(set(required_roles)) != len(required_roles)
        ):
            findings.append(
                {
                    "code": "INVALID_INTERACTION_ROLE_REQUIREMENT",
                    "concept": concept,
                }
            )
            continue

        for role_id in required_roles:
            role = role_index.get(role_id)
            if role is None:
                findings.append(
                    {
                        "code": "INTERACTION_ROLE_REQUIRED_ROLE_MISSING",
                        "concept": concept,
                        "role": role_id,
                    }
                )
                continue
            if role.get("concept_ref") != concept:
                findings.append(
                    {
                        "code": "INTERACTION_ROLE_CONCEPT_MISMATCH",
                        "concept": concept,
                        "role": role_id,
                        "actual_concept": role.get("concept_ref"),
                    }
                )

        required_facets = requirement.get("required_role_facets", {}) or {}
        if not isinstance(required_facets, dict):
            findings.append(
                {
                    "code": "INVALID_INTERACTION_ROLE_REQUIRED_FACETS",
                    "concept": concept,
                }
            )
            required_facets = {}
        for role_id, facets in required_facets.items():
            if role_id not in required_roles:
                findings.append(
                    {
                        "code": "INVALID_INTERACTION_ROLE_REQUIRED_FACETS",
                        "concept": concept,
                        "role": role_id,
                    }
                )
                continue
            if (
                not isinstance(facets, list)
                or any(
                    not isinstance(facet, str) or facet not in allowed_facets
                    for facet in facets
                )
            ):
                findings.append(
                    {
                        "code": "INVALID_INTERACTION_ROLE_REQUIRED_FACETS",
                        "concept": concept,
                        "role": role_id,
                    }
                )
                continue
            role = role_index.get(role_id)
            if role is None:
                continue
            for facet in facets:
                value = role.get(facet)
                missing = value is None
                if isinstance(value, str):
                    missing = not value.strip()
                elif isinstance(value, list):
                    missing = not value
                if missing:
                    findings.append(
                        {
                            "code": "INTERACTION_ROLE_REQUIRED_FACET_MISSING",
                            "concept": concept,
                            "role": role_id,
                            "facet": facet,
                        }
                    )

        required_transitions = requirement.get("required_transitions", []) or []
        if not isinstance(required_transitions, list):
            findings.append(
                {
                    "code": "INVALID_INTERACTION_ROLE_REQUIRED_TRANSITIONS",
                    "concept": concept,
                }
            )
            required_transitions = []
        for transition in required_transitions:
            if (
                not isinstance(transition, dict)
                or not isinstance(transition.get("from"), str)
                or not transition.get("from")
                or not isinstance(transition.get("to"), str)
                or not transition.get("to")
            ):
                findings.append(
                    {
                        "code": "INVALID_INTERACTION_ROLE_REQUIRED_TRANSITIONS",
                        "concept": concept,
                    }
                )
                continue
            from_role = transition["from"]
            to_role = transition["to"]
            if from_role not in required_roles or to_role not in required_roles:
                findings.append(
                    {
                        "code": "INVALID_INTERACTION_ROLE_REQUIRED_TRANSITIONS",
                        "concept": concept,
                        "from": from_role,
                        "to": to_role,
                    }
                )
                continue
            source_role = role_index.get(from_role)
            if source_role is None:
                continue
            declared_targets = {
                item.get("to")
                for item in source_role.get("transitions", []) or []
                if isinstance(item, dict)
            }
            if to_role not in declared_targets:
                findings.append(
                    {
                        "code": "INTERACTION_ROLE_REQUIRED_TRANSITION_MISSING",
                        "concept": concept,
                        "from": from_role,
                        "to": to_role,
                    }
                )

    return findings


def _evaluate_representation_selection_applicability(
    review: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    """Validate semantic-review-selected material representation subjects.

    Semantic judgement owns whether representation choice is material and which
    task-facing dimensions/challenges matter. This validator checks only the
    machine-addressable accounting and inheritance/override disposition; it does
    not infer applicability from words such as card/list/table/compare.
    """
    if not isinstance(review, dict):
        return [{"code": "REPRESENTATION_REVIEW_REQUIRED"}]
    items = review.get("representation_requirements")
    if not isinstance(items, list):
        return [{"code": "REPRESENTATION_REVIEW_REQUIRED"}]

    findings: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    allowed_materiality = {"MATERIAL", "NOT_MATERIAL"}
    allowed_dispositions = {
        "DECIDE",
        "INHERIT",
        "OVERRIDE",
        "NOT_REQUIRED",
        "QUESTION",
    }
    allowed_basis_classes = {
        "TASK_SEMANTICS",
        "INFORMATION_SEMANTICS",
        "ACCEPTED_CONSTRAINT",
        "IMPLEMENTATION_PRIMITIVE",
        "LEGACY_IMPLEMENTATION",
        "OTHER",
    }
    task_facing_basis_classes = {
        "TASK_SEMANTICS",
        "INFORMATION_SEMANTICS",
        "ACCEPTED_CONSTRAINT",
    }

    for index, item in enumerate(items):
        if not isinstance(item, dict):
            findings.append(
                {"code": "INVALID_REPRESENTATION_REQUIREMENT", "index": index}
            )
            continue
        subject_id = item.get("id")
        materiality = item.get("materiality")
        disposition = item.get("disposition")
        task_semantics = item.get("task_semantics")
        if (
            not isinstance(subject_id, str)
            or not subject_id
            or subject_id in seen_ids
            or materiality not in allowed_materiality
            or disposition not in allowed_dispositions
            or not isinstance(task_semantics, str)
            or not task_semantics.strip()
        ):
            findings.append(
                {
                    "code": "INVALID_REPRESENTATION_REQUIREMENT",
                    "index": index,
                    **(
                        {"representation_subject": subject_id}
                        if isinstance(subject_id, str) and subject_id
                        else {}
                    ),
                }
            )
            continue
        seen_ids.add(subject_id)

        bases = item.get("bases", []) or []
        valid_bases: list[dict[str, Any]] = []
        basis_ids: set[str] = set()
        if not isinstance(bases, list):
            findings.append(
                {
                    "code": "INVALID_REPRESENTATION_BASES",
                    "representation_subject": subject_id,
                }
            )
            bases = []
        for basis_index, basis in enumerate(bases):
            if not isinstance(basis, dict):
                findings.append(
                    {
                        "code": "INVALID_REPRESENTATION_BASIS",
                        "representation_subject": subject_id,
                        "index": basis_index,
                    }
                )
                continue
            basis_id = basis.get("id")
            classification = basis.get("classification")
            rationale = basis.get("rationale")
            if (
                not isinstance(basis_id, str)
                or not basis_id
                or basis_id in basis_ids
                or classification not in allowed_basis_classes
                or not isinstance(rationale, str)
                or not rationale.strip()
            ):
                findings.append(
                    {
                        "code": "INVALID_REPRESENTATION_BASIS",
                        "representation_subject": subject_id,
                        "index": basis_index,
                    }
                )
                continue
            basis_ids.add(basis_id)
            valid_bases.append(basis)

        required_dimensions = item.get("required_dimensions", []) or []
        required_challenges = item.get("required_challenges", []) or []
        for field, value in (
            ("required_dimensions", required_dimensions),
            ("required_challenges", required_challenges),
        ):
            if (
                not isinstance(value, list)
                or any(not isinstance(entry, str) or not entry for entry in value)
                or len(set(value)) != len(value)
            ):
                findings.append(
                    {
                        "code": "INVALID_REPRESENTATION_REQUIREMENT",
                        "representation_subject": subject_id,
                        "field": field,
                    }
                )

        decision_refs = item.get("decision_refs", []) or []
        if (
            not isinstance(decision_refs, list)
            or any(not isinstance(ref, str) or not ref for ref in decision_refs)
            or len(set(decision_refs)) != len(decision_refs)
        ):
            findings.append(
                {
                    "code": "INVALID_REPRESENTATION_DECISION_REFS",
                    "representation_subject": subject_id,
                }
            )
            decision_refs = []

        shared_default_ref = item.get("shared_default_ref")
        if shared_default_ref is not None and (
            not isinstance(shared_default_ref, str) or not shared_default_ref
        ):
            findings.append(
                {
                    "code": "INVALID_REPRESENTATION_SHARED_DEFAULT_REF",
                    "representation_subject": subject_id,
                }
            )
            shared_default_ref = None

        if materiality == "NOT_MATERIAL":
            rationale = item.get("rationale")
            if (
                disposition != "NOT_REQUIRED"
                or decision_refs
                or shared_default_ref is not None
                or not isinstance(rationale, str)
                or not rationale.strip()
            ):
                findings.append(
                    {
                        "code": "INVALID_REPRESENTATION_NOT_MATERIAL_DISPOSITION",
                        "representation_subject": subject_id,
                    }
                )
            continue

        if not any(
            basis.get("classification") in task_facing_basis_classes
            for basis in valid_bases
        ):
            findings.append(
                {
                    "code": "REPRESENTATION_TASK_BASIS_REQUIRED",
                    "representation_subject": subject_id,
                }
            )

        if not isinstance(required_dimensions, list) or not required_dimensions:
            findings.append(
                {
                    "code": "REPRESENTATION_REQUIRED_DIMENSIONS_REQUIRED",
                    "representation_subject": subject_id,
                }
            )
        if disposition in {"DECIDE", "OVERRIDE"} and (
            not isinstance(required_challenges, list) or not required_challenges
        ):
            findings.append(
                {
                    "code": "REPRESENTATION_REQUIRED_CHALLENGES_REQUIRED",
                    "representation_subject": subject_id,
                }
            )

        if disposition == "DECIDE":
            if not decision_refs:
                findings.append(
                    {
                        "code": "REPRESENTATION_DECISION_REFS_REQUIRED",
                        "representation_subject": subject_id,
                    }
                )
            if shared_default_ref is not None:
                findings.append(
                    {
                        "code": "REPRESENTATION_OVERRIDE_DISPOSITION_REQUIRED",
                        "representation_subject": subject_id,
                    }
                )
        elif disposition == "INHERIT":
            if shared_default_ref is None or decision_refs:
                findings.append(
                    {
                        "code": "INVALID_REPRESENTATION_INHERITANCE",
                        "representation_subject": subject_id,
                    }
                )
        elif disposition == "OVERRIDE":
            rationale = item.get("override_rationale")
            if (
                shared_default_ref is None
                or not decision_refs
                or not isinstance(rationale, str)
                or not rationale.strip()
            ):
                findings.append(
                    {
                        "code": "REPRESENTATION_OVERRIDE_RATIONALE_REQUIRED",
                        "representation_subject": subject_id,
                    }
                )
        elif disposition == "QUESTION":
            rationale = item.get("rationale")
            if not isinstance(rationale, str) or not rationale.strip():
                findings.append(
                    {
                        "code": "INVALID_REPRESENTATION_REQUIREMENT",
                        "representation_subject": subject_id,
                    }
                )
            else:
                findings.append(
                    {
                        "code": "REPRESENTATION_SELECTION_QUESTION",
                        "representation_subject": subject_id,
                        "rationale": rationale,
                    }
                )
        else:
            findings.append(
                {
                    "code": "INVALID_REPRESENTATION_MATERIAL_DISPOSITION",
                    "representation_subject": subject_id,
                }
            )

    return findings


def _evaluate_view_boundary_semantics(
    review: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    """Validate semantic-review classification for concrete topology boundaries.

    Semantic review owns which candidate boundaries are material/contestable and
    whether a separation rationale is genuinely user-facing. Harness validates
    only the machine-addressable review structure; it does not infer semantics
    from task names, capability ids, routes, components, or rationale wording.
    """
    if not isinstance(review, dict):
        return [{"code": "VIEW_BOUNDARY_REVIEW_REQUIRED"}]
    items = review.get("view_boundary_requirements")
    if not isinstance(items, list):
        return [{"code": "VIEW_BOUNDARY_REVIEW_REQUIRED"}]

    findings: list[dict[str, Any]] = []
    boundaries: dict[str, dict[str, Any]] = {}
    allowed_materiality = {"MATERIAL", "NOT_MATERIAL"}
    allowed_contestability = {"CONTESTABLE", "DETERMINISTIC"}
    allowed_outcomes = {"SEPARATE", "MERGED", "QUESTION"}
    allowed_basis_classes = {
        "USER_FACING",
        "UPSTREAM_RESPONSIBILITY",
        "IMPLEMENTATION_STRUCTURE",
        "OTHER",
    }

    for index, item in enumerate(items):
        if not isinstance(item, dict):
            findings.append({"code": "INVALID_VIEW_BOUNDARY_REQUIREMENT", "index": index})
            continue
        boundary_id = item.get("id")
        participants = item.get("participants")
        materiality = item.get("materiality")
        contestability = item.get("contestability")
        outcome = item.get("outcome")
        if (
            not isinstance(boundary_id, str)
            or not boundary_id
            or boundary_id in boundaries
            or not isinstance(participants, list)
            or len(participants) < 2
            or any(not isinstance(value, str) or not value for value in participants)
            or len(set(participants)) != len(participants)
            or materiality not in allowed_materiality
            or contestability not in allowed_contestability
            or outcome not in allowed_outcomes
        ):
            findings.append(
                {
                    "code": "INVALID_VIEW_BOUNDARY_REQUIREMENT",
                    "index": index,
                    **(
                        {"boundary": boundary_id}
                        if isinstance(boundary_id, str) and boundary_id
                        else {}
                    ),
                }
            )
            continue

        bases = item.get("rationale_bases", []) or []
        if not isinstance(bases, list):
            findings.append(
                {"code": "INVALID_VIEW_BOUNDARY_BASES", "boundary": boundary_id}
            )
            bases = []
        basis_ids: set[str] = set()
        user_facing = False
        for basis_index, basis in enumerate(bases):
            if not isinstance(basis, dict):
                findings.append(
                    {
                        "code": "INVALID_VIEW_BOUNDARY_BASIS",
                        "boundary": boundary_id,
                        "index": basis_index,
                    }
                )
                continue
            basis_id = basis.get("id")
            classification = basis.get("classification")
            rationale = basis.get("rationale")
            if (
                not isinstance(basis_id, str)
                or not basis_id
                or basis_id in basis_ids
                or classification not in allowed_basis_classes
                or not isinstance(rationale, str)
                or not rationale.strip()
            ):
                findings.append(
                    {
                        "code": "INVALID_VIEW_BOUNDARY_BASIS",
                        "boundary": boundary_id,
                        "index": basis_index,
                    }
                )
                continue
            basis_ids.add(basis_id)
            if classification == "USER_FACING":
                user_facing = True

        if materiality == "MATERIAL" and outcome == "SEPARATE" and not user_facing:
            findings.append(
                {
                    "code": "VIEW_BOUNDARY_USER_FACING_BASIS_REQUIRED",
                    "boundary": boundary_id,
                }
            )

        decision_refs = item.get("decision_refs", []) or []
        if (
            not isinstance(decision_refs, list)
            or any(not isinstance(value, str) or not value for value in decision_refs)
            or len(set(decision_refs)) != len(decision_refs)
        ):
            findings.append(
                {"code": "INVALID_VIEW_BOUNDARY_DECISION_REFS", "boundary": boundary_id}
            )
            decision_refs = []

        if materiality == "MATERIAL" and contestability == "CONTESTABLE":
            if not decision_refs:
                findings.append(
                    {
                        "code": "VIEW_BOUNDARY_DECISION_REFS_REQUIRED",
                        "boundary": boundary_id,
                    }
                )
        elif contestability == "DETERMINISTIC":
            evidence = item.get("deterministic_evidence", []) or []
            rationale = item.get("deterministic_rationale")
            if (
                not isinstance(evidence, list)
                or not evidence
                or any(not isinstance(value, str) or not value for value in evidence)
                or not isinstance(rationale, str)
                or not rationale.strip()
            ):
                findings.append(
                    {
                        "code": "VIEW_BOUNDARY_DETERMINISTIC_EVIDENCE_REQUIRED",
                        "boundary": boundary_id,
                    }
                )
            if decision_refs:
                findings.append(
                    {
                        "code": "VIEW_BOUNDARY_DETERMINISTIC_DECISION_CONFLICT",
                        "boundary": boundary_id,
                    }
                )

        shared_group = item.get("shared_decision_group")
        if shared_group is not None and (
            not isinstance(shared_group, str) or not shared_group
        ):
            findings.append(
                {
                    "code": "INVALID_VIEW_BOUNDARY_SHARED_GROUP",
                    "boundary": boundary_id,
                }
            )

        boundaries[boundary_id] = item

    groups_value = review.get("shared_boundary_decision_groups", []) or []
    if not isinstance(groups_value, list):
        findings.append({"code": "INVALID_VIEW_BOUNDARY_SHARED_GROUPS"})
        groups_value = []

    groups: dict[str, dict[str, Any]] = {}
    for index, group in enumerate(groups_value):
        if not isinstance(group, dict):
            findings.append({"code": "INVALID_VIEW_BOUNDARY_SHARED_GROUP", "index": index})
            continue
        group_id = group.get("id")
        members = group.get("boundaries")
        if (
            not isinstance(group_id, str)
            or not group_id
            or group_id in groups
            or not isinstance(members, list)
            or len(members) < 2
            or any(not isinstance(value, str) or not value for value in members)
            or len(set(members)) != len(members)
            or group.get("semantic_equivalence") != "ACCEPTED"
            or not isinstance(group.get("rationale"), str)
            or not group["rationale"].strip()
        ):
            findings.append(
                {
                    "code": "INVALID_VIEW_BOUNDARY_SHARED_GROUP",
                    "index": index,
                    **(
                        {"group": group_id}
                        if isinstance(group_id, str) and group_id
                        else {}
                    ),
                }
            )
            continue
        unknown = sorted(set(members) - set(boundaries))
        if unknown:
            findings.append(
                {
                    "code": "VIEW_BOUNDARY_SHARED_GROUP_UNKNOWN_BOUNDARY",
                    "group": group_id,
                    "boundaries": unknown,
                }
            )
        groups[group_id] = group

    for boundary_id, item in boundaries.items():
        group_id = item.get("shared_decision_group")
        if not isinstance(group_id, str) or not group_id:
            continue
        group = groups.get(group_id)
        if group is None or boundary_id not in (group.get("boundaries", []) or []):
            findings.append(
                {
                    "code": "VIEW_BOUNDARY_SHARED_GROUP_REQUIRED",
                    "boundary": boundary_id,
                    "group": group_id,
                }
            )

    return findings


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

    if "independent-obligation-granularity" in required_review_checks:
        findings.extend(
            _evaluate_independent_obligation_accounting(review, assertions)
        )

    if "observable-realization-applicability" in required_review_checks:
        findings.extend(
            _evaluate_observable_realization_applicability(review, assertions)
        )

    if "interaction-role-coherence" in required_review_checks:
        findings.extend(
            _evaluate_interaction_role_coherence(review, candidate)
        )

    if "representation-selection-applicability" in required_review_checks:
        findings.extend(
            _evaluate_representation_selection_applicability(review)
        )

    if "view-boundary-semantics" in required_review_checks:
        findings.extend(
            _evaluate_view_boundary_semantics(review)
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


__all__ = [
    'Any',
    'CoreError',
    'CoverageAssuranceView',
    'Path',
    'accepted_claims_for',
    'annotations',
    'argparse',
    'coverage_assurance_view',
    'coverage_invalidation_closure',
    'coverage_proof_available',
    'defaultdict',
    'deque',
    'evaluate_artifact',
    'evaluation_index',
    'json',
    'load',
    'main',
    'rejected_semantic_providers',
    'semantic_invalidation_closure',
    'semantic_key',
    'yaml',
]
