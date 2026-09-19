#!/usr/bin/env python3
"""Validate Harness Engineering Graph v0 acceptance fixtures."""
from __future__ import annotations

import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from engineering_graph import (  # noqa: E402
    derive_profile,
    evaluate_engineering_target,
    validate_engineering_graph,
)
from harness import CoreError  # noqa: E402


def _capabilities(items):
    return sorted(item["capability"] for item in items)


def main() -> int:
    errors: list[str] = []
    fixtures = sorted((ROOT / "spec/engineering-graph-acceptance").glob("*.yaml"))
    if not fixtures:
        errors.append("no Engineering Graph acceptance fixtures found")

    for path in fixtures:
        try:
            doc = yaml.safe_load(path.read_text(encoding="utf-8"))
            if doc.get("kind") != "harness-engineering-graph-acceptance":
                raise CoreError("unexpected Engineering Graph acceptance fixture kind")

            graph = doc["graph"]
            validate_engineering_graph(graph)
            target = next(
                item["id"]
                for item in graph["consumers"]
                if item["id"] == "IMPLEMENTATION"
            )
            profile = derive_profile(graph, target)

            by_id = {item["id"]: item for item in profile["expectations"]}
            id_to_capability = {
                item_id: item["capability"]
                for item_id, item in by_id.items()
            }
            actual_caps = sorted(item["capability"] for item in profile["expectations"])
            expected_caps = sorted(doc["expect_profile"]["capabilities"])
            if actual_caps != expected_caps:
                raise CoreError(
                    f"derived profile capabilities mismatch: {actual_caps!r} != {expected_caps!r}"
                )

            actual_dependencies = {}
            for item in profile["expectations"]:
                actual_dependencies[item["capability"]] = sorted(
                    id_to_capability[dependency]
                    for dependency in item.get("depends_on", [])
                )
            expected_dependencies = {
                capability: sorted(dependencies)
                for capability, dependencies
                in doc["expect_profile"]["dependencies"].items()
            }
            if actual_dependencies != expected_dependencies:
                raise CoreError(
                    "derived profile dependency mismatch: "
                    f"{actual_dependencies!r} != {expected_dependencies!r}"
                )

            for case_id, case in doc["cases"].items():
                actual = evaluate_engineering_target(
                    graph,
                    target,
                    case["model"],
                )
                expected = case["expect"]
                summary = {
                    "status": actual["status"],
                    "satisfied": sorted(
                        by_id[expectation_id]["capability"]
                        for expectation_id in actual["satisfied"]
                    ),
                    "create": _capabilities(actual["create"]),
                    "wait": _capabilities(actual["wait"]),
                    "pending": _capabilities(actual["pending"]),
                }
                normalized_expected = {
                    "status": expected["status"],
                    "satisfied": sorted(expected["satisfied"]),
                    "create": sorted(expected["create"]),
                    "wait": sorted(expected["wait"]),
                    "pending": sorted(expected["pending"]),
                }
                if summary != normalized_expected:
                    raise CoreError(
                        f"{case_id} target-state mismatch: "
                        f"{summary!r} != {normalized_expected!r}"
                    )

        except Exception as exc:
            errors.append(f"{path.relative_to(ROOT)}: {exc}")

    # Structural invalidity: one capability cannot have two semantic producers.
    invalid_multiple_producers = {
        "version": 1,
        "kind": "harness-engineering-graph",
        "id": "MULTIPLE-PRODUCERS",
        "authorities": [
            {
                "id": "A",
                "responsibility": "A",
                "boundary": {
                    "semantic_cohesion": "A",
                    "independent_change": "A",
                    "public_contract": "A",
                },
                "requires": [],
                "produces": ["x"],
            },
            {
                "id": "B",
                "responsibility": "B",
                "boundary": {
                    "semantic_cohesion": "B",
                    "independent_change": "B",
                    "public_contract": "B",
                },
                "requires": [],
                "produces": ["x"],
            },
        ],
        "consumers": [
            {"id": "IMPLEMENTATION", "purpose": "Build", "requires": ["x"]}
        ],
    }

    invalid_subject_collapse = {
        "version": 1,
        "kind": "harness-engineering-graph",
        "id": "SUBJECT-COLLAPSE",
        "authorities": [
            {
                "id": "DOMAIN",
                "responsibility": "Domain",
                "boundary": {
                    "semantic_cohesion": "Domain",
                    "independent_change": "Domain",
                    "public_contract": "Domain",
                },
                "requires": [],
                "produces": ["domain.tactical"],
            },
        ],
        "consumers": [
            {
                "id": "IMPLEMENTATION",
                "purpose": "Build",
                "requires": [
                    {"capability": "domain.tactical", "subject": "A"},
                    {"capability": "domain.tactical", "subject": "B"},
                ],
            }
        ],
    }

    invalid_cycle = {
        "version": 1,
        "kind": "harness-engineering-graph",
        "id": "CYCLE",
        "authorities": [
            {
                "id": "A",
                "responsibility": "A",
                "boundary": {
                    "semantic_cohesion": "A",
                    "independent_change": "A",
                    "public_contract": "A",
                },
                "requires": ["b"],
                "produces": ["a"],
            },
            {
                "id": "B",
                "responsibility": "B",
                "boundary": {
                    "semantic_cohesion": "B",
                    "independent_change": "B",
                    "public_contract": "B",
                },
                "requires": ["a"],
                "produces": ["b"],
            },
        ],
        "consumers": [
            {"id": "IMPLEMENTATION", "purpose": "Build", "requires": ["a"]}
        ],
    }

    for invalid in (
        invalid_multiple_producers,
        invalid_subject_collapse,
        invalid_cycle,
    ):
        try:
            validate_engineering_graph(invalid)
        except CoreError:
            pass
        else:
            errors.append(
                f"invalid Engineering Graph passed validation: {invalid['id']}"
            )

    if errors:
        print("Harness Engineering Graph validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(
        "Harness Engineering Graph validation passed "
        f"({len(fixtures)} acceptance fixture(s))"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
