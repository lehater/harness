#!/usr/bin/env python3
"""Derive a candidate-free execution request for Decision Exploration."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml

from authority_context import build_authority_context
from capability_lifecycle import lifecycle_index, lifecycle_states
from decision_explorer_contract import build_decision_explorer_request
from decision_governance import axis_policies, decision_contract_index
from engineering_graph import producer_index, production_index, validate_realization
from harness import CoreError


def derive_decision_explorer_request(
    *,
    graph: dict[str, Any],
    model: dict[str, Any],
    decision_contracts: dict[str, Any],
    decision_policy: dict[str, Any] | None,
    capability: str,
    lifecycle: dict[str, Any] | None = None,
    mode: str = "CREATE",
) -> dict[str, Any] | None:
    realized = validate_realization(graph, model)
    productions = production_index(graph)
    producers = producer_index(graph)
    production = productions.get(capability)
    if production is None:
        raise CoreError(f"unknown produced capability: {capability}")
    knowledge_kind = production.get("knowledge_kind")
    if not isinstance(knowledge_kind, str) or not knowledge_kind:
        raise CoreError(f"capability {capability} requires knowledge_kind")
    authority = producers[capability]
    contract = decision_contract_index(decision_contracts).get(knowledge_kind)
    policies = axis_policies(contract, decision_policy)
    if contract is None or policies is None:
        return None

    context = build_authority_context(
        graph,
        realized,
        authority,
        [capability],
    )
    if context["status"] not in {"ROOT", "READY"}:
        raise CoreError(
            f"Authority {authority} cannot explore {capability}: "
            f"context status {context['status']}"
        )

    prerequisites = [
        item["capability"] for item in production.get("requires", []) or []
    ]
    baseline: dict[str, str] = {}
    current_provider_baseline: dict[str, Any] | None = None
    if prerequisites:
        if lifecycle is None:
            raise CoreError(
                f"capability {capability} has prerequisites and requires "
                "lifecycle evidence for explorer request generation"
            )
        states = lifecycle_states(graph, realized, lifecycle)
        index = lifecycle_index(lifecycle)
        for prerequisite in prerequisites:
            if states[prerequisite]["state"] != "CURRENT":
                raise CoreError(
                    f"explorer prerequisite {prerequisite} is "
                    f"{states[prerequisite]['state']}, not CURRENT"
                )
            baseline[prerequisite] = index[prerequisite]["acceptance_id"]

    if mode in {"REVISION", "REDO"}:
        if lifecycle is None:
            raise CoreError(
                f"{mode} decision option request requires lifecycle evidence"
            )
        index = lifecycle_index(lifecycle)
        provider = index.get(capability)
        if provider is None:
            raise CoreError(
                f"{mode} decision option request requires accepted current provider"
            )
        artifact_id = provider["artifact"]
        matches = [
            item
            for item in realized.get("artifacts", []) or []
            if item.get("id") == artifact_id
        ]
        if len(matches) != 1:
            raise CoreError(
                f"{mode} decision option request cannot resolve current provider {artifact_id}"
            )
        current_provider_baseline = matches[0]

    return build_decision_explorer_request(
        capability=capability,
        knowledge_kind=knowledge_kind,
        authority=authority,
        authority_context=context,
        contract=contract,
        axis_policies=policies,
        prerequisite_baseline=baseline,
        model=realized,
        mode=mode,
        current_provider_baseline=current_provider_baseline,
    )


def _load(path: str | Path) -> dict[str, Any]:
    value = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise CoreError(f"{path} must contain a mapping")
    return value


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate candidate-free Decision Explorer request"
    )
    parser.add_argument("graph")
    parser.add_argument("model")
    parser.add_argument("capability")
    parser.add_argument("decision_policy")
    parser.add_argument("--lifecycle")
    parser.add_argument(
        "--decision-contracts",
        default="spec/decision-governance/knowledge-kind-decision-contracts-v1.yaml",
    )
    args = parser.parse_args()
    request = derive_decision_explorer_request(
        graph=_load(args.graph),
        model=_load(args.model),
        decision_contracts=_load(args.decision_contracts),
        decision_policy=_load(args.decision_policy),
        capability=args.capability,
        lifecycle=_load(args.lifecycle) if args.lifecycle else None,
    )
    if request is None:
        print(json.dumps({"status": "NOT_REQUIRED"}, indent=2))
        return 0
    print(json.dumps(request, indent=2, sort_keys=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
