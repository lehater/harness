#!/usr/bin/env python3
"""Contract tests for assurance execution profiles."""
from __future__ import annotations

import copy
import io
import sys
from contextlib import redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from harness.assurance.execution_profiles import (
    AssuranceProfileError,
    external_dispatches,
    fast_commands,
    load_registry,
    main,
    profile_config,
    render_external_plan,
)


def assert_raises(fn, fragment: str) -> None:
    try:
        fn()
    except AssuranceProfileError as exc:
        assert fragment in str(exc), (fragment, str(exc))
    else:
        raise AssertionError(f"expected AssuranceProfileError containing {fragment!r}")


def main_test() -> int:
    registry = load_registry()

    fast = fast_commands(registry)
    checks = {
        item["command"]: item
        for item in registry["checks"]
        if isinstance(item, dict) and isinstance(item.get("command"), str)
    }
    assert fast[0] == "python checks/validate_ci_policy.py"
    assert "python tests/test_scenario_suite.py" not in fast
    assert "python tests/test_consumer_pack.py" not in fast
    for command in fast:
        item = checks[command]
        assert item["disposition"] == "full_gate"
        assert item["stage"] in {"policy", "focused"}
        assert item["cost_class"] == "cheap"

    full = profile_config(registry, "full")
    assert full["makefile_target"] == "assurance-full"
    assert full["delegate_target"] == registry["full_gate"]["makefile_target"]
    assert full["delegate_target"] == "harness-check"

    external = external_dispatches(registry)
    workflows = [item["workflow"] for item in external]
    assert workflows == [
        ".github/workflows/assurance-campaign-copilot.yml",
        ".github/workflows/greenfield-bootstrap-assurance.yml",
        ".github/workflows/live-calibration-copilot.yml",
    ]
    assert external[0]["inputs"] == {"campaign": "all"}
    assert all(item["ref"] == "main" for item in external)

    plan = render_external_plan(registry)
    assert len(plan) == 3
    assert "campaign=all" in plan[0]
    assert all("--ref main" in command for command in plan)

    broken = copy.deepcopy(registry)
    broken["execution_profiles"]["fast"]["stages"] = []
    assert_raises(lambda: fast_commands(broken), "stages must be non-empty")

    broken = copy.deepcopy(registry)
    broken["execution_profiles"]["external-release"]["workflow_dispatches"][0].pop("ref")
    assert_raises(lambda: external_dispatches(broken), "dispatch ref is required")

    previous = sys.argv
    try:
        sys.argv = ["execution_profiles", "external-release", "--plan", "--skip-full"]
        output = io.StringIO()
        with redirect_stdout(output):
            assert main() == 0
        rendered = output.getvalue()
        assert "assurance-campaign-copilot.yml" in rendered
        assert "live-calibration-copilot.yml" in rendered
        assert "make harness-check" not in rendered
    finally:
        sys.argv = previous

    print(
        "assurance execution profiles: ok "
        f"(fast={len(fast)} checks; full=harness-check; external={len(external)} dispatches)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main_test())
