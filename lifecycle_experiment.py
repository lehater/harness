#!/usr/bin/env python3
"""Experimental lifecycle-aware evaluation for accepted engineering knowledge.

This module intentionally does not change Core v0. It overlays optional revision
and accepted-prerequisite-baseline facts on a normal Core realization and uses
Engineering Graph production prerequisites for semantic staleness propagation.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml

from engineering_graph import (
    derive_profile,
    production_index,
    validate_engineering_graph,
    validate_realization,
)
from harness import CoreError, blocked, capability_blockers
from target_state import validate_profile


def _load(path: str | Path) -> dict[str, Any]:
    value = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise CoreError(f"{path} must contain a mapping")
    return value


def _providers(model: dict[str, Any]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for artifact in model.get("artifacts", []):
        for capability in artifact.get("provides", []) or []:
            if capability in result:
                raise CoreError(
                    f"lifecycle experiment requires one current provider per capability: {capability}"
                )
            result[capability] = artifact
    return result


def validate_lifecycle_metadata(
    graph: dict[str, Any], model: dict[str, Any]
) -> dict[str, dict[str, Any]]:
    realized = validate_realization(graph, model)
    productions = production_index(graph)
    providers = _providers(realized)

    revisions: set[str] = set()
    for artifact in realized.get("artifacts", []):
        revision = artifact.get("revision")
        baseline = artifact.get("accepted_prerequisites")
        if revision is None and baseline is None:
            continue
        if not isinstance(revision, str) or not revision:
            raise CoreError(f"artifact {artifact['id']} revision is required with lifecycle metadata")
        if revision in revisions:
            raise CoreError(f"duplicate artifact revision identity: {revision}")
        revisions.add(revision)
        if not isinstance(baseline, dict):
            raise CoreError(
                f"artifact {artifact['id']} accepted_prerequisites must be a mapping"
            )
        if any(
            not isinstance(capability, str)
            or not capability
            or not isinstance(value, str)
            or not value
            for capability, value in baseline.items()
        ):
            raise CoreError(
                f"artifact {artifact['id']} accepted_prerequisites must map capability ids to revision ids"
            )

        expected: set[str] = set()
        for capability in artifact.get("provides", []) or []:
            production = productions.get(capability)
            if production is None:
                continue
            expected.update(req["capability"] for req in production["requires"])
        unknown = set(baseline) - expected
        if unknown:
            raise CoreError(
                f"artifact {artifact['id']} baseline contains non-prerequisites: {sorted(unknown)}"
            )

    return providers


def lifecycle_states(
    graph: dict[str, Any], model: dict[str, Any]
) -> dict[str, dict[str, Any]]:
    validate_engineering_graph(graph)
    providers = validate_lifecycle_metadata(graph, model)
    productions = production_index(graph)
    memo: dict[str, dict[str, Any]] = {}

    def state(capability: str) -> dict[str, Any]:
        if capability in memo:
            return memo[capability]
        artifact = providers.get(capability)
        if artifact is None:
            result = {"state": "MISSING", "capability": capability}
            memo[capability] = result
            return result

        revision = artifact.get("revision")
        baseline = artifact.get("accepted_prerequisites")
        production = productions.get(capability)
        required = [] if production is None else [
            req["capability"] for req in production["requires"]
        ]

        if revision is None or baseline is None:
            result = {
                "state": "UNKNOWN",
                "capability": capability,
                "provider": artifact["id"],
                "reason": "lifecycle metadata unavailable",
            }
            memo[capability] = result
            return result

        mismatches: list[dict[str, Any]] = []
        for prerequisite in required:
            upstream = state(prerequisite)
            upstream_artifact = providers.get(prerequisite)
            current_revision = (
                upstream_artifact.get("revision") if upstream_artifact is not None else None
            )
            accepted_revision = baseline.get(prerequisite)
            if upstream["state"] != "CURRENT" or accepted_revision != current_revision:
                mismatches.append({
                    "capability": prerequisite,
                    "accepted_revision": accepted_revision,
                    "current_revision": current_revision,
                    "upstream_state": upstream["state"],
                })

        result = {
            "state": "STALE" if mismatches else "CURRENT",
            "capability": capability,
            "provider": artifact["id"],
            "revision": revision,
        }
        if mismatches:
            result["mismatches"] = mismatches
        memo[capability] = result
        return result

    for capability in productions:
        state(capability)
    return memo


def evaluate_lifecycle_target(
    graph: dict[str, Any], target_consumer: str, model: dict[str, Any]
) -> dict[str, Any]:
    realized = validate_realization(graph, model)
    profile = derive_profile(graph, target_consumer)
    validate_profile(profile, realized)
    states = lifecycle_states(graph, realized)
    artifacts = realized.get("artifacts", [])
    expectations = {item["id"]: item for item in profile["expectations"]}

    satisfied: list[str] = []
    revalidate: list[dict[str, Any]] = []
    create: list[dict[str, Any]] = []
    wait: list[dict[str, Any]] = []
    pending: list[dict[str, Any]] = []
    remaining = set(expectations)

    while remaining:
        progressed = False
        for expectation_id in sorted(remaining):
            expectation = expectations[expectation_id]
            deps = expectation.get("depends_on", [])
            unresolved = [dep for dep in deps if dep not in satisfied]
            if unresolved:
                continue
            capability = expectation["capability"]
            providers = [
                artifact for artifact in artifacts
                if capability in (artifact.get("provides", []) or [])
            ]
            if not providers:
                blockers = capability_blockers(realized, capability)
                item = {
                    "expectation": expectation_id,
                    "capability": capability,
                    "authority": expectation["authority"],
                }
                if blockers:
                    wait.append({"action": "WAIT", **item, "questions": blockers})
                else:
                    create.append({"action": "CREATE", **item})
                remaining.remove(expectation_id)
                progressed = True
                continue

            blockers = sorted({
                question
                for provider in providers
                for question in blocked(realized, provider["id"])
            })
            if blockers:
                wait.append({
                    "action": "WAIT",
                    "expectation": expectation_id,
                    "capability": capability,
                    "authority": expectation["authority"],
                    "questions": blockers,
                })
                remaining.remove(expectation_id)
                progressed = True
                continue

            lifecycle = states[capability]
            if lifecycle["state"] == "CURRENT":
                satisfied.append(expectation_id)
            else:
                revalidate.append({
                    "action": "REVALIDATE",
                    "expectation": expectation_id,
                    "capability": capability,
                    "authority": expectation["authority"],
                    "lifecycle": lifecycle,
                })
            remaining.remove(expectation_id)
            progressed = True

        if not progressed:
            break

    for expectation_id in sorted(remaining):
        expectation = expectations[expectation_id]
        pending.append({
            "action": "PENDING",
            "expectation": expectation_id,
            "capability": expectation["capability"],
            "authority": expectation["authority"],
            "depends_on": [dep for dep in expectation.get("depends_on", []) if dep not in satisfied],
        })

    status = "COMPLETE" if len(satisfied) == len(expectations) else (
        "READY" if create or revalidate else "BLOCKED"
    )
    return {
        "status": status,
        "satisfied": sorted(satisfied),
        "create": create,
        "revalidate": revalidate,
        "wait": wait,
        "pending": pending,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Experimental Harness lifecycle evaluator")
    parser.add_argument("graph")
    parser.add_argument("target")
    parser.add_argument("model")
    args = parser.parse_args()
    print(json.dumps(
        evaluate_lifecycle_target(_load(args.graph), args.target, _load(args.model)),
        indent=2,
        sort_keys=True,
    ))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
