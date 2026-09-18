#!/usr/bin/env python3
"""Project an existing canonical design graph into a Harness Core v0 model.

The projection file supplies only Harness-specific ownership/capability/question
metadata. Artifact paths and dependency routing remain owned by the source graph.
"""
from __future__ import annotations

import argparse
import copy
from pathlib import Path
from typing import Any

import yaml

from harness import CoreError, validate_model


def _source_nodes(graph: dict[str, Any]) -> dict[str, dict[str, Any]]:
    nodes = graph.get("nodes", [])
    if not isinstance(nodes, list):
        raise CoreError("source graph nodes must be a list")

    result: dict[str, dict[str, Any]] = {}
    paths: set[str] = set()
    for node in nodes:
        if not isinstance(node, dict):
            raise CoreError("source graph node must be a mapping")
        node_id = node.get("id")
        if not isinstance(node_id, str) or not node_id:
            raise CoreError("source graph node id is required")
        if node_id in result:
            raise CoreError(f"duplicate source graph node id: {node_id}")
        path = node.get("path")
        if not isinstance(path, str) or not path:
            raise CoreError(f"source graph node {node_id} path is required")
        if path in paths:
            raise CoreError(f"duplicate source graph path: {path}")
        paths.add(path)
        result[node_id] = node

    for node_id, node in result.items():
        deps = node.get("depends_on", []) or []
        if not isinstance(deps, list):
            raise CoreError(f"source graph node {node_id} depends_on must be a list")
        for dep in deps:
            if dep not in result:
                raise CoreError(f"source graph node {node_id} depends on unknown node: {dep}")
            if dep == node_id:
                raise CoreError(f"source graph node {node_id} cannot depend on itself")

    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node_id: str) -> None:
        if node_id in visiting:
            raise CoreError(f"source graph dependency cycle at: {node_id}")
        if node_id in visited:
            return
        visiting.add(node_id)
        for dep in result[node_id].get("depends_on", []) or []:
            visit(dep)
        visiting.remove(node_id)
        visited.add(node_id)

    for node_id in result:
        visit(node_id)
    return result


def project_model(source_graph: dict[str, Any], projection: dict[str, Any]) -> dict[str, Any]:
    nodes = _source_nodes(source_graph)

    authorities = projection.get("authorities", [])
    if not isinstance(authorities, list):
        raise CoreError("projection authorities must be a list")
    authority_ids = {
        item.get("id")
        for item in authorities
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }
    if len(authority_ids) != len(authorities):
        raise CoreError("projection authority ids must be present and unique")

    bindings = projection.get("bindings", [])
    if not isinstance(bindings, list) or not bindings:
        raise CoreError("projection requires at least one binding")

    binding_by_artifact: dict[str, dict[str, Any]] = {}
    for binding in bindings:
        if not isinstance(binding, dict):
            raise CoreError("projection binding must be a mapping")
        artifact_id = binding.get("artifact")
        if not isinstance(artifact_id, str) or not artifact_id:
            raise CoreError("projection binding artifact is required")
        if artifact_id in binding_by_artifact:
            raise CoreError(f"duplicate projection binding: {artifact_id}")
        if artifact_id not in nodes:
            raise CoreError(f"projection binding references unknown source artifact: {artifact_id}")
        authority = binding.get("authority")
        if authority not in authority_ids:
            raise CoreError(
                f"projection binding {artifact_id} references unknown authority: {authority}"
            )
        provides = binding.get("provides", []) or []
        if not isinstance(provides, list) or any(
            not isinstance(item, str) or not item for item in provides
        ):
            raise CoreError(f"projection binding {artifact_id} has invalid provides")
        binding_by_artifact[artifact_id] = binding

    selected = set(binding_by_artifact)
    frontier_cache: dict[str, set[str]] = {}

    def selected_frontier(node_id: str) -> set[str]:
        if node_id in frontier_cache:
            return set(frontier_cache[node_id])
        found: set[str] = set()
        for dep in nodes[node_id].get("depends_on", []) or []:
            if dep in selected:
                found.add(dep)
            else:
                found.update(selected_frontier(dep))
        frontier_cache[node_id] = set(found)
        return found

    artifacts: list[dict[str, Any]] = []
    for artifact_id, binding in binding_by_artifact.items():
        artifacts.append(
            {
                "id": artifact_id,
                "authority": binding["authority"],
                "path": nodes[artifact_id]["path"],
                "provides": list(binding.get("provides", []) or []),
                "depends_on": sorted(selected_frontier(artifact_id)),
            }
        )

    questions = copy.deepcopy(projection.get("questions", []) or [])
    if not isinstance(questions, list):
        raise CoreError("projection questions must be a list")

    model = {
        "authorities": copy.deepcopy(authorities),
        "artifacts": artifacts,
        "questions": questions,
    }
    validate_model(model)
    return model


def load_projection(path: str | Path) -> dict[str, Any]:
    projection_path = Path(path)
    projection = yaml.safe_load(projection_path.read_text(encoding="utf-8"))
    if not isinstance(projection, dict):
        raise CoreError("projection document must be a mapping")
    if projection.get("kind") != "harness-canonical-graph-projection":
        raise CoreError("unexpected projection kind")
    source_ref = projection.get("source_graph")
    if not isinstance(source_ref, str) or not source_ref:
        raise CoreError("projection source_graph path is required")
    source_path = projection_path.parent / source_ref
    source_graph = yaml.safe_load(source_path.read_text(encoding="utf-8"))
    if not isinstance(source_graph, dict):
        raise CoreError("source graph document must be a mapping")
    return project_model(source_graph, projection)


def main() -> int:
    parser = argparse.ArgumentParser(description="Project a canonical graph into Harness Core v0")
    parser.add_argument("projection")
    parser.add_argument("--output")
    args = parser.parse_args()

    model = load_projection(args.projection)
    rendered = yaml.safe_dump(model, sort_keys=False)
    if args.output:
        Path(args.output).write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
