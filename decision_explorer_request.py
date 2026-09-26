#!/usr/bin/env python3
"""Derive a candidate-free execution request for Decision Exploration."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import yaml

from authority_context import build_authority_context
from capability_lifecycle import lifecycle_index, lifecycle_states
from decision_governance import axis_policies, decision_contract_index
from engineering_graph import producer_index, production_index, validate_realization
from harness import CoreError


def _canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )


def _request_id(payload: dict[str, Any]) -> str:
    digest = hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()
    return f"sha256:{digest}"


def build_decision_explorer_request(
    *,
    capability: str,
    knowledge_kind: str,
    authority: str,
    authority_context: dict[str, Any],
    contract: dict[str, Any] | None,
    axis_policies: dict[str, dict[str, str]] | None,
    prerequisite_baseline: dict[str, str],
    model: dict[str, Any],
) -> dict[str, Any] | None:
    """Build the exact allowed input manifest for a pre-choice explorer.

    The request intentionally excludes the current/candidate provider artifact and
    every write target. It contains only accepted prerequisite/support manifests,
    unresolved Core Questions, downstream consumer identities, the decision
    contract and effective exploration policy.
    """
    if contract is None or not contract.get("required") or axis_policies is None:
        return None

    if authority_context.get("authority") != authority:
        raise CoreError("decision explorer Authority context mismatch")
    if capability not in (authority_context.get("selected_outputs", []) or []):
        raise CoreError("decision explorer capability is outside Authority context")

    inputs: list[dict[str, Any]] = []
    for bucket in ("input_artifacts", "supporting_input_artifacts"):
        for item in authority_context.get(bucket, []) or []:
            if not isinstance(item, dict):
                continue
            inputs.append(
                {
                    "id": item["id"],
                    "authority": item["authority"],
                    "path": item["path"],
                    "provides": sorted(item.get("provides", []) or []),
                }
            )
    inputs = sorted(
        {item["id"]: item for item in inputs}.values(),
        key=lambda item: item["id"],
    )

    axes = []
    for axis, axis_contract in contract["axes"].items():
        effective = axis_policies[axis]
        axes.append(
            {
                "axis": axis,
                "exploration": effective["exploration"],
                "material_dimensions": list(axis_contract["material_dimensions"]),
                "challenge_strategies": list(
                    axis_contract["challenge_strategies"]
                ),
                "minimum_probes": axis_contract["minimum_probes"],
            }
        )

    payload = {
        "version": 1,
        "kind": "harness-decision-explorer-request",
        "capability": capability,
        "knowledge_kind": knowledge_kind,
        "authority": authority,
        "accepted_prerequisites": dict(
            sorted(prerequisite_baseline.items())
        ),
        "canonical_inputs": inputs,
        "downstream_consumers": authority_context.get(
            "downstream_consumers", []
        ),
        "axes": axes,
        "forbidden_inputs": [
            "candidate",
            "candidate_artifact",
            "decision_review",
            "preferred_solution",
            "selected_solution",
            "write_set",
        ],
    }
    return {**payload, "request_id": _request_id(payload)}


def validate_explorer_request_binding(
    *,
    expected_request: dict[str, Any] | None,
    evidence: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    if expected_request is None:
        return []
    if not isinstance(evidence, dict):
        return []
    actual = evidence.get("explorer_request_id")
    expected = expected_request["request_id"]
    if actual != expected:
        return [
            {
                "code": "DECISION_EXPLORER_REQUEST_MISMATCH",
                "expected": expected,
                "actual": actual,
            }
        ]
    return []



def derive_decision_explorer_request(
    *,
    graph: dict[str, Any],
    model: dict[str, Any],
    decision_contracts: dict[str, Any],
    decision_policy: dict[str, Any] | None,
    capability: str,
    lifecycle: dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    realized = validate_realization(graph, model)
    productions = production_index(graph)
    producers = producer_index(graph)
    production = productions.get(capability)
    if production is None:
        raise CoreError(f"unknown produced capability: {capability}")
    knowledge_kind = production.get("knowledge_kind")
    if not isinstance(knowledge_kind, str) or not knowledge_kind:
        raise CoreError(f"capability {capability} requires knowledge_kind")
    authority = producers[capability]
    contract = decision_contract_index(decision_contracts).get(knowledge_kind)
    policies = axis_policies(contract, decision_policy)
    if contract is None or policies is None:
        return None

    context = build_authority_context(
        graph,
        realized,
        authority,
        [capability],
    )
    if context["status"] not in {"ROOT", "READY"}:
        raise CoreError(
            f"Authority {authority} cannot explore {capability}: "
            f"context status {context['status']}"
        )

    prerequisites = [
        item["capability"] for item in production.get("requires", []) or []
    ]
    baseline: dict[str, str] = {}
    if prerequisites:
        if lifecycle is None:
            raise CoreError(
                f"capability {capability} has prerequisites and requires "
                "lifecycle evidence for explorer request generation"
            )
        states = lifecycle_states(graph, realized, lifecycle)
        index = lifecycle_index(lifecycle)
        for prerequisite in prerequisites:
            if states[prerequisite]["state"] != "CURRENT":
                raise CoreError(
                    f"explorer prerequisite {prerequisite} is "
                    f"{states[prerequisite]['state']}, not CURRENT"
                )
            baseline[prerequisite] = index[prerequisite]["acceptance_id"]

    return build_decision_explorer_request(
        capability=capability,
        knowledge_kind=knowledge_kind,
        authority=authority,
        authority_context=context,
        contract=contract,
        axis_policies=policies,
        prerequisite_baseline=baseline,
        model=realized,
    )


def _load(path: str | Path) -> dict[str, Any]:
    value = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise CoreError(f"{path} must contain a mapping")
    return value


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate candidate-free Decision Explorer request"
    )
    parser.add_argument("graph")
    parser.add_argument("model")
    parser.add_argument("capability")
    parser.add_argument("decision_policy")
    parser.add_argument("--lifecycle")
    parser.add_argument(
        "--decision-contracts",
        default="spec/decision-governance/knowledge-kind-decision-contracts-v1.yaml",
    )
    args = parser.parse_args()
    request = derive_decision_explorer_request(
        graph=_load(args.graph),
        model=_load(args.model),
        decision_contracts=_load(args.decision_contracts),
        decision_policy=_load(args.decision_policy),
        capability=args.capability,
        lifecycle=_load(args.lifecycle) if args.lifecycle else None,
    )
    if request is None:
        print(json.dumps({"status": "NOT_REQUIRED"}, indent=2))
        return 0
    print(json.dumps(request, indent=2, sort_keys=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
