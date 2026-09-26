#!/usr/bin/env python3
from __future__ import annotations

import copy
from pathlib import Path
import sys
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from authority_context import build_authority_context
from decision_explorer_request import build_decision_explorer_request
from decision_execution_assurance import evaluate_execution_assurance
from decision_governance import axis_policies, decision_contract_index
from semantic_acceptance import evaluate_artifact
from semantic_admission import admit_artifact


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
    contract = decision_contract_index(decision_contracts)["system-architecture"]

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
