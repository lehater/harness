#!/usr/bin/env python3
"""Validate semantic CREATE-to-skill routing."""
from __future__ import annotations

import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from agent_router import (  # noqa: E402
    route_create_work,
    validate_skill_registry,
)
from harness import CoreError  # noqa: E402


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
        assert result["routed"] == [], result
        assert len(result["unrouted"]) == 1, result
        work = result["unrouted"][0]
        assert work["knowledge_kind"] == "product-requirements", work
        assert work["reason"] == "NO_REGISTERED_SKILL", work
        assert work["capabilities"] == [
            "example.acceptance",
            "example.product-intent",
        ], work
    except Exception as exc:
        errors.append(f"grouped artifact work: {exc}")

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
