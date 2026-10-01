#!/usr/bin/env python3
"""Validate fresh-context skill routing contracts in source and Consumer Pack environments."""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from consumer_pack import materialize_pack  # noqa: E402
from harness import CoreError  # noqa: E402
from skill_router import route_artifact, route_method, route_operation  # noqa: E402

FIXTURES = ROOT / "spec/agent-routing/fresh-context-v0.yaml"


def load() -> dict[str, Any]:
    value = yaml.safe_load(FIXTURES.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise AssertionError("fresh-context fixture must contain a mapping")
    assert value.get("version") == 1
    assert value.get("kind") == "harness-fresh-context-routing-fixtures"
    cases = value.get("cases")
    assert isinstance(cases, list) and cases
    return value


def route_case(case: dict[str, Any], root: Path) -> dict[str, Any]:
    route = case["route"]
    route_class = route["class"]
    if route_class == "operation":
        return route_operation(
            surface=route["surface"],
            operation=route["operation"],
            root=root,
        )
    if route_class == "method":
        return route_method(
            concerns=route.get("concerns"),
            method=route.get("method"),
            root=root,
        )
    if route_class == "artifact-production":
        return route_artifact(
            knowledge_kind=route["knowledge_kind"],
            root=root,
        )
    raise AssertionError(f"unknown fixture route class: {route_class}")


def assert_case(case: dict[str, Any], root: Path) -> None:
    expected_error = case.get("expect_error")
    if expected_error is not None:
        try:
            route_case(case, root)
        except CoreError as exc:
            assert expected_error in str(exc), (case["id"], expected_error, str(exc))
        else:
            raise AssertionError(f"{case['id']}: expected routing error")
        return

    result = route_case(case, root)
    if "expect_skill" in case:
        assert result.get("skill") == case["expect_skill"], (case["id"], result)
    if "expect_methods" in case:
        methods = [item["method"] for item in result.get("routed", [])]
        assert methods == case["expect_methods"], (case["id"], methods)


def main() -> int:
    fixture = load()

    agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    assert "Ordinary work in this repository uses the Maintainer Skill Surface" in agents
    assert "skill_router.py" in agents
    assert "Do not reconstruct task-specific procedures from this file." in agents

    with tempfile.TemporaryDirectory(prefix="fresh-context-pack-") as temp:
        pack = Path(temp) / "consumer-pack"
        materialize_pack(
            ROOT,
            pack,
            binding_revision="c" * 40,
            effective_revision="fresh-context-fixture",
        )

        for case in fixture["cases"]:
            assert isinstance(case, dict)
            environment = case.get("environment")
            if environment == "maintainer-source":
                root = ROOT
            elif environment == "consumer-pack":
                root = pack
            else:
                raise AssertionError(
                    f"{case.get('id')}: unknown environment {environment!r}"
                )
            assert_case(case, root)

    print(f"Fresh-context routing validation passed ({len(fixture['cases'])} cases)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
