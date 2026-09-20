#!/usr/bin/env python3
"""Unified Harness integration checks for project-owned canonical graphs."""
from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Any

import yaml

from adapters.canonical_graph import project_model
from engineering_graph import (
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
    for capability in materialized_capabilities:
        production = productions[capability]
        owner = producers[capability]
        for requirement in production.get("requires", []) or []:
            upstream = producers[requirement["capability"]]
            if upstream != owner:
                declared_by_authority[owner].add(upstream)

    selected_authorities = set(artifact_authority.values())
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
    }


def load_yaml(path: str | Path) -> dict[str, Any]:
    value = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise CoreError(f"{path} must contain a mapping")
    return value
