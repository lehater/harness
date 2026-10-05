#!/usr/bin/env python3
from __future__ import annotations

import copy
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from harness.application.project_publication import build_project_publication
from harness.application.reconciliation import (
    execute_reconciliation,
    plan_reconciliation,
)
from harness.application.semantic_admission import (
    derive_acceptance_policy_fingerprints,
)
from harness.application.semantic_closure import evaluate_semantic_closure
from harness.project_model.core import CoreError


GRAPH = {
    "version": 1,
    "kind": "harness-engineering-graph",
    "id": "RECONCILIATION",
    "authorities": [
        {
            "id": "SOURCE-AUTHORITY",
            "responsibility": "Own source knowledge.",
            "boundary": {
                "semantic_cohesion": "Source semantics.",
                "independent_change": "Source semantics change independently.",
                "public_contract": "Accepted source knowledge.",
            },
            "produces": [
                {
                    "capability": "demo.source",
                    "knowledge_kind": "product-requirements",
                    "requires": [],
                }
            ],
        },
        {
            "id": "DEPENDENT-AUTHORITY",
            "responsibility": "Own dependent knowledge.",
            "boundary": {
                "semantic_cohesion": "Dependent semantics.",
                "independent_change": "Dependent semantics change independently.",
                "public_contract": "Accepted dependent knowledge.",
            },
            "produces": [
                {
                    "capability": "demo.dependent",
                    "knowledge_kind": "product-requirements",
                    "requires": ["demo.source"],
                }
            ],
        },
        {
            "id": "UNAFFECTED-AUTHORITY",
            "responsibility": "Own independent knowledge.",
            "boundary": {
                "semantic_cohesion": "Independent semantics.",
                "independent_change": "Independent semantics change independently.",
                "public_contract": "Accepted independent knowledge.",
            },
            "produces": [
                {
                    "capability": "demo.unaffected",
                    "knowledge_kind": "product-requirements",
                    "requires": [],
                }
            ],
        },
    ],
    "consumers": [
        {
            "id": "TARGET",
            "purpose": "Consume dependent and independent knowledge.",
            "requires": ["demo.dependent", "demo.unaffected"],
        }
    ],
    "terminal_capabilities": [],
}

CORE = {
    "artifacts": [
        {
            "id": "SOURCE",
            "authority": "SOURCE-AUTHORITY",
            "path": "docs/source.yaml",
            "provides": ["demo.source"],
            "depends_on": [],
        },
        {
            "id": "DEPENDENT",
            "authority": "DEPENDENT-AUTHORITY",
            "path": "docs/dependent.yaml",
            "provides": ["demo.dependent"],
            "depends_on": ["SOURCE"],
        },
        {
            "id": "UNAFFECTED",
            "authority": "UNAFFECTED-AUTHORITY",
            "path": "docs/unaffected.yaml",
            "provides": ["demo.unaffected"],
            "depends_on": [],
        },
    ],
    "questions": [],
}

EMPTY_FAILURES = {
    "version": 1,
    "kind": "harness-decision-failure-set",
    "failures": [],
}


def load(path: str) -> dict:
    return yaml.safe_load((ROOT / path).read_text(encoding="utf-8"))


REGISTRY = load("skills/artifact-skill-registry-v0.yaml")
CONTRACTS = load("spec/semantic-acceptance/knowledge-kind-contracts-v1.yaml")
DECISION_CONTRACTS = load(
    "spec/decision-governance/knowledge-kind-decision-contracts-v1.yaml"
)
CURRENT_POLICY = derive_acceptance_policy_fingerprints(
    graph=GRAPH,
    knowledge_contracts=CONTRACTS,
    decision_contracts=DECISION_CONTRACTS,
)


def accepted_evaluation(
    artifact: str,
    capability: str,
    acceptance_id: str,
    policy_fingerprint: str,
) -> dict:
    return {
        "version": 1,
        "kind": "harness-artifact-semantic-evaluation",
        "artifact": artifact,
        "capability": capability,
        "status": "ACCEPTED",
        "obligations": {
            "expected": [],
            "satisfied": [],
            "dispositions": [],
        },
        "findings": [],
        "semantic_claims": {"accepted": []},
        "question_proposals": [],
        "admission": {
            "status": "ACCEPTED",
            "acceptance_id": acceptance_id,
            "acceptance_policy_fingerprint": policy_fingerprint,
        },
    }


def publication(*, unaffected_stale: bool = False) -> dict:
    old = "sha256:stale-policy"
    unaffected_policy = (
        old if unaffected_stale else CURRENT_POLICY["demo.unaffected"]
    )
    evaluations = {
        "version": 1,
        "kind": "harness-semantic-evaluation-set",
        "semantic_evaluations": [
            accepted_evaluation("SOURCE", "demo.source", "SOURCE-1", old),
            accepted_evaluation(
                "DEPENDENT",
                "demo.dependent",
                "DEPENDENT-1",
                old,
            ),
            accepted_evaluation(
                "UNAFFECTED",
                "demo.unaffected",
                "UNAFFECTED-1",
                unaffected_policy,
            ),
        ],
    }
    lifecycle = {
        "version": 1,
        "kind": "harness-capability-lifecycle",
        "providers": [
            {
                "artifact": "SOURCE",
                "capability": "demo.source",
                "acceptance_id": "SOURCE-1",
                "acceptance_policy_fingerprint": old,
                "accepted_prerequisites": {},
            },
            {
                "artifact": "DEPENDENT",
                "capability": "demo.dependent",
                "acceptance_id": "DEPENDENT-1",
                "acceptance_policy_fingerprint": old,
                "accepted_prerequisites": {"demo.source": "SOURCE-1"},
            },
            {
                "artifact": "UNAFFECTED",
                "capability": "demo.unaffected",
                "acceptance_id": "UNAFFECTED-1",
                "acceptance_policy_fingerprint": unaffected_policy,
                "accepted_prerequisites": {},
            },
        ],
    }
    return build_project_publication(
        graph=GRAPH,
        core_model=CORE,
        semantic_evaluations=evaluations,
        lifecycle=lifecycle,
        decision_failures=EMPTY_FAILURES,
    )


def closure(current: dict) -> dict:
    return evaluate_semantic_closure(
        graph=GRAPH,
        model=current["state"]["core_model"],
        target="TARGET",
        skill_registry=REGISTRY,
        semantic_evaluations=current["state"]["semantic_evaluations"],
        lifecycle=current["state"]["lifecycle"],
        knowledge_contracts=CONTRACTS,
        decision_contracts=DECISION_CONTRACTS,
    )


def frontier(semantic_closure: dict) -> dict:
    next_actions = [
        {
            "source": "SEMANTIC_CLOSURE",
            "action": "REVALIDATE_SEMANTICS",
            "capability": item["capability"],
            "state": item["state"],
        }
        for item in semantic_closure["currentness_gaps"]
        if item.get("state") == "STALE"
    ]
    return {
        "version": 1,
        "kind": "harness-project-frontier",
        "target": "TARGET",
        "status": "READY" if next_actions else semantic_closure["status"],
        "next_actions": next_actions,
        "failed_validation": [],
        "blocked": [],
        "waiting": [],
        "gaps": [],
        "source_status": {
            "decision": "COMPLETE",
            "semantic": semantic_closure["status"],
            "structural": semantic_closure["structural_status"],
            "coverage_completion_ready": True,
        },
    }


def plan(current: dict) -> dict:
    semantic_closure = closure(current)
    return plan_reconciliation(
        graph=GRAPH,
        target="TARGET",
        current_publication_revision=current["revision"],
        project_frontier=frontier(semantic_closure),
        semantic_closure=semantic_closure,
    )


def candidate(artifact: str, capability: str, path: str, *, valid: bool = True) -> dict:
    checks = [
        "source-discipline",
        "authority-boundary",
        "no-invention",
        "observable-product-level",
        "no-downstream-design-promotion",
    ]
    return {
        "id": artifact,
        "capability": capability,
        "path": path,
        "semantic_assertions": [],
        "semantic_review": {
            "status": "ACCEPTED" if valid else "REJECTED",
            "checks": checks if valid else [],
            **({} if valid else {"reason": "synthetic invalid candidate"}),
        },
    }


def good_inputs() -> dict:
    return {
        "demo.source": {
            "sources": {"semantic_assertions": []},
            "candidate": candidate(
                "SOURCE",
                "demo.source",
                "docs/source.yaml",
            ),
            "acceptance_id": "SOURCE-2",
        },
        "demo.dependent": {
            "sources": {"semantic_assertions": []},
            "candidate": candidate(
                "DEPENDENT",
                "demo.dependent",
                "docs/dependent.yaml",
            ),
            "acceptance_id": "DEPENDENT-2",
        },
    }


def expect_core_error(fn, fragment: str) -> None:
    try:
        fn()
    except CoreError as exc:
        assert fragment in str(exc), (fragment, str(exc))
    else:
        raise AssertionError(f"expected CoreError containing {fragment!r}")


def by_capability(document: dict, field: str) -> dict[str, dict]:
    return {item["capability"]: item for item in document[field]}


def test_policy_staleness_reuse_and_atomic_completion() -> None:
    current = publication()
    semantic_closure = closure(current)
    stale = {
        item["capability"]
        for item in semantic_closure["currentness_gaps"]
        if item["state"] == "STALE"
    }
    assert stale == {"demo.source", "demo.dependent"}, semantic_closure
    assert semantic_closure["satisfied_capabilities"] == [
        "demo.unaffected"
    ], semantic_closure

    reconciliation_plan = plan(current)
    assert reconciliation_plan["affected"] == [
        "demo.source",
        "demo.dependent",
    ], reconciliation_plan
    assert reconciliation_plan["unchanged"] == [
        "demo.unaffected"
    ], reconciliation_plan

    result = execute_reconciliation(
        graph=GRAPH,
        target="TARGET",
        current_publication=current,
        expected_revision=current["revision"],
        plan=reconciliation_plan,
        skill_registry=REGISTRY,
        knowledge_contracts=CONTRACTS,
        decision_contracts=DECISION_CONTRACTS,
        admission_inputs=good_inputs(),
        resume_token=reconciliation_plan["resume_token"],
    )
    assert result["status"] == "COMPLETE", result
    assert result["completed"] == ["demo.source", "demo.dependent"], result
    assert result["closure"] == {
        "structural": "COMPLETE",
        "semantic": "COMPLETE",
    }, result
    assert result["semantic_closure"]["status"] == "COMPLETE", result

    next_publication = result["publication"]
    assert next_publication["parent_revision"] == current["revision"], result
    assert next_publication["revision"] != current["revision"], result

    old_evaluations = by_capability(
        current["state"]["semantic_evaluations"],
        "semantic_evaluations",
    )
    new_evaluations = by_capability(
        next_publication["state"]["semantic_evaluations"],
        "semantic_evaluations",
    )
    old_lifecycle = by_capability(current["state"]["lifecycle"], "providers")
    new_lifecycle = by_capability(next_publication["state"]["lifecycle"], "providers")
    assert new_evaluations["demo.unaffected"] == old_evaluations["demo.unaffected"]
    assert new_lifecycle["demo.unaffected"] == old_lifecycle["demo.unaffected"]
    assert new_lifecycle["demo.source"]["acceptance_id"] == "SOURCE-2"
    assert (
        new_lifecycle["demo.dependent"]["accepted_prerequisites"]["demo.source"]
        == "SOURCE-2"
    )


def test_resume_and_cas_are_revision_bound() -> None:
    current = publication()
    reconciliation_plan = plan(current)
    inputs = good_inputs()

    expect_core_error(
        lambda: execute_reconciliation(
            graph=GRAPH,
            target="TARGET",
            current_publication=current,
            expected_revision=current["revision"],
            plan=reconciliation_plan,
            skill_registry=REGISTRY,
            knowledge_contracts=CONTRACTS,
            decision_contracts=DECISION_CONTRACTS,
            admission_inputs=inputs,
            resume_token="sha256:not-the-plan-token",
        ),
        "resume token mismatch",
    )
    expect_core_error(
        lambda: execute_reconciliation(
            graph=GRAPH,
            target="TARGET",
            current_publication=current,
            expected_revision="sha256:stale-writer",
            plan=reconciliation_plan,
            skill_registry=REGISTRY,
            knowledge_contracts=CONTRACTS,
            decision_contracts=DECISION_CONTRACTS,
            admission_inputs=inputs,
        ),
        "compare-and-swap failed",
    )


def test_missing_acceptance_is_blocked_not_fabricated() -> None:
    current = publication()
    reconciliation_plan = plan(current)
    inputs = good_inputs()
    inputs["demo.source"].pop("acceptance_id")

    result = execute_reconciliation(
        graph=GRAPH,
        target="TARGET",
        current_publication=current,
        expected_revision=current["revision"],
        plan=reconciliation_plan,
        skill_registry=REGISTRY,
        knowledge_contracts=CONTRACTS,
        decision_contracts=DECISION_CONTRACTS,
        admission_inputs=inputs,
    )
    assert result["status"] == "BLOCKED", result
    assert {
        item.get("code") for item in result["blocked"]
    } >= {"ACCEPTANCE_ID_REQUIRED"}, result
    assert "publication" not in result, result
    assert result["completed"] == [], result
    assert result["waiting"] == [
        {
            "capability": "demo.dependent",
            "code": "WAITING_FOR_RECONCILIATION_PREREQUISITES",
            "prerequisites": ["demo.source"],
        }
    ], result


def test_independent_failures_are_aggregated() -> None:
    current = publication(unaffected_stale=True)
    reconciliation_plan = plan(current)
    assert set(reconciliation_plan["affected"]) == {
        "demo.source",
        "demo.dependent",
        "demo.unaffected",
    }, reconciliation_plan

    inputs = good_inputs()
    inputs["demo.source"]["candidate"] = candidate(
        "SOURCE",
        "demo.source",
        "docs/source.yaml",
        valid=False,
    )
    inputs["demo.unaffected"] = {
        "sources": {"semantic_assertions": []},
        "candidate": candidate(
            "UNAFFECTED",
            "demo.unaffected",
            "docs/unaffected.yaml",
            valid=False,
        ),
        "acceptance_id": "UNAFFECTED-2",
    }

    result = execute_reconciliation(
        graph=GRAPH,
        target="TARGET",
        current_publication=current,
        expected_revision=current["revision"],
        plan=reconciliation_plan,
        skill_registry=REGISTRY,
        knowledge_contracts=CONTRACTS,
        decision_contracts=DECISION_CONTRACTS,
        admission_inputs=inputs,
    )
    assert result["status"] == "FAILED_VALIDATION", result
    failed_capabilities = {
        item.get("capability") for item in result["failed_validation"]
    }
    assert {"demo.source", "demo.unaffected"} <= failed_capabilities, result
    assert any(
        item.get("capability") == "demo.dependent"
        and item.get("code") == "WAITING_FOR_RECONCILIATION_PREREQUISITES"
        for item in result["waiting"]
    ), result
    assert "publication" not in result, result


def main() -> int:
    test_policy_staleness_reuse_and_atomic_completion()
    test_resume_and_cas_are_revision_bound()
    test_missing_acceptance_is_blocked_not_fabricated()
    test_independent_failures_are_aggregated()
    print(
        "project reconciliation: PASS "
        "(policy staleness + unaffected reuse + aggregated blockers + "
        "revision-bound resume + one atomic publication)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
