#!/usr/bin/env python3
from __future__ import annotations

import copy
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from harness.project_model.core import CoreError
from harness.application.project_publication import (
    _yaml_serialization_projection,
    build_project_publication,
    prepare_capability_transition,
    prepare_reconciliation_publication,
    publish_project_publication,
    read_project_publication,
    validate_project_publication,
)


GRAPH = {
    "version": 1,
    "kind": "harness-engineering-graph",
    "id": "PROJECT-PUBLICATION",
    "authorities": [
        {
            "id": "PRODUCT",
            "responsibility": "Own accepted product knowledge.",
            "boundary": {
                "semantic_cohesion": "Product semantics.",
                "independent_change": "Product semantics change independently.",
                "public_contract": "Accepted product requirement.",
            },
            "produces": [
                {
                    "capability": "demo.requirement",
                    "knowledge_kind": "product-requirements",
                    "requires": [],
                }
            ],
        }
    ],
    "consumers": [
        {
            "id": "TARGET",
            "purpose": "Consume accepted product requirement.",
            "requires": ["demo.requirement"],
        }
    ],
    "terminal_capabilities": [],
}

EMPTY_CORE = {"artifacts": [], "questions": []}
EMPTY_EVALUATIONS = {
    "version": 1,
    "kind": "harness-semantic-evaluation-set",
    "semantic_evaluations": [],
}
EMPTY_LIFECYCLE = {
    "version": 1,
    "kind": "harness-capability-lifecycle",
    "providers": [],
}
EMPTY_FAILURES = {
    "version": 1,
    "kind": "harness-decision-failure-set",
    "failures": [],
}

CURRENT_CORE = {
    "artifacts": [
        {
            "id": "REQUIREMENT",
            "authority": "PRODUCT",
            "path": "docs/requirement.yaml",
            "provides": ["demo.requirement"],
            "depends_on": [],
        }
    ],
    "questions": [],
}
CURRENT_EVALUATIONS = {
    "version": 1,
    "kind": "harness-semantic-evaluation-set",
    "semantic_evaluations": [
        {
            "version": 1,
            "kind": "harness-artifact-semantic-evaluation",
            "artifact": "REQUIREMENT",
            "capability": "demo.requirement",
            "status": "ACCEPTED",
            "obligations": {
                "expected": [],
                "satisfied": [],
                "dispositions": [],
            },
            "findings": [],
            "semantic_claims": {"accepted": []},
            "admission": {
                "status": "ACCEPTED",
                "acceptance_id": "REQ-1",
            },
        }
    ],
}
CURRENT_LIFECYCLE = {
    "version": 1,
    "kind": "harness-capability-lifecycle",
    "providers": [
        {
            "artifact": "REQUIREMENT",
            "capability": "demo.requirement",
            "acceptance_id": "REQ-1",
            "accepted_prerequisites": {},
        }
    ],
}


def expect_core_error(fn, fragment: str) -> None:
    try:
        fn()
    except CoreError as exc:
        assert fragment in str(exc), (fragment, str(exc))
    else:
        raise AssertionError(f"expected CoreError containing {fragment!r}")


def test_capability_blocker_granularity() -> None:
    graph = {
        "version": 1,
        "kind": "harness-engineering-graph",
        "id": "PUBLICATION-BLOCKER-GRANULARITY",
        "authorities": [
            {
                "id": "PRODUCT",
                "responsibility": "Own product requirements.",
                "boundary": {
                    "semantic_cohesion": "Product semantics.",
                    "independent_change": "Product requirements change independently.",
                    "public_contract": "Accepted product requirements.",
                },
                "produces": [
                    {
                        "capability": "product.intent",
                        "knowledge_kind": "product-requirements",
                        "requires": [],
                    },
                    {
                        "capability": "product.acceptance",
                        "knowledge_kind": "product-requirements",
                        "requires": [],
                    },
                ],
            }
        ],
        "consumers": [
            {
                "id": "TARGET",
                "purpose": "Consume both product capabilities.",
                "requires": ["product.intent", "product.acceptance"],
            }
        ],
        "terminal_capabilities": [],
    }
    initial = build_project_publication(
        graph=graph,
        core_model={"artifacts": [], "questions": []},
        semantic_evaluations=EMPTY_EVALUATIONS,
        lifecycle=EMPTY_LIFECYCLE,
        decision_failures=EMPTY_FAILURES,
    )
    core = {
        "artifacts": [
            {
                "id": "REQUIREMENTS",
                "authority": "PRODUCT",
                "path": "docs/requirements.md",
                "provides": ["product.intent", "product.acceptance"],
                "depends_on": [],
            }
        ],
        "questions": [
            {
                "id": "Q-ACCEPTANCE",
                "authority": "PRODUCT",
                "text": "Which acceptance behavior is required?",
                "blocks_capabilities": ["product.acceptance"],
            }
        ],
    }
    intent_evaluations = {
        "version": 1,
        "kind": "harness-semantic-evaluation-set",
        "semantic_evaluations": [
            {
                "version": 1,
                "kind": "harness-artifact-semantic-evaluation",
                "artifact": "REQUIREMENTS",
                "capability": "product.intent",
                "status": "ACCEPTED",
                "obligations": {
                    "expected": [],
                    "satisfied": [],
                    "dispositions": [],
                },
                "findings": [],
                "semantic_claims": {"accepted": []},
                "admission": {
                    "status": "ACCEPTED",
                    "acceptance_id": "INTENT-1",
                },
            }
        ],
    }
    intent_lifecycle = {
        "version": 1,
        "kind": "harness-capability-lifecycle",
        "providers": [
            {
                "artifact": "REQUIREMENTS",
                "capability": "product.intent",
                "acceptance_id": "INTENT-1",
                "accepted_prerequisites": {},
            }
        ],
    }

    expect_core_error(
        lambda: prepare_capability_transition(
            graph=graph,
            current_publication=initial,
            expected_revision=initial["revision"],
            capability="product.intent",
            outcome="BLOCKED",
            core_model=core,
            semantic_evaluations=EMPTY_EVALUATIONS,
            lifecycle=EMPTY_LIFECYCLE,
            decision_failures=EMPTY_FAILURES,
        ),
        "requires an unresolved Core blocker",
    )

    current = prepare_capability_transition(
        graph=graph,
        current_publication=initial,
        expected_revision=initial["revision"],
        capability="product.intent",
        outcome="CURRENT",
        core_model=core,
        semantic_evaluations=intent_evaluations,
        lifecycle=intent_lifecycle,
        decision_failures=EMPTY_FAILURES,
    )
    assert current["state"]["lifecycle"]["providers"][0]["capability"] == "product.intent"


def test_reconciliation_publication_batches_terminal_outcomes() -> None:
    graph = {
        "version": 1,
        "kind": "harness-engineering-graph",
        "id": "BATCH-PUBLICATION",
        "authorities": [
            {
                "id": "PRODUCT",
                "responsibility": "Own product knowledge.",
                "boundary": {
                    "semantic_cohesion": "Product knowledge.",
                    "independent_change": "Product knowledge changes.",
                    "public_contract": "Accepted product knowledge.",
                },
                "produces": [
                    {
                        "capability": "demo.one",
                        "knowledge_kind": "product-requirements",
                        "requires": [],
                    },
                    {
                        "capability": "demo.two",
                        "knowledge_kind": "product-requirements",
                        "requires": [],
                    },
                ],
            }
        ],
        "consumers": [
            {
                "id": "TARGET",
                "purpose": "Consume both.",
                "requires": ["demo.one", "demo.two"],
            }
        ],
        "terminal_capabilities": [],
    }
    initial = build_project_publication(
        graph=graph,
        core_model=EMPTY_CORE,
        semantic_evaluations=EMPTY_EVALUATIONS,
        lifecycle=EMPTY_LIFECYCLE,
        decision_failures=EMPTY_FAILURES,
    )
    core = {
        "artifacts": [
            {
                "id": "PRODUCT",
                "authority": "PRODUCT",
                "path": "docs/product.yaml",
                "provides": ["demo.one", "demo.two"],
                "depends_on": [],
            }
        ],
        "questions": [],
    }
    evaluations = {
        "version": 1,
        "kind": "harness-semantic-evaluation-set",
        "semantic_evaluations": [
            {
                "version": 1,
                "kind": "harness-artifact-semantic-evaluation",
                "artifact": "PRODUCT",
                "capability": capability,
                "status": "ACCEPTED",
                "obligations": {
                    "expected": [],
                    "satisfied": [],
                    "dispositions": [],
                },
                "findings": [],
                "semantic_claims": {"accepted": []},
                "admission": {
                    "status": "ACCEPTED",
                    "acceptance_id": acceptance_id,
                },
            }
            for capability, acceptance_id in (
                ("demo.one", "ONE-1"),
                ("demo.two", "TWO-1"),
            )
        ],
    }
    lifecycle = {
        "version": 1,
        "kind": "harness-capability-lifecycle",
        "providers": [
            {
                "artifact": "PRODUCT",
                "capability": capability,
                "acceptance_id": acceptance_id,
                "accepted_prerequisites": {},
            }
            for capability, acceptance_id in (
                ("demo.one", "ONE-1"),
                ("demo.two", "TWO-1"),
            )
        ],
    }

    result = prepare_reconciliation_publication(
        graph=graph,
        current_publication=initial,
        expected_revision=initial["revision"],
        outcomes={"demo.one": "CURRENT", "demo.two": "CURRENT"},
        core_model=core,
        semantic_evaluations=evaluations,
        lifecycle=lifecycle,
        decision_failures=EMPTY_FAILURES,
    )
    assert result["parent_revision"] == initial["revision"], result
    assert result["revision"] != initial["revision"], result
    assert {
        item["capability"] for item in result["state"]["lifecycle"]["providers"]
    } == {"demo.one", "demo.two"}, result

    expect_core_error(
        lambda: prepare_reconciliation_publication(
            graph=graph,
            current_publication=result,
            expected_revision=initial["revision"],
            outcomes={"demo.one": "CURRENT", "demo.two": "CURRENT"},
            core_model=core,
            semantic_evaluations=evaluations,
            lifecycle=lifecycle,
            decision_failures=EMPTY_FAILURES,
        ),
        "compare-and-swap failed",
    )


def test_semantic_snapshot_currentness() -> None:
    duplicate_derivation_snapshot = {
        "version": 1,
        "kind": "harness-semantic-evaluation-set",
        "semantic_evaluations": [],
        "derivation_evaluations": [
            {
                "version": 1,
                "kind": "harness-semantic-derivation-evaluation",
                "source_capability": "demo.source",
                "target_capability": "demo.target",
                "status": "ACCEPTED",
                "question_proposals": [],
            },
            {
                "version": 1,
                "kind": "harness-semantic-derivation-evaluation",
                "source_capability": "demo.source",
                "target_capability": "demo.target",
                "status": "REJECTED",
                "question_proposals": [],
            },
        ],
    }
    expect_core_error(
        lambda: build_project_publication(
            graph=GRAPH,
            core_model=EMPTY_CORE,
            semantic_evaluations=duplicate_derivation_snapshot,
            lifecycle=EMPTY_LIFECYCLE,
            decision_failures=EMPTY_FAILURES,
        ),
        "duplicate current semantic derivation evaluation",
    )


def test_yaml_serialization_deduplicates_fingerprint_maps_losslessly() -> None:
    fingerprints = {
        f"ATOM-{index:03d}": "SAF-" + f"{index:064x}"
        for index in range(64)
    }
    publication = {
        "first": {
            "semantic_atom_fingerprints": copy.deepcopy(fingerprints),
        },
        "second": {
            "semantic_atoms": copy.deepcopy(fingerprints),
        },
        "third": {
            "source_surface_fingerprints": copy.deepcopy(fingerprints),
        },
    }

    projection = _yaml_serialization_projection(publication)
    assert projection == publication
    first = projection["first"]["semantic_atom_fingerprints"]
    second = projection["second"]["semantic_atoms"]
    third = projection["third"]["source_surface_fingerprints"]
    assert first is second is third

    naive = yaml.safe_dump(
        publication,
        sort_keys=False,
        allow_unicode=True,
    )
    compact = yaml.safe_dump(
        projection,
        sort_keys=False,
        allow_unicode=True,
    )
    assert len(compact) < len(naive) / 2, (len(compact), len(naive))
    assert yaml.safe_load(compact) == publication


def test_yaml_serialization_does_not_alias_unrelated_equal_mappings() -> None:
    fingerprints = {
        f"ATOM-{index:03d}": "SAF-" + f"{index:064x}"
        for index in range(16)
    }
    publication = {
        "fingerprint": {
            "semantic_atom_fingerprints": copy.deepcopy(fingerprints),
        },
        "unrelated_a": {"payload": copy.deepcopy(fingerprints)},
        "unrelated_b": {"payload": copy.deepcopy(fingerprints)},
    }

    projection = _yaml_serialization_projection(publication)

    assert projection == publication
    assert (
        projection["unrelated_a"]["payload"]
        is not projection["unrelated_b"]["payload"]
    )


def test_publish_project_publication_writes_compact_lossless_yaml() -> None:
    fingerprints = {
        f"ATOM-{index:03d}": "SAF-" + f"{index:064x}"
        for index in range(64)
    }
    evaluations = copy.deepcopy(CURRENT_EVALUATIONS)
    evaluation = evaluations["semantic_evaluations"][0]
    evaluation["semantic_atom_fingerprints"] = copy.deepcopy(fingerprints)
    evaluation["source_surface_fingerprints"] = copy.deepcopy(fingerprints)

    publication = build_project_publication(
        graph=GRAPH,
        core_model=CURRENT_CORE,
        semantic_evaluations=evaluations,
        lifecycle=CURRENT_LIFECYCLE,
        decision_failures=EMPTY_FAILURES,
    )
    naive = yaml.safe_dump(
        publication,
        sort_keys=False,
        allow_unicode=True,
    )

    with tempfile.TemporaryDirectory(prefix="project-publication-compact-") as temp_dir:
        path = Path(temp_dir) / "project-publication.yaml"
        publish_project_publication(
            path,
            graph=GRAPH,
            publication=publication,
            expected_revision=None,
        )

        raw = path.read_text(encoding="utf-8")
        reloaded = read_project_publication(path, graph=GRAPH)

    assert len(raw) < len(naive), (len(raw), len(naive))
    assert "&id" in raw, raw
    assert "*id" in raw, raw
    assert reloaded == publication
    assert reloaded["revision"] == publication["revision"]


def test_yaml_serialization_compaction_scales_with_repeated_fanout() -> None:
    fingerprints = {
        f"ATOM-{index:03d}": "SAF-" + f"{index:064x}"
        for index in range(96)
    }
    one_edge = {
        "edges": [
            {
                "source_surface_fingerprints": copy.deepcopy(fingerprints),
            }
        ]
    }
    many_edges = {
        "edges": [
            {
                "source_surface_fingerprints": copy.deepcopy(fingerprints),
            }
            for _ in range(32)
        ]
    }

    one_naive = yaml.safe_dump(
        one_edge,
        sort_keys=False,
        allow_unicode=True,
    )
    many_naive = yaml.safe_dump(
        many_edges,
        sort_keys=False,
        allow_unicode=True,
    )
    one_compact = yaml.safe_dump(
        _yaml_serialization_projection(one_edge),
        sort_keys=False,
        allow_unicode=True,
    )
    many_compact = yaml.safe_dump(
        _yaml_serialization_projection(many_edges),
        sort_keys=False,
        allow_unicode=True,
    )

    assert yaml.safe_load(many_compact) == many_edges
    naive_growth = len(many_naive) - len(one_naive)
    compact_growth = len(many_compact) - len(one_compact)
    assert compact_growth * 8 < naive_growth, (
        compact_growth,
        naive_growth,
    )


def main() -> int:
    test_yaml_serialization_deduplicates_fingerprint_maps_losslessly()
    test_yaml_serialization_does_not_alias_unrelated_equal_mappings()
    test_publish_project_publication_writes_compact_lossless_yaml()
    test_yaml_serialization_compaction_scales_with_repeated_fanout()
    test_semantic_snapshot_currentness()
    test_capability_blocker_granularity()
    test_reconciliation_publication_batches_terminal_outcomes()
    initial = build_project_publication(
        graph=GRAPH,
        core_model=EMPTY_CORE,
        semantic_evaluations=EMPTY_EVALUATIONS,
        lifecycle=EMPTY_LIFECYCLE,
        decision_failures=EMPTY_FAILURES,
    )
    validate_project_publication(GRAPH, initial)

    current = prepare_capability_transition(
        graph=GRAPH,
        current_publication=initial,
        expected_revision=initial["revision"],
        capability="demo.requirement",
        outcome="CURRENT",
        core_model=CURRENT_CORE,
        semantic_evaluations=CURRENT_EVALUATIONS,
        lifecycle=CURRENT_LIFECYCLE,
        decision_failures=EMPTY_FAILURES,
    )
    assert current["parent_revision"] == initial["revision"], current
    assert current["revision"] != initial["revision"], current

    repeated = prepare_capability_transition(
        graph=GRAPH,
        current_publication=current,
        expected_revision=current["revision"],
        capability="demo.requirement",
        outcome="CURRENT",
        core_model=CURRENT_CORE,
        semantic_evaluations=CURRENT_EVALUATIONS,
        lifecycle=CURRENT_LIFECYCLE,
        decision_failures=EMPTY_FAILURES,
    )
    assert repeated == current, (repeated, current)

    expect_core_error(
        lambda: prepare_capability_transition(
            graph=GRAPH,
            current_publication=current,
            expected_revision=initial["revision"],
            capability="demo.requirement",
            outcome="CURRENT",
            core_model=CURRENT_CORE,
            semantic_evaluations=CURRENT_EVALUATIONS,
            lifecycle=CURRENT_LIFECYCLE,
            decision_failures=EMPTY_FAILURES,
        ),
        "compare-and-swap failed",
    )

    tampered = copy.deepcopy(current)
    tampered["state"]["lifecycle"]["providers"][0]["acceptance_id"] = "REQ-PARTIAL"
    expect_core_error(
        lambda: validate_project_publication(GRAPH, tampered),
        "acceptance identity mismatch",
    )

    blocked_core = {
        "artifacts": [],
        "questions": [
            {
                "id": "Q-REQUIREMENT",
                "authority": "PRODUCT",
                "text": "Which product behavior is required?",
                "blocks": [],
                "blocks_capabilities": ["demo.requirement"],
            }
        ],
    }
    blocked = prepare_capability_transition(
        graph=GRAPH,
        current_publication=initial,
        expected_revision=initial["revision"],
        capability="demo.requirement",
        outcome="BLOCKED",
        core_model=blocked_core,
        semantic_evaluations=EMPTY_EVALUATIONS,
        lifecycle=EMPTY_LIFECYCLE,
        decision_failures=EMPTY_FAILURES,
    )
    assert blocked["revision"] != initial["revision"], blocked

    failure_set = {
        "version": 1,
        "kind": "harness-decision-failure-set",
        "failures": [
            {
                "capability": "demo.requirement",
                "failure_id": "FAIL-1",
                "stage": "SEMANTIC_ADMISSION",
                "finding": "candidate validation failed",
            }
        ],
    }
    failed = prepare_capability_transition(
        graph=GRAPH,
        current_publication=initial,
        expected_revision=initial["revision"],
        capability="demo.requirement",
        outcome="FAILED_VALIDATION",
        core_model=EMPTY_CORE,
        semantic_evaluations=EMPTY_EVALUATIONS,
        lifecycle=EMPTY_LIFECYCLE,
        decision_failures=failure_set,
    )
    assert failed["state"]["decision_failures"]["failures"], failed

    expect_core_error(
        lambda: prepare_capability_transition(
            graph=GRAPH,
            current_publication=initial,
            expected_revision=initial["revision"],
            capability="demo.requirement",
            outcome="CURRENT",
            core_model=CURRENT_CORE,
            semantic_evaluations=CURRENT_EVALUATIONS,
            lifecycle=CURRENT_LIFECYCLE,
            decision_failures=failure_set,
        ),
        "must clear persisted failure evidence",
    )

    with tempfile.TemporaryDirectory(prefix="project-publication-") as temp_dir:
        path = Path(temp_dir) / "project-publication.yaml"
        publish_project_publication(
            path,
            graph=GRAPH,
            publication=initial,
            expected_revision=None,
        )
        assert read_project_publication(path, graph=GRAPH)["revision"] == initial["revision"]

        with patch("harness.application.project_publication.os.replace", side_effect=OSError("simulated crash")):
            try:
                publish_project_publication(
                    path,
                    graph=GRAPH,
                    publication=current,
                    expected_revision=initial["revision"],
                )
            except OSError as exc:
                assert "simulated crash" in str(exc), exc
            else:
                raise AssertionError("simulated publication crash must fail")

        after_crash = read_project_publication(path, graph=GRAPH)
        assert after_crash["revision"] == initial["revision"], after_crash

        publish_project_publication(
            path,
            graph=GRAPH,
            publication=current,
            expected_revision=initial["revision"],
        )
        assert read_project_publication(path, graph=GRAPH)["revision"] == current["revision"]

        expect_core_error(
            lambda: publish_project_publication(
                path,
                graph=GRAPH,
                publication=current,
                expected_revision=initial["revision"],
            ),
            "compare-and-swap failed",
        )

    print(
        "project publication: PASS "
        "(coherent snapshot + terminal outcome + CAS + crash-safe direct publish)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
