#!/usr/bin/env python3
"""Evaluate repository-wide artifact-skill invariant coverage."""
from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from .agent_router import validate_skill_registry
from .semantic_admission import knowledge_contract_index

__all__ = ['Any',
 'Path',
 'annotations',
 'evaluate_skill_invariant_policy',
 'knowledge_contract_index',
 'validate_skill_registry',
 'yaml']


def _load(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a mapping")
    return value


def evaluate_skill_invariant_policy(root: str | Path) -> dict[str, Any]:
    root = Path(root)
    registry = _load(root / "skills/artifact-skill-registry-v0.yaml")
    contracts_doc = _load(
        root / "spec/semantic-acceptance/knowledge-kind-contracts-v1.yaml"
    )
    policy = _load(
        root / "spec/semantic-acceptance/skill-invariant-policy-v1.yaml"
    )

    findings: list[dict[str, Any]] = []
    try:
        validate_skill_registry(registry, root=root)
    except Exception as exc:
        findings.append(
            {
                "code": "SKILL_REGISTRY_INVALID",
                "detail": str(exc),
            }
        )

    contracts = knowledge_contract_index(contracts_doc)
    active = {
        path.relative_to(root).as_posix()
        for path in (root / "skills/artifacts").glob("*/SKILL.md")
    }
    routes = {
        item["knowledge_kind"]: item["skill"]
        for item in registry.get("routes", []) or []
    }
    enforced = {
        item["knowledge_kind"]: item["skill"]
        for item in policy.get("enforced", []) or []
    }
    judgement = {
        item["skill"]: item.get("rationale")
        for item in policy.get("judgement_only", []) or []
    }

    if policy.get("version") != 1 or policy.get("kind") != "harness-skill-invariant-policy":
        findings.append({"code": "SKILL_INVARIANT_POLICY_INVALID"})
    if routes != enforced:
        findings.append(
            {
                "code": "SKILL_ROUTE_ENFORCEMENT_MISMATCH",
                "routed": sorted(routes),
                "enforced": sorted(enforced),
            }
        )
    if set(routes) != set(contracts):
        findings.append(
            {
                "code": "SKILL_SEMANTIC_CONTRACT_MISMATCH",
                "routes_without_contracts": sorted(set(routes) - set(contracts)),
                "contracts_without_routes": sorted(set(contracts) - set(routes)),
            }
        )

    overlap = sorted(set(enforced.values()) & set(judgement))
    if overlap:
        findings.append(
            {
                "code": "SKILL_POLICY_OVERLAP",
                "skills": overlap,
            }
        )

    classified = set(enforced.values()) | set(judgement)
    missing = sorted(active - classified)
    stale = sorted(classified - active)
    if missing:
        findings.append(
            {
                "code": "ACTIVE_SKILL_UNCLASSIFIED",
                "skills": missing,
            }
        )
    if stale:
        findings.append(
            {
                "code": "SKILL_POLICY_REFERENCES_MISSING_SKILL",
                "skills": stale,
            }
        )

    missing_rationale = sorted(
        skill
        for skill, rationale in judgement.items()
        if not isinstance(rationale, str) or not rationale.strip()
    )
    if missing_rationale:
        findings.append(
            {
                "code": "JUDGEMENT_ONLY_RATIONALE_MISSING",
                "skills": missing_rationale,
            }
        )

    product_checks = set(
        contracts.get("product-requirements", {}).get(
            "required_review_checks", []
        )
        or []
    )
    required_product_checks = {
        "observable-product-level",
        "no-downstream-design-promotion",
    }
    missing_product_checks = sorted(required_product_checks - product_checks)
    if missing_product_checks:
        findings.append(
            {
                "code": "PRODUCT_REQUIREMENT_REVIEW_INVARIANT_MISSING",
                "checks": missing_product_checks,
            }
        )

    return {
        "version": 1,
        "kind": "harness-skill-invariant-policy-evaluation",
        "status": "ACCEPTED" if not findings else "REJECTED",
        "active_skill_count": len(active),
        "enforced_count": len(enforced),
        "judgement_only_count": len(judgement),
        "semantic_contract_count": len(contracts),
        "findings": findings,
    }
