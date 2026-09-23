#!/usr/bin/env python3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from agent_router import load_yaml, route_create_work  # noqa: E402
from engineering_graph import evaluate_engineering_target, validate_engineering_graph  # noqa: E402
EXAMPLE = ROOT / "examples" / "user-facing-application"
GRAPH = load_yaml(EXAMPLE / "engineering-graph.yaml")
REGISTRY = load_yaml(ROOT / "skills" / "artifact-skill-registry-v0.yaml")

CASES = [
    ("core-state-empty.yaml", "problem-evidence", "DISCOVERY"),
    ("core-state-with-problem-evidence.yaml", "user-needs", "DISCOVERY"),
    ("core-state-with-user-needs.yaml", "product-requirements", "PRODUCT-REQUIREMENTS"),
    ("core-state-before-task-model.yaml", "task-model", "APPLICATION-DESIGN"),
    ("core-state-upstream.yaml", "user-journey-design", "APPLICATION-DESIGN"),
    ("core-state-with-interface.yaml", "presentation-system-design", "INTERFACE-DESIGN"),
    ("core-state-with-ui-foundations.yaml", "screen-view-design", "INTERFACE-DESIGN"),
    ("core-state-with-screen-view.yaml", "system-architecture", "SYSTEM-ARCHITECTURE"),
]

def assert_single_frontier(state_name: str, knowledge_kind: str, authority: str) -> None:
    state = load_yaml(EXAMPLE / state_name)
    routed = route_create_work(GRAPH, "FRONTEND-IMPLEMENTATION", state, REGISTRY)
    assert routed["target_status"] == "READY", (state_name, routed)
    assert len(routed["routed"]) == 1, (state_name, routed)
    item = routed["routed"][0]
    assert item["knowledge_kind"] == knowledge_kind, (state_name, item)
    assert item["authority"] == authority, (state_name, item)
    assert not routed["unrouted"], (state_name, routed["unrouted"])

def main() -> None:
    validate_engineering_graph(GRAPH)

    for state_name, knowledge_kind, authority in CASES:
        assert_single_frontier(state_name, knowledge_kind, authority)

    # Regression: a materialized Requirements provider cannot bypass its newly
    # declared User Needs predecessor. Downstream requirement consumers remain pending.
    legacy_requirements = load_yaml(
        EXAMPLE / "core-state-legacy-requirements-without-user-needs.yaml"
    )
    legacy_requirements_frontier = route_create_work(
        GRAPH, "FRONTEND-IMPLEMENTATION", legacy_requirements, REGISTRY
    )
    assert legacy_requirements_frontier["target_status"] == "READY", legacy_requirements_frontier
    assert {
        (item["knowledge_kind"], item["authority"])
        for item in legacy_requirements_frontier["routed"]
    } == {("user-needs", "DISCOVERY")}, legacy_requirements_frontier

    # Regression: a materialized Journey provider cannot substitute for Task Model.
    # Interface Design stays downstream until the task-model predecessor is accepted.
    legacy_journeys = load_yaml(
        EXAMPLE / "core-state-legacy-journeys-without-task-model.yaml"
    )
    legacy_journeys_frontier = route_create_work(
        GRAPH, "FRONTEND-IMPLEMENTATION", legacy_journeys, REGISTRY
    )
    assert legacy_journeys_frontier["target_status"] == "READY", legacy_journeys_frontier
    legacy_journeys_routed = {
        (item["knowledge_kind"], item["authority"])
        for item in legacy_journeys_frontier["routed"]
    }
    assert ("task-model", "APPLICATION-DESIGN") in legacy_journeys_routed, legacy_journeys_frontier
    assert not any(
        item["knowledge_kind"] in {
            "user-journey-design",
            "human-interface-design",
            "presentation-system-design",
            "screen-view-design",
        }
        for item in legacy_journeys_frontier["routed"]
    ), legacy_journeys_frontier

    # Human Interface semantics and the shared Presentation System are independent
    # once journeys/upstream constraints are known; both must close before screen design.
    journeys_state = load_yaml(EXAMPLE / "core-state-with-journeys.yaml")
    journeys_frontier = route_create_work(
        GRAPH, "FRONTEND-IMPLEMENTATION", journeys_state, REGISTRY
    )
    assert journeys_frontier["target_status"] == "READY", journeys_frontier
    actual_journeys = {
        (item["knowledge_kind"], item["authority"])
        for item in journeys_frontier["routed"]
    }
    assert actual_journeys == {
        ("human-interface-design", "INTERFACE-DESIGN"),
        ("presentation-system-design", "INTERFACE-DESIGN"),
    }, journeys_frontier
    assert not journeys_frontier["unrouted"], journeys_frontier["unrouted"]

    # Regression: Human Interface alone must not allow frontend architecture.
    interface_only = load_yaml(EXAMPLE / "core-state-with-interface.yaml")
    interface_only_eval = evaluate_engineering_target(
        GRAPH, "FRONTEND-IMPLEMENTATION", interface_only
    )
    assert interface_only_eval["status"] != "COMPLETE", interface_only_eval
    assert any(
        item.get("capability") == "example.frontend.presentation-system"
        for item in interface_only_eval["create"]
    ), interface_only_eval

    # Regression: Presentation + Human Interface without Screen/View Design is incomplete.
    ui_foundations = load_yaml(EXAMPLE / "core-state-with-ui-foundations.yaml")
    ui_foundations_eval = evaluate_engineering_target(
        GRAPH, "FRONTEND-IMPLEMENTATION", ui_foundations
    )
    assert ui_foundations_eval["status"] != "COMPLETE", ui_foundations_eval
    assert any(
        item.get("capability") == "example.frontend.screen-view-design"
        for item in ui_foundations_eval["create"]
    ), ui_foundations_eval

    blocked_state = load_yaml(EXAMPLE / "core-state-browser-auth-blocked.yaml")
    blocked = route_create_work(
        GRAPH, "FRONTEND-IMPLEMENTATION", blocked_state, REGISTRY
    )
    assert blocked["target_status"] == "BLOCKED", blocked
    assert not blocked["routed"], blocked
    assert not blocked["unrouted"], blocked
    assert blocked["wait"], blocked

    architecture_state = load_yaml(EXAMPLE / "core-state-with-architecture.yaml")
    architecture_frontier = route_create_work(
        GRAPH, "FRONTEND-IMPLEMENTATION", architecture_state, REGISTRY
    )
    assert architecture_frontier["target_status"] == "READY", architecture_frontier
    actual = {
        (item["knowledge_kind"], item["authority"])
        for item in architecture_frontier["routed"]
    }
    assert actual == {
        ("component-design", "COMPONENT-DESIGN"),
        ("verification-strategy", "VERIFICATION-DESIGN"),
    }, architecture_frontier
    assert not architecture_frontier["unrouted"], architecture_frontier["unrouted"]

    component_verification_state = load_yaml(
        EXAMPLE / "core-state-with-component-verification.yaml"
    )
    test_frontier = route_create_work(
        GRAPH, "FRONTEND-IMPLEMENTATION", component_verification_state, REGISTRY
    )
    assert test_frontier["target_status"] == "READY", test_frontier
    assert len(test_frontier["routed"]) == 1, test_frontier
    assert test_frontier["routed"][0]["knowledge_kind"] == "test-design", test_frontier

    test_state = load_yaml(EXAMPLE / "core-state-with-test-design.yaml")
    implementation_frontier = route_create_work(
        GRAPH, "FRONTEND-IMPLEMENTATION", test_state, REGISTRY
    )
    assert implementation_frontier["target_status"] == "READY", implementation_frontier
    assert len(implementation_frontier["routed"]) == 1, implementation_frontier
    assert implementation_frontier["routed"][0]["knowledge_kind"] == "implementation-design", implementation_frontier

    complete_state = load_yaml(EXAMPLE / "core-state-complete.yaml")
    complete = evaluate_engineering_target(
        GRAPH, "FRONTEND-IMPLEMENTATION", complete_state
    )
    assert complete["status"] == "COMPLETE", complete
    assert not complete["create"], complete
    assert not complete["wait"], complete
    assert not complete["pending"], complete

    print("user-facing application graph: PASS")

if __name__ == "__main__":
    main()
