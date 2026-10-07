#!/usr/bin/env python3
from __future__ import annotations

import copy
from unittest.mock import patch
from pathlib import Path
import sys
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from harness.application.authority_context import build_authority_context
from harness.application.decision_explorer_request import build_decision_explorer_request
from harness.application.decision_preflight import evaluate_decision_preflight
from harness.decision.decision_execution_assurance import (
    effective_execution_assurance,
    evaluate_execution_assurance,
)
from harness.decision.decision_governance import axis_policies, decision_contract_index
from harness.assurance.semantic_acceptance import evaluate_artifact
from harness.application.semantic_admission import admit_artifact


GRAPH = {
    "version": 1,
    "kind": "harness-engineering-graph",
    "id": "DECISION-GOVERNANCE",
    "authorities": [
        {
            "id": "SYSTEM-ARCHITECTURE",
            "responsibility": "Own structural/runtime architecture decisions.",
            "boundary": {
                "semantic_cohesion": "System architecture decisions.",
                "independent_change": "Architecture can change independently.",
                "public_contract": "Accepted runtime structure.",
            },
            "produces": [
                {
                    "capability": "example.architecture",
                    "knowledge_kind": "system-architecture",
                    "requires": [],
                }
            ],
        }
    ],
    "consumers": [
        {
            "id": "ARCHITECTURE-BASELINE",
            "purpose": "Consume accepted architecture.",
            "requires": ["example.architecture"],
        }
    ],
    "terminal_capabilities": [],
}

MODEL = {"artifacts": [], "questions": []}


def load(path: str):
    return yaml.safe_load((ROOT / path).read_text(encoding="utf-8"))


def semantic_review():
    return {
        "status": "ACCEPTED",
        "checks": [
            "source-discipline",
            "authority-boundary",
            "no-invention",
            "architecture-not-product-requirement",
            "dependency-topology-explicit-where-material",
        ],
    }


def candidate(contract, *, runtime_disposition="DELEGATED"):
    axes = []
    for axis in contract["axes"]:
        decision_id = f"{axis}-choice"
        alternatives = [
            {"id": f"{axis}-a", "state": "VIABLE"},
            {
                "id": f"{axis}-b",
                "state": (
                    "VIABLE"
                    if axis == "runtime-boundaries"
                    else "REJECTED"
                ),
                **(
                    {}
                    if axis == "runtime-boundaries"
                    else {"rationale": "Accepted constraints eliminate option B."}
                ),
            },
        ]
        if axis == "runtime-boundaries":
            disposition = runtime_disposition
            selected = (
                f"{axis}-a"
                if disposition in {"DETERMINED", "DELEGATED"}
                else None
            )
        else:
            disposition = "DETERMINED"
            selected = f"{axis}-a"
        decision = {
            "id": decision_id,
            "owner_authority": "SYSTEM-ARCHITECTURE",
            "alternatives": alternatives,
            "disposition": disposition,
        }
        if selected is not None:
            decision["selected"] = selected
        if disposition == "ESCALATED":
            decision["question"] = "Q-RUNTIME-SHAPE"
        axes.append({"axis": axis, "decisions": [decision]})
    return {
        "id": "ARCHITECTURE",
        "capability": "example.architecture",
        "path": "docs/architecture.md",
        "semantic_assertions": [
            {
                "id": "ARCH-RUNTIME",
                "kind": "architecture-decision",
                "subject": "runtime-shape",
                "semantic_value": "Use one runtime boundary for the selected scope.",
                "decision_authority": "SYSTEM-ARCHITECTURE",
            }
        ],
        "semantic_review": semantic_review(),
        "decision_review": {"axes": axes},
    }


def exploration(contract, *, research_axis=None, research_evidence=True):
    sources = []
    if research_axis is not None and research_evidence:
        sources.append(
            {
                "id": "ARCH-SOURCE",
                "kind": "official",
                "reference": "authoritative architecture/runtime documentation",
            }
        )
    axes = []
    for axis, axis_contract in contract["axes"].items():
        dim = axis_contract["material_dimensions"][0]
        strategies = axis_contract["challenge_strategies"][:2]
        level = "RESEARCH" if axis == research_axis else "EXPLORE"
        item = {
            "axis": axis,
            "applicability": "APPLICABLE",
            "exploration_level": level,
            "probes": [
                {
                    "strategy": strategies[0],
                    "challenge": f"Challenge {axis} through {strategies[0]}.",
                    "alternatives": [f"{axis}-a", f"{axis}-b"],
                },
                {
                    "strategy": strategies[1],
                    "challenge": f"Challenge {axis} through {strategies[1]}.",
                    "alternatives": [f"{axis}-a", f"{axis}-b"],
                },
            ],
            "decision_points": [
                {
                    "id": f"{axis}-choice",
                    "alternatives": [
                        {
                            "id": f"{axis}-a",
                            "difference": f"Alternative A for {axis}.",
                            "material_effects": {dim: "A"},
                        },
                        {
                            "id": f"{axis}-b",
                            "difference": f"Alternative B for {axis}.",
                            "material_effects": {dim: "B"},
                        },
                    ],
                }
            ],
        }
        if axis == research_axis and research_evidence:
            item["research_sources"] = ["ARCH-SOURCE"]
        axes.append(item)
    return {
        "version": 1,
        "kind": "harness-decision-exploration",
        "capability": "example.architecture",
        "knowledge_kind": "system-architecture",
        "research_sources": sources,
        "axes": axes,
        "decision_space_review": {
            "status": "COMPLETE",
            "checks": [
                "mixed-decision-split",
                "missing-material-case-search",
                "impact-and-reversal-frontier-check",
                "accepted-constraint-cross-check",
                "authority-boundary-cross-check",
            ],
            "reviewed_decisions": [
                point["id"]
                for axis_item in axes
                for point in axis_item.get("decision_points", [])
            ],
            "open_gaps": [],
        },
    }


def bind_exploration(contract, policy, value, *, model=MODEL):
    context = build_authority_context(
        GRAPH,
        model,
        "SYSTEM-ARCHITECTURE",
        ["example.architecture"],
    )
    request = build_decision_explorer_request(
        capability="example.architecture",
        knowledge_kind="system-architecture",
        authority="SYSTEM-ARCHITECTURE",
        authority_context=context,
        contract=contract,
        axis_policies=axis_policies(contract, policy),
        prerequisite_baseline={},
        model=model,
    )
    result = copy.deepcopy(value)
    result["explorer_request_id"] = request["request_id"]
    return result


def preflight(*, contract, policy, candidate_value, exploration_value, model=MODEL):
    context = build_authority_context(
        GRAPH,
        model,
        "SYSTEM-ARCHITECTURE",
        ["example.architecture"],
    )
    request = build_decision_explorer_request(
        capability="example.architecture",
        knowledge_kind="system-architecture",
        authority="SYSTEM-ARCHITECTURE",
        authority_context=context,
        contract=contract,
        axis_policies=axis_policies(contract, policy),
        prerequisite_baseline={},
        model=model,
    )
    return evaluate_decision_preflight(
        contract=contract,
        policy=policy,
        axis_policies=axis_policies(contract, policy),
        explorer_request=request,
        capability="example.architecture",
        knowledge_kind="system-architecture",
        authority="SYSTEM-ARCHITECTURE",
        exploration_evidence=exploration_value,
        candidate=candidate_value,
        model=model,
    )


def admit(
    *,
    registry,
    semantic_contracts,
    decision_contracts,
    policy,
    candidate_value,
    exploration_value,
    model=MODEL,
    acceptance_id="ARCH",
):
    return admit_artifact(
        graph=GRAPH,
        model=model,
        skill_registry=registry,
        knowledge_contracts=semantic_contracts,
        decision_contracts=decision_contracts,
        decision_policy=policy,
        decision_exploration=exploration_value,
        capability="example.architecture",
        sources={"semantic_assertions": []},
        candidate=candidate_value,
        acceptance_id=acceptance_id,
    )


def codes(result):
    return {item["code"] for item in result.get("findings", [])}


def main() -> int:
    registry = load("skills/artifact-skill-registry-v0.yaml")
    semantic_contracts = load(
        "spec/semantic-acceptance/knowledge-kind-contracts-v1.yaml"
    )
    decision_contracts = load(
        "spec/decision-governance/knowledge-kind-decision-contracts-v1.yaml"
    )
    contracts = decision_contract_index(decision_contracts)
    contract = contracts["system-architecture"]
    presentation_contract = contracts["presentation-system-design"]
    assert set(presentation_contract["axes"]) == {
        "application-surface",
        "knowledge-representation",
        "information-density",
        "control-surface",
    }, presentation_contract
    surface_axis = presentation_contract["axes"]["application-surface"]
    assert set(surface_axis["material_dimensions"]) == {
        "surface-archetype",
        "viewport-ownership",
        "navigation-persistence",
        "overflow-ownership",
    }, surface_axis
    assert set(surface_axis["challenge_strategies"]) == {
        "document-vs-bounded-workspace",
        "workspace-vs-step-flow",
        "page-scroll-vs-region-overflow",
        "persistent-vs-contextual-navigation",
    }, surface_axis
    assert all(
        item["delegation_requires"] == "CONSERVATIVE"
        for item in presentation_contract["axes"].values()
    ), presentation_contract
    topology_contract = contracts["interface-topology-design"]
    assert topology_contract["required"] is True, topology_contract
    assert set(topology_contract["axes"]) == {"view-boundaries"}, topology_contract
    boundary_axis = topology_contract["axes"]["view-boundaries"]
    assert boundary_axis["delegation_requires"] == "CONSERVATIVE", boundary_axis
    assert set(boundary_axis["material_dimensions"]) == {
        "goal-continuity",
        "information-dependency",
        "working-state-continuity",
        "commit-recovery-boundary",
        "mode-authority-boundary",
        "independent-addressability",
    }, boundary_axis
    assert set(boundary_axis["challenge_strategies"]) == {
        "merge-vs-separate-view",
        "persistent-context-vs-navigation",
        "contextual-surface-vs-destination",
    }, boundary_axis

    # WP-H4 RED reproduction: both false-greens must be rejected by the
    # corrected Harness. The accepted baseline is expected to fail this assertion.
    h4_graph = {
        "version": 1,
        "kind": "harness-engineering-graph",
        "id": "H4-RED",
        "authorities": [
            {
                "id": "HUMAN-INTERFACE-DESIGN",
                "responsibility": "Own interface topology.",
                "boundary": {
                    "semantic_cohesion": "User-facing topology.",
                    "independent_change": "Topology changes independently.",
                    "public_contract": "Accepted view partition.",
                },
                "produces": [
                    {
                        "capability": "example.topology",
                        "knowledge_kind": "interface-topology-design",
                        "requires": [],
                    }
                ],
            }
        ],
        "consumers": [
            {
                "id": "TOPOLOGY-CONSUMER",
                "purpose": "Consume accepted topology.",
                "requires": ["example.topology"],
            }
        ],
        "terminal_capabilities": [],
    }
    h4_model = {"artifacts": [], "questions": []}
    h4_policy = {
        "version": 1,
        "kind": "harness-decision-policy",
        "knowledge_kinds": [
            {
                "knowledge_kind": "interface-topology-design",
                "autonomy": "CONSERVATIVE",
            }
        ],
    }
    h4_context = build_authority_context(
        h4_graph,
        h4_model,
        "HUMAN-INTERFACE-DESIGN",
        ["example.topology"],
    )
    h4_request = build_decision_explorer_request(
        capability="example.topology",
        knowledge_kind="interface-topology-design",
        authority="HUMAN-INTERFACE-DESIGN",
        authority_context=h4_context,
        contract=topology_contract,
        axis_policies=axis_policies(topology_contract, h4_policy),
        prerequisite_baseline={},
        model=h4_model,
    )
    h4_exploration = {
        "version": 1,
        "kind": "harness-decision-exploration",
        "capability": "example.topology",
        "knowledge_kind": "interface-topology-design",
        "explorer_request_id": h4_request["request_id"],
        "research_sources": [],
        "axes": [
            {
                "axis": "view-boundaries",
                "applicability": "APPLICABLE",
                "exploration_level": "EXPLORE",
                "probes": [
                    {
                        "strategy": "merge-vs-separate-view",
                        "challenge": "Challenge the overall topology.",
                        "alternatives": ["overall-a", "overall-b"],
                    },
                    {
                        "strategy": "persistent-context-vs-navigation",
                        "challenge": "Challenge global context continuity.",
                        "alternatives": ["overall-a", "overall-b"],
                    },
                ],
                "decision_points": [
                    {
                        "id": "overall-view-structure",
                        "alternatives": [
                            {
                                "id": "overall-a",
                                "difference": "Use separate task destinations.",
                                "material_effects": {"goal-continuity": "task-oriented"},
                            },
                            {
                                "id": "overall-b",
                                "difference": "Use one workspace.",
                                "material_effects": {"goal-continuity": "workspace-oriented"},
                            },
                        ],
                    }
                ],
            }
        ],
        "decision_space_review": {
            "status": "COMPLETE",
            "checks": [
                "mixed-decision-split",
                "missing-material-case-search",
                "impact-and-reversal-frontier-check",
                "accepted-constraint-cross-check",
                "authority-boundary-cross-check",
            ],
            "reviewed_decisions": ["overall-view-structure"],
            "open_gaps": [],
        },
    }
    h4_candidate = {
        "id": "H4-TOPOLOGY",
        "capability": "example.topology",
        "path": "docs/interface/h4-topology.yaml",
        "semantic_assertions": [],
        "semantic_review": {
            "status": "ACCEPTED",
            "checks": [
                "source-discipline",
                "authority-boundary",
                "no-invention",
                "topology-not-screen-composition",
            ],
            "view_boundary_requirements": [
                {
                    "id": "BOUNDARY-A-B",
                    "participants": ["VIEW-A", "VIEW-B"],
                    "materiality": "MATERIAL",
                    "contestability": "CONTESTABLE",
                    "outcome": "SEPARATE",
                    "rationale_bases": [
                        {
                            "id": "USER-GOAL",
                            "classification": "USER_FACING",
                            "rationale": "Material user-facing distinction.",
                        }
                    ],
                    "decision_refs": ["overall-view-structure"],
                }
            ],
        },
        "decision_review": {
            "axes": [
                {
                    "axis": "view-boundaries",
                    "decisions": [
                        {
                            "id": "overall-view-structure",
                            "owner_authority": "HUMAN-INTERFACE-DESIGN",
                            "alternatives": [
                                {"id": "overall-a", "state": "VIABLE"},
                                {
                                    "id": "overall-b",
                                    "state": "REJECTED",
                                    "rationale": "Global constraints eliminate B.",
                                },
                            ],
                            "disposition": "DETERMINED",
                            "selected": "overall-a",
                        }
                    ],
                }
            ]
        },
    }
    h003_baseline = evaluate_decision_preflight(
        contract=topology_contract,
        policy=h4_policy,
        axis_policies=axis_policies(topology_contract, h4_policy),
        explorer_request=h4_request,
        capability="example.topology",
        knowledge_kind="interface-topology-design",
        authority="HUMAN-INTERFACE-DESIGN",
        exploration_evidence=h4_exploration,
        candidate=h4_candidate,
        model=h4_model,
    )

    h008_contract = {
        "authority": "HUMAN-INTERFACE-DESIGN",
        "requires_source_authority": True,
        "requires_assertion_authority": True,
        "requires_semantic_review": True,
        "required_semantic_review_checks": [
            "source-discipline",
            "authority-boundary",
            "no-invention",
            "topology-not-screen-composition",
        ],
    }
    h008_candidate = {
        "id": "H4-RESPONSIBILITY-SHAPED",
        "capability": "example.topology",
        "semantic_assertions": [],
        "semantic_review": {
            "status": "ACCEPTED",
            "checks": h008_contract["required_semantic_review_checks"],
            "view_boundary_requirements": [
                {
                    "id": "BOUNDARY-A-B",
                    "participants": ["VIEW-A", "VIEW-B"],
                    "materiality": "MATERIAL",
                    "contestability": "CONTESTABLE",
                    "outcome": "SEPARATE",
                    "rationale_bases": [
                        {
                            "id": "RESPONSIBILITY",
                            "classification": "UPSTREAM_RESPONSIBILITY",
                            "rationale": "Different tasks and application capabilities.",
                        }
                    ],
                    "decision_refs": ["overall-view-structure"],
                }
            ],
        },
    }
    h008_baseline = evaluate_artifact(
        h008_contract,
        {"semantic_assertions": []},
        h008_candidate,
    )
    assert (
        h003_baseline["status"] == "REJECTED"
        and h008_baseline["status"] == "REJECTED"
    ), {"HARNESS-003": h003_baseline, "HARNESS-008": h008_baseline}

    screen_contract = contracts["screen-view-design"]
    assert set(screen_contract["axes"]) == {
        "view-composition",
        "detail-edit-placement",
        "responsive-composition",
    }, screen_contract
    assert all(
        item["delegation_requires"] == "CONSERVATIVE"
        for item in screen_contract["axes"].values()
    ), screen_contract
    assert set(screen_contract["axes"]["view-composition"]["challenge_strategies"]) == {
        "region-vs-pane",
        "co-locate-vs-disclose",
        "region-priority-shift",
    }, screen_contract
    assert set(screen_contract["axes"]["detail-edit-placement"]["challenge_strategies"]) == {
        "inline-vs-overlay",
        "local-detail-vs-disclosure",
        "context-preservation-perturbation",
    }, screen_contract
    component_contract = contracts["component-design"]
    assert set(component_contract["axes"]) == {
        "responsibility-boundaries",
        "provider-seams",
        "state-ownership",
    }, component_contract
    assert all(
        item["delegation_requires"] == "CONSERVATIVE"
        for item in component_contract["axes"].values()
    ), component_contract

    process_contract = contracts["application-process-design"]
    assert process_contract["required"] is True, process_contract
    assert set(process_contract["axes"]) == {
        "occurrence-boundary",
        "composition",
        "continuation",
        "completion-recovery",
    }, process_contract
    assert process_contract["axes"]["occurrence-boundary"]["delegation_requires"] == "BROAD"
    assert process_contract["axes"]["composition"]["delegation_requires"] == "BROAD"
    assert process_contract["axes"]["continuation"]["delegation_requires"] == "MAXIMUM"
    assert process_contract["axes"]["completion-recovery"]["delegation_requires"] == "MAXIMUM"
    assert all(
        item["minimum_exploration"] == "EXPLORE"
        for item in process_contract["axes"].values()
    ), process_contract

    # A global project decision policy must not accidentally govern knowledge
    # kinds that have no decision contract.
    not_required_execution = evaluate_execution_assurance(
        policy={"version": 1, "kind": "harness-decision-policy"},
        knowledge_kind="product-requirements",
        explorer_request=None,
        exploration_evaluation={"status": "NOT_REQUIRED"},
    )
    assert not_required_execution["status"] == "NOT_REQUIRED", not_required_execution

    # Original consumer failure remains: semantic review alone accepts the first
    # satisfactory architecture choice.
    old_candidate = candidate(contract)
    old_candidate.pop("decision_review")
    old_boundary = evaluate_artifact(
        {
            "authority": "SYSTEM-ARCHITECTURE",
            "requires_source_authority": True,
            "requires_assertion_authority": True,
            "requires_semantic_review": True,
            "required_semantic_review_checks": semantic_review()["checks"],
        },
        {"semantic_assertions": []},
        old_candidate,
    )
    assert old_boundary["status"] == "ACCEPTED", old_boundary

    strict_policy = {"version": 1, "kind": "harness-decision-policy"}
    broad_policy = {
        "version": 1,
        "kind": "harness-decision-policy",
        "knowledge_kinds": [
            {"knowledge_kind": "system-architecture", "autonomy": "BROAD"}
        ],
    }
    sparse_unrelated_policy = {
        "version": 1,
        "kind": "harness-decision-policy",
        "knowledge_kinds": [
            {"knowledge_kind": "presentation-system-design", "autonomy": "CONSERVATIVE"}
        ],
    }
    assert axis_policies(contract, sparse_unrelated_policy) is None
    assert (
        effective_execution_assurance(
            sparse_unrelated_policy,
            "product-requirements",
        )
        is None
    )
    sparse_preflight = evaluate_decision_preflight(
        contract=contract,
        policy=sparse_unrelated_policy,
        axis_policies=axis_policies(contract, sparse_unrelated_policy),
        explorer_request=None,
        capability="example.architecture",
        knowledge_kind="system-architecture",
        authority="SYSTEM-ARCHITECTURE",
        exploration_evidence=None,
        candidate=candidate(contract),
        model=MODEL,
    )
    assert sparse_preflight["status"] == "NOT_REQUIRED", sparse_preflight
    assert all(
        sparse_preflight[key]["status"] == "NOT_REQUIRED"
        for key in (
            "decision_exploration",
            "decision_execution_assurance",
            "decision_governance",
        )
    ), sparse_preflight
    global_defaults_policy = {
        "version": 1,
        "kind": "harness-decision-policy",
        "defaults": {"autonomy": "CONSERVATIVE"},
        "knowledge_kinds": [
            {"knowledge_kind": "presentation-system-design"}
        ],
    }
    assert axis_policies(contract, global_defaults_policy) is not None
    assert (
        effective_execution_assurance(
            global_defaults_policy,
            "product-requirements",
        )
        == "REQUEST_BOUND"
    )

    attested_policy = {
        "version": 1,
        "kind": "harness-decision-policy",
        "defaults": {"execution_assurance": "ATTESTED_ISOLATED"},
        "knowledge_kinds": [
            {"knowledge_kind": "system-architecture", "autonomy": "BROAD"}
        ],
    }

    # A schema-blind-looking exploration document is no longer sufficient by
    # itself. It must be bound to the candidate-free Explorer Request derived by
    # Harness from the current canonical context.
    unbound = exploration(contract)
    result = admit(
        registry=registry,
        semantic_contracts=semantic_contracts,
        decision_contracts=decision_contracts,
        policy=broad_policy,
        candidate_value=candidate(contract),
        exploration_value=unbound,
        acceptance_id="ARCH-REQUEST-0",
    )
    assert result["status"] == "REJECTED", result
    assert "DECISION_EXPLORER_REQUEST_MISMATCH" in codes(result), result

    # Policy activates the new boundary and exploration is a separate required
    # input, not post-hoc candidate prose.
    result = admit(
        registry=registry,
        semantic_contracts=semantic_contracts,
        decision_contracts=decision_contracts,
        policy=strict_policy,
        candidate_value=candidate(contract),
        exploration_value=None,
        acceptance_id="ARCH-1",
    )
    assert result["status"] == "REJECTED", result
    assert "DECISION_EXPLORATION_REQUIRED" in codes(result), result

    # The old lazy escape hatch no longer exists. An APPLICABLE axis without a
    # discovered decision point cannot be accepted.
    lazy = bind_exploration(contract, broad_policy, exploration(contract))
    lazy["axes"][0]["decision_points"] = []
    lazy["axes"][0]["probes"][0]["alternatives"] = []
    lazy["axes"][0]["probes"][1]["alternatives"] = []
    result = admit(
        registry=registry,
        semantic_contracts=semantic_contracts,
        decision_contracts=decision_contracts,
        policy=broad_policy,
        candidate_value=candidate(contract),
        exploration_value=lazy,
        acceptance_id="ARCH-2",
    )
    assert result["status"] == "REJECTED", result
    assert "DECISION_POINT_DISCOVERY_REQUIRED" in codes(result), result

    # Option formation is not complete until the discovered decision space is
    # explicitly challenged for mixed concerns, missing cases, accepted
    # constraints and Authority ownership.
    unreviewed = bind_exploration(contract, broad_policy, exploration(contract))
    unreviewed.pop("decision_space_review")
    result = admit(
        registry=registry,
        semantic_contracts=semantic_contracts,
        decision_contracts=decision_contracts,
        policy=broad_policy,
        candidate_value=candidate(contract),
        exploration_value=unreviewed,
        acceptance_id="ARCH-SPACE-REVIEW",
    )
    assert result["status"] == "REJECTED", result
    assert "DECISION_SPACE_REVIEW_REQUIRED" in codes(result), result

    # The frontier completeness check is mandatory even when all already-discovered
    # decision points were reviewed.
    no_frontier = bind_exploration(contract, broad_policy, exploration(contract))
    no_frontier["decision_space_review"]["checks"].remove(
        "impact-and-reversal-frontier-check"
    )
    result = admit(
        registry=registry,
        semantic_contracts=semantic_contracts,
        decision_contracts=decision_contracts,
        policy=broad_policy,
        candidate_value=candidate(contract),
        exploration_value=no_frontier,
        acceptance_id="ARCH-FRONTIER-REVIEW",
    )
    assert result["status"] == "REJECTED", result
    assert "DECISION_SPACE_REVIEW_CHECKS_MISSING" in codes(result), result

    # Exploration must remain pre-choice/blind. A selected/preferred marker
    # contaminates the evidence and is rejected before governance.
    contaminated = bind_exploration(contract, broad_policy, exploration(contract))
    contaminated["axes"][0]["selected"] = "runtime-boundaries-a"
    result = admit(
        registry=registry,
        semantic_contracts=semantic_contracts,
        decision_contracts=decision_contracts,
        policy=broad_policy,
        candidate_value=candidate(contract),
        exploration_value=contaminated,
        acceptance_id="ARCH-3",
    )
    assert result["status"] == "REJECTED", result
    assert "DECISION_EXPLORATION_NOT_BLIND" in codes(result), result

    # Two superficially different alternatives with identical material effects
    # are not accepted as search diversity.
    fake_diversity = bind_exploration(contract, broad_policy, exploration(contract))
    point = fake_diversity["axes"][0]["decision_points"][0]
    point["alternatives"][1]["material_effects"] = copy.deepcopy(
        point["alternatives"][0]["material_effects"]
    )
    result = admit(
        registry=registry,
        semantic_contracts=semantic_contracts,
        decision_contracts=decision_contracts,
        policy=broad_policy,
        candidate_value=candidate(contract),
        exploration_value=fake_diversity,
        acceptance_id="ARCH-4",
    )
    assert result["status"] == "REJECTED", result
    assert "DECISION_ALTERNATIVES_NOT_MATERIALLY_DISTINCT" in codes(result), result

    # With accepted exploration, autonomy remains an independent later decision.
    valid_exploration = bind_exploration(contract, broad_policy, exploration(contract))

    # Cheap preflight catches governance failures without running artifact
    # semantic evaluation or requiring an acceptance identity.
    not_determined = preflight(
        contract=contract,
        policy=broad_policy,
        candidate_value=candidate(contract, runtime_disposition="DETERMINED"),
        exploration_value=valid_exploration,
    )
    assert not_determined["status"] == "REJECTED", not_determined
    assert "DECISION_NOT_DETERMINED" in codes(not_determined), not_determined
    assert "acceptance_id" not in not_determined, not_determined

    # Admission must short-circuit on deterministic decision rejection instead
    # of running the more expensive artifact semantic evaluation first.
    with patch(
        "harness.application.semantic_admission.evaluate_artifact",
        side_effect=AssertionError(
            "artifact semantics must not run before rejected decision preflight"
        ),
    ):
        early_rejection = admit(
            registry=registry,
            semantic_contracts=semantic_contracts,
            decision_contracts=decision_contracts,
            policy=broad_policy,
            candidate_value=candidate(
                contract,
                runtime_disposition="DETERMINED",
            ),
            exploration_value=valid_exploration,
            acceptance_id="ARCH-PREFLIGHT-FIRST",
        )
    assert early_rejection["status"] == "REJECTED", early_rejection
    assert "DECISION_NOT_DETERMINED" in codes(early_rejection), early_rejection

    conservative_exploration = bind_exploration(
        contract,
        strict_policy,
        exploration(contract),
    )
    autonomy_blocked = preflight(
        contract=contract,
        policy=strict_policy,
        candidate_value=candidate(contract),
        exploration_value=conservative_exploration,
    )
    assert autonomy_blocked["status"] == "REJECTED", autonomy_blocked
    assert "DECISION_AUTONOMY_EXCEEDED" in codes(autonomy_blocked), autonomy_blocked

    accepted_preflight = preflight(
        contract=contract,
        policy=broad_policy,
        candidate_value=candidate(contract),
        exploration_value=valid_exploration,
    )
    assert accepted_preflight["status"] == "ACCEPTED", accepted_preflight

    result = admit(
        registry=registry,
        semantic_contracts=semantic_contracts,
        decision_contracts=decision_contracts,
        policy=broad_policy,
        candidate_value=candidate(contract),
        exploration_value=valid_exploration,
        acceptance_id="ARCH-5",
    )
    assert result["status"] == "ACCEPTED", result
    assert (
        result["decision_execution_assurance"]["status"] == "ACCEPTED"
    ), result

    # A project may require stronger runtime assurance, but workload-authored
    # claims cannot satisfy it. Harness fails closed until a trusted external
    # executor/verifier can authenticate isolated execution provenance.
    attested_exploration = bind_exploration(
        contract,
        attested_policy,
        exploration(contract),
    )
    result = admit(
        registry=registry,
        semantic_contracts=semantic_contracts,
        decision_contracts=decision_contracts,
        policy=attested_policy,
        candidate_value=candidate(contract),
        exploration_value=attested_exploration,
        acceptance_id="ARCH-ATTESTED-UNAVAILABLE",
    )
    assert result["status"] == "REJECTED", result
    assert "DECISION_TRUSTED_EXECUTION_VERIFIER_REQUIRED" in codes(result), result

    result = admit(
        registry=registry,
        semantic_contracts=semantic_contracts,
        decision_contracts=decision_contracts,
        policy=strict_policy,
        candidate_value=candidate(contract),
        exploration_value=valid_exploration,
        acceptance_id="ARCH-6",
    )
    assert result["status"] == "REJECTED", result
    assert "DECISION_AUTONOMY_EXCEEDED" in codes(result), result

    # Non-delegated choice can still use the existing Core Question mechanism.
    question_model = {
        "artifacts": [],
        "questions": [
            {
                "id": "Q-RUNTIME-SHAPE",
                "authority": "SYSTEM-ARCHITECTURE",
                "text": "Which viable runtime boundary should be selected?",
                "blocks_capabilities": ["example.architecture"],
            }
        ],
    }
    result = admit(
        registry=registry,
        semantic_contracts=semantic_contracts,
        decision_contracts=decision_contracts,
        policy=strict_policy,
        candidate_value=candidate(contract, runtime_disposition="ESCALATED"),
        exploration_value=valid_exploration,
        model=question_model,
        acceptance_id="ARCH-7",
    )
    assert result["status"] == "ACCEPTED", result

    # Research depth belongs to exploration, not governance.
    research_policy = {
        "version": 1,
        "kind": "harness-decision-policy",
        "knowledge_kinds": [
            {
                "knowledge_kind": "system-architecture",
                "autonomy": "BROAD",
                "axes": [
                    {"axis": "runtime-boundaries", "exploration": "RESEARCH"}
                ],
            }
        ],
    }
    result = admit(
        registry=registry,
        semantic_contracts=semantic_contracts,
        decision_contracts=decision_contracts,
        policy=research_policy,
        candidate_value=candidate(contract),
        exploration_value=bind_exploration(
            contract,
            research_policy,
            exploration(
                contract,
                research_axis="runtime-boundaries",
                research_evidence=False,
            ),
        ),
        acceptance_id="ARCH-8",
    )
    assert result["status"] == "REJECTED", result
    assert "DECISION_RESEARCH_EVIDENCE_MISSING" in codes(result), result

    result = admit(
        registry=registry,
        semantic_contracts=semantic_contracts,
        decision_contracts=decision_contracts,
        policy=research_policy,
        candidate_value=candidate(contract),
        exploration_value=bind_exploration(
            contract,
            research_policy,
            exploration(
                contract,
                research_axis="runtime-boundaries",
                research_evidence=True,
            ),
        ),
        acceptance_id="ARCH-9",
    )
    assert result["status"] == "ACCEPTED", result

    print(
        "decision governance v2: PASS "
        "(pre-choice exploration + material diversity + autonomy + escalation)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
