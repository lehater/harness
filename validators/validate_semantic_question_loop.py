#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from engineering_graph import evaluate_engineering_target, realize_core_model
from harness import resolve_question, unresolved_questions
from semantic_admission import admit_artifact
from semantic_questions import append_question_proposals


GRAPH = {
    "version": 1,
    "kind": "harness-engineering-graph",
    "id": "SEMANTIC-QUESTION-LOOP",
    "authorities": [
        {
            "id": "APPLICATION-DESIGN",
            "responsibility": "Own task semantics.",
            "boundary": {
                "semantic_cohesion": "User task semantics.",
                "independent_change": "Tasks may change independently.",
                "public_contract": "Accepted task model.",
            },
            "produces": [
                {
                    "capability": "example.task-model",
                    "knowledge_kind": "task-model",
                    "requires": [],
                }
            ],
        }
    ],
    "consumers": [
        {
            "id": "IMPLEMENTATION",
            "purpose": "Consume a complete task model.",
            "requires": ["example.task-model"],
        }
    ],
    "terminal_capabilities": [],
}

MODEL = {"authorities": [], "artifacts": [], "questions": []}

CONTRACTS = {
    "version": 1,
    "kind": "harness-knowledge-kind-semantic-contracts",
    "defaults": {
        "requires_assertion_authority": True,
        "requires_source_authority": False,
        "requires_semantic_review": True,
        "required_review_checks": [
            "source-discipline",
            "authority-boundary",
            "no-invention",
        ],
    },
    "contracts": [
        {
            "knowledge_kind": "task-model",
            "owned_assertion_kinds": ["task-goal", "task-recovery"],
            "obligations": [
                {"id": "goal", "kind": "task-goal"},
                {"id": "recovery", "kind": "task-recovery"},
            ],
            "required_review_checks": ["task-not-screen-design"],
        }
    ],
}


def candidate(*, include_recovery: bool) -> dict:
    assertions = [
        {
            "id": "TASK-GOAL",
            "kind": "task-goal",
            "subject": "prepare",
            "semantic_value": "prepare for a target",
            "decision_authority": "APPLICATION-DESIGN",
        }
    ]
    if include_recovery:
        assertions.append(
            {
                "id": "TASK-RECOVERY",
                "kind": "task-recovery",
                "subject": "prepare",
                "semantic_value": "preserve context after validation failure",
                "decision_authority": "APPLICATION-DESIGN",
            }
        )
    return {
        "id": "TASK-MODEL",
        "capability": "example.task-model",
        "path": "docs/task-model.yaml",
        "changed_paths": ["docs/task-model.yaml"],
        "canonical_references": [],
        "semantic_assertions": assertions,
        "semantic_review": {
            "status": "ACCEPTED",
            "checks": [
                "source-discipline",
                "authority-boundary",
                "no-invention",
                "task-not-screen-design",
            ],
        },
    }


def main() -> int:
    from semantic_admission import load_yaml

    registry = load_yaml(ROOT / "skills/artifact-skill-registry-v0.yaml")

    rejected = admit_artifact(
        graph=GRAPH,
        model=MODEL,
        skill_registry=registry,
        knowledge_contracts=CONTRACTS,
        capability="example.task-model",
        sources={"semantic_assertions": []},
        candidate=candidate(include_recovery=False),
        acceptance_id="TASK-INCOMPLETE",
    )
    assert rejected["status"] == "REJECTED", rejected
    assert {
        item["code"] for item in rejected["findings"]
    } >= {"MISSING_OBLIGATION"}, rejected

    proposals = rejected["question_proposals"]
    assert len(proposals) == 1, proposals
    question = proposals[0]
    assert question["authority"] == "APPLICATION-DESIGN", question
    assert question["blocks_capabilities"] == ["example.task-model"], question

    questioned = append_question_proposals(MODEL, proposals)
    target = evaluate_engineering_target(GRAPH, "IMPLEMENTATION", questioned)
    assert target["status"] == "BLOCKED", target
    assert target["wait"][0]["questions"] == [question["id"]], target

    accepted = admit_artifact(
        graph=GRAPH,
        model=MODEL,
        skill_registry=registry,
        knowledge_contracts=CONTRACTS,
        capability="example.task-model",
        sources={"semantic_assertions": []},
        candidate=candidate(include_recovery=True),
        acceptance_id="TASK-COMPLETE",
    )
    assert accepted["status"] == "ACCEPTED", accepted
    assert accepted["question_proposals"] == [], accepted

    realized = realize_core_model(
        GRAPH,
        {
            **questioned,
            "artifacts": [
                {
                    "id": "TASK-MODEL",
                    "authority": "APPLICATION-DESIGN",
                    "path": "docs/task-model.yaml",
                    "provides": ["example.task-model"],
                    "depends_on": [],
                }
            ],
        },
    )
    resolved = resolve_question(realized, question["id"], "TASK-MODEL")
    assert unresolved_questions(resolved) == [], resolved

    print(
        "semantic question loop: PASS "
        "(missing obligation -> Question -> block -> accepted artifact -> resolve)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
