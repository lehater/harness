#!/usr/bin/env python3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from agent_router import load_yaml, route_create_work  # noqa: E402
from engineering_graph import evaluate_engineering_target, validate_engineering_graph  # noqa: E402
PILOT = ROOT / "examples" / "frontend-blind-pilot"
GRAPH = load_yaml(PILOT / "engineering-graph.yaml")
REGISTRY = load_yaml(ROOT / "skills" / "artifact-skill-registry-v0.yaml")

CASES = [
    ("core-state-upstream.yaml", "user-journey-design", "APPLICATION-DESIGN"),
    ("core-state-with-journeys.yaml", "human-interface-design", "INTERFACE-DESIGN"),
    ("core-state-with-interface.yaml", "system-architecture", "SYSTEM-ARCHITECTURE"),
]

def assert_single_frontier(state_name: str, knowledge_kind: str, authority: str) -> None:
    state = load_yaml(PILOT / state_name)
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

    blocked_state = load_yaml(PILOT / "core-state-browser-auth-blocked.yaml")
    blocked = route_create_work(
        GRAPH, "FRONTEND-IMPLEMENTATION", blocked_state, REGISTRY
    )
    assert blocked["target_status"] == "BLOCKED", blocked
    assert not blocked["routed"], blocked
    assert not blocked["unrouted"], blocked
    assert blocked["wait"], blocked

    architecture_state = load_yaml(PILOT / "core-state-with-architecture.yaml")
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
        PILOT / "core-state-with-component-verification.yaml"
    )
    test_frontier = route_create_work(
        GRAPH, "FRONTEND-IMPLEMENTATION", component_verification_state, REGISTRY
    )
    assert test_frontier["target_status"] == "READY", test_frontier
    assert len(test_frontier["routed"]) == 1, test_frontier
    assert test_frontier["routed"][0]["knowledge_kind"] == "test-design", test_frontier

    test_state = load_yaml(PILOT / "core-state-with-test-design.yaml")
    implementation_frontier = route_create_work(
        GRAPH, "FRONTEND-IMPLEMENTATION", test_state, REGISTRY
    )
    assert implementation_frontier["target_status"] == "READY", implementation_frontier
    assert len(implementation_frontier["routed"]) == 1, implementation_frontier
    assert implementation_frontier["routed"][0]["knowledge_kind"] == "implementation-design", implementation_frontier

    complete_state = load_yaml(PILOT / "core-state-complete.yaml")
    complete = evaluate_engineering_target(
        GRAPH, "FRONTEND-IMPLEMENTATION", complete_state
    )
    assert complete["status"] == "COMPLETE", complete
    assert not complete["create"], complete
    assert not complete["wait"], complete
    assert not complete["pending"], complete

    print("frontend blind pilot graph: PASS")

if __name__ == "__main__":
    main()
