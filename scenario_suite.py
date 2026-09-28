#!/usr/bin/env python3
"""Universal executable scenario suite for Harness behavior."""
from __future__ import annotations

import argparse
import copy
import importlib
import json
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from harness import CoreError
from scenario_drivers import get_driver


class ScenarioError(CoreError):
    pass


_MISSING = object()
_NO_DEFAULT = object()


@dataclass
class ScenarioResult:
    id: str
    path: str
    status: str
    covers: list[str]
    dimensions: dict[str, str]
    steps: list[dict[str, Any]]
    error: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "path": self.path,
            "status": self.status,
            "covers": self.covers,
            "dimensions": self.dimensions,
            "steps": self.steps,
            **({"error": self.error} if self.error else {}),
        }


def _load_yaml(path: Path) -> Any:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _load_fixture(
    spec: Any,
    scenario_dir: Path,
    temp_root: Path,
    fixture_id: str,
) -> Any:
    if not isinstance(spec, dict) or not any(
        key in spec for key in ("value", "yaml", "json", "text", "path", "workspace")
    ):
        return copy.deepcopy(spec)
    if "value" in spec:
        return copy.deepcopy(spec["value"])
    for kind in ("yaml", "json", "text", "path", "workspace"):
        if kind not in spec:
            continue
        source = (scenario_dir / str(spec[kind])).resolve()
        if kind == "yaml":
            return _load_yaml(source)
        if kind == "json":
            return json.loads(source.read_text(encoding="utf-8"))
        if kind == "text":
            return source.read_text(encoding="utf-8")
        if kind == "path":
            return str(source)
        target = temp_root / fixture_id
        shutil.copytree(source, target)
        return str(target)
    raise ScenarioError(f"invalid fixture {fixture_id}")


def _pointer(value: Any, pointer: str, default: Any = _NO_DEFAULT) -> Any:
    if pointer in ("", "/"):
        return value
    if not pointer.startswith("/"):
        raise ScenarioError(f"assertion path must be JSON Pointer: {pointer}")
    current = value
    try:
        for raw in pointer[1:].split("/"):
            token = raw.replace("~1", "/").replace("~0", "~")
            if isinstance(current, list):
                current = current[int(token)]
            elif isinstance(current, dict):
                current = current[token]
            else:
                raise KeyError(token)
        return current
    except (KeyError, IndexError, ValueError, TypeError):
        if default is not _NO_DEFAULT:
            return default
        raise ScenarioError(f"assertion path not found: {pointer}")


def _resolve_reference(ref: str, fixtures: dict[str, Any], steps: dict[str, Any]) -> Any:
    pointer = ""
    if "#" in ref:
        ref, pointer = ref.split("#", 1)
    if ref.startswith("fixture."):
        name = ref[len("fixture."):]
        if name not in fixtures:
            raise ScenarioError(f"unknown fixture reference: {ref}")
        value = fixtures[name]
    elif ref.startswith("step."):
        name = ref[len("step."):]
        if name not in steps:
            raise ScenarioError(f"unknown step reference: {ref}")
        value = steps[name]
    else:
        raise ScenarioError(f"unsupported reference: {ref}")
    return copy.deepcopy(_pointer(value, pointer)) if pointer else copy.deepcopy(value)


def _resolve(value: Any, fixtures: dict[str, Any], steps: dict[str, Any]) -> Any:
    if isinstance(value, dict):
        if set(value) == {"ref"} and isinstance(value["ref"], str):
            return _resolve_reference(value["ref"], fixtures, steps)
        return {k: _resolve(v, fixtures, steps) for k, v in value.items()}
    if isinstance(value, list):
        return [_resolve(v, fixtures, steps) for v in value]
    return copy.deepcopy(value)


def _matches_subset(actual: Any, expected: Any) -> bool:
    if isinstance(expected, dict):
        return (
            isinstance(actual, dict)
            and all(
                key in actual and _matches_subset(actual[key], value)
                for key, value in expected.items()
            )
        )
    if isinstance(expected, list):
        return actual == expected
    return actual == expected


def _assertion(
    output: Any,
    spec: dict[str, Any],
    fixtures: dict[str, Any],
    steps: dict[str, Any],
) -> None:
    op = spec.get("op", "equals")
    path = spec.get("path", "")
    if op == "not_exists":
        actual = _pointer(output, path, _MISSING)
        if actual is not _MISSING:
            raise ScenarioError(f"{path}: expected path to be absent")
        return

    actual = _pointer(output, path, _MISSING)
    if op == "exists":
        if actual is _MISSING:
            raise ScenarioError(f"{path}: expected path to exist")
        return
    if actual is _MISSING:
        raise ScenarioError(f"{path}: path absent")

    expected = _resolve(spec.get("value"), fixtures, steps)
    if op == "equals":
        ok = actual == expected
    elif op == "not_equals":
        ok = actual != expected
    elif op == "contains":
        ok = expected in actual
    elif op == "contains_all":
        ok = all(item in actual for item in expected)
    elif op == "set_equals":
        ok = set(actual) == set(expected)
    elif op == "length":
        ok = len(actual) == expected
    elif op == "contains_match":
        ok = isinstance(actual, list) and any(
            _matches_subset(item, expected) for item in actual
        )
    elif op == "not_contains_match":
        ok = isinstance(actual, list) and not any(
            _matches_subset(item, expected) for item in actual
        )
    elif op == "gte":
        ok = actual >= expected
    elif op == "lte":
        ok = actual <= expected
    elif op == "one_of":
        ok = actual in expected
    elif op == "truthy":
        ok = bool(actual)
    elif op == "falsy":
        ok = not bool(actual)
    else:
        raise ScenarioError(f"unsupported assertion op: {op}")
    if not ok:
        raise ScenarioError(
            f"{path or '/'}: assertion {op} failed; "
            f"actual={actual!r} expected={expected!r}"
        )


def validate_scenario(document: dict[str, Any]) -> None:
    if document.get("version") != 1:
        raise ScenarioError("scenario version must be 1")
    if document.get("kind") != "harness-scenario":
        raise ScenarioError("scenario kind must be harness-scenario")
    if not isinstance(document.get("id"), str) or not document["id"]:
        raise ScenarioError("scenario id is required")
    dimensions = document.get("dimensions", {}) or {}
    if not isinstance(dimensions, dict):
        raise ScenarioError("scenario dimensions must be a mapping")
    for name, value in dimensions.items():
        if not isinstance(name, str) or not name:
            raise ScenarioError("scenario dimension name must be non-empty")
        if not isinstance(value, str) or not value:
            raise ScenarioError(f"scenario dimension {name} must be a non-empty string")

    steps = document.get("steps")
    if not isinstance(steps, list) or not steps:
        raise ScenarioError("scenario requires non-empty steps")
    ids: set[str] = set()
    for step in steps:
        if not isinstance(step, dict):
            raise ScenarioError("scenario step must be a mapping")
        step_id = step.get("id")
        driver = step.get("driver")
        if not isinstance(step_id, str) or not step_id:
            raise ScenarioError("scenario step id is required")
        if step_id in ids:
            raise ScenarioError(f"duplicate scenario step id: {step_id}")
        ids.add(step_id)
        if not isinstance(driver, str) or not driver:
            raise ScenarioError(f"step {step_id} driver is required")
        benchmark = step.get("benchmark")
        if benchmark is not None:
            if not isinstance(benchmark, dict):
                raise ScenarioError(
                    f"step {step_id} benchmark must be a mapping"
                )
            metrics = benchmark.get("metrics")
            if (
                not isinstance(metrics, list)
                or not metrics
                or any(not isinstance(item, str) or not item for item in metrics)
            ):
                raise ScenarioError(
                    f"step {step_id} benchmark requires non-empty metrics"
                )
            mutation_class = benchmark.get("mutation_class")
            if mutation_class is not None and (
                not isinstance(mutation_class, str) or not mutation_class
            ):
                raise ScenarioError(
                    f"step {step_id} benchmark mutation_class must be non-empty"
                )


def run_scenario(path: Path) -> ScenarioResult:
    document = _load_yaml(path)
    if not isinstance(document, dict):
        return ScenarioResult(
            id=path.stem,
            path=str(path),
            status="FAILED",
            covers=[],
            dimensions={},
            steps=[],
            error="scenario must contain a mapping",
        )
    scenario_id = str(document.get("id", path.stem))
    covers = list(document.get("covers", []) or [])
    dimensions = dict(document.get("dimensions", {}) or {})
    for legacy_name in ("project_archetype", "stage"):
        if legacy_name in document and legacy_name not in dimensions:
            dimensions[legacy_name] = document[legacy_name]
    trace: list[dict[str, Any]] = []
    current_step: dict[str, Any] | None = None

    try:
        validate_scenario(document)
        with tempfile.TemporaryDirectory(prefix=f"harness-scenario-{scenario_id}-") as tmp:
            temp_root = Path(tmp)
            fixtures = {
                fixture_id: _load_fixture(
                    spec,
                    path.parent,
                    temp_root,
                    fixture_id,
                )
                for fixture_id, spec in (document.get("fixtures", {}) or {}).items()
            }
            outputs: dict[str, Any] = {}
            for step in document["steps"]:
                current_step = step
                step_id = step["id"]
                args = _resolve(step.get("with", {}) or {}, fixtures, outputs)
                driver = get_driver(step["driver"])
                expect_error = step.get("expect_error")
                try:
                    output = driver(**args)
                except Exception as exc:
                    if not isinstance(expect_error, dict):
                        raise
                    expected_type = expect_error.get("type")
                    contains = expect_error.get("contains")
                    if expected_type and exc.__class__.__name__ != expected_type:
                        raise ScenarioError(
                            f"step {step_id}: expected error {expected_type}, "
                            f"got {exc.__class__.__name__}"
                        ) from exc
                    if contains and contains not in str(exc):
                        raise ScenarioError(
                            f"step {step_id}: error text does not contain {contains!r}"
                        ) from exc
                    output = {
                        "error": {
                            "type": exc.__class__.__name__,
                            "message": str(exc),
                        }
                    }
                else:
                    if expect_error is not None:
                        raise ScenarioError(
                            f"step {step_id}: expected an error but driver succeeded"
                        )

                outputs[step_id] = output
                for assertion in step.get("expect", []) or []:
                    if not isinstance(assertion, dict):
                        raise ScenarioError(
                            f"step {step_id}: assertion must be a mapping"
                        )
                    _assertion(output, assertion, fixtures, outputs)
                observe = step.get("observe", {}) or {}
                if not isinstance(observe, dict):
                    raise ScenarioError(
                        f"step {step_id}: observe must be a mapping"
                    )
                observations = {}
                for name, pointer in observe.items():
                    if not isinstance(name, str) or not name:
                        raise ScenarioError(
                            f"step {step_id}: observation name must be non-empty"
                        )
                    if not isinstance(pointer, str):
                        raise ScenarioError(
                            f"step {step_id}: observation path must be a string"
                        )
                    observed = _pointer(output, pointer, _MISSING)
                    if observed is _MISSING:
                        raise ScenarioError(
                            f"step {step_id}: observation path absent: {pointer}"
                        )
                    observations[name] = copy.deepcopy(observed)

                trace.append(
                    {
                        "id": step_id,
                        "driver": step["driver"],
                        "status": "PASS",
                        **(
                            {"benchmark": copy.deepcopy(step["benchmark"])}
                            if step.get("benchmark") is not None
                            else {}
                        ),
                        **(
                            {"observations": observations}
                            if observations
                            else {}
                        ),
                    }
                )
    except Exception as exc:
        trace.append(
            {
                "id": (
                    current_step.get("id")
                    if isinstance(current_step, dict)
                    else "<setup>"
                ),
                **(
                    {"driver": current_step.get("driver")}
                    if isinstance(current_step, dict)
                    and current_step.get("driver")
                    else {}
                ),
                "status": "FAIL",
                **(
                    {"benchmark": copy.deepcopy(current_step["benchmark"])}
                    if isinstance(current_step, dict)
                    and current_step.get("benchmark") is not None
                    else {}
                ),
                "error": f"{exc.__class__.__name__}: {exc}",
            }
        )
        return ScenarioResult(
            id=scenario_id,
            path=str(path),
            status="FAILED",
            covers=covers,
            dimensions=dimensions,
            steps=trace,
            error=f"{exc.__class__.__name__}: {exc}",
        )

    return ScenarioResult(
        id=scenario_id,
        path=str(path),
        status="PASSED",
        covers=covers,
        dimensions=dimensions,
        steps=trace,
    )


def load_driver_modules(modules: list[str]) -> None:
    """Load explicitly configured driver extensions.

    Scenario YAML cannot select Python modules to import. Extensions are an
    operator/CI choice supplied through the CLI, keeping executable code out of
    untrusted scenario data.
    """
    for module in modules:
        if not isinstance(module, str) or not module.strip():
            raise ScenarioError("driver module name must be non-empty")
        importlib.import_module(module)


def _load_catalog(path: Path) -> dict[str, Any]:
    document = _load_yaml(path)
    if not isinstance(document, dict):
        raise ScenarioError("coverage catalog must contain a mapping")
    if document.get("version") != 1:
        raise ScenarioError("coverage catalog version must be 1")
    if document.get("kind") != "harness-scenario-coverage-catalog":
        raise ScenarioError("unexpected coverage catalog kind")
    return document


def evaluate_coverage(
    catalog: dict[str, Any],
    results: list[ScenarioResult],
) -> dict[str, Any]:
    requirements = {
        item["id"]: item
        for item in catalog.get("requirements", []) or []
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }
    dimensions = catalog.get("dimensions", {}) or {}
    findings: list[dict[str, Any]] = []
    planned_gaps: list[dict[str, Any]] = []

    required_scenario_dimensions = (
        catalog.get("required_scenario_dimensions", []) or []
    )

    for result in results:
        for dimension in required_scenario_dimensions:
            if dimension not in result.dimensions:
                findings.append(
                    {
                        "code": "SCENARIO_DIMENSION_MISSING",
                        "scenario": result.id,
                        "dimension": dimension,
                    }
                )
        for claim in result.covers:
            if claim not in requirements:
                findings.append(
                    {
                        "code": "UNKNOWN_COVERAGE_CLAIM",
                        "scenario": result.id,
                        "requirement": claim,
                    }
                )
        for dimension, allowed in dimensions.items():
            value = result.dimensions.get(dimension)
            if value is not None and value not in allowed:
                findings.append(
                    {
                        "code": "INVALID_SCENARIO_DIMENSION",
                        "scenario": result.id,
                        "dimension": dimension,
                        "value": value,
                    }
                )

    passed_by_requirement: dict[str, list[str]] = {
        requirement: [] for requirement in requirements
    }
    for result in results:
        if result.status != "PASSED":
            continue
        for claim in result.covers:
            if claim in passed_by_requirement:
                passed_by_requirement[claim].append(result.id)

    by_id = {result.id: result for result in results}
    requirement_status: dict[str, dict[str, Any]] = {}
    for requirement, spec in requirements.items():
        enforcement = spec.get("enforcement", "required")
        if enforcement not in {"required", "planned"}:
            findings.append(
                {
                    "code": "INVALID_REQUIREMENT_ENFORCEMENT",
                    "requirement": requirement,
                    "enforcement": enforcement,
                }
            )
            enforcement = "required"
        minimum = int(spec.get("min_scenarios", 1))
        passed = sorted(set(passed_by_requirement[requirement]))
        requirement_status[requirement] = {
            "enforcement": enforcement,
            "minimum": minimum,
            "passed": passed,
            "covered": len(passed) >= minimum,
        }
        if len(passed) < minimum:
            gap = {
                "code": "SCENARIO_COVERAGE_MISSING",
                "requirement": requirement,
                "required": minimum,
                "passed": passed,
            }
            if enforcement == "required":
                findings.append(gap)
            else:
                planned_gaps.append(gap)
        required_dimensions = spec.get("required_dimensions", {}) or {}
        for dimension, required_values in required_dimensions.items():
            observed = {
                by_id[scenario_id].dimensions.get(dimension)
                for scenario_id in passed
                if scenario_id in by_id
            }
            for required_value in required_values:
                if required_value not in observed:
                    gap = {
                        "code": "SCENARIO_DIMENSION_COVERAGE_MISSING",
                        "requirement": requirement,
                        "dimension": dimension,
                        "value": required_value,
                        "observed": sorted(
                            value for value in observed if value is not None
                        ),
                    }
                    if enforcement == "required":
                        findings.append(gap)
                    else:
                        planned_gaps.append(gap)

    passed_results = [result for result in results if result.status == "PASSED"]
    required_dimension_values = catalog.get("required_dimension_values", {}) or {}
    for dimension, required_values in required_dimension_values.items():
        observed = {
            result.dimensions.get(dimension)
            for result in passed_results
            if result.dimensions.get(dimension) is not None
        }
        for required_value in required_values:
            if required_value not in observed:
                findings.append(
                    {
                        "code": "SUITE_DIMENSION_COVERAGE_MISSING",
                        "dimension": dimension,
                        "value": required_value,
                        "observed": sorted(observed),
                    }
                )

    used_drivers = {
        step.get("driver")
        for result in passed_results
        for step in result.steps
        if step.get("driver")
    }
    for driver in catalog.get("required_drivers", []) or []:
        if driver not in used_drivers:
            findings.append(
                {
                    "code": "SCENARIO_DRIVER_COVERAGE_MISSING",
                    "driver": driver,
                }
            )

    return {
        "status": "PASS" if not findings else "FAIL",
        "requirements": {
            requirement: sorted(set(scenarios))
            for requirement, scenarios in passed_by_requirement.items()
        },
        "requirement_status": requirement_status,
        "planned_gaps": planned_gaps,
        "planned_gap_count": len(planned_gaps),
        "findings": findings,
    }



def evaluate_benchmarks(
    catalog: dict[str, Any],
    results: list[ScenarioResult],
) -> dict[str, Any]:
    metric_counts: dict[str, dict[str, int]] = {}
    mutation_counts: dict[str, dict[str, int]] = {}
    cases: list[dict[str, Any]] = []

    for result in results:
        for step in result.steps:
            benchmark = step.get("benchmark")
            if not isinstance(benchmark, dict):
                continue
            metrics = benchmark.get("metrics", []) or []
            passed = step.get("status") == "PASS"
            case = {
                "scenario": result.id,
                "step": step.get("id"),
                "status": "PASS" if passed else "FAIL",
                "metrics": list(metrics),
            }
            mutation_class = benchmark.get("mutation_class")
            if isinstance(mutation_class, str):
                case["mutation_class"] = mutation_class
            cases.append(case)

            for metric in metrics:
                counts = metric_counts.setdefault(
                    metric,
                    {"total": 0, "passed": 0, "failed": 0},
                )
                counts["total"] += 1
                counts["passed" if passed else "failed"] += 1

            if isinstance(mutation_class, str):
                counts = mutation_counts.setdefault(
                    mutation_class,
                    {"total": 0, "passed": 0, "failed": 0},
                )
                counts["total"] += 1
                counts["passed" if passed else "failed"] += 1

    def rendered(
        source: dict[str, dict[str, int]],
    ) -> dict[str, dict[str, Any]]:
        return {
            key: {
                **counts,
                "pass_rate": (
                    counts["passed"] / counts["total"]
                    if counts["total"]
                    else None
                ),
            }
            for key, counts in sorted(source.items())
        }

    findings: list[dict[str, Any]] = []
    for metric in catalog.get("required_benchmark_metrics", []) or []:
        if metric not in metric_counts:
            findings.append(
                {
                    "code": "BENCHMARK_METRIC_MISSING",
                    "metric": metric,
                }
            )

    return {
        "status": "PASS" if not findings else "FAIL",
        "case_count": len(cases),
        "metrics": rendered(metric_counts),
        "mutation_classes": rendered(mutation_counts),
        "cases": cases,
        "findings": findings,
    }

def run_suite(root: Path, catalog_path: Path) -> dict[str, Any]:
    paths = sorted(root.rglob("*.yaml"))
    results = [run_scenario(path) for path in paths]
    ids = [result.id for result in results]
    duplicate_ids = sorted({item for item in ids if ids.count(item) > 1})
    catalog = _load_catalog(catalog_path)
    coverage = evaluate_coverage(catalog, results)
    benchmarks = evaluate_benchmarks(catalog, results)
    findings = list(coverage["findings"]) + list(benchmarks["findings"])
    if duplicate_ids:
        findings.append(
            {"code": "DUPLICATE_SCENARIO_ID", "ids": duplicate_ids}
        )
    failed = [result.id for result in results if result.status != "PASSED"]
    status = "PASS" if not failed and not findings else "FAIL"
    return {
        "version": 1,
        "kind": "harness-scenario-suite-report",
        "status": status,
        "scenario_count": len(results),
        "passed": [result.id for result in results if result.status == "PASSED"],
        "failed": failed,
        "driver_usage": sorted(
            {
                step.get("driver")
                for result in results
                for step in result.steps
                if step.get("driver")
            }
        ),
        "coverage": {
            **coverage,
            "findings": findings,
        },
        "benchmarks": benchmarks,
        "scenarios": [result.as_dict() for result in results],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Harness scenario suite")
    parser.add_argument("root", nargs="?", default="spec/scenario-suite/scenarios")
    parser.add_argument(
        "--catalog",
        default="spec/scenario-suite/catalog-v1.yaml",
    )
    parser.add_argument("--json-report")
    parser.add_argument(
        "--driver-module",
        action="append",
        default=[],
        help=(
            "Explicit Python module that registers extra scenario drivers. "
            "May be repeated; modules are never selected from scenario YAML."
        ),
    )
    args = parser.parse_args()

    load_driver_modules(args.driver_module)
    report = run_suite(Path(args.root), Path(args.catalog))
    rendered = json.dumps(report, indent=2, sort_keys=True)
    if args.json_report:
        Path(args.json_report).write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
