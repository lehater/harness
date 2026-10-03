#!/usr/bin/env python3
"""Fail closed on executable known-project identity coupling in generic runtime."""
from __future__ import annotations

import ast
import re
from pathlib import Path
from typing import Iterable

import yaml

ROOT = Path(__file__).resolve().parents[1]
RUNTIME_ROOT = ROOT / "src" / "harness"
KNOWN_PROJECT_ROOT = ROOT / "spec" / "behavioral-evals" / "tl5-known-project"


class PortabilityError(ValueError):
    """Raised when generic runtime contains project-specific executable coupling."""


def _known_project_markers() -> set[str]:
    markers: set[str] = set()
    fixtures = sorted(KNOWN_PROJECT_ROOT.glob("cases/*/fixture.yaml"))
    if not fixtures:
        raise PortabilityError("no TL5 known-project fixtures found")
    for path in fixtures:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not isinstance(value, dict):
            raise PortabilityError(f"{path.relative_to(ROOT)} must contain a mapping")
        known = value.get("known_project")
        if not isinstance(known, dict):
            continue
        repository = known.get("repository")
        if not isinstance(repository, str) or "/" not in repository:
            raise PortabilityError(
                f"{path.relative_to(ROOT)} known_project.repository must be owner/name"
            )
        repository = repository.casefold()
        markers.add(repository)
        markers.add(repository.rsplit("/", 1)[-1])
    if not markers:
        raise PortabilityError("no known-project repository identities discovered")
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


def main() -> int:
    markers = _known_project_markers()
    _self_test(markers)
    violations: list[str] = []
    for path in sorted(RUNTIME_ROOT.rglob("*.py")):
        violations.extend(_source_violations(path, markers))
    if violations:
        raise PortabilityError(
            "generic Harness runtime contains known-project executable coupling:\n- "
            + "\n- ".join(violations)
        )
    print(
        "Cross-project portability runtime neutrality: PASS "
        f"({len(markers)} known-project marker(s))"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
