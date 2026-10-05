#!/usr/bin/env python3
"""Plan bounded target reconciliation without mutating Project Publication."""
from __future__ import annotations

import hashlib
import json
from typing import Any

from harness.project_model.core import CoreError
from harness.project_model.engineering_graph import derive_profile

__all__ = ["plan_reconciliation"]


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
