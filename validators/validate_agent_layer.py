#!/usr/bin/env python3
"""Validate the explicit Harness skill-surface model and active skill contracts."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from harness import CoreError  # noqa: E402
from target_state import validate_profile  # noqa: E402

SURFACE_REGISTRY = ROOT / "skills/skill-surface-registry-v0.yaml"
ARTIFACT_REGISTRY = ROOT / "skills/artifact-skill-registry-v0.yaml"
CONSUMER_OPERATION_REGISTRY = ROOT / "skills/consumer-operation-registry-v0.yaml"
MAINTAINER_OPERATION_REGISTRY = ROOT / "skills/maintainer-operation-registry-v0.yaml"

ALLOWED_SURFACES = {"maintainer", "consumer"}
ALLOWED_ROUTE_CLASSES = {"operation", "method", "artifact-production"}
ALLOWED_LIFECYCLES = {"active", "deprecated", "archived"}
ALLOWED_ROUTE_STATUS = {"routed", "unrouted", "not-applicable"}


def _load_mapping(path: Path) -> dict[str, Any]:
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise CoreError(f"cannot load {path.relative_to(ROOT)}: {exc}") from exc
    if not isinstance(value, dict):
        raise CoreError(f"{path.relative_to(ROOT)} must contain a mapping")
    return value


def _physical_skill_paths() -> set[str]:
    return {
        path.relative_to(ROOT).as_posix()
        for path in (ROOT / "skills").glob("*/*/SKILL.md")
        if path.is_file()
    }


def _frontmatter(path: Path, text: str, errors: list[str]) -> dict[str, Any] | None:
    if not text.startswith("---\n"):
        errors.append(f"skill missing frontmatter: {path.relative_to(ROOT)}")
        return None
    end = text.find("\n---\n", 4)
    if end < 0:
        errors.append(f"skill has unterminated frontmatter: {path.relative_to(ROOT)}")
        return None
    try:
        metadata = yaml.safe_load(text[4:end])
    except yaml.YAMLError as exc:
        errors.append(f"skill invalid frontmatter {path.relative_to(ROOT)}: {exc}")
        return None
    if not isinstance(metadata, dict):
        errors.append(f"skill frontmatter must be a mapping: {path.relative_to(ROOT)}")
        return None
    for key in ("name", "description"):
        if not isinstance(metadata.get(key), str) or not metadata[key].strip():
            errors.append(f"skill frontmatter missing {key}: {path.relative_to(ROOT)}")
    return metadata


def _require(path: Path, text: str, fragments: tuple[str, ...], errors: list[str]) -> None:
    for fragment in fragments:
        if fragment not in text:
            errors.append(
                f"skill {path.relative_to(ROOT)} missing contract fragment: {fragment}"
            )


def _validate_surface_registry(errors: list[str]) -> list[dict[str, Any]]:
    try:
        registry = _load_mapping(SURFACE_REGISTRY)
    except CoreError as exc:
        errors.append(str(exc))
        return []

    if registry.get("version") != 1:
        errors.append("skill surface registry version must be 1")
    if registry.get("kind") != "harness-skill-surface-registry":
        errors.append("unexpected skill surface registry kind")
    if not isinstance(registry.get("id"), str) or not registry["id"]:
        errors.append("skill surface registry id is required")

    entries = registry.get("skills")
    if not isinstance(entries, list):
        errors.append("skill surface registry skills must be a list")
        return []

    seen_ids: set[str] = set()
    seen_paths: set[str] = set()
    normalized: list[dict[str, Any]] = []

    for index, item in enumerate(entries):
        label = f"skill surface entry #{index + 1}"
        if not isinstance(item, dict):
            errors.append(f"{label} must be a mapping")
            continue

        required = {
            "id", "path", "surface", "route_class", "lifecycle", "route_status"
        }
        missing = sorted(required - set(item))
        if missing:
            errors.append(f"{label} missing fields: {', '.join(missing)}")
            continue

        skill_id = item["id"]
        path_value = item["path"]
        surface = item["surface"]
        route_class = item["route_class"]
        lifecycle = item["lifecycle"]
        route_status = item["route_status"]

        if not isinstance(skill_id, str) or not skill_id:
            errors.append(f"{label} id must be a non-empty string")
            continue
        if skill_id in seen_ids:
            errors.append(f"duplicate skill id in surface registry: {skill_id}")
        seen_ids.add(skill_id)

        if not isinstance(path_value, str) or not path_value:
            errors.append(f"{skill_id}: path must be a non-empty string")
            continue
        if path_value in seen_paths:
            errors.append(f"duplicate skill path in surface registry: {path_value}")
        seen_paths.add(path_value)

        if surface not in ALLOWED_SURFACES:
            errors.append(f"{skill_id}: invalid surface {surface!r}")
        if route_class not in ALLOWED_ROUTE_CLASSES:
            errors.append(f"{skill_id}: invalid route_class {route_class!r}")
        if lifecycle not in ALLOWED_LIFECYCLES:
            errors.append(f"{skill_id}: invalid lifecycle {lifecycle!r}")
        if route_status not in ALLOWED_ROUTE_STATUS:
            errors.append(f"{skill_id}: invalid route_status {route_status!r}")

        knowledge_kind = item.get("knowledge_kind")
        if route_class != "artifact-production" and knowledge_kind is not None:
            errors.append(
                f"{skill_id}: knowledge_kind is only valid for artifact-production"
            )
        if route_status == "routed" and route_class == "artifact-production":
            if not isinstance(knowledge_kind, str) or not knowledge_kind:
                errors.append(
                    f"{skill_id}: routed artifact-production requires knowledge_kind"
                )
        if lifecycle == "active" and route_status == "not-applicable":
            errors.append(f"{skill_id}: active skill cannot have not-applicable routing")
        if lifecycle in {"deprecated", "archived"} and route_status != "not-applicable":
            errors.append(
                f"{skill_id}: non-active skill must have route_status not-applicable"
            )
        if route_status == "unrouted":
            note = item.get("route_note")
            if not isinstance(note, str) or not note.strip():
                errors.append(f"{skill_id}: unrouted skill requires route_note")

        path = ROOT / path_value
        if not path.is_file():
            errors.append(f"{skill_id}: registered skill does not exist: {path_value}")
            continue

        text = path.read_text(encoding="utf-8")
        metadata = _frontmatter(path, text, errors)
        if metadata is not None and metadata.get("name") != skill_id:
            errors.append(
                f"{path_value}: frontmatter name {metadata.get('name')!r} "
                f"does not match registered id {skill_id!r}"
            )

        normalized.append(item)

    physical = _physical_skill_paths()
    registered = {item["path"] for item in normalized if isinstance(item.get("path"), str)}
    missing_from_registry = sorted(physical - registered)
    stale_registry_paths = sorted(registered - physical)
    if missing_from_registry:
        errors.append(
            "active-looking SKILL.md files missing from surface registry: "
            + ", ".join(missing_from_registry)
        )
    if stale_registry_paths:
        errors.append(
            "surface registry references missing SKILL.md files: "
            + ", ".join(stale_registry_paths)
        )

    return normalized


def _validate_artifact_registry_alignment(
    entries: list[dict[str, Any]], errors: list[str]
) -> None:
    try:
        registry = _load_mapping(ARTIFACT_REGISTRY)
    except CoreError as exc:
        errors.append(str(exc))
        return

    routes = registry.get("routes")
    if not isinstance(routes, list):
        errors.append("artifact skill registry routes must be a list")
        return

    actual: dict[str, str] = {}
    for item in routes:
        if not isinstance(item, dict):
            errors.append("artifact skill registry route must be a mapping")
            continue
        kind = item.get("knowledge_kind")
        path = item.get("skill")
        if not isinstance(kind, str) or not kind or not isinstance(path, str) or not path:
            errors.append("artifact skill registry route requires knowledge_kind and skill")
            continue
        if kind in actual:
            errors.append(f"duplicate artifact knowledge_kind route: {kind}")
        actual[kind] = path

    expected = {
        item["knowledge_kind"]: item["path"]
        for item in entries
        if item.get("lifecycle") == "active"
        and item.get("route_class") == "artifact-production"
        and item.get("route_status") == "routed"
        and isinstance(item.get("knowledge_kind"), str)
    }
    if actual != expected:
        errors.append(
            "artifact registry does not match routed artifact-production skills "
            f"(expected={expected!r}, actual={actual!r})"
        )




def _validate_operation_registry_alignment(
    entries: list[dict[str, Any]],
    errors: list[str],
    *,
    registry_path: Path,
    expected_kind: str,
    surface: str,
) -> None:
    try:
        registry = _load_mapping(registry_path)
    except CoreError as exc:
        errors.append(str(exc))
        return

    label = f"{surface} operation"
    if registry.get("version") != 1:
        errors.append(f"{label} registry version must be 1")
    if registry.get("kind") != expected_kind:
        errors.append(f"unexpected {label} registry kind")
    if not isinstance(registry.get("id"), str) or not registry["id"]:
        errors.append(f"{label} registry id is required")

    routes = registry.get("routes")
    if not isinstance(routes, list):
        errors.append(f"{label} registry routes must be a list")
        return

    actual_paths: set[str] = set()
    public_operations: set[str] = set()
    operation_ids: set[str] = set()
    public_triggers: set[str] = set()
    internal_refs: list[tuple[str, list[str]]] = []

    for item in routes:
        if not isinstance(item, dict):
            errors.append(f"{label} route must be a mapping")
            continue
        operation = item.get("operation")
        path = item.get("skill")
        exposure = item.get("exposure")
        if not isinstance(operation, str) or not operation:
            errors.append(f"{label} route requires operation")
            continue
        if operation in operation_ids:
            errors.append(f"duplicate {label} id: {operation}")
        operation_ids.add(operation)
        if not isinstance(path, str) or not path:
            errors.append(f"{operation}: {label} skill path is required")
            continue
        if path in actual_paths:
            errors.append(f"{label} skill routed more than once: {path}")
        actual_paths.add(path)
        if exposure not in {"public", "internal"}:
            errors.append(f"{operation}: invalid exposure {exposure!r}")
            continue

        if exposure == "public":
            trigger = item.get("trigger")
            if not isinstance(trigger, str) or not trigger:
                errors.append(f"{operation}: public route requires trigger")
            elif trigger in public_triggers:
                errors.append(f"duplicate public {label} trigger: {trigger}")
            else:
                public_triggers.add(trigger)
            public_operations.add(operation)
            if "invoked_by" in item:
                errors.append(f"{operation}: public route must not declare invoked_by")
        else:
            invoked_by = item.get("invoked_by")
            if (
                not isinstance(invoked_by, list)
                or not invoked_by
                or not all(isinstance(value, str) and value for value in invoked_by)
            ):
                errors.append(f"{operation}: internal route requires invoked_by")
            else:
                internal_refs.append((operation, invoked_by))
            if "trigger" in item:
                errors.append(f"{operation}: internal route must not expose trigger")

    for operation, parents in internal_refs:
        missing = sorted(set(parents) - public_operations)
        if missing:
            errors.append(
                f"{operation}: invoked_by references non-public operations: "
                + ", ".join(missing)
            )

    expected_paths = {
        item["path"]
        for item in entries
        if item.get("lifecycle") == "active"
        and item.get("surface") == surface
        and item.get("route_class") == "operation"
        and item.get("route_status") == "routed"
    }
    if actual_paths != expected_paths:
        errors.append(
            f"{label} registry does not match routed {label}s "
            f"(expected={sorted(expected_paths)!r}, actual={sorted(actual_paths)!r})"
        )

def _validate_skill_contracts(
    entries: list[dict[str, Any]], errors: list[str]
) -> tuple[int, int, int]:
    operation_count = 0
    method_count = 0
    artifact_count = 0
    decision_governed = {
        "application-design",
        "domain-model",
        "implementation-design",
        "system-architecture",
    }

    for item in entries:
        if item.get("lifecycle") != "active":
            continue
        path = ROOT / item["path"]
        text = path.read_text(encoding="utf-8")
        route_class = item["route_class"]

        if route_class == "operation":
            operation_count += 1
            _require(path, text, ("## Trigger", "## Inputs", "## Procedure"), errors)
        elif route_class == "method":
            method_count += 1
            _require(path, text, ("## Trigger", "## Inputs", "## Procedure"), errors)
        elif route_class == "artifact-production":
            artifact_count += 1
            _require(
                path,
                text,
                (
                    "## Trigger",
                    "## Inputs",
                    "## Read boundary",
                    "## Procedure",
                    "## Stop conditions",
                    "## Registration",
                    "## Human projection",
                ),
                errors,
            )
            if "## Output schema" not in text and "## Output contract" not in text:
                errors.append(
                    f"artifact-production skill {path.relative_to(ROOT)} "
                    "must define Output schema or Output contract"
                )
            if "acceptance" not in text.lower():
                errors.append(
                    f"artifact-production skill {path.relative_to(ROOT)} "
                    "must define acceptance checks"
                )
            if item["id"] in decision_governed:
                _require(path, text, ("## Decision exploration",), errors)

    return operation_count, method_count, artifact_count


def _validate_starter_profile(errors: list[str]) -> None:
    starter = ROOT / "profiles/software-application-design-v0.yaml"
    if not starter.is_file():
        errors.append("missing software application starter profile")
        return
    try:
        profile = yaml.safe_load(starter.read_text(encoding="utf-8"))
        if not isinstance(profile, dict):
            raise CoreError("starter profile must contain a mapping")
        validate_profile(profile)
        expected = {
            "PROBLEM": [],
            "REQUIREMENTS": ["PROBLEM"],
            "DOMAIN": ["REQUIREMENTS"],
            "ARCHITECTURE": ["DOMAIN"],
            "VERIFICATION": ["ARCHITECTURE"],
        }
        actual = {
            item["id"]: item.get("depends_on", [])
            for item in profile.get("expectations", [])
        }
        if actual != expected:
            raise CoreError(
                f"unexpected starter profile dependency chain: {actual!r}"
            )
    except Exception as exc:
        errors.append(f"starter profile: {exc}")


def main() -> int:
    errors: list[str] = []

    entries = _validate_surface_registry(errors)
    _validate_artifact_registry_alignment(entries, errors)
    _validate_operation_registry_alignment(
        entries,
        errors,
        registry_path=CONSUMER_OPERATION_REGISTRY,
        expected_kind="harness-consumer-operation-registry",
        surface="consumer",
    )
    _validate_operation_registry_alignment(
        entries,
        errors,
        registry_path=MAINTAINER_OPERATION_REGISTRY,
        expected_kind="harness-maintainer-operation-registry",
        surface="maintainer",
    )
    operation_count, method_count, artifact_count = _validate_skill_contracts(
        entries, errors
    )

    workbench = ROOT / "docs/design/agent-artifact-workbench-v0.md"
    if not workbench.is_file():
        errors.append("missing agent artifact workbench contract")

    _validate_starter_profile(errors)

    if errors:
        print("Harness agent-layer validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    archived_count = sum(
        item.get("lifecycle") == "archived" for item in entries
    )
    unrouted_count = sum(
        item.get("lifecycle") == "active" and item.get("route_status") == "unrouted"
        for item in entries
    )
    print(
        "Harness agent-layer validation passed "
        f"({operation_count} operations, {method_count} methods, "
        f"{artifact_count} artifact producers, {archived_count} archived, "
        f"{unrouted_count} explicitly unrouted)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
