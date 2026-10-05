#!/usr/bin/env python3
"""Validate semantic CREATE-to-skill routing."""
from __future__ import annotations

import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from harness.application.agent_router import (  # noqa: E402
    route_create_work,
    validate_skill_registry,
)
from harness.project_model.core import CoreError  # noqa: E402


def boundary(label: str) -> dict[str, str]:
    return {
        "semantic_cohesion": label,
        "independent_change": label,
        "public_contract": label,
    }


def graph_for(kind_marker: object = "verification-strategy") -> dict:
    production = {
        "capability": "example.verification",
        "requires": [],
    }
    if kind_marker is not None:
        production["knowledge_kind"] = kind_marker
    return {
        "version": 1,
        "kind": "harness-engineering-graph",
        "id": "ROUTER-PILOT",
        "authorities": [
            {
                "id": "VERIFICATION",
                "responsibility": "Own verification design.",
                "boundary": boundary("Verification"),
                "produces": [production],
            }
        ],
        "consumers": [
            {
                "id": "IMPLEMENTATION",
                "purpose": "Build",
                "requires": ["example.verification"],
            }
        ],
    }


def main() -> int:
    errors: list[str] = []
    registry_path = ROOT / "skills" / "artifact-skill-registry-v0.yaml"
    registry = yaml.safe_load(registry_path.read_text(encoding="utf-8"))

    try:
        validate_skill_registry(registry, root=ROOT)
    except Exception as exc:
        errors.append(f"registry: {exc}")

    empty_model = {"artifacts": [], "questions": []}

    try:
        result = route_create_work(
            graph_for(),
            "IMPLEMENTATION",
            empty_model,
            registry,
        )
        assert result["target_status"] == "READY", result
        assert result["unrouted"] == [], result
        assert len(result["routed"]) == 1, result
        routed = result["routed"][0]
        assert routed["knowledge_kind"] == "verification-strategy", routed
        assert routed["capabilities"] == ["example.verification"], routed
        assert routed["skill"] == "skills/artifacts/verification-strategy/SKILL.md", routed
        assert routed["instruction_contracts"] == [
            "docs/design/agent-instruction-architecture-v0.md",
            "docs/design/process-simplicity-and-efficiency-v0.md",
        ], routed
        assert all(
            (ROOT / path).is_file()
            for path in routed["instruction_contracts"]
        ), routed
    except Exception as exc:
        errors.append(f"registered route: {exc}")

    try:
        result = route_create_work(
            graph_for("not-yet-supported-kind"),
            "IMPLEMENTATION",
            empty_model,
            registry,
        )
        assert result["routed"] == [], result
        assert result["unrouted"][0]["reason"] == "NO_REGISTERED_SKILL", result
    except Exception as exc:
        errors.append(f"unsupported kind: {exc}")

    try:
        result = route_create_work(
            graph_for("source-coverage-audit"),
            "IMPLEMENTATION",
            empty_model,
            registry,
        )
        assert result["unrouted"] == [], result
        assert len(result["routed"]) == 1, result
        routed = result["routed"][0]
        assert routed["knowledge_kind"] == "source-coverage-audit", routed
        assert routed["skill"] == "skills/artifacts/source-coverage-audit/SKILL.md", routed
    except Exception as exc:
        errors.append(f"source coverage route: {exc}")

    try:
        result = route_create_work(
            graph_for(None),
            "IMPLEMENTATION",
            empty_model,
            registry,
        )
        assert result["routed"] == [], result
        assert result["unrouted"][0]["reason"] == "NO_KNOWLEDGE_KIND", result
    except Exception as exc:
        errors.append(f"missing kind: {exc}")


    try:
        grouped_graph = {
            "version": 1,
            "kind": "harness-engineering-graph",
            "id": "GROUPED-ROUTER-PILOT",
            "authorities": [
                {
                    "id": "PRODUCT",
                    "responsibility": "Own product requirements.",
                    "boundary": boundary("Product"),
                    "produces": [
                        {
                            "capability": "example.product-intent",
                            "knowledge_kind": "product-requirements",
                            "requires": [],
                        },
                        {
                            "capability": "example.acceptance",
                            "knowledge_kind": "product-requirements",
                            "requires": [],
                        },
                    ],
                }
            ],
            "consumers": [
                {
                    "id": "IMPLEMENTATION",
                    "purpose": "Build",
                    "requires": [
                        "example.product-intent",
                        "example.acceptance",
                    ],
                }
            ],
        }
        result = route_create_work(
            grouped_graph,
            "IMPLEMENTATION",
            empty_model,
            registry,
        )
        assert result["unrouted"] == [], result
        assert len(result["routed"]) == 1, result
        work = result["routed"][0]
        assert work["knowledge_kind"] == "product-requirements", work
        assert work["skill"] == "skills/artifacts/product-requirements/SKILL.md", work
        assert work["capabilities"] == [
            "example.acceptance",
            "example.product-intent",
        ], work
    except Exception as exc:
        errors.append(f"grouped artifact work: {exc}")

    try:
        split_graph = {
            "version": 1,
            "kind": "harness-engineering-graph",
            "id": "SPLIT-ROUTER-BOUNDARY",
            "authorities": [
                {
                    "id": "DISCOVERY",
                    "responsibility": "Own accepted source knowledge.",
                    "boundary": boundary("Discovery"),
                    "produces": [
                        {
                            "capability": "example.source-a",
                            "knowledge_kind": "problem-evidence",
                            "requires": [],
                        },
                        {
                            "capability": "example.source-b",
                            "knowledge_kind": "problem-evidence",
                            "requires": [],
                        },
                    ],
                },
                {
                    "id": "PRODUCT",
                    "responsibility": "Own product requirements.",
                    "boundary": boundary("Product"),
                    "produces": [
                        {
                            "capability": "example.product-a",
                            "knowledge_kind": "product-requirements",
                            "requires": ["example.source-a"],
                        },
                        {
                            "capability": "example.product-b",
                            "knowledge_kind": "product-requirements",
                            "requires": ["example.source-b"],
                        },
                    ],
                },
            ],
            "consumers": [
                {
                    "id": "IMPLEMENTATION",
                    "purpose": "Build",
                    "requires": ["example.product-a", "example.product-b"],
                }
            ],
            "terminal_capabilities": [],
        }
        split_model = {
            "artifacts": [
                {
                    "id": "SOURCE-A",
                    "authority": "DISCOVERY",
                    "path": "docs/source-a.md",
                    "provides": ["example.source-a"],
                    "depends_on": [],
                },
                {
                    "id": "SOURCE-B",
                    "authority": "DISCOVERY",
                    "path": "docs/source-b.md",
                    "provides": ["example.source-b"],
                    "depends_on": [],
                },
            ],
            "questions": [],
        }
        result = route_create_work(
            split_graph,
            "IMPLEMENTATION",
            split_model,
            registry,
        )
        product_work = [
            item
            for item in result["routed"]
            if item["knowledge_kind"] == "product-requirements"
        ]
        assert len(product_work) == 2, product_work
        assert {
            tuple(item["capabilities"])
            for item in product_work
        } == {
            ("example.product-a",),
            ("example.product-b",),
        }, product_work
    except Exception as exc:
        errors.append(f"prerequisite-boundary grouping: {exc}")

    try:
        blocked_model = {
            "artifacts": [],
            "questions": [
                {
                    "id": "Q-VERIFY",
                    "authority": "VERIFICATION",
                    "text": "What verification semantics are accepted?",
                    "blocks_capabilities": ["example.verification"],
                }
            ],
        }
        result = route_create_work(
            graph_for(),
            "IMPLEMENTATION",
            blocked_model,
            registry,
        )
        assert result["routed"] == [], result
        assert result["unrouted"] == [], result
        assert len(result["wait"]) == 1, result
    except Exception as exc:
        errors.append(f"WAIT must not route: {exc}")

    if errors:
        print("Harness agent router validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print("Harness agent router validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
