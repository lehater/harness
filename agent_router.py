#!/usr/bin/env python3
"""Route actionable Engineering Graph CREATE work to artifact skills."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml

from engineering_graph import (
    evaluate_engineering_target,
    production_index,
    validate_engineering_graph,
)
from harness import CoreError


def load_yaml(path: str | Path) -> dict[str, Any]:
    value = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise CoreError(f"{path} must contain a mapping")
    return value


def validate_skill_registry(
    registry: dict[str, Any],
    *,
    root: Path | None = None,
) -> None:
    if registry.get("version") != 1:
        raise CoreError("artifact skill registry version must be 1")
    if registry.get("kind") != "harness-artifact-skill-registry":
        raise CoreError("unexpected artifact skill registry kind")
    if not isinstance(registry.get("id"), str) or not registry["id"]:
        raise CoreError("artifact skill registry id is required")

    routes = registry.get("routes", [])
    if not isinstance(routes, list):
        raise CoreError("artifact skill registry routes must be a list")

    seen: set[str] = set()
    for route in routes:
        if not isinstance(route, dict):
            raise CoreError("artifact skill route must be a mapping")
        if set(route) != {"knowledge_kind", "skill"}:
            raise CoreError(
                "artifact skill route must contain exactly knowledge_kind and skill"
            )
        knowledge_kind = route["knowledge_kind"]
        skill = route["skill"]
        if not isinstance(knowledge_kind, str) or not knowledge_kind:
            raise CoreError("route knowledge_kind is required")
        if knowledge_kind in seen:
            raise CoreError(f"duplicate knowledge_kind route: {knowledge_kind}")
        seen.add(knowledge_kind)
        if not isinstance(skill, str) or not skill:
            raise CoreError(f"{knowledge_kind}: skill path is required")
        if root is not None and not (root / skill).is_file():
            raise CoreError(
                f"{knowledge_kind}: registered skill does not exist: {skill}"
            )


def route_create_work(
    graph: dict[str, Any],
    target: str,
    model: dict[str, Any],
    registry: dict[str, Any],
) -> dict[str, Any]:
    validate_engineering_graph(graph)
    validate_skill_registry(registry)
    result = evaluate_engineering_target(graph, target, model)
    productions = production_index(graph)
    routes = {
        item["knowledge_kind"]: item["skill"]
        for item in registry.get("routes", [])
    }

    groups: dict[tuple[str, str, str | None], list[dict[str, Any]]] = {}
    untyped: list[dict[str, Any]] = []

    for item in result["create"]:
        capability = item["capability"]
        production = productions[capability]
        knowledge_kind = production.get("knowledge_kind")
        if knowledge_kind is None:
            untyped.append(item)
            continue
        key = (item["authority"], item["subject"], knowledge_kind)
        groups.setdefault(key, []).append(item)

    routed: list[dict[str, Any]] = []
    unrouted: list[dict[str, Any]] = []

    for item in untyped:
        unrouted.append(
            {
                "authority": item["authority"],
                "subject": item["subject"],
                "capabilities": [item["capability"]],
                "expectations": [item["expectation"]],
                "reason": "NO_KNOWLEDGE_KIND",
            }
        )

    for (authority, subject, knowledge_kind), items in sorted(groups.items()):
        base = {
            "authority": authority,
            "subject": subject,
            "knowledge_kind": knowledge_kind,
            "capabilities": sorted(item["capability"] for item in items),
            "expectations": sorted(item["expectation"] for item in items),
        }
        skill = routes.get(knowledge_kind)
        if skill is None:
            unrouted.append(
                {
                    **base,
                    "reason": "NO_REGISTERED_SKILL",
                }
            )
            continue
        routed.append(
            {
                **base,
                "skill": skill,
            }
        )

    return {
        "target_status": result["status"],
        "routed": routed,
        "unrouted": unrouted,
        "wait": result["wait"],
        "pending": result["pending"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Route Harness CREATE work to artifact skills")
    parser.add_argument("graph")
    parser.add_argument("target")
    parser.add_argument("model")
    parser.add_argument(
        "--registry",
        default="skills/artifact-skill-registry-v0.yaml",
    )
    args = parser.parse_args()

    result = route_create_work(
        load_yaml(args.graph),
        args.target,
        load_yaml(args.model),
        load_yaml(args.registry),
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
