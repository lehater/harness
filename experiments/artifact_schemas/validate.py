#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import yaml


class ExperimentError(ValueError):
    pass


def _load(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ExperimentError(f"{path}: expected mapping")
    return value


def _strings(value: Any, field: str, *, allow_empty: bool = True) -> list[str]:
    if not isinstance(value, list):
        raise ExperimentError(f"{field}: expected list")
    if not allow_empty and not value:
        raise ExperimentError(f"{field}: must not be empty")
    if any(not isinstance(item, str) or not item.strip() for item in value):
        raise ExperimentError(f"{field}: expected non-empty strings")
    return value


def _base(doc: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    if doc.get("version") != 1:
        raise ExperimentError("knowledge artifact version must be 1")
    if doc.get("kind") != "harness-knowledge-artifact":
        raise ExperimentError("kind must be harness-knowledge-artifact")
    schema = doc.get("schema")
    if not isinstance(schema, str) or not schema:
        raise ExperimentError("schema is required")
    artifact = doc.get("artifact")
    if not isinstance(artifact, str) or not artifact:
        raise ExperimentError("artifact is required")
    title = doc.get("title")
    if not isinstance(title, str) or not title.strip():
        raise ExperimentError("title is required")
    research = doc.get("research")
    if not isinstance(research, dict):
        raise ExperimentError("research metadata is required for experiment candidates")
    source = research.get("source")
    if not isinstance(source, str) or not source:
        raise ExperimentError("research.source is required")
    claims = _strings(research.get("capability_claims", []), "research.capability_claims", allow_empty=False)
    if len(claims) != len(set(claims)):
        raise ExperimentError("research.capability_claims must be unique")
    content = doc.get("content")
    if not isinstance(content, dict):
        raise ExperimentError("content must be a mapping")
    return schema, content


def _validate_product_requirements(content: dict[str, Any]) -> None:
    purpose = content.get("purpose")
    if not isinstance(purpose, str) or not purpose.strip():
        raise ExperimentError("product-requirements purpose is required")
    _strings(content.get("goals", []), "goals", allow_empty=False)
    groups = content.get("requirement_groups")
    if not isinstance(groups, list) or not groups:
        raise ExperimentError("requirement_groups must be a non-empty list")
    seen: set[str] = set()
    for group in groups:
        if not isinstance(group, dict):
            raise ExperimentError("requirement group must be a mapping")
        group_id = group.get("id")
        title = group.get("title")
        if not isinstance(group_id, str) or not group_id:
            raise ExperimentError("requirement group id is required")
        if group_id in seen:
            raise ExperimentError(f"duplicate requirement group id: {group_id}")
        seen.add(group_id)
        if not isinstance(title, str) or not title.strip():
            raise ExperimentError(f"{group_id}: title is required")
        _strings(group.get("requirements", []), f"{group_id}.requirements", allow_empty=False)
    _strings(content.get("constraints", []), "constraints")
    _strings(content.get("acceptance_examples", []), "acceptance_examples")
    _strings(content.get("non_goals", []), "non_goals")
    evidence = content.get("evidence", [])
    if not isinstance(evidence, list):
        raise ExperimentError("evidence: expected list")
    for index, item in enumerate(evidence):
        if not isinstance(item, dict):
            raise ExperimentError(f"evidence[{index}]: expected mapping")
        if not isinstance(item.get("kind"), str) or not item["kind"].strip():
            raise ExperimentError(f"evidence[{index}].kind is required")
        meaningful = [
            item.get("ref"),
            item.get("statement"),
            item.get("accepted_requirement_id"),
            item.get("rule"),
        ]
        if not any(isinstance(value, str) and value.strip() for value in meaningful):
            raise ExperimentError(f"evidence[{index}] requires ref/statement/accepted_requirement_id/rule")
        date = item.get("date")
        if date is not None and (not isinstance(date, str) or not date.strip()):
            raise ExperimentError(f"evidence[{index}].date must be a non-empty string")


def _validate_implementation_design(content: dict[str, Any]) -> None:
    purpose = content.get("purpose")
    if not isinstance(purpose, str) or not purpose.strip():
        raise ExperimentError("implementation-design purpose is required")
    sections = content.get("design_sections")
    if not isinstance(sections, list) or not sections:
        raise ExperimentError("design_sections must be a non-empty list")
    seen: set[str] = set()
    for section in sections:
        if not isinstance(section, dict):
            raise ExperimentError("design section must be a mapping")
        section_id = section.get("id")
        title = section.get("title")
        if not isinstance(section_id, str) or not section_id:
            raise ExperimentError("design section id is required")
        if section_id in seen:
            raise ExperimentError(f"duplicate design section id: {section_id}")
        seen.add(section_id)
        if not isinstance(title, str) or not title.strip():
            raise ExperimentError(f"{section_id}: title is required")
        _strings(section.get("decisions", []), f"{section_id}.decisions", allow_empty=False)
    _strings(content.get("implementation_slices", []), "implementation_slices", allow_empty=False)
    _strings(content.get("completion_criteria", []), "completion_criteria", allow_empty=False)
    _strings(content.get("forbidden_decisions", []), "forbidden_decisions")
    _strings(content.get("open_questions", []), "open_questions")
    _strings(content.get("design_refs", []), "design_refs")
    _strings(content.get("authorization_semantics", []), "authorization_semantics")



def _validate_cli_contract(content: dict[str, Any]) -> None:
    command = content.get("command")
    if not isinstance(command, str) or not command.strip():
        raise ExperimentError("cli-contract command is required")
    arguments = content.get("arguments")
    if not isinstance(arguments, list) or not arguments:
        raise ExperimentError("cli-contract arguments must be a non-empty list")
    seen: set[str] = set()
    for item in arguments:
        if not isinstance(item, dict):
            raise ExperimentError("cli-contract argument must be a mapping")
        name = item.get("name")
        if not isinstance(name, str) or not name.strip():
            raise ExperimentError("cli-contract argument name is required")
        if name in seen:
            raise ExperimentError(f"duplicate cli argument: {name}")
        seen.add(name)
        if not isinstance(item.get("semantics"), str) or not item["semantics"].strip():
            raise ExperimentError(f"cli-contract argument {name}: semantics are required")
        required = item.get("required")
        if required is not None and not isinstance(required, bool):
            raise ExperimentError(f"cli-contract argument {name}: required must be boolean")
    _strings(content.get("success_semantics", []), "success_semantics", allow_empty=False)
    failures = content.get("failure_classes", [])
    if not isinstance(failures, list):
        raise ExperimentError("failure_classes must be a list")
    failure_ids: set[str] = set()
    for item in failures:
        if not isinstance(item, dict):
            raise ExperimentError("failure class must be a mapping")
        failure_id = item.get("id")
        if not isinstance(failure_id, str) or not failure_id:
            raise ExperimentError("failure class id is required")
        if failure_id in failure_ids:
            raise ExperimentError(f"duplicate failure class id: {failure_id}")
        failure_ids.add(failure_id)
        _strings(item.get("conditions", []), f"{failure_id}.conditions", allow_empty=False)
        _strings(item.get("result_semantics", []), f"{failure_id}.result_semantics", allow_empty=False)
        exit_status = item.get("exit_status")
        if exit_status is not None and not isinstance(exit_status, int):
            raise ExperimentError(f"{failure_id}.exit_status must be integer when present")
    _strings(content.get("representation_rules", []), "representation_rules")
    _strings(content.get("boundary_rules", []), "boundary_rules")
    _strings(content.get("scope_exclusions", []), "scope_exclusions")

VALIDATORS = {
    "product-requirements/v0-experiment": _validate_product_requirements,
    "implementation-design/v0-experiment": _validate_implementation_design,
    "cli-contract/v0-experiment": _validate_cli_contract,
}


def validate(path: Path) -> str:
    doc = _load(path)
    schema, content = _base(doc)
    validator = VALIDATORS.get(schema)
    if validator is None:
        raise ExperimentError(f"unsupported experimental schema: {schema}")
    validator(content)
    return schema


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="+")
    args = parser.parse_args()
    for raw in args.paths:
        path = Path(raw)
        schema = validate(path)
        print(f"{path}: PASS [{schema}]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
