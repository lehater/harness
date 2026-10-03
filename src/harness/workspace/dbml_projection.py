#!/usr/bin/env python3
"""Validate one source-bounded DBML data-model generated projection."""
from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Any

import yaml

from harness.project_model.core import CoreError
from harness.workspace.projection_boundary import (
    bind_projection_sources,
    repository_relative_path,
)

PROJECTION_ID = "data-model-dbml"
PROFILE_KIND = "harness-dbml-data-model-profile"
PROVENANCE_KIND = "harness-generated-projection-provenance"


def load_yaml(path: str | Path) -> dict[str, Any]:
    path = Path(path)
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise CoreError(f"cannot load {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise CoreError(f"{path} must contain a mapping")
    return value


def validate_profile(profile: dict[str, Any]) -> dict[str, Any]:
    if profile.get("version") != 1:
        raise CoreError("DBML data-model profile version must be 1")
    if profile.get("kind") != PROFILE_KIND:
        raise CoreError("unexpected DBML data-model profile kind")
    if profile.get("projection") != PROJECTION_ID:
        raise CoreError("DBML data-model profile projection id mismatch")

    profile_id = profile.get("id")
    if not isinstance(profile_id, str) or not profile_id:
        raise CoreError("DBML data-model profile id is required")

    scope = profile.get("scope")
    if not isinstance(scope, dict):
        raise CoreError("DBML data-model profile scope must be a mapping")
    scope_pattern = scope.get("id_pattern")
    if not isinstance(scope_pattern, str) or not scope_pattern:
        raise CoreError("DBML data-model profile scope id_pattern is required")
    try:
        re.compile(scope_pattern)
    except re.error as exc:
        raise CoreError(f"DBML data-model scope id_pattern is invalid: {exc}") from exc

    output = profile.get("output")
    if not isinstance(output, dict):
        raise CoreError("DBML data-model profile output must be a mapping")
    for key in ("dbml", "provenance"):
        template = output.get(key)
        if not isinstance(template, str) or not template:
            raise CoreError(f"DBML {key} output template is required")
        if template.count("{scope-id}") != 1:
            raise CoreError(
                f"DBML {key} output template must contain exactly one {{scope-id}}"
            )
        if "{" in template.replace("{scope-id}", "") or "}" in template.replace(
            "{scope-id}", ""
        ):
            raise CoreError(f"DBML {key} output template has unsupported placeholder")
        rendered = repository_relative_path(
            template.replace("{scope-id}", "scope"),
            f"DBML {key} output",
        )
        if not rendered.startswith("docs/generated/"):
            raise CoreError(f"DBML {key} output must remain under docs/generated/")
    if output["dbml"] == output["provenance"]:
        raise CoreError("DBML and provenance output templates must differ")

    dbml = profile.get("dbml")
    if not isinstance(dbml, dict):
        raise CoreError("DBML data-model profile dbml must be a mapping")
    identifier_pattern = dbml.get("identifier_pattern")
    if not isinstance(identifier_pattern, str) or not identifier_pattern:
        raise CoreError("DBML identifier_pattern is required")
    try:
        re.compile(identifier_pattern)
    except re.error as exc:
        raise CoreError(f"DBML identifier_pattern is invalid: {exc}") from exc
    if dbml.get("table_ordering") != "declaration":
        raise CoreError("DBML v1 table_ordering must be declaration")
    if dbml.get("column_ordering") != "declaration":
        raise CoreError("DBML v1 column_ordering must be declaration")
    if dbml.get("enum_policy") != "explicit-canonical-only":
        raise CoreError("DBML v1 enum policy must be explicit-canonical-only")
    if dbml.get("relationship_representation") != (
        "Ref: <fk-table>.<fk-column> > <referenced-table>.<referenced-column>"
    ):
        raise CoreError("DBML v1 relationship representation is invalid")

    required_header = dbml.get("required_header")
    if required_header != [
        "// GENERATED PROJECTION",
        "// NOT A SOURCE OF TRUTH",
    ]:
        raise CoreError("DBML v1 required_header is invalid")

    if set(dbml.get("allowed_column_settings") or []) != {
        "pk",
        "not null",
        "unique",
    }:
        raise CoreError("DBML v1 allowed_column_settings is invalid")
    if set(dbml.get("allowed_constraint_settings") or []) != {"pk", "unique"}:
        raise CoreError("DBML v1 allowed_constraint_settings is invalid")
    for key in (
        "allow_inline_ref",
        "allow_notes",
        "allow_defaults",
        "allow_column_type_arguments",
        "allow_non_unique_indexes",
    ):
        if dbml.get(key) is not False:
            raise CoreError(f"DBML v1 {key} must be false")

    basic_types = dbml.get("basic_data_types")
    if (
        not isinstance(basic_types, list)
        or not basic_types
        or any(not isinstance(item, str) or not item for item in basic_types)
        or len(basic_types) != len(set(basic_types))
    ):
        raise CoreError("DBML v1 basic_data_types must be a unique non-empty list")

    validation = profile.get("validation")
    if not isinstance(validation, dict):
        raise CoreError("DBML data-model profile validation must be a mapping")
    if validation.get("require_output_under") != "docs/generated/":
        raise CoreError("DBML v1 require_output_under must be docs/generated/")
    for key in (
        "require_unique_names",
        "require_reference_endpoints",
        "require_reference_target_key",
    ):
        if validation.get(key) is not True:
            raise CoreError(f"DBML v1 {key} must be true")
    return profile


def validate_scope(scope_id: Any, profile: dict[str, Any]) -> str:
    validate_profile(profile)
    if not isinstance(scope_id, str) or not scope_id:
        raise CoreError("DBML projection scope-id is required")
    if not re.fullmatch(profile["scope"]["id_pattern"], scope_id):
        raise CoreError(f"DBML projection scope-id is invalid: {scope_id}")
    return scope_id


def expected_output_paths(profile: dict[str, Any], scope_id: str) -> dict[str, str]:
    validate_scope(scope_id, profile)
    rendered = {
        key: repository_relative_path(
            value.replace("{scope-id}", scope_id),
            f"DBML {key} output",
        )
        for key, value in profile["output"].items()
    }
    required_root = profile["validation"]["require_output_under"]
    for key, value in rendered.items():
        if not value.startswith(required_root):
            raise CoreError(f"DBML {key} output escapes generated boundary: {value}")
    if rendered["dbml"] == rendered["provenance"]:
        raise CoreError("DBML and provenance outputs must differ")
    return rendered


def expected_provenance(
    manifest: dict[str, Any],
    plan: dict[str, Any],
    *,
    document_id: str,
    section_id: str,
    scope_id: str,
    profile: dict[str, Any],
) -> dict[str, Any]:
    validate_profile(profile)
    validate_scope(scope_id, profile)
    section, sources = bind_projection_sources(
        manifest,
        plan,
        document_id=document_id,
        section_id=section_id,
        renderer=PROJECTION_ID,
        projection_label="DBML projection",
    )
    if section.get("scope") != scope_id:
        raise CoreError(
            f"DBML projection scope-id {scope_id} does not match plan scope "
            f"{section.get('scope')!r}"
        )

    outputs = expected_output_paths(profile, scope_id)
    return {
        "version": 1,
        "kind": PROVENANCE_KIND,
        "projection": PROJECTION_ID,
        "profile": profile["id"],
        "profile_version": profile["version"],
        "scope": scope_id,
        "manifest_digest": manifest["manifest_digest"],
        "document": document_id,
        "section": section_id,
        "sources": sources,
        "outputs": [
            outputs["dbml"],
            outputs["provenance"],
        ],
    }


def _parse_settings(
    value: str | None,
    *,
    allowed: set[str],
    label: str,
) -> set[str]:
    if value is None:
        return set()
    settings = {item.strip() for item in value.split(",")}
    if not settings or "" in settings:
        raise CoreError(f"{label} has invalid settings")
    unknown = sorted(settings - allowed)
    if unknown:
        raise CoreError(f"{label} has unsupported settings: {', '.join(unknown)}")
    return settings


def _identifier(value: str, profile: dict[str, Any], label: str) -> str:
    if not re.fullmatch(profile["dbml"]["identifier_pattern"], value):
        raise CoreError(f"{label} is not a supported DBML identifier: {value}")
    return value


def parse_dbml(text: str, profile: dict[str, Any]) -> dict[str, Any]:
    validate_profile(profile)
    if not isinstance(text, str) or not text.strip():
        raise CoreError("DBML content is required")

    lines = text.splitlines()
    header = [line.strip() for line in lines if line.strip()][:2]
    if header != profile["dbml"]["required_header"]:
        raise CoreError("DBML projection requires generated/non-source header")

    table_re = re.compile(r"^Table\s+([A-Za-z_][A-Za-z0-9_]*)\s*\{$")
    enum_re = re.compile(r"^Enum\s+([A-Za-z_][A-Za-z0-9_]*)\s*\{$")
    column_re = re.compile(
        r"^([A-Za-z_][A-Za-z0-9_]*)\s+"
        r"([A-Za-z_][A-Za-z0-9_]*)"
        r"(?:\s+\[([^\]]+)\])?$"
    )
    constraint_re = re.compile(r"^\(([^)]+)\)\s+\[([^\]]+)\]$")
    ref_re = re.compile(
        r"^Ref:\s*"
        r"([A-Za-z_][A-Za-z0-9_]*)\.([A-Za-z_][A-Za-z0-9_]*)\s*>\s*"
        r"([A-Za-z_][A-Za-z0-9_]*)\.([A-Za-z_][A-Za-z0-9_]*)$"
    )

    tables: dict[str, dict[str, Any]] = {}
    enums: dict[str, list[str]] = {}
    refs: list[tuple[str, str, str, str]] = []
    mode: str | None = None
    current: str | None = None

    for number, raw in enumerate(lines, start=1):
        line = raw.strip()
        if not line or line.startswith("//"):
            continue

        if mode is None:
            match = table_re.fullmatch(line)
            if match:
                name = _identifier(match.group(1), profile, "table name")
                if name in tables:
                    raise CoreError(f"duplicate DBML table: {name}")
                if name in enums:
                    raise CoreError(f"DBML identifier collides with enum: {name}")
                tables[name] = {"columns": {}, "constraints": []}
                mode, current = "table", name
                continue

            match = enum_re.fullmatch(line)
            if match:
                name = _identifier(match.group(1), profile, "enum name")
                if name in enums:
                    raise CoreError(f"duplicate DBML enum: {name}")
                if name in tables:
                    raise CoreError(f"DBML identifier collides with table: {name}")
                enums[name] = []
                mode, current = "enum", name
                continue

            match = ref_re.fullmatch(line)
            if match:
                ref = tuple(match.groups())
                if ref in refs:
                    raise CoreError(
                        "duplicate DBML reference: "
                        + f"{ref[0]}.{ref[1]} > {ref[2]}.{ref[3]}"
                    )
                refs.append(ref)
                continue

            raise CoreError(f"unsupported DBML construct at line {number}: {line}")

        if mode == "enum":
            if line == "}":
                mode, current = None, None
                continue
            assert current is not None
            value = _identifier(line, profile, f"enum {current} value")
            if value in enums[current]:
                raise CoreError(f"duplicate DBML enum value: {current}.{value}")
            enums[current].append(value)
            continue

        if mode == "table":
            assert current is not None
            if line == "}":
                mode, current = None, None
                continue
            if line == "indexes {":
                mode = "indexes"
                continue
            match = column_re.fullmatch(line)
            if match is None:
                raise CoreError(
                    f"unsupported DBML table construct at line {number}: {line}"
                )
            name, data_type, raw_settings = match.groups()
            name = _identifier(name, profile, f"column name in {current}")
            if name in tables[current]["columns"]:
                raise CoreError(f"duplicate DBML column: {current}.{name}")
            settings = _parse_settings(
                raw_settings,
                allowed=set(profile["dbml"]["allowed_column_settings"]),
                label=f"DBML column {current}.{name}",
            )
            tables[current]["columns"][name] = {
                "type": data_type,
                "settings": settings,
            }
            continue

        if mode == "indexes":
            assert current is not None
            if line == "}":
                mode = "table"
                continue
            match = constraint_re.fullmatch(line)
            if match is None:
                raise CoreError(
                    f"unsupported DBML indexes construct at line {number}: {line}"
                )
            raw_columns, raw_settings = match.groups()
            columns = [item.strip() for item in raw_columns.split(",")]
            if (
                not columns
                or any(not item for item in columns)
                or len(columns) != len(set(columns))
            ):
                raise CoreError(f"DBML constraint in {current} has invalid columns")
            for column in columns:
                _identifier(column, profile, f"constraint column in {current}")
            settings = _parse_settings(
                raw_settings,
                allowed=set(profile["dbml"]["allowed_constraint_settings"]),
                label=f"DBML constraint in {current}",
            )
            if len(settings) != 1:
                raise CoreError(
                    f"DBML constraint in {current} must be exactly pk or unique"
                )
            kind = next(iter(settings))
            constraint = (tuple(columns), kind)
            if constraint in tables[current]["constraints"]:
                raise CoreError(f"duplicate DBML constraint in table {current}")
            tables[current]["constraints"].append(constraint)
            continue

        raise CoreError(f"invalid DBML parser state at line {number}")

    if mode is not None:
        raise CoreError(f"DBML {mode} block is not closed")
    if not tables:
        raise CoreError("DBML projection requires at least one table")

    basic_types = set(profile["dbml"]["basic_data_types"])
    for table_name, table in tables.items():
        for column_name, column in table["columns"].items():
            data_type = column["type"]
            if data_type not in basic_types and data_type not in enums:
                raise CoreError(
                    f"DBML column {table_name}.{column_name} has unsupported type "
                    f"{data_type}"
                )
        for columns, kind in table["constraints"]:
            missing = [name for name in columns if name not in table["columns"]]
            if missing:
                raise CoreError(
                    f"DBML {kind} constraint in {table_name} references unknown "
                    f"columns: {', '.join(missing)}"
                )

    for source_table, source_column, target_table, target_column in refs:
        source = tables.get(source_table)
        target = tables.get(target_table)
        if source is None:
            raise CoreError(f"DBML reference source table does not exist: {source_table}")
        if target is None:
            raise CoreError(f"DBML reference target table does not exist: {target_table}")
        if source_column not in source["columns"]:
            raise CoreError(
                f"DBML reference source column does not exist: "
                f"{source_table}.{source_column}"
            )
        if target_column not in target["columns"]:
            raise CoreError(
                f"DBML reference target column does not exist: "
                f"{target_table}.{target_column}"
            )
        target_settings = target["columns"][target_column]["settings"]
        if not ({"pk", "unique"} & target_settings):
            raise CoreError(
                f"DBML reference target must be a single-column pk/unique key: "
                f"{target_table}.{target_column}"
            )

    return {"tables": tables, "enums": enums, "refs": refs}


def validate_dbml(text: str, profile: dict[str, Any]) -> None:
    parse_dbml(text, profile)


def validate_generated_projection(
    manifest: dict[str, Any],
    plan: dict[str, Any],
    *,
    document_id: str,
    section_id: str,
    scope_id: str,
    profile: dict[str, Any],
    dbml_text: str,
    provenance: dict[str, Any],
    dbml_path: str | None = None,
    provenance_path: str | None = None,
) -> None:
    expected = expected_provenance(
        manifest,
        plan,
        document_id=document_id,
        section_id=section_id,
        scope_id=scope_id,
        profile=profile,
    )
    if provenance != expected:
        raise CoreError(
            "DBML projection provenance does not match current manifest/plan/scope"
        )
    paths = expected_output_paths(profile, scope_id)
    if dbml_path is not None and repository_relative_path(dbml_path, "DBML path") != paths["dbml"]:
        raise CoreError("DBML projection path does not match profile/scope")
    if (
        provenance_path is not None
        and repository_relative_path(provenance_path, "DBML provenance path")
        != paths["provenance"]
    ):
        raise CoreError("DBML provenance path does not match profile/scope")
    validate_dbml(dbml_text, profile)


def _write_yaml(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(value, sort_keys=False), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate one Harness DBML data-model generated projection"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    for name in ("provenance", "validate"):
        command = sub.add_parser(name)
        command.add_argument("--manifest", required=True)
        command.add_argument("--plan", required=True)
        command.add_argument("--document", required=True)
        command.add_argument("--section", required=True)
        command.add_argument("--scope", required=True)
        command.add_argument("--profile", required=True)
        if name == "provenance":
            command.add_argument("--output")
        else:
            command.add_argument("--dbml", required=True)
            command.add_argument("--provenance", required=True)

    args = parser.parse_args()
    manifest = load_yaml(args.manifest)
    plan = load_yaml(args.plan)
    profile = load_yaml(args.profile)

    if args.command == "provenance":
        provenance = expected_provenance(
            manifest,
            plan,
            document_id=args.document,
            section_id=args.section,
            scope_id=args.scope,
            profile=profile,
        )
        if args.output:
            expected_path = expected_output_paths(profile, args.scope)["provenance"]
            if repository_relative_path(args.output, "DBML provenance output") != expected_path:
                raise CoreError(
                    "DBML provenance output path does not match profile/scope"
                )
            _write_yaml(Path(args.output), provenance)
        else:
            print(yaml.safe_dump(provenance, sort_keys=False), end="")
        return 0

    expected_paths = expected_output_paths(profile, args.scope)
    if repository_relative_path(args.dbml, "DBML path") != expected_paths["dbml"]:
        raise CoreError("DBML projection path does not match profile/scope")
    if (
        repository_relative_path(args.provenance, "DBML provenance path")
        != expected_paths["provenance"]
    ):
        raise CoreError("DBML provenance path does not match profile/scope")

    provenance = load_yaml(args.provenance)
    dbml_text = Path(args.dbml).read_text(encoding="utf-8")
    validate_generated_projection(
        manifest,
        plan,
        document_id=args.document,
        section_id=args.section,
        scope_id=args.scope,
        profile=profile,
        dbml_text=dbml_text,
        provenance=provenance,
        dbml_path=args.dbml,
        provenance_path=args.provenance,
    )
    print("DBML data-model projection valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
