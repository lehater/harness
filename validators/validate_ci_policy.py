#!/usr/bin/env python3
"""Validate Harness CI execution policy before expensive repository checks."""
from __future__ import annotations

from pathlib import Path
import re
import sys
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "spec/ci/check-registry-v0.yaml"
MAKEFILE_PATH = ROOT / "Makefile"

DRAFT_SAFE_PULL_REQUEST_TYPES = {"ready_for_review"}
VALID_ROLES = {"exhaustive", "focused", "external"}
VALID_COSTS = {"cheap", "medium", "heavy"}
VALID_DISPOSITIONS = {"full_gate", "standalone", "unresolved"}


def load_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path.relative_to(ROOT)} must contain a mapping")
    return data


def workflow_events(workflow: dict[str, Any]) -> dict[str, Any]:
    # PyYAML 1.1 resolves the GitHub Actions key `on` as boolean True.
    value = workflow.get("on")
    if value is None and True in workflow:
        value = workflow[True]
    if value is None:
        return {}
    if isinstance(value, str):
        return {value: None}
    if isinstance(value, list):
        return {str(item): None for item in value}
    if isinstance(value, dict):
        return {str(key): val for key, val in value.items()}
    return {}


def normalize_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value]
    return [str(value)]


def pull_request_may_run_on_draft(config: Any) -> bool:
    if config is None:
        return True
    if not isinstance(config, dict):
        return True
    types = normalize_list(config.get("types"))
    if not types:
        return True
    return any(event not in DRAFT_SAFE_PULL_REQUEST_TYPES for event in types)


def exhaustive_jobs_have_draft_guard(workflow: dict[str, Any]) -> bool:
    jobs = workflow.get("jobs")
    if not isinstance(jobs, dict) or not jobs:
        return False
    for job in jobs.values():
        if not isinstance(job, dict):
            return False
        condition = str(job.get("if", ""))
        normalized = re.sub(r"\s+", "", condition).lower()
        guarded = (
            "github.event.pull_request.draft==false" in normalized
            or "github.event_name!='pull_request'" in normalized
            and "github.event.pull_request.draft" in normalized
        )
        if not guarded:
            return False
    return True


def push_is_main_only(config: Any) -> bool:
    if not isinstance(config, dict):
        return False
    branches = normalize_list(config.get("branches"))
    return bool(branches) and set(branches) == {"main"}


def extract_make_target_commands(text: str, target: str) -> list[str]:
    lines = text.splitlines()
    in_target = False
    commands: list[str] = []
    target_prefix = f"{target}:"

    for line in lines:
        if not line.startswith(("\t", " ")) and ":" in line:
            if in_target:
                break
            in_target = line.startswith(target_prefix)
            continue
        if in_target and line.startswith(("\t", " ")):
            stripped = line.strip()
            if stripped and not stripped.startswith("#"):
                commands.append(stripped)
    return commands


def referenced_python_path(command: str) -> str | None:
    tokens = command.split()
    for token in reversed(tokens):
        if token.endswith(".py"):
            return token
    return None


def main() -> int:
    errors: list[str] = []

    try:
        registry = load_yaml(REGISTRY_PATH)
    except Exception as exc:
        print(f"Harness CI policy validation failed:\n- CI-P04 registry unreadable: {exc}")
        return 1

    policy_path = ROOT / str(registry.get("policy", ""))
    if not policy_path.is_file():
        errors.append(f"CI-P04 canonical policy missing: {policy_path.relative_to(ROOT)}")

    stage_order = registry.get("stage_order")
    if not isinstance(stage_order, list) or not stage_order:
        errors.append("CI-P03 registry stage_order must be a non-empty list")
        stage_order = []
    stage_rank = {str(stage): index for index, stage in enumerate(stage_order)}

    checks = registry.get("checks")
    if not isinstance(checks, list):
        errors.append("CI-P04 registry checks must be a list")
        checks = []

    by_command: dict[str, dict[str, Any]] = {}
    registered_paths: set[str] = set()
    for index, check in enumerate(checks):
        if not isinstance(check, dict):
            errors.append(f"CI-P04 check entry #{index + 1} must be a mapping")
            continue
        command = str(check.get("command", "")).strip()
        check_id = str(check.get("id", "")).strip() or f"entry-{index + 1}"
        stage = str(check.get("stage", ""))
        cost = str(check.get("cost_class", ""))
        disposition = str(check.get("disposition", ""))
        if not command:
            errors.append(f"CI-P04 check {check_id} has no command")
            continue
        if command in by_command:
            errors.append(f"CI-P04 duplicate registered command: {command}")
        by_command[command] = check
        if stage not in stage_rank:
            errors.append(f"CI-P03 check {check_id} has unknown stage: {stage}")
        if cost not in VALID_COSTS:
            errors.append(f"CI-P05 check {check_id} has unknown cost_class: {cost}")
        if disposition not in VALID_DISPOSITIONS:
            errors.append(f"CI-P04 check {check_id} has unknown disposition: {disposition}")
        elif disposition == "unresolved":
            errors.append(f"CI-P04 unresolved check disposition: {check_id}")
        if cost in {"medium", "heavy"} and not str(check.get("rationale", "")).strip():
            errors.append(f"CI-P05 {cost} check {check_id} requires rationale")
        if stage in {"policy", "focused"} and cost in {"medium", "heavy"}:
            errors.append(
                f"CI-P05 early-stage check {check_id} must be cheap; "
                f"found {cost} in {stage}"
            )
        if disposition == "standalone" and not str(check.get("rationale", "")).strip():
            errors.append(f"CI-P04 standalone check {check_id} requires rationale")
        path = referenced_python_path(command)
        if path:
            registered_paths.add(path)

    discovered_paths = {
        str(path.relative_to(ROOT))
        for pattern in ("validators/validate_*.py", "tests/test_*.py")
        for path in ROOT.glob(pattern)
    }
    for path in sorted(discovered_paths - registered_paths):
        errors.append(f"CI-P04 validation code is unregistered: {path}")
    for path in sorted(registered_paths - discovered_paths):
        errors.append(f"CI-P04 registered validation path does not exist: {path}")

    full_gate = registry.get("full_gate")
    if not isinstance(full_gate, dict):
        errors.append("CI-P04 full_gate configuration missing")
        full_gate = {}

    target = str(full_gate.get("makefile_target", "harness-check"))
    make_commands = extract_make_target_commands(
        MAKEFILE_PATH.read_text(encoding="utf-8"), target
    )

    policy_first = str(full_gate.get("policy_first_command", ""))
    if not make_commands or make_commands[0] != policy_first:
        errors.append(
            f"CI-P09 {target} must start with {policy_first!r}; "
            f"found {make_commands[0] if make_commands else '<empty>'!r}"
        )

    registered_make_commands = set(by_command)
    for command in make_commands:
        if command not in registered_make_commands:
            errors.append(f"CI-P04 full-gate command is unregistered: {command}")

    full_gate_commands = {
        command
        for command, check in by_command.items()
        if check.get("disposition") == "full_gate"
    }
    for command in sorted(full_gate_commands - set(make_commands)):
        errors.append(f"CI-P04 full_gate check missing from {target}: {command}")
    for command in make_commands:
        check = by_command.get(command)
        if check and check.get("disposition") != "full_gate":
            errors.append(
                f"CI-P04 {target} executes check with disposition "
                f"{check.get('disposition')}: {command}"
            )

    previous_rank = -1
    previous_command = ""
    for command in make_commands:
        check = by_command.get(command)
        if not check:
            continue
        rank = stage_rank.get(str(check.get("stage", "")))
        if rank is None:
            continue
        if rank < previous_rank:
            errors.append(
                "CI-P03 stage order regression: "
                f"{command} ({check.get('stage')}) runs after "
                f"{previous_command} ({stage_order[previous_rank]})"
            )
            break
        previous_rank = rank
        previous_command = command

    roles = registry.get("workflow_roles")
    if not isinstance(roles, list):
        errors.append("CI-P04 workflow_roles must be a list")
        roles = []

    registered_workflows: set[str] = set()

    for entry in roles:
        if not isinstance(entry, dict):
            errors.append("CI-P04 workflow role entry must be a mapping")
            continue
        relative = str(entry.get("path", ""))
        role = str(entry.get("role", ""))
        if relative:
            registered_workflows.add(relative)
        if role not in VALID_ROLES:
            errors.append(f"CI-P04 workflow {relative} has unknown role: {role}")
            continue
        path = ROOT / relative
        if not path.is_file():
            errors.append(f"CI-P04 registered workflow missing: {relative}")
            continue
        workflow = load_yaml(path)
        events = workflow_events(workflow)

        if role == "exhaustive":
            pr = events.get("pull_request")
            if "pull_request" not in events:
                errors.append(f"CI-P02 exhaustive workflow lacks pull_request trigger: {relative}")
            elif isinstance(pr, dict) and (
                "paths" in pr or "paths-ignore" in pr
            ):
                errors.append(
                    f"CI-P02 exhaustive pull_request gate is path-filtered: {relative}"
                )
            if "pull_request" in events and pull_request_may_run_on_draft(pr):
                if not exhaustive_jobs_have_draft_guard(workflow):
                    errors.append(
                        f"CI-P01 exhaustive workflow can run automatically on draft PR updates: {relative}"
                    )
            push = events.get("push")
            if "push" not in events or not push_is_main_only(push):
                errors.append(
                    f"CI-P02 exhaustive workflow push trigger must be restricted to main: {relative}"
                )
            expected_command = str(full_gate.get("command", ""))
            rendered = path.read_text(encoding="utf-8")
            if expected_command and expected_command not in rendered:
                errors.append(
                    f"CI-P04 exhaustive workflow does not invoke full gate {expected_command!r}: {relative}"
                )

        elif role == "focused":
            if "pull_request" in events and "push" in events:
                if not push_is_main_only(events.get("push")):
                    errors.append(
                        "CI-P07 focused workflow owns overlapping pull_request and "
                        f"non-main push events: {relative}"
                    )

        elif role == "external":
            event_names = set(events)
            if event_names != {"workflow_dispatch"}:
                errors.append(
                    "CI-P08 external workflow must be workflow_dispatch-only: "
                    f"{relative} has {sorted(event_names)}"
                )

    discovered_workflows = {
        str(path.relative_to(ROOT))
        for pattern in (".github/workflows/*.yml", ".github/workflows/*.yaml")
        for path in ROOT.glob(pattern)
    }
    for relative in sorted(discovered_workflows - registered_workflows):
        errors.append(f"CI-P04 workflow is unregistered: {relative}")
    for relative in sorted(registered_workflows - discovered_workflows):
        errors.append(f"CI-P04 registered workflow does not exist: {relative}")

    if errors:
        print("Harness CI policy validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Harness CI policy validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
