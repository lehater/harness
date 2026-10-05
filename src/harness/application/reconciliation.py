#!/usr/bin/env python3
"""Plan bounded target reconciliation without mutating Project Publication."""
from __future__ import annotations

import copy
import hashlib
import json
from typing import Any

from harness.project_model.core import CoreError
from harness.assurance.capability_lifecycle import lifecycle_index
from harness.project_model.engineering_graph import derive_profile, production_index
from .project_publication import (
    prepare_reconciliation_publication,
    validate_project_publication,
)
from .semantic_admission import admit_artifact
from .semantic_closure import evaluate_semantic_closure

__all__ = ["execute_reconciliation", "plan_reconciliation"]


def _canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )


def _target_capability_order(
    graph: dict[str, Any],
    target: str,
) -> list[str]:
    profile = derive_profile(graph, target)
    expectations = {
        item["id"]: item
        for item in profile.get("expectations", []) or []
    }
    remaining = set(expectations)
    completed: set[str] = set()
    ordered: list[str] = []
    while remaining:
        ready = sorted(
            expectation_id
            for expectation_id in remaining
            if set(expectations[expectation_id].get("depends_on", []) or [])
            <= completed
        )
        if not ready:
            raise CoreError("target profile contains unresolved dependency order")
        for expectation_id in ready:
            ordered.append(expectations[expectation_id]["capability"])
            completed.add(expectation_id)
            remaining.remove(expectation_id)
    return ordered


def _dedupe(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_key: dict[str, dict[str, Any]] = {}
    for item in items:
        by_key[_canonical_json(item)] = item
    return [by_key[key] for key in sorted(by_key)]


def plan_reconciliation(
    *,
    graph: dict[str, Any],
    target: str,
    current_publication_revision: str,
    project_frontier: dict[str, Any],
    semantic_closure: dict[str, Any],
) -> dict[str, Any]:
    """Derive affected work, unchanged reuse and the full known blocker frontier.

    The plan is disposable. The resume token binds a continuation attempt to
    the current publication plus the deterministic plan inputs; it is not a
    persisted workflow identity and carries no semantic acceptance authority.
    """

    if not isinstance(current_publication_revision, str) or not current_publication_revision:
        raise CoreError("current publication revision is required")
    if (
        project_frontier.get("version") != 1
        or project_frontier.get("kind") != "harness-project-frontier"
        or project_frontier.get("target") != target
    ):
        raise CoreError("unexpected project frontier for reconciliation target")
    if (
        semantic_closure.get("version") != 1
        or semantic_closure.get("kind") != "harness-semantic-closure-evaluation"
        or semantic_closure.get("target") != target
    ):
        raise CoreError("unexpected semantic closure for reconciliation target")

    order = _target_capability_order(graph, target)
    order_index = {capability: index for index, capability in enumerate(order)}

    stale_by_capability = {
        item["capability"]: item
        for item in semantic_closure.get("currentness_gaps", []) or []
        if isinstance(item, dict)
        and isinstance(item.get("capability"), str)
        and item.get("state") == "STALE"
    }
    semantic_by_capability = {
        item["capability"]: item
        for item in semantic_closure.get("semantic_gaps", []) or []
        if isinstance(item, dict)
        and isinstance(item.get("capability"), str)
        and item.get("code") == "SEMANTIC_ADMISSION_REQUIRED"
    }

    frontier_actions: dict[str, list[dict[str, Any]]] = {}
    non_capability_actions: list[dict[str, Any]] = []
    for item in project_frontier.get("next_actions", []) or []:
        if not isinstance(item, dict):
            continue
        capability = item.get("capability")
        if isinstance(capability, str) and capability:
            frontier_actions.setdefault(capability, []).append(item)
        else:
            non_capability_actions.append(item)

    affected = set(stale_by_capability) | set(semantic_by_capability) | set(frontier_actions)
    work: list[dict[str, Any]] = []
    for capability in sorted(
        affected,
        key=lambda value: (order_index.get(value, len(order)), value),
    ):
        if capability in stale_by_capability:
            action = "REVALIDATE_CAPABILITY"
            reason = stale_by_capability[capability].get("details", {})
        elif capability in semantic_by_capability:
            action = "VALIDATE_SEMANTICS"
            reason = semantic_by_capability[capability].get("code")
        else:
            actions = frontier_actions.get(capability, [])
            action = actions[0].get("action", "RUN_CAPABILITY_PIPELINE")
            reason = actions[0].get("reason")

        work.append(
            {
                "capability": capability,
                "action": action,
                "reason": reason,
                "frontier_actions": frontier_actions.get(capability, []),
            }
        )

    satisfied = {
        capability
        for capability in semantic_closure.get("satisfied_capabilities", []) or []
        if isinstance(capability, str)
    }
    unchanged = [
        capability
        for capability in order
        if capability in satisfied and capability not in affected
    ]

    blocked = _dedupe(
        [
            item
            for item in project_frontier.get("blocked", []) or []
            if isinstance(item, dict)
        ]
    )
    failed_validation = _dedupe(
        [
            item
            for item in project_frontier.get("failed_validation", []) or []
            if isinstance(item, dict)
        ]
    )
    gaps = _dedupe(
        [
            item
            for item in project_frontier.get("gaps", []) or []
            if isinstance(item, dict)
        ]
    )

    if project_frontier.get("status") == "COMPLETE" and not work:
        status = "COMPLETE"
    elif work or non_capability_actions:
        status = "READY"
    elif blocked or failed_validation or gaps:
        status = "BLOCKED"
    else:
        status = "WAITING"

    token_payload = {
        "target": target,
        "current_publication_revision": current_publication_revision,
        "work": work,
        "non_capability_actions": non_capability_actions,
        "blocked": blocked,
        "failed_validation": failed_validation,
        "gaps": gaps,
        "closure": {
            "structural": semantic_closure.get("structural_status"),
            "semantic": semantic_closure.get("status"),
        },
    }
    resume_token = "sha256:" + hashlib.sha256(
        _canonical_json(token_payload).encode("utf-8")
    ).hexdigest()

    return {
        "version": 1,
        "kind": "harness-reconciliation-plan",
        "target": target,
        "status": status,
        "current_publication": current_publication_revision,
        "closure": token_payload["closure"],
        "unchanged": unchanged,
        "affected": [item["capability"] for item in work],
        "work": work,
        "non_capability_actions": non_capability_actions,
        "blocked": blocked,
        "failed_validation": failed_validation,
        "gaps": gaps,
        "resume_token": resume_token,
    }



def _replace_semantic_evaluation(
    document: dict[str, Any],
    evaluation: dict[str, Any],
) -> dict[str, Any]:
    result = copy.deepcopy(document)
    rows = result.get("semantic_evaluations")
    if not isinstance(rows, list):
        raise CoreError("semantic evaluation set semantic_evaluations must be a list")
    key = (evaluation.get("artifact"), evaluation.get("capability"))
    if not all(isinstance(value, str) and value for value in key):
        raise CoreError("semantic evaluation identity requires artifact and capability")

    replacement = copy.deepcopy(evaluation)
    found = False
    next_rows: list[dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, dict):
            raise CoreError("semantic evaluation must be a mapping")
        if (row.get("artifact"), row.get("capability")) == key:
            if found:
                raise CoreError(
                    "duplicate current semantic evaluation: "
                    f"artifact={key[0]!r}, capability={key[1]!r}"
                )
            next_rows.append(replacement)
            found = True
        else:
            next_rows.append(copy.deepcopy(row))
    if not found:
        next_rows.append(replacement)
    result["semantic_evaluations"] = next_rows
    return result


def _replace_lifecycle_assertion(
    document: dict[str, Any],
    assertion: dict[str, Any],
) -> dict[str, Any]:
    result = copy.deepcopy(document)
    rows = result.get("providers")
    if not isinstance(rows, list):
        raise CoreError("capability lifecycle providers must be a list")
    capability = assertion.get("capability")
    if not isinstance(capability, str) or not capability:
        raise CoreError("lifecycle assertion capability is required")

    replacement = copy.deepcopy(assertion)
    found = False
    next_rows: list[dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, dict):
            raise CoreError("capability lifecycle provider must be a mapping")
        if row.get("capability") == capability:
            if found:
                raise CoreError(f"duplicate lifecycle capability: {capability}")
            next_rows.append(replacement)
            found = True
        else:
            next_rows.append(copy.deepcopy(row))
    if not found:
        next_rows.append(replacement)
    result["providers"] = next_rows
    return result


def _clear_decision_failures(
    document: dict[str, Any],
    capability: str,
) -> dict[str, Any]:
    result = copy.deepcopy(document)
    failures = result.get("failures")
    if not isinstance(failures, list):
        raise CoreError("decision failure set failures must be a list")
    result["failures"] = [
        copy.deepcopy(item)
        for item in failures
        if not isinstance(item, dict) or item.get("capability") != capability
    ]
    return result


def _existing_provider_ids(
    model: dict[str, Any],
    capability: str,
) -> set[str]:
    return {
        item["id"]
        for item in model.get("artifacts", []) or []
        if isinstance(item, dict)
        and isinstance(item.get("id"), str)
        and capability in (item.get("provides", []) or [])
    }


def _accepted_derivations_for_target(
    semantic_evaluations: dict[str, Any],
    capability: str,
) -> list[dict[str, Any]]:
    rows = semantic_evaluations.get("derivation_evaluations", []) or []
    if not isinstance(rows, list):
        raise CoreError("semantic evaluation set derivation_evaluations must be a list")
    return [
        copy.deepcopy(item)
        for item in rows
        if isinstance(item, dict)
        and item.get("kind") == "harness-semantic-derivation-evaluation"
        and item.get("target_capability") == capability
        and item.get("status") == "ACCEPTED"
    ]


def _validate_execution_plan(
    *,
    plan: dict[str, Any],
    target: str,
    current_revision: str,
    resume_token: str | None,
) -> None:
    if (
        plan.get("version") != 1
        or plan.get("kind") != "harness-reconciliation-plan"
        or plan.get("target") != target
    ):
        raise CoreError("unexpected reconciliation plan for target")
    if plan.get("current_publication") != current_revision:
        raise CoreError(
            "reconciliation plan is stale for current project publication"
        )
    token = plan.get("resume_token")
    if not isinstance(token, str) or not token:
        raise CoreError("reconciliation plan resume_token is required")
    if resume_token is not None and resume_token != token:
        raise CoreError("reconciliation resume token mismatch")


def execute_reconciliation(
    *,
    graph: dict[str, Any],
    target: str,
    current_publication: dict[str, Any],
    expected_revision: str,
    plan: dict[str, Any],
    skill_registry: dict[str, Any],
    knowledge_contracts: dict[str, Any],
    admission_inputs: dict[str, dict[str, Any]] | None = None,
    knowledge_contract_overlays: list[dict[str, Any]] | None = None,
    decision_contracts: dict[str, Any] | None = None,
    decision_policy: dict[str, Any] | None = None,
    resume_token: str | None = None,
) -> dict[str, Any]:
    """Execute bounded reconciliation against one immutable current revision.

    v0 deliberately handles only re/admission of already-modeled Core providers.
    It never creates providers, invents semantic evidence or acceptance ids, and
    keeps all intermediate state non-current. A publication is prepared only
    when the resulting target reaches full Semantic Closure.
    """

    checked = validate_project_publication(graph, current_publication)
    current_revision = current_publication["revision"]
    if expected_revision != current_revision:
        raise CoreError(
            "project publication compare-and-swap failed: expected "
            f"{expected_revision}, current {current_revision}"
        )
    _validate_execution_plan(
        plan=plan,
        target=target,
        current_revision=current_revision,
        resume_token=resume_token,
    )

    inputs = admission_inputs or {}
    if not isinstance(inputs, dict):
        raise CoreError("reconciliation admission_inputs must be a mapping")

    working_model = copy.deepcopy(current_publication["state"]["core_model"])
    working_evaluations = copy.deepcopy(
        current_publication["state"]["semantic_evaluations"]
    )
    working_lifecycle = copy.deepcopy(current_publication["state"]["lifecycle"])
    working_failures = copy.deepcopy(
        current_publication["state"]["decision_failures"]
    )

    work = plan.get("work", []) or []
    if not isinstance(work, list) or any(not isinstance(item, dict) for item in work):
        raise CoreError("reconciliation plan work must be a list of mappings")
    affected = {
        item.get("capability")
        for item in work
        if isinstance(item.get("capability"), str)
    }
    productions = production_index(graph)

    completed: list[str] = []
    blocked = copy.deepcopy(plan.get("blocked", []) or [])
    failed_validation = copy.deepcopy(plan.get("failed_validation", []) or [])
    gaps = copy.deepcopy(plan.get("gaps", []) or [])
    external_actions = copy.deepcopy(plan.get("non_capability_actions", []) or [])
    waiting: list[dict[str, Any]] = []

    for item in work:
        capability = item.get("capability")
        if not isinstance(capability, str) or not capability:
            raise CoreError("reconciliation work capability is required")
        production = productions.get(capability)
        if production is None:
            gaps.append(
                {
                    "capability": capability,
                    "code": "UNKNOWN_CAPABILITY",
                }
            )
            continue

        prerequisites = [
            requirement["capability"]
            for requirement in production.get("requires", []) or []
        ]
        unresolved_affected = sorted(
            prerequisite
            for prerequisite in prerequisites
            if prerequisite in affected and prerequisite not in completed
        )
        if unresolved_affected:
            waiting.append(
                {
                    "capability": capability,
                    "code": "WAITING_FOR_RECONCILIATION_PREREQUISITES",
                    "prerequisites": unresolved_affected,
                }
            )
            continue

        supplied = inputs.get(capability)
        if not isinstance(supplied, dict):
            blocked.append(
                {
                    "capability": capability,
                    "code": "RECONCILIATION_INPUT_REQUIRED",
                    "required": ["sources", "candidate", "acceptance_id"],
                }
            )
            continue

        acceptance_id = supplied.get("acceptance_id")
        if not isinstance(acceptance_id, str) or not acceptance_id:
            blocked.append(
                {
                    "capability": capability,
                    "code": "ACCEPTANCE_ID_REQUIRED",
                }
            )
            continue
        candidate = supplied.get("candidate")
        sources = supplied.get("sources")
        if not isinstance(candidate, dict) or not isinstance(sources, dict):
            blocked.append(
                {
                    "capability": capability,
                    "code": "RECONCILIATION_INPUT_REQUIRED",
                    "required": ["sources", "candidate"],
                }
            )
            continue

        provider_ids = _existing_provider_ids(working_model, capability)
        candidate_id = candidate.get("id")
        if candidate_id not in provider_ids:
            blocked.append(
                {
                    "capability": capability,
                    "code": "ARTIFACT_PRODUCTION_REQUIRED",
                    "candidate_artifact": candidate_id,
                    "existing_providers": sorted(provider_ids),
                }
            )
            continue

        lifecycle_by_capability = lifecycle_index(working_lifecycle)
        current_provider = lifecycle_by_capability.get(capability)
        if (
            current_provider is not None
            and current_provider.get("artifact") != candidate_id
        ):
            blocked.append(
                {
                    "capability": capability,
                    "code": "PROVIDER_SELECTION_CHANGE_REQUIRED",
                    "current_artifact": current_provider.get("artifact"),
                    "candidate_artifact": candidate_id,
                }
            )
            continue

        request_mode = supplied.get("decision_request_mode")
        if request_mode is None:
            request_mode = "REVISION" if current_provider is not None else "CREATE"
        if request_mode not in {"CREATE", "REVISION", "REDO"}:
            failed_validation.append(
                {
                    "capability": capability,
                    "stage": "RECONCILIATION_INPUT",
                    "code": "INVALID_DECISION_REQUEST_MODE",
                    "value": request_mode,
                }
            )
            continue

        derivations = supplied.get("derivation_evaluations")
        if derivations is None:
            derivations = _accepted_derivations_for_target(
                working_evaluations,
                capability,
            )
        if not isinstance(derivations, list):
            failed_validation.append(
                {
                    "capability": capability,
                    "stage": "RECONCILIATION_INPUT",
                    "code": "INVALID_DERIVATION_EVALUATIONS",
                }
            )
            continue

        try:
            evaluation = admit_artifact(
                graph=graph,
                model=working_model,
                skill_registry=skill_registry,
                knowledge_contracts=knowledge_contracts,
                knowledge_contract_overlays=knowledge_contract_overlays,
                decision_contracts=decision_contracts,
                decision_policy=decision_policy,
                decision_exploration=supplied.get("decision_exploration"),
                derivation_evaluations=derivations,
                capability=capability,
                sources=sources,
                candidate=candidate,
                acceptance_id=acceptance_id,
                lifecycle=working_lifecycle,
                decision_request_mode=request_mode,
            )
        except CoreError as exc:
            failed_validation.append(
                {
                    "capability": capability,
                    "stage": "SEMANTIC_ADMISSION",
                    "code": "SEMANTIC_ADMISSION_ERROR",
                    "detail": str(exc),
                }
            )
            continue

        working_evaluations = _replace_semantic_evaluation(
            working_evaluations,
            evaluation,
        )
        if evaluation.get("status") != "ACCEPTED":
            proposals = evaluation.get("question_proposals", []) or []
            if proposals:
                blocked.append(
                    {
                        "capability": capability,
                        "code": "SEMANTIC_QUESTION_REQUIRED",
                        "questions": [
                            proposal.get("id")
                            for proposal in proposals
                            if isinstance(proposal, dict)
                            and isinstance(proposal.get("id"), str)
                        ],
                        "findings": copy.deepcopy(evaluation.get("findings", []) or []),
                    }
                )
            else:
                failed_validation.append(
                    {
                        "capability": capability,
                        "stage": "SEMANTIC_ADMISSION",
                        "code": "SEMANTIC_ADMISSION_REJECTED",
                        "findings": copy.deepcopy(evaluation.get("findings", []) or []),
                    }
                )
            continue

        assertion = evaluation.get("lifecycle_assertion")
        if not isinstance(assertion, dict):
            raise CoreError(
                f"accepted semantic admission for {capability} lacks lifecycle assertion"
            )
        working_lifecycle = _replace_lifecycle_assertion(
            working_lifecycle,
            assertion,
        )
        working_failures = _clear_decision_failures(
            working_failures,
            capability,
        )
        completed.append(capability)

    final_closure: dict[str, Any] | None = None
    try:
        final_closure = evaluate_semantic_closure(
            graph=graph,
            model=working_model,
            target=target,
            skill_registry=skill_registry,
            semantic_evaluations=working_evaluations,
            lifecycle=working_lifecycle,
            knowledge_contracts=knowledge_contracts,
            knowledge_contract_overlays=knowledge_contract_overlays,
            decision_contracts=decision_contracts,
            decision_policy=decision_policy,
        )
    except CoreError as exc:
        failed_validation.append(
            {
                "stage": "FINAL_SEMANTIC_CLOSURE",
                "code": "SEMANTIC_CLOSURE_ERROR",
                "detail": str(exc),
            }
        )

    publication: dict[str, Any] | None = None
    can_publish = (
        final_closure is not None
        and final_closure.get("status") == "COMPLETE"
        and not blocked
        and not failed_validation
        and not gaps
        and not external_actions
        and not waiting
    )
    if can_publish:
        if completed:
            publication = prepare_reconciliation_publication(
                graph=graph,
                current_publication=current_publication,
                expected_revision=expected_revision,
                outcomes={capability: "CURRENT" for capability in completed},
                core_model=working_model,
                semantic_evaluations=working_evaluations,
                lifecycle=working_lifecycle,
                decision_failures=working_failures,
            )
        else:
            publication = copy.deepcopy(current_publication)

    if publication is not None:
        status = "COMPLETE"
    elif failed_validation:
        status = "FAILED_VALIDATION"
    elif blocked:
        status = "BLOCKED"
    elif waiting:
        status = "WAITING"
    else:
        status = "INCOMPLETE"

    closure = {
        "structural": (
            final_closure.get("structural_status")
            if final_closure is not None
            else plan.get("closure", {}).get("structural")
        ),
        "semantic": (
            final_closure.get("status")
            if final_closure is not None
            else plan.get("closure", {}).get("semantic")
        ),
    }
    result = {
        "version": 1,
        "kind": "harness-reconciliation-result",
        "target": target,
        "status": status,
        "current_publication": current_revision,
        "resume_token": plan["resume_token"],
        "closure": closure,
        "unchanged": copy.deepcopy(plan.get("unchanged", []) or []),
        "affected": copy.deepcopy(plan.get("affected", []) or []),
        "completed": completed,
        "blocked": blocked,
        "failed_validation": failed_validation,
        "gaps": gaps,
        "external_actions": external_actions,
        "waiting": waiting,
    }
    if final_closure is not None:
        result["semantic_closure"] = final_closure
    if publication is not None:
        result["publication"] = publication
    return result
