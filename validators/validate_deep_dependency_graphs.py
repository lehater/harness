#!/usr/bin/env python3
"""Depth regression for project-controlled dependency DAG traversals."""
from __future__ import annotations

import copy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from adapters.canonical_graph import _source_nodes  # noqa: E402
from capability_lifecycle import lifecycle_states  # noqa: E402
from harness.coverage.concern_activation import _capability_closure as activation_closure  # noqa: E402
from harness.coverage.coverage_planner import _capability_closure as planner_closure  # noqa: E402
from engineering_graph import derive_profile, validate_engineering_graph  # noqa: E402
from frontend_interface_knowledge import _task_rows  # noqa: E402
from harness import CoreError, validate_model  # noqa: E402
from reference_materializer import validate_reference_model  # noqa: E402
from target_state import validate_profile  # noqa: E402

DEPTH = 1200


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


def main() -> int:
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
        f"({DEPTH} nodes across Core/Graph/Profile/Lifecycle/Coverage/"
        "Adapter/Reference/Frontend)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
