#!/usr/bin/env python3
"""Cheap deterministic Decision Pipeline validation before semantic admission."""
from __future__ import annotations

from typing import Any

from harness.decision.decision_execution_assurance import evaluate_execution_assurance
from harness.decision.decision_exploration import evaluate_decision_exploration
from harness.decision.decision_governance import evaluate_decision_governance

__all__ = ["evaluate_decision_preflight"]


def evaluate_decision_preflight(
    *,
    contract: dict[str, Any] | None,
    policy: dict[str, Any] | None,
    axis_policies: dict[str, dict[str, str]] | None,
    explorer_request: dict[str, Any] | None,
    capability: str,
    knowledge_kind: str,
    authority: str,
    exploration_evidence: dict[str, Any] | None,
    candidate: dict[str, Any],
    model: dict[str, Any],
) -> dict[str, Any]:
    """Evaluate deterministic decision evidence without artifact semantics.

    This is intentionally an application preflight. It composes the existing
    Decision Exploration, execution-assurance and Decision Governance owners;
    it does not accept semantic knowledge and cannot create an acceptance id.
    """

    exploration = evaluate_decision_exploration(
        contract=contract,
        axis_policies=axis_policies,
        capability=capability,
        knowledge_kind=knowledge_kind,
        evidence=exploration_evidence,
        explorer_request=explorer_request,
        model=model,
    )
    execution = evaluate_execution_assurance(
        policy=policy,
        knowledge_kind=knowledge_kind,
        explorer_request=explorer_request,
        exploration_evaluation=exploration,
    )
    governance = evaluate_decision_governance(
        contract=contract,
        policy=policy,
        exploration_evaluation=exploration,
        authority=authority,
        capability=capability,
        candidate=candidate,
        model=model,
    )

    evaluations = (exploration, execution, governance)
    if all(item["status"] == "NOT_REQUIRED" for item in evaluations):
        status = "NOT_REQUIRED"
    elif all(item["status"] == "ACCEPTED" for item in evaluations):
        status = "ACCEPTED"
    else:
        status = "REJECTED"

    findings = [
        finding
        for item in evaluations
        for finding in item.get("findings", []) or []
    ]
    return {
        "version": 1,
        "kind": "harness-decision-preflight",
        "artifact": candidate.get("id"),
        "capability": capability,
        "knowledge_kind": knowledge_kind,
        "status": status,
        "findings": findings,
        "decision_exploration": exploration,
        "decision_execution_assurance": execution,
        "decision_governance": governance,
    }
