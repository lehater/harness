#!/usr/bin/env python3
from __future__ import annotations

import copy
from pathlib import Path
import sys
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from harness.assurance.semantic_acceptance import evaluate_artifact
from harness.application.semantic_admission import admit_artifact, knowledge_contract_index
from harness.project_model.core import CoreError


MANDATORY_KINDS = {
    "process-boundary": "application-process-boundary",
    "referenced-work": "application-process-work-reference",
    "composition": "application-process-composition",
    "completion": "application-process-completion",
}


def load(path: str):
    return yaml.safe_load((ROOT / path).read_text(encoding="utf-8"))


def semantic_contract() -> dict:
    contracts = knowledge_contract_index(
        load("spec/semantic-acceptance/knowledge-kind-contracts-v1.yaml")
    )
    base = contracts["application-process-design"]
    return {
        "authority": "APPLICATION-DESIGN",
        "owned_assertion_kinds": list(base["owned_assertion_kinds"]),
        "obligations": list(base["obligations"]),
        "requires_assertion_authority": base["requires_assertion_authority"],
        "requires_source_authority": base["requires_source_authority"],
        "requires_semantic_review": base["requires_semantic_review"],
        "required_semantic_review_checks": list(base["required_review_checks"]),
        "semantic_claims": ["engineering.application.process"],
    }


def candidate() -> dict:
    review_checks = semantic_contract()["required_semantic_review_checks"]
    return {
        "id": "PROCESS",
        "capability": "demo.application-process",
        "path": "docs/process.yaml",
        "changed_paths": ["docs/process.yaml"],
        "canonical_references": [],
        "semantic_assertions": [
            {
                "id": "PROCESS-BOUNDARY",
                "kind": "application-process-boundary",
                "subject": "policy-export",
                "semantic_value": "One export request through terminal export outcome.",
                "decision_authority": "APPLICATION-DESIGN",
            },
            {
                "id": "PROCESS-WORK",
                "kind": "application-process-work-reference",
                "subject": "build-export",
                "semantic_value": "Participates as referenced application work.",
                "decision_authority": "APPLICATION-DESIGN",
            },
            {
                "id": "PROCESS-COMPOSITION",
                "kind": "application-process-composition",
                "subject": "policy-export",
                "semantic_value": "Build export precedes terminal completion.",
                "decision_authority": "APPLICATION-DESIGN",
            },
            {
                "id": "PROCESS-COMPLETION",
                "kind": "application-process-completion",
                "subject": "policy-export",
                "semantic_value": "Completed when the accepted export outcome exists.",
                "decision_authority": "APPLICATION-DESIGN",
            },
        ],
        "semantic_review": {
            "status": "ACCEPTED",
            "checks": review_checks,
        },
    }


def codes(result: dict) -> set[str]:
    return {item["code"] for item in result.get("findings", [])}


def test_semantic_contract() -> None:
    contract = semantic_contract()
    base = candidate()

    # A simple synchronous process needs only the four mandatory semantics.
    # Continuation/recovery/progress remain genuinely optional.
    result = evaluate_artifact(contract, {"semantic_assertions": []}, base)
    assert result["status"] == "ACCEPTED", result

    for obligation, kind in MANDATORY_KINDS.items():
        mutated = copy.deepcopy(base)
        mutated["semantic_assertions"] = [
            item for item in mutated["semantic_assertions"]
            if item["kind"] != kind
        ]
        result = evaluate_artifact(contract, {"semantic_assertions": []}, mutated)
        assert result["status"] == "REJECTED", (obligation, result)
        assert any(
            item["code"] == "MISSING_OBLIGATION"
            and item.get("obligation") == obligation
            for item in result["findings"]
        ), (obligation, result)

    reowned = copy.deepcopy(base)
    reowned["semantic_assertions"].append(
        {
            "id": "DOMAIN-EVENT",
            "kind": "domain-event",
            "subject": "ExportCompleted",
            "semantic_value": "Process owns the domain event definition.",
            "decision_authority": "APPLICATION-DESIGN",
        }
    )
    result = evaluate_artifact(contract, {"semantic_assertions": []}, reowned)
    assert result["status"] == "REJECTED", result
    assert "WRONG_AUTHORITY_OWNERSHIP" in codes(result), result

    wrong_owner = copy.deepcopy(base)
    wrong_owner["semantic_assertions"][0]["decision_authority"] = "DOMAIN-DESIGN"
    result = evaluate_artifact(contract, {"semantic_assertions": []}, wrong_owner)
    assert result["status"] == "REJECTED", result
    assert "WRONG_AUTHORITY_OWNERSHIP" in codes(result), result

    missing_review = copy.deepcopy(base)
    missing_review["semantic_review"]["checks"].remove(
        "process-not-runtime-topology"
    )
    result = evaluate_artifact(contract, {"semantic_assertions": []}, missing_review)
    assert result["status"] == "REJECTED", result
    assert "SEMANTIC_REVIEW_CHECKS_MISSING" in codes(result), result


def process_graph(*, hidden_source: bool = False) -> dict:
    produces = []
    if hidden_source:
        produces.append(
            {
                "capability": "demo.hidden-application",
                "knowledge_kind": "application-design",
                "requires": [],
            }
        )
    produces.append(
        {
            "capability": "demo.application-process",
            "knowledge_kind": "application-process-design",
            "semantic_claims": ["engineering.application.process"],
            "requires": [],
        }
    )
    return {
        "version": 1,
        "kind": "harness-engineering-graph",
        "id": "PROCESS-DESIGN-TEST",
        "authorities": [
            {
                "id": "APPLICATION-DESIGN",
                "responsibility": "Own application composition.",
                "boundary": {
                    "semantic_cohesion": "Application composition.",
                    "independent_change": "Application composition changes independently.",
                    "public_contract": "Accepted application contracts.",
                },
                "produces": produces,
            }
        ],
        "consumers": [
            {
                "id": "IMPLEMENTATION",
                "purpose": "Consume the process.",
                "requires": ["demo.application-process"],
            }
        ],
        "terminal_capabilities": [],
    }


def test_process_decision_exploration_required() -> None:
    result = admit_artifact(
        graph=process_graph(),
        model={"artifacts": [], "questions": []},
        skill_registry=load("skills/artifact-skill-registry-v0.yaml"),
        knowledge_contracts=load(
            "spec/semantic-acceptance/knowledge-kind-contracts-v1.yaml"
        ),
        decision_contracts=load(
            "spec/decision-governance/knowledge-kind-decision-contracts-v1.yaml"
        ),
        capability="demo.application-process",
        sources={"semantic_assertions": []},
        candidate=candidate(),
        acceptance_id="PROCESS-1",
        decision_exploration=None,
    )
    assert result["status"] == "REJECTED", result
    assert "DECISION_EXPLORATION_REQUIRED" in codes(result), result


def test_process_cannot_read_undeclared_semantic_source() -> None:
    graph = process_graph(hidden_source=True)
    model = {
        "artifacts": [
            {
                "id": "HIDDEN-APPLICATION",
                "authority": "APPLICATION-DESIGN",
                "path": "docs/hidden-application.yaml",
                "provides": ["demo.hidden-application"],
                "depends_on": [],
            }
        ],
        "questions": [],
    }
    process = candidate()
    process["canonical_references"] = [
        {
            "artifact": "PROCESS",
            "referenced_path": "docs/hidden-application.yaml",
        }
    ]
    process["semantic_assertions"][1]["derived_from"] = ["HIDDEN-WORK"]
    sources = {
        "semantic_assertions": [
            {
                "id": "HIDDEN-WORK",
                "kind": "application-operation",
                "subject": "build-export",
                "semantic_value": "Build export.",
                "decision_authority": "APPLICATION-DESIGN",
                "source_artifact": "HIDDEN-APPLICATION",
            }
        ]
    }
    try:
        admit_artifact(
            graph=graph,
            model=model,
            skill_registry=load("skills/artifact-skill-registry-v0.yaml"),
            knowledge_contracts=load(
                "spec/semantic-acceptance/knowledge-kind-contracts-v1.yaml"
            ),
            decision_contracts=load(
                "spec/decision-governance/knowledge-kind-decision-contracts-v1.yaml"
            ),
            capability="demo.application-process",
            sources=sources,
            candidate=process,
            acceptance_id="PROCESS-HIDDEN",
            decision_exploration=None,
        )
    except CoreError as exc:
        assert "outside declared production prerequisites" in str(exc), str(exc)
    else:
        raise AssertionError("undeclared semantic source must be rejected")


def main() -> int:
    test_semantic_contract()
    test_process_decision_exploration_required()
    test_process_cannot_read_undeclared_semantic_source()
    print(
        "application process design: PASS "
        "(semantic obligations + ownership + review + decision + read boundary)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
