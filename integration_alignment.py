#!/usr/bin/env python3
"""Unified Harness integration checks for project-owned canonical graphs."""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

import yaml

from adapters.canonical_graph import project_model
from engineering_graph import (
    derive_profile,
    producer_index,
    production_index,
    validate_engineering_graph,
)
from harness import CoreError, validate_model


def _nodes(source_graph: dict[str, Any]) -> dict[str, dict[str, Any]]:
    items = source_graph.get("nodes", [])
    if not isinstance(items, list):
        raise CoreError("source graph nodes must be a list")
    result: dict[str, dict[str, Any]] = {}
    for item in items:
        if not isinstance(item, dict):
            raise CoreError("source graph node must be a mapping")
        node_id = item.get("id")
        if not isinstance(node_id, str) or not node_id:
            raise CoreError("source graph node id is required")
        if node_id in result:
            raise CoreError(f"duplicate source graph node id: {node_id}")
        result[node_id] = item
    return result


def validate_project_alignment(
    source_graph: dict[str, Any],
    projection: dict[str, Any],
    engineering_graph: dict[str, Any],
    *,
    require_complete_binding: bool = True,
    target_consumer: str | None = None,
) -> dict[str, Any]:
    """Validate that project artifact routing and capability topology agree.

    Project canonical artifacts remain the owner of file/dependency routing.
    Engineering Graph remains the owner of public capability prerequisites.
    This validator compares their cross-Authority dependency frontiers without
    creating a second project topology.
    """
    validate_engineering_graph(engineering_graph)
    model = project_model(source_graph, projection)
    validate_model(model)

    source_nodes = _nodes(source_graph)
    bindings = {
        item["artifact"]: item
        for item in projection.get("bindings", []) or []
    }

    if require_complete_binding:
        missing = sorted(set(source_nodes) - set(bindings))
        extra = sorted(set(bindings) - set(source_nodes))
        if missing:
            raise CoreError(
                f"selected canonical artifacts without Authority binding: {missing}"
            )
        if extra:
            raise CoreError(
                f"Authority bindings reference artifacts outside selected graph: {extra}"
            )

    producers = producer_index(engineering_graph)
    productions = production_index(engineering_graph)

    # Realization capability ownership must agree with normative producers.
    for binding in bindings.values():
        authority = binding["authority"]
        for capability in binding.get("provides", []) or []:
            expected = producers.get(capability)
            if expected is None:
                raise CoreError(
                    f"project capability {capability} has no Engineering Graph producer"
                )
            if expected != authority:
                raise CoreError(
                    f"project capability {capability} is bound to {authority}, "
                    f"Engineering Graph producer is {expected}"
                )

    artifact_authority = {
        item["artifact"]: item["authority"]
        for item in projection.get("bindings", []) or []
    }

    actual_by_authority: dict[str, set[str]] = defaultdict(set)
    for artifact_id, node in source_nodes.items():
        owner = artifact_authority.get(artifact_id)
        if owner is None:
            continue
        for dep in node.get("depends_on", []) or []:
            dep_owner = artifact_authority.get(dep)
            if dep_owner is None:
                if require_complete_binding:
                    raise CoreError(
                        f"canonical dependency {dep} of {artifact_id} has no Authority binding"
                    )
                continue
            if dep_owner != owner:
                actual_by_authority[owner].add(dep_owner)

    declared_by_authority: dict[str, set[str]] = defaultdict(set)
    materialized_capabilities = {
        capability
        for binding in bindings.values()
        for capability in binding.get("provides", []) or []
    }
    if target_consumer is None:
        alignment_capabilities = set(materialized_capabilities)
    else:
        profile = derive_profile(engineering_graph, target_consumer)
        alignment_capabilities = {
            item["capability"] for item in profile["expectations"]
        }

    for capability in alignment_capabilities:
        production = productions[capability]
        owner = producers[capability]
        for requirement in production.get("requires", []) or []:
            upstream = producers[requirement["capability"]]
            if upstream != owner:
                declared_by_authority[owner].add(upstream)

    selected_authorities = {
        authority
        for authority in artifact_authority.values()
        if any(
            producers.get(capability) == authority
            for capability in alignment_capabilities
        )
    }
    for authority in sorted(selected_authorities):
        actual = actual_by_authority.get(authority, set())
        declared = declared_by_authority.get(authority, set())
        hidden = sorted(actual - declared)
        phantom = sorted(declared - actual)
        if hidden:
            raise CoreError(
                f"Authority {authority} has hidden project-graph upstream Authorities: {hidden}"
            )
        if phantom:
            raise CoreError(
                f"Authority {authority} has phantom capability prerequisites not present "
                f"in project graph: {phantom}"
            )

    return {
        "model": model,
        "authority_dependencies": {
            authority: sorted(actual_by_authority.get(authority, set()))
            for authority in sorted(selected_authorities)
        },
        "bound_artifacts": sorted(bindings),
        "materialized_capabilities": sorted(materialized_capabilities),
        "alignment_capabilities": sorted(alignment_capabilities),
        "target_consumer": target_consumer,
    }


def load_yaml(path: str | Path) -> dict[str, Any]:
    value = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise CoreError(f"{path} must contain a mapping")
    return value


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate project canonical-graph alignment with Harness Engineering Graph"
    )
    parser.add_argument("source_graph")
    parser.add_argument("projection")
    parser.add_argument("engineering_graph")
    parser.add_argument("--allow-partial-binding", action="store_true")
    parser.add_argument("--target")
    parser.add_argument("--output-core")
    args = parser.parse_args()

    result = validate_project_alignment(
        load_yaml(args.source_graph),
        load_yaml(args.projection),
        load_yaml(args.engineering_graph),
        require_complete_binding=not args.allow_partial_binding,
        target_consumer=args.target,
    )
    if args.output_core:
        Path(args.output_core).write_text(
            yaml.safe_dump(result["model"], sort_keys=False),
            encoding="utf-8",
        )
    printable = {key: value for key, value in result.items() if key != "model"}
    print(json.dumps(printable, indent=2, sort_keys=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
