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
from harness import CoreError, artifact_blockers, capability_blockers


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
        acceptance_policy_fingerprint = item.get("acceptance_policy_fingerprint")
        baseline = item.get("accepted_prerequisites", {})
        semantic_atoms = item.get("semantic_atom_fingerprints", {})
        semantic_baseline = item.get("accepted_prerequisite_semantics", {})
        if not all(isinstance(v, str) and v for v in (capability, artifact, acceptance_id)):
            raise CoreError("lifecycle provider artifact/capability/acceptance_id are required")
        if capability in result:
            raise CoreError(f"duplicate lifecycle capability: {capability}")
        if (
            acceptance_policy_fingerprint is not None
            and (
                not isinstance(acceptance_policy_fingerprint, str)
                or not acceptance_policy_fingerprint
            )
        ):
            raise CoreError(
                f"invalid acceptance policy fingerprint for {capability}"
            )
        if not isinstance(baseline, dict) or any(
            not isinstance(k, str)
            or not k
            or not isinstance(v, str)
            or not v
            for k, v in baseline.items()
        ):
            raise CoreError(f"invalid prerequisite baseline for {capability}")
        if not isinstance(semantic_atoms, dict) or any(
            not isinstance(k, str)
            or not k
            or not isinstance(v, str)
            or not v
            for k, v in semantic_atoms.items()
        ):
            raise CoreError(f"invalid semantic atom fingerprints for {capability}")
        if not isinstance(semantic_baseline, dict):
            raise CoreError(
                f"invalid prerequisite semantic baseline for {capability}"
            )
        for prerequisite, baseline_entry in semantic_baseline.items():
            if (
                not isinstance(prerequisite, str)
                or not prerequisite
                or not isinstance(baseline_entry, dict)
                or baseline_entry.get("exhaustive") is not True
                or not isinstance(baseline_entry.get("semantic_atoms"), dict)
                or not baseline_entry["semantic_atoms"]
                or any(
                    not isinstance(atom_id, str)
                    or not atom_id
                    or not isinstance(fingerprint, str)
                    or not fingerprint
                    for atom_id, fingerprint
                    in baseline_entry["semantic_atoms"].items()
                )
                or not isinstance(
                    baseline_entry.get("source_surface_fingerprints"), dict
                )
                or not baseline_entry["source_surface_fingerprints"]
                or any(
                    not isinstance(atom_id, str)
                    or not atom_id
                    or not isinstance(fingerprint, str)
                    or not fingerprint
                    for atom_id, fingerprint
                    in baseline_entry["source_surface_fingerprints"].items()
                )
            ):
                raise CoreError(
                    f"prerequisite semantic baseline for {capability} must be exhaustive and contain semantic_atoms plus source_surface_fingerprints"
                )
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

    active: dict[str, dict[str, Any]] = {}
    for capability, item in lifecycle.items():
        production = productions.get(capability)
        if production is None:
            # Graph evolution may retire a CapabilityId while historical/project
            # storage still contains its previous lifecycle assertion. It is
            # inert and must never be transferred to a new CapabilityId.
            continue

        artifact = artifacts.get(item["artifact"])
        if artifact is None or capability not in (artifact.get("provides", []) or []):
            raise CoreError(
                f"lifecycle provider does not match Core provider: {capability}"
            )

        accepted = set(item.get("accepted_prerequisites", {}))
        semantic_actual = set(item.get("accepted_prerequisite_semantics", {}))
        if not semantic_actual.issubset(accepted):
            raise CoreError(
                f"semantic lifecycle baseline for {capability} references prerequisites "
                f"outside its accepted baseline; expected subset of {sorted(accepted)}, "
                f"got {sorted(semantic_actual)}"
            )
        active[capability] = item
    return active


def obsolete_lifecycle_rows(
    graph: dict[str, Any],
    projection: dict[str, Any],
) -> list[dict[str, Any]]:
    """Return lifecycle assertions whose CapabilityIds are absent from the graph."""
    productions = production_index(graph)
    lifecycle = lifecycle_index(projection)
    return [
        {
            "capability": capability,
            "artifact": item["artifact"],
            "acceptance_id": item["acceptance_id"],
            "reason": "CAPABILITY_NOT_IN_ENGINEERING_GRAPH",
        }
        for capability, item in sorted(lifecycle.items())
        if capability not in productions
    ]


def lifecycle_states(
    graph: dict[str, Any],
    model: dict[str, Any],
    projection: dict[str, Any],
    *,
    current_acceptance_policy_fingerprints: dict[str, str] | None = None,
) -> dict[str, dict[str, Any]]:
    lifecycle = validate_projection(graph, model, projection)
    productions = production_index(graph)
    memo: dict[str, dict[str, Any]] = {}

    def required_capabilities(capability: str) -> list[str]:
        production = productions.get(capability)
        return (
            []
            if production is None
            else [r["capability"] for r in production["requires"]]
        )

    def changed_atom_rows(
        accepted_atoms: dict[str, str],
        current_atom_map: dict[str, str],
    ) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        for atom_id in sorted(set(accepted_atoms) | set(current_atom_map)):
            accepted_fingerprint = accepted_atoms.get(atom_id)
            current_fingerprint = current_atom_map.get(atom_id)
            if current_fingerprint != accepted_fingerprint:
                rows.append(
                    {
                        "id": atom_id,
                        "accepted_fingerprint": accepted_fingerprint,
                        "current_fingerprint": current_fingerprint,
                    }
                )
        return rows

    def finalize(capability: str) -> None:
        item = lifecycle.get(capability)
        if item is None:
            memo[capability] = {
                "state": "UNKNOWN",
                "capability": capability,
                "reason": "lifecycle coverage unavailable",
            }
            return

        required = required_capabilities(capability)
        mismatches: list[dict[str, Any]] = []
        baseline = item.get("accepted_prerequisites", {})
        accepted_topology = set(baseline)
        current_topology = set(required)
        if accepted_topology != current_topology:
            mismatches.append(
                {
                    "capability": capability,
                    "mode": "PREREQUISITE_TOPOLOGY",
                    "accepted_prerequisites": sorted(accepted_topology),
                    "current_prerequisites": sorted(current_topology),
                }
            )

        current_policy_fingerprint = (
            current_acceptance_policy_fingerprints.get(capability)
            if current_acceptance_policy_fingerprints is not None
            else None
        )
        accepted_policy_fingerprint = item.get(
            "acceptance_policy_fingerprint"
        )
        if (
            current_policy_fingerprint is not None
            and accepted_policy_fingerprint != current_policy_fingerprint
        ):
            mismatches.append(
                {
                    "capability": capability,
                    "mode": "ACCEPTANCE_POLICY",
                    "accepted_policy_fingerprint": accepted_policy_fingerprint,
                    "current_policy_fingerprint": current_policy_fingerprint,
                }
            )

        semantic_baseline = item.get("accepted_prerequisite_semantics", {})
        for prerequisite in required:
            upstream = memo[prerequisite]
            upstream_provider = lifecycle.get(prerequisite, {})
            current = upstream_provider.get("acceptance_id")
            accepted = baseline.get(prerequisite)

            if upstream["state"] != "CURRENT":
                mismatches.append(
                    {
                        "capability": prerequisite,
                        "mode": "UPSTREAM_STATE",
                        "accepted_acceptance_id": accepted,
                        "current_acceptance_id": current,
                        "upstream_state": upstream["state"],
                    }
                )
                continue

            semantic_entry = semantic_baseline.get(prerequisite)
            if semantic_entry is not None:
                consumed_atoms = semantic_entry["semantic_atoms"]
                accepted_surface = semantic_entry["source_surface_fingerprints"]
                current_atoms = upstream_provider.get(
                    "semantic_atom_fingerprints",
                    {},
                )
                consumed_changes = changed_atom_rows(
                    consumed_atoms,
                    {
                        atom_id: current_atoms.get(atom_id)
                        for atom_id in consumed_atoms
                    },
                )
                surface_changes = changed_atom_rows(
                    accepted_surface,
                    current_atoms,
                )
                if consumed_changes:
                    mismatches.append(
                        {
                            "capability": prerequisite,
                            "mode": "SEMANTIC_ATOMS",
                            "accepted_acceptance_id": accepted,
                            "current_acceptance_id": current,
                            "upstream_state": upstream["state"],
                            "changed_atoms": consumed_changes,
                        }
                    )
                elif surface_changes:
                    mismatches.append(
                        {
                            "capability": prerequisite,
                            "mode": "SEMANTIC_SURFACE",
                            "accepted_acceptance_id": accepted,
                            "current_acceptance_id": current,
                            "upstream_state": upstream["state"],
                            "changed_atoms": surface_changes,
                        }
                    )
                continue

            if accepted != current:
                mismatches.append(
                    {
                        "capability": prerequisite,
                        "mode": "CAPABILITY_ACCEPTANCE",
                        "accepted_acceptance_id": accepted,
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

    for root in productions:
        if root in memo:
            continue
        stack: list[tuple[str, bool]] = [(root, False)]
        while stack:
            capability, expanded = stack.pop()
            if capability in memo:
                continue
            if expanded:
                finalize(capability)
                continue

            item = lifecycle.get(capability)
            if item is None:
                finalize(capability)
                continue

            stack.append((capability, True))
            for prerequisite in reversed(required_capabilities(capability)):
                if prerequisite not in memo:
                    stack.append((prerequisite, False))

    return memo

def evaluate_lifecycle_target(
    graph: dict[str, Any],
    target: str,
    model: dict[str, Any],
    projection: dict[str, Any],
    *,
    current_acceptance_policy_fingerprints: dict[str, str] | None = None,
) -> dict[str, Any]:
    realized = validate_realization(graph, model)
    profile = derive_profile(graph, target)
    states = lifecycle_states(
        graph,
        realized,
        projection,
        current_acceptance_policy_fingerprints=current_acceptance_policy_fingerprints,
    )
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
                direct_blockers = set(
                    capability_blockers(realized, capability)
                )
                if selected:
                    provider_blockers = {
                        q
                        for a in selected
                        for q in artifact_blockers(realized, a["id"])
                    }
                else:
                    usable = [
                        a
                        for a in providers
                        if not artifact_blockers(realized, a["id"])
                    ]
                    provider_blockers = (
                        set()
                        if usable
                        else {
                            q
                            for a in providers
                            for q in artifact_blockers(realized, a["id"])
                        }
                    )
                blockers = sorted(direct_blockers | provider_blockers)
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
