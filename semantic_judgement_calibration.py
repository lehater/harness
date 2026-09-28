#!/usr/bin/env python3
"""Score external semantic-judgement predictions against expert labels."""
from __future__ import annotations

from typing import Any

from harness import CoreError

STATUSES = {"ACCEPTED", "REJECTED"}


def evaluate_judgement_calibration(
    *,
    corpus: dict[str, Any],
    predictions: list[dict[str, Any]],
) -> dict[str, Any]:
    if corpus.get("version") != 1:
        raise CoreError("semantic judgement calibration corpus version must be 1")
    if corpus.get("kind") != "harness-semantic-judgement-calibration-corpus":
        raise CoreError("unexpected semantic judgement calibration corpus kind")

    cases: dict[str, dict[str, Any]] = {}
    for item in corpus.get("cases", []) or []:
        if not isinstance(item, dict):
            raise CoreError("calibration case must be a mapping")
        case_id = item.get("id")
        expected = item.get("expected_status")
        mutation_class = item.get("mutation_class")
        if not isinstance(case_id, str) or not case_id:
            raise CoreError("calibration case id is required")
        if case_id in cases:
            raise CoreError(f"duplicate calibration case: {case_id}")
        if expected not in STATUSES:
            raise CoreError(
                f"calibration case {case_id} has invalid expected_status: {expected}"
            )
        if not isinstance(mutation_class, str) or not mutation_class:
            raise CoreError(
                f"calibration case {case_id} requires mutation_class"
            )
        cases[case_id] = item

    if not cases:
        raise CoreError("semantic judgement calibration corpus requires cases")

    predicted: dict[str, str] = {}
    for item in predictions:
        if not isinstance(item, dict):
            raise CoreError("calibration prediction must be a mapping")
        case_id = item.get("id")
        status = item.get("status")
        if not isinstance(case_id, str) or not case_id:
            raise CoreError("calibration prediction id is required")
        if case_id not in cases:
            raise CoreError(f"unknown calibration prediction case: {case_id}")
        if case_id in predicted:
            raise CoreError(f"duplicate calibration prediction: {case_id}")
        if status not in STATUSES:
            raise CoreError(
                f"calibration prediction {case_id} has invalid status: {status}"
            )
        predicted[case_id] = status

    missing = sorted(set(cases) - set(predicted))
    confusion = {
        "true_positive": 0,
        "true_negative": 0,
        "false_positive": 0,
        "false_negative": 0,
    }
    misses: list[dict[str, Any]] = []
    per_class: dict[str, dict[str, int]] = {}

    for case_id, case in sorted(cases.items()):
        expected = case["expected_status"]
        actual = predicted.get(case_id)
        if actual is None:
            continue

        mutation_class = case["mutation_class"]
        class_counts = per_class.setdefault(
            mutation_class,
            {"total": 0, "correct": 0, "incorrect": 0},
        )
        class_counts["total"] += 1

        if expected == "REJECTED" and actual == "REJECTED":
            confusion["true_positive"] += 1
            class_counts["correct"] += 1
        elif expected == "ACCEPTED" and actual == "ACCEPTED":
            confusion["true_negative"] += 1
            class_counts["correct"] += 1
        elif expected == "ACCEPTED" and actual == "REJECTED":
            confusion["false_positive"] += 1
            class_counts["incorrect"] += 1
            misses.append(
                {
                    "id": case_id,
                    "mutation_class": mutation_class,
                    "expected": expected,
                    "actual": actual,
                    "error": "FALSE_POSITIVE",
                }
            )
        else:
            confusion["false_negative"] += 1
            class_counts["incorrect"] += 1
            misses.append(
                {
                    "id": case_id,
                    "mutation_class": mutation_class,
                    "expected": expected,
                    "actual": actual,
                    "error": "FALSE_NEGATIVE",
                }
            )

    positives = confusion["true_positive"] + confusion["false_negative"]
    negatives = confusion["true_negative"] + confusion["false_positive"]
    scored = positives + negatives
    correct = confusion["true_positive"] + confusion["true_negative"]

    metrics = {
        "detection_recall": (
            confusion["true_positive"] / positives if positives else None
        ),
        "false_positive_rate": (
            confusion["false_positive"] / negatives if negatives else None
        ),
        "accuracy": correct / scored if scored else None,
    }

    if missing:
        status = "INCOMPLETE"
    elif misses:
        status = "FAIL"
    else:
        status = "PASS"

    return {
        "version": 1,
        "kind": "harness-semantic-judgement-calibration-evaluation",
        "corpus_id": corpus.get("id"),
        "status": status,
        "case_count": len(cases),
        "scored_count": scored,
        "missing": missing,
        "confusion": confusion,
        "metrics": metrics,
        "mutation_classes": {
            key: {
                **counts,
                "accuracy": (
                    counts["correct"] / counts["total"]
                    if counts["total"]
                    else None
                ),
            }
            for key, counts in sorted(per_class.items())
        },
        "misses": misses,
    }
