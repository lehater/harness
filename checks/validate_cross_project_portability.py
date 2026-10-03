#!/usr/bin/env python3
"""Fail closed on executable known-project identity coupling in generic runtime."""
from __future__ import annotations

import ast
import re
import sys
from pathlib import Path
from typing import Any, Iterable

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from harness.integration.adapters.canonical_graph import project_model  # noqa: E402
from harness.project_model.core import (  # noqa: E402
    affected,
    capability_owner,
    capability_resolve,
    unresolved_questions,
    validate_model,
)

RUNTIME_ROOT = ROOT / "src" / "harness"
KNOWN_PROJECT_ROOT = ROOT / "spec" / "behavioral-evals" / "tl5-known-project"
PORTABILITY_ROOT = ROOT / "spec" / "portability"
TL5_PAIR = PORTABILITY_ROOT / "tl5-napms-mode-equivalence-v1.yaml"
TL6_HOLDOUT = PORTABILITY_ROOT / "tl6-pluggy-independent-holdout-v1.yaml"
REVISION_RE = re.compile(r"^[0-9a-f]{40}$")


class PortabilityError(ValueError):
    """Raised when generic runtime contains project-specific executable coupling."""


def _load_yaml(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise PortabilityError(f"{path.relative_to(ROOT)} must contain a mapping")
    return value


def _repository_marker(repository: str, *, label: str) -> set[str]:
    if not isinstance(repository, str) or "/" not in repository:
        raise PortabilityError(f"{label} repository must be owner/name")
    folded = repository.casefold()
    return {folded, folded.rsplit("/", 1)[-1]}


def _project_markers() -> set[str]:
    markers: set[str] = set()
    fixtures = sorted(KNOWN_PROJECT_ROOT.glob("cases/*/fixture.yaml"))
    if not fixtures:
        raise PortabilityError("no TL5 known-project fixtures found")
    for path in fixtures:
        value = _load_yaml(path)
        known = value.get("known_project")
        if isinstance(known, dict):
            markers.update(
                _repository_marker(
                    known.get("repository"),
                    label=str(path.relative_to(ROOT)),
                )
            )

    for path, key in ((TL5_PAIR, "known_project"), (TL6_HOLDOUT, "holdout")):
        value = _load_yaml(path)
        project = value.get(key)
        if not isinstance(project, dict):
            raise PortabilityError(f"{path.relative_to(ROOT)} missing {key}")
        markers.update(
            _repository_marker(
                project.get("repository"),
                label=str(path.relative_to(ROOT)),
            )
        )

    if not markers:
        raise PortabilityError("no portability project repository identities discovered")
    return markers


def _docstring_nodes(tree: ast.AST) -> set[int]:
    ignored: set[int] = set()
    containers = [tree] + [
        node
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
    ]
    for node in containers:
        body = getattr(node, "body", None)
        if (
            isinstance(body, list)
            and body
            and isinstance(body[0], ast.Expr)
            and isinstance(body[0].value, ast.Constant)
            and isinstance(body[0].value.value, str)
        ):
            ignored.add(id(body[0].value))
    return ignored


def _contains_marker(value: str, markers: Iterable[str]) -> str | None:
    folded = value.casefold()
    for marker in sorted(markers, key=len, reverse=True):
        if marker in folded:
            return marker
    return None


def _source_violations(path: Path, markers: set[str]) -> list[str]:
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(path))
    ignored = _docstring_nodes(tree)
    violations: list[str] = []
    for node in ast.walk(tree):
        marker: str | None = None
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            if id(node) in ignored:
                continue
            marker = _contains_marker(node.value, markers)
        elif isinstance(node, (ast.Name, ast.Attribute)):
            identifier = node.id if isinstance(node, ast.Name) else node.attr
            for candidate in markers:
                leaf = candidate.rsplit("/", 1)[-1]
                if re.search(
                    rf"(^|_)" + re.escape(leaf) + r"($|_)",
                    identifier.casefold(),
                ):
                    marker = candidate
                    break
        if marker is not None:
            violations.append(
                f"{path.relative_to(ROOT)}:{getattr(node, 'lineno', '?')}: "
                f"executable known-project identity {marker!r}"
            )
    return violations


def _self_test(markers: set[str]) -> None:
    marker = sorted(markers, key=len)[0].rsplit("/", 1)[-1]
    synthetic = ast.parse(f'if project == "{marker}":\n    result = 1\n')
    ignored = _docstring_nodes(synthetic)
    assert not ignored
    assert any(
        isinstance(node, ast.Constant)
        and isinstance(node.value, str)
        and _contains_marker(node.value, markers)
        for node in ast.walk(synthetic)
    )
    doc_only = ast.parse(f'"""{marker} research history."""\nvalue = "generic"\n')
    ignored = _docstring_nodes(doc_only)
    assert all(
        not (
            isinstance(node, ast.Constant)
            and isinstance(node.value, str)
            and id(node) not in ignored
            and _contains_marker(node.value, markers)
        )
        for node in ast.walk(doc_only)
    )



def _model_observation(model: dict[str, Any]) -> dict[str, Any]:
    validate_model(model)
    capability_ids = sorted(
        {
            capability
            for artifact in model.get("artifacts", [])
            for capability in artifact.get("provides", []) or []
        }
    )
    return {
        "unresolved_questions": unresolved_questions(model),
        "capabilities": {
            capability: {
                "owner": capability_owner(model, capability),
                "providers": capability_resolve(model, capability),
            }
            for capability in capability_ids
        },
        "affected": {
            artifact["id"]: affected(model, artifact["id"])
            for artifact in model.get("artifacts", [])
        },
    }


def _assert_oracle(
    *,
    path: Path,
    actual: dict[str, Any],
    oracle: Any,
) -> None:
    if not isinstance(oracle, dict):
        raise PortabilityError(f"{path.relative_to(ROOT)} oracle must be a mapping")
    if actual != oracle:
        raise PortabilityError(
            f"{path.relative_to(ROOT)} generic semantic observation differs from frozen oracle"
        )


def _validate_project_identity(project: dict[str, Any], *, label: str) -> None:
    repository = project.get("repository")
    _repository_marker(repository, label=label)
    revision = project.get("commit")
    if not isinstance(revision, str) or not REVISION_RE.fullmatch(revision):
        raise PortabilityError(f"{label} commit must be an immutable 40-hex revision")


def _validate_blob_rows(rows: Any, *, label: str) -> None:
    if not isinstance(rows, list) or not rows:
        raise PortabilityError(f"{label} must contain frozen source rows")
    for row in rows:
        if not isinstance(row, dict):
            raise PortabilityError(f"{label} row must be a mapping")
        path = row.get("path")
        sha = row.get("git_blob_sha")
        if not isinstance(path, str) or not path:
            raise PortabilityError(f"{label} source path is required")
        if not isinstance(sha, str) or not REVISION_RE.fullmatch(sha):
            raise PortabilityError(f"{label} {path} must bind a 40-hex git blob sha")


def _validate_tl5_mode_equivalence() -> None:
    doc = _load_yaml(TL5_PAIR)
    if doc.get("kind") != "harness-portability-known-project-pair":
        raise PortabilityError("unexpected TL5 portability fixture kind")
    if doc.get("test_level") != "TL5" or doc.get("oracle_class") != "O2":
        raise PortabilityError("TL5 portability fixture must be TL5/O2")
    if doc.get("method") != "EM-10":
        raise PortabilityError("TL5 portability fixture must use EM-10")

    known = doc.get("known_project")
    if not isinstance(known, dict):
        raise PortabilityError("TL5 portability fixture missing known_project")
    _validate_project_identity(known, label="TL5 known_project")
    source_artifacts = known.get("source_artifacts")
    if not isinstance(source_artifacts, dict) or not source_artifacts:
        raise PortabilityError("TL5 known_project must bind accepted source artifacts")
    _validate_blob_rows(
        [
            {"path": value.get("path"), "git_blob_sha": value.get("git_blob_sha")}
            for value in source_artifacts.values()
            if isinstance(value, dict)
        ],
        label="TL5 accepted source artifacts",
    )

    direct = doc.get("direct_model")
    adapter = doc.get("adapter_projection")
    if not isinstance(direct, dict) or not isinstance(adapter, dict):
        raise PortabilityError("TL5 fixture requires direct_model and adapter_projection")
    source_graph = adapter.get("source_graph")
    projection = adapter.get("projection")
    if not isinstance(source_graph, dict) or not isinstance(projection, dict):
        raise PortabilityError("TL5 adapter_projection must contain source_graph/projection")

    validate_model(direct)
    projected = project_model(source_graph, projection)
    direct_observation = _model_observation(direct)
    projected_observation = _model_observation(projected)
    if direct_observation != projected_observation:
        raise PortabilityError(
            "TL5 direct-declaration and adapter-projection modes disagree "
            "under generic Harness Core semantics"
        )
    _assert_oracle(path=TL5_PAIR, actual=direct_observation, oracle=doc.get("oracle"))


def _validate_tl6_independent_holdout() -> None:
    doc = _load_yaml(TL6_HOLDOUT)
    if doc.get("kind") != "harness-portability-independent-holdout":
        raise PortabilityError("unexpected TL6 holdout fixture kind")
    if doc.get("test_level") != "TL6" or doc.get("oracle_class") != "O3":
        raise PortabilityError("independent holdout fixture must be TL6/O3")
    if doc.get("method") != "EM-11":
        raise PortabilityError("independent holdout fixture must use EM-11")

    holdout = doc.get("holdout")
    if not isinstance(holdout, dict):
        raise PortabilityError("TL6 portability fixture missing holdout")
    _validate_project_identity(holdout, label="TL6 holdout")
    if holdout.get("classification") != "independent-holdout":
        raise PortabilityError("TL6 project must be classified independent-holdout")
    failure_shape = holdout.get("failure_shape")
    if not isinstance(failure_shape, str) or not failure_shape.strip():
        raise PortabilityError("TL6 holdout must document a materially different failure shape")
    independence = holdout.get("independence")
    if not isinstance(independence, dict) or set(independence) != {
        "absent_from_harness_before_selection",
        "did_not_shape_tested_mechanism",
        "oracle_frozen_before_execution",
    }:
        raise PortabilityError("TL6 holdout independence declaration is incomplete")
    if not all(value is True for value in independence.values()):
        raise PortabilityError("TL6 holdout independence declarations must be explicit true")
    _validate_blob_rows(holdout.get("oracle_basis"), label="TL6 O3 oracle_basis")

    adapter = doc.get("adapter_projection")
    if not isinstance(adapter, dict):
        raise PortabilityError("TL6 holdout requires adapter_projection")
    source_graph = adapter.get("source_graph")
    projection = adapter.get("projection")
    if not isinstance(source_graph, dict) or not isinstance(projection, dict):
        raise PortabilityError("TL6 adapter_projection must contain source_graph/projection")
    projected = project_model(source_graph, projection)
    observation = _model_observation(projected)
    _assert_oracle(path=TL6_HOLDOUT, actual=observation, oracle=doc.get("oracle"))

def main() -> int:
    markers = _project_markers()
    _self_test(markers)
    _validate_tl5_mode_equivalence()
    _validate_tl6_independent_holdout()
    violations: list[str] = []
    for path in sorted(RUNTIME_ROOT.rglob("*.py")):
        violations.extend(_source_violations(path, markers))
    if violations:
        raise PortabilityError(
            "generic Harness runtime contains known-project executable coupling:\n- "
            + "\n- ".join(violations)
        )
    print(
        "Cross-project portability: PASS "
        f"({len(markers)} project marker(s); TL5 direct/adapter equivalence; "
        "TL6 independent holdout)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
