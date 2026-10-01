#!/usr/bin/env python3
"""Strict semantic admission for one Engineering Graph capability.

This composes Authority execution context, source provenance/direction,
artifact-specific semantic review and capability lifecycle baselines before a
provider may be treated as accepted semantic knowledge.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml

from agent_router import validate_skill_registry
from authority_context import build_authority_context, validate_extracted_references
from capability_lifecycle import lifecycle_index, lifecycle_states
from decision_execution_assurance import evaluate_execution_assurance
from decision_exploration import evaluate_decision_exploration
from decision_explorer_request import build_decision_explorer_request
from decision_governance import (
    axis_policies,
    decision_contract_index,
    evaluate_decision_governance,
)
from engineering_graph import producer_index, production_index, validate_realization
from harness import CoreError
from semantic_acceptance import evaluate_artifact
from semantic_fingerprint import semantic_assertion_fingerprints
from semantic_questions import questions_from_semantic_evaluation


def load_yaml(path: str | Path) -> dict[str, Any]:
    value = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise CoreError(f"{path} must contain a mapping")
    return value


def knowledge_contract_index(document: dict[str, Any]) -> dict[str, dict[str, Any]]:
    if document.get("version") != 1:
        raise CoreError("knowledge-kind semantic contract version must be 1")
    if document.get("kind") != "harness-knowledge-kind-semantic-contracts":
        raise CoreError("unexpected knowledge-kind semantic contract kind")

    defaults = document.get("defaults", {}) or {}
    if not isinstance(defaults, dict):
        raise CoreError("knowledge-kind semantic contract defaults must be a mapping")

    result: dict[str, dict[str, Any]] = {}
    for item in document.get("contracts", []) or []:
        if not isinstance(item, dict):
            raise CoreError("knowledge-kind semantic contract must be a mapping")
        knowledge_kind = item.get("knowledge_kind")
        if not isinstance(knowledge_kind, str) or not knowledge_kind:
            raise CoreError("knowledge-kind semantic contract requires knowledge_kind")
        if knowledge_kind in result:
            raise CoreError(
                f"duplicate knowledge-kind semantic contract: {knowledge_kind}"
            )
        merged = dict(defaults)
        default_checks = list(defaults.get("required_review_checks", []) or [])
        item_checks = list(item.get("required_review_checks", []) or [])
        merged.update(item)
        merged["required_review_checks"] = sorted(
            set(default_checks + item_checks)
        )
        result[knowledge_kind] = merged
    return result


def _merge_named_items(
    base: list[dict[str, Any]],
    overlay: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    result = {
        item["id"]: dict(item)
        for item in base
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }
    order = [
        item["id"]
        for item in base
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    ]
    for item in overlay:
        if not isinstance(item, dict) or not isinstance(item.get("id"), str):
            raise CoreError("semantic contract overlay items require id")
        item_id = item["id"]
        if item_id not in result:
            order.append(item_id)
        result[item_id] = dict(item)
    return [result[item_id] for item_id in order]


def effective_knowledge_contract(
    base: dict[str, Any],
    knowledge_kind: str,
    overlays: list[dict[str, Any]] | None,
) -> dict[str, Any]:
    result = dict(base)
    for document in overlays or []:
        if document.get("version") != 1:
            raise CoreError("knowledge-kind semantic overlay version must be 1")
        if document.get("kind") != "harness-knowledge-kind-semantic-overlay":
            raise CoreError("unexpected knowledge-kind semantic overlay kind")
        matches = [
            item
            for item in document.get("contracts", []) or []
            if isinstance(item, dict)
            and item.get("knowledge_kind") == knowledge_kind
        ]
        if len(matches) > 1:
            raise CoreError(
                f"duplicate semantic overlay knowledge_kind: {knowledge_kind}"
            )
        if not matches:
            continue
        item = matches[0]
        for field in (
            "requires_source_authority",
            "requires_assertion_authority",
            "requires_semantic_review",
        ):
            if field in item:
                result[field] = item[field]
        for field in ("required_review_checks", "owned_assertion_kinds"):
            result[field] = sorted(
                set(result.get(field, []) or []) | set(item.get(field, []) or [])
            )
        for field in ("obligations", "compatibility_obligations"):
            result[field] = _merge_named_items(
                list(result.get(field, []) or []),
                list(item.get(field, []) or []),
            )
    return result


def _artifact_index(model: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        item["id"]: item
        for item in model.get("artifacts", []) or []
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }


def _validate_candidate_write_set(
    model: dict[str, Any],
    context: dict[str, Any],
    candidate: dict[str, Any],
) -> list[str]:
    candidate_id = candidate.get("id")
    candidate_path = candidate.get("path")
    if not isinstance(candidate_id, str) or not candidate_id:
        raise CoreError("semantic admission candidate id is required")
    if not isinstance(candidate_path, str) or not candidate_path:
        raise CoreError("semantic admission candidate path is required")

    artifacts = _artifact_index(model)
    for artifact_id, artifact in artifacts.items():
        if artifact_id == candidate_id:
            if artifact["authority"] != context["authority"]:
                raise CoreError(
                    f"candidate {candidate_id} belongs to {artifact['authority']}, "
                    f"not {context['authority']}"
                )
            if artifact["path"] != candidate_path:
                raise CoreError(
                    f"candidate {candidate_id} path mismatch: "
                    f"{candidate_path} != {artifact['path']}"
                )
        elif artifact.get("path") == candidate_path:
            raise CoreError(
                f"candidate path already belongs to another canonical artifact: "
                f"{candidate_path}"
            )

    changed_paths = candidate.get("changed_paths", [candidate_path])
    if not isinstance(changed_paths, list) or any(
        not isinstance(value, str) or not value for value in changed_paths
    ):
        raise CoreError("candidate changed_paths must be non-empty strings")

    allowed = set(context["access"]["write"])
    allowed.add(candidate_path)
    outside = sorted(set(changed_paths) - allowed)
    if outside:
        raise CoreError(
            f"Authority {context['authority']} may not write outside admitted "
            f"canonical artifacts: {outside}"
        )
    return sorted(set(changed_paths))


def _validate_source_assertion_artifacts(
    model: dict[str, Any],
    context: dict[str, Any],
    sources: dict[str, Any],
    candidate: dict[str, Any],
) -> None:
    artifacts = _artifact_index(model)
    allowed_paths = set(context["access"]["read"])
    source_by_id = {
        item["id"]: item
        for item in sources.get("semantic_assertions", []) or []
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }

    for assertion in candidate.get("semantic_assertions", []) or []:
        for source_id in assertion.get("derived_from", []) or []:
            source = source_by_id.get(source_id)
            if source is None:
                continue
            source_artifact = source.get("source_artifact")
            if not isinstance(source_artifact, str) or not source_artifact:
                raise CoreError(
                    f"source assertion {source_id} requires source_artifact "
                    "under strict semantic admission"
                )
            artifact = artifacts.get(source_artifact)
            if artifact is None:
                raise CoreError(
                    f"source assertion {source_id} references unknown canonical "
                    f"artifact: {source_artifact}"
                )
            if artifact["path"] not in allowed_paths:
                raise CoreError(
                    f"source assertion {source_id} comes from canonical artifact "
                    f"outside Authority read boundary: {source_artifact}"
                )
            source_authority = source.get("decision_authority")
            if source_authority != artifact["authority"]:
                raise CoreError(
                    f"source assertion {source_id} Authority {source_authority} "
                    f"does not match canonical artifact owner {artifact['authority']}"
                )




def _accepted_prerequisite_semantics(
    *,
    capability: str,
    prerequisite_capabilities: list[str],
    derivation_evaluations: list[dict[str, Any]] | None,
) -> dict[str, dict[str, Any]]:
    if not derivation_evaluations:
        return {}

    allowed = set(prerequisite_capabilities)
    result: dict[str, dict[str, Any]] = {}
    for evaluation in derivation_evaluations:
        if not isinstance(evaluation, dict):
            raise CoreError("derivation evaluation must be a mapping")
        if evaluation.get("kind") != "harness-semantic-derivation-evaluation":
            raise CoreError("unexpected derivation evaluation kind")
        if evaluation.get("status") != "ACCEPTED":
            raise CoreError(
                f"derivation evaluation for {capability} must be ACCEPTED"
            )
        if evaluation.get("target_capability") != capability:
            raise CoreError(
                f"derivation evaluation target mismatch for {capability}"
            )
        source_capability = evaluation.get("source_capability")
        if source_capability not in allowed:
            raise CoreError(
                f"derivation evaluation source {source_capability} is not a "
                f"prerequisite of {capability}"
            )
        if source_capability in result:
            raise CoreError(
                f"duplicate derivation lifecycle baseline for {source_capability}"
            )
        dependency = evaluation.get("lifecycle_dependency")
        if (
            not isinstance(dependency, dict)
            or dependency.get("capability") != source_capability
            or dependency.get("exhaustive") is not True
            or not isinstance(dependency.get("semantic_atoms"), dict)
            or not dependency["semantic_atoms"]
            or any(
                not isinstance(atom_id, str)
                or not atom_id
                or not isinstance(fingerprint, str)
                or not fingerprint
                for atom_id, fingerprint in dependency["semantic_atoms"].items()
            )
            or not isinstance(dependency.get("source_surface_fingerprints"), dict)
            or not dependency["source_surface_fingerprints"]
            or any(
                not isinstance(atom_id, str)
                or not atom_id
                or not isinstance(fingerprint, str)
                or not fingerprint
                for atom_id, fingerprint
                in dependency["source_surface_fingerprints"].items()
            )
        ):
            raise CoreError(
                f"lifecycle dependency evidence for {source_capability} must be exhaustive and contain consumed semantic atoms plus the complete source surface"
            )
        result[source_capability] = {
            "exhaustive": True,
            "semantic_atoms": dict(dependency["semantic_atoms"]),
            "source_surface_fingerprints": dict(
                dependency["source_surface_fingerprints"]
            ),
        }
    return result


def admit_artifact(
    *,
    graph: dict[str, Any],
    model: dict[str, Any],
    skill_registry: dict[str, Any],
    knowledge_contracts: dict[str, Any],
    knowledge_contract_overlays: list[dict[str, Any]] | None = None,
    decision_contracts: dict[str, Any] | None = None,
    decision_policy: dict[str, Any] | None = None,
    decision_exploration: dict[str, Any] | None = None,
    derivation_evaluations: list[dict[str, Any]] | None = None,
    capability: str,
    sources: dict[str, Any],
    candidate: dict[str, Any],
    acceptance_id: str,
    lifecycle: dict[str, Any] | None = None,
    decision_request_mode: str = "CREATE",
) -> dict[str, Any]:
    validate_skill_registry(skill_registry)
    realized = validate_realization(graph, model)
    producers = producer_index(graph)
    productions = production_index(graph)

    if capability not in productions:
        raise CoreError(f"unknown produced capability: {capability}")
    authority = producers[capability]
    production = productions[capability]

    if candidate.get("capability") != capability:
        raise CoreError(
            f"candidate capability mismatch: {candidate.get('capability')} != {capability}"
        )
    if not isinstance(acceptance_id, str) or not acceptance_id:
        raise CoreError("semantic admission acceptance_id is required")

    knowledge_kind = production.get("knowledge_kind")
    if not isinstance(knowledge_kind, str) or not knowledge_kind:
        raise CoreError(
            f"capability {capability} has no knowledge_kind; strict semantic "
            "admission cannot select an artifact contract"
        )

    route_by_kind = {
        item["knowledge_kind"]: item["skill"]
        for item in skill_registry.get("routes", []) or []
    }
    if knowledge_kind not in route_by_kind:
        raise CoreError(
            f"capability {capability} knowledge_kind {knowledge_kind} has no "
            "registered artifact skill"
        )

    contracts = knowledge_contract_index(knowledge_contracts)
    kind_contract = contracts.get(knowledge_kind)
    if kind_contract is None:
        raise CoreError(
            f"knowledge_kind {knowledge_kind} has no semantic admission contract"
        )

    kind_contract = effective_knowledge_contract(
        kind_contract,
        knowledge_kind,
        knowledge_contract_overlays,
    )

    if decision_contracts is None:
        decision_contracts = load_yaml(
            Path(__file__).resolve().parent
            / "spec/decision-governance/knowledge-kind-decision-contracts-v1.yaml"
        )
    decision_contract = decision_contract_index(decision_contracts).get(
        knowledge_kind
    )
    decision_axis_policies = axis_policies(
        decision_contract,
        decision_policy,
    )

    context = build_authority_context(
        graph, realized, authority, [capability]
    )
    if context["status"] not in {"ROOT", "READY"}:
        raise CoreError(
            f"Authority {authority} cannot admit {capability}: "
            f"context status {context['status']}"
        )

    changed_paths = _validate_candidate_write_set(realized, context, candidate)
    references = candidate.get("canonical_references", []) or []
    if not isinstance(references, list):
        raise CoreError("candidate canonical_references must be a list")
    validate_extracted_references(context, references)
    _validate_source_assertion_artifacts(realized, context, sources, candidate)

    prerequisite_capabilities = [
        item["capability"] for item in production.get("requires", []) or []
    ]
    allowed_source_authorities = {authority}
    for prerequisite in prerequisite_capabilities:
        allowed_source_authorities.add(producers[prerequisite])

    baseline: dict[str, str] = {}
    if prerequisite_capabilities:
        if lifecycle is None:
            raise CoreError(
                f"capability {capability} has prerequisites and requires a "
                "capability lifecycle projection for semantic admission"
            )
        states = lifecycle_states(graph, realized, lifecycle)
        index = lifecycle_index(lifecycle)
        for prerequisite in prerequisite_capabilities:
            if states[prerequisite]["state"] != "CURRENT":
                raise CoreError(
                    f"capability {capability} prerequisite {prerequisite} is "
                    f"{states[prerequisite]['state']}, not CURRENT"
                )
            baseline[prerequisite] = index[prerequisite]["acceptance_id"]

    semantic_baseline = _accepted_prerequisite_semantics(
        capability=capability,
        prerequisite_capabilities=prerequisite_capabilities,
        derivation_evaluations=derivation_evaluations,
    )

    semantic_contract = {
        "authority": authority,
        "semantic_claims": [
            item["claim"] if isinstance(item, dict) else item
            for item in production.get("semantic_claims", []) or []
        ],
        "owned_assertion_kinds": list(
            kind_contract.get("owned_assertion_kinds", []) or []
        ),
        "obligations": list(kind_contract.get("obligations", []) or []),
        "compatibility_obligations": list(
            kind_contract.get("compatibility_obligations", []) or []
        ),
        "allowed_source_authorities": sorted(allowed_source_authorities),
        "requires_source_authority": bool(
            kind_contract.get("requires_source_authority", True)
        ),
        "requires_assertion_authority": bool(
            kind_contract.get("requires_assertion_authority", True)
        ),
        "requires_semantic_review": bool(
            kind_contract.get("requires_semantic_review", True)
        ),
        "required_semantic_review_checks": list(
            kind_contract.get("required_review_checks", []) or []
        ),
    }

    current_provider_baseline = None
    if decision_request_mode in {"REVISION", "REDO"}:
        if lifecycle is None:
            raise CoreError(
                f"{decision_request_mode} semantic admission requires lifecycle evidence"
            )
        lifecycle_by_capability = lifecycle_index(lifecycle)
        provider = lifecycle_by_capability.get(capability)
        if provider is None:
            raise CoreError(
                f"{decision_request_mode} semantic admission requires current provider"
            )
        artifact_id = provider["artifact"]
        matches = [
            item
            for item in realized.get("artifacts", []) or []
            if item.get("id") == artifact_id
        ]
        if len(matches) != 1:
            raise CoreError(
                f"{decision_request_mode} semantic admission cannot resolve current provider {artifact_id}"
            )
        current_provider_baseline = matches[0]

    explorer_request = build_decision_explorer_request(
        capability=capability,
        knowledge_kind=knowledge_kind,
        authority=authority,
        authority_context=context,
        contract=decision_contract,
        axis_policies=decision_axis_policies,
        prerequisite_baseline=baseline,
        model=realized,
        mode=decision_request_mode,
        current_provider_baseline=current_provider_baseline,
    )

    evaluation = evaluate_artifact(semantic_contract, sources, candidate)
    exploration_evaluation = evaluate_decision_exploration(
        contract=decision_contract,
        axis_policies=decision_axis_policies,
        capability=capability,
        knowledge_kind=knowledge_kind,
        evidence=decision_exploration,
        explorer_request=explorer_request,
        model=realized,
    )
    execution_evaluation = evaluate_execution_assurance(
        policy=decision_policy,
        knowledge_kind=knowledge_kind,
        explorer_request=explorer_request,
        exploration_evaluation=exploration_evaluation,
    )
    decision_evaluation = evaluate_decision_governance(
        contract=decision_contract,
        policy=decision_policy,
        exploration_evaluation=exploration_evaluation,
        authority=authority,
        capability=capability,
        candidate=candidate,
        model=realized,
    )
    if exploration_evaluation["status"] != "NOT_REQUIRED":
        evaluation["decision_exploration"] = exploration_evaluation
        evaluation["decision_execution_assurance"] = execution_evaluation
        evaluation["decision_governance"] = decision_evaluation
        if (
            exploration_evaluation["status"] != "ACCEPTED"
            or execution_evaluation["status"] != "ACCEPTED"
            or decision_evaluation["status"] != "ACCEPTED"
        ):
            evaluation["status"] = "REJECTED"
            evaluation["findings"].extend(
                exploration_evaluation["findings"]
            )
            evaluation["findings"].extend(execution_evaluation["findings"])
            evaluation["findings"].extend(decision_evaluation["findings"])
            evaluation["semantic_claims"]["accepted"] = []

    evaluation["question_proposals"] = (
        questions_from_semantic_evaluation(
            graph=graph,
            capability=capability,
            evaluation=evaluation,
        )
        if evaluation["status"] != "ACCEPTED"
        else []
    )

    evaluation["admission"] = {
        "status": evaluation["status"],
        "knowledge_kind": knowledge_kind,
        "skill": route_by_kind[knowledge_kind],
        "acceptance_id": acceptance_id,
        "authority": authority,
        "allowed_source_authorities": sorted(allowed_source_authorities),
        "changed_paths": changed_paths,
        "canonical_references": references,
        "accepted_prerequisites": baseline,
        "accepted_prerequisite_semantics": semantic_baseline,
        "semantic_contract": "knowledge-kind-semantic-contracts/v1",
        "decision_exploration": exploration_evaluation["status"],
        "decision_explorer_request_id": (
            explorer_request.get("request_id")
            if isinstance(explorer_request, dict)
            else None
        ),
        "decision_execution_assurance": execution_evaluation["status"],
        "decision_governance": decision_evaluation["status"],
        "decision_request_mode": decision_request_mode,
    }
    if evaluation["status"] == "ACCEPTED":
        evaluation["lifecycle_assertion"] = {
            "artifact": candidate["id"],
            "capability": capability,
            "acceptance_id": acceptance_id,
            "accepted_prerequisites": baseline,
            **(
                {"accepted_prerequisite_semantics": semantic_baseline}
                if semantic_baseline
                else {}
            ),
            "semantic_atom_fingerprints": semantic_assertion_fingerprints(candidate),
        }
    return evaluation


def main() -> int:
    parser = argparse.ArgumentParser(description="Strict artifact semantic admission")
    parser.add_argument("graph")
    parser.add_argument("model")
    parser.add_argument("capability")
    parser.add_argument("sources")
    parser.add_argument("candidate")
    parser.add_argument("acceptance_id")
    parser.add_argument("--lifecycle")
    parser.add_argument(
        "--skill-registry",
        default="skills/artifact-skill-registry-v0.yaml",
    )
    parser.add_argument(
        "--knowledge-contracts",
        default="spec/semantic-acceptance/knowledge-kind-contracts-v1.yaml",
    )
    parser.add_argument(
        "--knowledge-contract-overlay",
        action="append",
        default=[],
    )
    parser.add_argument(
        "--decision-contracts",
        default="spec/decision-governance/knowledge-kind-decision-contracts-v1.yaml",
    )
    parser.add_argument("--decision-policy")
    parser.add_argument("--decision-exploration")
    parser.add_argument(
        "--derivation-evaluation",
        action="append",
        default=[],
    )
    parser.add_argument(
        "--decision-request-mode",
        choices=["CREATE", "REVISION", "REDO"],
        default="CREATE",
    )
    args = parser.parse_args()

    result = admit_artifact(
        graph=load_yaml(args.graph),
        model=load_yaml(args.model),
        skill_registry=load_yaml(args.skill_registry),
        knowledge_contracts=load_yaml(args.knowledge_contracts),
        knowledge_contract_overlays=[
            load_yaml(path) for path in args.knowledge_contract_overlay
        ],
        decision_contracts=load_yaml(args.decision_contracts),
        decision_policy=load_yaml(args.decision_policy) if args.decision_policy else None,
        decision_exploration=(
            load_yaml(args.decision_exploration)
            if args.decision_exploration
            else None
        ),
        derivation_evaluations=[
            load_yaml(path) for path in args.derivation_evaluation
        ],
        capability=args.capability,
        sources=load_yaml(args.sources),
        candidate=load_yaml(args.candidate),
        acceptance_id=args.acceptance_id,
        lifecycle=load_yaml(args.lifecycle) if args.lifecycle else None,
        decision_request_mode=args.decision_request_mode,
    )
    print(yaml.safe_dump(result, sort_keys=False, allow_unicode=True))
    return 0 if result["status"] == "ACCEPTED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
