#!/usr/bin/env python3
"""Derive a bounded execution context for one Engineering Graph Authority."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml

from engineering_graph import (
    producer_index,
    production_index,
    realize_core_model,
    validate_engineering_graph,
)
from harness import (
    CoreError,
    blocked,
    capability_blockers,
    capability_resolve,
    validate_model,
)


def _artifacts(model: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {item["id"]: item for item in model.get("artifacts", []) or []}


def _same_authority_closure(
    artifact_id: str,
    artifacts: dict[str, dict[str, Any]],
) -> set[str]:
    owner = artifacts[artifact_id]["authority"]
    result: set[str] = set()
    stack = [artifact_id]
    while stack:
        current = stack.pop()
        for dep in artifacts[current].get("depends_on", []) or []:
            if dep not in artifacts:
                raise CoreError(
                    f"artifact {current} depends on unknown artifact: {dep}"
                )
            if artifacts[dep]["authority"] != owner:
                continue
            if dep not in result:
                result.add(dep)
                stack.append(dep)
    return result


def build_authority_context(
    graph: dict[str, Any],
    model: dict[str, Any],
    authority_id: str,
) -> dict[str, Any]:
    validate_engineering_graph(graph)
    realized = realize_core_model(graph, model)
    validate_model(realized)

    authorities = {item["id"]: item for item in graph["authorities"]}
    if authority_id not in authorities:
        raise CoreError(f"unknown Engineering Graph Authority: {authority_id}")

    producers = producer_index(graph)
    productions = production_index(graph)
    artifacts = _artifacts(realized)

    owned = sorted(
        (
            {
                "id": artifact_id,
                "path": artifact["path"],
                "provides": sorted(artifact.get("provides", []) or []),
            }
            for artifact_id, artifact in artifacts.items()
            if artifact["authority"] == authority_id
        ),
        key=lambda item: item["id"],
    )

    public_outputs = sorted(
        capability
        for capability, owner in producers.items()
        if owner == authority_id
    )

    required_caps: dict[str, dict[str, Any]] = {}
    for capability in public_outputs:
        for requirement in productions[capability].get("requires", []) or []:
            required_caps.setdefault(requirement["capability"], requirement)

    requirements: list[dict[str, Any]] = []
    input_artifact_ids: set[str] = set()
    support_artifact_ids: set[str] = set()
    blockers: list[dict[str, Any]] = []

    for capability in sorted(required_caps):
        expected_authority = producers[capability]
        direct_capability_blockers = capability_blockers(realized, capability)
        providers: list[str] = []
        provider_blockers: set[str] = set()
        try:
            providers = capability_resolve(realized, capability)
        except CoreError:
            providers = []

        if providers:
            for provider in providers:
                if artifacts[provider]["authority"] != expected_authority:
                    raise CoreError(
                        f"capability {capability} provider {provider} belongs to "
                        f"{artifacts[provider]['authority']}, expected {expected_authority}"
                    )
                input_artifact_ids.add(provider)
                support_artifact_ids.update(
                    _same_authority_closure(provider, artifacts)
                )
                provider_blockers.update(blocked(realized, provider))

        all_blockers = sorted(
            set(direct_capability_blockers) | provider_blockers
        )
        if all_blockers:
            status = "WAIT"
        elif providers:
            status = "SATISFIED"
        else:
            status = "DESIGN_GAP"

        row = {
            "capability": capability,
            "authority": expected_authority,
            "status": status,
            "providers": sorted(providers),
            "blocked_by": all_blockers,
        }
        requirements.append(row)
        if status != "SATISFIED":
            blockers.append(row)

    support_artifact_ids.difference_update(input_artifact_ids)
    own_ids = {item["id"] for item in owned}
    support_artifact_ids.difference_update(own_ids)

    def info(artifact_id: str) -> dict[str, Any]:
        artifact = artifacts[artifact_id]
        return {
            "id": artifact_id,
            "authority": artifact["authority"],
            "path": artifact["path"],
            "provides": sorted(artifact.get("provides", []) or []),
        }

    input_artifacts = [info(item) for item in sorted(input_artifact_ids)]
    supporting_input_artifacts = [
        info(item) for item in sorted(support_artifact_ids)
    ]

    downstream: list[dict[str, Any]] = []
    public_set = set(public_outputs)
    for capability, production in productions.items():
        consumed = sorted(
            {
                requirement["capability"]
                for requirement in production.get("requires", []) or []
            } & public_set
        )
        if consumed:
            downstream.append(
                {
                    "kind": "production",
                    "consumer": capability,
                    "authority": producers[capability],
                    "capabilities": consumed,
                }
            )
    for consumer in graph.get("consumers", []) or []:
        consumed = sorted(
            {
                (
                    requirement
                    if isinstance(requirement, str)
                    else requirement["capability"]
                )
                for requirement in consumer.get("requires", []) or []
            } & public_set
        )
        if consumed:
            downstream.append(
                {
                    "kind": "consumer",
                    "consumer": consumer["id"],
                    "capabilities": consumed,
                }
            )

    status = "ROOT" if not requirements else ("BLOCKED" if blockers else "READY")

    allowed_reads = sorted(
        {
            item["path"]
            for item in input_artifacts + supporting_input_artifacts + owned
        }
    )
    allowed_writes = sorted(item["path"] for item in owned)

    return {
        "kind": "harness-authority-execution-context",
        "authority": authority_id,
        "status": status,
        "responsibility": authorities[authority_id]["responsibility"],
        "requirements": requirements,
        "input_artifacts": input_artifacts,
        "supporting_input_artifacts": supporting_input_artifacts,
        "owned_artifacts": owned,
        "public_outputs": public_outputs,
        "downstream_consumers": sorted(
            downstream,
            key=lambda item: (item["kind"], item["consumer"]),
        ),
        "blockers": blockers,
        "access": {
            "read": allowed_reads,
            "write": allowed_writes,
        },
    }


def validate_write_set(
    context: dict[str, Any],
    changed_paths: list[str],
) -> list[str]:
    if context["status"] == "BLOCKED":
        raise CoreError(
            f"Authority {context['authority']} is BLOCKED; canonical artifact production is not allowed"
        )
    allowed = set(context["access"]["write"])
    normalized = sorted(
        {
            Path(path).as_posix().lstrip("./")
            for path in changed_paths
        }
    )
    outside = sorted(set(normalized) - allowed)
    if outside:
        raise CoreError(
            f"Authority {context['authority']} may not write outside owned canonical artifacts: {outside}"
        )
    return normalized


def validate_extracted_references(
    context: dict[str, Any],
    references: list[dict[str, str]],
) -> list[dict[str, str]]:
    """Validate references extracted by a project-specific adapter.

    Harness owns the allowed read boundary; projects remain free to decide how
    references are extracted from YAML, DSL, Markdown or other canonical forms.
    """
    allowed = set(context["access"]["read"])
    violations = [
        item
        for item in references
        if item.get("referenced_path") not in allowed
    ]
    if violations:
        raise CoreError(
            f"Authority {context['authority']} has canonical references outside "
            f"its execution context: {violations}"
        )
    return references


def _load(path: str) -> dict[str, Any]:
    value = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise CoreError(f"{path} must contain a mapping")
    return value


def main() -> int:
    parser = argparse.ArgumentParser(description="Harness Authority execution context")
    parser.add_argument("engineering_graph")
    parser.add_argument("core_model")
    parser.add_argument("authority")
    parser.add_argument("--check-write", nargs="*")
    args = parser.parse_args()

    context = build_authority_context(
        _load(args.engineering_graph),
        _load(args.core_model),
        args.authority,
    )
    if args.check_write is not None:
        context["validated_write_set"] = validate_write_set(
            context,
            args.check_write,
        )
    print(json.dumps(context, indent=2, sort_keys=False))
    return 2 if context["status"] == "BLOCKED" else 0


if __name__ == "__main__":
    raise SystemExit(main())
