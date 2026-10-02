#!/usr/bin/env python3
"""Strict semantic/currentness closure above structural target state."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml

from agent_router import validate_skill_registry
from harness.assurance.capability_lifecycle import evaluate_lifecycle_target, lifecycle_index, lifecycle_states
from harness.project_model.engineering_graph import derive_profile, evaluate_engineering_target, production_index, validate_realization
from harness.project_model.core import CoreError, question_frontier
from harness.assurance.semantic_acceptance import evaluation_index
from semantic_admission import derive_acceptance_policy_fingerprints
from semantic_questions import append_question_proposals, proposals_from_evaluation_set


def load_yaml(path: str | Path) -> dict[str, Any]:
    value = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise CoreError(f"{path} must contain a mapping")
    return value


def evaluate_semantic_closure(
    *,
    graph: dict[str, Any],
    model: dict[str, Any],
    target: str,
    skill_registry: dict[str, Any],
    semantic_evaluations: dict[str, Any],
    lifecycle: dict[str, Any],
    knowledge_contracts: dict[str, Any] | None = None,
    knowledge_contract_overlays: list[dict[str, Any]] | None = None,
    decision_contracts: dict[str, Any] | None = None,
    decision_policy: dict[str, Any] | None = None,
) -> dict[str, Any]:
    validate_skill_registry(skill_registry)
    if knowledge_contracts is None:
        knowledge_contracts = load_yaml(
            Path(__file__).resolve().parent
            / "spec/semantic-acceptance/knowledge-kind-contracts-v1.yaml"
        )
    if decision_contracts is None:
        decision_contracts = load_yaml(
            Path(__file__).resolve().parent
            / "spec/decision-governance/knowledge-kind-decision-contracts-v1.yaml"
        )
    current_policy_fingerprints = derive_acceptance_policy_fingerprints(
        graph=graph,
        knowledge_contracts=knowledge_contracts,
        knowledge_contract_overlays=knowledge_contract_overlays,
        decision_contracts=decision_contracts,
        decision_policy=decision_policy,
    )

    proposals = proposals_from_evaluation_set(semantic_evaluations)
    projected_model = append_question_proposals(model, proposals)
    realized = validate_realization(graph, projected_model)

    structural = evaluate_engineering_target(graph, target, realized)
    profile = derive_profile(graph, target)
    productions = production_index(graph)
    evaluations = evaluation_index([semantic_evaluations])
    lifecycle_by_capability = lifecycle_index(lifecycle)
    states = lifecycle_states(
        graph,
        realized,
        lifecycle,
        current_acceptance_policy_fingerprints=current_policy_fingerprints,
    )

    routed_kinds = {
        item["knowledge_kind"]
        for item in skill_registry.get("routes", []) or []
    }
    artifacts = realized.get("artifacts", []) or []
    providers: dict[str, list[str]] = {}
    for artifact in artifacts:
        for capability in artifact.get("provides", []) or []:
            providers.setdefault(capability, []).append(artifact["id"])

    semantic_gaps: list[dict[str, Any]] = []
    currentness_gaps: list[dict[str, Any]] = []
    satisfied: list[str] = []

    structural_satisfied = set(structural.get("satisfied", []) or [])
    proposals_by_capability: dict[str, list[dict[str, Any]]] = {}
    for proposal in proposals:
        for capability in proposal.get("blocks_capabilities", []) or []:
            proposals_by_capability.setdefault(capability, []).append(proposal)

    for expectation in profile["expectations"]:
        capability = expectation["capability"]

        direct_proposals = proposals_by_capability.get(capability, [])
        if direct_proposals:
            lifecycle_item = lifecycle_by_capability.get(capability)
            artifact_id = (
                lifecycle_item.get("artifact")
                if isinstance(lifecycle_item, dict)
                else None
            )
            evaluation = (
                evaluations.get((artifact_id, capability))
                if artifact_id is not None
                else None
            )
            if evaluation is None and artifact_id is not None:
                evaluation = evaluations.get((artifact_id, None))
            semantic_gaps.append(
                {
                    "capability": capability,
                    "authority": expectation["authority"],
                    **({"artifact": artifact_id} if artifact_id else {}),
                    "code": "SEMANTIC_QUESTION",
                    "questions": [item["id"] for item in direct_proposals],
                    "findings": (
                        evaluation.get("findings", [])
                        if isinstance(evaluation, dict)
                        else []
                    ),
                }
            )
            continue

        # WAIT/PENDING structural expectations are consequences of an upstream
        # blocker, not independent lifecycle defects. Evaluate currentness only
        # for expectations that remain structurally satisfied after Question
        # projection.
        if expectation["id"] not in structural_satisfied:
            continue

        production = productions[capability]
        knowledge_kind = production.get("knowledge_kind")
        if knowledge_kind not in routed_kinds:
            semantic_gaps.append(
                {
                    "capability": capability,
                    "authority": expectation["authority"],
                    "code": "NO_STRICT_SEMANTIC_CONTRACT",
                    "knowledge_kind": knowledge_kind,
                }
            )
            continue

        lifecycle_item = lifecycle_by_capability.get(capability)
        state = states[capability]
        if lifecycle_item is None or state["state"] != "CURRENT":
            currentness_gaps.append(
                {
                    "capability": capability,
                    "authority": expectation["authority"],
                    "state": state["state"],
                    "details": state,
                }
            )
            continue

        artifact_id = lifecycle_item["artifact"]
        if artifact_id not in providers.get(capability, []):
            currentness_gaps.append(
                {
                    "capability": capability,
                    "authority": expectation["authority"],
                    "state": "INVALID_PROVIDER",
                    "artifact": artifact_id,
                }
            )
            continue

        evaluation = evaluations.get((artifact_id, capability))
        if evaluation is None:
            evaluation = evaluations.get((artifact_id, None))
        admission = evaluation.get("admission", {}) if evaluation else {}
        if (
            evaluation is None
            or evaluation.get("status") != "ACCEPTED"
            or admission.get("status") != "ACCEPTED"
        ):
            semantic_gaps.append(
                {
                    "capability": capability,
                    "authority": expectation["authority"],
                    "artifact": artifact_id,
                    "code": "SEMANTIC_ADMISSION_REQUIRED",
                    "findings": (
                        evaluation.get("findings", [])
                        if isinstance(evaluation, dict)
                        else []
                    ),
                }
            )
            continue

        if admission.get("acceptance_id") != lifecycle_item.get("acceptance_id"):
            currentness_gaps.append(
                {
                    "capability": capability,
                    "authority": expectation["authority"],
                    "state": "ACCEPTANCE_ID_MISMATCH",
                    "semantic_acceptance_id": admission.get("acceptance_id"),
                    "lifecycle_acceptance_id": lifecycle_item.get("acceptance_id"),
                }
            )
            continue

        if admission.get("acceptance_policy_fingerprint") != lifecycle_item.get(
            "acceptance_policy_fingerprint"
        ):
            currentness_gaps.append(
                {
                    "capability": capability,
                    "authority": expectation["authority"],
                    "state": "ACCEPTANCE_POLICY_EVIDENCE_MISMATCH",
                    "semantic_policy_fingerprint": admission.get(
                        "acceptance_policy_fingerprint"
                    ),
                    "lifecycle_policy_fingerprint": lifecycle_item.get(
                        "acceptance_policy_fingerprint"
                    ),
                }
            )
            continue

        satisfied.append(capability)

    lifecycle_target = evaluate_lifecycle_target(
        graph,
        target,
        realized,
        lifecycle,
        current_acceptance_policy_fingerprints=current_policy_fingerprints,
    )
    proposal_ids = [item["id"] for item in proposals]
    frontier = question_frontier(realized, proposal_ids) if proposal_ids else []

    complete = (
        structural["status"] == "COMPLETE"
        and not semantic_gaps
        and not currentness_gaps
        and not frontier
        and len(satisfied) == len(profile["expectations"])
    )
    status = (
        "COMPLETE"
        if complete
        else "BLOCKED"
        if frontier or structural["status"] == "BLOCKED"
        else "INCOMPLETE"
    )

    return {
        "version": 1,
        "kind": "harness-semantic-closure-evaluation",
        "target": target,
        "status": status,
        "structural_status": structural["status"],
        "semantic_gaps": semantic_gaps,
        "currentness_gaps": currentness_gaps,
        "question_proposals": proposals,
        "question_frontier": frontier,
        "revalidate": lifecycle_target["revalidate"],
        "pending": lifecycle_target["pending"],
        "satisfied_capabilities": sorted(satisfied),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Evaluate strict semantic/currentness target closure"
    )
    parser.add_argument("graph")
    parser.add_argument("target")
    parser.add_argument("model")
    parser.add_argument("semantic_evaluations")
    parser.add_argument("lifecycle")
    parser.add_argument(
        "--skill-registry",
        default="skills/artifact-skill-registry-v0.yaml",
    )
    parser.add_argument(
        "--knowledge-contracts",
        default="spec/semantic-acceptance/knowledge-kind-contracts-v1.yaml",
    )
    parser.add_argument(
        "--knowledge-contract-overlay",
        action="append",
        default=[],
    )
    parser.add_argument(
        "--decision-contracts",
        default="spec/decision-governance/knowledge-kind-decision-contracts-v1.yaml",
    )
    parser.add_argument("--decision-policy")
    args = parser.parse_args()
    result = evaluate_semantic_closure(
        graph=load_yaml(args.graph),
        model=load_yaml(args.model),
        target=args.target,
        skill_registry=load_yaml(args.skill_registry),
        semantic_evaluations=load_yaml(args.semantic_evaluations),
        lifecycle=load_yaml(args.lifecycle),
        knowledge_contracts=load_yaml(args.knowledge_contracts),
        knowledge_contract_overlays=[
            load_yaml(path) for path in args.knowledge_contract_overlay
        ],
        decision_contracts=load_yaml(args.decision_contracts),
        decision_policy=(
            load_yaml(args.decision_policy)
            if args.decision_policy
            else None
        ),
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "COMPLETE" else 1


if __name__ == "__main__":
    raise SystemExit(main())
