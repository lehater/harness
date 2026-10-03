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
VALID_DRAFT_BEHAVIORS = {"allow", "skip", "manual"}


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


def validate_workflow_path_filters(
    relative: str,
    events: dict[str, Any],
    errors: list[str],
) -> None:
    for event_name, config in events.items():
        if not isinstance(config, dict):
            continue
        for key in ("paths", "paths-ignore"):
            for value in normalize_list(config.get(key)):
                candidate = value[1:] if value.startswith("!") else value
                if not candidate or any(char in candidate for char in "*?["):
                    continue
                if not (ROOT / candidate).exists():
                    errors.append(
                        f"CI-P04 workflow {relative} {event_name}.{key} "
                        f"references missing path: {value}"
                    )


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


def validate_execution_profiles(
    registry: dict[str, Any],
    makefile_text: str,
    errors: list[str],
) -> None:
    profiles = registry.get("execution_profiles")
    if not isinstance(profiles, dict):
        errors.append("CI-P11 execution_profiles mapping is required")
        return

    required_names = {"fast", "full", "external-release"}
    names = set(profiles)
    missing = sorted(required_names - names)
    extra = sorted(names - required_names)
    if missing:
        errors.append(f"CI-P11 missing assurance execution profiles: {missing}")
    if extra:
        errors.append(f"CI-P11 unknown assurance execution profiles: {extra}")

    for name in sorted(required_names & names):
        profile = profiles.get(name)
        if not isinstance(profile, dict):
            errors.append(f"CI-P11 profile {name} must be a mapping")
            continue
        target = profile.get("makefile_target")
        command = profile.get("command")
        if not isinstance(target, str) or not target:
            errors.append(f"CI-P11 profile {name} requires makefile_target")
            continue
        if not isinstance(command, str) or not command:
            errors.append(f"CI-P11 profile {name} requires command")
            continue
        target_commands = extract_make_target_commands(makefile_text, target)
        if target_commands != [command]:
            errors.append(
                f"CI-P11 profile {name} target {target!r} must execute exactly "
                f"{command!r}; found {target_commands!r}"
            )

    fast = profiles.get("fast")
    if isinstance(fast, dict):
        if fast.get("kind") != "deterministic":
            errors.append("CI-P11 fast profile must be deterministic")
        if fast.get("disposition") != "full_gate":
            errors.append("CI-P11 fast profile must select full_gate checks")
        if fast.get("stages") != ["policy", "focused"]:
            errors.append("CI-P11 fast profile stages must be [policy, focused]")
        if fast.get("cost_classes") != ["cheap"]:
            errors.append("CI-P11 fast profile cost_classes must be [cheap]")

    full = profiles.get("full")
    full_gate = registry.get("full_gate")
    if isinstance(full, dict) and isinstance(full_gate, dict):
        if full.get("kind") != "deterministic":
            errors.append("CI-P11 full profile must be deterministic")
        if full.get("delegate_target") != full_gate.get("makefile_target"):
            errors.append(
                "CI-P11 full profile must delegate to the canonical full_gate target"
            )

    external = profiles.get("external-release")
    if not isinstance(external, dict):
        return
    if external.get("kind") != "external":
        errors.append("CI-P11 external-release profile must be external")
    if external.get("preflight_profile") != "full":
        errors.append("CI-P11 external-release must preflight the full profile")

    dispatches = external.get("workflow_dispatches")
    if not isinstance(dispatches, list) or not dispatches:
        errors.append("CI-P11 external-release requires workflow_dispatches")
        return

    expected = {
        ".github/workflows/assurance-campaign-copilot.yml",
        ".github/workflows/greenfield-bootstrap-assurance.yml",
        ".github/workflows/live-calibration-copilot.yml",
    }
    seen: set[str] = set()
    for item in dispatches:
        if not isinstance(item, dict):
            errors.append("CI-P11 external-release dispatch must be a mapping")
            continue
        workflow_path = item.get("workflow")
        ref = item.get("ref")
        inputs = item.get("inputs")
        if not isinstance(workflow_path, str) or not workflow_path:
            errors.append("CI-P11 external-release dispatch requires workflow")
            continue
        if workflow_path in seen:
            errors.append(
                f"CI-P11 external-release duplicate workflow dispatch: {workflow_path}"
            )
        seen.add(workflow_path)
        if ref != "main":
            errors.append(
                f"CI-P11 external-release workflow {workflow_path} must dispatch ref main"
            )
        if not isinstance(inputs, dict):
            errors.append(
                f"CI-P11 external-release workflow {workflow_path} inputs must be a mapping"
            )

        path = ROOT / workflow_path
        if not path.is_file():
            errors.append(
                f"CI-P11 external-release workflow does not exist: {workflow_path}"
            )
            continue
        events = workflow_events(load_yaml(path))
        if "workflow_dispatch" not in events:
            errors.append(
                f"CI-P11 external-release workflow is not manually dispatchable: "
                f"{workflow_path}"
            )

    if seen != expected:
        errors.append(
            "CI-P11 external-release dispatch set must be aggregate campaign + "
            f"greenfield + live calibration; found {sorted(seen)}"
        )
    campaign = next(
        (
            item
            for item in dispatches
            if isinstance(item, dict)
            and item.get("workflow")
            == ".github/workflows/assurance-campaign-copilot.yml"
        ),
        None,
    )
    if not isinstance(campaign, dict) or campaign.get("inputs") != {"campaign": "all"}:
        errors.append(
            "CI-P11 assurance campaign dispatch must use campaign=all to avoid "
            "duplicating first-wave/TL4 provider runs"
        )


def main() -> int:
    errors: list[str] = []

    try:
        registry = load_yaml(REGISTRY_PATH)
    except Exception as exc:
        print(f"Harness CI policy validation failed:\n- CI-P04 registry unreadable: {exc}")
        return 1

    makefile_text = MAKEFILE_PATH.read_text(encoding="utf-8")
    validate_execution_profiles(registry, makefile_text, errors)

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
        for directory, pattern in (
            (ROOT / "checks", "validate_*.py"),
            (ROOT / "tests", "test_*.py"),
        )
        if directory.is_dir()
        for path in directory.rglob(pattern)
    }
    legacy_root = ROOT / "validators"
    legacy_validation_paths = {
        str(path.relative_to(ROOT))
        for path in (
            legacy_root.rglob("validate_*.py") if legacy_root.is_dir() else []
        )
    }
    for path in sorted(legacy_validation_paths):
        errors.append(f"CI-P04 legacy validation path is forbidden: {path}")
    for path in sorted(discovered_paths - registered_paths):
        errors.append(f"CI-P04 validation code is unregistered: {path}")
    for path in sorted(registered_paths - discovered_paths):
        errors.append(f"CI-P04 registered validation path does not exist: {path}")

    full_gate = registry.get("full_gate")
    if not isinstance(full_gate, dict):
        errors.append("CI-P04 full_gate configuration missing")
        full_gate = {}

    target = str(full_gate.get("makefile_target", "harness-check"))
    make_commands = extract_make_target_commands(makefile_text, target)

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
        workflow_cost = str(entry.get("cost_class", ""))
        draft_behavior = str(entry.get("draft_behavior", ""))
        rationale = str(entry.get("rationale", "")).strip()
        if relative:
            registered_workflows.add(relative)
        if workflow_cost not in VALID_COSTS:
            errors.append(f"CI-P05 workflow {relative} has unknown cost_class: {workflow_cost}")
        if workflow_cost in {"medium", "heavy"} and not rationale:
            errors.append(f"CI-P05 {workflow_cost} workflow {relative} requires rationale")
        if draft_behavior not in VALID_DRAFT_BEHAVIORS:
            errors.append(f"CI-P01 workflow {relative} has unknown draft_behavior: {draft_behavior}")
        if role not in VALID_ROLES:
            errors.append(f"CI-P04 workflow {relative} has unknown role: {role}")
            continue
        path = ROOT / relative
        if not path.is_file():
            errors.append(f"CI-P04 registered workflow missing: {relative}")
            continue
        workflow = load_yaml(path)
        events = workflow_events(workflow)
        validate_workflow_path_filters(relative, events, errors)

        if role == "exhaustive":
            if draft_behavior != "skip":
                errors.append(
                    f"CI-P01 exhaustive workflow must declare draft_behavior skip: {relative}"
                )
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
            if draft_behavior not in {"allow", "skip"}:
                errors.append(
                    f"CI-P01 focused workflow {relative} must declare draft_behavior allow or skip"
                )
            if draft_behavior == "allow" and workflow_cost != "cheap":
                errors.append(
                    f"CI-P05 draft-enabled focused workflow must be cheap: {relative}"
                )
            if (
                draft_behavior == "skip"
                and "pull_request" in events
                and pull_request_may_run_on_draft(events.get("pull_request"))
                and not exhaustive_jobs_have_draft_guard(workflow)
            ):
                errors.append(
                    f"CI-P01 focused workflow declared skip but can run jobs on draft PR updates: {relative}"
                )
            if "pull_request" in events and "push" in events:
                if not push_is_main_only(events.get("push")):
                    errors.append(
                        "CI-P07 focused workflow owns overlapping pull_request and "
                        f"non-main push events: {relative}"
                    )

        elif role == "external":
            if draft_behavior != "manual":
                errors.append(
                    f"CI-P08 external workflow must declare draft_behavior manual: {relative}"
                )
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
