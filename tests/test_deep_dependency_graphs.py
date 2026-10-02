#!/usr/bin/env python3
"""Depth regression for project-controlled dependency DAG traversals."""
from __future__ import annotations

import copy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from harness.integration.adapters.canonical_graph import _source_nodes  # noqa: E402
from harness.assurance.capability_lifecycle import lifecycle_states  # noqa: E402
from harness.coverage.concern_activation import _capability_closure as activation_closure  # noqa: E402
from harness.coverage.coverage_planner import _capability_closure as planner_closure  # noqa: E402
from harness.project_model.engineering_graph import derive_profile, validate_engineering_graph  # noqa: E402
from harness.workspace.frontend_interface_knowledge import _task_rows  # noqa: E402
from harness.project_model.core import CoreError, validate_model  # noqa: E402
from harness.reference_model.reference_materializer import validate_reference_model  # noqa: E402
from harness.project_model.target_state import validate_profile  # noqa: E402

DEPTH = 1200
BREADTH = 512
CARDINALITY = 2000


def graph_fixture() -> dict:
    productions = []
    for index in range(DEPTH):
        productions.append(
            {
                "capability": f"cap.{index}",
                "knowledge_kind": "depth-regression",
                "requires": [] if index == 0 else [f"cap.{index - 1}"],
            }
        )
    return {
        "version": 1,
        "kind": "harness-engineering-graph",
        "id": "DEEP-DEPENDENCY-REGRESSION",
        "authorities": [
            {
                "id": "DEPTH",
                "responsibility": "Own synthetic depth-regression knowledge.",
                "boundary": {
                    "semantic_cohesion": "Synthetic dependency-chain knowledge.",
                    "independent_change": "Synthetic nodes change independently.",
                    "public_contract": "Depth-safe dependency traversal.",
                },
                "produces": productions,
            }
        ],
        "consumers": [
            {
                "id": "TARGET",
                "purpose": "Consume the deepest synthetic capability.",
                "requires": [f"cap.{DEPTH - 1}"],
            }
        ],
        "terminal_capabilities": [],
    }


def core_fixture() -> dict:
    return {
        "authorities": [{"id": "DEPTH"}],
        "artifacts": [
            {
                "id": f"ART-{index}",
                "authority": "DEPTH",
                "path": f"docs/depth/{index}.yaml",
                "provides": [f"cap.{index}"],
                "depends_on": [] if index == 0 else [f"ART-{index - 1}"],
            }
            for index in range(DEPTH)
        ],
        "questions": [],
    }


def lifecycle_fixture() -> dict:
    return {
        "version": 1,
        "kind": "harness-capability-lifecycle",
        "providers": [
            {
                "artifact": f"ART-{index}",
                "capability": f"cap.{index}",
                "acceptance_id": f"ACC-{index}",
                "accepted_prerequisites": (
                    {}
                    if index == 0
                    else {f"cap.{index - 1}": f"ACC-{index - 1}"}
                ),
            }
            for index in range(DEPTH)
        ],
    }


def source_graph_fixture() -> dict:
    return {
        "nodes": [
            {
                "id": f"NODE-{index}",
                "path": f"docs/source/{index}.yaml",
                "depends_on": [] if index == 0 else [f"NODE-{index - 1}"],
            }
            for index in range(DEPTH)
        ]
    }


def task_model_fixture() -> dict:
    leaf: dict = {
        "id": f"TASK-{DEPTH - 1}",
        "responsibility": "SYSTEM",
    }
    for index in range(DEPTH - 2, -1, -1):
        leaf = {
            "id": f"TASK-{index}",
            "responsibility": "SYSTEM",
            "tasks": [leaf],
        }
    return {
        "goals": [
            {
                "id": "GOAL",
                "tasks": [leaf],
            }
        ]
    }


def reference_model_fixture() -> tuple[dict, dict, dict]:
    model = {
        "version": 1,
        "kind": "harness-reference-engineering-model",
        "predicates": [],
        "templates": [
            {
                "id": f"T-{index}",
                "authority_type": "DEPTH",
                "claim_surface": [],
                "primary_claims": [],
                "scope": {"mode": "singleton"},
                "requires": (
                    [] if index == 0 else [{"template": f"T-{index - 1}"}]
                ),
            }
            for index in range(DEPTH)
        ],
    }
    return model, {"authorities": [{"id": "DEPTH"}]}, {"proofs": {}}


def breadth_graph_fixture() -> tuple[dict, dict, dict]:
    productions = [
        {
            "capability": "breadth.root",
            "knowledge_kind": "breadth-regression",
            "requires": [],
        }
    ]
    productions.extend(
        {
            "capability": f"breadth.leaf.{index}",
            "knowledge_kind": "breadth-regression",
            "requires": ["breadth.root"],
        }
        for index in range(BREADTH)
    )
    graph = {
        "version": 1,
        "kind": "harness-engineering-graph",
        "id": "BREADTH-DEPENDENCY-REGRESSION",
        "authorities": [
            {
                "id": "BREADTH",
                "responsibility": "Own synthetic breadth-regression knowledge.",
                "boundary": {
                    "semantic_cohesion": "Synthetic fan-out knowledge.",
                    "independent_change": "Synthetic nodes change independently.",
                    "public_contract": "Breadth-safe lifecycle traversal.",
                },
                "produces": productions,
            }
        ],
        "consumers": [
            {
                "id": "TARGET",
                "purpose": "Consume every fan-out leaf.",
                "requires": [f"breadth.leaf.{index}" for index in range(BREADTH)],
            }
        ],
        "terminal_capabilities": [],
    }
    model = {
        "artifacts": [
            {
                "id": "BREADTH-ROOT",
                "authority": "BREADTH",
                "path": "docs/breadth/root.yaml",
                "provides": ["breadth.root"],
                "depends_on": [],
            }
        ]
        + [
            {
                "id": f"BREADTH-{index}",
                "authority": "BREADTH",
                "path": f"docs/breadth/{index}.yaml",
                "provides": [f"breadth.leaf.{index}"],
                "depends_on": ["BREADTH-ROOT"],
            }
            for index in range(BREADTH)
        ],
        "questions": [],
    }
    lifecycle = {
        "version": 1,
        "kind": "harness-capability-lifecycle",
        "providers": [
            {
                "artifact": "BREADTH-ROOT",
                "capability": "breadth.root",
                "acceptance_id": "BREADTH-ROOT-1",
                "accepted_prerequisites": {},
            }
        ]
        + [
            {
                "artifact": f"BREADTH-{index}",
                "capability": f"breadth.leaf.{index}",
                "acceptance_id": f"BREADTH-{index}-1",
                "accepted_prerequisites": {
                    "breadth.root": "BREADTH-ROOT-1",
                },
            }
            for index in range(BREADTH)
        ],
    }
    return graph, model, lifecycle


def cardinality_graph_fixture() -> tuple[dict, dict, dict]:
    graph = {
        "version": 1,
        "kind": "harness-engineering-graph",
        "id": "CARDINALITY-REGRESSION",
        "authorities": [
            {
                "id": "CARDINALITY",
                "responsibility": "Own synthetic cardinality-regression knowledge.",
                "boundary": {
                    "semantic_cohesion": "Independent synthetic knowledge.",
                    "independent_change": "Every synthetic capability changes independently.",
                    "public_contract": "Cardinality-safe lifecycle traversal.",
                },
                "produces": [
                    {
                        "capability": f"cardinality.{index}",
                        "knowledge_kind": "cardinality-regression",
                        "requires": [],
                    }
                    for index in range(CARDINALITY)
                ],
            }
        ],
        "consumers": [
            {
                "id": "TARGET",
                "purpose": "Consume one capability while the remainder exercise cardinality only.",
                "requires": ["cardinality.0"],
            }
        ],
        "terminal_capabilities": [
            {
                "capability": f"cardinality.{index}",
                "authority": "CARDINALITY",
                "reason": "Synthetic terminal used only for lifecycle scale regression.",
            }
            for index in range(1, CARDINALITY)
        ],
    }
    model = {
        "artifacts": [
            {
                "id": f"CARDINALITY-{index}",
                "authority": "CARDINALITY",
                "path": f"docs/cardinality/{index}.yaml",
                "provides": [f"cardinality.{index}"],
                "depends_on": [],
            }
            for index in range(CARDINALITY)
        ],
        "questions": [],
    }
    lifecycle = {
        "version": 1,
        "kind": "harness-capability-lifecycle",
        "providers": [
            {
                "artifact": f"CARDINALITY-{index}",
                "capability": f"cardinality.{index}",
                "acceptance_id": f"CARDINALITY-{index}-1",
                "accepted_prerequisites": {},
            }
            for index in range(CARDINALITY)
        ],
    }
    return graph, model, lifecycle


def test_lifecycle_scale_shapes() -> None:
    breadth_graph, breadth_model, breadth_lifecycle = breadth_graph_fixture()
    validate_engineering_graph(breadth_graph)
    breadth_states = lifecycle_states(
        breadth_graph,
        breadth_model,
        breadth_lifecycle,
    )
    assert len(breadth_states) == BREADTH + 1, len(breadth_states)
    assert all(
        item["state"] == "CURRENT"
        for item in breadth_states.values()
    ), breadth_states

    cardinality_graph, cardinality_model, cardinality_lifecycle = (
        cardinality_graph_fixture()
    )
    validate_engineering_graph(cardinality_graph)
    cardinality_states = lifecycle_states(
        cardinality_graph,
        cardinality_model,
        cardinality_lifecycle,
    )
    assert len(cardinality_states) == CARDINALITY, len(cardinality_states)
    assert all(
        item["state"] == "CURRENT"
        for item in cardinality_states.values()
    ), cardinality_states


def main() -> int:
    test_lifecycle_scale_shapes()
    graph = graph_fixture()
    model = core_fixture()

    validate_model(model)
    validate_engineering_graph(graph)

    profile = derive_profile(graph, "TARGET")
    assert len(profile["expectations"]) == DEPTH, len(profile["expectations"])
    validate_profile(profile)

    states = lifecycle_states(graph, model, lifecycle_fixture())
    deepest = states[f"cap.{DEPTH - 1}"]
    assert deepest["state"] == "CURRENT", deepest

    expected = {f"cap.{index}" for index in range(DEPTH)}
    assert activation_closure(graph, [f"cap.{DEPTH - 1}"]) == expected
    assert planner_closure(graph, [f"cap.{DEPTH - 1}"]) == expected

    assert len(_source_nodes(source_graph_fixture())) == DEPTH
    assert len(_task_rows(task_model_fixture())) == DEPTH

    reference_model, authorities, proof = reference_model_fixture()
    assert not validate_reference_model(reference_model, authorities, proof)

    cyclic = copy.deepcopy(graph)
    cyclic["authorities"][0]["produces"][0]["requires"] = [f"cap.{DEPTH - 1}"]
    try:
        validate_engineering_graph(cyclic)
    except CoreError as exc:
        assert "cycle" in str(exc).lower(), exc
    except RecursionError as exc:
        raise AssertionError("deep invalid graph leaked RecursionError") from exc
    else:
        raise AssertionError("deep dependency cycle must be rejected")

    print(
        "deep dependency graphs: PASS "
        f"(depth={DEPTH}, breadth={BREADTH}, cardinality={CARDINALITY} "
        "across Core/Graph/Profile/Lifecycle/Coverage/Adapter/Reference/Frontend)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
