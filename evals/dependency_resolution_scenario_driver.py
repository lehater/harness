"""Experimental Dependency Resolution calibration Scenario Suite extension.

Loads only by operator-selected --driver-module. No canonical graph writes,
no model calls, and no ability to assert semantic truth from score equality.
"""
from __future__ import annotations

from typing import Any

from harness.application.scenario_drivers import scenario_driver
from evals.dependency_resolution_calibration import validate, score


@scenario_driver("dependency.calibration.validate")
def validate_dependency_calibration(
    *, inputs: dict[str, Any], oracle: dict[str, Any]
) -> dict[str, Any]:
    try:
        return validate(inputs, oracle)
    except (ValueError, TypeError, KeyError) as exc:
        return {"status": "INVALID", "error": str(exc)}


@scenario_driver("dependency.calibration.score")
def score_dependency_calibration(
    *,
    inputs: dict[str, Any],
    oracle: dict[str, Any],
    predictions: dict[str, Any],
) -> dict[str, Any]:
    try:
        return score(inputs, oracle, predictions)
    except (ValueError, TypeError, KeyError) as exc:
        return {"status": "INVALID", "error": str(exc)}
