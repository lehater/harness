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


def _boundary(label):
    return {
        "semantic_cohesion": label,
        "independent_change": label,
        "public_contract": label,
    }


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
            target = doc.get("target", "IMPLEMENTATION")
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

    invalid_multiple_producers = {
        "version": 1,
        "kind": "harness-engineering-graph",
        "id": "MULTIPLE-PRODUCERS",
        "authorities": [
            {
                "id": "A",
                "responsibility": "A",
                "boundary": _boundary("A"),
                "produces": ["x"],
            },
            {
                "id": "B",
                "responsibility": "B",
                "boundary": _boundary("B"),
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
                "boundary": _boundary("Domain"),
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
                "boundary": _boundary("A"),
                "produces": [
                    {"capability": "a", "requires": ["b"]}
                ],
            },
            {
                "id": "B",
                "responsibility": "B",
                "boundary": _boundary("B"),
                "produces": [
                    {"capability": "b", "requires": ["a"]}
                ],
            },
        ],
        "consumers": [
            {"id": "IMPLEMENTATION", "purpose": "Build", "requires": ["a"]}
        ],
    }

    multi_consumer_shared_graph = {
        "version": 1,
        "kind": "harness-engineering-graph",
        "id": "MULTI-CONSUMER-INDEPENDENCE",
        "default_subject": "APPLICATION",
        "authorities": [
            {"id": "PRODUCT", "responsibility": "Product", "boundary": _boundary("Product"),
             "produces": [{"capability": "intent", "requires": []}]},
            {"id": "ARCHITECTURE", "responsibility": "Architecture", "boundary": _boundary("Architecture"),
             "produces": [{"capability": "architecture", "requires": ["intent"]}]},
            {"id": "VERIFICATION", "responsibility": "Verification", "boundary": _boundary("Verification"),
             "produces": [{"capability": "verification", "requires": ["architecture"]}]},
        ],
        "consumers": [
            {"id": "IMPLEMENTATION", "purpose": "Build", "requires": ["architecture"]},
            {"id": "AUDIT", "purpose": "Audit", "requires": ["verification"]},
        ],
    }

    valid_same_authority_chain = {
        "version": 1,
        "kind": "harness-engineering-graph",
        "id": "SAME-AUTHORITY-CHAIN",
        "authorities": [
            {
                "id": "PRODUCT",
                "responsibility": "Product",
                "boundary": _boundary("Product"),
                "produces": [
                    {"capability": "problem", "requires": []},
                    {"capability": "requirements", "requires": ["problem"]},
                ],
            },
        ],
        "consumers": [
            {
                "id": "IMPLEMENTATION",
                "purpose": "Build",
                "requires": ["requirements"],
            }
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

    applicability_graph = {
        "version": 1,
        "kind": "harness-engineering-graph",
        "id": "APPLICABILITY-EVIDENCE",
        "authorities": [
            {"id": "ARCHITECTURE", "responsibility": "Architecture", "boundary": _boundary("Architecture"),
             "produces": [
                 {"capability": "deployment.topology", "requires": []},
                 {"capability": "deployment.persistence-not-required", "requires": ["deployment.topology"]},
             ]},
            {"id": "DATA", "responsibility": "Data", "boundary": _boundary("Data"),
             "produces": [
                 {"capability": "deployment.persistence-design", "requires": ["deployment.topology"]}
             ]},
        ],
        "consumers": [
            {"id": "STATELESS-IMPLEMENTATION", "purpose": "Build a stateless deployment",
             "requires": ["deployment.persistence-not-required"]},
            {"id": "STATEFUL-IMPLEMENTATION", "purpose": "Build a stateful deployment",
             "requires": ["deployment.persistence-design"]},
        ],
    }
    applicability_model = {
        "artifacts": [
            {"id": "TOPOLOGY", "authority": "ARCHITECTURE", "path": "docs/topology.yaml",
             "provides": ["deployment.topology"], "depends_on": []},
            {"id": "NO-PERSISTENCE", "authority": "ARCHITECTURE", "path": "docs/no-persistence.yaml",
             "provides": ["deployment.persistence-not-required"], "depends_on": ["TOPOLOGY"]},
        ],
        "questions": [],
    }
    try:
        stateless = evaluate_engineering_target(
            applicability_graph, "STATELESS-IMPLEMENTATION", applicability_model
        )
        stateful = evaluate_engineering_target(
            applicability_graph, "STATEFUL-IMPLEMENTATION", applicability_model
        )
        if stateless["status"] != "COMPLETE":
            errors.append(f"evidence-based non-applicability should complete: {stateless!r}")
        if stateful["status"] != "READY" or {
            item["capability"] for item in stateful["create"]
        } != {"deployment.persistence-design"}:
            errors.append(f"applicable persistence design should remain CREATE: {stateful!r}")
    except CoreError as exc:
        errors.append(f"applicability evidence topology should be valid: {exc}")

    feedback_graph = {
        "version": 1,
        "kind": "harness-engineering-graph",
        "id": "FEEDBACK-REPAIR",
        "authorities": [
            {"id": "PRODUCT", "responsibility": "Product", "boundary": _boundary("Product"),
             "produces": [{"capability": "requirements", "requires": []}]},
            {"id": "ARCHITECTURE", "responsibility": "Architecture", "boundary": _boundary("Architecture"),
             "produces": [{"capability": "architecture", "requires": ["requirements"]}]},
        ],
        "consumers": [{"id": "IMPLEMENTATION", "purpose": "Build", "requires": ["architecture"]}],
    }
    feedback_model = {
        "artifacts": [
            {"id": "REQUIREMENTS", "authority": "PRODUCT", "path": "docs/requirements.yaml",
             "provides": ["requirements"], "depends_on": []},
            {"id": "ARCHITECTURE", "authority": "ARCHITECTURE", "path": "docs/architecture.yaml",
             "provides": ["architecture"], "depends_on": ["REQUIREMENTS"]},
        ],
        "questions": [
            {"id": "Q-REQUIREMENTS-REPAIR", "authority": "PRODUCT",
             "text": "Which corrected product decision resolves the architecture contradiction?",
             "blocks": ["REQUIREMENTS"]},
        ],
    }
    try:
        blocked_feedback = evaluate_engineering_target(
            feedback_graph, "IMPLEMENTATION", feedback_model
        )
        if blocked_feedback["status"] != "BLOCKED":
            errors.append(f"feedback repair should block target: {blocked_feedback!r}")
        waiting = {item["capability"] for item in blocked_feedback["wait"]}
        if waiting != {"requirements"}:
            errors.append(f"feedback repair WAIT mismatch: {sorted(waiting)!r}")
        pending = {item["capability"] for item in blocked_feedback["pending"]}
        if pending != {"architecture"}:
            errors.append(f"feedback repair PENDING mismatch: {sorted(pending)!r}")

        repaired = {
            "artifacts": feedback_model["artifacts"] + [
                {"id": "REQUIREMENTS-REPAIR", "authority": "PRODUCT",
                 "path": "docs/requirements-repair.yaml",
                 "provides": ["requirements"], "depends_on": []},
            ],
            "questions": [
                {**feedback_model["questions"][0], "resolution": "REQUIREMENTS-REPAIR"}
            ],
        }
        repaired_result = evaluate_engineering_target(
            feedback_graph, "IMPLEMENTATION", repaired
        )
        if repaired_result["status"] != "COMPLETE":
            errors.append(f"feedback repair should restore target: {repaired_result!r}")
    except CoreError as exc:
        errors.append(f"feedback repair topology should be valid: {exc}")

    try:
        implementation_profile = derive_profile(multi_consumer_shared_graph, "IMPLEMENTATION")
        audit_profile = derive_profile(multi_consumer_shared_graph, "AUDIT")
        implementation_caps = {item["capability"] for item in implementation_profile["expectations"]}
        audit_caps = {item["capability"] for item in audit_profile["expectations"]}
        if implementation_caps != {"intent", "architecture"}:
            errors.append(f"IMPLEMENTATION closure polluted by another consumer: {sorted(implementation_caps)!r}")
        if audit_caps != {"intent", "architecture", "verification"}:
            errors.append(f"AUDIT closure mismatch: {sorted(audit_caps)!r}")
    except CoreError as exc:
        errors.append(f"independent consumer closure should be valid: {exc}")

    try:
        validate_engineering_graph(valid_same_authority_chain)
    except CoreError as exc:
        errors.append(
            "same-Authority acyclic production chain should be valid: "
            f"{exc}"
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
