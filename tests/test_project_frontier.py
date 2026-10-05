#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from harness.project_model.core import CoreError
from harness.application.project_frontier import compose_project_frontier
from harness.application.reconciliation import plan_reconciliation


def decision(status: str, **extra):
    return {
        "version": 1,
        "kind": "harness-decision-roadmap",
        "target": "IMPLEMENTATION",
        "frontier_status": status,
        "ready": [],
        "completed": [],
        "blocked": [],
        "failed_validation": [],
        "lifecycle_gaps": [],
        "waiting_upstream": [],
        **extra,
    }


def semantic(status: str = "COMPLETE", **extra):
    return {
        "version": 1,
        "kind": "harness-semantic-closure-evaluation",
        "target": "IMPLEMENTATION",
        "status": status,
        "structural_status": "COMPLETE",
        "semantic_gaps": [],
        "currentness_gaps": [],
        "question_frontier": [],
        "revalidate": [],
        "pending": [],
        **extra,
    }


def coverage(ready: bool = True, **extra):
    return {
        "version": 1,
        "kind": "harness-engineering-coverage-evaluation",
        "consumer": "IMPLEMENTATION",
        "completion_ready": ready,
        "work_items": [],
        "question_frontier": [],
        **extra,
    }


def test_cross_layer_precedence_matrix() -> None:
    executable = {
        "capability": "demo.ready",
        "authority": "DESIGN",
        "reason": "CREATE_MISSING_PROVIDER",
        "decision_request_mode": "CREATE",
        "pipeline": ["PRODUCE_CANDIDATE"],
    }
    failure = {
        "capability": "demo.failed",
        "state": "FAILED_VALIDATION",
        "failure_id": "ATTEMPT-1",
    }
    blocker = {
        "capability": "demo.blocked",
        "authority": "DESIGN",
        "questions": ["Q-BLOCKED"],
    }
    gap = {
        "capability": "demo.gap",
        "state": "UNKNOWN",
    }
    wait = {
        "capability": "demo.wait",
        "state": "WAITING_UPSTREAM",
    }

    cases = [
        (
            "READY",
            decision(
                "READY",
                ready=[executable],
                failed_validation=[failure],
                blocked=[blocker],
                lifecycle_gaps=[gap],
                waiting_upstream=[wait],
            ),
            semantic(
                status="INCOMPLETE",
                semantic_gaps=[
                    {
                        "capability": "demo.semantic",
                        "authority": "DESIGN",
                        "code": "SEMANTIC_ADMISSION_REQUIRED",
                    }
                ],
            ),
            coverage(False),
        ),
        (
            "FAILED_VALIDATION",
            decision(
                "FAILED_VALIDATION",
                failed_validation=[failure],
                blocked=[blocker],
                lifecycle_gaps=[gap],
                waiting_upstream=[wait],
            ),
            semantic(status="INCOMPLETE"),
            coverage(False),
        ),
        (
            "BLOCKED",
            decision(
                "BLOCKED",
                blocked=[blocker],
                lifecycle_gaps=[gap],
                waiting_upstream=[wait],
            ),
            semantic(status="INCOMPLETE"),
            coverage(False),
        ),
        (
            "INCOMPLETE",
            decision(
                "INCOMPLETE",
                lifecycle_gaps=[gap],
                waiting_upstream=[wait],
            ),
            semantic(status="INCOMPLETE"),
            coverage(False),
        ),
        (
            "WAITING",
            decision(
                "WAITING",
                waiting_upstream=[wait],
            ),
            semantic(status="INCOMPLETE"),
            coverage(False),
        ),
        (
            "COMPLETE",
            decision("COMPLETE"),
            semantic(),
            coverage(),
        ),
    ]

    for expected, decision_model, semantic_model, coverage_model in cases:
        result = compose_project_frontier(
            target="IMPLEMENTATION",
            decision_roadmap=decision_model,
            semantic_closure=semantic_model,
            engineering_coverage=coverage_model,
        )
        assert result["status"] == expected, (expected, result)

    false_complete_cases = [
        (
            decision("COMPLETE"),
            semantic(status="INCOMPLETE"),
            coverage(),
        ),
        (
            decision("COMPLETE"),
            semantic(),
            coverage(False),
        ),
        (
            decision("WAITING", waiting_upstream=[]),
            semantic(),
            coverage(),
        ),
    ]
    for decision_model, semantic_model, coverage_model in false_complete_cases:
        result = compose_project_frontier(
            target="IMPLEMENTATION",
            decision_roadmap=decision_model,
            semantic_closure=semantic_model,
            engineering_coverage=coverage_model,
        )
        assert result["status"] != "COMPLETE", result


def test_reconciliation_plan_reuses_unaffected_and_expands_stale_closure() -> None:
    graph = {
        "version": 1,
        "kind": "harness-engineering-graph",
        "id": "RECONCILIATION",
        "authorities": [
            {
                "id": "A",
                "responsibility": "Own A.",
                "boundary": {
                    "semantic_cohesion": "A.",
                    "independent_change": "A changes.",
                    "public_contract": "A.",
                },
                "produces": [
                    {"capability": "a", "knowledge_kind": "user-needs", "requires": []}
                ],
            },
            {
                "id": "B",
                "responsibility": "Own B.",
                "boundary": {
                    "semantic_cohesion": "B.",
                    "independent_change": "B changes.",
                    "public_contract": "B.",
                },
                "produces": [
                    {"capability": "b", "knowledge_kind": "product-requirements", "requires": ["a"]}
                ],
            },
            {
                "id": "X",
                "responsibility": "Own X.",
                "boundary": {
                    "semantic_cohesion": "X.",
                    "independent_change": "X changes.",
                    "public_contract": "X.",
                },
                "produces": [
                    {"capability": "x", "knowledge_kind": "user-needs", "requires": []}
                ],
            },
        ],
        "consumers": [
            {"id": "TARGET", "purpose": "Consume B and X.", "requires": ["b", "x"]}
        ],
        "terminal_capabilities": [],
    }
    frontier = {
        "version": 1,
        "kind": "harness-project-frontier",
        "target": "TARGET",
        "status": "READY",
        "next_actions": [
            {
                "source": "DECISION_ROADMAP",
                "action": "RUN_CAPABILITY_PIPELINE",
                "capability": "a",
                "reason": "REVISE_NONCURRENT_PROVIDER",
            }
        ],
        "failed_validation": [],
        "blocked": [
            {"source": "DECISION_ROADMAP", "capability": "q1", "questions": ["Q1"]},
            {"source": "DECISION_ROADMAP", "capability": "q2", "questions": ["Q2"]},
        ],
        "waiting": [],
        "gaps": [],
        "source_status": {
            "decision": "READY",
            "semantic": "INCOMPLETE",
            "structural": "COMPLETE",
            "coverage_completion_ready": True,
        },
    }
    closure = {
        "version": 1,
        "kind": "harness-semantic-closure-evaluation",
        "target": "TARGET",
        "status": "INCOMPLETE",
        "structural_status": "COMPLETE",
        "semantic_gaps": [],
        "currentness_gaps": [
            {"capability": "a", "state": "STALE", "details": {"state": "STALE"}},
            {"capability": "b", "state": "STALE", "details": {"state": "STALE"}},
        ],
        "question_frontier": [],
        "revalidate": [{"capability": "a"}],
        "pending": [{"capability": "b"}],
        "satisfied_capabilities": ["x"],
    }

    first = plan_reconciliation(
        graph=graph,
        target="TARGET",
        current_publication_revision="sha256:publication-1",
        project_frontier=frontier,
        semantic_closure=closure,
    )
    assert first["status"] == "READY", first
    assert first["closure"] == {
        "structural": "COMPLETE",
        "semantic": "INCOMPLETE",
    }, first
    assert first["affected"] == ["a", "b"], first
    assert first["unchanged"] == ["x"], first
    assert [item["capability"] for item in first["work"]] == ["a", "b"], first
    assert len(first["blocked"]) == 2, first

    repeated = plan_reconciliation(
        graph=graph,
        target="TARGET",
        current_publication_revision="sha256:publication-1",
        project_frontier=frontier,
        semantic_closure=closure,
    )
    assert repeated["resume_token"] == first["resume_token"], (first, repeated)

    changed_publication = plan_reconciliation(
        graph=graph,
        target="TARGET",
        current_publication_revision="sha256:publication-2",
        project_frontier=frontier,
        semantic_closure=closure,
    )
    assert changed_publication["resume_token"] != first["resume_token"], (
        first,
        changed_publication,
    )


def main() -> int:
    test_cross_layer_precedence_matrix()
    test_reconciliation_plan_reuses_unaffected_and_expands_stale_closure()
    complete = compose_project_frontier(
        target="IMPLEMENTATION",
        decision_roadmap=decision("COMPLETE"),
        semantic_closure=semantic(),
        engineering_coverage=coverage(),
    )
    assert complete["status"] == "COMPLETE", complete
    assert complete["next_actions"] == [], complete

    ready = compose_project_frontier(
        target="IMPLEMENTATION",
        decision_roadmap=decision(
            "READY",
            ready=[
                {
                    "capability": "demo.architecture",
                    "authority": "SYSTEM-ARCHITECTURE",
                    "reason": "CREATE_MISSING_PROVIDER",
                    "decision_request_mode": "CREATE",
                    "pipeline": ["PRODUCE_CANDIDATE", "SEMANTIC_ADMISSION"],
                }
            ],
        ),
        semantic_closure=semantic(status="INCOMPLETE"),
        engineering_coverage=coverage(
            False,
            work_items=[
                {
                    "action": "PRODUCE_CAPABILITY",
                    "capability": "demo.architecture",
                    "authority": "SYSTEM-ARCHITECTURE",
                    "knowledge_kind": "system-architecture",
                    "concerns": ["architecture.structure"],
                },
                {
                    "action": "MODEL_PRODUCTION_CONTRACT",
                    "concern": "reliability.failure-semantics",
                },
            ],
        ),
        create_routing={
            "routed": [
                {
                    "capabilities": ["demo.architecture"],
                    "skill": "skills/artifacts/system-architecture/SKILL.md",
                    "instruction_contracts": [
                        "docs/design/agent-instruction-architecture-v0.md",
                        "docs/design/process-simplicity-and-efficiency-v0.md",
                    ],
                }
            ],
            "unrouted": [],
        },
    )
    assert ready["status"] == "READY", ready
    capability = next(
        item
        for item in ready["next_actions"]
        if item.get("capability") == "demo.architecture"
    )
    assert capability["action"] == "RUN_CAPABILITY_PIPELINE", capability
    assert capability["execution_route"]["status"] == "ROUTED", capability
    assert capability["execution_route"]["instruction_contracts"] == [
        "docs/design/agent-instruction-architecture-v0.md",
        "docs/design/process-simplicity-and-efficiency-v0.md",
    ], capability
    assert capability["coverage_requirements"][0]["concerns"] == [
        "architecture.structure"
    ], capability
    assert sum(
        1
        for item in ready["next_actions"]
        if item.get("capability") == "demo.architecture"
    ) == 1, ready
    assert any(
        item.get("action") == "MODEL_PRODUCTION_CONTRACT"
        for item in ready["next_actions"]
    ), ready

    try:
        compose_project_frontier(
            target="IMPLEMENTATION",
            decision_roadmap=decision(
                "READY",
                ready=[
                    {
                        "capability": "demo.architecture",
                        "authority": "SYSTEM-ARCHITECTURE",
                        "reason": "CREATE_MISSING_PROVIDER",
                        "decision_request_mode": "CREATE",
                        "pipeline": [],
                    }
                ],
            ),
            semantic_closure=semantic(status="INCOMPLETE"),
            engineering_coverage=coverage(),
            create_routing={
                "routed": [
                    {
                        "capabilities": ["demo.architecture"],
                        "skill": "skills/artifacts/system-architecture/SKILL.md",
                    }
                ],
                "unrouted": [],
            },
        )
    except CoreError as exc:
        assert "instruction_contracts" in str(exc), exc
    else:
        raise AssertionError(
            "Project Frontier must reject routed work without trust contracts"
        )

    semantic_only = compose_project_frontier(
        target="IMPLEMENTATION",
        decision_roadmap=decision("COMPLETE"),
        semantic_closure=semantic(
            status="INCOMPLETE",
            semantic_gaps=[
                {
                    "capability": "demo.architecture",
                    "authority": "SYSTEM-ARCHITECTURE",
                    "code": "SEMANTIC_ADMISSION_REQUIRED",
                }
            ],
        ),
        engineering_coverage=coverage(),
    )
    assert semantic_only["status"] == "READY", semantic_only
    assert semantic_only["next_actions"][0]["action"] == "VALIDATE_SEMANTICS"

    blocked = compose_project_frontier(
        target="IMPLEMENTATION",
        decision_roadmap=decision(
            "BLOCKED",
            blocked=[
                {
                    "capability": "demo.architecture",
                    "authority": "SYSTEM-ARCHITECTURE",
                    "questions": ["Q-ARCH"],
                }
            ],
        ),
        semantic_closure=semantic(),
        engineering_coverage=coverage(),
    )
    assert blocked["status"] == "BLOCKED", blocked

    incomplete = compose_project_frontier(
        target="IMPLEMENTATION",
        decision_roadmap=decision(
            "INCOMPLETE",
            lifecycle_gaps=[
                {
                    "capability": "demo.architecture",
                    "state": "UNKNOWN",
                }
            ],
        ),
        semantic_closure=semantic(status="INCOMPLETE"),
        engineering_coverage=coverage(),
    )
    assert incomplete["status"] == "INCOMPLETE", incomplete

    waiting = compose_project_frontier(
        target="IMPLEMENTATION",
        decision_roadmap=decision(
            "WAITING",
            waiting_upstream=[
                {
                    "capability": "demo.component",
                    "state": "WAITING_UPSTREAM",
                }
            ],
        ),
        semantic_closure=semantic(status="INCOMPLETE"),
        engineering_coverage=coverage(),
    )
    assert waiting["status"] == "WAITING", waiting

    failed = compose_project_frontier(
        target="IMPLEMENTATION",
        decision_roadmap=decision(
            "FAILED_VALIDATION",
            failed_validation=[
                {
                    "capability": "demo.architecture",
                    "state": "FAILED_VALIDATION",
                    "failure_id": "ATTEMPT-1",
                }
            ],
        ),
        semantic_closure=semantic(status="INCOMPLETE"),
        engineering_coverage=coverage(),
    )
    assert failed["status"] == "FAILED_VALIDATION", failed

    try:
        compose_project_frontier(
            target="IMPLEMENTATION",
            decision_roadmap=decision("EMPTY"),
            semantic_closure=semantic(),
            engineering_coverage=coverage(),
        )
    except CoreError:
        pass
    else:
        raise AssertionError("ambiguous legacy EMPTY decision frontier must fail")

    print(
        "project frontier: PASS "
        "(cross-layer composition + deduplication + explicit terminal states)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
