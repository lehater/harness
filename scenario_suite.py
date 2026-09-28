#!/usr/bin/env python3
"""Universal executable scenario suite for Harness behavior."""
from __future__ import annotations

import argparse
import copy
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


@dataclass
class ScenarioResult:
    id: str
    path: str
    status: str
    covers: list[str]
    project_archetype: str | None
    stage: str | None
    steps: list[dict[str, Any]]
    error: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "path": self.path,
            "status": self.status,
            "covers": self.covers,
            "project_archetype": self.project_archetype,
            "stage": self.stage,
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


def _pointer(value: Any, pointer: str, default: Any = _MISSING) -> Any:
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
        if default is not _MISSING:
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


def run_scenario(path: Path) -> ScenarioResult:
    document = _load_yaml(path)
    if not isinstance(document, dict):
        return ScenarioResult(
            id=path.stem,
            path=str(path),
            status="FAILED",
            covers=[],
            project_archetype=None,
            stage=None,
            steps=[],
            error="scenario must contain a mapping",
        )
    scenario_id = str(document.get("id", path.stem))
    covers = list(document.get("covers", []) or [])
    archetype = document.get("project_archetype")
    stage = document.get("stage")
    trace: list[dict[str, Any]] = []

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
                trace.append(
                    {
                        "id": step_id,
                        "driver": step["driver"],
                        "status": "PASS",
                    }
                )
    except Exception as exc:
        trace.append(
            {
                "id": trace[-1]["id"] if trace else "<setup>",
                "status": "FAIL",
                "error": f"{exc.__class__.__name__}: {exc}",
            }
        )
        return ScenarioResult(
            id=scenario_id,
            path=str(path),
            status="FAILED",
            covers=covers,
            project_archetype=archetype,
            stage=stage,
            steps=trace,
            error=f"{exc.__class__.__name__}: {exc}",
        )

    return ScenarioResult(
        id=scenario_id,
        path=str(path),
        status="PASSED",
        covers=covers,
        project_archetype=archetype,
        stage=stage,
        steps=trace,
    )


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

    for result in results:
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
            value = getattr(result, dimension, None)
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

    for requirement, spec in requirements.items():
        minimum = int(spec.get("min_scenarios", 1))
        passed = sorted(set(passed_by_requirement[requirement]))
        if len(passed) < minimum:
            findings.append(
                {
                    "code": "SCENARIO_COVERAGE_MISSING",
                    "requirement": requirement,
                    "required": minimum,
                    "passed": passed,
                }
            )

    return {
        "status": "PASS" if not findings else "FAIL",
        "requirements": {
            requirement: sorted(set(scenarios))
            for requirement, scenarios in passed_by_requirement.items()
        },
        "findings": findings,
    }


def run_suite(root: Path, catalog_path: Path) -> dict[str, Any]:
    paths = sorted(root.rglob("*.yaml"))
    results = [run_scenario(path) for path in paths]
    ids = [result.id for result in results]
    duplicate_ids = sorted({item for item in ids if ids.count(item) > 1})
    catalog = _load_catalog(catalog_path)
    coverage = evaluate_coverage(catalog, results)
    findings = list(coverage["findings"])
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
    args = parser.parse_args()

    report = run_suite(Path(args.root), Path(args.catalog))
    rendered = json.dumps(report, indent=2, sort_keys=True)
    if args.json_report:
        Path(args.json_report).write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
