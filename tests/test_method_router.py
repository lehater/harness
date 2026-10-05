#!/usr/bin/env python3
"""Acceptance checks for deterministic consumer method routing."""
from __future__ import annotations

import contextlib
import copy
import io
import json
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from harness.project_model.core import CoreError  # noqa: E402
from harness.application.method_router import main as method_router_main, route_methods, validate_method_registry  # noqa: E402


def load(path: str) -> dict:
    value = yaml.safe_load((ROOT / path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise AssertionError(f"{path} must contain a mapping")
    return value


def main() -> int:
    registry = load("skills/consumer-method-registry-v0.yaml")
    catalog = load("spec/engineering-coverage/concern-catalog-v1.yaml")
    validate_method_registry(registry, catalog, root=ROOT)

    mixed = route_methods(
        registry,
        catalog,
        concerns=["reliability.failure-semantics", "interface.human.i18n"],
    )
    assert [item["method"] for item in mixed["routed"]] == [
        "internationalization-localization-analysis",
        "reliability-analysis",
    ]
    assert mixed["unrouted_concerns"] == []

    recovery = route_methods(
        registry,
        catalog,
        concerns=["reliability.recovery"],
    )
    assert [item["method"] for item in recovery["routed"]] == [
        "recovery-continuity-analysis"
    ]

    no_method = route_methods(registry, catalog, concerns=["intent.behavior"])
    assert no_method["routed"] == []
    assert no_method["unrouted_concerns"] == ["intent.behavior"]

    explicit = route_methods(registry, catalog, method="obligation-analysis")
    assert explicit["routed"][0]["skill"] == (
        "skills/artifacts/obligation-analysis/SKILL.md"
    )

    previous_argv = sys.argv
    output = io.StringIO()
    try:
        sys.argv = [
            "method_router.py",
            "--registry",
            str(ROOT / "skills/consumer-method-registry-v0.yaml"),
            "--catalog",
            str(ROOT / "spec/engineering-coverage/concern-catalog-v1.yaml"),
            "--method",
            "obligation-analysis",
        ]
        with contextlib.redirect_stdout(output):
            assert method_router_main() == 0
    finally:
        sys.argv = previous_argv
    cli_route = json.loads(output.getvalue())
    assert cli_route["surface"] == "consumer", cli_route
    assert cli_route["route_class"] == "method", cli_route
    assert cli_route["instruction_contracts"] == [
        "docs/design/agent-instruction-architecture-v0.md",
        "docs/design/process-simplicity-and-efficiency-v0.md",
    ], cli_route

    duplicate = copy.deepcopy(registry)
    duplicate["routes"][0]["concern_any"].append("reliability.failure-semantics")
    try:
        validate_method_registry(duplicate, catalog)
    except CoreError as exc:
        assert "ambiguous method selector reliability.failure-semantics" in str(exc)
    else:
        raise AssertionError("duplicate concern selector must be rejected")

    try:
        route_methods(registry, catalog, concerns=["not.a.real.concern"])
    except CoreError as exc:
        assert "unknown engineering concerns" in str(exc)
    else:
        raise AssertionError("unknown concern must be rejected")

    print("Consumer method router validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
