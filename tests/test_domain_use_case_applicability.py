#!/usr/bin/env python3
"""Regression: optional strategic domain knowledge must not gate a domain use case."""
from __future__ import annotations

import copy
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from harness.application.agent_router import route_create_work
from harness.project_model.engineering_graph import derive_profile, validate_engineering_graph


def boundary(label: str) -> dict[str, str]:
    return {
        "semantic_cohesion": label,
        "independent_change": label,
        "public_contract": label,
    }


def checker_like_graph(*, strategic_input: bool = False) -> dict:
    authorities = [
        {
            "id": "PRODUCT-REQUIREMENTS",
            "responsibility": "Own observable requirements.",
            "boundary": boundary("Product"),
            "produces": [
                {"capability": "checker.requirements", "knowledge_kind": "product-requirements", "requires": []}
            ],
        },
    ]
    if strategic_input:
        authorities.append({
            "id": "DOMAIN-STRATEGY",
            "responsibility": "Own material accepted strategic classification.",
            "boundary": boundary("Strategy"),
            "produces": [
                {
                    "capability": "checker.strategy",
                    "knowledge_kind": "domain-strategy",
                    "requires": ["checker.requirements"],
                },
            ],
        })
    authorities.append({
        "id": "DOMAIN-USE-CASE-DESIGN",
        "responsibility": "Own independently verified domain behavior.",
        "boundary": boundary("Domain behavior"),
        "produces": [
            {
                "capability": "checker.domain-use-case",
                "knowledge_kind": "domain-use-case",
                "requires": ["checker.requirements"]
                + (["checker.strategy"] if strategic_input else []),
            },
        ],
    })
    return {
        "version": 1,
        "kind": "harness-engineering-graph",
        "id": "CHECKER-SELECTIVE-CASE",
        "authorities": authorities,
        "consumers": [
            {
                "id": "CHECKER-DOMAIN-ADMISSION",
                "purpose": "Accept scoped domain behavior; not implementation.",
                "requires": ["checker.domain-use-case"],
            },
        ],
    }


def accepted_requirements() -> dict:
    return {
        "artifacts": [{
            "id": "CHECKER-REQUIREMENTS",
            "authority": "PRODUCT-REQUIREMENTS",
            "path": "requirements.yaml",
            "provides": ["checker.requirements"],
            "depends_on": [],
        }],
        "questions": [],
    }


def main() -> int:
    registry = yaml.safe_load(
        (ROOT / "skills/artifact-skill-registry-v0.yaml").read_text(encoding="utf-8")
    )
    skill = (ROOT / "skills/artifacts/domain-use-case/SKILL.md").read_text(encoding="utf-8")

    # The routing rule and human-facing procedure must agree: no hidden stage gate.
    assert "Strategic Domain ownership is **not a universal prerequisite**" in skill
    assert "when its specific decisions materially constrain" in skill
    assert "Never infer `NOT_APPLICABLE` merely from an absent graph node" in skill
    assert "missing domain behavior is blocked by a real Question" in skill

    graph = checker_like_graph()
    validate_engineering_graph(graph)
    profile = derive_profile(graph, "CHECKER-DOMAIN-ADMISSION")
    assert {p["capability"] for p in profile["expectations"]} == {
        "checker.requirements", "checker.domain-use-case",
    }
    result = route_create_work(graph, "CHECKER-DOMAIN-ADMISSION", accepted_requirements(), registry)
    assert result["unrouted"] == [], result
    assert result["wait"] == [] and result["pending"] == [], result
    assert len(result["routed"]) == 1, result
    assert result["routed"][0]["capabilities"] == ["checker.domain-use-case"], result
    assert result["routed"][0]["skill"] == "skills/artifacts/domain-use-case/SKILL.md", result

    # Missing domain truth still blocks actual production; optional strategy is not
    # permission for the verifier to invent a match predicate or an oracle.
    unresolved = accepted_requirements()
    unresolved["questions"] = [{
        "id": "Q-DV-002",
        "authority": "DOMAIN-USE-CASE-DESIGN",
        "text": "Which independently supported match/non-match semantics apply?",
        "blocks_capabilities": ["checker.domain-use-case"],
        "blocks": [],
        "answer_from": [],
    }]
    blocked = route_create_work(graph, "CHECKER-DOMAIN-ADMISSION", unresolved, registry)
    assert not blocked["routed"] and blocked["wait"], blocked

    # When an accepted strategic decision *is* a direct semantic prerequisite,
    # the graph must hold back Domain Use-Case until that decision is available.
    with_strategy = checker_like_graph(strategic_input=True)
    validate_engineering_graph(with_strategy)
    strategy_pending = route_create_work(
        with_strategy, "CHECKER-DOMAIN-ADMISSION", accepted_requirements(), registry
    )
    assert [r["capabilities"] for r in strategy_pending["routed"]] == [["checker.strategy"]], strategy_pending
    assert any(p["capability"] == "checker.domain-use-case" for p in strategy_pending["pending"]), strategy_pending

    print("Domain Use-Case conditional Strategy regression passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
