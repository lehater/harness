#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from harness.project_model.core import CoreError
from harness.application.project_frontier import compose_project_frontier


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


def main() -> int:
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
                        "docs/design/agent-instruction-architecture-v0.md"
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
        "docs/design/agent-instruction-architecture-v0.md"
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
