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
    if doc.get("version") != 0:
        raise ExperimentError("version must be 0 for the research experiment")
    if doc.get("kind") != "harness-artifact-schema-candidate":
        raise ExperimentError("kind must be harness-artifact-schema-candidate")
    schema = doc.get("schema")
    if not isinstance(schema, str) or not schema:
        raise ExperimentError("schema is required")
    artifact = doc.get("artifact")
    if not isinstance(artifact, str) or not artifact:
        raise ExperimentError("artifact is required")
    source = doc.get("source")
    if not isinstance(source, str) or not source:
        raise ExperimentError("source is required")
    claims = _strings(doc.get("capability_claims", []), "capability_claims", allow_empty=False)
    if len(claims) != len(set(claims)):
        raise ExperimentError("capability_claims must be unique")
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
    _strings(content.get("evidence_refs", []), "evidence_refs")


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


VALIDATORS = {
    "product-requirements/v0-experiment": _validate_product_requirements,
    "implementation-design/v0-experiment": _validate_implementation_design,
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
