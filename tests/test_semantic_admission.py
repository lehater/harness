#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import copy
import sys
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from harness.project_model.core import CoreError
from harness.application.semantic_admission import (
    admit_artifact,
    derive_acceptance_policy_fingerprints,
    knowledge_contract_index,
)
from harness.assurance.semantic_derivation import evaluate_derivation


GRAPH = {
    "version": 1,
    "kind": "harness-engineering-graph",
    "id": "ADMISSION",
    "authorities": [
        {
            "id": "DISCOVERY",
            "responsibility": "Own user evidence.",
            "boundary": {
                "semantic_cohesion": "User evidence.",
                "independent_change": "Evidence changes independently.",
                "public_contract": "Accepted user needs.",
            },
            "produces": [
                {
                    "capability": "example.user-needs",
                    "knowledge_kind": "user-needs",
                    "requires": [],
                }
            ],
        },
        {
            "id": "PRODUCT-REQUIREMENTS",
            "responsibility": "Own observable product requirements.",
            "boundary": {
                "semantic_cohesion": "Product requirements.",
                "independent_change": "Requirements change independently.",
                "public_contract": "Accepted product intent.",
            },
            "produces": [
                {
                    "capability": "example.requirements",
                    "knowledge_kind": "product-requirements",
                    "requires": ["example.user-needs"],
                }
            ],
        },
        {
            "id": "DOMAIN-DESIGN",
            "responsibility": "Own domain decisions.",
            "boundary": {
                "semantic_cohesion": "Domain decisions.",
                "independent_change": "Domain model changes independently.",
                "public_contract": "Accepted domain semantics.",
            },
            "produces": [
                {
                    "capability": "example.domain",
                    "knowledge_kind": "domain-model",
                    "requires": ["example.requirements"],
                }
            ],
        },
    ],
    "consumers": [
        {
            "id": "IMPLEMENTATION",
            "purpose": "Consume accepted domain semantics.",
            "requires": ["example.domain"],
        }
    ],
    "terminal_capabilities": [],
}

MODEL = {
    "artifacts": [
        {
            "id": "NEEDS",
            "authority": "DISCOVERY",
            "path": "docs/needs.yaml",
            "provides": ["example.user-needs"],
            "depends_on": [],
        }
    ],
    "questions": [],
}

LIFECYCLE = {
    "version": 1,
    "kind": "harness-capability-lifecycle",
    "providers": [
        {
            "artifact": "NEEDS",
            "capability": "example.user-needs",
            "acceptance_id": "NEEDS-1",
            "accepted_prerequisites": {},
        }
    ],
}


def load(path: str):
    return yaml.safe_load((ROOT / path).read_text(encoding="utf-8"))


def candidate():
    return {
        "id": "REQUIREMENTS",
        "capability": "example.requirements",
        "path": "docs/requirements.yaml",
        "changed_paths": ["docs/requirements.yaml"],
        "canonical_references": [
            {
                "artifact": "REQUIREMENTS",
                "referenced_path": "docs/needs.yaml",
            }
        ],
        "semantic_assertions": [
            {
                "id": "REQ-AUTHORIZED-SOURCE",
                "kind": "product-requirement",
                "subject": "request-admission",
                "semantic_value": (
                    "Reject submission when the actor is not authorized "
                    "for the source side."
                ),
                "derived_from": ["NEED-AUTHORIZED-SOURCE"],
                "decision_authority": "PRODUCT-REQUIREMENTS",
            }
        ],
        "semantic_review": {
            "status": "ACCEPTED",
            "checks": [
                "source-discipline",
                "authority-boundary",
                "no-invention",
                "observable-product-level",
                "no-downstream-design-promotion",
            ],
        },
    }


def sources():
    return {
        "semantic_assertions": [
            {
                "id": "NEED-AUTHORIZED-SOURCE",
                "kind": "user-need",
                "subject": "request-admission",
                "semantic_value": (
                    "Only an authorized source-side actor may initiate access."
                ),
                "decision_authority": "DISCOVERY",
                "source_artifact": "NEEDS",
            }
        ]
    }


def expect_core_error(fn, fragment: str):
    try:
        fn()
    except CoreError as exc:
        assert fragment in str(exc), (fragment, str(exc))
    else:
        raise AssertionError(f"expected CoreError containing {fragment!r}")


def test_irrelevant_source_invariance() -> None:
    contract = {
        "version": 1,
        "kind": "harness-semantic-derivation-contract",
        "source_capability": "example.user-needs",
        "target_capability": "example.requirements",
        "obligations": [{"id": "needs", "source_kind": "user-need"}],
    }
    evidence = {
        "version": 1,
        "kind": "harness-semantic-derivation-evidence",
        "source_capability": "example.user-needs",
        "target_capability": "example.requirements",
        "links": [
            {
                "sources": ["NEED-AUTHORIZED-SOURCE"],
                "relation": "REALIZES",
                "targets": ["REQ-AUTHORIZED-SOURCE"],
            }
        ],
        "dispositions": [],
    }
    baseline_sources = sources()
    baseline = evaluate_derivation(
        graph=GRAPH,
        contract=contract,
        source=baseline_sources,
        candidate=candidate(),
        evidence=evidence,
    )

    noisy_sources = copy.deepcopy(baseline_sources)
    noisy_sources["semantic_assertions"].append(
        {
            "id": "IRRELEVANT-IMPLEMENTATION-NOTE",
            "kind": "implementation-note",
            "subject": "unrelated-runtime-detail",
            "semantic_value": "This statement is outside the declared derivation obligations.",
            "decision_authority": "DISCOVERY",
            "source_artifact": "NEEDS",
        }
    )
    noisy = evaluate_derivation(
        graph=GRAPH,
        contract=contract,
        source=noisy_sources,
        candidate=candidate(),
        evidence=evidence,
    )
    assert noisy == baseline, (noisy, baseline)


def test_required_target_provenance() -> None:
    contract = {
        "version": 1,
        "kind": "harness-semantic-derivation-contract",
        "source_capability": "example.user-needs",
        "target_capability": "example.requirements",
        "obligations": [
            {
                "id": "needs",
                "source_kind": "user-need",
                "require_target_provenance": True,
            }
        ],
    }
    evidence = {
        "version": 1,
        "kind": "harness-semantic-derivation-evidence",
        "source_capability": "example.user-needs",
        "target_capability": "example.requirements",
        "links": [
            {
                "sources": ["NEED-AUTHORIZED-SOURCE"],
                "relation": "REALIZES",
                "targets": ["REQ-AUTHORIZED-SOURCE"],
            }
        ],
        "dispositions": [],
    }

    accepted = evaluate_derivation(
        graph=GRAPH,
        contract=contract,
        source=sources(),
        candidate=candidate(),
        evidence=evidence,
    )
    assert accepted["status"] == "ACCEPTED", accepted
    assert accepted["coverage"] == {
        "required": 1,
        "covered": 1,
        "disposed": 0,
        "unresolved": 0,
    }

    missing_provenance = candidate()
    missing_provenance["semantic_assertions"][0]["derived_from"] = []
    rejected = evaluate_derivation(
        graph=GRAPH,
        contract=contract,
        source=sources(),
        candidate=missing_provenance,
        evidence=evidence,
    )
    assert rejected["status"] == "REJECTED", rejected
    assert rejected["coverage"]["covered"] == 0, rejected
    assert rejected["coverage"]["unresolved"] == 1, rejected
    assert any(
        finding.get("code") == "DERIVATION_TARGET_PROVENANCE_MISSING"
        and finding.get("source") == "NEED-AUTHORIZED-SOURCE"
        and finding.get("targets") == ["REQ-AUTHORIZED-SOURCE"]
        for finding in rejected["findings"]
    ), rejected


def main() -> int:
    test_irrelevant_source_invariance()
    test_required_target_provenance()
    registry = load("skills/artifact-skill-registry-v0.yaml")
    contracts = load(
        "spec/semantic-acceptance/knowledge-kind-contracts-v1.yaml"
    )
    decision_contracts = load(
        "spec/decision-governance/knowledge-kind-decision-contracts-v1.yaml"
    )
    current_policy_fingerprints = derive_acceptance_policy_fingerprints(
        graph=GRAPH,
        knowledge_contracts=contracts,
        decision_contracts=decision_contracts,
        decision_policy=None,
    )
    LIFECYCLE["providers"][0]["acceptance_policy_fingerprint"] = (
        current_policy_fingerprints["example.user-needs"]
    )
    contract_index = knowledge_contract_index(contracts)
    assert {
        "dependency-topology-explicit-where-material",
    } <= set(contract_index["system-architecture"]["required_review_checks"])
    assert {
        "obligations-concrete-and-reviewable",
        "optional-patterns-not-defaults",
    } <= set(contract_index["engineering-policy"]["required_review_checks"])
    assert {
        "implementation-facing-boundaries-complete-for-scope",
        "cross-consumer-reuse-disposition-complete",
    } <= set(contract_index["component-design"]["required_review_checks"])
    assert {
        "implementation-slices-explicit",
        "repository-realization-derived-from-accepted-boundaries",
    } <= set(contract_index["implementation-design"]["required_review_checks"])

    derivation = evaluate_derivation(
        graph=GRAPH,
        contract={
            "version": 1,
            "kind": "harness-semantic-derivation-contract",
            "source_capability": "example.user-needs",
            "target_capability": "example.requirements",
            "obligations": [
                {"id": "needs", "source_kind": "user-need"},
            ],
            "lifecycle_dependency": {"exhaustive": True},
        },
        source=sources(),
        candidate=candidate(),
        evidence={
            "version": 1,
            "kind": "harness-semantic-derivation-evidence",
            "source_capability": "example.user-needs",
            "target_capability": "example.requirements",
            "links": [
                {
                    "sources": ["NEED-AUTHORIZED-SOURCE"],
                    "relation": "REALIZES",
                    "targets": ["REQ-AUTHORIZED-SOURCE"],
                }
            ],
            "dispositions": [],
        },
    )
    assert derivation["status"] == "ACCEPTED", derivation

    result = admit_artifact(
        graph=GRAPH,
        model=MODEL,
        skill_registry=registry,
        knowledge_contracts=contracts,
        capability="example.requirements",
        sources=sources(),
        candidate=candidate(),
        acceptance_id="REQ-1",
        lifecycle=LIFECYCLE,
        derivation_evaluations=[derivation],
    )
    assert result["status"] == "ACCEPTED", result
    assert result["admission"]["allowed_source_authorities"] == [
        "DISCOVERY",
        "PRODUCT-REQUIREMENTS",
    ]
    assert result["lifecycle_assertion"]["accepted_prerequisites"] == {
        "example.user-needs": "NEEDS-1"
    }
    assert result["lifecycle_assertion"]["accepted_prerequisite_semantics"] == {
        "example.user-needs": {
            "exhaustive": True,
            "semantic_atoms": derivation["lifecycle_dependency"]["semantic_atoms"],
            "source_surface_fingerprints": derivation["lifecycle_dependency"][
                "source_surface_fingerprints"
            ],
        }
    }
    assert result["lifecycle_assertion"]["semantic_atom_fingerprints"], result
    assert result["admission"]["acceptance_policy_fingerprint"] == (
        current_policy_fingerprints["example.requirements"]
    ), result
    assert result["lifecycle_assertion"]["acceptance_policy_fingerprint"] == (
        current_policy_fingerprints["example.requirements"]
    ), result

    changed_contracts = copy.deepcopy(contracts)
    changed_user_needs = next(
        item
        for item in changed_contracts["contracts"]
        if item["knowledge_kind"] == "user-needs"
    )
    changed_user_needs.setdefault("required_review_checks", []).append(
        "policy-change-probe"
    )
    expect_core_error(
        lambda: admit_artifact(
            graph=GRAPH,
            model=MODEL,
            skill_registry=registry,
            knowledge_contracts=changed_contracts,
            decision_contracts=decision_contracts,
            capability="example.requirements",
            sources=sources(),
            candidate=candidate(),
            acceptance_id="REQ-POLICY-STALE",
            lifecycle=LIFECYCLE,
        ),
        "prerequisite example.user-needs is STALE",
    )


    hidden_graph = copy.deepcopy(GRAPH)
    product_authority = next(
        item
        for item in hidden_graph["authorities"]
        if item["id"] == "PRODUCT-REQUIREMENTS"
    )
    product_authority["produces"].append(
        {
            "capability": "example.product-context",
            "knowledge_kind": "product-requirements",
            "requires": [],
        }
    )
    hidden_graph["consumers"].append(
        {
            "id": "PRODUCT-CONTEXT-CONSUMER",
            "purpose": "Keep the support capability public for the regression fixture.",
            "requires": ["example.product-context"],
        }
    )

    hidden_model = copy.deepcopy(MODEL)
    hidden_model["artifacts"].extend(
        [
            {
                "id": "PRODUCT-CONTEXT",
                "authority": "PRODUCT-REQUIREMENTS",
                "path": "docs/product-context.yaml",
                "provides": ["example.product-context"],
                "depends_on": [],
            },
            {
                "id": "REQUIREMENTS",
                "authority": "PRODUCT-REQUIREMENTS",
                "path": "docs/requirements.yaml",
                "provides": ["example.requirements"],
                "depends_on": ["NEEDS", "PRODUCT-CONTEXT"],
            },
        ]
    )

    hidden_sources = {
        "semantic_assertions": [
            {
                "id": "PRODUCT-CONTEXT-SOURCE",
                "kind": "product-input",
                "subject": "request-admission",
                "semantic_value": "Use the existing same-Authority support decision.",
                "decision_authority": "PRODUCT-REQUIREMENTS",
                "source_artifact": "PRODUCT-CONTEXT",
            }
        ]
    }
    hidden_candidate = candidate()
    hidden_candidate["canonical_references"].append(
        {
            "artifact": "REQUIREMENTS",
            "referenced_path": "docs/product-context.yaml",
        }
    )
    hidden_candidate["semantic_assertions"][0]["derived_from"] = [
        "PRODUCT-CONTEXT-SOURCE"
    ]

    expect_core_error(
        lambda: admit_artifact(
            graph=hidden_graph,
            model=hidden_model,
            skill_registry=registry,
            knowledge_contracts=contracts,
            capability="example.requirements",
            sources=hidden_sources,
            candidate=hidden_candidate,
            acceptance_id="REQ-HIDDEN-SOURCE",
            lifecycle=LIFECYCLE,
        ),
        "outside declared production prerequisites for example.requirements",
    )

    declared_graph = copy.deepcopy(hidden_graph)
    declared_product = next(
        item
        for item in declared_graph["authorities"]
        if item["id"] == "PRODUCT-REQUIREMENTS"
    )
    declared_requirements = next(
        item
        for item in declared_product["produces"]
        if item["capability"] == "example.requirements"
    )
    declared_requirements["requires"].append("example.product-context")

    declared_policy_fingerprints = derive_acceptance_policy_fingerprints(
        graph=declared_graph,
        knowledge_contracts=contracts,
        decision_contracts=decision_contracts,
        decision_policy=None,
    )
    declared_lifecycle = copy.deepcopy(LIFECYCLE)
    declared_lifecycle["providers"][0]["acceptance_policy_fingerprint"] = (
        declared_policy_fingerprints["example.user-needs"]
    )
    declared_lifecycle["providers"].append(
        {
            "artifact": "PRODUCT-CONTEXT",
            "capability": "example.product-context",
            "acceptance_id": "PRODUCT-CONTEXT-1",
            "acceptance_policy_fingerprint": declared_policy_fingerprints[
                "example.product-context"
            ],
            "accepted_prerequisites": {},
        }
    )

    declared_result = admit_artifact(
        graph=declared_graph,
        model=hidden_model,
        skill_registry=registry,
        knowledge_contracts=contracts,
        decision_contracts=decision_contracts,
        capability="example.requirements",
        sources=hidden_sources,
        candidate=hidden_candidate,
        acceptance_id="REQ-DECLARED-SOURCE",
        lifecycle=declared_lifecycle,
    )
    assert declared_result["status"] == "ACCEPTED", declared_result
    assert declared_result["lifecycle_assertion"]["accepted_prerequisites"] == {
        "example.user-needs": "NEEDS-1",
        "example.product-context": "PRODUCT-CONTEXT-1",
    }

    bad_review = candidate()
    bad_review["semantic_review"]["checks"].remove(
        "no-downstream-design-promotion"
    )
    result = admit_artifact(
        graph=GRAPH,
        model=MODEL,
        skill_registry=registry,
        knowledge_contracts=contracts,
        capability="example.requirements",
        sources=sources(),
        candidate=bad_review,
        acceptance_id="REQ-2",
        lifecycle=LIFECYCLE,
    )
    assert result["status"] == "REJECTED", result
    assert {
        item["code"] for item in result["findings"]
    } >= {"SEMANTIC_REVIEW_CHECKS_MISSING"}

    bad_source = sources()
    bad_source["semantic_assertions"][0]["decision_authority"] = "DOMAIN-DESIGN"
    expect_core_error(
        lambda: admit_artifact(
            graph=GRAPH,
            model=MODEL,
            skill_registry=registry,
            knowledge_contracts=contracts,
            capability="example.requirements",
            sources=bad_source,
            candidate=candidate(),
            acceptance_id="REQ-3",
            lifecycle=LIFECYCLE,
        ),
        "does not match canonical artifact owner",
    )

    bad_write = candidate()
    bad_write["changed_paths"].append("docs/domain.yaml")
    expect_core_error(
        lambda: admit_artifact(
            graph=GRAPH,
            model=MODEL,
            skill_registry=registry,
            knowledge_contracts=contracts,
            capability="example.requirements",
            sources=sources(),
            candidate=bad_write,
            acceptance_id="REQ-4",
            lifecycle=LIFECYCLE,
        ),
        "may not write outside admitted canonical artifacts",
    )

    print(
        "semantic admission: PASS "
        "(direction + review + provenance + declared dependency topology + "
        "write boundary + derivation lifecycle baseline)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
