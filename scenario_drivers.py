#!/usr/bin/env python3
"""Pluggable drivers for Harness scenario-suite execution.

Drivers expose Harness behavior to the scenario runner. The scenario DSL owns
only test orchestration; it does not model engineering semantics.
"""
from __future__ import annotations

import copy
from typing import Any, Callable

from agent_router import route_create_work
from authority_context import build_authority_context
from capability_lifecycle import lifecycle_states
from concern_activation import derive_activation
from coverage_obligations import (
    derive_subject_inventory_disposition,
    validate_subject_obligations,
)
from decision_exploration import evaluate_decision_exploration
from decision_governance import evaluate_decision_governance
from decision_pipeline import derive_decision_roadmap
from engineering_coverage import evaluate_with_repository_policy
from engineering_graph import evaluate_engineering_target
from graph_doctor import diagnose_project
from harness import validate_model
from project_status import bootstrap_registry, status as project_status
from repository_realization import evaluate as evaluate_repository_realization
from source_coverage import validate_source_coverage
from semantic_acceptance import evaluate_artifact
from semantic_closure import evaluate_semantic_closure
from semantic_questions import (
    append_question_proposals,
    questions_from_semantic_evaluation,
)

Driver = Callable[..., Any]
DRIVERS: dict[str, Driver] = {}


def scenario_driver(name: str) -> Callable[[Driver], Driver]:
    def register(func: Driver) -> Driver:
        if name in DRIVERS:
            raise RuntimeError(f"duplicate scenario driver: {name}")
        DRIVERS[name] = func
        return func
    return register


def get_driver(name: str) -> Driver:
    try:
        return DRIVERS[name]
    except KeyError as exc:
        raise KeyError(f"unknown scenario driver: {name}") from exc


def _pointer_tokens(pointer: str) -> list[str]:
    if pointer == "":
        return []
    if not pointer.startswith("/"):
        raise ValueError(f"JSON pointer must start with '/': {pointer}")
    return [
        token.replace("~1", "/").replace("~0", "~")
        for token in pointer[1:].split("/")
    ]


def _container(root: Any, pointer: str) -> tuple[Any, str]:
    tokens = _pointer_tokens(pointer)
    if not tokens:
        raise ValueError("patch operation cannot target document root")
    current = root
    for token in tokens[:-1]:
        if isinstance(current, list):
            current = current[int(token)]
        elif isinstance(current, dict):
            current = current[token]
        else:
            raise ValueError(f"cannot traverse patch pointer: {pointer}")
    return current, tokens[-1]


@scenario_driver("data.patch")
def data_patch(*, value: Any, operations: list[dict[str, Any]]) -> Any:
    result = copy.deepcopy(value)
    for operation in operations:
        op = operation.get("op")
        path = operation.get("path")
        if op not in {"add", "replace", "remove"}:
            raise ValueError(f"unsupported patch op: {op}")
        if not isinstance(path, str):
            raise ValueError("patch path is required")
        container, token = _container(result, path)
        if isinstance(container, list):
            if token == "-":
                if op != "add":
                    raise ValueError("'-' list pointer is valid only for add")
                container.append(copy.deepcopy(operation.get("value")))
                continue
            index = int(token)
            if op == "remove":
                del container[index]
            elif op == "replace":
                container[index] = copy.deepcopy(operation.get("value"))
            else:
                container.insert(index, copy.deepcopy(operation.get("value")))
        elif isinstance(container, dict):
            if op == "remove":
                del container[token]
            elif op == "replace":
                if token not in container:
                    raise KeyError(f"replace target absent: {path}")
                container[token] = copy.deepcopy(operation.get("value"))
            else:
                container[token] = copy.deepcopy(operation.get("value"))
        else:
            raise ValueError(f"patch target is not a container: {path}")
    return result


@scenario_driver("core.validate")
def core_validate(*, model: dict[str, Any]) -> dict[str, Any]:
    validate_model(model)
    return {"status": "VALID"}


@scenario_driver("engineering.target")
def engineering_target(
    *,
    graph: dict[str, Any],
    target: str,
    model: dict[str, Any],
) -> dict[str, Any]:
    return evaluate_engineering_target(graph, target, model)


@scenario_driver("semantic.acceptance")
def semantic_acceptance(
    *,
    contract: dict[str, Any],
    sources: dict[str, Any],
    candidate: dict[str, Any],
) -> dict[str, Any]:
    return evaluate_artifact(contract, sources, candidate)


@scenario_driver("semantic.questions")
def semantic_questions(
    *,
    graph: dict[str, Any],
    capability: str,
    evaluation: dict[str, Any],
) -> list[dict[str, Any]]:
    return questions_from_semantic_evaluation(
        graph=graph,
        capability=capability,
        evaluation=evaluation,
    )


@scenario_driver("semantic.apply_questions")
def semantic_apply_questions(
    *,
    model: dict[str, Any],
    proposals: list[dict[str, Any]],
) -> dict[str, Any]:
    return append_question_proposals(model, proposals)


@scenario_driver("semantic.closure")
def semantic_closure(**kwargs: Any) -> dict[str, Any]:
    return evaluate_semantic_closure(**kwargs)


@scenario_driver("lifecycle.states")
def lifecycle_states_driver(
    *,
    graph: dict[str, Any],
    model: dict[str, Any],
    projection: dict[str, Any],
) -> dict[str, Any]:
    return lifecycle_states(graph, model, projection)


@scenario_driver("concern.activation")
def concern_activation(**kwargs: Any) -> dict[str, Any]:
    return derive_activation(**kwargs)


@scenario_driver("decision.exploration")
def decision_exploration(**kwargs: Any) -> dict[str, Any]:
    return evaluate_decision_exploration(**kwargs)


@scenario_driver("decision.governance")
def decision_governance(**kwargs: Any) -> dict[str, Any]:
    return evaluate_decision_governance(**kwargs)


@scenario_driver("agent.route")
def agent_route(
    *,
    graph: dict[str, Any],
    target: str,
    model: dict[str, Any],
    registry: dict[str, Any],
) -> dict[str, Any]:
    return route_create_work(graph, target, model, registry)


@scenario_driver("decision.roadmap")
def decision_roadmap(**kwargs: Any) -> dict[str, Any]:
    return derive_decision_roadmap(**kwargs)


@scenario_driver("engineering.coverage")
def engineering_coverage(**kwargs: Any) -> dict[str, Any]:
    return evaluate_with_repository_policy(**kwargs)


@scenario_driver("graph.doctor")
def graph_doctor(**kwargs: Any) -> dict[str, Any]:
    return diagnose_project(**kwargs)


@scenario_driver("project.authority_bootstrap")
def project_authority_bootstrap(
    *,
    catalog: dict[str, Any],
    existing: dict[str, Any] | None = None,
    core: dict[str, Any] | None = None,
    authority_migrations: dict[str, list[str]] | None = None,
) -> dict[str, Any]:
    return bootstrap_registry(
        catalog,
        existing=existing,
        core=core,
        authority_migrations=authority_migrations,
    )


@scenario_driver("project.status")
def project_status_driver(
    *,
    catalog: dict[str, Any],
    registry: dict[str, Any],
    core: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return project_status(catalog, registry, core)


@scenario_driver("source.coverage")
def source_coverage_driver(*, document: dict[str, Any]) -> dict[str, Any]:
    return validate_source_coverage(document)


@scenario_driver("authority.context")
def authority_context_driver(
    *,
    graph: dict[str, Any],
    model: dict[str, Any],
    authority_id: str,
    capability_ids: list[str] | None = None,
) -> dict[str, Any]:
    return build_authority_context(
        graph,
        model,
        authority_id,
        capability_ids,
    )


@scenario_driver("coverage.subject_inventory")
def subject_inventory_driver(
    *,
    disposition: dict[str, Any] | None,
    consumer: str,
    scope: str,
) -> dict[str, Any]:
    return derive_subject_inventory_disposition(
        disposition,
        consumer=consumer,
        scope=scope,
    )


@scenario_driver("coverage.subject_obligations")
def subject_obligations_driver(
    *,
    obligations: dict[str, Any],
    source: dict[str, Any],
    consumer: str,
    scope: str,
) -> dict[str, Any]:
    return validate_subject_obligations(
        obligations,
        source,
        consumer=consumer,
        scope=scope,
    )


@scenario_driver("repository.realization")
def repository_realization_driver(
    *,
    model: dict[str, Any],
) -> dict[str, Any]:
    return evaluate_repository_realization(model)
