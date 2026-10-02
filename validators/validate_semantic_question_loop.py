#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import copy
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from harness.project_model.engineering_graph import evaluate_engineering_target, realize_core_model
from harness.project_model.core import CoreError, resolve_question, unresolved_questions
from harness.application.semantic_admission import (
    admit_artifact,
    derive_acceptance_policy_fingerprints,
    load_yaml,
)
from harness.application.semantic_closure import evaluate_semantic_closure
from harness.application.semantic_questions import append_question_proposals, proposals_from_evaluation_set


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
        },
        {
            "id": "HUMAN-INTERFACE-DESIGN",
            "responsibility": "Consume accepted task semantics.",
            "boundary": {
                "semantic_cohesion": "Human interaction semantics.",
                "independent_change": "Interaction can change behind task semantics.",
                "public_contract": "Accepted interaction.",
            },
            "produces": [
                {
                    "capability": "example.interaction",
                    "knowledge_kind": "interaction-design",
                    "requires": ["example.task-model"],
                }
            ],
        },
    ],
    "consumers": [
        {
            "id": "IMPLEMENTATION",
            "purpose": "Consume accepted interaction.",
            "requires": ["example.interaction"],
        }
    ],
    "terminal_capabilities": [],
}

EMPTY_MODEL = {"authorities": [], "artifacts": [], "questions": []}


def task_candidate(
    *,
    recovery: bool = True,
    recovery_disposition: str | None = None,
    bad_review: bool = False,
) -> dict:
    assertions = [
        {
            "id": "GOAL-PREPARE",
            "kind": "task-goal",
            "semantic_value": "prepare",
            "decision_authority": "APPLICATION-DESIGN",
        },
        {
            "id": "TASK-PREPARE",
            "kind": "task",
            "semantic_value": "prepare for a target",
            "decision_authority": "APPLICATION-DESIGN",
        },
    ]
    fields = {
        "task-goal-ref": "GOAL-PREPARE",
        "task-responsibility": "USER",
        "task-information": "target context",
        "task-decision-input": "choose preparation path",
        "task-outcome": "target preparation started",
        "task-system-support": "show viable preparation paths",
    }
    for kind, value in fields.items():
        assertions.append(
            {
                "id": f"{kind.upper()}-TASK-PREPARE",
                "kind": kind,
                "subject": "TASK-PREPARE",
                "semantic_value": value,
                "decision_authority": "APPLICATION-DESIGN",
            }
        )
    if recovery:
        assertions.append(
            {
                "id": "TASK-RECOVERY-TASK-PREPARE",
                "kind": "task-recovery",
                "subject": "TASK-PREPARE",
                "semantic_value": "preserve target context",
                "decision_authority": "APPLICATION-DESIGN",
            }
        )

    candidate = {
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
    if recovery_disposition is not None:
        candidate["semantic_dispositions"] = [
            {
                "obligation": "recovery-per-task",
                "subject": "TASK-PREPARE",
                "status": recovery_disposition,
                "rationale": "Experiment disposition.",
            }
        ]
    if bad_review:
        candidate["semantic_review"]["checks"].remove("task-not-screen-design")
    return candidate


def test_current_derivation_snapshot_uniqueness() -> None:
    first = {
        "version": 1,
        "kind": "harness-semantic-derivation-evaluation",
        "source_capability": "demo.source",
        "target_capability": "demo.target",
        "status": "ACCEPTED",
        "question_proposals": [],
    }
    stale = {
        **first,
        "status": "REJECTED",
        "question_proposals": [
            {
                "id": "Q-STALE-DERIVATION",
                "authority": "TARGET",
                "text": "Stale derivation evidence must not reopen this Question.",
                "blocks_capabilities": ["demo.target"],
            }
        ],
    }
    bundle = {
        "version": 1,
        "kind": "harness-semantic-evaluation-set",
        "semantic_evaluations": [],
        "derivation_evaluations": [first, stale],
    }
    try:
        proposals_from_evaluation_set(bundle)
    except CoreError as exc:
        assert "duplicate current semantic derivation evaluation" in str(exc), exc
    else:
        raise AssertionError(
            "current derivation evaluation snapshot must reject duplicate edge identity"
        )


def main() -> int:
    test_current_derivation_snapshot_uniqueness()
    registry = load_yaml(ROOT / "skills/artifact-skill-registry-v0.yaml")
    base_contracts = load_yaml(
        ROOT / "spec/semantic-acceptance/knowledge-kind-contracts-v1.yaml"
    )
    decision_contracts = load_yaml(
        ROOT / "spec/decision-governance/knowledge-kind-decision-contracts-v1.yaml"
    )
    current_policy_fingerprints = derive_acceptance_policy_fingerprints(
        graph=GRAPH,
        knowledge_contracts=base_contracts,
        decision_contracts=decision_contracts,
        decision_policy=None,
    )

    rejected = admit_artifact(
        graph=GRAPH,
        model=EMPTY_MODEL,
        skill_registry=registry,
        knowledge_contracts=base_contracts,
        capability="example.task-model",
        sources={"semantic_assertions": []},
        candidate=task_candidate(recovery=False),
        acceptance_id="TASK-INCOMPLETE",
    )
    assert rejected["status"] == "REJECTED", rejected
    assert any(
        item.get("code") == "MISSING_SUBJECTS"
        and item.get("obligation") == "recovery-per-task"
        and item.get("subjects") == ["TASK-PREPARE"]
        for item in rejected["findings"]
    ), rejected
    assert len(rejected["question_proposals"]) == 1, rejected

    question = rejected["question_proposals"][0]
    assert question["authority"] == "APPLICATION-DESIGN", question
    assert question["blocks_capabilities"] == ["example.task-model"], question

    questioned = append_question_proposals(EMPTY_MODEL, [question])
    target = evaluate_engineering_target(GRAPH, "IMPLEMENTATION", questioned)
    assert target["status"] == "BLOCKED", target

    not_applicable = admit_artifact(
        graph=GRAPH,
        model=EMPTY_MODEL,
        skill_registry=registry,
        knowledge_contracts=base_contracts,
        capability="example.task-model",
        sources={"semantic_assertions": []},
        candidate=task_candidate(
            recovery=False,
            recovery_disposition="NOT_APPLICABLE",
        ),
        acceptance_id="TASK-NA",
    )
    assert not_applicable["status"] == "ACCEPTED", not_applicable
    assert not_applicable["question_proposals"] == [], not_applicable

    deferred = admit_artifact(
        graph=GRAPH,
        model=EMPTY_MODEL,
        skill_registry=registry,
        knowledge_contracts=base_contracts,
        capability="example.task-model",
        sources={"semantic_assertions": []},
        candidate=task_candidate(
            recovery=False,
            recovery_disposition="DEFERRED",
        ),
        acceptance_id="TASK-DEFERRED",
    )
    assert deferred["status"] == "REJECTED", deferred
    assert {
        item["code"] for item in deferred["findings"]
    } >= {"OBLIGATION_DEFERRED"}, deferred
    assert len(deferred["question_proposals"]) == 1, deferred

    bad_review = admit_artifact(
        graph=GRAPH,
        model=EMPTY_MODEL,
        skill_registry=registry,
        knowledge_contracts=base_contracts,
        capability="example.task-model",
        sources={"semantic_assertions": []},
        candidate=task_candidate(bad_review=True),
        acceptance_id="TASK-BAD-REVIEW",
    )
    assert bad_review["status"] == "REJECTED", bad_review
    assert "SEMANTIC_REVIEW_CHECKS_MISSING" in {
        item["code"] for item in bad_review["findings"]
    }
    assert bad_review["question_proposals"] == [], bad_review

    overlay = {
        "version": 1,
        "kind": "harness-knowledge-kind-semantic-overlay",
        "contracts": [
            {
                "knowledge_kind": "task-model",
                "owned_assertion_kinds": ["task-research-validation"],
                "obligations": [
                    {
                        "id": "research-validation",
                        "kind": "task-research-validation",
                    }
                ],
            }
        ],
    }
    overlaid = admit_artifact(
        graph=GRAPH,
        model=EMPTY_MODEL,
        skill_registry=registry,
        knowledge_contracts=base_contracts,
        knowledge_contract_overlays=[overlay],
        capability="example.task-model",
        sources={"semantic_assertions": []},
        candidate=task_candidate(),
        acceptance_id="TASK-OVERLAY",
    )
    assert overlaid["status"] == "REJECTED", overlaid
    assert any(
        item.get("obligation") == "research-validation"
        for item in overlaid["findings"]
    ), overlaid
    assert len(overlaid["question_proposals"]) == 1, overlaid

    complete_model = {
        "authorities": [],
        "artifacts": [
            {
                "id": "TASK-MODEL",
                "authority": "APPLICATION-DESIGN",
                "path": "docs/task-model.yaml",
                "provides": ["example.task-model"],
                "depends_on": [],
            },
            {
                "id": "INTERACTION",
                "authority": "HUMAN-INTERFACE-DESIGN",
                "path": "docs/interaction.yaml",
                "provides": ["example.interaction"],
                "depends_on": ["TASK-MODEL"],
            },
        ],
        "questions": [],
    }
    lifecycle = {
        "version": 1,
        "kind": "harness-capability-lifecycle",
        "providers": [
            {
                "artifact": "TASK-MODEL",
                "capability": "example.task-model",
                "acceptance_id": "TASK-INCOMPLETE",
                "accepted_prerequisites": {},
            },
            {
                "artifact": "INTERACTION",
                "capability": "example.interaction",
                "acceptance_id": "INTERACTION-1",
                "accepted_prerequisites": {
                    "example.task-model": "TASK-INCOMPLETE",
                },
            },
        ],
    }
    interaction_eval = {
        "version": 1,
        "kind": "harness-artifact-semantic-evaluation",
        "artifact": "INTERACTION",
        "capability": "example.interaction",
        "status": "ACCEPTED",
        "findings": [],
        "semantic_claims": {"accepted": []},
        "question_proposals": [],
        "admission": {
            "status": "ACCEPTED",
            "acceptance_id": "INTERACTION-1",
        },
    }
    for provider in lifecycle["providers"]:
        provider["acceptance_policy_fingerprint"] = (
            current_policy_fingerprints[provider["capability"]]
        )
    interaction_eval["admission"]["acceptance_policy_fingerprint"] = (
        current_policy_fingerprints["example.interaction"]
    )

    bundle = {
        "version": 1,
        "kind": "harness-semantic-evaluation-set",
        "semantic_evaluations": [rejected, interaction_eval],
    }
    closure = evaluate_semantic_closure(
        graph=GRAPH,
        model=complete_model,
        target="IMPLEMENTATION",
        skill_registry=registry,
        semantic_evaluations=bundle,
        lifecycle=lifecycle,
    )
    assert closure["status"] == "BLOCKED", closure
    assert closure["structural_status"] == "BLOCKED", closure
    assert closure["question_frontier"][0]["authority"] == "APPLICATION-DESIGN", closure
    assert closure["currentness_gaps"] == [], closure
    assert closure["semantic_gaps"] == [
        {
            "capability": "example.task-model",
            "authority": "APPLICATION-DESIGN",
            "artifact": "TASK-MODEL",
            "code": "SEMANTIC_QUESTION",
            "questions": [question["id"]],
            "findings": rejected["findings"],
        }
    ], closure
    assert {
        item["capability"] for item in closure["pending"]
    } == {"example.interaction"}, closure

    realized = realize_core_model(
        GRAPH,
        append_question_proposals(complete_model, [question]),
    )
    try:
        resolve_question(
            realized,
            question["id"],
            "TASK-MODEL",
            "TASK-INCOMPLETE",
            "TASK-INCOMPLETE",
        )
    except Exception as exc:
        assert "must differ" in str(exc), exc
    else:
        raise AssertionError(
            "Question resolution must reject unchanged semantic identity"
        )

    accepted = admit_artifact(
        graph=GRAPH,
        model=complete_model,
        skill_registry=registry,
        knowledge_contracts=base_contracts,
        capability="example.task-model",
        sources={"semantic_assertions": []},
        candidate=task_candidate(),
        acceptance_id="TASK-COMPLETE",
    )
    assert accepted["status"] == "ACCEPTED", accepted

    resolved = resolve_question(
        realized,
        question["id"],
        "TASK-MODEL",
        accepted["admission"]["acceptance_id"],
        "TASK-INCOMPLETE",
    )
    assert unresolved_questions(resolved) == [], resolved
    reopened = append_question_proposals(resolved, [question])
    assert unresolved_questions(reopened) == [question["id"]], reopened
    reopened_target = evaluate_engineering_target(
        GRAPH,
        "IMPLEMENTATION",
        reopened,
    )
    assert reopened_target["status"] == "BLOCKED", reopened_target

    updated_lifecycle = copy.deepcopy(lifecycle)
    updated_lifecycle["providers"][0] = accepted["lifecycle_assertion"]
    fixed_bundle = {
        "version": 1,
        "kind": "harness-semantic-evaluation-set",
        "semantic_evaluations": [accepted, interaction_eval],
    }
    fixed = evaluate_semantic_closure(
        graph=GRAPH,
        model=complete_model,
        target="IMPLEMENTATION",
        skill_registry=registry,
        semantic_evaluations=fixed_bundle,
        lifecycle=updated_lifecycle,
    )
    assert fixed["status"] == "INCOMPLETE", fixed
    assert any(
        item.get("capability") == "example.interaction"
        and item.get("state") == "STALE"
        for item in fixed["currentness_gaps"]
    ), fixed
    assert any(
        item.get("capability") == "example.interaction"
        for item in fixed["revalidate"]
    ), fixed

    print(
        "semantic question loop: PASS "
        "(obligations + dispositions + overlay + Question routing + "
        "honest closure + downstream revalidation)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
