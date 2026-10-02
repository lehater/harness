#!/usr/bin/env python3
"""Build, validate and locally synchronize the versioned Harness Consumer Pack."""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any

import yaml

__all__ = ['Any',
 'ConsumerPackError',
 'DEFAULT_DEFINITION',
 'DEFAULT_SURFACE_REGISTRY',
 'PACK_MANIFEST',
 'Path',
 'REVISION_RE',
 'annotations',
 'argparse',
 'ast',
 'hashlib',
 'json',
 'load_yaml',
 'main',
 'materialize_pack',
 're',
 'shutil',
 'subprocess',
 'sync_binding',
 'tempfile',
 'validate_binding',
 'validate_definition',
 'validate_pack',
 'yaml']

REVISION_RE = re.compile(r"^[0-9a-fA-F]{40}$")
PACK_MANIFEST = "harness-consumer-pack.yaml"
DEFAULT_DEFINITION = "spec/distribution/consumer-pack-v0.yaml"
DEFAULT_SURFACE_REGISTRY = "skills/skill-surface-registry-v0.yaml"


class ConsumerPackError(ValueError):
    pass


def load_yaml(path: str | Path) -> dict[str, Any]:
    path = Path(path)
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise ConsumerPackError(f"cannot load {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ConsumerPackError(f"{path} must contain a mapping")
    return value


def _write_yaml(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        yaml.safe_dump(value, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_binding(binding: dict[str, Any]) -> None:
    if binding.get("version") != 1:
        raise ConsumerPackError("consumer binding version must be 1")
    if binding.get("kind") != "harness-consumer-binding":
        raise ConsumerPackError("unexpected consumer binding kind")
    if binding.get("consumer_api") != "v0":
        raise ConsumerPackError("unsupported consumer_api; expected v0")
    source = binding.get("source")
    if not isinstance(source, dict):
        raise ConsumerPackError("consumer binding source must be a mapping")
    if set(source) != {"repository", "revision"}:
        raise ConsumerPackError(
            "consumer binding source must contain exactly repository and revision"
        )
    repository = source["repository"]
    revision = source["revision"]
    if not isinstance(repository, str) or not repository.strip():
        raise ConsumerPackError("consumer binding repository is required")
    if not isinstance(revision, str) or not REVISION_RE.fullmatch(revision):
        raise ConsumerPackError(
            "consumer binding revision must be an immutable 40-hex commit"
        )


def validate_definition(definition: dict[str, Any], source_root: Path) -> None:
    if definition.get("version") != 1:
        raise ConsumerPackError("consumer pack definition version must be 1")
    if definition.get("kind") != "harness-consumer-pack-definition":
        raise ConsumerPackError("unexpected consumer pack definition kind")
    if definition.get("consumer_api") != "v0":
        raise ConsumerPackError("consumer pack definition consumer_api must be v0")

    entry = definition.get("entry")
    if not isinstance(entry, dict):
        raise ConsumerPackError("consumer pack entry must be a mapping")
    required_entry = {
        "surface_registry",
        "operation_registry",
        "method_registry",
        "artifact_registry",
    }
    if set(entry) != required_entry:
        raise ConsumerPackError(
            "consumer pack entry must contain exactly "
            + ", ".join(sorted(required_entry))
        )

    for key in ("root_files", "include_prefixes", "exact_files", "forbidden_prefixes"):
        values = definition.get(key)
        if not isinstance(values, list) or not all(
            isinstance(value, str) and value for value in values
        ):
            raise ConsumerPackError(f"{key} must be a string list")

    generated = definition.get("generated_files")
    if not isinstance(generated, dict) or set(generated) != {
        "surface_registry",
        "pack_manifest",
    }:
        raise ConsumerPackError(
            "generated_files must contain surface_registry and pack_manifest"
        )
    if generated["pack_manifest"] != PACK_MANIFEST:
        raise ConsumerPackError(
            f"generated pack_manifest must be {PACK_MANIFEST}"
        )

    for relative in definition["root_files"] + definition["exact_files"]:
        if not (source_root / relative).is_file():
            raise ConsumerPackError(f"consumer pack source file missing: {relative}")

    for prefix in definition["include_prefixes"]:
        if not (source_root / prefix).exists():
            raise ConsumerPackError(f"consumer pack source prefix missing: {prefix}")

    _validate_runtime_import_closure(definition, source_root)


def _validate_runtime_import_closure(
    definition: dict[str, Any], source_root: Path
) -> None:
    source_root_modules = {
        path.stem
        for path in source_root.glob("*.py")
        if path.is_file()
    }
    included_root_modules = {
        Path(relative).stem
        for relative in definition["root_files"]
        if relative.endswith(".py")
    }

    for relative in definition["root_files"]:
        if not relative.endswith(".py"):
            continue
        path = source_root / relative
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=relative)
        except SyntaxError as exc:
            raise ConsumerPackError(f"cannot parse runtime module {relative}: {exc}") from exc
        imported: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.update(alias.name.split(".", 1)[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module.split(".", 1)[0])
        missing = sorted(
            (imported & source_root_modules) - included_root_modules
        )
        if missing:
            raise ConsumerPackError(
                f"{relative} imports Harness root modules missing from Consumer Pack: "
                + ", ".join(missing)
            )


def _is_forbidden(relative: str, definition: dict[str, Any]) -> bool:
    return any(relative.startswith(prefix) for prefix in definition["forbidden_prefixes"])


def _active_consumer_entries(source_root: Path) -> list[dict[str, Any]]:
    registry = load_yaml(source_root / DEFAULT_SURFACE_REGISTRY)
    if registry.get("kind") != "harness-skill-surface-registry":
        raise ConsumerPackError("unexpected source skill-surface registry kind")
    entries = registry.get("skills")
    if not isinstance(entries, list):
        raise ConsumerPackError("source skill-surface registry skills must be a list")

    result: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for item in entries:
        if not isinstance(item, dict):
            raise ConsumerPackError("source skill-surface entry must be a mapping")
        if not (
            item.get("surface") == "consumer"
            and item.get("lifecycle") == "active"
            and item.get("route_status") == "routed"
        ):
            continue
        skill_id = item.get("id")
        path = item.get("path")
        if not isinstance(skill_id, str) or not skill_id:
            raise ConsumerPackError("distributed skill id is required")
        if skill_id in seen_ids:
            raise ConsumerPackError(f"duplicate distributed skill id: {skill_id}")
        seen_ids.add(skill_id)
        if not isinstance(path, str) or not path.endswith("/SKILL.md"):
            raise ConsumerPackError(
                f"{skill_id}: distributed skill must reference SKILL.md"
            )
        if not (source_root / path).is_file():
            raise ConsumerPackError(f"{skill_id}: distributed skill missing: {path}")
        result.append(dict(item))
    result.sort(key=lambda item: item["id"])
    return result


def _selected_source_files(
    source_root: Path, definition: dict[str, Any]
) -> set[str]:
    selected: set[str] = set(definition["root_files"])
    selected.update(definition["exact_files"])

    for prefix in definition["include_prefixes"]:
        base = source_root / prefix
        if base.is_file():
            selected.add(prefix)
            continue
        for path in base.rglob("*"):
            if path.is_file():
                selected.add(path.relative_to(source_root).as_posix())

    for item in _active_consumer_entries(source_root):
        selected.add(item["path"])

    generated_surface = definition["generated_files"]["surface_registry"]
    selected.discard(generated_surface)

    forbidden = sorted(path for path in selected if _is_forbidden(path, definition))
    if forbidden:
        raise ConsumerPackError(
            "consumer pack definition selected forbidden paths: "
            + ", ".join(forbidden)
        )

    missing = sorted(path for path in selected if not (source_root / path).is_file())
    if missing:
        raise ConsumerPackError(
            "consumer pack selected missing source files: " + ", ".join(missing)
        )
    return selected


def _filtered_surface_registry(source_root: Path) -> dict[str, Any]:
    return {
        "version": 1,
        "kind": "harness-skill-surface-registry",
        "id": "SKILL-SURFACES-CONSUMER-V0",
        "status": "distributed",
        "skills": _active_consumer_entries(source_root),
    }


def _registry_skill_paths(pack_root: Path, relative: str) -> set[str]:
    value = load_yaml(pack_root / relative)
    routes = value.get("routes")
    if not isinstance(routes, list):
        raise ConsumerPackError(f"{relative}: routes must be a list")
    result: set[str] = set()
    for route in routes:
        if not isinstance(route, dict):
            raise ConsumerPackError(f"{relative}: route must be a mapping")
        skill = route.get("skill")
        if not isinstance(skill, str) or not skill:
            raise ConsumerPackError(f"{relative}: route skill is required")
        result.add(skill)
    return result


def validate_pack(
    pack_root: str | Path,
    *,
    expected_revision: str | None = None,
    expected_api: str = "v0",
) -> dict[str, Any]:
    pack_root = Path(pack_root)
    manifest = load_yaml(pack_root / PACK_MANIFEST)
    if manifest.get("version") != 1:
        raise ConsumerPackError("consumer pack manifest version must be 1")
    if manifest.get("kind") != "harness-consumer-pack":
        raise ConsumerPackError("unexpected consumer pack manifest kind")
    if manifest.get("consumer_api") != expected_api:
        raise ConsumerPackError(
            f"consumer pack API mismatch: expected {expected_api}, "
            f"got {manifest.get('consumer_api')!r}"
        )
    if expected_revision is not None and manifest.get("binding_revision") != expected_revision:
        raise ConsumerPackError(
            "consumer pack binding revision does not match requested revision"
        )

    definition = manifest.get("definition")
    if not isinstance(definition, str) or not definition:
        raise ConsumerPackError("consumer pack definition identity is required")
    entry = manifest.get("entry")
    if not isinstance(entry, dict):
        raise ConsumerPackError("consumer pack entry must be a mapping")

    file_rows = manifest.get("files")
    if not isinstance(file_rows, list):
        raise ConsumerPackError("consumer pack files must be a list")
    expected_files: set[str] = set()
    for row in file_rows:
        if not isinstance(row, dict) or set(row) != {"path", "sha256"}:
            raise ConsumerPackError("consumer pack file row must contain path and sha256")
        relative = row["path"]
        digest = row["sha256"]
        if not isinstance(relative, str) or not relative:
            raise ConsumerPackError("consumer pack file path is required")
        if relative in expected_files:
            raise ConsumerPackError(f"duplicate consumer pack file: {relative}")
        expected_files.add(relative)
        path = pack_root / relative
        if not path.is_file():
            raise ConsumerPackError(f"consumer pack file missing: {relative}")
        if _sha256(path) != digest:
            raise ConsumerPackError(f"consumer pack hash mismatch: {relative}")

    actual_files = {
        path.relative_to(pack_root).as_posix()
        for path in pack_root.rglob("*")
        if path.is_file() and path.name != PACK_MANIFEST
    }
    if actual_files != expected_files:
        raise ConsumerPackError(
            "consumer pack manifest/file set mismatch "
            f"(missing={sorted(expected_files - actual_files)!r}, "
            f"untracked={sorted(actual_files - expected_files)!r})"
        )

    surface_path = entry.get("surface_registry")
    if not isinstance(surface_path, str):
        raise ConsumerPackError("consumer pack surface_registry entry is required")
    surface = load_yaml(pack_root / surface_path)
    skills = surface.get("skills")
    if not isinstance(skills, list):
        raise ConsumerPackError("distributed surface registry skills must be a list")
    distributed_skill_paths: set[str] = set()
    for item in skills:
        if not isinstance(item, dict):
            raise ConsumerPackError("distributed surface entry must be a mapping")
        if item.get("surface") != "consumer":
            raise ConsumerPackError("Consumer Pack contains non-consumer skill")
        if item.get("lifecycle") != "active":
            raise ConsumerPackError("Consumer Pack contains non-active skill")
        if item.get("route_status") != "routed":
            raise ConsumerPackError("Consumer Pack contains unrouted skill")
        path = item.get("path")
        if not isinstance(path, str) or not (pack_root / path).is_file():
            raise ConsumerPackError(
                f"distributed skill path missing: {path!r}"
            )
        distributed_skill_paths.add(path)

    routed_paths: set[str] = set()
    for key in ("operation_registry", "method_registry", "artifact_registry"):
        relative = entry.get(key)
        if not isinstance(relative, str):
            raise ConsumerPackError(f"consumer pack {key} entry is required")
        routed_paths.update(_registry_skill_paths(pack_root, relative))

    if routed_paths != distributed_skill_paths:
        raise ConsumerPackError(
            "Consumer Pack surface and route registries disagree "
            f"(surface_only={sorted(distributed_skill_paths-routed_paths)!r}, "
            f"route_only={sorted(routed_paths-distributed_skill_paths)!r})"
        )

    forbidden_prefixes = manifest.get("forbidden_prefixes")
    if not isinstance(forbidden_prefixes, list):
        raise ConsumerPackError("consumer pack forbidden_prefixes must be a list")
    leaked = sorted(
        relative
        for relative in actual_files
        if any(relative.startswith(prefix) for prefix in forbidden_prefixes)
    )
    if leaked:
        raise ConsumerPackError(
            "Consumer Pack contains forbidden Maintainer/internal paths: "
            + ", ".join(leaked)
        )
    return manifest


def materialize_pack(
    source_root: str | Path,
    output_root: str | Path,
    *,
    binding_revision: str,
    effective_revision: str | None = None,
) -> dict[str, Any]:
    source_root = Path(source_root).resolve()
    output_root = Path(output_root).resolve()
    if not REVISION_RE.fullmatch(binding_revision):
        raise ConsumerPackError("binding_revision must be a 40-hex commit")

    definition_path = source_root / DEFAULT_DEFINITION
    definition = load_yaml(definition_path)
    validate_definition(definition, source_root)
    selected = _selected_source_files(source_root, definition)

    if output_root.exists():
        shutil.rmtree(output_root)
    output_root.mkdir(parents=True)

    for relative in sorted(selected):
        target = output_root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((source_root / relative).read_bytes())

    surface_relative = definition["generated_files"]["surface_registry"]
    _write_yaml(
        output_root / surface_relative,
        _filtered_surface_registry(source_root),
    )

    actual_effective = effective_revision or binding_revision
    if not isinstance(actual_effective, str) or not actual_effective:
        raise ConsumerPackError("effective_revision is required")

    entry = dict(definition["entry"])
    files = sorted(
        (
            {
                "path": path.relative_to(output_root).as_posix(),
                "sha256": _sha256(path),
            }
            for path in output_root.rglob("*")
            if path.is_file()
        ),
        key=lambda row: row["path"],
    )
    manifest = {
        "version": 1,
        "kind": "harness-consumer-pack",
        "consumer_api": definition["consumer_api"],
        "definition": definition["id"],
        "binding_revision": binding_revision,
        "effective_revision": actual_effective,
        "entry": entry,
        "forbidden_prefixes": list(definition["forbidden_prefixes"]),
        "files": files,
    }
    _write_yaml(output_root / PACK_MANIFEST, manifest)
    return validate_pack(
        output_root,
        expected_revision=binding_revision,
        expected_api=definition["consumer_api"],
    )


def _git_revision(path: Path) -> str | None:
    try:
        result = subprocess.run(
            ["git", "-C", str(path), "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    revision = result.stdout.strip()
    return revision if REVISION_RE.fullmatch(revision) else None


def sync_binding(
    binding_path: str | Path,
    cache_root: str | Path,
    *,
    dev_source: str | Path | None = None,
) -> Path:
    binding = load_yaml(binding_path)
    validate_binding(binding)
    cache_root = Path(cache_root).resolve()
    source = binding["source"]
    revision = source["revision"]
    consumer_api = binding["consumer_api"]

    if dev_source is not None:
        dev_source = Path(dev_source).resolve()
        identity = hashlib.sha256(str(dev_source).encode("utf-8")).hexdigest()[:16]
        output = cache_root / consumer_api / f"dev-{identity}"
        effective = _git_revision(dev_source) or "working-tree"
        materialize_pack(
            dev_source,
            output,
            binding_revision=revision,
            effective_revision=effective,
        )
        return output

    output = cache_root / consumer_api / revision
    if output.is_dir():
        try:
            validate_pack(
                output,
                expected_revision=revision,
                expected_api=consumer_api,
            )
            return output
        except ConsumerPackError:
            shutil.rmtree(output)

    cache_root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="harness-consumer-source-") as temp:
        checkout = Path(temp) / "source"
        subprocess.run(
            ["git", "init", str(checkout)],
            check=True,
            capture_output=True,
            text=True,
        )
        subprocess.run(
            ["git", "-C", str(checkout), "remote", "add", "origin", source["repository"]],
            check=True,
            capture_output=True,
            text=True,
        )
        subprocess.run(
            ["git", "-C", str(checkout), "fetch", "--depth=1", "origin", revision],
            check=True,
            capture_output=True,
            text=True,
        )
        subprocess.run(
            ["git", "-C", str(checkout), "checkout", "--detach", "FETCH_HEAD"],
            check=True,
            capture_output=True,
            text=True,
        )
        actual = _git_revision(checkout)
        if actual != revision:
            raise ConsumerPackError(
                f"resolved Harness revision {actual!r} does not match binding {revision}"
            )
        materialize_pack(
            checkout,
            output,
            binding_revision=revision,
            effective_revision=actual,
        )
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description="Harness Consumer Pack tooling")
    sub = parser.add_subparsers(dest="command", required=True)

    validate_def = sub.add_parser("validate-definition")
    validate_def.add_argument("--source-root", default=".")

    materialize = sub.add_parser("materialize")
    materialize.add_argument("source_root")
    materialize.add_argument("output_root")
    materialize.add_argument("--revision", required=True)

    validate = sub.add_parser("validate-pack")
    validate.add_argument("pack_root")
    validate.add_argument("--revision")

    validate_binding_parser = sub.add_parser("validate-binding")
    validate_binding_parser.add_argument("binding")

    sync = sub.add_parser("sync")
    sync.add_argument("binding")
    sync.add_argument("cache_root")
    sync.add_argument("--dev-source")

    args = parser.parse_args()

    if args.command == "validate-definition":
        source_root = Path(args.source_root).resolve()
        definition = load_yaml(source_root / DEFAULT_DEFINITION)
        validate_definition(definition, source_root)
        print(json.dumps({"status": "VALID", "consumer_api": definition["consumer_api"]}))
        return 0
    if args.command == "materialize":
        manifest = materialize_pack(
            args.source_root,
            args.output_root,
            binding_revision=args.revision,
        )
        print(yaml.safe_dump(manifest, sort_keys=False), end="")
        return 0
    if args.command == "validate-pack":
        manifest = validate_pack(
            args.pack_root,
            expected_revision=args.revision,
        )
        print(json.dumps({"status": "VALID", "consumer_api": manifest["consumer_api"]}))
        return 0
    if args.command == "validate-binding":
        binding = load_yaml(args.binding)
        validate_binding(binding)
        print(json.dumps({"status": "VALID", "consumer_api": binding["consumer_api"]}))
        return 0
    if args.command == "sync":
        output = sync_binding(
            args.binding,
            args.cache_root,
            dev_source=args.dev_source,
        )
        print(output)
        return 0
    raise AssertionError(args.command)


if __name__ == "__main__":
    raise SystemExit(main())
