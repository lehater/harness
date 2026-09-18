#!/usr/bin/env python3
"""Validate consumer contracts and package projections built on Core v0."""
from __future__ import annotations

import copy
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from consumers.contract import (  # noqa: E402
    ConsumerContractError,
    evaluate_contract,
    project_package,
)


def _requirements_by_id(evaluation: dict) -> dict[str, dict]:
    return {item["id"]: item for item in evaluation["requirements"]}


def main() -> int:
    errors: list[str] = []
    fixtures = sorted((ROOT / "spec/consumer-acceptance").glob("*.yaml"))
    if not fixtures:
        errors.append("no consumer acceptance fixtures found")

    for path in fixtures:
        try:
            doc = yaml.safe_load(path.read_text(encoding="utf-8"))
            if doc.get("kind") != "harness-consumer-acceptance":
                raise ConsumerContractError("unexpected consumer acceptance fixture kind")

            model = doc["model"]
            contract = doc["contract"]
            expect = doc["expect"]

            evaluation = evaluate_contract(model, contract)
            if evaluation["satisfied"] is not expect["satisfied"]:
                raise ConsumerContractError("consumer contract satisfaction mismatch")

            actual = _requirements_by_id(evaluation)
            expected_statuses = expect["statuses"]
            if set(actual) != set(expected_statuses):
                raise ConsumerContractError("consumer requirement set mismatch")
            for requirement_id, status in expected_statuses.items():
                if actual[requirement_id]["status"] != status:
                    raise ConsumerContractError(
                        f"{requirement_id}: expected {status}, "
                        f"got {actual[requirement_id]['status']}"
                    )

            package = project_package(model, contract)
            package_entries = {item["id"]: item for item in package["entries"]}
            for requirement_id, expected_sources in expect.get("package_sources", {}).items():
                if package_entries[requirement_id]["source_artifacts"] != sorted(expected_sources):
                    raise ConsumerContractError(
                        f"{requirement_id}: package source projection mismatch"
                    )

            regression = doc["regression"]
            broken_model = copy.deepcopy(model)
            removal = regression["remove_capability"]
            for artifact in broken_model["artifacts"]:
                if artifact["id"] == removal["artifact"]:
                    artifact["provides"].remove(removal["capability"])
                    break
            else:
                raise ConsumerContractError(
                    f"regression artifact not found: {removal['artifact']}"
                )

            broken = evaluate_contract(broken_model, contract)
            regression_expect = regression["expect"]
            if broken["satisfied"] is not regression_expect["satisfied"]:
                raise ConsumerContractError("regression satisfaction mismatch")

            broken_requirement = _requirements_by_id(broken)[regression_expect["requirement"]]
            if broken_requirement["status"] != regression_expect["status"]:
                raise ConsumerContractError("regression DESIGN_GAP mismatch")
            if broken_requirement["question"]["authority"] != regression_expect["question_authority"]:
                raise ConsumerContractError("regression Question routing mismatch")

            if regression_expect.get("package_projection_blocked"):
                try:
                    project_package(broken_model, contract)
                except ConsumerContractError:
                    pass
                else:
                    raise ConsumerContractError(
                        "package projection must fail for an unsatisfied consumer contract"
                    )
        except Exception as exc:
            errors.append(f"{path.relative_to(ROOT)}: {exc}")

    if errors:
        print("Harness consumer validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(f"Harness consumer validation passed ({len(fixtures)} acceptance fixture(s))")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
