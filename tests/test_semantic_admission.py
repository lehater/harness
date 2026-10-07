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
from harness.assurance.semantic_acceptance import evaluate_artifact


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



def test_independently_losable_obligation_granularity() -> None:
    contract = {
        "authority": "HUMAN-INTERFACE-DESIGN",
        "owned_assertion_kinds": ["interaction-obligation"],
        "requires_assertion_authority": True,
        "requires_semantic_review": True,
        "required_semantic_review_checks": [
            "independent-obligation-granularity",
        ],
    }
    lossy_candidate = {
        "id": "CAPABILITY-SCOPE-INTERACTION",
        "capability": "example.capability-scope",
        "semantic_assertions": [
            {
                "id": "SCOPE-SUMMARY",
                "kind": "interaction-obligation",
                "subject": "capability-scope",
                "semantic_value": "Capability scope is explicit and reversible.",
                "decision_authority": "HUMAN-INTERFACE-DESIGN",
            },
            {
                "id": "SCOPE-VISIBLE",
                "kind": "interaction-obligation",
                "subject": "capability-scope-visible",
                "semantic_value": "Current Capability-derived scope is visible.",
                "decision_authority": "HUMAN-INTERFACE-DESIGN",
            },
            {
                "id": "SCOPE-CLEAR",
                "kind": "interaction-obligation",
                "subject": "capability-scope-clear",
                "semantic_value": "User can clear the current Capability-derived scope.",
                "decision_authority": "HUMAN-INTERFACE-DESIGN",
            },
        ],
        "semantic_review": {
            "status": "ACCEPTED",
            "checks": ["independent-obligation-granularity"],
            "independent_obligations": [
                {
                    "id": "apply-capability-scope",
                    "status": "COLLAPSED",
                    "assertions": ["SCOPE-SUMMARY"],
                    "rationale": (
                        "The user action for applying/selecting scope has no "
                        "dedicated semantic atom; only the reversible-scope "
                        "summary remains."
                    ),
                },
                {
                    "id": "visible-capability-scope",
                    "status": "ACCOUNTED",
                    "assertions": ["SCOPE-VISIBLE"],
                },
                {
                    "id": "clear-capability-scope",
                    "status": "ACCOUNTED",
                    "assertions": ["SCOPE-CLEAR"],
                },
            ],
        },
    }

    rejected = evaluate_artifact(contract, {"semantic_assertions": []}, lossy_candidate)
    assert rejected["status"] == "REJECTED", rejected
    assert any(
        finding.get("code") == "INDEPENDENT_OBLIGATION_COLLAPSED"
        and finding.get("obligation") == "apply-capability-scope"
        for finding in rejected["findings"]
    ), rejected

    cohesive_candidate = {
        "id": "COHESIVE-ASSERTION",
        "capability": "example.cohesive",
        "semantic_assertions": [
            {
                "id": "COHESIVE-ATOM",
                "kind": "interaction-obligation",
                "subject": "cohesive-state",
                "semantic_value": (
                    "The current mode indicator remains visible while the "
                    "mode is active."
                ),
                "decision_authority": "HUMAN-INTERFACE-DESIGN",
            }
        ],
        "semantic_review": {
            "status": "ACCEPTED",
            "checks": ["independent-obligation-granularity"],
            "independent_obligations": [
                {
                    "id": "visible-active-mode",
                    "status": "ACCOUNTED",
                    "assertions": ["COHESIVE-ATOM"],
                }
            ],
        },
    }
    accepted = evaluate_artifact(contract, {"semantic_assertions": []}, cohesive_candidate)
    assert accepted["status"] == "ACCEPTED", accepted



def _h3_role_contract() -> dict:
    return {
        "authority": "HUMAN-INTERFACE-DESIGN",
        "owned_assertion_kinds": ["interaction-obligation"],
        "requires_assertion_authority": True,
        "requires_semantic_review": True,
        "required_semantic_review_checks": ["interaction-role-coherence"],
    }


def _h3_role_candidate() -> dict:
    return {
        "semantic_assertions": [
            {
                "id": "COMPARE",
                "kind": "interaction-obligation",
                "subject": "compare-selection",
                "semantic_value": "User can mark an entity for comparison.",
                "decision_authority": "HUMAN-INTERFACE-DESIGN",
            },
            {
                "id": "ACTIVE",
                "kind": "interaction-obligation",
                "subject": "active-context",
                "semantic_value": "User can commit an entity as current context.",
                "decision_authority": "HUMAN-INTERFACE-DESIGN",
            },
        ],
        "interaction_roles": [
            {
                "id": "ROLE-COMPARE",
                "concept_ref": "ENTITY-X",
                "meaning": "Entity participates in comparison without becoming current.",
                "entry": "mark entity for comparison",
                "exit": "remove entity from comparison",
                "transitions": [
                    {"to": "ROLE-ACTIVE", "trigger": "commit as current context"}
                ],
                "side_effects": ["comparison set changes"],
                "forbidden_side_effects": ["current context does not change"],
                "observable_distinction": "comparison membership is distinguishable from current context",
            },
            {
                "id": "ROLE-ACTIVE",
                "concept_ref": "ENTITY-X",
                "meaning": "Entity is committed as current working context.",
                "entry": "commit entity as current context",
                "exit": "replace or clear current context",
                "transitions": [],
                "side_effects": ["current working context changes"],
                "forbidden_side_effects": [],
                "observable_distinction": "current context is distinguishable from comparison membership",
            },
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
                    "rationale": "The roles have materially different lifecycle and side effects.",
                }
            ],
        },
    }


def test_interaction_role_coherence_regressions() -> None:
    contract = _h3_role_contract()

    conflated = _h3_role_candidate()
    conflated["interaction_roles"] = [
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
    ]
    result = evaluate_artifact(contract, {"semantic_assertions": []}, conflated)
    assert result["status"] == "REJECTED", result
    assert {
        item.get("code") for item in result["findings"]
    } >= {"INTERACTION_ROLE_REQUIRED_ROLE_MISSING"}, result

    missing_forbidden = _h3_role_candidate()
    missing_forbidden["interaction_roles"][0]["forbidden_side_effects"] = []
    result = evaluate_artifact(
        contract,
        {"semantic_assertions": []},
        missing_forbidden,
    )
    assert result["status"] == "REJECTED", result
    assert any(
        item.get("code") == "INTERACTION_ROLE_REQUIRED_FACET_MISSING"
        and item.get("role") == "ROLE-COMPARE"
        and item.get("facet") == "forbidden_side_effects"
        for item in result["findings"]
    ), result

    missing_transition = _h3_role_candidate()
    missing_transition["interaction_roles"][0]["transitions"] = []
    result = evaluate_artifact(
        contract,
        {"semantic_assertions": []},
        missing_transition,
    )
    assert result["status"] == "REJECTED", result
    assert any(
        item.get("code") == "INTERACTION_ROLE_REQUIRED_TRANSITION_MISSING"
        for item in result["findings"]
    ), result

    same_role = {
        "semantic_assertions": [
            {
                "id": "INSPECT",
                "kind": "interaction-obligation",
                "subject": "entity-inspection",
                "semantic_value": "The entity can be inspected in multiple contexts.",
                "decision_authority": "HUMAN-INTERFACE-DESIGN",
            }
        ],
        "semantic_review": {
            "status": "ACCEPTED",
            "checks": ["interaction-role-coherence"],
            "interaction_role_requirements": [
                {
                    "concept": "ENTITY-X",
                    "status": "NOT_REQUIRED",
                    "rationale": "All contexts use the same lifecycle and side effects.",
                }
            ],
        },
    }
    accepted = evaluate_artifact(contract, {"semantic_assertions": []}, same_role)
    assert accepted["status"] == "ACCEPTED", accepted

    complete = evaluate_artifact(
        contract,
        {"semantic_assertions": []},
        _h3_role_candidate(),
    )
    assert complete["status"] == "ACCEPTED", complete


def _h3_observable_graph() -> dict:
    return {
        "version": 1,
        "kind": "harness-engineering-graph",
        "id": "OBSERVABLE-REALIZATION",
        "authorities": [
            {
                "id": "HUMAN-INTERFACE-DESIGN",
                "responsibility": "Own user-facing interaction semantics.",
                "boundary": {
                    "semantic_cohesion": "User-facing semantics.",
                    "independent_change": "Interaction and screen knowledge evolve independently.",
                    "public_contract": "Accepted user-facing semantics.",
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
        "consumers": [
            {
                "id": "FRONTEND",
                "purpose": "Consume the accepted screen contract.",
                "requires": ["example.screen"],
            }
        ],
        "terminal_capabilities": [],
    }


def _h3_observable_contract() -> dict:
    return {
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


def _h3_source(rows: list[tuple[str, str, str, str]]) -> dict:
    assertions = []
    review = []
    for assertion_id, category, status, semantic_value in rows:
        assertions.append(
            {
                "id": assertion_id,
                "kind": "interaction-obligation",
                "subject": assertion_id.lower(),
                "semantic_value": semantic_value,
                "decision_authority": "HUMAN-INTERFACE-DESIGN",
            }
        )
        item = {
            "id": f"OBS-{assertion_id}",
            "assertion": assertion_id,
            "category": category,
            "status": status,
        }
        if status != "REQUIRED":
            item["rationale"] = "Accepted semantics do not require a user-facing realization."
        review.append(item)
    return {
        "semantic_assertions": assertions,
        "semantic_review": {
            "status": "ACCEPTED",
            "checks": ["observable-realization-applicability"],
            "observable_realization_obligations": review,
        },
    }


def _h3_accept_judgement(
    *,
    source: dict,
    candidate: dict,
    evidence: dict,
    status: str = "ACCEPTED",
    findings: list | None = None,
) -> dict:
    graph = _h3_observable_graph()
    contract = _h3_observable_contract()
    probe = evaluate_derivation(
        graph=graph,
        contract=contract,
        source=source,
        candidate=candidate,
        evidence=evidence,
    )
    request = probe["semantic_judgement_request"]
    judged = copy.deepcopy(evidence)
    judged["semantic_judgement"] = {
        "version": 1,
        "kind": "harness-semantic-derivation-judgement",
        "reviewer_kind": "EVALUATOR",
        "request_id": request["request_id"],
        "status": status,
        "checks": ["observable-realization-correspondence"],
        "reviewed_links": [
            item["id"] for item in probe["links"] if item.get("id")
        ],
        "findings": findings or [],
    }
    return evaluate_derivation(
        graph=graph,
        contract=contract,
        source=source,
        candidate=candidate,
        evidence=judged,
    )


def test_observable_realization_regressions() -> None:
    source = _h3_source(
        [
            ("APPLY", "ACTION", "REQUIRED", "User can apply a scope."),
            ("CURRENT", "STATE", "REQUIRED", "Current scope is perceptible."),
            ("CLEAR", "ACTION", "REQUIRED", "User can clear scope."),
        ]
    )
    target = {
        "semantic_assertions": [
            {
                "id": "VIEW-CURRENT",
                "kind": "observable-realization",
                "subject": "current",
                "semantic_value": "Current scope is visibly indicated.",
                "observable_category": "STATE",
                "derived_from": ["CURRENT"],
            },
            {
                "id": "VIEW-CLEAR",
                "kind": "observable-realization",
                "subject": "clear",
                "semantic_value": "A user mechanism can clear scope.",
                "observable_category": "ACTION",
                "derived_from": ["CLEAR"],
            },
        ]
    }

    missing_action_evidence = {
        "version": 1,
        "kind": "harness-semantic-derivation-evidence",
        "source_capability": "example.interaction",
        "target_capability": "example.screen",
        "links": [
            {"id": "CURRENT", "sources": ["CURRENT"], "relation": "REALIZES", "targets": ["VIEW-CURRENT"]},
            {"id": "CLEAR", "sources": ["CLEAR"], "relation": "REALIZES", "targets": ["VIEW-CLEAR"]},
        ],
        "dispositions": [],
    }
    result = _h3_accept_judgement(
        source=source,
        candidate=target,
        evidence=missing_action_evidence,
    )
    assert result["status"] == "REJECTED", result
    assert any(
        item.get("code") == "UNDISPOSITIONED_SOURCE"
        and item.get("source") == "APPLY"
        for item in result["findings"]
    ), result

    reference_only = copy.deepcopy(missing_action_evidence)
    reference_only["links"].append(
        {
            "id": "APPLY-REFERENCE-ONLY",
            "sources": ["APPLY"],
            "relation": "REALIZES",
            "targets": ["VIEW-CURRENT"],
        }
    )
    result = _h3_accept_judgement(
        source=source,
        candidate=target,
        evidence=reference_only,
    )
    assert result["status"] == "REJECTED", result
    assert any(
        item.get("code") == "OBSERVABLE_REALIZATION_TARGET_MISSING"
        and item.get("source") == "APPLY"
        for item in result["findings"]
    ), result

    distinction_source = _h3_source(
        [
            (
                "COMPARE-VS-ACTIVE",
                "DISTINCTION",
                "REQUIRED",
                "Comparison selection is distinct from committed active context.",
            )
        ]
    )
    collapsed_target = {
        "semantic_assertions": [
            {
                "id": "GENERIC-SELECTION",
                "kind": "observable-realization",
                "subject": "selection",
                "semantic_value": "The entity is selected.",
                "observable_category": "DISTINCTION",
                "derived_from": ["COMPARE-VS-ACTIVE"],
            }
        ]
    }
    collapsed_evidence = {
        "version": 1,
        "kind": "harness-semantic-derivation-evidence",
        "source_capability": "example.interaction",
        "target_capability": "example.screen",
        "links": [
            {
                "id": "COLLAPSED-DISTINCTION",
                "sources": ["COMPARE-VS-ACTIVE"],
                "relation": "REALIZES",
                "targets": ["GENERIC-SELECTION"],
            }
        ],
        "dispositions": [],
    }
    result = _h3_accept_judgement(
        source=distinction_source,
        candidate=collapsed_target,
        evidence=collapsed_evidence,
        status="REJECTED",
        findings=["Generic selected state does not expose the material distinction."],
    )
    assert result["status"] == "REJECTED", result
    assert any(
        item.get("code") == "SEMANTIC_DERIVATION_JUDGEMENT_REJECTED"
        for item in result["findings"]
    ), result

    action_source = _h3_source(
        [("APPLY", "ACTION", "REQUIRED", "User can apply a scope.")]
    )
    state_substitute = {
        "semantic_assertions": [
            {
                "id": "VIEW-STATE",
                "kind": "observable-realization",
                "subject": "scope",
                "semantic_value": "Current scope is visible.",
                "observable_category": "STATE",
                "derived_from": ["APPLY"],
            }
        ]
    }
    substitute_evidence = {
        "version": 1,
        "kind": "harness-semantic-derivation-evidence",
        "source_capability": "example.interaction",
        "target_capability": "example.screen",
        "links": [
            {
                "id": "STATE-FOR-ACTION",
                "sources": ["APPLY"],
                "relation": "REALIZES",
                "targets": ["VIEW-STATE"],
            }
        ],
        "dispositions": [],
    }
    result = _h3_accept_judgement(
        source=action_source,
        candidate=state_substitute,
        evidence=substitute_evidence,
    )
    assert result["status"] == "REJECTED", result
    assert any(
        item.get("code") == "OBSERVABLE_REALIZATION_TARGET_MISSING"
        for item in result["findings"]
    ), result

    command_target = {
        "semantic_assertions": [
            {
                "id": "VIEW-APPLY",
                "kind": "observable-realization",
                "subject": "scope-apply",
                "semantic_value": (
                    "The user can invoke scope application through an accepted "
                    "interaction mechanism."
                ),
                "observable_category": "ACTION",
                "derived_from": ["APPLY"],
            }
        ]
    }
    command_evidence = {
        "version": 1,
        "kind": "harness-semantic-derivation-evidence",
        "source_capability": "example.interaction",
        "target_capability": "example.screen",
        "links": [
            {
                "id": "REALIZE-APPLY",
                "sources": ["APPLY"],
                "relation": "REALIZES",
                "targets": ["VIEW-APPLY"],
            }
        ],
        "dispositions": [],
    }
    accepted = _h3_accept_judgement(
        source=action_source,
        candidate=command_target,
        evidence=command_evidence,
    )
    assert accepted["status"] == "ACCEPTED", accepted

    non_ui_source = _h3_source(
        [
            (
                "SYSTEM-ONLY",
                "STATE",
                "NOT_APPLICABLE",
                "Internal system state has no user-facing realization obligation.",
            )
        ]
    )
    empty_candidate = {"semantic_assertions": []}
    empty_evidence = {
        "version": 1,
        "kind": "harness-semantic-derivation-evidence",
        "source_capability": "example.interaction",
        "target_capability": "example.screen",
        "links": [],
        "dispositions": [],
    }
    accepted = evaluate_derivation(
        graph=_h3_observable_graph(),
        contract=_h3_observable_contract(),
        source=non_ui_source,
        candidate=empty_candidate,
        evidence=empty_evidence,
    )
    assert accepted["status"] == "ACCEPTED", accepted
    assert accepted["dispositions"] == [
        {
            "source": "SYSTEM-ONLY",
            "status": "NOT_APPLICABLE",
            "rationale": "Accepted semantics do not require a user-facing realization.",
            "basis": "SOURCE_SEMANTIC_REVIEW",
        }
    ], accepted

def main() -> int:
    test_interaction_role_coherence_regressions()
    test_observable_realization_regressions()
    test_independently_losable_obligation_granularity()
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
    } <= set(contract_index["component-design"]["required_review_checks"])
    assert {
        "implementation-slices-explicit",
        "repository-realization-derived-from-accepted-boundaries",
    } <= set(contract_index["implementation-design"]["required_review_checks"])
    for knowledge_kind in (
        "user-journey-design",
        "interaction-design",
        "presentation-system-design",
        "screen-view-design",
    ):
        assert "independent-obligation-granularity" in set(
            contract_index[knowledge_kind]["required_review_checks"]
        ), knowledge_kind

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
