#!/usr/bin/env python3
"""Experimental semantic-gap -> Core Question projection.

This layer is intentionally above Harness Core. It does not invent semantic
answers and does not mutate canonical state. It turns machine-addressable
semantic admission gaps into deterministic Question proposals addressed to the
Authority that owns the rejected capability.
"""
from __future__ import annotations

import copy
import re
from typing import Any

from engineering_graph import producer_index
from harness import CoreError

GAP_FINDING_CODES = {
    "MISSING_OBLIGATION",
    "MISSING_SUBJECTS",
    "MISSING_VALUES",
    "SEMANTIC_REVIEW_REQUIRED",
    "SEMANTIC_REVIEW_CHECKS_MISSING",
}


def _slug(value: str) -> str:
    return re.sub(r"[^A-Z0-9]+", "-", value.upper()).strip("-")


def _gap_identity(finding: dict[str, Any]) -> str:
    obligation = finding.get("obligation")
    if isinstance(obligation, str) and obligation:
        return obligation
    checks = finding.get("checks")
    if isinstance(checks, list) and checks:
        return "review-" + "-".join(str(item) for item in checks)
    return str(finding.get("code", "semantic-gap")).lower()


def questions_from_semantic_evaluation(
    *,
    graph: dict[str, Any],
    capability: str,
    evaluation: dict[str, Any],
) -> list[dict[str, Any]]:
    """Project accepted semantic-gap finding types into Core Question proposals."""
    if evaluation.get("status") == "ACCEPTED":
        return []

    producers = producer_index(graph)
    authority = producers.get(capability)
    if authority is None:
        raise CoreError(f"cannot route semantic gap for unknown capability: {capability}")

    proposals: dict[str, dict[str, Any]] = {}
    for finding in evaluation.get("findings", []) or []:
        if not isinstance(finding, dict):
            continue
        code = finding.get("code")
        if code not in GAP_FINDING_CODES:
            continue
        identity = _gap_identity(finding)
        question_id = (
            f"Q-SEMANTIC-{_slug(capability)}-{_slug(identity)}"
        )
        proposals[question_id] = {
            "id": question_id,
            "authority": authority,
            "text": (
                f"Resolve semantic completeness gap '{identity}' "
                f"for capability '{capability}' ({code})."
            ),
            "blocks_capabilities": [capability],
        }

    return [proposals[key] for key in sorted(proposals)]


def append_question_proposals(
    model: dict[str, Any],
    proposals: list[dict[str, Any]],
) -> dict[str, Any]:
    """Return a copy with non-conflicting proposals appended.

    Engineering-Graph callers may keep Authorities outside Core; validation is
    therefore performed later through validate_realization(), which projects
    those Authorities before Core validation.
    """
    result = copy.deepcopy(model)
    questions = result.setdefault("questions", [])
    if not isinstance(questions, list):
        raise CoreError("questions must be a list")

    existing = {
        item.get("id"): item
        for item in questions
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }
    for proposal in proposals:
        question_id = proposal.get("id")
        if not isinstance(question_id, str) or not question_id:
            raise CoreError("question proposal id is required")
        current = existing.get(question_id)
        if current is None:
            questions.append(copy.deepcopy(proposal))
            existing[question_id] = proposal
            continue
        comparable = ("authority", "text", "blocks_capabilities")
        if any(current.get(key) != proposal.get(key) for key in comparable):
            raise CoreError(f"conflicting semantic question proposal: {question_id}")

    return result
