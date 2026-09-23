#!/usr/bin/env python3
"""Strict semantic/currentness closure above structural target state."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml

from agent_router import validate_skill_registry
from capability_lifecycle import evaluate_lifecycle_target, lifecycle_index, lifecycle_states
from engineering_graph import derive_profile, evaluate_engineering_target, production_index, validate_realization
from harness import CoreError
from semantic_acceptance import evaluation_index


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
) -> dict[str, Any]:
    validate_skill_registry(skill_registry)
    realized = validate_realization(graph, model)
    structural = evaluate_engineering_target(graph, target, realized)
    profile = derive_profile(graph, target)
    productions = production_index(graph)
    evaluations = evaluation_index([semantic_evaluations])
    lifecycle_by_capability = lifecycle_index(lifecycle)
    states = lifecycle_states(graph, realized, lifecycle)

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

    for expectation in profile["expectations"]:
        capability = expectation["capability"]
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

        satisfied.append(capability)

    lifecycle_target = evaluate_lifecycle_target(
        graph, target, realized, lifecycle
    )
    complete = (
        structural["status"] == "COMPLETE"
        and not semantic_gaps
        and not currentness_gaps
        and len(satisfied) == len(profile["expectations"])
    )

    return {
        "version": 1,
        "kind": "harness-semantic-closure-evaluation",
        "target": target,
        "status": "COMPLETE" if complete else "INCOMPLETE",
        "structural_status": structural["status"],
        "semantic_gaps": semantic_gaps,
        "currentness_gaps": currentness_gaps,
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
    args = parser.parse_args()
    result = evaluate_semantic_closure(
        graph=load_yaml(args.graph),
        model=load_yaml(args.model),
        target=args.target,
        skill_registry=load_yaml(args.skill_registry),
        semantic_evaluations=load_yaml(args.semantic_evaluations),
        lifecycle=load_yaml(args.lifecycle),
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "COMPLETE" else 1


if __name__ == "__main__":
    raise SystemExit(main())
