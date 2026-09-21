#!/usr/bin/env python3
"""Canonical Engineering Coverage evaluator.

Public interface:
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

Reusable Harness policy is loaded from spec/engineering-coverage. Callers do not
manually assemble activation -> proof -> routing stages.
"""
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any

import yaml

from concern_activation import derive_activation
from coverage_planner import derive_plan
from coverage_obligations import derive_subject_obligation_rows
from engineering_graph import validate_engineering_graph, validate_realization
from harness import question_frontier
from integration_alignment import validate_project_alignment
from agent_router import validate_skill_registry


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
                        "knowledge_kind": candidate.get("knowledge_kind"),
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

        if action == "REVALIDATE_SEMANTICS":
            others.append(
                {
                    "action": action,
                    "concern": concern,
                    "capabilities": sorted(row.get("capabilities", []) or []),
                    "causes": row.get("causes", {}),
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


def _route_production_work(
    work_items: list[dict[str, Any]],
    registry: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    if registry is None:
        return work_items
    validate_skill_registry(registry)
    routes = {
        item["knowledge_kind"]: item["skill"]
        for item in registry.get("routes", []) or []
    }
    result = []
    for item in work_items:
        current = dict(item)
        if current.get("action") == "PRODUCE_CAPABILITY":
            knowledge_kind = current.get("knowledge_kind")
            if knowledge_kind is None:
                current["execution_route"] = {
                    "status": "UNROUTED",
                    "reason": "NO_KNOWLEDGE_KIND",
                }
            elif knowledge_kind not in routes:
                current["execution_route"] = {
                    "status": "UNROUTED",
                    "reason": "NO_REGISTERED_SKILL",
                    "knowledge_kind": knowledge_kind,
                }
            else:
                current["execution_route"] = {
                    "status": "ROUTED",
                    "knowledge_kind": knowledge_kind,
                    "skill": routes[knowledge_kind],
                }
        result.append(current)
    return result


def _resolve_realization(
    graph: dict[str, Any],
    realization: dict[str, Any],
    *,
    consumer: str,
    canonical_source: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if realization.get("kind") == "harness-canonical-graph-projection":
        if canonical_source is None:
            raise ValueError(
                "canonical_source is required when realization is a canonical graph projection"
            )
        aligned = validate_project_alignment(
            canonical_source,
            realization,
            graph,
            target_consumer=consumer,
        )
        return aligned["model"]
    return realization


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
    artifact_skill_registry: dict[str, Any] | None = None,
    canonical_source: dict[str, Any] | None = None,
    semantic_evaluations: dict[str, Any] | None = None,
    subject_obligations: dict[str, Any] | None = None,
    scope_source: dict[str, Any] | None = None,
) -> dict[str, Any]:
    graph = _apply_production_contract_overlay(graph, production_contract_overlay)
    validate_engineering_graph(graph)
    realization = _resolve_realization(
        graph,
        realization,
        consumer=consumer,
        canonical_source=canonical_source,
    )
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
    if semantic_evaluations is not None:
        project_docs.append(semantic_evaluations)

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

    subject_evaluation = None
    if subject_obligations is not None:
        if scope_source is None:
            raise ValueError("scope_source is required with subject_obligations")
        subject_evaluation = derive_subject_obligation_rows(
            obligations=subject_obligations,
            source=scope_source,
            graph=graph,
            project_docs=project_docs,
            proof_contract=proof_contract,
            capability_bindings=claim_bindings,
            consumer=consumer,
            scope=scope,
            scope_roots=activation.get("scope_roots", []),
            extension_capabilities=set(
                planner_overlay.get("coverage_extension_capabilities", []) or []
            ),
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
    subject_rows = (
        list(subject_evaluation.get("rows", []))
        if subject_evaluation is not None
        else []
    )
    subject_remaining = (
        list(subject_evaluation.get("remaining_work", []))
        if subject_evaluation is not None
        else []
    )
    remaining_work = remaining_work + subject_remaining
    work_items = _route_production_work(
        _derive_work_items(remaining_work),
        artifact_skill_registry,
    )
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
        "status": "canonical",
        "project": overlay["project"],
        "consumer": consumer,
        "scope": scope,
        "scope_roots": activation.get("scope_roots", []),
        "completion_ready": not remaining_work,
        "activated_count": activation["activated_count"],
        "remaining_work_count": len(remaining_work),
        "work_item_count": len(work_items),
        "routed_production_count": sum(
            1
            for item in work_items
            if item.get("execution_route", {}).get("status") == "ROUTED"
        ),
        "question_frontier_count": len(questions),
        "summary": plan["summary"],
        "authority_roles": roles,
        "activation_signals": activation["signals"],
        "rows": rows,
        "subject_obligation_rows": subject_rows,
        "subject_obligation_evaluation": subject_evaluation,
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
    artifact_skill_registry: dict[str, Any] | None = None,
    canonical_source: dict[str, Any] | None = None,
    semantic_evaluations: dict[str, Any] | None = None,
    subject_obligations: dict[str, Any] | None = None,
    scope_source: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if artifact_skill_registry is None:
        artifact_skill_registry = load(
            ROOT / "skills/artifact-skill-registry-v0.yaml"
        )
    return evaluate_coverage(
        graph=graph,
        realization=realization,
        consumer=consumer,
        scope=scope,
        scope_roots=scope_roots,
        activation_policy=load(ROOT / "spec/engineering-coverage/activation-policy-v1.yaml"),
        proof_contract=load(ROOT / "spec/engineering-coverage/semantic-proof-contract-v1.yaml"),
        authority_role_contract=load(ROOT / "spec/engineering-coverage/authority-role-contract-v1.yaml"),
        standard_authority_roles=load(ROOT / "spec/engineering-coverage/standard-authority-role-bindings-v1.yaml"),
        authority_aliases=authority_aliases,
        project_overlay=project_overlay,
        semantic_claim_bindings=semantic_claim_bindings,
        production_contract_overlay=production_contract_overlay,
        artifact_skill_registry=artifact_skill_registry,
        canonical_source=canonical_source,
        semantic_evaluations=semantic_evaluations,
        subject_obligations=subject_obligations,
        scope_source=scope_source,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Engineering Coverage evaluator")
    parser.add_argument("graph")
    parser.add_argument("realization")
    parser.add_argument("consumer")
    parser.add_argument("--scope", default="default")
    parser.add_argument("--scope-root", action="append", default=[])
    parser.add_argument("--authority-aliases")
    parser.add_argument("--overlay")
    parser.add_argument("--semantic-claim-bindings")
    parser.add_argument("--canonical-source")
    parser.add_argument("--production-contract-overlay")
    parser.add_argument("--subject-obligations")
    parser.add_argument("--scope-source")
    parser.add_argument(
        "--semantic-evaluations",
        help="Generated semantic acceptance evidence document; may contain one evaluation or semantic_evaluations list.",
    )
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
        canonical_source=(
            load(args.canonical_source)
            if args.canonical_source
            else None
        ),
        semantic_evaluations=(
            load(args.semantic_evaluations)
            if args.semantic_evaluations
            else None
        ),
        subject_obligations=(
            load(args.subject_obligations)
            if args.subject_obligations
            else None
        ),
        scope_source=(load(args.scope_source) if args.scope_source else None),
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
