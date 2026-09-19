#!/usr/bin/env python3
"""Evaluate a project Core model against a declared design target state."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml

from harness import CoreError, blocked, capability_blockers, validate_model


def _by_id(items: list[dict[str, Any]], kind: str) -> dict[str, dict[str, Any]]:
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


def validate_profile(profile: dict[str, Any], model: dict[str, Any] | None = None) -> None:
    if profile.get("version") != 1:
        raise CoreError("design profile version must be 1")
    if profile.get("kind") != "harness-design-profile":
        raise CoreError("unexpected design profile kind")
    if not isinstance(profile.get("id"), str) or not profile["id"]:
        raise CoreError("design profile id is required")

    expectations = profile.get("expectations", [])
    if not isinstance(expectations, list):
        raise CoreError("design profile expectations must be a list")
    indexed = _by_id(expectations, "expectation")

    authority_ids: set[str] | None = None
    if model is not None:
        validate_model(model)
        authority_ids = {
            item["id"]
            for item in model.get("authorities", [])
            if isinstance(item, dict) and isinstance(item.get("id"), str)
        }

    pairs: set[tuple[str, str]] = set()
    for expectation_id, expectation in indexed.items():
        subject = expectation.get("subject")
        capability = expectation.get("capability")
        authority = expectation.get("authority")
        if not isinstance(subject, str) or not subject:
            raise CoreError(f"expectation {expectation_id} subject is required")
        if not isinstance(capability, str) or not capability:
            raise CoreError(f"expectation {expectation_id} capability is required")
        if not isinstance(authority, str) or not authority:
            raise CoreError(f"expectation {expectation_id} authority is required")
        pair = (subject, capability)
        if pair in pairs:
            raise CoreError(f"duplicate design expectation: {subject}/{capability}")
        pairs.add(pair)
        if authority_ids is not None and authority not in authority_ids:
            raise CoreError(
                f"expectation {expectation_id} references unknown authority: {authority}"
            )

        depends_on = expectation.get("depends_on", [])
        if not isinstance(depends_on, list) or any(
            not isinstance(value, str) or not value for value in depends_on
        ):
            raise CoreError(f"expectation {expectation_id} depends_on must be expectation ids")
        if len(depends_on) != len(set(depends_on)):
            raise CoreError(f"expectation {expectation_id} has duplicate dependencies")
        for dependency in depends_on:
            if dependency == expectation_id:
                raise CoreError(f"expectation {expectation_id} cannot depend on itself")
            if dependency not in indexed:
                raise CoreError(
                    f"expectation {expectation_id} references unknown dependency: {dependency}"
                )

    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(expectation_id: str) -> None:
        if expectation_id in visited:
            return
        if expectation_id in visiting:
            raise CoreError(f"design profile expectation dependency cycle at: {expectation_id}")
        visiting.add(expectation_id)
        for dependency in indexed[expectation_id].get("depends_on", []):
            visit(dependency)
        visiting.remove(expectation_id)
        visited.add(expectation_id)

    for expectation_id in indexed:
        visit(expectation_id)


def evaluate_target_state(profile: dict[str, Any], model: dict[str, Any]) -> dict[str, Any]:
    validate_profile(profile, model)
    artifacts = model.get("artifacts", [])
    expectations = {
        item["id"]: item
        for item in profile.get("expectations", [])
    }

    satisfied: list[str] = []
    create: list[dict[str, Any]] = []
    wait: list[dict[str, Any]] = []
    pending: list[dict[str, Any]] = []

    remaining = set(expectations)
    while remaining:
        progressed = False
        for expectation_id in sorted(remaining):
            expectation = expectations[expectation_id]
            prerequisites = expectation.get("depends_on", [])
            unresolved_prerequisites = [
                dependency for dependency in prerequisites if dependency not in satisfied
            ]
            if unresolved_prerequisites:
                continue

            subject = expectation["subject"]
            capability = expectation["capability"]
            authority = expectation["authority"]
            providers = sorted(
                artifact["id"]
                for artifact in artifacts
                if capability in (artifact.get("provides", []) or [])
            )

            if not providers:
                blockers = capability_blockers(model, capability)
                if blockers:
                    wait.append(
                        {
                            "action": "WAIT",
                            "expectation": expectation_id,
                            "subject": subject,
                            "capability": capability,
                            "authority": authority,
                            "providers": [],
                            "questions": blockers,
                        }
                    )
                else:
                    create.append(
                        {
                            "action": "CREATE",
                            "expectation": expectation_id,
                            "subject": subject,
                            "capability": capability,
                            "authority": authority,
                        }
                    )
                remaining.remove(expectation_id)
                progressed = True
                continue

            provider_authority = next(
                artifact["authority"]
                for artifact in artifacts
                if artifact["id"] == providers[0]
            )
            if provider_authority != authority:
                raise CoreError(
                    f"expectation {expectation_id} requires authority {authority}, "
                    f"but capability {capability} is owned by {provider_authority}"
                )

            blockers = sorted(
                {
                    question
                    for provider in providers
                    for question in blocked(model, provider)
                }
            )
            if blockers:
                wait.append(
                    {
                        "action": "WAIT",
                        "expectation": expectation_id,
                        "subject": subject,
                        "capability": capability,
                        "authority": authority,
                        "providers": providers,
                        "questions": blockers,
                    }
                )
                remaining.remove(expectation_id)
                progressed = True
                continue

            satisfied.append(expectation_id)
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
                "subject": expectation["subject"],
                "capability": expectation["capability"],
                "authority": expectation["authority"],
                "depends_on": [
                    dependency
                    for dependency in expectation.get("depends_on", [])
                    if dependency not in satisfied
                ],
            }
        )

    if len(satisfied) == len(expectations):
        status = "COMPLETE"
    elif create:
        status = "READY"
    else:
        status = "BLOCKED"

    return {
        "status": status,
        "satisfied": sorted(satisfied),
        "create": create,
        "wait": wait,
        "pending": pending,
    }


def _load(path: str | Path) -> dict[str, Any]:
    value = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise CoreError(f"{path} must contain a mapping")
    return value


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate Harness design target state")
    parser.add_argument("profile")
    parser.add_argument("model")
    args = parser.parse_args()

    result = evaluate_target_state(_load(args.profile), _load(args.model))
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
