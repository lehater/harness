#!/usr/bin/env python3
"""Semantic completeness/derivation gap -> Core Question projection above Harness Core."""
from __future__ import annotations

import copy
import re
from typing import Any

from harness.project_model.engineering_graph import producer_index
from harness.project_model.core import CoreError
from harness.assurance.semantic_acceptance import evaluation_index
from harness.assurance.semantic_derivation import derivation_evaluation_index

__all__ = ['Any',
 'CoreError',
 'DERIVATION_GAP_FINDING_CODES',
 'GAP_FINDING_CODES',
 'annotations',
 'append_question_proposals',
 'copy',
 'derivation_evaluation_index',
 'evaluation_index',
 'producer_index',
 'proposals_from_evaluation_set',
 'questions_from_derivation_evaluation',
 'questions_from_evaluation',
 'questions_from_semantic_evaluation',
 're']

GAP_FINDING_CODES = {
    "MISSING_OBLIGATION",
    "MISSING_SUBJECTS",
    "MISSING_VALUES",
    "OBLIGATION_DEFERRED",
    "OBLIGATION_QUESTION",
}

DERIVATION_GAP_FINDING_CODES = {
    "MISSING_REQUIRED_INPUT",
    "DERIVATION_QUESTION",
}


def _slug(value: str) -> str:
    return re.sub(r"[^A-Z0-9]+", "-", value.upper()).strip("-")


def _gap_identity(finding: dict[str, Any]) -> str:
    obligation = finding.get("obligation")
    subject = finding.get("subject")
    if isinstance(obligation, str) and obligation:
        if isinstance(subject, str) and subject:
            return f"{obligation}-{subject}"
        return obligation
    return str(finding.get("code", "semantic-gap")).lower()


def _gap_text(
    capability: str,
    identity: str,
    finding: dict[str, Any],
) -> str:
    details: list[str] = []
    if finding.get("subjects"):
        details.append("subjects=" + ", ".join(finding["subjects"]))
    if finding.get("values"):
        details.append("values=" + ", ".join(str(v) for v in finding["values"]))
    if finding.get("rationale"):
        details.append("rationale=" + str(finding["rationale"]))
    suffix = f"; {'; '.join(details)}" if details else ""
    return (
        f"Resolve semantic completeness gap '{identity}' "
        f"for capability '{capability}' ({finding.get('code')}{suffix})."
    )


def questions_from_semantic_evaluation(
    *,
    graph: dict[str, Any],
    capability: str,
    evaluation: dict[str, Any],
) -> list[dict[str, Any]]:
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
        if finding.get("code") not in GAP_FINDING_CODES:
            continue
        identity = _gap_identity(finding)
        question_id = f"Q-SEMANTIC-{_slug(capability)}-{_slug(identity)}"
        proposals[question_id] = {
            "id": question_id,
            "authority": authority,
            "text": _gap_text(capability, identity, finding),
            "blocks_capabilities": [capability],
        }

    return [proposals[key] for key in sorted(proposals)]


def questions_from_derivation_evaluation(
    *,
    graph: dict[str, Any],
    evaluation: dict[str, Any],
) -> list[dict[str, Any]]:
    if evaluation.get("status") == "ACCEPTED":
        return []
    if evaluation.get("kind") != "harness-semantic-derivation-evaluation":
        raise CoreError("unexpected semantic derivation evaluation kind")

    producers = producer_index(graph)
    source_capability = evaluation.get("source_capability")
    target_capability = evaluation.get("target_capability")
    if source_capability not in producers or target_capability not in producers:
        raise CoreError("semantic derivation evaluation references unknown capability")

    proposals: dict[str, dict[str, Any]] = {}
    for finding in evaluation.get("findings", []) or []:
        if not isinstance(finding, dict):
            continue
        code = finding.get("code")
        if code not in DERIVATION_GAP_FINDING_CODES:
            continue

        identity = _gap_identity(finding)
        if code == "MISSING_REQUIRED_INPUT":
            capability = source_capability
            authority = producers[source_capability]
            prefix = "INPUT"
            text = (
                f"Resolve missing upstream semantic input '{identity}' in "
                f"capability '{source_capability}' required by "
                f"'{target_capability}'."
            )
        else:
            capability = target_capability
            authority = producers[target_capability]
            prefix = "DERIVATION"
            text = (
                f"Resolve downstream derivation question '{identity}' for "
                f"capability '{target_capability}' from '{source_capability}'."
            )
            if finding.get("rationale"):
                text += f" Rationale: {finding['rationale']}"

        question_id = (
            f"Q-{prefix}-{_slug(capability)}-{_slug(identity)}"
        )
        proposals[question_id] = {
            "id": question_id,
            "authority": authority,
            "text": text,
            "blocks_capabilities": [capability],
        }

    return [proposals[key] for key in sorted(proposals)]


def questions_from_evaluation(
    *,
    graph: dict[str, Any],
    evaluation: dict[str, Any],
    capability: str | None = None,
) -> list[dict[str, Any]]:
    kind = evaluation.get("kind")
    if kind == "harness-semantic-derivation-evaluation":
        return questions_from_derivation_evaluation(
            graph=graph,
            evaluation=evaluation,
        )
    if capability is None:
        raise CoreError("artifact semantic Question routing requires capability")
    return questions_from_semantic_evaluation(
        graph=graph,
        capability=capability,
        evaluation=evaluation,
    )


def proposals_from_evaluation_set(
    evaluations: dict[str, Any],
) -> list[dict[str, Any]]:
    proposals: dict[str, dict[str, Any]] = {}
    documents: list[dict[str, Any]] = list(
        evaluation_index([evaluations]).values()
    )
    documents.extend(
        derivation_evaluation_index([evaluations]).values()
    )
    for evaluation in documents:
        for proposal in evaluation.get("question_proposals", []) or []:
            if not isinstance(proposal, dict):
                continue
            question_id = proposal.get("id")
            if not isinstance(question_id, str) or not question_id:
                raise CoreError("semantic Question proposal id is required")
            current = proposals.get(question_id)
            if current is not None and current != proposal:
                raise CoreError(
                    f"conflicting semantic Question proposals: {question_id}"
                )
            proposals[question_id] = copy.deepcopy(proposal)
    return [proposals[key] for key in sorted(proposals)]


def append_question_proposals(
    model: dict[str, Any],
    proposals: list[dict[str, Any]],
) -> dict[str, Any]:
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
        current.pop("resolution", None)

    return result
