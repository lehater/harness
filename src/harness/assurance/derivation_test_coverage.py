#!/usr/bin/env python3
"""Coverage of semantic-derivation tests over Engineering Graph dependency edges."""
from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from harness.project_model.engineering_graph import production_index
from harness.project_model.core import CoreError

DISPOSITIONS = {"NOT_APPLICABLE"}


def _kind(production: dict[str, Any], capability: str) -> str:
    value = production.get("knowledge_kind")
    if not isinstance(value, str) or not value:
        raise CoreError(
            f"capability {capability} requires knowledge_kind for derivation test coverage"
        )
    return value




def _scenario_fixture_value(
    document: dict[str, Any],
    scenario_path: Path,
    name: str,
) -> Any:
    fixtures = document.get("fixtures", {}) or {}
    spec = fixtures.get(name)
    if spec is None:
        raise CoreError(
            f"scenario {document.get('id')} references unknown fixture: {name}"
        )
    if not isinstance(spec, dict):
        return spec
    if "value" in spec:
        return spec["value"]
    if "yaml" in spec:
        path = (scenario_path.parent / str(spec["yaml"])).resolve()
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    raise CoreError(
        f"scenario {document.get('id')} derivation proof fixture {name} "
        "must use value or yaml"
    )


def _resolve_scenario_value(
    document: dict[str, Any],
    scenario_path: Path,
    value: Any,
) -> Any:
    if (
        isinstance(value, dict)
        and set(value) == {"ref"}
        and isinstance(value.get("ref"), str)
    ):
        ref = value["ref"]
        if not ref.startswith("fixture.") or "#" in ref:
            raise CoreError(
                f"scenario {document.get('id')} derivation proof uses "
                f"unsupported reference: {ref}"
            )
        return _scenario_fixture_value(
            document,
            scenario_path,
            ref[len("fixture."):],
        )
    return value


def _declared_derivation_edges(
    document: dict[str, Any],
) -> tuple[set[tuple[str, str]], set[tuple[str, str]]]:
    kind_edges: set[tuple[str, str]] = set()
    capability_edges: set[tuple[str, str]] = set()
    for item in document.get("derivation_edges", []) or []:
        if not isinstance(item, dict):
            raise CoreError(
                f"scenario {document.get('id')} derivation_edge must be a mapping"
            )
        source_kind = item.get("source_knowledge_kind")
        target_kind = item.get("target_knowledge_kind")
        source_capability = item.get("source_capability")
        target_capability = item.get("target_capability")
        if (
            isinstance(source_kind, str)
            and source_kind
            and isinstance(target_kind, str)
            and target_kind
        ):
            kind_edges.add((source_kind, target_kind))
            continue
        if (
            isinstance(source_capability, str)
            and source_capability
            and isinstance(target_capability, str)
            and target_capability
        ):
            capability_edges.add((source_capability, target_capability))
            continue
        raise CoreError(
            f"scenario {document.get('id')} derivation_edge requires a "
            "knowledge-kind pair or capability pair"
        )
    return kind_edges, capability_edges


def _scenario_edge_index(
    scenario_directory: str | None,
) -> dict[str, dict[str, set[tuple[str, str]]]]:
    if scenario_directory is None:
        return {}
    root = Path(scenario_directory)
    if not root.is_dir():
        raise CoreError(
            f"derivation coverage scenario_directory is not a directory: {root}"
        )

    result: dict[str, dict[str, set[tuple[str, str]]]] = {}
    for path in sorted(root.glob("*.yaml")):
        document = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not isinstance(document, dict) or document.get("kind") != "harness-scenario":
            continue
        scenario_id = document.get("id")
        if not isinstance(scenario_id, str) or not scenario_id:
            continue

        actual_kind_edges: set[tuple[str, str]] = set()
        actual_capability_edges: set[tuple[str, str]] = set()
        for step in document.get("steps", []) or []:
            if not isinstance(step, dict) or step.get("driver") != "semantic.derivation":
                continue
            arguments = step.get("with", {}) or {}
            if not isinstance(arguments, dict):
                raise CoreError(
                    f"scenario {scenario_id} semantic.derivation step requires with mapping"
                )
            graph = _resolve_scenario_value(
                document,
                path,
                arguments.get("graph"),
            )
            contract = _resolve_scenario_value(
                document,
                path,
                arguments.get("contract"),
            )
            if not isinstance(graph, dict) or not isinstance(contract, dict):
                raise CoreError(
                    f"scenario {scenario_id} semantic.derivation proof requires "
                    "resolvable graph and contract"
                )
            source_capability = contract.get("source_capability")
            target_capability = contract.get("target_capability")
            if not (
                isinstance(source_capability, str)
                and source_capability
                and isinstance(target_capability, str)
                and target_capability
            ):
                raise CoreError(
                    f"scenario {scenario_id} semantic.derivation contract "
                    "requires source_capability and target_capability"
                )
            productions = production_index(graph)
            source_production = productions.get(source_capability)
            target_production = productions.get(target_capability)
            if source_production is None or target_production is None:
                raise CoreError(
                    f"scenario {scenario_id} semantic.derivation step references "
                    "capability outside its graph"
                )
            actual_capability_edges.add(
                (source_capability, target_capability)
            )
            actual_kind_edges.add(
                (
                    _kind(source_production, source_capability),
                    _kind(target_production, target_capability),
                )
            )

        declared_kind_edges, declared_capability_edges = _declared_derivation_edges(
            document
        )
        if declared_kind_edges and declared_kind_edges != actual_kind_edges:
            raise CoreError(
                f"scenario {scenario_id} derivation_edges do not match executable "
                f"semantic.derivation kind edges; declared={sorted(declared_kind_edges)}, "
                f"actual={sorted(actual_kind_edges)}"
            )
        if (
            declared_capability_edges
            and declared_capability_edges != actual_capability_edges
        ):
            raise CoreError(
                f"scenario {scenario_id} capability derivation_edges do not match "
                "executable semantic.derivation steps"
            )

        result[scenario_id] = {
            "kind_edges": actual_kind_edges,
            "capability_edges": actual_capability_edges,
        }
    return result

def evaluate_derivation_test_coverage(
    *,
    graph: dict[str, Any],
    tested_kind_edges: list[dict[str, Any]] | None = None,
    tested_capability_edges: list[dict[str, Any]] | None = None,
    dispositions: list[dict[str, Any]] | None = None,
    scenario_directory: str | None = None,
) -> dict[str, Any]:
    productions = production_index(graph)
    scenario_edges = _scenario_edge_index(scenario_directory)
    invalid_registrations: list[dict[str, Any]] = []
    auto_kind_edges = tested_kind_edges is None and scenario_directory is not None
    auto_capability_edges = (
        tested_capability_edges is None and scenario_directory is not None
    )

    if auto_kind_edges:
        tested_kind_edges = [
            {
                "source_knowledge_kind": source_kind,
                "target_knowledge_kind": target_kind,
                "scenario": scenario_id,
            }
            for scenario_id, meta in sorted(scenario_edges.items())
            for source_kind, target_kind in sorted(meta["kind_edges"])
        ]
    if auto_capability_edges:
        tested_capability_edges = [
            {
                "source_capability": source_capability,
                "target_capability": target_capability,
                "scenario": scenario_id,
            }
            for scenario_id, meta in sorted(scenario_edges.items())
            for source_capability, target_capability in sorted(
                meta["capability_edges"]
            )
        ]

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
        scenario_meta = scenario_edges.get(scenario)
        if scenario_directory is not None and (
            scenario_meta is None or key not in scenario_meta["kind_edges"]
        ):
            invalid_registrations.append(
                {
                    "mode": "TESTED_KIND_EDGE",
                    "source_knowledge_kind": source_kind,
                    "target_knowledge_kind": target_kind,
                    "scenario": scenario,
                }
            )
            continue
        if key not in tested_kind_pairs:
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
        scenario_meta = scenario_edges.get(scenario)
        if scenario_directory is not None and (
            scenario_meta is None or key not in scenario_meta["capability_edges"]
        ):
            invalid_registrations.append(
                {
                    "mode": "TESTED_CAPABILITY_EDGE",
                    "source_capability": source,
                    "target_capability": target,
                    "scenario": scenario,
                }
            )
            continue
        if key not in edge_ids:
            if auto_capability_edges:
                continue
            raise CoreError(f"tested derivation capability edge is not in graph: {key}")
        if key not in tested_capability_pairs:
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
        "status": (
            "COMPLETE"
            if not gaps and not invalid_registrations
            else "INCOMPLETE"
        ),
        "edge_count": len(graph_edges),
        "covered_count": len(covered),
        "disposed_count": len(disposed),
        "gap_count": len(gaps),
        "invalid_registration_count": len(invalid_registrations),
        "covered": covered,
        "invalid_registrations": invalid_registrations,
        "disposed": disposed,
        "gaps": gaps,
    }


__all__ = [
    'Any',
    'CoreError',
    'DISPOSITIONS',
    'Path',
    'annotations',
    'evaluate_derivation_test_coverage',
    'production_index',
    'yaml',
]
