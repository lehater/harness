#!/usr/bin/env python3
"""Acceptance checks for source_coverage.py."""
from __future__ import annotations

import copy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from harness import CoreError  # noqa: E402
from source_coverage import validate_source_coverage  # noqa: E402


def base() -> dict:
    return {
        "version": 1,
        "kind": "harness-source-coverage",
        "id": "SOURCE-COVERAGE-ACCEPTANCE",
        "source_baseline": "repo@example",
        "coverage_status": "COMPLETE",
        "statements": [
            {
                "id": "S1",
                "source_ref": "requirements.md#one",
                "text": "Request authority is scoped.",
            },
            {
                "id": "S2",
                "source_ref": "requirements.md#two",
                "text": "HTTP is a prior design choice.",
            },
        ],
        "dispositions": [
            {
                "statement_id": "S1",
                "classification": "ADMITTED",
                "admitted_ref": "source-corpus.yaml#authority",
                "sanitized_statement": "Request authority is scoped.",
            },
            {
                "statement_id": "S2",
                "classification": "EXCLUDED_DERIVED_DESIGN",
                "rationale": "Representation choice, not product behavior.",
            },
        ],
    }


def must_fail(document: dict, marker: str, errors: list[str]) -> None:
    try:
        validate_source_coverage(document)
        errors.append(f"{marker}: expected failure")
    except CoreError:
        pass


def main() -> int:
    errors: list[str] = []
    try:
        result = validate_source_coverage(base())
        assert result["coverage_status"] == "COMPLETE", result
        assert result["statement_count"] == 2, result
    except Exception as exc:
        errors.append(f"valid fixture: {exc}")

    missing = base()
    missing["dispositions"] = missing["dispositions"][:1]
    must_fail(missing, "silent source loss", errors)

    duplicate = base()
    duplicate["dispositions"].append(copy.deepcopy(duplicate["dispositions"][0]))
    must_fail(duplicate, "duplicate disposition", errors)

    question = base()
    question["dispositions"][0] = {
        "statement_id": "S1",
        "classification": "QUESTION",
        "authority": "PRODUCT-REQUIREMENTS",
        "question": "Is authority scope source-level?",
    }
    must_fail(question, "question cannot claim COMPLETE", errors)
    question["coverage_status"] = "INCOMPLETE"
    try:
        result = validate_source_coverage(question)
        assert result["questions"] == ["S1"], result
    except Exception as exc:
        errors.append(f"incomplete fixture: {exc}")

    if errors:
        print("Harness source coverage validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print("Harness source coverage validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
