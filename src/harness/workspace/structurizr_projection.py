#!/usr/bin/env python3
"""Validate one source-bounded C4/Structurizr generated projection."""
from __future__ import annotations

import argparse
import re
import shlex
from pathlib import Path
from typing import Any

import yaml

from harness.project_model.core import CoreError
from harness.workspace.projection_boundary import (
    bind_projection_sources,
    repository_relative_path,
)

PROJECTION_ID = "architecture-c4-structurizr"
PROFILE_KIND = "harness-structurizr-c4-profile"
PROVENANCE_KIND = "harness-generated-projection-provenance"
ALLOWED_VIEW_TYPES = {"systemContext", "container", "component"}
UNSUPPORTED_VIEW_TYPES = {
    "systemLandscape",
    "dynamic",
    "deployment",
    "filtered",
    "custom",
    "image",
}


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
        raise CoreError("Structurizr C4 profile version must be 1")
    if profile.get("kind") != PROFILE_KIND:
        raise CoreError("unexpected Structurizr C4 profile kind")
    if profile.get("projection") != PROJECTION_ID:
        raise CoreError("Structurizr C4 profile projection id mismatch")

    profile_id = profile.get("id")
    if not isinstance(profile_id, str) or not profile_id:
        raise CoreError("Structurizr C4 profile id is required")

    output = profile.get("output")
    if not isinstance(output, dict):
        raise CoreError("Structurizr C4 profile output must be a mapping")
    dsl_path = _repo_relative(output.get("dsl"), "Structurizr DSL output")
    provenance_path = _repo_relative(
        output.get("provenance"),
        "Structurizr provenance output",
    )
    if dsl_path == provenance_path:
        raise CoreError("Structurizr DSL and provenance outputs must differ")
    if not dsl_path.startswith("docs/generated/"):
        raise CoreError("Structurizr DSL output must remain under docs/generated/")
    if not provenance_path.startswith("docs/generated/"):
        raise CoreError(
            "Structurizr provenance output must remain under docs/generated/"
        )

    dsl = profile.get("dsl")
    if not isinstance(dsl, dict):
        raise CoreError("Structurizr C4 profile dsl must be a mapping")
    if dsl.get("identifiers") != "hierarchical":
        raise CoreError("Structurizr C4 profile requires hierarchical identifiers")
    if dsl.get("implied_relationships") is not False:
        raise CoreError("Structurizr C4 profile must disable implied relationships")
    if dsl.get("auto_layout") not in {"tb", "bt", "lr", "rl"}:
        raise CoreError("Structurizr C4 profile auto_layout is invalid")
    if dsl.get("require_explicit_view_keys") is not True:
        raise CoreError("Structurizr C4 profile must require explicit view keys")
    if dsl.get("require_include_wildcard") is not True:
        raise CoreError("Structurizr C4 profile must require include * in C4 views")
    if dsl.get("allow_styles") is not False:
        raise CoreError("Structurizr C4 v1 profile must keep styles disabled")

    allowed_directives = dsl.get("allowed_directives")
    if (
        not isinstance(allowed_directives, list)
        or set(allowed_directives) != {"!identifiers", "!impliedRelationships"}
    ):
        raise CoreError(
            "Structurizr C4 profile allowed_directives must contain only "
            "!identifiers and !impliedRelationships"
        )
    return profile


def _manifest_source_index(manifest: dict[str, Any]) -> dict[str, dict[str, Any]]:
    if (
        manifest.get("version") != 1
        or manifest.get("kind") != "harness-human-projection-manifest"
    ):
        raise CoreError("unexpected human projection manifest")
    digest = manifest.get("manifest_digest")
    if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
        raise CoreError("human projection manifest digest is required")

    sources = manifest.get("sources")
    if not isinstance(sources, list):
        raise CoreError("human projection manifest sources must be a list")
    result: dict[str, dict[str, Any]] = {}
    for row in sources:
        if not isinstance(row, dict):
            raise CoreError("human projection source row must be a mapping")
        artifact = row.get("artifact")
        path = row.get("path")
        if not isinstance(artifact, str) or not artifact:
            raise CoreError("human projection source artifact id is required")
        if artifact in result:
            raise CoreError(f"duplicate human projection source: {artifact}")
        _repo_relative(path, f"canonical source path for {artifact}")
        sha = row.get("sha256")
        if sha is not None and (
            not isinstance(sha, str) or not re.fullmatch(r"[0-9a-f]{64}", sha)
        ):
            raise CoreError(f"canonical source {artifact} sha256 is invalid")
        result[artifact] = row
    return result


def _find_section(
    plan: dict[str, Any],
    *,
    document_id: str,
    section_id: str,
) -> dict[str, Any]:
    if (
        plan.get("version") != 1
        or plan.get("kind") != "harness-human-projection-plan"
    ):
        raise CoreError("unexpected human projection plan")
    documents = plan.get("documents")
    if not isinstance(documents, list):
        raise CoreError("human projection plan documents must be a list")
    document = next(
        (
            item
            for item in documents
            if isinstance(item, dict) and item.get("id") == document_id
        ),
        None,
    )
    if document is None:
        raise CoreError(f"unknown projection document: {document_id}")
    sections = document.get("sections")
    if not isinstance(sections, list):
        raise CoreError(f"projection document {document_id} sections must be a list")
    section = next(
        (
            item
            for item in sections
            if isinstance(item, dict) and item.get("id") == section_id
        ),
        None,
    )
    if section is None:
        raise CoreError(f"unknown projection section: {document_id}/{section_id}")
    return section


def expected_provenance(
    manifest: dict[str, Any],
    plan: dict[str, Any],
    *,
    document_id: str,
    section_id: str,
    profile: dict[str, Any],
) -> dict[str, Any]:
    validate_profile(profile)
    source_index = _manifest_source_index(manifest)
    if plan.get("manifest_digest") != manifest["manifest_digest"]:
        raise CoreError("projection plan manifest digest does not match manifest")

    section = _find_section(
        plan,
        document_id=document_id,
        section_id=section_id,
    )
    if section.get("renderer") != PROJECTION_ID:
        raise CoreError(f"projection section renderer must be {PROJECTION_ID}")
    source_ids = section.get("sources")
    if (
        not isinstance(source_ids, list)
        or not source_ids
        or any(not isinstance(value, str) or not value for value in source_ids)
    ):
        raise CoreError("Structurizr projection section requires source ids")
    if len(source_ids) != len(set(source_ids)):
        raise CoreError("Structurizr projection section source ids must be unique")
    outside = sorted(set(source_ids) - set(source_index))
    if outside:
        raise CoreError(
            "Structurizr projection sources are outside manifest: "
            + ", ".join(outside)
        )

    sources: list[dict[str, Any]] = []
    for artifact in source_ids:
        row = source_index[artifact]
        source = {"artifact": artifact, "path": row["path"]}
        if "sha256" in row:
            source["sha256"] = row["sha256"]
        sources.append(source)

    return {
        "version": 1,
        "kind": PROVENANCE_KIND,
        "projection": PROJECTION_ID,
        "profile": profile["id"],
        "manifest_digest": manifest["manifest_digest"],
        "document": document_id,
        "section": section_id,
        "sources": sources,
        "outputs": [
            profile["output"]["dsl"],
            profile["output"]["provenance"],
        ],
    }


def _brace_delta(line: str) -> int:
    delta = 0
    quoted = False
    escaped = False
    for char in line:
        if escaped:
            escaped = False
            continue
        if char == "\\" and quoted:
            escaped = True
            continue
        if char == '"':
            quoted = not quoted
            continue
        if quoted:
            continue
        if char == "{":
            delta += 1
        elif char == "}":
            delta -= 1
    return delta


def _validate_balanced_braces(text: str) -> None:
    depth = 0
    for number, line in enumerate(text.splitlines(), start=1):
        depth += _brace_delta(line)
        if depth < 0:
            raise CoreError(
                f"Structurizr DSL closes a block before it opens at line {number}"
            )
    if depth != 0:
        raise CoreError("Structurizr DSL braces are not balanced")


def _extract_block(text: str, keyword: str) -> str:
    match = re.search(rf"(?m)^\s*{re.escape(keyword)}\b[^{{]*\{{", text)
    if match is None:
        raise CoreError(f"Structurizr DSL requires {keyword} block")
    open_pos = text.find("{", match.start())
    depth = 0
    quoted = False
    escaped = False
    for index in range(open_pos, len(text)):
        char = text[index]
        if escaped:
            escaped = False
            continue
        if char == "\\" and quoted:
            escaped = True
            continue
        if char == '"':
            quoted = not quoted
            continue
        if quoted:
            continue
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return text[open_pos + 1:index]
    raise CoreError(f"Structurizr DSL {keyword} block is not closed")


def _model_has(model: str, element_type: str) -> bool:
    return bool(
        re.search(
            rf"(?m)^\s*(?:[A-Za-z_][A-Za-z0-9_]*\s*=\s*)?{element_type}\b",
            model,
        )
    )


def _view_rows(views: str, profile: dict[str, Any]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    seen_keys: set[str] = set()
    depth = 0
    current: dict[str, Any] | None = None
    layout = profile["dsl"]["auto_layout"]

    for number, line in enumerate(views.splitlines(), start=1):
        stripped = line.strip()
        if depth == 0 and stripped:
            first = stripped.split(maxsplit=1)[0]
            if first in UNSUPPORTED_VIEW_TYPES:
                raise CoreError(f"Structurizr C4 v1 does not support {first} view")
            if first == "styles" and profile["dsl"]["allow_styles"] is False:
                raise CoreError("Structurizr C4 v1 does not allow local styles")
            if first in ALLOWED_VIEW_TYPES:
                if "{" not in stripped:
                    raise CoreError(
                        f"Structurizr view header must open its block on line {number}"
                    )
                header = stripped.split("{", 1)[0].strip()
                try:
                    tokens = shlex.split(header)
                except ValueError as exc:
                    raise CoreError(
                        f"cannot parse Structurizr view header on line {number}: {exc}"
                    ) from exc
                if len(tokens) < 3:
                    raise CoreError(
                        f"Structurizr {first} view requires explicit scope and key"
                    )
                key = tokens[2]
                if key in seen_keys:
                    raise CoreError(f"duplicate Structurizr view key: {key}")
                seen_keys.add(key)
                current = {
                    "type": first,
                    "key": key,
                    "auto_layout": False,
                    "include": False,
                }

        if current is not None:
            if re.match(r"^\s*include\s+\*\s*$", line):
                current["include"] = True
            auto = re.match(r"^\s*autoLayout(?:\s+(tb|bt|lr|rl))?\s*$", line)
            if auto:
                direction = auto.group(1) or "tb"
                if direction != layout:
                    raise CoreError(
                        f"Structurizr view {current['key']} autoLayout must be {layout}"
                    )
                current["auto_layout"] = True

        depth += _brace_delta(line)
        if depth < 0:
            raise CoreError(
                f"Structurizr views block closes unexpectedly at line {number}"
            )
        if current is not None and depth == 0:
            if not current["auto_layout"]:
                raise CoreError(
                    f"Structurizr view {current['key']} requires autoLayout {layout}"
                )
            if not current["include"]:
                raise CoreError(
                    f"Structurizr view {current['key']} requires include *"
                )
            rows.append({"type": current["type"], "key": current["key"]})
            current = None

    if depth != 0:
        raise CoreError("Structurizr views block is not balanced")
    return rows


def validate_dsl(text: str, profile: dict[str, Any]) -> None:
    validate_profile(profile)
    if not isinstance(text, str) or not text.strip():
        raise CoreError("Structurizr DSL content is required")
    if re.search(r"(?mi)^\s*workspace\s+extends\b", text):
        raise CoreError("Structurizr C4 v1 forbids workspace extension")

    allowed_directives = set(profile["dsl"]["allowed_directives"])
    for directive in re.findall(r"(?m)^\s*(![A-Za-z][A-Za-z0-9]*)\b", text):
        if directive not in allowed_directives:
            raise CoreError(f"Structurizr C4 v1 forbids directive {directive}")

    if not re.search(r"(?m)^\s*!identifiers\s+hierarchical\s*$", text):
        raise CoreError("Structurizr DSL requires !identifiers hierarchical")
    if not re.search(r"(?m)^\s*!impliedRelationships\s+false\s*$", text):
        raise CoreError("Structurizr DSL requires !impliedRelationships false")

    _validate_balanced_braces(text)
    if not re.search(r"(?m)^\s*workspace\b[^\{]*\{", text):
        raise CoreError("Structurizr DSL requires workspace block")

    model = _extract_block(text, "model")
    views = _extract_block(text, "views")
    if not _model_has(model, "softwareSystem"):
        raise CoreError("Structurizr C4 projection requires a softwareSystem")

    rows = _view_rows(views, profile)
    types = [row["type"] for row in rows]
    if "systemContext" not in types:
        raise CoreError("Structurizr C4 projection requires a systemContext view")
    if _model_has(model, "container") and "container" not in types:
        raise CoreError(
            "Structurizr C4 projection with containers requires a container view"
        )
    if _model_has(model, "component") and "component" not in types:
        raise CoreError(
            "Structurizr C4 projection with components requires a component view"
        )


def validate_generated_projection(
    manifest: dict[str, Any],
    plan: dict[str, Any],
    *,
    document_id: str,
    section_id: str,
    profile: dict[str, Any],
    dsl_text: str,
    provenance: dict[str, Any],
) -> None:
    expected = expected_provenance(
        manifest,
        plan,
        document_id=document_id,
        section_id=section_id,
        profile=profile,
    )
    if provenance != expected:
        raise CoreError(
            "Structurizr projection provenance does not match current manifest/plan"
        )
    validate_dsl(dsl_text, profile)


def _write_yaml(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(value, sort_keys=False), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate one Harness C4/Structurizr generated projection"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    for name in ("provenance", "validate"):
        command = sub.add_parser(name)
        command.add_argument("--manifest", required=True)
        command.add_argument("--plan", required=True)
        command.add_argument("--document", required=True)
        command.add_argument("--section", required=True)
        command.add_argument("--profile", required=True)
        if name == "provenance":
            command.add_argument("--output")
        else:
            command.add_argument("--dsl", required=True)
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
            profile=profile,
        )
        if args.output:
            _write_yaml(Path(args.output), provenance)
        else:
            print(yaml.safe_dump(provenance, sort_keys=False), end="")
        return 0

    provenance = load_yaml(args.provenance)
    dsl_text = Path(args.dsl).read_text(encoding="utf-8")
    validate_generated_projection(
        manifest,
        plan,
        document_id=args.document,
        section_id=args.section,
        profile=profile,
        dsl_text=dsl_text,
        provenance=provenance,
    )
    print("Structurizr C4 projection valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
