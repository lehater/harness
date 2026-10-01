#!/usr/bin/env python3
"""Resolve typed Harness skill routes without flattening route semantics."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml

from harness import CoreError
from method_router import route_methods, load_yaml as load_method_yaml


ROOT = Path(__file__).resolve().parent


def load_yaml(path: str | Path) -> dict[str, Any]:
    path = Path(path)
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise CoreError(f"cannot load {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise CoreError(f"{path} must contain a mapping")
    return value


def _route_operation(
    registry: dict[str, Any],
    *,
    surface: str,
    operation: str,
    allow_internal: bool = False,
) -> dict[str, Any]:
    routes = registry.get("routes")
    if not isinstance(routes, list):
        raise CoreError(f"{surface} operation registry routes must be a list")
    for item in routes:
        if not isinstance(item, dict):
            continue
        if item.get("operation") != operation:
            continue
        exposure = item.get("exposure")
        if exposure == "internal" and not allow_internal:
            raise CoreError(
                f"{surface} operation {operation!r} is internal and not a public entry"
            )
        if exposure not in {"public", "internal"}:
            raise CoreError(
                f"{surface} operation {operation!r} has invalid exposure {exposure!r}"
            )
        skill = item.get("skill")
        if not isinstance(skill, str) or not skill:
            raise CoreError(f"{surface} operation {operation!r} has no skill")
        return {
            "surface": surface,
            "route_class": "operation",
            "route_key": operation,
            "skill": skill,
            "exposure": exposure,
        }
    raise CoreError(f"unknown {surface} operation: {operation}")


def route_operation(
    *,
    surface: str,
    operation: str,
    root: str | Path = ROOT,
    allow_internal: bool = False,
) -> dict[str, Any]:
    root = Path(root)
    if surface == "maintainer":
        path = root / "skills/maintainer-operation-registry-v0.yaml"
    elif surface == "consumer":
        path = root / "skills/consumer-operation-registry-v0.yaml"
    else:
        raise CoreError(f"unsupported operation surface: {surface}")
    if not path.is_file():
        raise CoreError(
            f"{surface} operation registry is not available in this distribution"
        )
    return _route_operation(
        load_yaml(path),
        surface=surface,
        operation=operation,
        allow_internal=allow_internal,
    )


def route_artifact(
    *,
    knowledge_kind: str,
    root: str | Path = ROOT,
) -> dict[str, Any]:
    root = Path(root)
    registry = load_yaml(root / "skills/artifact-skill-registry-v0.yaml")
    routes = registry.get("routes")
    if not isinstance(routes, list):
        raise CoreError("artifact skill registry routes must be a list")
    for item in routes:
        if not isinstance(item, dict):
            continue
        if item.get("knowledge_kind") != knowledge_kind:
            continue
        skill = item.get("skill")
        if not isinstance(skill, str) or not skill:
            raise CoreError(f"artifact route {knowledge_kind!r} has no skill")
        return {
            "surface": "consumer",
            "route_class": "artifact-production",
            "route_key": knowledge_kind,
            "skill": skill,
        }
    raise CoreError(f"no artifact skill registered for knowledge_kind: {knowledge_kind}")


def route_method(
    *,
    concerns: list[str] | None = None,
    method: str | None = None,
    root: str | Path = ROOT,
) -> dict[str, Any]:
    root = Path(root)
    registry = load_method_yaml(root / "skills/consumer-method-registry-v0.yaml")
    catalog = load_method_yaml(root / "spec/engineering-coverage/concern-catalog-v1.yaml")
    routed = route_methods(
        registry,
        catalog,
        concerns=concerns,
        method=method,
    )
    return {
        "surface": "consumer",
        "route_class": "method",
        **routed,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Resolve one typed Harness skill route"
    )
    sub = parser.add_subparsers(dest="route_class", required=True)

    operation = sub.add_parser("operation")
    operation.add_argument("--surface", choices=("maintainer", "consumer"), required=True)
    operation.add_argument("--operation", required=True)
    operation.add_argument("--allow-internal", action="store_true")
    operation.add_argument("--root", default=".")

    method = sub.add_parser("method")
    method_group = method.add_mutually_exclusive_group(required=True)
    method_group.add_argument("--method")
    method_group.add_argument("--concern", action="append", dest="concerns")
    method.add_argument("--root", default=".")

    artifact = sub.add_parser("artifact")
    artifact.add_argument("--knowledge-kind", required=True)
    artifact.add_argument("--root", default=".")

    args = parser.parse_args()
    if args.route_class == "operation":
        result = route_operation(
            surface=args.surface,
            operation=args.operation,
            root=args.root,
            allow_internal=args.allow_internal,
        )
    elif args.route_class == "method":
        result = route_method(
            concerns=args.concerns,
            method=args.method,
            root=args.root,
        )
    else:
        result = route_artifact(
            knowledge_kind=args.knowledge_kind,
            root=args.root,
        )

    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
