#!/usr/bin/env python3
"""Consumer-specific completeness contracts built on Harness Core v0.

This module is intentionally outside Core. It composes existing Core operations
to answer whether a downstream consumer has the canonical knowledge it needs and
to produce a package projection plan. It never interprets domain semantics or
renders target representations.
"""
from __future__ import annotations

import re
from typing import Any

from harness import (
    CoreError,
    blocked,
    capability_owner,
    capability_resolve,
    validate_model,
)


class ConsumerContractError(CoreError):
    pass


def _require_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise ConsumerContractError(f"{label} is required")
    return value


def _contract_requirements(
    model: dict[str, Any], contract: dict[str, Any]
) -> list[dict[str, Any]]:
    _require_string(contract.get("id"), "consumer contract id")
    _require_string(contract.get("consumer"), "consumer contract consumer")

    authorities = {
        item.get("id")
        for item in model.get("authorities", [])
        if isinstance(item, dict)
    }

    requirements = contract.get("requirements")
    if not isinstance(requirements, list) or not requirements:
        raise ConsumerContractError("consumer contract requires at least one requirement")

    seen: set[str] = set()
    for requirement in requirements:
        if not isinstance(requirement, dict):
            raise ConsumerContractError("consumer contract requirement must be a mapping")
        requirement_id = _require_string(requirement.get("id"), "requirement id")
        if requirement_id in seen:
            raise ConsumerContractError(f"duplicate consumer requirement id: {requirement_id}")
        seen.add(requirement_id)

        _require_string(requirement.get("capability"), f"requirement {requirement_id} capability")
        authority = _require_string(
            requirement.get("expected_authority"),
            f"requirement {requirement_id} expected_authority",
        )
        if authority not in authorities:
            raise ConsumerContractError(
                f"requirement {requirement_id} references unknown authority: {authority}"
            )

        representation = requirement.get("representation")
        if not isinstance(representation, dict) or not representation:
            raise ConsumerContractError(
                f"requirement {requirement_id} representation must be a non-empty mapping"
            )

        not_applicable = requirement.get("not_applicable")
        if not_applicable is not None:
            if not isinstance(not_applicable, dict):
                raise ConsumerContractError(
                    f"requirement {requirement_id} not_applicable must be a mapping"
                )
            _require_string(
                not_applicable.get("evidence_capability"),
                f"requirement {requirement_id} not_applicable evidence_capability",
            )

    return requirements


def _try_resolve(model: dict[str, Any], capability: str) -> tuple[list[str], str] | None:
    try:
        providers = capability_resolve(model, capability)
    except CoreError as exc:
        if str(exc) == f"unresolved capability: {capability}":
            return None
        raise
    return providers, capability_owner(model, capability)


def _blocking_questions(model: dict[str, Any], providers: list[str]) -> list[str]:
    result: set[str] = set()
    for artifact_id in providers:
        result.update(blocked(model, artifact_id))
    return sorted(result)


def _question_id(contract_id: str, requirement_id: str) -> str:
    def normalize(value: str) -> str:
        return re.sub(r"[^A-Z0-9]+", "-", value.upper()).strip("-")

    return f"Q-{normalize(contract_id)}-{normalize(requirement_id)}"


def _gap_question(contract_id: str, requirement: dict[str, Any]) -> dict[str, str]:
    requirement_id = requirement["id"]
    capability = requirement["capability"]
    authority = requirement["expected_authority"]
    if requirement.get("not_applicable"):
        text = (
            f"Provide canonical {capability} for consumer requirement {requirement_id}, "
            "or record canonical evidence that it is not applicable."
        )
    else:
        text = f"Provide canonical {capability} for consumer requirement {requirement_id}."
    return {
        "id": _question_id(contract_id, requirement_id),
        "authority": authority,
        "text": text,
    }


def evaluate_contract(
    model: dict[str, Any], contract: dict[str, Any]
) -> dict[str, Any]:
    """Evaluate one consumer contract against a valid Core v0 model."""
    validate_model(model)
    requirements = _contract_requirements(model, contract)

    results: list[dict[str, Any]] = []
    satisfied = True

    for requirement in requirements:
        requirement_id = requirement["id"]
        capability = requirement["capability"]
        expected_authority = requirement["expected_authority"]
        representation = requirement["representation"]

        resolved = _try_resolve(model, capability)
        if resolved is not None:
            providers, owner = resolved
            if owner != expected_authority:
                raise ConsumerContractError(
                    f"requirement {requirement_id} expects authority {expected_authority}, "
                    f"but capability {capability} is owned by {owner}"
                )
            blockers = _blocking_questions(model, providers)
            if blockers:
                satisfied = False
            results.append(
                {
                    "id": requirement_id,
                    "status": "PROVIDED",
                    "capability": capability,
                    "authority": owner,
                    "providers": providers,
                    "representation": representation,
                    "blocking_questions": blockers,
                }
            )
            continue

        not_applicable = requirement.get("not_applicable")
        if not_applicable is not None:
            evidence_capability = not_applicable["evidence_capability"]
            evidence = _try_resolve(model, evidence_capability)
            if evidence is not None:
                providers, owner = evidence
                if owner != expected_authority:
                    raise ConsumerContractError(
                        f"requirement {requirement_id} expects authority {expected_authority}, "
                        f"but NOT_APPLICABLE evidence {evidence_capability} is owned by {owner}"
                    )
                blockers = _blocking_questions(model, providers)
                if blockers:
                    satisfied = False
                results.append(
                    {
                        "id": requirement_id,
                        "status": "NOT_APPLICABLE",
                        "capability": capability,
                        "authority": owner,
                        "providers": providers,
                        "evidence_capability": evidence_capability,
                        "representation": representation,
                        "blocking_questions": blockers,
                    }
                )
                continue

        satisfied = False
        results.append(
            {
                "id": requirement_id,
                "status": "DESIGN_GAP",
                "capability": capability,
                "authority": expected_authority,
                "providers": [],
                "representation": representation,
                "blocking_questions": [],
                "question": _gap_question(contract["id"], requirement),
            }
        )

    return {
        "contract": contract["id"],
        "consumer": contract["consumer"],
        "satisfied": satisfied,
        "requirements": results,
    }


def project_package(
    model: dict[str, Any], contract: dict[str, Any]
) -> dict[str, Any]:
    """Project a satisfied contract into an opaque package source/representation plan."""
    evaluation = evaluate_contract(model, contract)
    if not evaluation["satisfied"]:
        raise ConsumerContractError(
            "consumer contract is not satisfied; package projection is blocked"
        )

    artifacts = {item["id"]: item for item in model.get("artifacts", [])}
    entries: list[dict[str, Any]] = []
    for requirement in evaluation["requirements"]:
        source_artifacts = list(requirement["providers"])
        entries.append(
            {
                "id": requirement["id"],
                "status": requirement["status"],
                "source_artifacts": source_artifacts,
                "source_paths": [artifacts[item]["path"] for item in source_artifacts],
                "representation": requirement["representation"],
            }
        )

    return {
        "version": 1,
        "kind": "harness-package-projection",
        "contract": evaluation["contract"],
        "consumer": evaluation["consumer"],
        "entries": entries,
    }
