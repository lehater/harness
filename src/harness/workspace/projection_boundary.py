#!/usr/bin/env python3
"""Shared deterministic source-boundary checks for specialized projections."""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from harness.project_model.core import CoreError

MANIFEST_KIND = "harness-human-projection-manifest"
PLAN_KIND = "harness-human-projection-plan"
GENERATED_ROOT = "docs/generated"


def repository_relative_path(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise CoreError(f"{label} is required")
    path = Path(value)
    if path.is_absolute() or ".." in path.parts:
        raise CoreError(f"{label} must be repository-relative: {value}")
    return path.as_posix()


def _manifest_source_index(
    manifest: dict[str, Any],
    *,
    projection_label: str,
) -> dict[str, dict[str, Any]]:
    if manifest.get("version") != 1 or manifest.get("kind") != MANIFEST_KIND:
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
        if not isinstance(artifact, str) or not artifact:
            raise CoreError("human projection source artifact id is required")
        if artifact in result:
            raise CoreError(f"duplicate human projection source: {artifact}")

        repository_relative_path(
            row.get("path"),
            f"canonical source path for {artifact}",
        )

        sha = row.get("sha256")
        if sha is not None and (
            not isinstance(sha, str) or not re.fullmatch(r"[0-9a-f]{64}", sha)
        ):
            raise CoreError(f"canonical source {artifact} sha256 is invalid")

        result[artifact] = row

    return result


def _find_plan_section(
    plan: dict[str, Any],
    *,
    document_id: str,
    section_id: str,
) -> dict[str, Any]:
    if plan.get("version") != 1 or plan.get("kind") != PLAN_KIND:
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


def bind_projection_sources(
    manifest: dict[str, Any],
    plan: dict[str, Any],
    *,
    document_id: str,
    section_id: str,
    renderer: str,
    projection_label: str,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Validate one planned projection's exact canonical source boundary."""
    source_index = _manifest_source_index(
        manifest,
        projection_label=projection_label,
    )
    if plan.get("manifest_digest") != manifest["manifest_digest"]:
        raise CoreError("projection plan manifest digest does not match manifest")

    section = _find_plan_section(
        plan,
        document_id=document_id,
        section_id=section_id,
    )
    if section.get("renderer") != renderer:
        raise CoreError(f"projection section renderer must be {renderer}")

    source_ids = section.get("sources")
    if (
        not isinstance(source_ids, list)
        or not source_ids
        or any(not isinstance(value, str) or not value for value in source_ids)
    ):
        raise CoreError(f"{projection_label} section requires source ids")
    if len(source_ids) != len(set(source_ids)):
        raise CoreError(f"{projection_label} section source ids must be unique")

    outside = sorted(set(source_ids) - set(source_index))
    if outside:
        raise CoreError(
            f"{projection_label} sources are outside manifest: "
            + ", ".join(outside)
        )

    sources: list[dict[str, Any]] = []
    for artifact in source_ids:
        row = source_index[artifact]
        path = repository_relative_path(
            row["path"],
            f"canonical source path for {artifact}",
        )
        if path == GENERATED_ROOT or path.startswith(GENERATED_ROOT + "/"):
            raise CoreError(
                f"{projection_label} forbids generated source artifact "
                f"{artifact}: {path}"
            )
        source = {"artifact": artifact, "path": path}
        if "sha256" in row:
            source["sha256"] = row["sha256"]
        sources.append(source)

    return section, sources
