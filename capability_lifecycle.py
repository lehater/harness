#!/usr/bin/env python3
"""Capability-granular semantic currentness evaluation.

This is the canonical runtime form of the lifecycle projection previously
validated experimentally against Nutrition Management and NAPMS.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml

from engineering_graph import derive_profile, production_index, validate_realization
from harness import CoreError, blocked, capability_blockers


def _load(path: str | Path) -> dict[str, Any]:
    value = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise CoreError(f"{path} must contain a mapping")
    return value


def lifecycle_index(projection: dict[str, Any]) -> dict[str, dict[str, Any]]:
    if projection.get("version") != 1 or projection.get("kind") != "harness-capability-lifecycle":
        raise CoreError("unexpected capability lifecycle projection")
    result: dict[str, dict[str, Any]] = {}
    for item in projection.get("providers", []) or []:
        if not isinstance(item, dict):
            raise CoreError("lifecycle provider must be a mapping")
        capability = item.get("capability")
        artifact = item.get("artifact")
        acceptance_id = item.get("acceptance_id")
        baseline = item.get("accepted_prerequisites", {})
        if not all(isinstance(v, str) and v for v in (capability, artifact, acceptance_id)):
            raise CoreError("lifecycle provider artifact/capability/acceptance_id are required")
        if capability in result:
            raise CoreError(f"duplicate lifecycle capability: {capability}")
        if not isinstance(baseline, dict) or any(
            not isinstance(k, str)
            or not k
            or not isinstance(v, str)
            or not v
            for k, v in baseline.items()
        ):
            raise CoreError(f"invalid prerequisite baseline for {capability}")
        result[capability] = item
    return result


def validate_projection(
    graph: dict[str, Any],
    model: dict[str, Any],
    projection: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    realized = validate_realization(graph, model)
    productions = production_index(graph)
    lifecycle = lifecycle_index(projection)
    artifacts = {a["id"]: a for a in realized.get("artifacts", []) or []}

    for capability, item in lifecycle.items():
        artifact = artifacts.get(item["artifact"])
        if artifact is None or capability not in (artifact.get("provides", []) or []):
            raise CoreError(
                f"lifecycle provider does not match Core provider: {capability}"
            )
        production = productions.get(capability)
        if production is None:
            raise CoreError(
                f"lifecycle capability is not in Engineering Graph production topology: {capability}"
            )
        expected = {r["capability"] for r in production["requires"]}
        actual = set(item.get("accepted_prerequisites", {}))
        if actual != expected:
            raise CoreError(
                f"lifecycle baseline for {capability} must cover exactly production prerequisites; "
                f"expected {sorted(expected)}, got {sorted(actual)}"
            )
    return lifecycle


def lifecycle_states(
    graph: dict[str, Any],
    model: dict[str, Any],
    projection: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    lifecycle = validate_projection(graph, model, projection)
    productions = production_index(graph)
    memo: dict[str, dict[str, Any]] = {}

    def state(capability: str) -> dict[str, Any]:
        if capability in memo:
            return memo[capability]

        item = lifecycle.get(capability)
        if item is None:
            result = {
                "state": "UNKNOWN",
                "capability": capability,
                "reason": "lifecycle coverage unavailable",
            }
            memo[capability] = result
            return result

        production = productions.get(capability)
        required = (
            []
            if production is None
            else [r["capability"] for r in production["requires"]]
        )
        mismatches: list[dict[str, Any]] = []
        baseline = item.get("accepted_prerequisites", {})

        for prerequisite in required:
            upstream = state(prerequisite)
            current = lifecycle.get(prerequisite, {}).get("acceptance_id")
            if (
                upstream["state"] != "CURRENT"
                or baseline.get(prerequisite) != current
            ):
                mismatches.append(
                    {
                        "capability": prerequisite,
                        "accepted_acceptance_id": baseline.get(prerequisite),
                        "current_acceptance_id": current,
                        "upstream_state": upstream["state"],
                    }
                )

        result = {
            "state": "STALE" if mismatches else "CURRENT",
            "capability": capability,
            "artifact": item["artifact"],
            "acceptance_id": item["acceptance_id"],
        }
        if mismatches:
            result["mismatches"] = mismatches
        memo[capability] = result
        return result

    for capability in productions:
        state(capability)
    return memo


def evaluate_lifecycle_target(
    graph: dict[str, Any],
    target: str,
    model: dict[str, Any],
    projection: dict[str, Any],
) -> dict[str, Any]:
    realized = validate_realization(graph, model)
    profile = derive_profile(graph, target)
    states = lifecycle_states(graph, realized, projection)
    artifacts = realized.get("artifacts", []) or []
    expectations = {e["id"]: e for e in profile["expectations"]}

    satisfied: list[str] = []
    create: list[dict[str, Any]] = []
    revalidate: list[dict[str, Any]] = []
    wait: list[dict[str, Any]] = []
    pending: list[dict[str, Any]] = []
    lifecycle_gaps: list[dict[str, Any]] = []
    remaining = set(expectations)

    while remaining:
        progressed = False
        for expectation_id in sorted(remaining):
            expectation = expectations[expectation_id]
            deps = expectation.get("depends_on", []) or []
            if any(dep not in satisfied for dep in deps):
                continue

            capability = expectation["capability"]
            providers = [
                a
                for a in artifacts
                if capability in (a.get("provides", []) or [])
            ]
            if not providers:
                blockers = capability_blockers(realized, capability)
                item = {
                    "expectation": expectation_id,
                    "capability": capability,
                    "authority": expectation["authority"],
                }
                if blockers:
                    wait.append(
                        {"action": "WAIT", **item, "questions": blockers}
                    )
                else:
                    create.append({"action": "CREATE", **item})
            else:
                lifecycle_provider = validate_projection(
                    graph, realized, projection
                ).get(capability)
                selected = [
                    a
                    for a in providers
                    if lifecycle_provider is not None
                    and a["id"] == lifecycle_provider["artifact"]
                ]
                blockers = sorted(
                    {
                        q
                        for a in (selected or providers)
                        for q in blocked(realized, a["id"])
                    }
                )
                if blockers:
                    wait.append(
                        {
                            "action": "WAIT",
                            "expectation": expectation_id,
                            "capability": capability,
                            "authority": expectation["authority"],
                            "questions": blockers,
                        }
                    )
                elif states[capability]["state"] == "CURRENT":
                    satisfied.append(expectation_id)
                elif states[capability]["state"] == "STALE":
                    revalidate.append(
                        {
                            "action": "REVALIDATE",
                            "expectation": expectation_id,
                            "capability": capability,
                            "authority": expectation["authority"],
                            "lifecycle": states[capability],
                        }
                    )
                else:
                    lifecycle_gaps.append(
                        {
                            "expectation": expectation_id,
                            "capability": capability,
                            "authority": expectation["authority"],
                            "lifecycle": states[capability],
                        }
                    )

            remaining.remove(expectation_id)
            progressed = True

        if not progressed:
            break

    for expectation_id in sorted(remaining):
        expectation = expectations[expectation_id]
        pending.append(
            {
                "action": "PENDING",
                "expectation": expectation_id,
                "capability": expectation["capability"],
                "authority": expectation["authority"],
                "depends_on": [
                    dep
                    for dep in expectation.get("depends_on", []) or []
                    if dep not in satisfied
                ],
            }
        )

    if len(satisfied) == len(expectations):
        status = "COMPLETE"
    elif create or revalidate:
        status = "READY"
    elif lifecycle_gaps:
        status = "INCOMPLETE"
    else:
        status = "BLOCKED"

    return {
        "status": status,
        "satisfied": sorted(satisfied),
        "create": create,
        "revalidate": revalidate,
        "wait": wait,
        "pending": pending,
        "lifecycle_gaps": lifecycle_gaps,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Evaluate capability semantic currentness"
    )
    parser.add_argument("graph")
    parser.add_argument("target")
    parser.add_argument("model")
    parser.add_argument("lifecycle")
    args = parser.parse_args()
    print(
        json.dumps(
            evaluate_lifecycle_target(
                _load(args.graph),
                args.target,
                _load(args.model),
                _load(args.lifecycle),
            ),
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
