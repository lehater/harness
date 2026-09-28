#!/usr/bin/env python3
"""Coverage of semantic-derivation tests over Engineering Graph dependency edges."""
from __future__ import annotations

from typing import Any

from engineering_graph import production_index
from harness import CoreError

DISPOSITIONS = {"NOT_APPLICABLE"}


def _kind(production: dict[str, Any], capability: str) -> str:
    value = production.get("knowledge_kind")
    if not isinstance(value, str) or not value:
        raise CoreError(
            f"capability {capability} requires knowledge_kind for derivation test coverage"
        )
    return value


def evaluate_derivation_test_coverage(
    *,
    graph: dict[str, Any],
    tested_kind_edges: list[dict[str, Any]] | None = None,
    tested_capability_edges: list[dict[str, Any]] | None = None,
    dispositions: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    productions = production_index(graph)

    graph_edges: list[dict[str, str]] = []
    edge_ids: set[tuple[str, str]] = set()
    for target_capability, target_production in productions.items():
        target_kind = _kind(target_production, target_capability)
        for requirement in target_production.get("requires", []) or []:
            source_capability = requirement["capability"]
            source_production = productions.get(source_capability)
            if source_production is None:
                raise CoreError(
                    f"unknown prerequisite capability in derivation coverage: "
                    f"{source_capability}"
                )
            source_kind = _kind(source_production, source_capability)
            edge = {
                "source_capability": source_capability,
                "target_capability": target_capability,
                "source_knowledge_kind": source_kind,
                "target_knowledge_kind": target_kind,
            }
            graph_edges.append(edge)
            edge_ids.add((source_capability, target_capability))

    tested_kind_pairs: dict[tuple[str, str], str] = {}
    for item in tested_kind_edges or []:
        if not isinstance(item, dict):
            raise CoreError("tested derivation kind edge must be a mapping")
        source_kind = item.get("source_knowledge_kind")
        target_kind = item.get("target_knowledge_kind")
        scenario = item.get("scenario")
        if not all(isinstance(value, str) and value for value in (
            source_kind,
            target_kind,
            scenario,
        )):
            raise CoreError("tested derivation kind edge requires kinds and scenario")
        key = (source_kind, target_kind)
        if key in tested_kind_pairs and tested_kind_pairs[key] != scenario:
            raise CoreError(
                f"duplicate tested derivation kind edge with conflicting scenario: {key}"
            )
        tested_kind_pairs[key] = scenario

    tested_capability_pairs: dict[tuple[str, str], str] = {}
    for item in tested_capability_edges or []:
        if not isinstance(item, dict):
            raise CoreError("tested derivation capability edge must be a mapping")
        source = item.get("source_capability")
        target = item.get("target_capability")
        scenario = item.get("scenario")
        if not all(isinstance(value, str) and value for value in (
            source,
            target,
            scenario,
        )):
            raise CoreError(
                "tested derivation capability edge requires capabilities and scenario"
            )
        key = (source, target)
        if key not in edge_ids:
            raise CoreError(f"tested derivation capability edge is not in graph: {key}")
        if key in tested_capability_pairs and tested_capability_pairs[key] != scenario:
            raise CoreError(
                f"duplicate tested derivation capability edge with conflicting scenario: {key}"
            )
        tested_capability_pairs[key] = scenario

    disposition_by_edge: dict[tuple[str, str], dict[str, Any]] = {}
    for item in dispositions or []:
        if not isinstance(item, dict):
            raise CoreError("derivation coverage disposition must be a mapping")
        source = item.get("source_capability")
        target = item.get("target_capability")
        disposition = item.get("disposition")
        rationale = item.get("rationale")
        if not all(isinstance(value, str) and value for value in (
            source,
            target,
            disposition,
            rationale,
        )):
            raise CoreError(
                "derivation coverage disposition requires edge, disposition and rationale"
            )
        if disposition not in DISPOSITIONS:
            raise CoreError(
                f"unsupported derivation coverage disposition: {disposition}"
            )
        key = (source, target)
        if key not in edge_ids:
            raise CoreError(f"derivation coverage disposition is not a graph edge: {key}")
        if key in disposition_by_edge:
            raise CoreError(f"duplicate derivation coverage disposition: {key}")
        disposition_by_edge[key] = item

    covered: list[dict[str, Any]] = []
    disposed: list[dict[str, Any]] = []
    gaps: list[dict[str, Any]] = []

    for edge in sorted(
        graph_edges,
        key=lambda item: (
            item["target_capability"],
            item["source_capability"],
        ),
    ):
        capability_key = (
            edge["source_capability"],
            edge["target_capability"],
        )
        kind_key = (
            edge["source_knowledge_kind"],
            edge["target_knowledge_kind"],
        )
        if capability_key in tested_capability_pairs:
            covered.append(
                {
                    **edge,
                    "mode": "TESTED_CAPABILITY_EDGE",
                    "scenario": tested_capability_pairs[capability_key],
                }
            )
            continue
        if kind_key in tested_kind_pairs:
            covered.append(
                {
                    **edge,
                    "mode": "TESTED_KIND_EDGE",
                    "scenario": tested_kind_pairs[kind_key],
                }
            )
            continue
        if capability_key in disposition_by_edge:
            disposition = disposition_by_edge[capability_key]
            disposed.append(
                {
                    **edge,
                    "disposition": disposition["disposition"],
                    "rationale": disposition["rationale"],
                }
            )
            continue
        gaps.append(edge)

    return {
        "version": 1,
        "kind": "harness-semantic-derivation-test-coverage",
        "status": "COMPLETE" if not gaps else "INCOMPLETE",
        "edge_count": len(graph_edges),
        "covered_count": len(covered),
        "disposed_count": len(disposed),
        "gap_count": len(gaps),
        "covered": covered,
        "disposed": disposed,
        "gaps": gaps,
    }
