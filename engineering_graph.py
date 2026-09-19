#!/usr/bin/env python3
"""Harness Engineering Graph v0: producer/consumer knowledge topology."""
from __future__ import annotations

import argparse
import copy
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


def _requirements(values: object, where: str) -> list[dict[str, str]]:
    if values is None:
        values = []
    if not isinstance(values, list):
        raise CoreError(f"{where} requires must be a list")
    result = [_requirement(value, where) for value in values]
    keys = [(value["capability"], value.get("subject")) for value in result]
    if len(keys) != len(set(keys)):
        raise CoreError(f"{where} has duplicate requirements")
    return result


def _production(value: object, authority_id: str) -> dict[str, Any]:
    where = f"authority {authority_id} production"
    if isinstance(value, str):
        value = {"capability": value, "requires": []}
    if not isinstance(value, dict):
        raise CoreError(f"{where} must be a capability id or mapping")
    unknown = set(value) - {"capability", "requires", "knowledge_kind"}
    if unknown:
        raise CoreError(f"{where} has unknown fields: {sorted(unknown)}")
    capability = value.get("capability")
    if not isinstance(capability, str) or not capability:
        raise CoreError(f"{where} capability is required")
    knowledge_kind = value.get("knowledge_kind")
    if knowledge_kind is not None and (
        not isinstance(knowledge_kind, str) or not knowledge_kind
    ):
        raise CoreError(f"{where} knowledge_kind must be a non-empty string")
    result = {
        "capability": capability,
        "requires": _requirements(
            value.get("requires", []),
            f"production {capability}",
        ),
    }
    if knowledge_kind is not None:
        result["knowledge_kind"] = knowledge_kind
    return result


def _productions(authority: dict[str, Any]) -> list[dict[str, Any]]:
    authority_id = authority["id"]
    values = authority.get("produces", []) or []
    if not isinstance(values, list):
        raise CoreError(f"authority {authority_id} produces must be a list")
    result = [_production(value, authority_id) for value in values]
    capabilities = [item["capability"] for item in result]
    if len(capabilities) != len(set(capabilities)):
        raise CoreError(f"authority {authority_id} has duplicate produced capabilities")
    return result


def _consumer_requirements(consumer: dict[str, Any]) -> list[dict[str, str]]:
    return _requirements(
        consumer.get("requires", []),
        f"consumer {consumer['id']}",
    )


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
    production_by_capability: dict[str, dict[str, Any]] = {}

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

        if "requires" in authority:
            raise CoreError(
                f"authority {authority_id} must declare prerequisites per produced capability; "
                "top-level authority.requires is not part of Engineering Graph v0"
            )

        for production in _productions(authority):
            capability = production["capability"]
            previous = producer_by_capability.setdefault(capability, authority_id)
            if previous != authority_id:
                raise CoreError(
                    f"capability {capability} has multiple producer Authorities: "
                    f"{previous}, {authority_id}"
                )
            production_by_capability[capability] = production

    if not producer_by_capability:
        raise CoreError("engineering graph must declare at least one produced capability")

    for consumer_id, consumer in consumers.items():
        purpose = consumer.get("purpose")
        if not isinstance(purpose, str) or not purpose.strip():
            raise CoreError(f"consumer {consumer_id} purpose is required")
        _consumer_requirements(consumer)

    # Every production prerequisite and consumer requirement needs a semantic producer.
    all_requirements: list[tuple[str, dict[str, str]]] = []
    for capability, production in production_by_capability.items():
        all_requirements.extend(
            (f"production {capability}", item)
            for item in production["requires"]
        )
    for consumer_id, consumer in consumers.items():
        all_requirements.extend(
            (f"consumer {consumer_id}", item)
            for item in _consumer_requirements(consumer)
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

    # v0 rejects the NAPMS false-positive pattern explicitly.
    for capability, subjects in subjects_by_capability.items():
        if len(subjects) > 1:
            raise CoreError(
                f"capability {capability} is required for multiple subjects {sorted(subjects)}; "
                "use distinct subject-scoped CapabilityIds in Engineering Graph v0"
            )

    # Stable capability production topology must be a DAG.
    dependencies: dict[str, set[str]] = {
        capability: {
            requirement["capability"]
            for requirement in production["requires"]
        }
        for capability, production in production_by_capability.items()
    }

    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(capability: str) -> None:
        if capability in visited:
            return
        if capability in visiting:
            raise CoreError(
                f"engineering capability production cycle at: {capability}"
            )
        visiting.add(capability)
        for dependency in dependencies[capability]:
            visit(dependency)
        visiting.remove(capability)
        visited.add(capability)

    for capability in dependencies:
        visit(capability)


def producer_index(graph: dict[str, Any]) -> dict[str, str]:
    validate_engineering_graph(graph)
    result: dict[str, str] = {}
    for authority in graph["authorities"]:
        for production in _productions(authority):
            result[production["capability"]] = authority["id"]
    return result


def production_index(graph: dict[str, Any]) -> dict[str, dict[str, Any]]:
    validate_engineering_graph(graph)
    result: dict[str, dict[str, Any]] = {}
    for authority in graph["authorities"]:
        for production in _productions(authority):
            result[production["capability"]] = production
    return result


def _expectation_id(capability: str, subject: str) -> str:
    raw = f"{capability}-{subject}".upper()
    slug = re.sub(r"[^A-Z0-9]+", "-", raw).strip("-")
    return f"E-{slug}"


def derive_profile(graph: dict[str, Any], target_consumer: str) -> dict[str, Any]:
    validate_engineering_graph(graph)
    consumers = {item["id"]: item for item in graph["consumers"]}
    if target_consumer not in consumers:
        raise CoreError(f"unknown engineering target consumer: {target_consumer}")

    producers = producer_index(graph)
    productions = production_index(graph)
    default_subject = graph.get("default_subject", graph["id"])

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

        upstream = productions[capability]["requires"]
        dependencies = prerequisites.setdefault(capability, set())
        for upstream_requirement in upstream:
            upstream_capability = upstream_requirement["capability"]
            dependencies.add(upstream_capability)
            if upstream_capability not in required:
                include(upstream_requirement)

    for requirement in _consumer_requirements(consumers[target_consumer]):
        include(requirement)

    expectation_ids = {
        capability: _expectation_id(item["capability"], item["subject"])
        for capability, item in required.items()
    }
    expectations: list[dict[str, Any]] = []
    for capability in sorted(required):
        item = required[capability]
        expectation: dict[str, Any] = {
            "id": expectation_ids[capability],
            "subject": item["subject"],
            "capability": capability,
            "authority": producers[capability],
        }
        deps = sorted(
            expectation_ids[value]
            for value in prerequisites.get(capability, set())
        )
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


def realize_core_model(
    graph: dict[str, Any],
    model: dict[str, Any],
) -> dict[str, Any]:
    """Project Engineering Graph Authorities into a Core realization state."""
    validate_engineering_graph(graph)
    if not isinstance(model, dict):
        raise CoreError("Core realization must be a mapping")

    result = copy.deepcopy(model)
    declared = result.get("authorities", []) or []
    if not isinstance(declared, list):
        raise CoreError("Core realization authorities must be a list")

    by_id: dict[str, dict[str, Any]] = {}
    for authority in declared:
        if not isinstance(authority, dict):
            raise CoreError("Core realization authority must be a mapping")
        authority_id = authority.get("id")
        if not isinstance(authority_id, str) or not authority_id:
            raise CoreError("Core realization authority id is required")
        if authority_id in by_id:
            raise CoreError(f"duplicate Core realization authority: {authority_id}")
        by_id[authority_id] = authority

    for authority in graph["authorities"]:
        by_id.setdefault(authority["id"], {"id": authority["id"]})

    result["authorities"] = list(by_id.values())
    result.setdefault("artifacts", [])
    result.setdefault("questions", [])
    validate_model(result)
    return result


def validate_realization(graph: dict[str, Any], model: dict[str, Any]) -> dict[str, Any]:
    realized = realize_core_model(graph, model)
    producers = producer_index(graph)

    for artifact in realized.get("artifacts", []):
        for capability in artifact.get("provides", []) or []:
            producer = producers.get(capability)
            if producer is None:
                continue
            if artifact["authority"] != producer:
                raise CoreError(
                    f"artifact {artifact['id']} provides {capability} under "
                    f"{artifact['authority']}, but Engineering Graph producer is {producer}"
                )
    return realized


def evaluate_engineering_target(
    graph: dict[str, Any],
    target_consumer: str,
    model: dict[str, Any],
) -> dict[str, Any]:
    realized = validate_realization(graph, model)
    profile = derive_profile(graph, target_consumer)
    result = evaluate_target_state(profile, realized)
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
