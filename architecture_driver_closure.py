#!/usr/bin/env python3
"""Evaluate architecture-driving requirement closure before SYSTEM-ARCHITECTURE."""
from __future__ import annotations
from typing import Any

BASELINE_CONCERNS = (
    "execution-mode",
    "consumers",
    "load-volume-frequency",
    "latency-freshness",
    "availability",
    "recovery-durability",
    "growth-horizon",
    "deployment-environment",
    "concurrency",
    "integration-boundaries",
    "persistence-history",
    "security-trust-boundary",
)

TERMINAL_STATES = {"RESOLVED", "NOT_APPLICABLE", "DEFERRED"}


def evaluate(document: dict[str, Any]) -> dict[str, Any]:
    errors: list[dict[str, Any]] = []
    if document.get("version") != 1:
        errors.append({"code": "INVALID_VERSION"})
    if document.get("kind") != "harness-architecture-driver-closure":
        errors.append({"code": "INVALID_KIND"})

    rows = document.get("drivers", []) or []
    by_concern: dict[str, dict[str, Any]] = {}
    for row in rows:
        if not isinstance(row, dict):
            errors.append({"code": "INVALID_DRIVER"})
            continue
        concern = row.get("concern")
        if not isinstance(concern, str) or not concern:
            errors.append({"code": "DRIVER_CONCERN_MISSING"})
            continue
        if concern in by_concern:
            errors.append({"code": "DUPLICATE_DRIVER", "concern": concern})
            continue
        by_concern[concern] = row

    for concern in BASELINE_CONCERNS:
        if concern not in by_concern:
            errors.append({"code": "DRIVER_UNCLASSIFIED", "concern": concern})

    for concern, row in by_concern.items():
        state = row.get("state")
        if state not in {"RESOLVED", "NOT_APPLICABLE", "DEFERRED", "QUESTION"}:
            errors.append({"code": "INVALID_DRIVER_STATE", "concern": concern})
            continue
        material = row.get("architecture_impact", "material") == "material"
        rationale = str(row.get("rationale", "")).strip()
        refs = row.get("source_refs", []) or []

        if state == "RESOLVED":
            if row.get("decision") in (None, ""):
                errors.append({"code": "RESOLVED_DECISION_MISSING", "concern": concern})
            if not refs:
                errors.append({"code": "RESOLVED_SOURCE_MISSING", "concern": concern})
        elif state == "NOT_APPLICABLE":
            if not rationale:
                errors.append({"code": "DISPOSITION_RATIONALE_MISSING", "concern": concern})
        elif state == "DEFERRED":
            if not rationale:
                errors.append({"code": "DISPOSITION_RATIONALE_MISSING", "concern": concern})
            if material:
                errors.append({"code": "MATERIAL_DRIVER_DEFERRED", "concern": concern})
        elif state == "QUESTION":
            if not rationale:
                errors.append({"code": "QUESTION_RATIONALE_MISSING", "concern": concern})
            if not row.get("question"):
                errors.append({"code": "QUESTION_ID_MISSING", "concern": concern})
            errors.append({"code": "UNRESOLVED_DRIVER_QUESTION", "concern": concern})

    return {
        "complete": not errors,
        "errors": errors,
        "classified_count": len(by_concern),
        "baseline_count": len(BASELINE_CONCERNS),
    }
