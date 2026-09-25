#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from harness import CoreError
from semantic_admission import admit_artifact, knowledge_contract_index


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


def main() -> int:
    registry = load("skills/artifact-skill-registry-v0.yaml")
    contracts = load(
        "spec/semantic-acceptance/knowledge-kind-contracts-v1.yaml"
    )
    contract_index = knowledge_contract_index(contracts)
    assert {
        "dependency-topology-explicit-where-material",
    } <= set(contract_index["system-architecture"]["required_review_checks"])
    assert {
        "implementation-facing-boundaries-complete-for-scope",
    } <= set(contract_index["component-design"]["required_review_checks"])
    assert {
        "implementation-slices-explicit",
        "repository-realization-derived-from-accepted-boundaries",
    } <= set(contract_index["implementation-design"]["required_review_checks"])

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
    )
    assert result["status"] == "ACCEPTED", result
    assert result["admission"]["allowed_source_authorities"] == [
        "DISCOVERY",
        "PRODUCT-REQUIREMENTS",
    ]
    assert result["lifecycle_assertion"]["accepted_prerequisites"] == {
        "example.user-needs": "NEEDS-1"
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

    print("semantic admission: PASS (direction + review + provenance + write boundary)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
