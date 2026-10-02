#!/usr/bin/env python3
"""Application orchestration around the pure Engineering Coverage evaluator."""
from __future__ import annotations
import argparse
import copy
import json
from pathlib import Path
from typing import Any

from agent_router import validate_skill_registry
from harness.coverage.engineering_coverage import evaluate_with_repository_policy, load, load_scope_source
from harness.integration.integration_alignment import validate_project_alignment
from skill_router import GLOBAL_INSTRUCTION_CONTRACTS

ROOT = Path(__file__).resolve().parent


def _resolve_realization(graph: dict[str, Any], realization: dict[str, Any], *, consumer: str, canonical_source: dict[str, Any] | None) -> dict[str, Any]:
    if realization.get("kind") != "harness-canonical-graph-projection":
        return realization
    if canonical_source is None:
        raise ValueError("canonical_source is required when realization is a canonical graph projection")
    return validate_project_alignment(
        canonical_source, realization, graph, target_consumer=consumer
    )["model"]


def _route_production_work(work_items: list[dict[str, Any]], registry: dict[str, Any]) -> list[dict[str, Any]]:
    validate_skill_registry(registry)
    routes = {item["knowledge_kind"]: item["skill"] for item in registry.get("routes", []) or []}
    result = []
    for item in work_items:
        current = copy.deepcopy(item)
        if current.get("action") == "PRODUCE_CAPABILITY":
            knowledge_kind = current.get("knowledge_kind")
            if knowledge_kind is None:
                current["execution_route"] = {"status": "UNROUTED", "reason": "NO_KNOWLEDGE_KIND"}
            elif knowledge_kind not in routes:
                current["execution_route"] = {"status": "UNROUTED", "reason": "NO_REGISTERED_SKILL", "knowledge_kind": knowledge_kind}
            else:
                current["execution_route"] = {
                    "status": "ROUTED",
                    "knowledge_kind": knowledge_kind,
                    "skill": routes[knowledge_kind],
                    "instruction_contracts": list(GLOBAL_INSTRUCTION_CONTRACTS),
                }
        result.append(current)
    return result


def evaluate_project_coverage(
    *,
    graph: dict[str, Any],
    realization: dict[str, Any],
    consumer: str,
    scope: str,
    scope_roots: list[str] | None = None,
    authority_aliases: dict[str, Any] | None = None,
    project_overlay: dict[str, Any] | None = None,
    semantic_claim_bindings: dict[str, Any] | None = None,
    production_contract_overlay: dict[str, Any] | None = None,
    artifact_skill_registry: dict[str, Any] | None = None,
    canonical_source: dict[str, Any] | None = None,
    semantic_evaluations: dict[str, Any] | None = None,
    subject_obligations: dict[str, Any] | None = None,
    scope_source: dict[str, Any] | None = None,
) -> dict[str, Any]:
    resolved = _resolve_realization(graph, realization, consumer=consumer, canonical_source=canonical_source)
    coverage = evaluate_with_repository_policy(
        graph=graph, realization=resolved, consumer=consumer, scope=scope,
        scope_roots=scope_roots, authority_aliases=authority_aliases,
        project_overlay=project_overlay, semantic_claim_bindings=semantic_claim_bindings,
        production_contract_overlay=production_contract_overlay,
        semantic_evaluations=semantic_evaluations, subject_obligations=subject_obligations,
        scope_source=scope_source,
    )
    registry = artifact_skill_registry or load(ROOT / "skills/artifact-skill-registry-v0.yaml")
    result = copy.deepcopy(coverage)
    result["work_items"] = _route_production_work(list(coverage.get("work_items", []) or []), registry)
    result["work_item_count"] = len(result["work_items"])
    result["routed_production_count"] = sum(
        1 for item in result["work_items"]
        if item.get("execution_route", {}).get("status") == "ROUTED"
    )
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Application-level Engineering Coverage evaluation")
    parser.add_argument("graph"); parser.add_argument("realization"); parser.add_argument("consumer")
    parser.add_argument("--scope", default="default"); parser.add_argument("--scope-root", action="append", default=[])
    parser.add_argument("--authority-aliases"); parser.add_argument("--overlay"); parser.add_argument("--semantic-claim-bindings")
    parser.add_argument("--canonical-source"); parser.add_argument("--production-contract-overlay")
    parser.add_argument("--subject-obligations"); parser.add_argument("--scope-source"); parser.add_argument("--semantic-evaluations")
    args = parser.parse_args()
    result = evaluate_project_coverage(
        graph=load(args.graph), realization=load(args.realization), consumer=args.consumer,
        scope=args.scope, scope_roots=args.scope_root,
        authority_aliases=load(args.authority_aliases) if args.authority_aliases else None,
        project_overlay=load(args.overlay) if args.overlay else None,
        semantic_claim_bindings=load(args.semantic_claim_bindings) if args.semantic_claim_bindings else None,
        canonical_source=load(args.canonical_source) if args.canonical_source else None,
        production_contract_overlay=load(args.production_contract_overlay) if args.production_contract_overlay else None,
        semantic_evaluations=load(args.semantic_evaluations) if args.semantic_evaluations else None,
        subject_obligations=load(args.subject_obligations) if args.subject_obligations else None,
        scope_source=load_scope_source(args.scope_source) if args.scope_source else None,
    )
    print(json.dumps(result, indent=2, sort_keys=True)); return 0


if __name__ == "__main__":
    raise SystemExit(main())
