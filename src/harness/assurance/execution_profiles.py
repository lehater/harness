#!/usr/bin/env python3
"""Execute Harness assurance profiles from the CI registry authority."""
from __future__ import annotations

import argparse
import shlex
import shutil
import subprocess
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[3]
REGISTRY_PATH = ROOT / "spec" / "ci" / "check-registry-v0.yaml"


class AssuranceProfileError(ValueError):
    """Raised when an assurance execution profile is invalid."""


def load_registry(path: Path = REGISTRY_PATH) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise AssuranceProfileError("CI registry must contain a mapping")
    return value


def profile_config(registry: dict[str, Any], profile: str) -> dict[str, Any]:
    profiles = registry.get("execution_profiles")
    if not isinstance(profiles, dict):
        raise AssuranceProfileError("execution_profiles mapping is required")
    value = profiles.get(profile)
    if not isinstance(value, dict):
        raise AssuranceProfileError(f"unknown assurance profile: {profile}")
    return value


def fast_commands(registry: dict[str, Any]) -> list[str]:
    profile = profile_config(registry, "fast")
    stages = profile.get("stages")
    costs = profile.get("cost_classes")
    disposition = profile.get("disposition")
    if not isinstance(stages, list) or not stages:
        raise AssuranceProfileError("fast profile stages must be non-empty")
    if not isinstance(costs, list) or not costs:
        raise AssuranceProfileError("fast profile cost_classes must be non-empty")
    if disposition != "full_gate":
        raise AssuranceProfileError("fast profile must select full_gate checks")

    checks = registry.get("checks")
    if not isinstance(checks, list):
        raise AssuranceProfileError("registry checks must be a list")

    selected: list[str] = []
    for check in checks:
        if not isinstance(check, dict):
            raise AssuranceProfileError("registry check entry must be a mapping")
        if (
            check.get("disposition") == disposition
            and check.get("stage") in stages
            and check.get("cost_class") in costs
        ):
            command = check.get("command")
            if not isinstance(command, str) or not command.strip():
                raise AssuranceProfileError("selected fast check has no command")
            selected.append(command.strip())

    if not selected:
        raise AssuranceProfileError("fast profile selected no checks")
    expected_first = registry.get("full_gate", {}).get("policy_first_command")
    if selected[0] != expected_first:
        raise AssuranceProfileError(
            f"fast profile must start with policy command {expected_first!r}"
        )
    return selected


def external_dispatches(registry: dict[str, Any]) -> list[dict[str, Any]]:
    profile = profile_config(registry, "external-release")
    dispatches = profile.get("workflow_dispatches")
    if not isinstance(dispatches, list) or not dispatches:
        raise AssuranceProfileError(
            "external-release profile requires workflow_dispatches"
        )
    result: list[dict[str, Any]] = []
    for item in dispatches:
        if not isinstance(item, dict):
            raise AssuranceProfileError("workflow dispatch must be a mapping")
        workflow = item.get("workflow")
        ref = item.get("ref")
        inputs = item.get("inputs", {})
        if not isinstance(workflow, str) or not workflow:
            raise AssuranceProfileError("workflow dispatch requires workflow")
        if not isinstance(ref, str) or not ref:
            raise AssuranceProfileError(f"{workflow}: dispatch ref is required")
        if not isinstance(inputs, dict) or any(
            not isinstance(key, str) or not isinstance(value, (str, int, bool))
            for key, value in inputs.items()
        ):
            raise AssuranceProfileError(f"{workflow}: dispatch inputs are invalid")
        result.append({"workflow": workflow, "ref": ref, "inputs": inputs})
    return result


def run_command(command: str) -> None:
    print(f"+ {command}", flush=True)
    completed = subprocess.run(shlex.split(command), cwd=ROOT, check=False)
    if completed.returncode:
        raise SystemExit(completed.returncode)


def run_fast(registry: dict[str, Any]) -> None:
    for command in fast_commands(registry):
        run_command(command)


def run_full(registry: dict[str, Any]) -> None:
    profile = profile_config(registry, "full")
    target = profile.get("delegate_target")
    expected = registry.get("full_gate", {}).get("makefile_target")
    if target != expected or not isinstance(target, str):
        raise AssuranceProfileError(
            "full profile must delegate to the canonical full_gate makefile target"
        )
    run_command(f"make {target}")


def render_external_plan(registry: dict[str, Any]) -> list[str]:
    commands: list[str] = []
    for item in external_dispatches(registry):
        parts = ["gh", "workflow", "run", item["workflow"], "--ref", item["ref"]]
        for key, value in sorted(item["inputs"].items()):
            parts.extend(["-f", f"{key}={str(value).lower() if isinstance(value, bool) else value}"])
        commands.append(" ".join(shlex.quote(part) for part in parts))
    return commands


def dispatch_external(registry: dict[str, Any]) -> None:
    if shutil.which("gh") is None:
        raise AssuranceProfileError(
            "GitHub CLI 'gh' is required to dispatch external-release assurance"
        )
    auth = subprocess.run(
        ["gh", "auth", "status"],
        cwd=ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    if auth.returncode:
        raise AssuranceProfileError(
            "GitHub CLI is not authenticated; run 'gh auth login' first"
        )
    for command in render_external_plan(registry):
        run_command(command)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Harness assurance profiles")
    parser.add_argument("profile", choices=("fast", "full", "external-release"))
    parser.add_argument(
        "--plan",
        action="store_true",
        help="print selected commands/workflows without executing them",
    )
    parser.add_argument(
        "--skip-full",
        action="store_true",
        help="for external-release only: dispatch provider workflows without full preflight",
    )
    args = parser.parse_args()

    registry = load_registry()

    if args.profile == "fast":
        commands = fast_commands(registry)
        if args.plan:
            print("\n".join(commands))
        else:
            run_fast(registry)
        return 0

    if args.profile == "full":
        profile = profile_config(registry, "full")
        target = profile.get("delegate_target")
        if args.plan:
            print(f"make {target}")
        else:
            run_full(registry)
        return 0

    if not args.skip_full:
        if args.plan:
            profile = profile_config(registry, "full")
            print(f"make {profile.get('delegate_target')}")
        else:
            run_full(registry)

    commands = render_external_plan(registry)
    if args.plan:
        print("\n".join(commands))
    else:
        dispatch_external(registry)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
