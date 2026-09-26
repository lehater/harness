#!/usr/bin/env python3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from agent_router import load_yaml, route_create_work
from engineering_graph import evaluate_engineering_target, validate_engineering_graph

EXAMPLE = ROOT / "examples" / "user-facing-application"
GRAPH = load_yaml(EXAMPLE / "engineering-graph.yaml")
REGISTRY = load_yaml(ROOT / "skills" / "artifact-skill-registry-v0.yaml")


def routed(state_name: str):
    return route_create_work(
        GRAPH,
        "FRONTEND-IMPLEMENTATION",
        load_yaml(EXAMPLE / state_name),
        REGISTRY,
    )


def assert_frontier(state_name: str, expected: set[tuple[str, str]]) -> None:
    result = routed(state_name)
    assert result["target_status"] == "READY", (state_name, result)
    actual = {(item["knowledge_kind"], item["authority"]) for item in result["routed"]}
    assert actual == expected, (state_name, actual, result)
    assert not result["unrouted"], (state_name, result["unrouted"])


def main() -> None:
    validate_engineering_graph(GRAPH)

    assert_frontier("core-state-empty.yaml", {("problem-evidence", "DISCOVERY")})
    assert_frontier("core-state-with-problem-evidence.yaml", {("user-needs", "DISCOVERY")})
    assert_frontier("core-state-with-user-needs.yaml", {("product-requirements", "PRODUCT-REQUIREMENTS")})
    assert_frontier("core-state-before-task-model.yaml", {("task-model", "APPLICATION-DESIGN")})
    assert_frontier("core-state-upstream.yaml", {("user-journey-design", "APPLICATION-DESIGN")})
    assert_frontier("core-state-with-journeys.yaml", {("conceptual-interface-model", "HUMAN-INTERFACE-DESIGN")})
    assert_frontier(
        "core-state-with-conceptual.yaml",
        {
            ("information-architecture-design", "HUMAN-INTERFACE-DESIGN"),
            ("interaction-design", "HUMAN-INTERFACE-DESIGN"),
        },
    )
    assert_frontier("core-state-with-ia-interaction.yaml", {("interface-topology-design", "HUMAN-INTERFACE-DESIGN")})
    assert_frontier(
        "core-state-with-topology.yaml",
        {
            ("presentation-system-design", "HUMAN-INTERFACE-DESIGN"),
            ("verification-strategy", "VERIFICATION-DESIGN"),
        },
    )
    assert_frontier("core-state-with-ui-foundations.yaml", {("screen-view-design", "HUMAN-INTERFACE-DESIGN")})
    assert_frontier(
        "core-state-with-screen-view.yaml",
        {
            ("visual-composition-design", "HUMAN-INTERFACE-DESIGN"),
            ("system-architecture", "SYSTEM-ARCHITECTURE"),
        },
    )
    assert_frontier(
        "core-state-with-architecture.yaml",
        {
            ("component-design", "COMPONENT-DESIGN"),
            ("verification-strategy", "VERIFICATION-DESIGN"),
        },
    )
    assert_frontier("core-state-with-component-verification.yaml", {("test-design", "TEST-DESIGN")})
    assert_frontier("core-state-with-test-design.yaml", {("implementation-design", "IMPLEMENTATION-DESIGN")})

    legacy_requirements = routed("core-state-legacy-requirements-without-user-needs.yaml")
    assert {
        (item["knowledge_kind"], item["authority"])
        for item in legacy_requirements["routed"]
    } == {("user-needs", "DISCOVERY")}, legacy_requirements

    legacy_journeys = routed("core-state-legacy-journeys-without-task-model.yaml")
    assert {
        (item["knowledge_kind"], item["authority"])
        for item in legacy_journeys["routed"]
    } == {("task-model", "APPLICATION-DESIGN")}, legacy_journeys

    blocked = routed("core-state-browser-auth-blocked.yaml")
    assert blocked["target_status"] == "BLOCKED", blocked
    assert not blocked["routed"], blocked
    assert blocked["wait"], blocked

    complete = evaluate_engineering_target(
        GRAPH,
        "FRONTEND-IMPLEMENTATION",
        load_yaml(EXAMPLE / "core-state-complete.yaml"),
    )
    assert complete["status"] == "COMPLETE", complete
    assert complete["implementation_consumer"] is True, complete
    assert not complete["create"], complete
    assert not complete["wait"], complete
    assert not complete["pending"], complete

    # Regression for the Prep failure shape: a design/revalidation Consumer may
    # be structurally COMPLETE while still being the wrong target for coding.
    revalidation_graph = {
        **GRAPH,
        "consumers": [
            *GRAPH["consumers"],
            {
                "id": "DESIGN-REVALIDATION",
                "purpose": "Revalidate accepted frontend design without authorizing implementation.",
                "requires": [
                    {"capability": "example.frontend.architecture"},
                    {"capability": "example.frontend.verification"},
                ],
            },
        ],
    }
    revalidation = evaluate_engineering_target(
        revalidation_graph,
        "DESIGN-REVALIDATION",
        load_yaml(EXAMPLE / "core-state-complete.yaml"),
    )
    assert revalidation["status"] == "COMPLETE", revalidation
    assert revalidation["implementation_consumer"] is False, revalidation

    print("user-facing application graph: PASS (granular frontend closure)")


if __name__ == "__main__":
    main()
