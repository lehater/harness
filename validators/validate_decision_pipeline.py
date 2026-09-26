#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from decision_pipeline import derive_decision_roadmap
from harness import CoreError


GRAPH = {
    "version": 1,
    "kind": "harness-engineering-graph",
    "id": "DECISION-PIPELINE",
    "authorities": [
        {
            "id": "SOURCE",
            "responsibility": "Own accepted source facts.",
            "boundary": {
                "semantic_cohesion": "Source facts.",
                "independent_change": "Source facts change independently.",
                "public_contract": "Accepted source facts.",
            },
            "produces": [
                {
                    "capability": "source.baseline",
                    "knowledge_kind": "problem-evidence",
                    "requires": [],
                }
            ],
        },
        {
            "id": "ARCH",
            "responsibility": "Own architecture decisions.",
            "boundary": {
                "semantic_cohesion": "Architecture decisions.",
                "independent_change": "Architecture changes independently.",
                "public_contract": "Accepted architecture.",
            },
            "produces": [
                {
                    "capability": "arch.a",
                    "knowledge_kind": "system-architecture",
                    "requires": [{"capability": "source.baseline"}],
                },
                {
                    "capability": "arch.b",
                    "knowledge_kind": "system-architecture",
                    "requires": [{"capability": "source.baseline"}],
                },
                {
                    "capability": "arch.c",
                    "knowledge_kind": "system-architecture",
                    "requires": [
                        {"capability": "arch.a"},
                        {"capability": "arch.b"},
                    ],
                },
            ],
        },
    ],
    "consumers": [
        {
            "id": "TARGET",
            "purpose": "Consume architecture.",
            "requires": [
                {"capability": "arch.b"},
                {"capability": "arch.c"},
            ],
        }
    ],
    "terminal_capabilities": [],
}

POLICY = {
    "version": 1,
    "kind": "harness-decision-policy",
    "defaults": {
        "exploration": "EXPLORE",
        "autonomy": "CONSERVATIVE",
        "execution_assurance": "REQUEST_BOUND",
    },
}

MODEL = {
    "artifacts": [
        {
            "id": "SOURCE",
            "authority": "SOURCE",
            "path": "source.md",
            "provides": ["source.baseline"],
            "depends_on": [],
        },
        {
            "id": "ARCH-A",
            "authority": "ARCH",
            "path": "a.md",
            "provides": ["arch.a"],
            "depends_on": ["SOURCE"],
        },
    ],
    "questions": [],
}

LIFECYCLE = {
    "version": 1,
    "kind": "harness-capability-lifecycle",
    "providers": [
        {
            "artifact": "SOURCE",
            "capability": "source.baseline",
            "acceptance_id": "SOURCE-1",
            "accepted_prerequisites": {},
        },
        {
            "artifact": "ARCH-A",
            "capability": "arch.a",
            "acceptance_id": "A-1",
            "accepted_prerequisites": {"source.baseline": "SOURCE-1"},
        },
    ],
}


def load(path: str):
    return yaml.safe_load((ROOT / path).read_text(encoding="utf-8"))


def caps(items):
    return [item["capability"] for item in items]


def main() -> int:
    contracts = load(
        "spec/decision-governance/knowledge-kind-decision-contracts-v1.yaml"
    )

    roadmap = derive_decision_roadmap(
        graph=GRAPH,
        model=MODEL,
        target="TARGET",
        lifecycle=LIFECYCLE,
        decision_contracts=contracts,
        decision_policy=POLICY,
    )
    assert caps(roadmap["ready"]) == ["arch.b"], roadmap
    assert caps(roadmap["completed"]) == ["arch.a", "source.baseline"], roadmap
    assert caps(roadmap["waiting_upstream"]) == ["arch.c"], roadmap
    create = roadmap["ready"][0]
    assert create["decision_request_mode"] == "CREATE", create
    assert create["pipeline"] == [
        "FORM_OPTIONS",
        "REVIEW_OPTIONS",
        "CHOOSE_OR_ESCALATE",
        "PRODUCE_CANDIDATE",
        "SEMANTIC_ADMISSION",
    ], create
    assert "b.md" not in {item["path"] for item in create["read_set"]}, create

    redo = derive_decision_roadmap(
        graph=GRAPH,
        model=MODEL,
        target="TARGET",
        lifecycle=LIFECYCLE,
        decision_contracts=contracts,
        decision_policy=POLICY,
        redo_capabilities=["arch.a"],
    )
    assert caps(redo["ready"]) == ["arch.a", "arch.b"], redo
    redo_a = next(item for item in redo["ready"] if item["capability"] == "arch.a")
    assert redo_a["decision_request_mode"] == "REDO", redo_a
    baseline = [
        item
        for item in redo_a["read_set"]
        if item["path"] == "a.md"
    ]
    assert len(baseline) == 1, redo_a
    assert baseline[0]["purpose"] == "CURRENT_ACCEPTED_BASELINE", redo_a
    assert "future_candidate" in redo_a["decision_request"]["forbidden_inputs"], redo_a

    # Explicit redo never bypasses a Core Question.
    blocked_model = {
        **MODEL,
        "questions": [
            {
                "id": "Q-A",
                "authority": "ARCH",
                "text": "Which accepted architecture semantics apply?",
                "blocks_capabilities": ["arch.a"],
            }
        ],
    }
    blocked = derive_decision_roadmap(
        graph=GRAPH,
        model=blocked_model,
        target="TARGET",
        lifecycle=LIFECYCLE,
        decision_contracts=contracts,
        decision_policy=POLICY,
        redo_capabilities=["arch.a"],
    )
    assert "arch.a" not in caps(blocked["ready"]), blocked
    assert next(
        item for item in blocked["blocked"] if item["capability"] == "arch.a"
    )["questions"] == ["Q-A"], blocked

    # Complete the selected target: a repeated ordinary invocation becomes a no-op.
    complete_model = {
        "artifacts": [
            *MODEL["artifacts"],
            {
                "id": "ARCH-B",
                "authority": "ARCH",
                "path": "b.md",
                "provides": ["arch.b"],
                "depends_on": ["SOURCE"],
            },
            {
                "id": "ARCH-C",
                "authority": "ARCH",
                "path": "c.md",
                "provides": ["arch.c"],
                "depends_on": ["ARCH-B"],
            },
        ],
        "questions": [],
    }
    complete_lifecycle = {
        "version": 1,
        "kind": "harness-capability-lifecycle",
        "providers": [
            *LIFECYCLE["providers"],
            {
                "artifact": "ARCH-B",
                "capability": "arch.b",
                "acceptance_id": "B-1",
                "accepted_prerequisites": {"source.baseline": "SOURCE-1"},
            },
            {
                "artifact": "ARCH-C",
                "capability": "arch.c",
                "acceptance_id": "C-1",
                "accepted_prerequisites": {"arch.a": "A-1", "arch.b": "B-1"},
            },
        ],
    }
    empty = derive_decision_roadmap(
        graph=GRAPH,
        model=complete_model,
        target="TARGET",
        lifecycle=complete_lifecycle,
        decision_contracts=contracts,
        decision_policy=POLICY,
    )
    assert empty["frontier_status"] == "EMPTY", empty
    assert empty["ready"] == [], empty

    try:
        derive_decision_roadmap(
            graph=GRAPH,
            model=MODEL,
            target="TARGET",
            lifecycle=LIFECYCLE,
            decision_contracts=contracts,
            decision_policy=POLICY,
            redo_capabilities=["outside.target"],
        )
    except CoreError:
        pass
    else:
        raise AssertionError("redo outside target closure must fail")

    print(
        "decision pipeline: PASS "
        "(single frontier + sequential stages + current-baseline redo + idempotence)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
