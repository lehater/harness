#!/usr/bin/env python3
"""Derive executable Capability work for the sequential Decision Pipeline."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Iterable

import yaml

from authority_context import build_authority_context
from capability_lifecycle import lifecycle_index, lifecycle_states
from decision_explorer_request import derive_decision_explorer_request
from engineering_graph import (
    derive_profile,
    producer_index,
    production_index,
    validate_realization,
)
from harness import CoreError, blocked, capability_blockers

PIPELINE_STAGES = [
    "FORM_OPTIONS",
    "REVIEW_OPTIONS",
    "CHOOSE_OR_ESCALATE",
    "PRODUCE_CANDIDATE",
    "SEMANTIC_ADMISSION",
]


def _load(path: str | Path) -> dict[str, Any]:
    value = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise CoreError(f"{path} must contain a mapping")
    return value


def _core_providers(
    realized: dict[str, Any],
    capability: str,
) -> list[dict[str, Any]]:
    return [
        artifact
        for artifact in realized.get("artifacts", []) or []
        if capability in (artifact.get("provides", []) or [])
    ]


def _selected_provider(
    realized: dict[str, Any],
    lifecycle_by_capability: dict[str, dict[str, Any]],
    capability: str,
) -> dict[str, Any] | None:
    item = lifecycle_by_capability.get(capability)
    if item is None:
        return None
    artifact_id = item["artifact"]
    matches = [
        artifact
        for artifact in realized.get("artifacts", []) or []
        if artifact.get("id") == artifact_id
    ]
    if len(matches) > 1:
        raise CoreError(f"multiple artifacts with id {artifact_id}")
    return matches[0] if matches else None


def _direct_blockers(
    realized: dict[str, Any],
    lifecycle_by_capability: dict[str, dict[str, Any]],
    capability: str,
) -> list[str]:
    result = set(capability_blockers(realized, capability))
    provider = _selected_provider(realized, lifecycle_by_capability, capability)
    providers = [provider] if provider is not None else _core_providers(
        realized, capability
    )
    for candidate in providers:
        result.update(blocked(realized, candidate["id"]))
    return sorted(result)


def _prerequisite_gaps(
    production: dict[str, Any],
    states: dict[str, dict[str, Any]],
    lifecycle_by_capability: dict[str, dict[str, Any]],
    realized: dict[str, Any],
) -> list[dict[str, Any]]:
    gaps: list[dict[str, Any]] = []
    for requirement in production.get("requires", []) or []:
        capability = requirement["capability"]
        state = states.get(capability, {"state": "UNKNOWN"})
        questions = _direct_blockers(
            realized, lifecycle_by_capability, capability
        )
        if (
            state.get("state") != "CURRENT"
            or capability not in lifecycle_by_capability
            or questions
        ):
            gaps.append(
                {
                    "capability": capability,
                    "state": state.get("state", "UNKNOWN"),
                    "questions": questions,
                }
            )
    return gaps


def _authority_read_set(
    graph: dict[str, Any],
    realized: dict[str, Any],
    authority: str,
    capability: str,
    current_provider: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    context = build_authority_context(
        graph,
        realized,
        authority,
        [capability],
    )
    result: dict[str, dict[str, Any]] = {}
    for bucket in ("input_artifacts", "supporting_input_artifacts"):
        for item in context.get(bucket, []) or []:
            result[item["id"]] = {
                "artifact": item["id"],
                "authority": item["authority"],
                "path": item["path"],
                "provides": sorted(item.get("provides", []) or []),
            }
    if current_provider is not None:
        result[current_provider["id"]] = {
            "artifact": current_provider["id"],
            "authority": current_provider["authority"],
            "path": current_provider["path"],
            "provides": sorted(current_provider.get("provides", []) or []),
            "purpose": "CURRENT_ACCEPTED_BASELINE",
        }
    return sorted(result.values(), key=lambda item: item["artifact"])


def derive_decision_roadmap(
    *,
    graph: dict[str, Any],
    model: dict[str, Any],
    target: str,
    lifecycle: dict[str, Any],
    decision_contracts: dict[str, Any],
    decision_policy: dict[str, Any] | None,
    redo_capabilities: Iterable[str] = (),
) -> dict[str, Any]:
    """Derive work without role-specific frontiers or execution stops.

    A READY Capability is expected to run the whole Decision Pipeline in one
    execution. The roadmap is recomputed after each terminal capability result.
    """
    realized = validate_realization(graph, model)
    profile = derive_profile(graph, target)
    productions = production_index(graph)
    producers = producer_index(graph)
    lifecycle_by_capability = lifecycle_index(lifecycle)
    states = lifecycle_states(graph, realized, lifecycle)
    redo = set(redo_capabilities)

    selected = {
        item["capability"] for item in profile.get("expectations", []) or []
    }
    unknown_redo = sorted(redo - selected)
    if unknown_redo:
        raise CoreError(
            "explicit redo is outside selected target closure: "
            + ", ".join(unknown_redo)
        )

    ready: list[dict[str, Any]] = []
    completed: list[dict[str, Any]] = []
    blocked_items: list[dict[str, Any]] = []
    waiting: list[dict[str, Any]] = []
    lifecycle_gaps: list[dict[str, Any]] = []

    for expectation in profile["expectations"]:
        capability = expectation["capability"]
        production = productions[capability]
        authority = producers[capability]
        state = states.get(capability, {"state": "UNKNOWN"})
        prerequisite_gaps = _prerequisite_gaps(
            production,
            states,
            lifecycle_by_capability,
            realized,
        )
        if prerequisite_gaps:
            waiting.append(
                {
                    "capability": capability,
                    "authority": authority,
                    "state": "WAITING_UPSTREAM",
                    "prerequisites": prerequisite_gaps,
                }
            )
            continue

        questions = _direct_blockers(
            realized, lifecycle_by_capability, capability
        )
        if questions:
            blocked_items.append(
                {
                    "capability": capability,
                    "authority": authority,
                    "state": "BLOCKED",
                    "reason": "CORE_QUESTION",
                    "questions": questions,
                }
            )
            continue

        is_current = state.get("state") == "CURRENT"
        current_provider = _selected_provider(
            realized, lifecycle_by_capability, capability
        )
        if is_current and capability not in redo:
            completed.append(
                {
                    "capability": capability,
                    "authority": authority,
                    "state": "CURRENT",
                }
            )
            continue

        core_providers = _core_providers(realized, capability)
        if current_provider is None and core_providers:
            lifecycle_gaps.append(
                {
                    "capability": capability,
                    "authority": authority,
                    "state": "UNKNOWN",
                    "reason": "LIFECYCLE_ASSERTION_MISSING",
                    "providers": sorted(
                        provider["id"] for provider in core_providers
                    ),
                }
            )
            continue

        if capability in redo:
            if current_provider is None:
                raise CoreError(
                    f"explicit redo requires current provider for {capability}"
                )
            mode = "REDO"
            reason = "EXPLICIT_REDO"
        elif current_provider is not None:
            mode = "REVISION"
            reason = "REVISE_NONCURRENT_PROVIDER"
        else:
            mode = "CREATE"
            reason = "CREATE_MISSING_PROVIDER"

        request = derive_decision_explorer_request(
            graph=graph,
            model=realized,
            decision_contracts=decision_contracts,
            decision_policy=decision_policy,
            capability=capability,
            lifecycle=lifecycle,
            mode=mode,
        )
        governed = isinstance(request, dict)
        read_set = (
            request["canonical_inputs"]
            if governed
            else _authority_read_set(
                graph,
                realized,
                authority,
                capability,
                current_provider,
            )
        )
        stages = (
            list(PIPELINE_STAGES)
            if governed
            else ["PRODUCE_CANDIDATE", "SEMANTIC_ADMISSION"]
        )

        ready.append(
            {
                "capability": capability,
                "authority": authority,
                "knowledge_kind": production.get("knowledge_kind"),
                "reason": reason,
                "decision_governed": governed,
                "decision_request_mode": mode,
                "read_set": read_set,
                "decision_request": request,
                "pipeline": stages,
                "terminal_outcomes": [
                    "CURRENT",
                    "BLOCKED",
                    "FAILED_VALIDATION",
                ],
            }
        )

    return {
        "version": 1,
        "kind": "harness-decision-roadmap",
        "target": target,
        "frontier_status": "READY" if ready else "EMPTY",
        "ready": sorted(ready, key=lambda item: item["capability"]),
        "completed": sorted(completed, key=lambda item: item["capability"]),
        "blocked": sorted(blocked_items, key=lambda item: item["capability"]),
        "lifecycle_gaps": sorted(
            lifecycle_gaps, key=lambda item: item["capability"]
        ),
        "waiting_upstream": sorted(
            waiting, key=lambda item: item["capability"]
        ),
        "execution_rule": (
            "Run one READY capability through the complete pipeline, persist "
            "its outcome, then recompute this roadmap."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Derive sequential Decision Pipeline work"
    )
    parser.add_argument("graph")
    parser.add_argument("model")
    parser.add_argument("target")
    parser.add_argument("lifecycle")
    parser.add_argument("decision_policy")
    parser.add_argument("--redo", action="append", default=[])
    parser.add_argument(
        "--decision-contracts",
        default="spec/decision-governance/knowledge-kind-decision-contracts-v1.yaml",
    )
    args = parser.parse_args()

    value = derive_decision_roadmap(
        graph=_load(args.graph),
        model=_load(args.model),
        target=args.target,
        lifecycle=_load(args.lifecycle),
        decision_contracts=_load(args.decision_contracts),
        decision_policy=_load(args.decision_policy),
        redo_capabilities=args.redo,
    )
    print(json.dumps(value, indent=2, sort_keys=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
