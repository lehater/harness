#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from harness.assurance.semantic_acceptance import evaluate_artifact
from harness.assurance.semantic_derivation import evaluate_derivation


def test_harness_004_rejects_material_role_conflation() -> None:
    contract = {
        "authority": "HUMAN-INTERFACE-DESIGN",
        "owned_assertion_kinds": ["interaction-obligation"],
        "requires_assertion_authority": True,
        "requires_semantic_review": True,
        "required_semantic_review_checks": ["interaction-role-coherence"],
    }
    candidate = {
        "semantic_assertions": [
            {
                "id": "SELECTED",
                "kind": "interaction-obligation",
                "subject": "entity-selection",
                "semantic_value": "The entity can be selected.",
                "decision_authority": "HUMAN-INTERFACE-DESIGN",
            }
        ],
        "interaction_roles": [
            {
                "id": "ROLE-SELECTED",
                "concept_ref": "ENTITY-X",
                "meaning": "Generic selected state.",
                "entry": "select entity",
                "exit": "clear selection",
                "transitions": [],
                "side_effects": [],
                "forbidden_side_effects": [],
                "observable_distinction": "selected",
            }
        ],
        "semantic_review": {
            "status": "ACCEPTED",
            "checks": ["interaction-role-coherence"],
            "interaction_role_requirements": [
                {
                    "concept": "ENTITY-X",
                    "status": "REQUIRED",
                    "roles": ["ROLE-COMPARE", "ROLE-ACTIVE"],
                    "required_role_facets": {
                        "ROLE-COMPARE": ["forbidden_side_effects"],
                        "ROLE-ACTIVE": ["side_effects"],
                    },
                    "required_transitions": [
                        {"from": "ROLE-COMPARE", "to": "ROLE-ACTIVE"}
                    ],
                    "rationale": (
                        "The roles have materially different lifecycle and side effects."
                    ),
                }
            ],
        },
    }

    result = evaluate_artifact(contract, {"semantic_assertions": []}, candidate)
    assert result["status"] == "REJECTED", (
        "HARNESS-004 false-green: material roles were conflated but admission "
        f"returned {result['status']}: {result}"
    )


def _observable_graph() -> dict:
    return {
        "version": 1,
        "kind": "harness-engineering-graph",
        "id": "OBSERVABLE-REALIZATION",
        "authorities": [
            {
                "id": "HUMAN-INTERFACE-DESIGN",
                "responsibility": "Own interaction and screen semantics.",
                "boundary": {
                    "semantic_cohesion": "User-facing semantics.",
                    "independent_change": "Interaction and composition evolve independently.",
                    "public_contract": "Accepted user-facing behavior.",
                },
                "produces": [
                    {
                        "capability": "example.interaction",
                        "knowledge_kind": "interaction-design",
                        "requires": [],
                    },
                    {
                        "capability": "example.screen",
                        "knowledge_kind": "screen-view-design",
                        "requires": ["example.interaction"],
                    },
                ],
            }
        ],
        "consumers": [],
        "terminal_capabilities": [],
    }


def test_harness_005_rejects_reference_only_observable_realization() -> None:
    source = {
        "semantic_assertions": [
            {
                "id": "APPLY-SCOPE",
                "kind": "interaction-obligation",
                "subject": "scope-apply",
                "semantic_value": "User can apply a scope.",
                "decision_authority": "HUMAN-INTERFACE-DESIGN",
            },
            {
                "id": "CURRENT-SCOPE",
                "kind": "interaction-obligation",
                "subject": "scope-current",
                "semantic_value": "Current scope is perceptible.",
                "decision_authority": "HUMAN-INTERFACE-DESIGN",
            },
            {
                "id": "CLEAR-SCOPE",
                "kind": "interaction-obligation",
                "subject": "scope-clear",
                "semantic_value": "User can clear the scope.",
                "decision_authority": "HUMAN-INTERFACE-DESIGN",
            },
        ],
        "semantic_review": {
            "status": "ACCEPTED",
            "checks": ["observable-realization-applicability"],
            "observable_realization_obligations": [
                {
                    "id": "OBS-APPLY",
                    "assertion": "APPLY-SCOPE",
                    "category": "ACTION",
                    "status": "REQUIRED",
                },
                {
                    "id": "OBS-CURRENT",
                    "assertion": "CURRENT-SCOPE",
                    "category": "STATE",
                    "status": "REQUIRED",
                },
                {
                    "id": "OBS-CLEAR",
                    "assertion": "CLEAR-SCOPE",
                    "category": "ACTION",
                    "status": "REQUIRED",
                },
            ],
        },
    }
    candidate = {
        "semantic_assertions": [
            {
                "id": "VIEW-CURRENT",
                "kind": "observable-realization",
                "subject": "scope-current",
                "semantic_value": "The current scope is visibly indicated.",
                "observable_category": "STATE",
                "derived_from": ["CURRENT-SCOPE"],
                "decision_authority": "HUMAN-INTERFACE-DESIGN",
            },
            {
                "id": "VIEW-CLEAR",
                "kind": "observable-realization",
                "subject": "scope-clear",
                "semantic_value": "The user has an available mechanism to clear scope.",
                "observable_category": "ACTION",
                "derived_from": ["CLEAR-SCOPE"],
                "decision_authority": "HUMAN-INTERFACE-DESIGN",
            },
        ]
    }
    contract = {
        "version": 1,
        "kind": "harness-semantic-derivation-contract",
        "source_capability": "example.interaction",
        "target_capability": "example.screen",
        "obligations": [
            {
                "id": "observable-interaction",
                "source_kind": "interaction-obligation",
                "observable_realization": True,
            }
        ],
    }
    evidence = {
        "version": 1,
        "kind": "harness-semantic-derivation-evidence",
        "source_capability": "example.interaction",
        "target_capability": "example.screen",
        "links": [
            {
                "id": "REALIZE-CURRENT",
                "sources": ["CURRENT-SCOPE"],
                "relation": "REALIZES",
                "targets": ["VIEW-CURRENT"],
            },
            {
                "id": "REALIZE-CLEAR",
                "sources": ["CLEAR-SCOPE"],
                "relation": "REALIZES",
                "targets": ["VIEW-CLEAR"],
            },
            {
                "id": "REFERENCE-APPLY-AS-CURRENT",
                "sources": ["APPLY-SCOPE"],
                "relation": "REALIZES",
                "targets": ["VIEW-CURRENT"],
            },
        ],
        "dispositions": [],
    }

    result = evaluate_derivation(
        graph=_observable_graph(),
        contract=contract,
        source=source,
        candidate=candidate,
        evidence=evidence,
    )
    assert result["status"] == "REJECTED", (
        "HARNESS-005 false-green: APPLY-SCOPE had only a reference to the "
        f"current-state realization but derivation returned {result['status']}: {result}"
    )


def main() -> int:
    failures: list[str] = []
    for defect_id, test in [
        ("HARNESS-004", test_harness_004_rejects_material_role_conflation),
        ("HARNESS-005", test_harness_005_rejects_reference_only_observable_realization),
    ]:
        try:
            test()
        except AssertionError as exc:
            failures.append(f"{defect_id}: {exc}")

    if failures:
        raise AssertionError("\n".join(failures))

    print("WP-H3 regressions: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
