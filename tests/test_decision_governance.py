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
        "representation-selection",
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
    assert boundary_axis["subject_scope"] == "view-boundary", boundary_axis
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

    # WP-H4 / HARNESS-003 RED: a broad topology decision can currently satisfy
    # Decision Governance while a concrete materially contestable boundary has
    # no boundary-local decision point or challenge evidence.
    topology_graph = {
        "version": 1,
        "kind": "harness-engineering-graph",
        "id": "H4-TOPOLOGY",
        "authorities": [
            {
                "id": "HUMAN-INTERFACE-DESIGN",
                "responsibility": "Own user-facing interface topology.",
                "boundary": {
                    "semantic_cohesion": "User-facing view boundaries.",
                    "independent_change": "Topology can change independently.",
                    "public_contract": "Accepted view partition and navigation.",
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
                "purpose": "Consume accepted interface topology.",
                "requires": ["example.topology"],
            }
        ],
        "terminal_capabilities": [],
    }
    topology_model = {"artifacts": [], "questions": []}
    topology_policy = {
        "version": 1,
        "kind": "harness-decision-policy",
        "knowledge_kinds": [
            {
                "knowledge_kind": "interface-topology-design",
                "autonomy": "CONSERVATIVE",
            }
        ],
    }
    topology_context = build_authority_context(
        topology_graph,
        topology_model,
        "HUMAN-INTERFACE-DESIGN",
        ["example.topology"],
    )
    topology_request = build_decision_explorer_request(
        capability="example.topology",
        knowledge_kind="interface-topology-design",
        authority="HUMAN-INTERFACE-DESIGN",
        authority_context=topology_context,
        contract=topology_contract,
        axis_policies=axis_policies(topology_contract, topology_policy),
        prerequisite_baseline={},
        model=topology_model,
    )
    broad_topology_exploration = {
        "version": 1,
        "kind": "harness-decision-exploration",
        "capability": "example.topology",
        "knowledge_kind": "interface-topology-design",
        "explorer_request_id": topology_request["request_id"],
        "research_sources": [],
        "axes": [
            {
                "axis": "view-boundaries",
                "applicability": "APPLICABLE",
                "exploration_level": "EXPLORE",
                "probes": [
                    {
                        "strategy": "merge-vs-separate-view",
                        "challenge": "Challenge the overall view structure.",
                        "alternatives": ["overall-a", "overall-b"],
                    },
                    {
                        "strategy": "persistent-context-vs-navigation",
                        "challenge": "Challenge context persistence globally.",
                        "alternatives": ["overall-a", "overall-b"],
                    },
                ],
                "decision_points": [
                    {
                        "id": "overall-view-structure",
                        "alternatives": [
                            {
                                "id": "overall-a",
                                "difference": "Use task-oriented destinations.",
                                "material_effects": {
                                    "goal-continuity": "task-oriented",
                                },
                            },
                            {
                                "id": "overall-b",
                                "difference": "Use one broad workspace.",
                                "material_effects": {
                                    "goal-continuity": "workspace-oriented",
                                },
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
    broad_topology_candidate = {
        "id": "TOPOLOGY-H4-003",
        "capability": "example.topology",
        "path": "docs/interface/topology-h4-003.yaml",
        "semantic_assertions": [],
        "semantic_review": {
            "status": "ACCEPTED",
            "checks": [
                "source-discipline",
                "authority-boundary",
                "no-invention",
                "topology-not-screen-composition",
                "view-boundary-semantics",
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
                            "id": "GOAL-BOUNDARY",
                            "classification": "USER_FACING",
                            "rationale": "The boundary is materially user-facing.",
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
                                    "rationale": "Accepted constraints eliminate the broad workspace.",
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
    h003_red = evaluate_decision_preflight(
        contract=topology_contract,
        policy=topology_policy,
        axis_policies=axis_policies(topology_contract, topology_policy),
        explorer_request=topology_request,
        capability="example.topology",
        knowledge_kind="interface-topology-design",
        authority="HUMAN-INTERFACE-DESIGN",
        exploration_evidence=broad_topology_exploration,
        candidate=broad_topology_candidate,
        model=topology_model,
    )
    assert h003_red["status"] == "REJECTED", h003_red
    assert "VIEW_BOUNDARY_DECISION_COVERAGE_MISSING" in codes(h003_red), h003_red

    # WP-H4 / HARNESS-008 RED: task/application responsibility separation can
    # currently masquerade as sufficient user-facing view-boundary rationale.
    semantic_defaults = semantic_contracts.get("defaults", {}) or {}
    topology_semantic_item = next(
        item
        for item in semantic_contracts["contracts"]
        if item["knowledge_kind"] == "interface-topology-design"
    )
    topology_semantic_contract = {
        "authority": "HUMAN-INTERFACE-DESIGN",
        "requires_source_authority": True,
        "requires_assertion_authority": True,
        "requires_semantic_review": True,
        "required_semantic_review_checks": sorted(
            set(semantic_defaults.get("required_review_checks", []) or [])
            | set(topology_semantic_item.get("required_review_checks", []) or [])
        ),
    }
    responsibility_shaped = {
        "id": "TOPOLOGY-H4-008",
        "capability": "example.topology",
        "semantic_assertions": [],
        "semantic_review": {
            "status": "ACCEPTED",
            "checks": topology_semantic_contract["required_semantic_review_checks"],
            "view_boundary_requirements": [
                {
                    "id": "BOUNDARY-A-B",
                    "participants": ["VIEW-A", "VIEW-B"],
                    "materiality": "MATERIAL",
                    "contestability": "CONTESTABLE",
                    "outcome": "SEPARATE",
                    "rationale_bases": [
                        {
                            "id": "RESPONSIBILITY-SPLIT",
                            "classification": "UPSTREAM_RESPONSIBILITY",
                            "rationale": "Different tasks and application capabilities.",
                        }
                    ],
                    "decision_refs": ["overall-view-structure"],
                }
            ],
        },
    }
    h008_red = evaluate_artifact(
        topology_semantic_contract,
        {"semantic_assertions": []},
        responsibility_shaped,
    )
    assert h008_red["status"] == "REJECTED", h008_red
    assert "VIEW_BOUNDARY_USER_FACING_BASIS_REQUIRED" in codes(h008_red), h008_red

    # H003 positive control: a concrete material boundary is a stable decision
    # subject and its alternatives are challenged by probes bound to that point.
    local_topology_exploration = {
        "version": 1,
        "kind": "harness-decision-exploration",
        "capability": "example.topology",
        "knowledge_kind": "interface-topology-design",
        "explorer_request_id": topology_request["request_id"],
        "research_sources": [],
        "axes": [
            {
                "axis": "view-boundaries",
                "applicability": "APPLICABLE",
                "exploration_level": "EXPLORE",
                "probes": [
                    {
                        "strategy": "merge-vs-separate-view",
                        "challenge": "Test merge versus separate for BOUNDARY-A-B.",
                        "alternatives": ["a-b-separate", "a-b-merge"],
                        "decision_points": ["boundary-a-b-choice"],
                    },
                    {
                        "strategy": "persistent-context-vs-navigation",
                        "challenge": "Test persistent context versus navigation for BOUNDARY-A-B.",
                        "alternatives": ["a-b-separate", "a-b-merge"],
                        "decision_points": ["boundary-a-b-choice"],
                    },
                ],
                "decision_points": [
                    {
                        "id": "boundary-a-b-choice",
                        "subjects": ["BOUNDARY-A-B"],
                        "alternatives": [
                            {
                                "id": "a-b-separate",
                                "difference": "Keep A and B independently addressable.",
                                "material_effects": {
                                    "goal-continuity": "intentional-context-switch",
                                },
                            },
                            {
                                "id": "a-b-merge",
                                "difference": "Keep A and B in one user-facing area.",
                                "material_effects": {
                                    "goal-continuity": "continuous-user-goal",
                                },
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
            "reviewed_decisions": ["boundary-a-b-choice"],
            "open_gaps": [],
        },
    }
    local_topology_candidate = {
        "id": "TOPOLOGY-H4-LOCAL",
        "capability": "example.topology",
        "path": "docs/interface/topology-h4-local.yaml",
        "semantic_assertions": [],
        "semantic_review": {
            "status": "ACCEPTED",
            "checks": topology_semantic_contract["required_semantic_review_checks"],
            "view_boundary_requirements": [
                {
                    "id": "BOUNDARY-A-B",
                    "participants": ["VIEW-A", "VIEW-B"],
                    "materiality": "MATERIAL",
                    "contestability": "CONTESTABLE",
                    "outcome": "SEPARATE",
                    "rationale_bases": [
                        {
                            "id": "INDEPENDENT-RESUME",
                            "classification": "USER_FACING",
                            "rationale": "B has independent revisit/resume value.",
                        }
                    ],
                    "decision_refs": ["boundary-a-b-choice"],
                }
            ],
        },
        "decision_review": {
            "axes": [
                {
                    "axis": "view-boundaries",
                    "decisions": [
                        {
                            "id": "boundary-a-b-choice",
                            "owner_authority": "HUMAN-INTERFACE-DESIGN",
                            "alternatives": [
                                {"id": "a-b-separate", "state": "VIABLE"},
                                {
                                    "id": "a-b-merge",
                                    "state": "REJECTED",
                                    "rationale": "Independent resume semantics make merge unsuitable.",
                                },
                            ],
                            "disposition": "DETERMINED",
                            "selected": "a-b-separate",
                        }
                    ],
                }
            ]
        },
    }
    local_preflight = evaluate_decision_preflight(
        contract=topology_contract,
        policy=topology_policy,
        axis_policies=axis_policies(topology_contract, topology_policy),
        explorer_request=topology_request,
        capability="example.topology",
        knowledge_kind="interface-topology-design",
        authority="HUMAN-INTERFACE-DESIGN",
        exploration_evidence=local_topology_exploration,
        candidate=local_topology_candidate,
        model=topology_model,
    )
    assert local_preflight["status"] == "ACCEPTED", local_preflight
    local_semantics = evaluate_artifact(
        topology_semantic_contract,
        {"semantic_assertions": []},
        local_topology_candidate,
    )
    assert local_semantics["status"] == "ACCEPTED", local_semantics

    # D2: naming a boundary is insufficient when the required challenges were
    # not performed for that concrete decision point.
    unchallenged_boundary = copy.deepcopy(local_topology_exploration)
    for probe in unchallenged_boundary["axes"][0]["probes"]:
        probe["decision_points"] = []
    d2 = evaluate_decision_preflight(
        contract=topology_contract,
        policy=topology_policy,
        axis_policies=axis_policies(topology_contract, topology_policy),
        explorer_request=topology_request,
        capability="example.topology",
        knowledge_kind="interface-topology-design",
        authority="HUMAN-INTERFACE-DESIGN",
        exploration_evidence=unchallenged_boundary,
        candidate=local_topology_candidate,
        model=topology_model,
    )
    assert d2["status"] == "REJECTED", d2
    assert "DECISION_SUBJECT_PROBE_DIVERSITY_INSUFFICIENT" in codes(d2), d2

    # D3: one decision cannot silently govern materially distinct boundaries.
    indiscriminate_exploration = copy.deepcopy(local_topology_exploration)
    indiscriminate_exploration["axes"][0]["decision_points"][0]["subjects"] = [
        "BOUNDARY-A-B",
        "BOUNDARY-B-C",
    ]
    indiscriminate_candidate = copy.deepcopy(local_topology_candidate)
    indiscriminate_candidate["semantic_review"]["view_boundary_requirements"].append(
        {
            "id": "BOUNDARY-B-C",
            "participants": ["VIEW-B", "VIEW-C"],
            "materiality": "MATERIAL",
            "contestability": "CONTESTABLE",
            "outcome": "SEPARATE",
            "rationale_bases": [
                {
                    "id": "AUTHORITY-MODE",
                    "classification": "USER_FACING",
                    "rationale": "C changes the user-visible authority mode.",
                }
            ],
            "decision_refs": ["boundary-a-b-choice"],
        }
    )
    d3 = evaluate_decision_preflight(
        contract=topology_contract,
        policy=topology_policy,
        axis_policies=axis_policies(topology_contract, topology_policy),
        explorer_request=topology_request,
        capability="example.topology",
        knowledge_kind="interface-topology-design",
        authority="HUMAN-INTERFACE-DESIGN",
        exploration_evidence=indiscriminate_exploration,
        candidate=indiscriminate_candidate,
        model=topology_model,
    )
    assert d3["status"] == "REJECTED", d3
    assert "VIEW_BOUNDARY_SHARED_DECISION_REVIEW_REQUIRED" in codes(d3), d3

    # P3: sharing is valid when semantic review explicitly establishes that the
    # boundaries are one decision context with the same material consequences.
    shared_candidate = copy.deepcopy(indiscriminate_candidate)
    for boundary in shared_candidate["semantic_review"]["view_boundary_requirements"]:
        boundary["shared_decision_group"] = "SHARED-AB-BC"
    shared_candidate["semantic_review"]["shared_boundary_decision_groups"] = [
        {
            "id": "SHARED-AB-BC",
            "boundaries": ["BOUNDARY-A-B", "BOUNDARY-B-C"],
            "semantic_equivalence": "ACCEPTED",
            "rationale": "Both boundaries are governed by the same addressability transition.",
        }
    ]
    shared = evaluate_decision_preflight(
        contract=topology_contract,
        policy=topology_policy,
        axis_policies=axis_policies(topology_contract, topology_policy),
        explorer_request=topology_request,
        capability="example.topology",
        knowledge_kind="interface-topology-design",
        authority="HUMAN-INTERFACE-DESIGN",
        exploration_evidence=indiscriminate_exploration,
        candidate=shared_candidate,
        model=topology_model,
    )
    assert shared["status"] == "ACCEPTED", shared
    shared_semantics = evaluate_artifact(
        topology_semantic_contract,
        {"semantic_assertions": []},
        shared_candidate,
    )
    assert shared_semantics["status"] == "ACCEPTED", shared_semantics

    # P1: deterministic material boundaries carry explicit accepted-constraint
    # evidence and do not require artificial alternatives.
    deterministic_candidate = copy.deepcopy(local_topology_candidate)
    deterministic_candidate["semantic_review"]["view_boundary_requirements"].append(
        {
            "id": "BOUNDARY-B-C",
            "participants": ["VIEW-B", "VIEW-C"],
            "materiality": "MATERIAL",
            "contestability": "DETERMINISTIC",
            "outcome": "SEPARATE",
            "rationale_bases": [
                {
                    "id": "AUTHORIZATION",
                    "classification": "USER_FACING",
                    "rationale": "Accepted authorization semantics require a mode boundary.",
                }
            ],
            "decision_refs": [],
            "deterministic_evidence": ["ACCEPTED-AUTHORIZATION-CONSTRAINT"],
            "deterministic_rationale": "The accepted constraint uniquely requires separation.",
        }
    )
    deterministic = evaluate_decision_preflight(
        contract=topology_contract,
        policy=topology_policy,
        axis_policies=axis_policies(topology_contract, topology_policy),
        explorer_request=topology_request,
        capability="example.topology",
        knowledge_kind="interface-topology-design",
        authority="HUMAN-INTERFACE-DESIGN",
        exploration_evidence=local_topology_exploration,
        candidate=deterministic_candidate,
        model=topology_model,
    )
    assert deterministic["status"] == "ACCEPTED", deterministic
    deterministic_semantics = evaluate_artifact(
        topology_semantic_contract,
        {"semantic_assertions": []},
        deterministic_candidate,
    )
    assert deterministic_semantics["status"] == "ACCEPTED", deterministic_semantics

    # H008 positive freedom: two upstream responsibilities may remain one
    # user-facing area. Responsibility decomposition is input, not boundary proof.
    grouped_responsibilities = {
        "id": "TOPOLOGY-H4-GROUPED",
        "capability": "example.topology",
        "semantic_assertions": [],
        "semantic_review": {
            "status": "ACCEPTED",
            "checks": topology_semantic_contract["required_semantic_review_checks"],
            "view_boundary_requirements": [
                {
                    "id": "BOUNDARY-TASK-A-TASK-B",
                    "participants": ["TASK-SURFACE-A", "TASK-SURFACE-B"],
                    "materiality": "MATERIAL",
                    "contestability": "CONTESTABLE",
                    "outcome": "MERGED",
                    "rationale_bases": [
                        {
                            "id": "UPSTREAM-SPLIT",
                            "classification": "UPSTREAM_RESPONSIBILITY",
                            "rationale": "The tasks and application capabilities remain separately owned.",
                        }
                    ],
                    "decision_refs": ["merge-task-surfaces"],
                }
            ],
        },
    }
    grouped = evaluate_artifact(
        topology_semantic_contract,
        {"semantic_assertions": []},
        grouped_responsibilities,
    )
    assert grouped["status"] == "ACCEPTED", grouped


    # WP-H5 / HARNESS-006 RED A+B: accepted task semantics can identify a
    # material comparison/collection representation need while all current
    # Presentation Decision Governance axes are complete. The baseline has no
    # representation-scoped axis, so both cases false-green.
    presentation_graph = {
        "version": 1,
        "kind": "harness-engineering-graph",
        "id": "H5-PRESENTATION",
        "authorities": [
            {
                "id": "HUMAN-INTERFACE-DESIGN",
                "responsibility": "Own user-facing presentation decisions.",
                "boundary": {
                    "semantic_cohesion": "Application presentation semantics.",
                    "independent_change": "Presentation can change independently.",
                    "public_contract": "Accepted presentation system.",
                },
                "produces": [
                    {
                        "capability": "example.presentation",
                        "knowledge_kind": "presentation-system-design",
                        "requires": [],
                    }
                ],
            }
        ],
        "consumers": [
            {
                "id": "PRESENTATION-CONSUMER",
                "purpose": "Consume accepted presentation decisions.",
                "requires": ["example.presentation"],
            }
        ],
        "terminal_capabilities": [],
    }
    presentation_model = {"artifacts": [], "questions": []}
    presentation_policy = {
        "version": 1,
        "kind": "harness-decision-policy",
        "knowledge_kinds": [
            {
                "knowledge_kind": "presentation-system-design",
                "autonomy": "CONSERVATIVE",
            }
        ],
    }
    presentation_context = build_authority_context(
        presentation_graph,
        presentation_model,
        "HUMAN-INTERFACE-DESIGN",
        ["example.presentation"],
    )
    presentation_request = build_decision_explorer_request(
        capability="example.presentation",
        knowledge_kind="presentation-system-design",
        authority="HUMAN-INTERFACE-DESIGN",
        authority_context=presentation_context,
        contract=presentation_contract,
        axis_policies=axis_policies(presentation_contract, presentation_policy),
        prerequisite_baseline={},
        model=presentation_model,
    )
    legacy_presentation_axes = [
        "application-surface",
        "knowledge-representation",
        "information-density",
        "control-surface",
    ]
    legacy_axes = []
    legacy_review_axes = []
    for axis in legacy_presentation_axes:
        axis_contract = presentation_contract["axes"][axis]
        dim = axis_contract["material_dimensions"][0]
        strategies = axis_contract["challenge_strategies"][:2]
        decision_id = f"{axis}-legacy-choice"
        alternative_ids = [f"{axis}-legacy-a", f"{axis}-legacy-b"]
        legacy_axes.append(
            {
                "axis": axis,
                "applicability": "APPLICABLE",
                "exploration_level": "EXPLORE",
                "probes": [
                    {
                        "strategy": strategies[0],
                        "challenge": f"Challenge {axis} through {strategies[0]}.",
                        "alternatives": alternative_ids,
                        "decision_points": [decision_id],
                    },
                    {
                        "strategy": strategies[1],
                        "challenge": f"Challenge {axis} through {strategies[1]}.",
                        "alternatives": alternative_ids,
                        "decision_points": [decision_id],
                    },
                ],
                "decision_points": [
                    {
                        "id": decision_id,
                        "alternatives": [
                            {
                                "id": alternative_ids[0],
                                "difference": f"Alternative A for {axis}.",
                                "material_effects": {dim: "A"},
                            },
                            {
                                "id": alternative_ids[1],
                                "difference": f"Alternative B for {axis}.",
                                "material_effects": {dim: "B"},
                            },
                        ],
                    }
                ],
            }
        )
        legacy_review_axes.append(
            {
                "axis": axis,
                "decisions": [
                    {
                        "id": decision_id,
                        "owner_authority": "HUMAN-INTERFACE-DESIGN",
                        "alternatives": [
                            {"id": alternative_ids[0], "state": "VIABLE"},
                            {
                                "id": alternative_ids[1],
                                "state": "REJECTED",
                                "rationale": "Accepted constraints eliminate alternative B.",
                            },
                        ],
                        "disposition": "DETERMINED",
                        "selected": alternative_ids[0],
                    }
                ],
            }
        )
    legacy_presentation_exploration = {
        "version": 1,
        "kind": "harness-decision-exploration",
        "capability": "example.presentation",
        "knowledge_kind": "presentation-system-design",
        "explorer_request_id": presentation_request["request_id"],
        "research_sources": [],
        "axes": legacy_axes,
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
                item["decisions"][0]["id"] for item in legacy_review_axes
            ],
            "open_gaps": [],
        },
    }

    def legacy_representation_candidate(subject):
        return {
            "id": f"PRESENTATION-{subject['id']}",
            "capability": "example.presentation",
            "semantic_assertions": [],
            "semantic_review": {
                "status": "ACCEPTED",
                "representation_requirements": [subject],
            },
            "decision_review": {"axes": copy.deepcopy(legacy_review_axes)},
        }

    h006_red_a = evaluate_decision_preflight(
        contract=presentation_contract,
        policy=presentation_policy,
        axis_policies=axis_policies(presentation_contract, presentation_policy),
        explorer_request=presentation_request,
        capability="example.presentation",
        knowledge_kind="presentation-system-design",
        authority="HUMAN-INTERFACE-DESIGN",
        exploration_evidence=legacy_presentation_exploration,
        candidate=legacy_representation_candidate(
            {
                "id": "REP-COMPARE-A-B",
                "materiality": "MATERIAL",
                "disposition": "DECIDE",
                "task_semantics": "Compare N candidate entities over the same semantic dimensions.",
                "required_dimensions": ["cross-entity-alignment"],
                "required_challenges": ["independent-vs-aligned-records"],
                "decision_refs": [],
            }
        ),
        model=presentation_model,
    )
    assert h006_red_a["status"] == "REJECTED", h006_red_a

    h006_red_b = evaluate_decision_preflight(
        contract=presentation_contract,
        policy=presentation_policy,
        axis_policies=axis_policies(presentation_contract, presentation_policy),
        explorer_request=presentation_request,
        capability="example.presentation",
        knowledge_kind="presentation-system-design",
        authority="HUMAN-INTERFACE-DESIGN",
        exploration_evidence=legacy_presentation_exploration,
        candidate=legacy_representation_candidate(
            {
                "id": "REP-HOMOGENEOUS-COLLECTION",
                "materiality": "MATERIAL",
                "disposition": "DECIDE",
                "task_semantics": "Scan homogeneous records over shared fields and repeated state.",
                "required_dimensions": ["record-scan-structure"],
                "required_challenges": ["repeated-vs-structured-collection"],
                "decision_refs": [],
            }
        ),
        model=presentation_model,
    )
    assert h006_red_b["status"] == "REJECTED", h006_red_b

    representation_axis = presentation_contract["axes"]["representation-selection"]
    assert representation_axis["subject_scope"] == "representation-subject", representation_axis
    assert set(representation_axis["material_dimensions"]) == {
        "cross-entity-alignment",
        "record-scan-structure",
        "selection-mechanics",
        "relation-encoding",
        "detail-context-preservation",
        "responsive-semantic-preservation",
    }, representation_axis
    assert {
        "independent-vs-aligned-records",
        "repeated-vs-structured-collection",
        "overview-vs-progressive-detail",
        "spatial-vs-nonspatial",
        "selection-mechanic-perturbation",
        "responsive-representation-perturbation",
    } == set(representation_axis["challenge_strategies"]), representation_axis

    def task_basis(basis_id="TASK"):
        return [
            {
                "id": basis_id,
                "classification": "TASK_SEMANTICS",
                "rationale": "Accepted user task semantics make representation choice material.",
            }
        ]

    def representation_requirement(
        subject_id,
        *,
        dimensions,
        challenges,
        decision_id=None,
        bases=None,
        disposition="DECIDE",
        shared_default_ref=None,
        override_rationale=None,
    ):
        value = {
            "id": subject_id,
            "materiality": "MATERIAL",
            "disposition": disposition,
            "task_semantics": f"Task-facing representation semantics for {subject_id}.",
            "bases": task_basis(subject_id) if bases is None else bases,
            "required_dimensions": list(dimensions),
            "required_challenges": list(challenges),
            "decision_refs": [decision_id] if decision_id else [],
        }
        if shared_default_ref is not None:
            value["shared_default_ref"] = shared_default_ref
        if override_rationale is not None:
            value["override_rationale"] = override_rationale
        return value

    def representation_preflight(
        requirement,
        alternatives,
        strategies,
        *,
        decision_id="representation-choice",
    ):
        alt_ids = [item["id"] for item in alternatives]
        axes = copy.deepcopy(legacy_axes)
        axes.append(
            {
                "axis": "representation-selection",
                "applicability": "APPLICABLE",
                "exploration_level": "EXPLORE",
                "probes": [
                    {
                        "strategy": strategy,
                        "challenge": f"Challenge {requirement['id']} through {strategy}.",
                        "alternatives": alt_ids,
                        "decision_points": [decision_id],
                    }
                    for strategy in strategies
                ],
                "decision_points": [
                    {
                        "id": decision_id,
                        "subjects": [requirement["id"]],
                        "alternatives": copy.deepcopy(alternatives),
                    }
                ],
            }
        )
        review_axes = copy.deepcopy(legacy_review_axes)
        review_axes.append(
            {
                "axis": "representation-selection",
                "decisions": [
                    {
                        "id": decision_id,
                        "owner_authority": "HUMAN-INTERFACE-DESIGN",
                        "alternatives": [
                            {"id": alt_ids[0], "state": "VIABLE"},
                            *[
                                {
                                    "id": alt_id,
                                    "state": "REJECTED",
                                    "rationale": "Accepted task constraints favor the selected alternative.",
                                }
                                for alt_id in alt_ids[1:]
                            ],
                        ],
                        "disposition": "DETERMINED",
                        "selected": alt_ids[0],
                    }
                ],
            }
        )
        exploration_value = {
            "version": 1,
            "kind": "harness-decision-exploration",
            "capability": "example.presentation",
            "knowledge_kind": "presentation-system-design",
            "explorer_request_id": presentation_request["request_id"],
            "research_sources": [],
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
                    item["decisions"][0]["id"] for item in review_axes
                ],
                "open_gaps": [],
            },
        }
        candidate_value = {
            "id": f"PRESENTATION-{requirement['id']}",
            "capability": "example.presentation",
            "semantic_assertions": [],
            "semantic_review": {
                "status": "ACCEPTED",
                "representation_requirements": [copy.deepcopy(requirement)],
            },
            "decision_review": {"axes": review_axes},
        }
        return evaluate_decision_preflight(
            contract=presentation_contract,
            policy=presentation_policy,
            axis_policies=axis_policies(presentation_contract, presentation_policy),
            explorer_request=presentation_request,
            capability="example.presentation",
            knowledge_kind="presentation-system-design",
            authority="HUMAN-INTERFACE-DESIGN",
            exploration_evidence=exploration_value,
            candidate=candidate_value,
            model=presentation_model,
        )

    # M1: an unrelated representation decision cannot cover the material subject.
    m1_requirement = representation_requirement(
        "REP-COMPARE-M1",
        dimensions=["cross-entity-alignment"],
        challenges=["independent-vs-aligned-records"],
    )
    m1 = representation_preflight(
        m1_requirement,
        [
            {
                "id": "aligned-rows",
                "difference": "Align same dimensions across candidates.",
                "material_effects": {"cross-entity-alignment": "aligned"},
            },
            {
                "id": "independent-records",
                "difference": "Keep each candidate independently grouped.",
                "material_effects": {"cross-entity-alignment": "independent"},
            },
        ],
        ["independent-vs-aligned-records", "overview-vs-progressive-detail"],
        decision_id="unrelated-representation-choice",
    )
    assert m1["status"] == "REJECTED", m1
    assert "REPRESENTATION_DECISION_COVERAGE_MISSING" in codes(m1), m1

    # M2: visually different card variants are not a semantic challenge to
    # same-dimension alignment when alignment itself never varies.
    m2_requirement = representation_requirement(
        "REP-COMPARE-M2",
        dimensions=["cross-entity-alignment"],
        challenges=["independent-vs-aligned-records"],
        decision_id="compare-m2-choice",
    )
    m2 = representation_preflight(
        m2_requirement,
        [
            {
                "id": "large-cards",
                "difference": "Large independent record surfaces.",
                "material_effects": {
                    "cross-entity-alignment": "independent",
                    "record-scan-structure": "large-repeated-records",
                },
            },
            {
                "id": "compact-cards",
                "difference": "Compact independent record surfaces.",
                "material_effects": {
                    "cross-entity-alignment": "independent",
                    "record-scan-structure": "compact-repeated-records",
                },
            },
        ],
        ["independent-vs-aligned-records", "overview-vs-progressive-detail"],
        decision_id="compare-m2-choice",
    )
    assert m2["status"] == "REJECTED", m2
    assert "REPRESENTATION_REQUIRED_DIMENSION_NOT_CHALLENGED" in codes(m2), m2

    # M3: implementation availability is evidence about feasibility, not
    # authority for a material representation choice.
    m3_requirement = representation_requirement(
        "REP-COLLECTION-M3",
        dimensions=["record-scan-structure"],
        challenges=["repeated-vs-structured-collection"],
        decision_id="collection-m3-choice",
        bases=[
            {
                "id": "EXISTING-DATATABLE",
                "classification": "IMPLEMENTATION_PRIMITIVE",
                "rationale": "A reusable DataTable already exists.",
            }
        ],
    )
    m3 = representation_preflight(
        m3_requirement,
        [
            {
                "id": "tabular-records",
                "difference": "Aligned shared fields.",
                "material_effects": {"record-scan-structure": "aligned-fields"},
            },
            {
                "id": "grouped-list",
                "difference": "Grouped records with repeated labels.",
                "material_effects": {"record-scan-structure": "grouped-records"},
            },
        ],
        ["repeated-vs-structured-collection", "overview-vs-progressive-detail"],
        decision_id="collection-m3-choice",
    )
    assert m3["status"] == "REJECTED", m3
    assert "REPRESENTATION_TASK_BASIS_REQUIRED" in codes(m3), m3

    # M4: homogeneous collection fallthrough is the collection analogue of RED A.
    m4_requirement = representation_requirement(
        "REP-COLLECTION-M4",
        dimensions=["record-scan-structure"],
        challenges=["repeated-vs-structured-collection"],
    )
    m4 = representation_preflight(
        m4_requirement,
        [
            {
                "id": "aligned-records",
                "difference": "Expose shared fields in aligned record structure.",
                "material_effects": {"record-scan-structure": "aligned-fields"},
            },
            {
                "id": "repeated-surfaces",
                "difference": "Repeat the full record surface.",
                "material_effects": {"record-scan-structure": "repeated-fields"},
            },
        ],
        ["repeated-vs-structured-collection", "overview-vs-progressive-detail"],
        decision_id="unrelated-collection-choice",
    )
    assert m4["status"] == "REJECTED", m4
    assert "REPRESENTATION_DECISION_COVERAGE_MISSING" in codes(m4), m4

    representation_semantic_contract = {
        "requires_semantic_review": True,
        "required_semantic_review_checks": ["representation-selection-applicability"],
    }

    # M5: a screen with a shared default must call a local change an OVERRIDE
    # and carry explicit rationale; silently choosing another representation is rejected.
    m5_candidate = {
        "id": "SCREEN-M5",
        "capability": "example.screen",
        "semantic_assertions": [],
        "semantic_review": {
            "status": "ACCEPTED",
            "checks": ["representation-selection-applicability"],
            "representation_requirements": [
                representation_requirement(
                    "REP-SCREEN-M5",
                    dimensions=["record-scan-structure"],
                    challenges=["repeated-vs-structured-collection"],
                    decision_id="screen-local-choice",
                    disposition="DECIDE",
                    shared_default_ref="REP-SHARED-COLLECTION",
                )
            ],
        },
    }
    m5 = evaluate_artifact(
        representation_semantic_contract,
        {"semantic_assertions": []},
        m5_candidate,
    )
    assert m5["status"] == "REJECTED", m5
    assert "REPRESENTATION_OVERRIDE_DISPOSITION_REQUIRED" in codes(m5), m5

    # P1: cards remain a valid result when individual rich inspection is the task.
    p1 = representation_preflight(
        representation_requirement(
            "REP-RICH-ENTITIES",
            dimensions=["detail-context-preservation"],
            challenges=["overview-vs-progressive-detail"],
            decision_id="rich-entity-choice",
        ),
        [
            {
                "id": "rich-cards",
                "difference": "Keep rich entity context co-located for individual inspection.",
                "material_effects": {"detail-context-preservation": "co-located"},
            },
            {
                "id": "summary-plus-detail",
                "difference": "Use compact summaries with progressive detail.",
                "material_effects": {"detail-context-preservation": "progressive"},
            },
        ],
        ["overview-vs-progressive-detail", "repeated-vs-structured-collection"],
        decision_id="rich-entity-choice",
    )
    assert p1["status"] == "ACCEPTED", p1

    # P2: homogeneous records are not forced into a table.
    p2 = representation_preflight(
        representation_requirement(
            "REP-HOMOGENEOUS-P2",
            dimensions=["record-scan-structure"],
            challenges=["repeated-vs-structured-collection"],
            decision_id="homogeneous-p2-choice",
        ),
        [
            {
                "id": "grouped-list",
                "difference": "Use a grouped list optimized for the accepted scan task.",
                "material_effects": {"record-scan-structure": "grouped-scan"},
            },
            {
                "id": "tabular-alignment",
                "difference": "Use aligned shared fields.",
                "material_effects": {"record-scan-structure": "aligned-fields"},
            },
        ],
        ["repeated-vs-structured-collection", "overview-vs-progressive-detail"],
        decision_id="homogeneous-p2-choice",
    )
    assert p2["status"] == "ACCEPTED", p2

    # P3: same-dimension comparison can be aligned without selecting an HTML table.
    p3 = representation_preflight(
        representation_requirement(
            "REP-COMPARE-P3",
            dimensions=["cross-entity-alignment"],
            challenges=["independent-vs-aligned-records"],
            decision_id="compare-p3-choice",
        ),
        [
            {
                "id": "synchronized-columns",
                "difference": "Synchronize candidate columns over shared dimensions.",
                "material_effects": {"cross-entity-alignment": "aligned"},
            },
            {
                "id": "independent-records",
                "difference": "Keep dimensions inside independent candidate records.",
                "material_effects": {"cross-entity-alignment": "independent"},
            },
        ],
        ["independent-vs-aligned-records", "overview-vs-progressive-detail"],
        decision_id="compare-p3-choice",
    )
    assert p3["status"] == "ACCEPTED", p3

    # P4: spatial/relational knowledge remains free to select graph or mixed forms.
    p4 = representation_preflight(
        representation_requirement(
            "REP-RELATIONAL-P4",
            dimensions=["relation-encoding"],
            challenges=["spatial-vs-nonspatial"],
            decision_id="relational-p4-choice",
        ),
        [
            {
                "id": "mixed-graph-and-results",
                "difference": "Use spatial overview plus nonspatial results.",
                "material_effects": {"relation-encoding": "mixed-spatial"},
            },
            {
                "id": "nonspatial-results",
                "difference": "Use only nonspatial relation listings.",
                "material_effects": {"relation-encoding": "nonspatial"},
            },
        ],
        ["spatial-vs-nonspatial", "overview-vs-progressive-detail"],
        decision_id="relational-p4-choice",
    )
    assert p4["status"] == "ACCEPTED", p4

    # P5: a local override is valid when the shared default is explicit and the
    # deviation is intentionally justified.
    p5_requirement = representation_requirement(
        "REP-SCREEN-P5",
        dimensions=["record-scan-structure"],
        challenges=["repeated-vs-structured-collection"],
        decision_id="screen-p5-choice",
        disposition="OVERRIDE",
        shared_default_ref="REP-SHARED-COLLECTION",
        override_rationale="This screen preserves required context through a local master-detail form.",
    )
    p5_semantics = evaluate_artifact(
        representation_semantic_contract,
        {"semantic_assertions": []},
        {
            "id": "SCREEN-P5",
            "capability": "example.screen",
            "semantic_assertions": [],
            "semantic_review": {
                "status": "ACCEPTED",
                "checks": ["representation-selection-applicability"],
                "representation_requirements": [p5_requirement],
            },
        },
    )
    assert p5_semantics["status"] == "ACCEPTED", p5_semantics
    p5 = representation_preflight(
        p5_requirement,
        [
            {
                "id": "local-master-detail",
                "difference": "Preserve local context with master-detail.",
                "material_effects": {"record-scan-structure": "master-detail"},
            },
            {
                "id": "shared-aligned-records",
                "difference": "Inherit aligned shared records unchanged.",
                "material_effects": {"record-scan-structure": "aligned-fields"},
            },
        ],
        ["repeated-vs-structured-collection", "overview-vs-progressive-detail"],
        decision_id="screen-p5-choice",
    )
    assert p5["status"] == "ACCEPTED", p5

    # P6: responsive structure may transform as long as preservation itself was
    # materially challenged rather than frozen to one primitive/layout.
    p6 = representation_preflight(
        representation_requirement(
            "REP-RESPONSIVE-P6",
            dimensions=["responsive-semantic-preservation"],
            challenges=["responsive-representation-perturbation"],
            decision_id="responsive-p6-choice",
        ),
        [
            {
                "id": "wide-aligned-narrow-serialized",
                "difference": "Align on wide surfaces and serialize on narrow surfaces.",
                "material_effects": {"responsive-semantic-preservation": "preserved"},
            },
            {
                "id": "fixed-wide-structure",
                "difference": "Keep the wide structure unchanged at narrow width.",
                "material_effects": {"responsive-semantic-preservation": "degraded"},
            },
        ],
        ["responsive-representation-perturbation", "independent-vs-aligned-records"],
        decision_id="responsive-p6-choice",
    )
    assert p6["status"] == "ACCEPTED", p6

    screen_contract = contracts["screen-view-design"]
    assert set(screen_contract["axes"]) == {
        "view-composition",
        "detail-edit-placement",
        "responsive-composition",
        "representation-selection",
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
