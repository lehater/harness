#!/usr/bin/env python3
"""Decision governance over an independently explored decision space."""
from __future__ import annotations

from typing import Any

from harness.project_model.core import CoreError

EXPLORATION = {"LOCAL": 0, "EXPLORE": 1, "RESEARCH": 2, "DEEP_RESEARCH": 3}
AUTONOMY = {"NONE": 0, "CONSERVATIVE": 1, "BROAD": 2, "MAXIMUM": 3}
ALT_STATES = {"VIABLE", "REJECTED", "UNKNOWN"}
DISPOSITIONS = {"DETERMINED", "DELEGATED", "ESCALATED"}

__all__ = [
    "annotations",
    "Any",
    "CoreError",
    "EXPLORATION",
    "AUTONOMY",
    "ALT_STATES",
    "DISPOSITIONS",
    "decision_contract_index",
    "policy_applies_to_kind",
    "effective_policy",
    "axis_policies",
    "evaluate_decision_governance",
]


def _level(value: Any, values: dict[str, int], where: str) -> str:
    if not isinstance(value, str) or value not in values:
        raise CoreError(f"{where} must be one of {sorted(values)}")
    return value


def decision_contract_index(document: dict[str, Any]) -> dict[str, dict[str, Any]]:
    if (
        document.get("version") != 1
        or document.get("kind") != "harness-knowledge-kind-decision-contracts"
    ):
        raise CoreError("invalid knowledge-kind decision contract document")
    defaults = document.get("policy_defaults", {}) or {}
    default_exploration = _level(
        defaults.get("exploration", "EXPLORE"),
        EXPLORATION,
        "policy_defaults.exploration",
    )
    default_autonomy = _level(
        defaults.get("autonomy", "CONSERVATIVE"),
        AUTONOMY,
        "policy_defaults.autonomy",
    )
    result: dict[str, dict[str, Any]] = {}
    for raw in document.get("contracts", []) or []:
        kind = raw.get("knowledge_kind") if isinstance(raw, dict) else None
        if not isinstance(kind, str) or not kind or kind in result:
            raise CoreError("decision contracts require unique knowledge_kind")
        minimum = _level(
            raw.get("minimum_exploration", default_exploration),
            EXPLORATION,
            f"{kind}.minimum_exploration",
        )
        axes: dict[str, dict[str, Any]] = {}
        for item in raw.get("axes", []) or []:
            axis = item.get("id") if isinstance(item, dict) else None
            if not isinstance(axis, str) or not axis or axis in axes:
                raise CoreError(f"{kind} decision axes require unique ids")
            dimensions = item.get("material_dimensions", []) or []
            strategies = item.get("challenge_strategies", []) or []
            minimum_probes = item.get("minimum_probes", 2)
            if (
                not isinstance(dimensions, list)
                or not dimensions
                or any(not isinstance(value, str) or not value for value in dimensions)
            ):
                raise CoreError(f"{kind}.{axis} requires material_dimensions")
            if (
                not isinstance(strategies, list)
                or not strategies
                or any(not isinstance(value, str) or not value for value in strategies)
            ):
                raise CoreError(f"{kind}.{axis} requires challenge_strategies")
            if not isinstance(minimum_probes, int) or minimum_probes < 1:
                raise CoreError(f"{kind}.{axis} minimum_probes must be positive")
            subject_scope = item.get("subject_scope")
            if subject_scope is not None and (
                not isinstance(subject_scope, str) or not subject_scope
            ):
                raise CoreError(f"{kind}.{axis} subject_scope must be a non-empty string")
            axes[axis] = {
                "minimum_exploration": _level(
                    item.get("minimum_exploration", minimum),
                    EXPLORATION,
                    f"{kind}.{axis}.minimum_exploration",
                ),
                "delegation_requires": _level(
                    item.get("delegation_requires", "BROAD"),
                    AUTONOMY,
                    f"{kind}.{axis}.delegation_requires",
                ),
                "material_dimensions": list(dict.fromkeys(dimensions)),
                "challenge_strategies": list(dict.fromkeys(strategies)),
                "minimum_probes": minimum_probes,
                **(
                    {"subject_scope": subject_scope}
                    if subject_scope is not None
                    else {}
                ),
            }
        if not axes:
            raise CoreError(f"{kind} decision contract requires axes")
        result[kind] = {
            "knowledge_kind": kind,
            "required": bool(raw.get("required", True)),
            "policy_defaults": {
                "exploration": default_exploration,
                "autonomy": default_autonomy,
            },
            "axes": axes,
        }
    return result


def _policy_item(policy: dict[str, Any] | None, kind: str) -> dict[str, Any]:
    if policy is None:
        return {}
    if (
        policy.get("version") != 1
        or policy.get("kind") != "harness-decision-policy"
    ):
        raise CoreError("invalid decision policy document")
    matches = [
        item
        for item in policy.get("knowledge_kinds", []) or []
        if isinstance(item, dict) and item.get("knowledge_kind") == kind
    ]
    if len(matches) > 1:
        raise CoreError(f"duplicate decision policy knowledge_kind: {kind}")
    return matches[0] if matches else {}


def policy_applies_to_kind(
    policy: dict[str, Any] | None,
    knowledge_kind: str,
) -> bool:
    if policy is None:
        return False
    if (
        policy.get("version") != 1
        or policy.get("kind") != "harness-decision-policy"
    ):
        raise CoreError("invalid decision policy document")
    items = policy.get("knowledge_kinds", []) or []
    if not isinstance(items, list):
        raise CoreError("decision policy knowledge_kinds must be a list")
    matches = [
        item
        for item in items
        if isinstance(item, dict) and item.get("knowledge_kind") == knowledge_kind
    ]
    if len(matches) > 1:
        raise CoreError(f"duplicate decision policy knowledge_kind: {knowledge_kind}")
    # Backward-compatible global policies keep their existing meaning when they
    # declare defaults or when no explicit knowledge-kind scope is present.
    if "defaults" in policy or not items:
        return True
    return bool(matches)


def effective_policy(
    contract: dict[str, Any],
    policy: dict[str, Any] | None,
    axis: str,
) -> dict[str, str]:
    defaults = dict(contract["policy_defaults"])
    if policy is not None:
        policy_defaults = policy.get("defaults", {}) or {}
        if not isinstance(policy_defaults, dict):
            raise CoreError("decision policy defaults must be a mapping")
        defaults.update(policy_defaults)
    item = _policy_item(policy, contract["knowledge_kind"])
    exploration = item.get("exploration", defaults["exploration"])
    autonomy = item.get("autonomy", defaults["autonomy"])
    for override in item.get("axes", []) or []:
        if isinstance(override, dict) and override.get("axis") == axis:
            exploration = override.get("exploration", exploration)
            autonomy = override.get("autonomy", autonomy)
            break
    exploration = _level(
        exploration,
        EXPLORATION,
        f"policy.{contract['knowledge_kind']}.{axis}.exploration",
    )
    autonomy = _level(
        autonomy,
        AUTONOMY,
        f"policy.{contract['knowledge_kind']}.{axis}.autonomy",
    )
    minimum = contract["axes"][axis]["minimum_exploration"]
    if EXPLORATION[exploration] < EXPLORATION[minimum]:
        exploration = minimum
    return {"exploration": exploration, "autonomy": autonomy}


def axis_policies(
    contract: dict[str, Any] | None,
    policy: dict[str, Any] | None,
) -> dict[str, dict[str, str]] | None:
    if (
        contract is None
        or not contract.get("required")
        or not policy_applies_to_kind(policy, contract["knowledge_kind"])
    ):
        return None
    return {
        axis: effective_policy(contract, policy, axis)
        for axis in contract["axes"]
    }


def _finding(
    code: str,
    axis: str | None = None,
    decision: str | None = None,
    **extra: Any,
) -> dict[str, Any]:
    value: dict[str, Any] = {"code": code}
    if axis is not None:
        value["axis"] = axis
    if decision is not None:
        value["decision"] = decision
    value.update(extra)
    return value


def _evaluate_view_boundary_subject_governance(
    *,
    explored_axis: dict[str, Any],
    review_axis: dict[str, Any] | None,
    candidate: dict[str, Any],
) -> list[dict[str, Any]]:
    """Bind material topology boundaries to boundary-local decision evidence."""
    semantic_review = candidate.get("semantic_review")
    if not isinstance(semantic_review, dict):
        return [_finding("VIEW_BOUNDARY_REVIEW_REQUIRED", explored_axis.get("axis"))]
    requirements = semantic_review.get("view_boundary_requirements")
    if not isinstance(requirements, list):
        return [_finding("VIEW_BOUNDARY_REVIEW_REQUIRED", explored_axis.get("axis"))]

    axis = explored_axis.get("axis")
    findings: list[dict[str, Any]] = []
    boundaries = {
        item.get("id"): item
        for item in requirements
        if isinstance(item, dict)
        and isinstance(item.get("id"), str)
        and item.get("id")
    }
    material = {
        boundary_id: item
        for boundary_id, item in boundaries.items()
        if item.get("materiality") == "MATERIAL"
    }
    explored_decisions = {
        item.get("id"): item
        for item in explored_axis.get("decision_points", []) or []
        if isinstance(item, dict)
        and isinstance(item.get("id"), str)
        and item.get("id")
    }
    reviewed_decisions = {
        item.get("id"): item
        for item in (review_axis.get("decisions", []) if isinstance(review_axis, dict) else []) or []
        if isinstance(item, dict)
        and isinstance(item.get("id"), str)
        and item.get("id")
    }
    groups = {
        item.get("id"): item
        for item in semantic_review.get("shared_boundary_decision_groups", []) or []
        if isinstance(item, dict)
        and isinstance(item.get("id"), str)
        and item.get("id")
    }

    for boundary_id, boundary in material.items():
        if boundary.get("outcome") == "SEPARATE":
            bases = boundary.get("rationale_bases", []) or []
            if not any(
                isinstance(item, dict) and item.get("classification") == "USER_FACING"
                for item in bases
            ):
                findings.append(
                    _finding(
                        "VIEW_BOUNDARY_USER_FACING_BASIS_REQUIRED",
                        axis,
                        boundary=boundary_id,
                    )
                )

        if boundary.get("contestability") == "DETERMINISTIC":
            continue
        if boundary.get("contestability") != "CONTESTABLE":
            continue

        refs = boundary.get("decision_refs", []) or []
        if not isinstance(refs, list) or not refs:
            findings.append(
                _finding(
                    "VIEW_BOUNDARY_DECISION_COVERAGE_MISSING",
                    axis,
                    boundary=boundary_id,
                )
            )
            continue

        for decision_id in refs:
            explored = explored_decisions.get(decision_id)
            reviewed = reviewed_decisions.get(decision_id)
            subjects = (
                explored.get("subjects", [])
                if isinstance(explored, dict)
                else []
            ) or []
            if (
                explored is None
                or reviewed is None
                or boundary_id not in subjects
            ):
                findings.append(
                    _finding(
                        "VIEW_BOUNDARY_DECISION_COVERAGE_MISSING",
                        axis,
                        decision_id if isinstance(decision_id, str) else None,
                        boundary=boundary_id,
                    )
                )

    for decision_id, explored in explored_decisions.items():
        subjects = [
            value
            for value in (explored.get("subjects", []) or [])
            if value in material
        ]
        if len(subjects) <= 1:
            continue

        group_ids = {
            material[boundary_id].get("shared_decision_group")
            for boundary_id in subjects
        }
        if len(group_ids) != 1:
            findings.append(
                _finding(
                    "VIEW_BOUNDARY_SHARED_DECISION_REVIEW_REQUIRED",
                    axis,
                    decision_id,
                    boundaries=sorted(subjects),
                )
            )
            continue
        group_id = next(iter(group_ids))
        group = groups.get(group_id) if isinstance(group_id, str) else None
        group_members = (
            set(group.get("boundaries", []) or [])
            if isinstance(group, dict)
            else set()
        )
        if (
            group is None
            or group.get("semantic_equivalence") != "ACCEPTED"
            or not set(subjects).issubset(group_members)
            or any(
                decision_id not in (material[boundary_id].get("decision_refs", []) or [])
                for boundary_id in subjects
            )
        ):
            findings.append(
                _finding(
                    "VIEW_BOUNDARY_SHARED_DECISION_REVIEW_REQUIRED",
                    axis,
                    decision_id,
                    boundaries=sorted(subjects),
                    **(
                        {"group": group_id}
                        if isinstance(group_id, str) and group_id
                        else {}
                    ),
                )
            )

    return findings



def _evaluate_representation_subject_governance(
    *,
    explored_axis: dict[str, Any],
    review_axis: dict[str, Any] | None,
    candidate: dict[str, Any],
    axis_contract: dict[str, Any],
) -> list[dict[str, Any]]:
    """Bind semantic-review-selected representation subjects to local decisions.

    Semantic review owns applicability and task-facing requirements. Decision
    Governance proves deterministic subject coverage and that the explored
    alternatives actually challenge the dimensions/strategies the review marked
    material. Concrete UI primitives remain downstream choices.
    """
    semantic_review = candidate.get("semantic_review")
    if not isinstance(semantic_review, dict):
        return [_finding("REPRESENTATION_REVIEW_REQUIRED", explored_axis.get("axis"))]
    requirements = semantic_review.get("representation_requirements")
    if not isinstance(requirements, list):
        return [_finding("REPRESENTATION_REVIEW_REQUIRED", explored_axis.get("axis"))]

    axis = explored_axis.get("axis")
    findings: list[dict[str, Any]] = []
    explored_decisions = {
        item.get("id"): item
        for item in explored_axis.get("decision_points", []) or []
        if isinstance(item, dict)
        and isinstance(item.get("id"), str)
        and item.get("id")
    }
    reviewed_decisions = {
        item.get("id"): item
        for item in (review_axis.get("decisions", []) if isinstance(review_axis, dict) else []) or []
        if isinstance(item, dict)
        and isinstance(item.get("id"), str)
        and item.get("id")
    }
    material_dimensions = set(axis_contract.get("material_dimensions", []) or [])
    challenge_strategies = set(axis_contract.get("challenge_strategies", []) or [])
    task_facing_basis_classes = {
        "TASK_SEMANTICS",
        "INFORMATION_SEMANTICS",
        "ACCEPTED_CONSTRAINT",
    }

    for requirement in requirements:
        if not isinstance(requirement, dict):
            continue
        subject_id = requirement.get("id")
        if (
            not isinstance(subject_id, str)
            or not subject_id
            or requirement.get("materiality") != "MATERIAL"
        ):
            continue

        bases = requirement.get("bases", []) or []
        if not any(
            isinstance(item, dict)
            and item.get("classification") in task_facing_basis_classes
            for item in bases
        ):
            findings.append(
                _finding(
                    "REPRESENTATION_TASK_BASIS_REQUIRED",
                    axis,
                    representation_subject=subject_id,
                )
            )

        disposition = requirement.get("disposition")
        shared_default_ref = requirement.get("shared_default_ref")
        if disposition == "INHERIT":
            continue
        if disposition == "DECIDE" and isinstance(shared_default_ref, str) and shared_default_ref:
            findings.append(
                _finding(
                    "REPRESENTATION_OVERRIDE_DISPOSITION_REQUIRED",
                    axis,
                    representation_subject=subject_id,
                )
            )
        if disposition == "OVERRIDE":
            rationale = requirement.get("override_rationale")
            if (
                not isinstance(shared_default_ref, str)
                or not shared_default_ref
                or not isinstance(rationale, str)
                or not rationale.strip()
            ):
                findings.append(
                    _finding(
                        "REPRESENTATION_OVERRIDE_RATIONALE_REQUIRED",
                        axis,
                        representation_subject=subject_id,
                    )
                )

        if disposition not in {"DECIDE", "OVERRIDE"}:
            continue

        refs = requirement.get("decision_refs", []) or []
        if not isinstance(refs, list) or not refs:
            findings.append(
                _finding(
                    "REPRESENTATION_DECISION_COVERAGE_MISSING",
                    axis,
                    representation_subject=subject_id,
                )
            )
            continue

        required_dimensions = requirement.get("required_dimensions", []) or []
        required_challenges = requirement.get("required_challenges", []) or []
        for dimension in required_dimensions:
            if dimension not in material_dimensions:
                findings.append(
                    _finding(
                        "REPRESENTATION_REQUIRED_DIMENSION_UNKNOWN",
                        axis,
                        representation_subject=subject_id,
                        dimension=dimension,
                    )
                )
        for challenge in required_challenges:
            if challenge not in challenge_strategies:
                findings.append(
                    _finding(
                        "REPRESENTATION_REQUIRED_CHALLENGE_UNKNOWN",
                        axis,
                        representation_subject=subject_id,
                        challenge=challenge,
                    )
                )

        for decision_id in refs:
            explored = explored_decisions.get(decision_id)
            reviewed = reviewed_decisions.get(decision_id)
            subjects = (
                explored.get("subjects", [])
                if isinstance(explored, dict)
                else []
            ) or []
            if (
                explored is None
                or reviewed is None
                or subject_id not in subjects
            ):
                findings.append(
                    _finding(
                        "REPRESENTATION_DECISION_COVERAGE_MISSING",
                        axis,
                        decision_id if isinstance(decision_id, str) else None,
                        representation_subject=subject_id,
                    )
                )
                continue

            scoped_strategies = set(
                explored.get("scoped_probe_strategies", []) or []
            )
            missing_challenges = sorted(
                set(required_challenges) - scoped_strategies
            )
            if missing_challenges:
                findings.append(
                    _finding(
                        "REPRESENTATION_REQUIRED_CHALLENGE_MISSING",
                        axis,
                        decision_id,
                        representation_subject=subject_id,
                        challenges=missing_challenges,
                    )
                )

            effects = explored.get("alternative_material_effects", {}) or {}
            for dimension in required_dimensions:
                if dimension not in material_dimensions:
                    continue
                values = {
                    material_effects.get(dimension)
                    for material_effects in effects.values()
                    if isinstance(material_effects, dict)
                    and dimension in material_effects
                }
                if len(values) < 2:
                    findings.append(
                        _finding(
                            "REPRESENTATION_REQUIRED_DIMENSION_NOT_CHALLENGED",
                            axis,
                            decision_id,
                            representation_subject=subject_id,
                            dimension=dimension,
                        )
                    )

    return findings


def evaluate_decision_governance(
    *,
    contract: dict[str, Any] | None,
    policy: dict[str, Any] | None,
    exploration_evaluation: dict[str, Any],
    authority: str,
    capability: str,
    candidate: dict[str, Any],
    model: dict[str, Any],
) -> dict[str, Any]:
    base = {
        "version": 1,
        "kind": "harness-decision-governance-evaluation",
        "artifact": candidate.get("id"),
        "capability": capability,
        "knowledge_kind": contract.get("knowledge_kind") if contract else None,
    }
    if (
        contract is None
        or not contract.get("required")
        or not policy_applies_to_kind(
            policy,
            contract["knowledge_kind"],
        )
    ):
        return {**base, "status": "NOT_REQUIRED", "findings": [], "axes": []}
    if exploration_evaluation.get("status") != "ACCEPTED":
        return {
            **base,
            "status": "REJECTED",
            "findings": [_finding("DECISION_EXPLORATION_NOT_ACCEPTED")],
            "axes": [],
        }

    review = candidate.get("decision_review")
    if not isinstance(review, dict):
        return {
            **base,
            "status": "REJECTED",
            "findings": [_finding("DECISION_REVIEW_REQUIRED")],
            "axes": [],
        }

    questions = {
        item.get("id"): item
        for item in model.get("questions", []) or []
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }
    review_axes = {
        item.get("axis"): item
        for item in review.get("axes", []) or []
        if isinstance(item, dict) and isinstance(item.get("axis"), str)
    }
    findings: list[dict[str, Any]] = []
    evaluated_axes: list[dict[str, Any]] = []

    for explored_axis in exploration_evaluation.get("axes", []) or []:
        axis = explored_axis["axis"]
        applicability = explored_axis["applicability"]
        axis_contract = contract["axes"].get(axis, {})
        if axis_contract.get("subject_scope") == "view-boundary":
            findings.extend(
                _evaluate_view_boundary_subject_governance(
                    explored_axis=explored_axis,
                    review_axis=review_axes.get(axis),
                    candidate=candidate,
                )
            )
        if axis_contract.get("subject_scope") == "representation-subject":
            findings.extend(
                _evaluate_representation_subject_governance(
                    explored_axis=explored_axis,
                    review_axis=review_axes.get(axis),
                    candidate=candidate,
                    axis_contract=axis_contract,
                )
            )
        if applicability == "NOT_APPLICABLE":
            if axis in review_axes:
                findings.append(_finding("DECISION_REVIEW_FOR_NOT_APPLICABLE_AXIS", axis))
            evaluated_axes.append(
                {"axis": axis, "applicability": applicability, "decisions": []}
            )
            continue
        if applicability != "APPLICABLE":
            findings.append(_finding("DECISION_APPLICABILITY_NOT_RESOLVED", axis))
            continue

        review_axis = review_axes.get(axis)
        if review_axis is None:
            findings.append(_finding("DECISION_REVIEW_AXIS_MISSING", axis))
            continue
        review_decisions = {
            item.get("id"): item
            for item in review_axis.get("decisions", []) or []
            if isinstance(item, dict) and isinstance(item.get("id"), str)
        }
        explored_decisions = {
            item["id"]: item
            for item in explored_axis.get("decision_points", []) or []
        }
        if set(review_decisions) != set(explored_decisions):
            findings.append(
                _finding(
                    "DECISION_REVIEW_POINT_SET_MISMATCH",
                    axis,
                    expected=sorted(explored_decisions),
                    actual=sorted(review_decisions),
                )
            )

        evaluated_decisions: list[dict[str, Any]] = []
        effective = effective_policy(contract, policy, axis)
        threshold = contract["axes"][axis]["delegation_requires"]

        for decision_id, explored in explored_decisions.items():
            decision = review_decisions.get(decision_id)
            if decision is None:
                continue
            owner = decision.get("owner_authority")
            if not isinstance(owner, str) or not owner:
                findings.append(_finding("DECISION_OWNER_REQUIRED", axis, decision_id))
                owner = ""

            explored_alt_ids = set(explored.get("alternatives", []) or [])
            reviewed_alternatives = decision.get("alternatives", []) or []
            if not isinstance(reviewed_alternatives, list):
                reviewed_alternatives = []
            reviewed_alt_ids = {
                item.get("id")
                for item in reviewed_alternatives
                if isinstance(item, dict) and isinstance(item.get("id"), str)
            }
            if reviewed_alt_ids != explored_alt_ids:
                findings.append(
                    _finding(
                        "DECISION_ALTERNATIVE_SET_MISMATCH",
                        axis,
                        decision_id,
                        expected=sorted(explored_alt_ids),
                        actual=sorted(reviewed_alt_ids),
                    )
                )

            viable: list[str] = []
            unknown: list[str] = []
            for alternative in reviewed_alternatives:
                alt_id = alternative.get("id") if isinstance(alternative, dict) else None
                if not isinstance(alt_id, str) or alt_id not in explored_alt_ids:
                    continue
                state = alternative.get("state")
                if state not in ALT_STATES:
                    findings.append(
                        _finding(
                            "DECISION_ALTERNATIVE_STATE_INVALID",
                            axis,
                            decision_id,
                            alternative=alt_id,
                        )
                    )
                    continue
                if state == "REJECTED":
                    rationale = alternative.get("rationale")
                    if not isinstance(rationale, str) or not rationale.strip():
                        findings.append(
                            _finding(
                                "DECISION_REJECTION_RATIONALE_REQUIRED",
                                axis,
                                decision_id,
                                alternative=alt_id,
                            )
                        )
                elif state == "VIABLE":
                    viable.append(alt_id)
                else:
                    unknown.append(alt_id)

            disposition = decision.get("disposition")
            if disposition not in DISPOSITIONS:
                findings.append(
                    _finding("DECISION_DISPOSITION_INVALID", axis, decision_id)
                )
                disposition = None
            selected = decision.get("selected")
            delegated = (
                owner == authority
                and AUTONOMY[effective["autonomy"]] >= AUTONOMY[threshold]
            )

            if disposition == "DETERMINED":
                if unknown or len(viable) != 1:
                    findings.append(
                        _finding(
                            "DECISION_NOT_DETERMINED",
                            axis,
                            decision_id,
                            viable=sorted(viable),
                            unknown=sorted(unknown),
                        )
                    )
                elif selected != viable[0]:
                    findings.append(
                        _finding("DECISION_SELECTION_INVALID", axis, decision_id)
                    )
            elif disposition == "DELEGATED":
                if unknown or len(viable) < 2:
                    findings.append(
                        _finding(
                            "DECISION_NOT_A_CHOICE",
                            axis,
                            decision_id,
                            viable=sorted(viable),
                            unknown=sorted(unknown),
                        )
                    )
                if not delegated:
                    findings.append(
                        _finding(
                            "DECISION_AUTONOMY_EXCEEDED",
                            axis,
                            decision_id,
                            autonomy=effective["autonomy"],
                            required=threshold,
                            owner_authority=owner,
                        )
                    )
                if selected not in viable:
                    findings.append(
                        _finding("DECISION_SELECTION_INVALID", axis, decision_id)
                    )
            elif disposition == "ESCALATED":
                if selected is not None:
                    findings.append(
                        _finding(
                            "DECISION_ESCALATION_MUST_NOT_SELECT",
                            axis,
                            decision_id,
                        )
                    )
                question = questions.get(decision.get("question"))
                if question is None:
                    findings.append(
                        _finding("DECISION_QUESTION_REQUIRED", axis, decision_id)
                    )
                else:
                    if question.get("resolution") is not None:
                        findings.append(
                            _finding(
                                "DECISION_QUESTION_ALREADY_RESOLVED",
                                axis,
                                decision_id,
                            )
                        )
                    if owner and question.get("authority") != owner:
                        findings.append(
                            _finding(
                                "DECISION_QUESTION_AUTHORITY_MISMATCH",
                                axis,
                                decision_id,
                            )
                        )
                    blocked = (
                        capability
                        in (question.get("blocks_capabilities", []) or [])
                        or candidate.get("id")
                        in (question.get("blocks", []) or [])
                    )
                    if not blocked:
                        findings.append(
                            _finding(
                                "DECISION_QUESTION_DOES_NOT_BLOCK_AFFECTED_KNOWLEDGE",
                                axis,
                                decision_id,
                            )
                        )
                must_escalate = (
                    bool(unknown)
                    or owner != authority
                    or len(viable) == 0
                    or (len(viable) >= 2 and not delegated)
                )
                if not must_escalate:
                    findings.append(
                        _finding("DECISION_UNNECESSARY_ESCALATION", axis, decision_id)
                    )

            evaluated_decisions.append(
                {
                    "id": decision_id,
                    "owner_authority": owner,
                    "viable": sorted(viable),
                    "unknown": sorted(unknown),
                    "disposition": disposition,
                    "delegation_allowed": delegated,
                }
            )

        evaluated_axes.append(
            {
                "axis": axis,
                "applicability": applicability,
                "autonomy": effective["autonomy"],
                "decisions": evaluated_decisions,
            }
        )

    return {
        **base,
        "status": "ACCEPTED" if not findings else "REJECTED",
        "findings": findings,
        "axes": evaluated_axes,
    }
