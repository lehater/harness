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
import copy
import json
from pathlib import Path
from typing import Any

import yaml

from concern_activation_experiment import derive_activation
from coverage_planner_experiment import derive_plan
from engineering_graph import validate_engineering_graph, validate_realization
from harness import question_frontier


ROOT = Path(__file__).resolve().parent


def load(path: str | Path) -> dict[str, Any]:
    value = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a mapping")
    return value


def _apply_production_contract_overlay(
    graph: dict[str, Any],
    overlay: dict[str, Any] | None,
) -> dict[str, Any]:
    if not overlay:
        return graph

    result = copy.deepcopy(graph)
    authorities = {
        item.get("id"): item
        for item in result.get("authorities", []) or []
        if isinstance(item, dict) and item.get("id")
    }
    existing = {
        production.get("capability")
        for authority in authorities.values()
        for production in authority.get("produces", []) or []
        if isinstance(production, dict) and production.get("capability")
    }

    for item in overlay.get("productions", []) or []:
        if not isinstance(item, dict):
            raise ValueError("production contract overlay item must be a mapping")
        authority_id = item.get("authority")
        capability = item.get("capability")
        semantic_claims = item.get("semantic_claims", []) or []
        knowledge_kind = item.get("knowledge_kind")
        requires = item.get("requires", []) or []

        if authority_id not in authorities:
            raise ValueError(
                f"production contract overlay references unknown Authority: {authority_id}"
            )
        if not isinstance(capability, str) or not capability:
            raise ValueError("production contract overlay capability is required")
        if capability in existing:
            raise ValueError(
                f"production contract overlay duplicates CapabilityId: {capability}"
            )
        if not semantic_claims:
            raise ValueError(
                f"production contract overlay {capability} must declare semantic_claims"
            )

        production = {
            "capability": capability,
            "semantic_claims": semantic_claims,
            "requires": [
                value if isinstance(value, dict) else {"capability": value}
                for value in requires
            ],
        }
        if knowledge_kind is not None:
            if not isinstance(knowledge_kind, str) or not knowledge_kind:
                raise ValueError(
                    f"production contract overlay {capability} knowledge_kind must be non-empty"
                )
            production["knowledge_kind"] = knowledge_kind
        authorities[authority_id].setdefault("produces", []).append(production)
        existing.add(capability)

    return result


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


def _derive_work_items(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_capability: dict[str, dict[str, Any]] = {}
    others: list[dict[str, Any]] = []

    for row in rows:
        action = row.get("action")
        concern = row.get("concern")

        if action == "PRODUCE_CAPABILITY":
            for candidate in row.get("ready_production_candidates", []) or []:
                capability = candidate["capability"]
                item = by_capability.setdefault(
                    capability,
                    {
                        "action": "PRODUCE_CAPABILITY",
                        "capability": capability,
                        "authority": candidate.get("authority"),
                        "concerns": [],
                        "semantic_claims": [],
                    },
                )
                if concern not in item["concerns"]:
                    item["concerns"].append(concern)
                claim_entry = {"claim": candidate["claim"]}
                if candidate.get("subject") is not None:
                    claim_entry["subject"] = candidate["subject"]
                if claim_entry not in item["semantic_claims"]:
                    item["semantic_claims"].append(claim_entry)
            continue

        if action == "WAIT_FOR_PREREQUISITES":
            blocked = []
            for candidate in row.get("production_candidates", []) or []:
                blocked.append(
                    {
                        "capability": candidate["capability"],
                        "authority": candidate.get("authority"),
                        "missing_prerequisites": candidate.get(
                            "missing_prerequisites", []
                        ),
                    }
                )
            others.append(
                {
                    "action": action,
                    "concern": concern,
                    "blocked_productions": blocked,
                }
            )
            continue

        if action == "MODEL_PRODUCTION_CONTRACT":
            candidate_authorities = sorted(
                {
                    authority
                    for values in (row.get("routes", {}) or {}).values()
                    for authority in values
                }
            )
            others.append(
                {
                    "action": action,
                    "concern": concern,
                    "candidate_authorities": candidate_authorities,
                    "accepted_semantic_claims": row.get(
                        "accepted_semantic_claims", []
                    ),
                }
            )
            continue

        if action == "RESOLVE_QUESTIONS":
            others.append(
                {
                    "action": action,
                    "concern": concern,
                    "questions": sorted(row.get("questions", []) or []),
                }
            )
            continue

        if action in {"ASSIGN_AUTHORITY", "MODEL_PROOF_CONTRACT"}:
            others.append(
                {
                    "action": action,
                    "concern": concern,
                    **(
                        {
                            "accepted_semantic_claims": row.get(
                                "accepted_semantic_claims", []
                            )
                        }
                        if row.get("accepted_semantic_claims") is not None
                        else {}
                    ),
                }
            )

    capability_items = sorted(
        by_capability.values(),
        key=lambda item: (item.get("authority") or "", item["capability"]),
    )
    for item in capability_items:
        item["concerns"].sort()
        item["semantic_claims"] = sorted(
            item["semantic_claims"],
            key=lambda value: (value["claim"], value.get("subject", "")),
        )
    return capability_items + others


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
    production_contract_overlay: dict[str, Any] | None = None,
) -> dict[str, Any]:
    graph = _apply_production_contract_overlay(graph, production_contract_overlay)
    validate_engineering_graph(graph)
    realized = validate_realization(graph, realization)

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
    project_docs = [graph, realized]

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
        "coverage_extension_capabilities": [
            item["capability"]
            for item in (production_contract_overlay or {}).get("productions", []) or []
            if isinstance(item, dict) and item.get("capability")
        ],
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
    work_items = _derive_work_items(remaining_work)
    question_ids = sorted(
        {
            question
            for row in remaining_work
            for question in row.get("questions", []) or []
        }
    )
    questions = question_frontier(realized, question_ids)

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
        "work_item_count": len(work_items),
        "question_frontier_count": len(questions),
        "summary": plan["summary"],
        "authority_roles": roles,
        "activation_signals": activation["signals"],
        "rows": rows,
        "remaining_work": remaining_work,
        "work_items": work_items,
        "question_frontier": questions,
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
    production_contract_overlay: dict[str, Any] | None = None,
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
        production_contract_overlay=production_contract_overlay,
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
    parser.add_argument("--production-contract-overlay")
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
        production_contract_overlay=(
            load(args.production_contract_overlay)
            if args.production_contract_overlay
            else None
        ),
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
