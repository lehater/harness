#!/usr/bin/env python3
"""Validate statement-level source coverage for reconstruction/blind workflows."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml

from harness import CoreError

ALLOWED = {
    "ADMITTED",
    "EXCLUDED_DERIVED_DESIGN",
    "EXCLUDED_OUT_OF_SCOPE",
    "EXCLUDED_DUPLICATE",
    "QUESTION",
}


def load_yaml(path: str | Path) -> dict[str, Any]:
    value = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise CoreError(f"{path} must contain a mapping")
    return value


def _text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise CoreError(f"{label} must be a non-empty string")
    return value.strip()


def validate_source_coverage(document: dict[str, Any]) -> dict[str, Any]:
    if document.get("version") != 1:
        raise CoreError("source coverage version must be 1")
    if document.get("kind") != "harness-source-coverage":
        raise CoreError("unexpected source coverage kind")
    _text(document.get("id"), "source coverage id")
    _text(document.get("source_baseline"), "source_baseline")

    statements = document.get("statements")
    if not isinstance(statements, list) or not statements:
        raise CoreError("statements must be a non-empty list")

    statement_ids: set[str] = set()
    for item in statements:
        if not isinstance(item, dict):
            raise CoreError("statement must be a mapping")
        sid = _text(item.get("id"), "statement.id")
        if sid in statement_ids:
            raise CoreError(f"duplicate statement id: {sid}")
        statement_ids.add(sid)
        _text(item.get("source_ref"), f"{sid}.source_ref")
        _text(item.get("text"), f"{sid}.text")

    dispositions = document.get("dispositions")
    if not isinstance(dispositions, list):
        raise CoreError("dispositions must be a list")

    seen: set[str] = set()
    questions: list[str] = []
    classifications: dict[str, int] = {}

    for item in dispositions:
        if not isinstance(item, dict):
            raise CoreError("disposition must be a mapping")
        sid = _text(item.get("statement_id"), "disposition.statement_id")
        if sid not in statement_ids:
            raise CoreError(f"disposition references unknown statement: {sid}")
        if sid in seen:
            raise CoreError(f"duplicate disposition for statement: {sid}")
        seen.add(sid)

        classification = _text(item.get("classification"), f"{sid}.classification")
        if classification not in ALLOWED:
            raise CoreError(f"{sid}: unsupported classification {classification}")
        classifications[classification] = classifications.get(classification, 0) + 1

        if classification == "ADMITTED":
            _text(item.get("admitted_ref"), f"{sid}.admitted_ref")
            _text(item.get("sanitized_statement"), f"{sid}.sanitized_statement")
        elif classification == "EXCLUDED_DUPLICATE":
            duplicate_of = _text(item.get("duplicate_of"), f"{sid}.duplicate_of")
            if duplicate_of not in statement_ids or duplicate_of == sid:
                raise CoreError(f"{sid}: duplicate_of must reference another source statement")
            _text(item.get("rationale"), f"{sid}.rationale")
        elif classification == "QUESTION":
            _text(item.get("authority"), f"{sid}.authority")
            _text(item.get("question"), f"{sid}.question")
            questions.append(sid)
        else:
            _text(item.get("rationale"), f"{sid}.rationale")

    missing = sorted(statement_ids - seen)
    if missing:
        raise CoreError(f"source statements without disposition: {missing}")

    expected_status = "COMPLETE" if not questions else "INCOMPLETE"
    actual_status = _text(document.get("coverage_status"), "coverage_status")
    if actual_status not in {"COMPLETE", "INCOMPLETE"}:
        raise CoreError("coverage_status must be COMPLETE or INCOMPLETE")
    if actual_status != expected_status:
        raise CoreError(
            f"coverage_status must be {expected_status} for current dispositions"
        )

    return {
        "valid": True,
        "coverage_status": actual_status,
        "statement_count": len(statement_ids),
        "classification_counts": dict(sorted(classifications.items())),
        "questions": sorted(questions),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Harness source coverage")
    parser.add_argument("command", choices=["validate", "report"])
    parser.add_argument("path")
    args = parser.parse_args()

    result = validate_source_coverage(load_yaml(args.path))
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
