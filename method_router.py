#!/usr/bin/env python3
"""Route canonical Engineering Coverage concerns to non-owning consumer methods."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml

from harness.project_model.core import CoreError


def load_yaml(path: str | Path) -> dict[str, Any]:
    value = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise CoreError(f"{path} must contain a mapping")
    return value


def concern_ids(catalog: dict[str, Any]) -> set[str]:
    if catalog.get("version") != 1:
        raise CoreError("engineering concern catalog version must be 1")
    if catalog.get("kind") != "harness-engineering-concern-catalog":
        raise CoreError("unexpected engineering concern catalog kind")

    result: set[str] = set()

    def visit(node: dict[str, Any]) -> None:
        concern = node.get("id")
        if not isinstance(concern, str) or not concern:
            raise CoreError("engineering concern node id is required")
        if concern in result:
            raise CoreError(f"duplicate engineering concern id: {concern}")
        result.add(concern)
        children = node.get("children", []) or []
        if not isinstance(children, list):
            raise CoreError(f"{concern}: children must be a list")
        for child in children:
            if not isinstance(child, dict):
                raise CoreError(f"{concern}: child must be a mapping")
            visit(child)

    for root in catalog.get("concerns", []) or []:
        if not isinstance(root, dict):
            raise CoreError("engineering concern root must be a mapping")
        visit(root)

    for key in ("quality_attribute_leaves", "specializations"):
        for item in catalog.get(key, []) or []:
            if not isinstance(item, dict):
                raise CoreError(f"{key} item must be a mapping")
            concern = item.get("id")
            if not isinstance(concern, str) or not concern:
                raise CoreError(f"{key} item id is required")
            if concern in result:
                raise CoreError(f"duplicate engineering concern id: {concern}")
            result.add(concern)

    return result


def validate_method_registry(
    registry: dict[str, Any],
    catalog: dict[str, Any],
    *,
    root: Path | None = None,
) -> None:
    if registry.get("version") != 1:
        raise CoreError("consumer method registry version must be 1")
    if registry.get("kind") != "harness-consumer-method-registry":
        raise CoreError("unexpected consumer method registry kind")
    if not isinstance(registry.get("id"), str) or not registry["id"]:
        raise CoreError("consumer method registry id is required")

    known_concerns = concern_ids(catalog)
    routes = registry.get("routes")
    if not isinstance(routes, list):
        raise CoreError("consumer method registry routes must be a list")

    seen_methods: set[str] = set()
    seen_skills: set[str] = set()
    selector_owner: dict[str, str] = {}

    for route in routes:
        if not isinstance(route, dict):
            raise CoreError("consumer method route must be a mapping")
        if set(route) != {"method", "skill", "concern_any"}:
            raise CoreError(
                "consumer method route must contain exactly method, skill and concern_any"
            )
        method = route["method"]
        skill = route["skill"]
        selectors = route["concern_any"]

        if not isinstance(method, str) or not method:
            raise CoreError("consumer method id is required")
        if method in seen_methods:
            raise CoreError(f"duplicate consumer method id: {method}")
        seen_methods.add(method)

        if not isinstance(skill, str) or not skill:
            raise CoreError(f"{method}: skill path is required")
        if skill in seen_skills:
            raise CoreError(f"consumer method skill routed more than once: {skill}")
        seen_skills.add(skill)
        if root is not None and not (root / skill).is_file():
            raise CoreError(f"{method}: registered skill does not exist: {skill}")

        if (
            not isinstance(selectors, list)
            or not selectors
            or not all(isinstance(value, str) and value for value in selectors)
        ):
            raise CoreError(f"{method}: concern_any must be a non-empty string list")

        for concern in selectors:
            if concern not in known_concerns:
                raise CoreError(f"{method}: unknown concern selector: {concern}")
            previous = selector_owner.get(concern)
            if previous is not None:
                raise CoreError(
                    f"ambiguous method selector {concern}: {previous} and {method}"
                )
            selector_owner[concern] = method


def route_methods(
    registry: dict[str, Any],
    catalog: dict[str, Any],
    *,
    concerns: list[str] | None = None,
    method: str | None = None,
) -> dict[str, Any]:
    validate_method_registry(registry, catalog)
    if (concerns is None) == (method is None):
        raise CoreError("provide exactly one of concerns or method")

    routes = registry["routes"]
    if method is not None:
        for route in routes:
            if route["method"] == method:
                return {
                    "mode": "explicit",
                    "routed": [
                        {
                            "method": route["method"],
                            "skill": route["skill"],
                            "matched_concerns": [],
                        }
                    ],
                    "unrouted_concerns": [],
                }
        raise CoreError(f"unknown consumer method: {method}")

    assert concerns is not None
    known = concern_ids(catalog)
    normalized = sorted(set(concerns))
    unknown = sorted(set(normalized) - known)
    if unknown:
        raise CoreError(f"unknown engineering concerns: {', '.join(unknown)}")

    routed: list[dict[str, Any]] = []
    matched_all: set[str] = set()
    requested = set(normalized)
    for route in routes:
        matched = sorted(set(route["concern_any"]) & requested)
        if not matched:
            continue
        matched_all.update(matched)
        routed.append(
            {
                "method": route["method"],
                "skill": route["skill"],
                "matched_concerns": matched,
            }
        )

    routed.sort(key=lambda item: item["method"])
    return {
        "mode": "concern",
        "requested_concerns": normalized,
        "routed": routed,
        "unrouted_concerns": sorted(requested - matched_all),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Route Harness concern ids or an explicit method id"
    )
    parser.add_argument(
        "--registry",
        default="skills/consumer-method-registry-v0.yaml",
    )
    parser.add_argument(
        "--catalog",
        default="spec/engineering-coverage/concern-catalog-v1.yaml",
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--concern", action="append", dest="concerns")
    group.add_argument("--method")
    args = parser.parse_args()

    result = route_methods(
        load_yaml(args.registry),
        load_yaml(args.catalog),
        concerns=args.concerns,
        method=args.method,
    )

    # This module remains the pure selector used by skill_router. Its executable
    # CLI is nevertheless a routing surface, so it must return the same trusted
    # instruction envelope as the canonical typed entrypoint.
    from skill_router import _with_instruction_contracts

    result = _with_instruction_contracts(
        {
            "surface": "consumer",
            "route_class": "method",
            **result,
        },
        Path(__file__).resolve().parent,
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
