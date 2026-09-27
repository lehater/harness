#!/usr/bin/env python3
"""Execution-assurance boundary for Decision Exploration."""
from __future__ import annotations

from typing import Any

from harness import CoreError

ASSURANCE = {"REQUEST_BOUND", "ATTESTED_ISOLATED"}


def effective_execution_assurance(
    policy: dict[str, Any] | None,
    knowledge_kind: str,
) -> str | None:
    if policy is None:
        return None
    if policy.get("version") != 1 or policy.get("kind") != "harness-decision-policy":
        raise CoreError("invalid decision policy document")
    defaults = policy.get("defaults", {}) or {}
    if not isinstance(defaults, dict):
        raise CoreError("decision policy defaults must be a mapping")
    level = defaults.get("execution_assurance", "REQUEST_BOUND")
    matches = [
        item
        for item in policy.get("knowledge_kinds", []) or []
        if isinstance(item, dict) and item.get("knowledge_kind") == knowledge_kind
    ]
    if len(matches) > 1:
        raise CoreError(f"duplicate decision policy knowledge_kind: {knowledge_kind}")
    if matches:
        level = matches[0].get("execution_assurance", level)
    if level not in ASSURANCE:
        raise CoreError(
            f"execution_assurance must be one of {sorted(ASSURANCE)}"
        )
    return level


def evaluate_execution_assurance(
    *,
    policy: dict[str, Any] | None,
    knowledge_kind: str,
    explorer_request: dict[str, Any] | None,
    exploration_evaluation: dict[str, Any],
    self_attested_execution: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Evaluate only guarantees Harness can actually establish.

    REQUEST_BOUND is established by deterministic request/evidence binding.
    ATTESTED_ISOLATED deliberately fails closed until a trusted external
    executor/verifier adapter can authenticate runtime provenance. A workload-
    supplied receipt never upgrades assurance by itself.
    """
    level = effective_execution_assurance(policy, knowledge_kind)
    base = {
        "version": 1,
        "kind": "harness-decision-execution-assurance-evaluation",
        "knowledge_kind": knowledge_kind,
        "required": level,
    }
    if level is None or exploration_evaluation.get("status") == "NOT_REQUIRED":
        return {**base, "status": "NOT_REQUIRED", "findings": []}

    if exploration_evaluation.get("status") != "ACCEPTED":
        return {
            **base,
            "status": "REJECTED",
            "findings": [{"code": "DECISION_EXPLORATION_NOT_ACCEPTED"}],
        }

    if level == "REQUEST_BOUND":
        expected = (
            explorer_request.get("request_id")
            if isinstance(explorer_request, dict)
            else None
        )
        actual = exploration_evaluation.get("explorer_request_id")
        if not expected or actual != expected:
            return {
                **base,
                "status": "REJECTED",
                "findings": [
                    {
                        "code": "DECISION_REQUEST_BOUND_ASSURANCE_MISSING",
                        "expected": expected,
                        "actual": actual,
                    }
                ],
            }
        return {
            **base,
            "status": "ACCEPTED",
            "findings": [],
            "executor_trust": "UNATTESTED",
            "guarantee": "AUTHORIZED_INPUT_MANIFEST_BOUND",
        }

    # Do not accept a producer/workload-authored claim such as isolated: true.
    # Stronger assurance requires an external verifier whose authenticity can be
    # checked outside the explored workload. Harness has no such verifier yet.
    finding = {
        "code": "DECISION_TRUSTED_EXECUTION_VERIFIER_REQUIRED",
        "required": "ATTESTED_ISOLATED",
    }
    if self_attested_execution is not None:
        finding["self_attested_claim_ignored"] = True
    return {
        **base,
        "status": "REJECTED",
        "findings": [finding],
        "executor_trust": "UNVERIFIED",
    }
