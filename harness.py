#!/usr/bin/env python3
"""Harness Core v0 structural model and derived operations."""
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any

import yaml


class CoreError(ValueError):
    pass


def _by_id(items: list[dict[str, Any]], kind: str) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for item in items:
        item_id = item.get("id")
        if not isinstance(item_id, str) or not item_id:
            raise CoreError(f"{kind} id is required")
        if item_id in result:
            raise CoreError(f"duplicate {kind} id: {item_id}")
        result[item_id] = item
    return result


def validate_model(model: dict[str, Any]) -> None:
    authorities = _by_id(model.get("authorities", []), "authority")
    artifacts = _by_id(model.get("artifacts", []), "artifact")
    questions = _by_id(model.get("questions", []), "question")

    paths: set[str] = set()
    capability_owners: dict[str, str] = {}
    for artifact_id, artifact in artifacts.items():
        authority = artifact.get("authority")
        if authority not in authorities:
            raise CoreError(f"artifact {artifact_id} references unknown authority: {authority}")
        path = artifact.get("path")
        if not isinstance(path, str) or not path:
            raise CoreError(f"artifact {artifact_id} path is required")
        if path in paths:
            raise CoreError(f"duplicate canonical artifact path: {path}")
        paths.add(path)
        for dep in artifact.get("depends_on", []) or []:
            if dep not in artifacts:
                raise CoreError(f"artifact {artifact_id} depends on unknown artifact: {dep}")
            if dep == artifact_id:
                raise CoreError(f"artifact {artifact_id} cannot depend on itself")
        for capability in artifact.get("provides", []) or []:
            if not isinstance(capability, str) or not capability:
                raise CoreError(f"artifact {artifact_id} has invalid capability id")
            previous = capability_owners.setdefault(capability, authority)
            if previous != authority:
                raise CoreError(
                    f"capability {capability} has providers in multiple authorities: {previous}, {authority}"
                )

    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(artifact_id: str) -> None:
        if artifact_id in visiting:
            raise CoreError(f"artifact dependency cycle at: {artifact_id}")
        if artifact_id in visited:
            return
        visiting.add(artifact_id)
        for dep in artifacts[artifact_id].get("depends_on", []) or []:
            visit(dep)
        visiting.remove(artifact_id)
        visited.add(artifact_id)

    for artifact_id in artifacts:
        visit(artifact_id)

    for question_id, question in questions.items():
        authority = question.get("authority")
        if authority not in authorities:
            raise CoreError(f"question {question_id} references unknown authority: {authority}")
        if not isinstance(question.get("text"), str) or not question.get("text"):
            raise CoreError(f"question {question_id} text is required")
        for blocked_id in question.get("blocks", []) or []:
            if blocked_id not in artifacts:
                raise CoreError(f"question {question_id} blocks unknown artifact: {blocked_id}")
        blocked_capabilities = question.get("blocks_capabilities", []) or []
        if not isinstance(blocked_capabilities, list) or any(
            not isinstance(capability, str) or not capability
            for capability in blocked_capabilities
        ):
            raise CoreError(
                f"question {question_id} blocks_capabilities must contain capability ids"
            )
        if len(blocked_capabilities) != len(set(blocked_capabilities)):
            raise CoreError(f"question {question_id} has duplicate blocked capabilities")
        for source_id in question.get("answer_from", []) or []:
            if source_id not in artifacts:
                raise CoreError(f"question {question_id} answers from unknown artifact: {source_id}")
            if artifacts[source_id]["authority"] != authority:
                raise CoreError(
                    f"question {question_id} answer source must belong to addressed authority {authority}"
                )
        resolution = question.get("resolution")
        if resolution is not None:
            if resolution not in artifacts:
                raise CoreError(f"question {question_id} resolves to unknown artifact: {resolution}")
            if artifacts[resolution]["authority"] != authority:
                raise CoreError(
                    f"question {question_id} resolution artifact must belong to addressed authority {authority}"
                )


def affected(model: dict[str, Any], artifact_id: str) -> list[str]:
    validate_model(model)
    artifacts = _by_id(model.get("artifacts", []), "artifact")
    if artifact_id not in artifacts:
        raise CoreError(f"unknown artifact: {artifact_id}")
    reverse: dict[str, set[str]] = {item: set() for item in artifacts}
    for item_id, artifact in artifacts.items():
        for dep in artifact.get("depends_on", []) or []:
            reverse[dep].add(item_id)
    result: set[str] = set()
    stack = list(reverse[artifact_id])
    while stack:
        current = stack.pop()
        if current in result:
            continue
        result.add(current)
        stack.extend(reverse[current])
    return sorted(result)


def capability_resolve(model: dict[str, Any], capability_id: str) -> list[str]:
    validate_model(model)
    providers = [
        artifact["id"]
        for artifact in model.get("artifacts", [])
        if capability_id in (artifact.get("provides", []) or [])
    ]
    if not providers:
        raise CoreError(f"unresolved capability: {capability_id}")
    return sorted(providers)


def capability_owner(model: dict[str, Any], capability_id: str) -> str:
    providers = capability_resolve(model, capability_id)
    artifacts = _by_id(model.get("artifacts", []), "artifact")
    return artifacts[providers[0]]["authority"]


def unresolved_questions(model: dict[str, Any], authority_id: str | None = None) -> list[str]:
    validate_model(model)
    result = []
    for question in model.get("questions", []):
        if question.get("resolution") is not None:
            continue
        if authority_id is not None and question.get("authority") != authority_id:
            continue
        result.append(question["id"])
    return sorted(result)


def capability_blockers(model: dict[str, Any], capability_id: str) -> list[str]:
    """Return unresolved Questions that directly block forming or using a capability."""
    validate_model(model)
    return sorted(
        question["id"]
        for question in model.get("questions", [])
        if question.get("resolution") is None
        and capability_id in (question.get("blocks_capabilities", []) or [])
    )


def blocked(model: dict[str, Any], artifact_id: str) -> list[str]:
    validate_model(model)
    artifacts = _by_id(model.get("artifacts", []), "artifact")
    if artifact_id not in artifacts:
        raise CoreError(f"unknown artifact: {artifact_id}")
    result: set[str] = set()
    for question in model.get("questions", []):
        if question.get("resolution") is not None:
            continue
        for seed in question.get("blocks", []) or []:
            if artifact_id == seed or artifact_id in affected(model, seed):
                result.add(question["id"])
        for capability in question.get("blocks_capabilities", []) or []:
            providers = [
                artifact["id"]
                for artifact in model.get("artifacts", [])
                if capability in (artifact.get("provides", []) or [])
            ]
            for provider in providers:
                if artifact_id == provider or artifact_id in affected(model, provider):
                    result.add(question["id"])
    return sorted(result)


def question_frontier(model: dict[str, Any], question_ids: list[str]) -> list[dict[str, Any]]:
    """Route unresolved blockers to their addressed authorities without guessing external escalation."""
    validate_model(model)
    questions = _by_id(model.get("questions", []), "question")
    result: list[dict[str, Any]] = []
    for question_id in sorted(set(question_ids)):
        question = questions.get(question_id)
        if question is None:
            raise CoreError(f"unknown question: {question_id}")
        if question.get("resolution") is not None:
            continue
        sources = question.get("answer_from", []) or []
        result.append({
            "action": "RESOLVE" if sources else "ASK",
            "question": question_id,
            "authority": question["authority"],
            "text": question["text"],
            **({"answer_from": sources} if sources else {}),
        })
    return result



def completeness(expectations: list[dict[str, str]], coverage: list[dict[str, str]]) -> list[dict[str, str]]:
    """Derive missing subject/capability expectations from declared coverage."""
    covered = {
        (item.get("subject"), item.get("capability"))
        for item in coverage
        if item.get("subject") and item.get("capability")
    }
    missing: list[dict[str, str]] = []
    for expectation in expectations:
        subject = expectation.get("subject")
        capability = expectation.get("capability")
        if not subject or not capability:
            raise CoreError("expectation subject and capability are required")
        if (subject, capability) not in covered:
            missing.append({"subject": subject, "capability": capability})
    return missing


def design_frontier(
    model: dict[str, Any],
    expectations: list[dict[str, str]],
    coverage: list[dict[str, str]],
) -> dict[str, Any]:
    """Return all immediately designable missing expectations, or their blockers."""
    missing = completeness(expectations, coverage)
    if not missing:
        return {"status": "COMPLETE", "design": [], "wait": []}
    design: list[dict[str, Any]] = []
    wait: list[dict[str, Any]] = []
    for expectation in missing:
        action = next_action(model, expectation["capability"])
        item = {**action, "expectation": expectation}
        if action["action"] == "DESIGN":
            design.append(item)
        else:
            wait.append(item)
    return {
        "status": "READY" if design else "BLOCKED",
        "design": design,
        "wait": wait,
    }


def next_action(model: dict[str, Any], capability_id: str) -> dict[str, Any]:
    """Return the next Core action for a required capability."""
    validate_model(model)
    providers = capability_resolve(model, capability_id)
    owner = capability_owner(model, capability_id)
    blockers = sorted({q for artifact_id in providers for q in blocked(model, artifact_id)})
    if blockers:
        return {
            "action": "WAIT",
            "capability": capability_id,
            "authority": owner,
            "providers": providers,
            "questions": blockers,
        }
    return {
        "action": "DESIGN",
        "capability": capability_id,
        "authority": owner,
        "providers": providers,
    }


def resolve_question(model: dict[str, Any], question_id: str, artifact_id: str) -> dict[str, Any]:
    validate_model(model)
    result = copy.deepcopy(model)
    artifacts = _by_id(result.get("artifacts", []), "artifact")
    questions = _by_id(result.get("questions", []), "question")
    if question_id not in questions:
        raise CoreError(f"unknown question: {question_id}")
    if artifact_id not in artifacts:
        raise CoreError(f"unknown artifact: {artifact_id}")
    question = questions[question_id]
    if artifacts[artifact_id]["authority"] != question["authority"]:
        raise CoreError(
            f"resolution artifact {artifact_id} is not owned by addressed authority {question['authority']}"
        )
    question["resolution"] = artifact_id
    validate_model(result)
    return result


def load_model(path: str | Path) -> dict[str, Any]:
    with Path(path).open(encoding="utf-8") as handle:
        value = yaml.safe_load(handle)
    if not isinstance(value, dict):
        raise CoreError("model document must be a mapping")
    validate_model(value)
    return value


def _emit(value: Any) -> None:
    print(json.dumps(value, indent=2, sort_keys=True))


def main() -> int:
    parser = argparse.ArgumentParser(description="Harness Core v0")
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("validate", "affected", "questions", "resolve", "owner", "blocked", "next-action", "resolve-question"):
        command = sub.add_parser(name)
        command.add_argument("model")
        if name in ("affected", "blocked"):
            command.add_argument("artifact")
        elif name in ("resolve", "owner", "next-action"):
            command.add_argument("capability")
        elif name == "questions":
            command.add_argument("--authority")
        elif name == "resolve-question":
            command.add_argument("question")
            command.add_argument("artifact")
            command.add_argument("--write", action="store_true")

    args = parser.parse_args()
    model = load_model(args.model)
    if args.command == "validate":
        _emit({"valid": True})
    elif args.command == "affected":
        _emit(affected(model, args.artifact))
    elif args.command == "questions":
        _emit(unresolved_questions(model, args.authority))
    elif args.command == "resolve":
        _emit(capability_resolve(model, args.capability))
    elif args.command == "owner":
        _emit(capability_owner(model, args.capability))
    elif args.command == "blocked":
        _emit(blocked(model, args.artifact))
    elif args.command == "next-action":
        _emit(next_action(model, args.capability))
    elif args.command == "resolve-question":
        resolved = resolve_question(model, args.question, args.artifact)
        if args.write:
            Path(args.model).write_text(yaml.safe_dump(resolved, sort_keys=False), encoding="utf-8")
        else:
            print(yaml.safe_dump(resolved, sort_keys=False), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
