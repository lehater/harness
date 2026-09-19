#!/usr/bin/env python3
"""Harness Engineering Graph v0: producer/consumer knowledge topology."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

import yaml

from harness import CoreError, validate_model
from target_state import evaluate_target_state, validate_profile


def _by_id(items: object, kind: str) -> dict[str, dict[str, Any]]:
    if not isinstance(items, list):
        raise CoreError(f"{kind}s must be a list")
    result: dict[str, dict[str, Any]] = {}
    for item in items:
        if not isinstance(item, dict):
            raise CoreError(f"{kind} must be a mapping")
        item_id = item.get("id")
        if not isinstance(item_id, str) or not item_id:
            raise CoreError(f"{kind} id is required")
        if item_id in result:
            raise CoreError(f"duplicate {kind} id: {item_id}")
        result[item_id] = item
    return result


def _requirement(value: object, where: str) -> dict[str, str]:
    if isinstance(value, str):
        value = {"capability": value}
    if not isinstance(value, dict):
        raise CoreError(f"{where} requirement must be a capability id or mapping")
    unknown = set(value) - {"capability", "subject"}
    if unknown:
        raise CoreError(f"{where} requirement has unknown fields: {sorted(unknown)}")
    capability = value.get("capability")
    if not isinstance(capability, str) or not capability:
        raise CoreError(f"{where} requirement capability is required")
    result = {"capability": capability}
    subject = value.get("subject")
    if subject is not None:
        if not isinstance(subject, str) or not subject:
            raise CoreError(f"{where} requirement subject must be a non-empty string")
        result["subject"] = subject
    return result


def _requirements(item: dict[str, Any], where: str) -> list[dict[str, str]]:
    values = item.get("requires", []) or []
    if not isinstance(values, list):
        raise CoreError(f"{where} requires must be a list")
    result = [_requirement(value, where) for value in values]
    keys = [(value["capability"], value.get("subject")) for value in result]
    if len(keys) != len(set(keys)):
        raise CoreError(f"{where} has duplicate requirements")
    return result


def validate_engineering_graph(graph: dict[str, Any]) -> None:
    if graph.get("version") != 1:
        raise CoreError("engineering graph version must be 1")
    if graph.get("kind") != "harness-engineering-graph":
        raise CoreError("unexpected engineering graph kind")
    if not isinstance(graph.get("id"), str) or not graph["id"]:
        raise CoreError("engineering graph id is required")
    default_subject = graph.get("default_subject", graph["id"])
    if not isinstance(default_subject, str) or not default_subject:
        raise CoreError("engineering graph default_subject must be a non-empty string")

    authorities = _by_id(graph.get("authorities", []), "authority")
    consumers = _by_id(graph.get("consumers", []), "consumer")
    if not consumers:
        raise CoreError("engineering graph must declare at least one consumer")
    overlap = set(authorities) & set(consumers)
    if overlap:
        raise CoreError(f"authority and consumer ids must be distinct: {sorted(overlap)}")

    producer_by_capability: dict[str, str] = {}
    for authority_id, authority in authorities.items():
        responsibility = authority.get("responsibility")
        if not isinstance(responsibility, str) or not responsibility.strip():
            raise CoreError(f"authority {authority_id} responsibility is required")

        boundary = authority.get("boundary")
        if not isinstance(boundary, dict):
            raise CoreError(f"authority {authority_id} boundary is required")
        for field in ("semantic_cohesion", "independent_change", "public_contract"):
            value = boundary.get(field)
            if not isinstance(value, str) or not value.strip():
                raise CoreError(
                    f"authority {authority_id} boundary.{field} is required"
                )

        produces = authority.get("produces", []) or []
        if not isinstance(produces, list):
            raise CoreError(f"authority {authority_id} produces must be a list")
        if len(produces) != len(set(produces)):
            raise CoreError(f"authority {authority_id} has duplicate produced capabilities")
        for capability in produces:
            if not isinstance(capability, str) or not capability:
                raise CoreError(f"authority {authority_id} has invalid produced capability")
            previous = producer_by_capability.setdefault(capability, authority_id)
            if previous != authority_id:
                raise CoreError(
                    f"capability {capability} has multiple producer Authorities: "
                    f"{previous}, {authority_id}"
                )

        _requirements(authority, f"authority {authority_id}")

    if not producer_by_capability:
        raise CoreError("engineering graph must declare at least one produced capability")

    for consumer_id, consumer in consumers.items():
        purpose = consumer.get("purpose")
        if not isinstance(purpose, str) or not purpose.strip():
            raise CoreError(f"consumer {consumer_id} purpose is required")
        _requirements(consumer, f"consumer {consumer_id}")

    # Every required capability must have a declared producer.
    all_requirements: list[tuple[str, dict[str, str]]] = []
    for authority_id, authority in authorities.items():
        all_requirements.extend(
            (f"authority {authority_id}", item)
            for item in _requirements(authority, f"authority {authority_id}")
        )
    for consumer_id, consumer in consumers.items():
        all_requirements.extend(
            (f"consumer {consumer_id}", item)
            for item in _requirements(consumer, f"consumer {consumer_id}")
        )

    subjects_by_capability: dict[str, set[str]] = {}
    for where, requirement in all_requirements:
        capability = requirement["capability"]
        if capability not in producer_by_capability:
            raise CoreError(
                f"{where} requires capability with no producer Authority: {capability}"
            )
        subject = requirement.get("subject")
        if subject is not None:
            subjects_by_capability.setdefault(capability, set()).add(subject)

    # v0 explicitly rejects the NAPMS false-positive pattern.
    for capability, subjects in subjects_by_capability.items():
        if len(subjects) > 1:
            raise CoreError(
                f"capability {capability} is required for multiple subjects {sorted(subjects)}; "
                "use distinct subject-scoped CapabilityIds in Engineering Graph v0"
            )

    # Stable producer dependency topology must be acyclic.
    dependencies: dict[str, set[str]] = {authority_id: set() for authority_id in authorities}
    for authority_id, authority in authorities.items():
        for requirement in _requirements(authority, f"authority {authority_id}"):
            producer = producer_by_capability[requirement["capability"]]
            if producer == authority_id:
                raise CoreError(
                    f"authority {authority_id} requires its own produced capability "
                    f"{requirement['capability']}"
                )
            dependencies[authority_id].add(producer)

    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(authority_id: str) -> None:
        if authority_id in visited:
            return
        if authority_id in visiting:
            raise CoreError(f"engineering Authority dependency cycle at: {authority_id}")
        visiting.add(authority_id)
        for dependency in dependencies[authority_id]:
            visit(dependency)
        visiting.remove(authority_id)
        visited.add(authority_id)

    for authority_id in authorities:
        visit(authority_id)


def producer_index(graph: dict[str, Any]) -> dict[str, str]:
    validate_engineering_graph(graph)
    result: dict[str, str] = {}
    for authority in graph["authorities"]:
        for capability in authority.get("produces", []) or []:
            result[capability] = authority["id"]
    return result


def _expectation_id(capability: str, subject: str) -> str:
    raw = f"{capability}-{subject}".upper()
    slug = re.sub(r"[^A-Z0-9]+", "-", raw).strip("-")
    return f"E-{slug}"


def derive_profile(graph: dict[str, Any], target_consumer: str) -> dict[str, Any]:
    validate_engineering_graph(graph)
    authorities = {item["id"]: item for item in graph["authorities"]}
    consumers = {item["id"]: item for item in graph["consumers"]}
    if target_consumer not in consumers:
        raise CoreError(f"unknown engineering target consumer: {target_consumer}")

    producers = producer_index(graph)
    default_subject = graph.get("default_subject", graph["id"])

    # capability -> one effective requirement. Multiple subjects for one broad capability
    # are rejected by validation; repeated same requirements collapse here.
    required: dict[str, dict[str, str]] = {}
    prerequisites: dict[str, set[str]] = {}

    def include(requirement: dict[str, str]) -> None:
        capability = requirement["capability"]
        subject = requirement.get("subject", default_subject)
        current = required.get(capability)
        if current is None:
            required[capability] = {"capability": capability, "subject": subject}
        elif current["subject"] != subject:
            raise CoreError(
                f"capability {capability} reached with conflicting subjects: "
                f"{current['subject']}, {subject}"
            )

        producer = producers[capability]
        upstream = _requirements(authorities[producer], f"authority {producer}")
        dependencies = prerequisites.setdefault(capability, set())
        for upstream_requirement in upstream:
            upstream_capability = upstream_requirement["capability"]
            dependencies.add(upstream_capability)
            if upstream_capability not in required:
                include(upstream_requirement)

    for requirement in _requirements(
        consumers[target_consumer], f"consumer {target_consumer}"
    ):
        include(requirement)

    expectation_ids = {
        capability: _expectation_id(item["capability"], item["subject"])
        for capability, item in required.items()
    }
    expectations: list[dict[str, Any]] = []
    for capability in sorted(required):
        item = required[capability]
        producer = producers[capability]
        expectation: dict[str, Any] = {
            "id": expectation_ids[capability],
            "subject": item["subject"],
            "capability": capability,
            "authority": producer,
        }
        deps = sorted(expectation_ids[value] for value in prerequisites.get(capability, set()))
        if deps:
            expectation["depends_on"] = deps
        expectations.append(expectation)

    profile = {
        "version": 1,
        "kind": "harness-design-profile",
        "id": f"{graph['id']}-{target_consumer}",
        "expectations": expectations,
    }
    validate_profile(profile)
    return profile


def validate_realization(graph: dict[str, Any], model: dict[str, Any]) -> None:
    validate_engineering_graph(graph)
    validate_model(model)
    producers = producer_index(graph)
    authorities = {item["id"] for item in graph["authorities"]}
    model_authorities = {item["id"] for item in model.get("authorities", [])}
    missing = sorted(authorities - model_authorities)
    if missing:
        raise CoreError(
            f"Core model is missing Engineering Graph Authorities: {missing}"
        )

    for artifact in model.get("artifacts", []):
        for capability in artifact.get("provides", []) or []:
            producer = producers.get(capability)
            if producer is None:
                continue
            if artifact["authority"] != producer:
                raise CoreError(
                    f"artifact {artifact['id']} provides {capability} under "
                    f"{artifact['authority']}, but Engineering Graph producer is {producer}"
                )


def evaluate_engineering_target(
    graph: dict[str, Any],
    target_consumer: str,
    model: dict[str, Any],
) -> dict[str, Any]:
    validate_realization(graph, model)
    profile = derive_profile(graph, target_consumer)
    result = evaluate_target_state(profile, model)
    return {
        "target": target_consumer,
        "profile": profile,
        **result,
    }


def _load(path: str | Path) -> dict[str, Any]:
    value = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise CoreError(f"{path} must contain a mapping")
    return value


def _emit(value: Any) -> None:
    print(json.dumps(value, indent=2, sort_keys=True))


def main() -> int:
    parser = argparse.ArgumentParser(description="Harness Engineering Graph v0")
    sub = parser.add_subparsers(dest="command", required=True)

    validate_cmd = sub.add_parser("validate")
    validate_cmd.add_argument("graph")

    profile_cmd = sub.add_parser("profile")
    profile_cmd.add_argument("graph")
    profile_cmd.add_argument("target")

    evaluate_cmd = sub.add_parser("evaluate")
    evaluate_cmd.add_argument("graph")
    evaluate_cmd.add_argument("target")
    evaluate_cmd.add_argument("model")

    args = parser.parse_args()
    graph = _load(args.graph)

    if args.command == "validate":
        validate_engineering_graph(graph)
        _emit({"valid": True})
    elif args.command == "profile":
        _emit(derive_profile(graph, args.target))
    elif args.command == "evaluate":
        _emit(
            evaluate_engineering_target(
                graph,
                args.target,
                _load(args.model),
            )
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
