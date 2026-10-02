#!/usr/bin/env python3
"""Deterministic lossless source-boundary coverage above Harness Core."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import yaml

from harness.project_model.core import CoreError


__all__ = [
    "annotations",
    "argparse",
    "hashlib",
    "json",
    "Path",
    "Any",
    "yaml",
    "CoreError",
    "evaluate_source_boundary",
    "load_yaml",
    "main",
]


def _text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise CoreError(f"{label} must be a non-empty string")
    return value.strip()


def _compress_lines(lines: list[int]) -> list[dict[str, int]]:
    if not lines:
        return []
    result: list[dict[str, int]] = []
    start = previous = lines[0]
    for value in lines[1:]:
        if value == previous + 1:
            previous = value
            continue
        result.append({"start_line": start, "end_line": previous})
        start = previous = value
    result.append({"start_line": start, "end_line": previous})
    return result


def evaluate_source_boundary(
    *,
    source: str,
    manifest: dict[str, Any],
) -> dict[str, Any]:
    """Verify that an immutable source is losslessly partitioned into review units.

    The validator intentionally proves only syntactic source coverage. It does
    not decide whether a unit is semantically meaningful or whether statements
    extracted from it are complete.
    """
    if not isinstance(source, str) or not source:
        raise CoreError("source must be a non-empty string")
    if manifest.get("version") != 1:
        raise CoreError("source boundary version must be 1")
    if manifest.get("kind") != "harness-source-boundary":
        raise CoreError("unexpected source boundary kind")

    _text(manifest.get("id"), "source boundary id")
    _text(manifest.get("source_baseline"), "source_baseline")
    expected_sha = _text(manifest.get("source_sha256"), "source_sha256")

    actual_sha = hashlib.sha256(source.encode("utf-8")).hexdigest()
    lines = source.splitlines()
    line_count = len(lines)
    findings: list[dict[str, Any]] = []

    if expected_sha != actual_sha:
        findings.append(
            {
                "code": "SOURCE_BOUNDARY_FINGERPRINT_MISMATCH",
                "expected": expected_sha,
                "actual": actual_sha,
            }
        )

    segments = manifest.get("segments")
    if not isinstance(segments, list) or not segments:
        raise CoreError("segments must be a non-empty list")

    seen_ids: set[str] = set()
    coverage: dict[int, list[str]] = {}

    for item in segments:
        if not isinstance(item, dict):
            raise CoreError("source boundary segment must be a mapping")
        segment_id = _text(item.get("id"), "segment.id")
        if segment_id in seen_ids:
            raise CoreError(f"duplicate source boundary segment id: {segment_id}")
        seen_ids.add(segment_id)

        start = item.get("start_line")
        end = item.get("end_line")
        if (
            not isinstance(start, int)
            or isinstance(start, bool)
            or not isinstance(end, int)
            or isinstance(end, bool)
            or start < 1
            or end < start
            or end > line_count
        ):
            raise CoreError(
                f"{segment_id}: invalid line range {start!r}..{end!r} "
                f"for source with {line_count} lines"
            )

        for line in range(start, end + 1):
            coverage.setdefault(line, []).append(segment_id)

    uncovered = [line for line in range(1, line_count + 1) if line not in coverage]
    overlaps = {
        line: ids for line, ids in coverage.items()
        if len(ids) > 1
    }

    if uncovered:
        findings.append(
            {
                "code": "UNCOVERED_SOURCE_LINES",
                "ranges": _compress_lines(uncovered),
            }
        )
    if overlaps:
        findings.append(
            {
                "code": "OVERLAPPING_SOURCE_SEGMENTS",
                "lines": [
                    {"line": line, "segments": ids}
                    for line, ids in sorted(overlaps.items())
                ],
            }
        )

    accepted = not findings
    return {
        "version": 1,
        "kind": "harness-source-boundary-evaluation",
        "status": "ACCEPTED" if accepted else "REJECTED",
        "source": {
            "sha256": actual_sha,
            "line_count": line_count,
        },
        "segment_count": len(segments),
        "covered_line_count": len(
            [line for line in range(1, line_count + 1) if line in coverage]
        ),
        "findings": findings,
    }


def load_yaml(path: str | Path) -> dict[str, Any]:
    value = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise CoreError(f"{path} must contain a mapping")
    return value


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate lossless source-boundary line coverage"
    )
    parser.add_argument("source")
    parser.add_argument("manifest")
    args = parser.parse_args()

    result = evaluate_source_boundary(
        source=Path(args.source).read_text(encoding="utf-8"),
        manifest=load_yaml(args.manifest),
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "ACCEPTED" else 2


if __name__ == "__main__":
    raise SystemExit(main())
