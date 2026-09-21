#!/usr/bin/env python3
"""Unified research Engineering Coverage evaluator.

Public research interface:
    evaluate_coverage(
        graph,
        realization,
        consumer,
        scope,
        scope_roots,
        project_overlay,
        authority_aliases,
        semantic_claim_bindings,
    )

Reusable Harness policy is loaded by the CLI from spec/research. Callers do not
manually assemble activation -> proof -> routing stages.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml

from concern_activation_experiment import derive_activation
from coverage_planner_experiment import derive_plan


ROOT = Path(__file__).resolve().parent


def load(path: str | Path) -> dict[str, Any]:
    value = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a mapping")
    return value


def _merge_authority_roles(
    standard: dict[str, Any],
    aliases: dict[str, Any],
    graph: dict[str, Any],
) -> dict[str, Any]:
    standard_bindings = standard.get("bindings", {}) or {}
    alias_bindings = aliases.get("bindings", {}) or {}
    authorities = {
        item["id"]
        for item in graph.get("authorities", []) or []
        if isinstance(item, dict) and item.get("id")
    }

    bindings: dict[str, list[str]] = {}
    provenance: dict[str, list[str]] = {}
    for authority in sorted(authorities):
        roles: set[str] = set()
        if authority in standard_bindings:
            roles.update(standard_bindings[authority] or [])
            provenance.setdefault(authority, []).append("STANDARD_ID")
        if authority in alias_bindings:
            roles.update(alias_bindings[authority] or [])
            provenance.setdefault(authority, []).append("PROJECT_ALIAS")
        if roles:
            bindings[authority] = sorted(roles)

    return {
        "version": 1,
        "kind": "harness-derived-authority-role-bindings",
        "project": aliases.get("project", graph.get("id")),
        "bindings": bindings,
        "provenance": provenance,
        "unresolved_authorities": sorted(authorities - set(bindings)),
    }


def _scope_overlay(
    project_overlay: dict[str, Any],
    *,
    project: str,
    consumer: str,
    scope: str,
    scope_roots: list[str],
) -> dict[str, Any]:
    result = dict(project_overlay)
    result["project"] = project
    result["consumer"] = consumer
    result["scope"] = scope
    result["scope_roots"] = list(scope_roots)
    result.setdefault("activate", [])
    result.setdefault("decisions", [])
    return result


def evaluate_coverage(
    *,
    graph: dict[str, Any],
    realization: dict[str, Any],
    consumer: str,
    scope: str,
    scope_roots: list[str] | None,
    activation_policy: dict[str, Any],
    proof_contract: dict[str, Any],
    authority_role_contract: dict[str, Any],
    standard_authority_roles: dict[str, Any],
    authority_aliases: dict[str, Any] | None = None,
    project_overlay: dict[str, Any] | None = None,
    semantic_claim_bindings: dict[str, Any] | None = None,
) -> dict[str, Any]:
    aliases = authority_aliases or {"bindings": {}}
    overlay = _scope_overlay(
        project_overlay or {},
        project=graph.get("id", "PROJECT"),
        consumer=consumer,
        scope=scope,
        scope_roots=list(scope_roots or []),
    )
    claim_bindings = semantic_claim_bindings or {
        "version": 1,
        "kind": "harness-semantic-claim-bindings",
        "bindings": [],
    }

    roles = _merge_authority_roles(standard_authority_roles, aliases, graph)
    project_docs = [graph, realization]

    activation = derive_activation(
        activation_policy,
        roles,
        overlay,
        project_docs,
        consumer,
    )

    applicable_decisions = []
    for item in overlay.get("decisions", []) or []:
        consumers = item.get("consumers", []) or []
        scopes = item.get("scopes", []) or []
        if consumers and consumer not in consumers:
            continue
        if scopes and scope not in scopes:
            continue
        applicable_decisions.append(item)

    planner_overlay = {
        "project": overlay["project"],
        "scope": scope,
        "scope_roots": activation.get("scope_roots", []),
        "required": [row["concern"] for row in activation["rows"]],
        "decisions": applicable_decisions,
    }

    plan = derive_plan(
        proof_contract,
        authority_role_contract,
        roles,
        claim_bindings,
        planner_overlay,
        project_docs,
        consumer,
    )

    activation_by_concern = {
        row["concern"]: row.get("provenance", [])
        for row in activation["rows"]
    }
    rows = []
    for row in plan["rows"]:
        item = dict(row)
        item["activation_provenance"] = activation_by_concern.get(
            row["concern"], []
        )
        rows.append(item)

    remaining_work = [
        row for row in rows
        if row["state"] not in {"COVERED", "NOT_APPLICABLE", "DEFERRED"}
    ]

    return {
        "version": 1,
        "kind": "harness-engineering-coverage-evaluation",
        "status": "research",
        "project": overlay["project"],
        "consumer": consumer,
        "scope": scope,
        "scope_roots": activation.get("scope_roots", []),
        "completion_ready": not remaining_work,
        "activated_count": activation["activated_count"],
        "remaining_work_count": len(remaining_work),
        "summary": plan["summary"],
        "authority_roles": roles,
        "activation_signals": activation["signals"],
        "rows": rows,
        "remaining_work": remaining_work,
    }


def evaluate_with_repository_policy(
    *,
    graph: dict[str, Any],
    realization: dict[str, Any],
    consumer: str,
    scope: str,
    scope_roots: list[str] | None = None,
    authority_aliases: dict[str, Any] | None = None,
    project_overlay: dict[str, Any] | None = None,
    semantic_claim_bindings: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return evaluate_coverage(
        graph=graph,
        realization=realization,
        consumer=consumer,
        scope=scope,
        scope_roots=scope_roots,
        activation_policy=load(ROOT / "spec/research/concern-activation-policy-v1.yaml"),
        proof_contract=load(ROOT / "spec/research/concern-semantic-proof-contract-v1.yaml"),
        authority_role_contract=load(ROOT / "spec/research/authority-role-contract-v1.yaml"),
        standard_authority_roles=load(ROOT / "spec/research/standard-authority-role-bindings-v1.yaml"),
        authority_aliases=authority_aliases,
        project_overlay=project_overlay,
        semantic_claim_bindings=semantic_claim_bindings,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Research Engineering Coverage evaluator")
    parser.add_argument("graph")
    parser.add_argument("realization")
    parser.add_argument("consumer")
    parser.add_argument("--scope", default="default")
    parser.add_argument("--scope-root", action="append", default=[])
    parser.add_argument("--authority-aliases")
    parser.add_argument("--overlay")
    parser.add_argument("--semantic-claim-bindings")
    args = parser.parse_args()

    result = evaluate_with_repository_policy(
        graph=load(args.graph),
        realization=load(args.realization),
        consumer=args.consumer,
        scope=args.scope,
        scope_roots=args.scope_root,
        authority_aliases=load(args.authority_aliases) if args.authority_aliases else None,
        project_overlay=load(args.overlay) if args.overlay else None,
        semantic_claim_bindings=(
            load(args.semantic_claim_bindings)
            if args.semantic_claim_bindings
            else None
        ),
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
