#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import copy
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from harness.assurance.capability_lifecycle import (
    evaluate_lifecycle_target,
    lifecycle_states,
    obsolete_lifecycle_rows,
)
from harness.project_model.core import CoreError


GRAPH = {
    "version": 1,
    "kind": "harness-engineering-graph",
    "id": "LIFECYCLE",
    "authorities": [
        {
            "id": "SOURCE",
            "responsibility": "Source facts.",
            "boundary": {
                "semantic_cohesion": "Source facts.",
                "independent_change": "Source changes.",
                "public_contract": "Source facts.",
            },
            "produces": [
                {
                    "capability": "source.identity",
                    "knowledge_kind": "problem-evidence",
                    "requires": [],
                }
            ],
        },
        {
            "id": "USE",
            "responsibility": "Use source facts.",
            "boundary": {
                "semantic_cohesion": "Use decisions.",
                "independent_change": "Use changes.",
                "public_contract": "Use result.",
            },
            "produces": [
                {
                    "capability": "use.result",
                    "knowledge_kind": "domain-model",
                    "requires": ["source.identity"],
                }
            ],
        },
    ],
    "consumers": [
        {
            "id": "IMPLEMENTATION",
            "purpose": "Implement accepted result.",
            "requires": ["use.result"],
        }
    ],
    "terminal_capabilities": [],
}

MODEL = {
    "artifacts": [
        {
            "id": "SOURCE",
            "authority": "SOURCE",
            "path": "source.md",
            "provides": ["source.identity"],
            "depends_on": [],
        },
        {
            "id": "USE",
            "authority": "USE",
            "path": "use.md",
            "provides": ["use.result"],
            "depends_on": ["SOURCE"],
        },
    ],
    "questions": [],
}


def projection(identity="ID1", accepted="ID1"):
    return {
        "version": 1,
        "kind": "harness-capability-lifecycle",
        "providers": [
            {
                "artifact": "SOURCE",
                "capability": "source.identity",
                "acceptance_id": identity,
                "accepted_prerequisites": {},
            },
            {
                "artifact": "USE",
                "capability": "use.result",
                "acceptance_id": "U1",
                "accepted_prerequisites": {
                    "source.identity": accepted
                },
            },
        ],
    }


def test_capability_question_granularity() -> None:
    graph = {
        "version": 1,
        "kind": "harness-engineering-graph",
        "id": "CAPABILITY-QUESTION-GRANULARITY",
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
                "id": "INTENT-CONSUMER",
                "purpose": "Consume product intent.",
                "requires": ["product.intent"],
            },
            {
                "id": "ACCEPTANCE-CONSUMER",
                "purpose": "Consume acceptance semantics.",
                "requires": ["product.acceptance"],
            },
        ],
        "terminal_capabilities": [],
    }
    model = {
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
    lifecycle = {
        "version": 1,
        "kind": "harness-capability-lifecycle",
        "providers": [
            {
                "artifact": "REQUIREMENTS",
                "capability": "product.intent",
                "acceptance_id": "INTENT-1",
                "accepted_prerequisites": {},
            },
            {
                "artifact": "REQUIREMENTS",
                "capability": "product.acceptance",
                "acceptance_id": "ACCEPTANCE-1",
                "accepted_prerequisites": {},
            },
        ],
    }

    intent = evaluate_lifecycle_target(
        graph,
        "INTENT-CONSUMER",
        model,
        lifecycle,
    )
    acceptance = evaluate_lifecycle_target(
        graph,
        "ACCEPTANCE-CONSUMER",
        model,
        lifecycle,
    )
    assert intent["status"] == "COMPLETE", intent
    assert intent["wait"] == [], intent
    assert acceptance["status"] == "BLOCKED", acceptance
    assert acceptance["wait"][0]["questions"] == ["Q-ACCEPTANCE"], acceptance


def test_split_merge_do_not_transfer_acceptance() -> None:
    split_graph = copy.deepcopy(GRAPH)
    split_graph["authorities"][0]["produces"] = [
        {
            "capability": "source.identity.primary",
            "knowledge_kind": "problem-evidence",
            "requires": [],
        },
        {
            "capability": "source.identity.metadata",
            "knowledge_kind": "problem-evidence",
            "requires": [],
        },
    ]
    split_graph["authorities"][1]["produces"][0]["requires"] = [
        "source.identity.primary",
        "source.identity.metadata",
    ]
    split_model = copy.deepcopy(MODEL)
    split_model["artifacts"][0]["provides"] = [
        "source.identity.primary",
        "source.identity.metadata",
    ]
    split_states = lifecycle_states(split_graph, split_model, projection())
    assert split_states["source.identity.primary"]["state"] == "UNKNOWN", split_states
    assert split_states["source.identity.metadata"]["state"] == "UNKNOWN", split_states
    assert split_states["use.result"]["state"] == "STALE", split_states
    assert any(
        item.get("mode") == "PREREQUISITE_TOPOLOGY"
        and item.get("accepted_prerequisites") == ["source.identity"]
        and item.get("current_prerequisites")
        == ["source.identity.metadata", "source.identity.primary"]
        for item in split_states["use.result"]["mismatches"]
    ), split_states
    assert obsolete_lifecycle_rows(split_graph, projection()) == [
        {
            "capability": "source.identity",
            "artifact": "SOURCE",
            "acceptance_id": "ID1",
            "reason": "CAPABILITY_NOT_IN_ENGINEERING_GRAPH",
        }
    ]

    merged_graph = copy.deepcopy(GRAPH)
    merged_graph["authorities"][0]["produces"] = [
        {
            "capability": "source.combined",
            "knowledge_kind": "problem-evidence",
            "requires": [],
        }
    ]
    merged_graph["authorities"][1]["produces"][0]["requires"] = [
        "source.combined"
    ]
    merged_model = copy.deepcopy(MODEL)
    merged_model["artifacts"][0]["provides"] = ["source.combined"]
    merged_projection = {
        "version": 1,
        "kind": "harness-capability-lifecycle",
        "providers": [
            {
                "artifact": "SOURCE",
                "capability": "source.identity",
                "acceptance_id": "ID1",
                "accepted_prerequisites": {},
            },
            {
                "artifact": "SOURCE",
                "capability": "source.structure",
                "acceptance_id": "S1",
                "accepted_prerequisites": {},
            },
            {
                "artifact": "USE",
                "capability": "use.result",
                "acceptance_id": "U1",
                "accepted_prerequisites": {
                    "source.identity": "ID1",
                    "source.structure": "S1",
                },
            },
        ],
    }
    merged_states = lifecycle_states(
        merged_graph,
        merged_model,
        merged_projection,
    )
    assert merged_states["source.combined"]["state"] == "UNKNOWN", merged_states
    assert merged_states["use.result"]["state"] == "STALE", merged_states
    assert any(
        item.get("mode") == "PREREQUISITE_TOPOLOGY"
        and item.get("accepted_prerequisites")
        == ["source.identity", "source.structure"]
        and item.get("current_prerequisites") == ["source.combined"]
        for item in merged_states["use.result"]["mismatches"]
    ), merged_states
    assert obsolete_lifecycle_rows(merged_graph, merged_projection) == [
        {
            "capability": "source.identity",
            "artifact": "SOURCE",
            "acceptance_id": "ID1",
            "reason": "CAPABILITY_NOT_IN_ENGINEERING_GRAPH",
        },
        {
            "capability": "source.structure",
            "artifact": "SOURCE",
            "acceptance_id": "S1",
            "reason": "CAPABILITY_NOT_IN_ENGINEERING_GRAPH",
        },
    ]


def main() -> int:
    test_capability_question_granularity()
    test_split_merge_do_not_transfer_acceptance()
    result = evaluate_lifecycle_target(
        GRAPH, "IMPLEMENTATION", MODEL, projection()
    )
    assert result["status"] == "COMPLETE", result

    result = evaluate_lifecycle_target(
        GRAPH, "IMPLEMENTATION", MODEL, projection(identity="ID2")
    )
    assert result["status"] == "READY", result
    assert result["revalidate"][0]["capability"] == "use.result", result

    result = evaluate_lifecycle_target(
        GRAPH,
        "IMPLEMENTATION",
        MODEL,
        projection(identity="ID2", accepted="ID2"),
    )
    assert result["status"] == "COMPLETE", result

    missing = projection()
    missing["providers"] = [
        item
        for item in missing["providers"]
        if item["capability"] != "use.result"
    ]
    result = evaluate_lifecycle_target(
        GRAPH, "IMPLEMENTATION", MODEL, missing
    )
    assert result["status"] == "INCOMPLETE", result
    assert result["lifecycle_gaps"], result

    bad = projection()
    bad["providers"][1]["accepted_prerequisites"] = {}
    result = evaluate_lifecycle_target(
        GRAPH, "IMPLEMENTATION", MODEL, bad
    )
    assert result["status"] == "READY", result
    assert result["revalidate"], result
    assert any(
        item.get("mode") == "PREREQUISITE_TOPOLOGY"
        and item.get("accepted_prerequisites") == []
        and item.get("current_prerequisites") == ["source.identity"]
        for item in result["revalidate"][0]["lifecycle"]["mismatches"]
    ), result

    partial_semantic = projection(identity="ID2")
    partial_semantic["providers"][0]["semantic_atom_fingerprints"] = {
        "ATOM-A": "HASH-A-1",
        "ATOM-B": "HASH-B-2",
    }
    partial_semantic["providers"][1]["accepted_prerequisite_semantics"] = {
        "source.identity": {
            "semantic_atoms": {"ATOM-A": "HASH-A-1"},
        }
    }
    try:
        evaluate_lifecycle_target(
            GRAPH,
            "IMPLEMENTATION",
            MODEL,
            partial_semantic,
        )
    except CoreError:
        pass
    else:
        raise AssertionError(
            "non-exhaustive semantic lifecycle baseline must fail"
        )

    missing_surface = projection(identity="ID2", accepted="ID2")
    missing_surface["providers"][0]["semantic_atom_fingerprints"] = {
        "ATOM-A": "HASH-A-1",
    }
    missing_surface["providers"][1]["accepted_prerequisite_semantics"] = {
        "source.identity": {
            "exhaustive": True,
            "semantic_atoms": {"ATOM-A": "HASH-A-1"},
        }
    }
    try:
        evaluate_lifecycle_target(
            GRAPH,
            "IMPLEMENTATION",
            MODEL,
            missing_surface,
        )
    except CoreError:
        pass
    else:
        raise AssertionError(
            "exhaustive semantic baseline without source surface must fail"
        )

    renamed_graph = copy.deepcopy(GRAPH)
    source_production = renamed_graph["authorities"][0]["produces"][0]
    source_production["capability"] = "source.identity.v2"
    use_production = renamed_graph["authorities"][1]["produces"][0]
    use_production["requires"] = ["source.identity.v2"]

    evolved_states = lifecycle_states(
        renamed_graph,
        MODEL,
        projection(),
    )
    assert evolved_states["source.identity.v2"]["state"] == "UNKNOWN", evolved_states
    assert evolved_states["use.result"]["state"] == "STALE", evolved_states
    assert any(
        item.get("mode") == "PREREQUISITE_TOPOLOGY"
        and item.get("accepted_prerequisites") == ["source.identity"]
        and item.get("current_prerequisites") == ["source.identity.v2"]
        for item in evolved_states["use.result"]["mismatches"]
    ), evolved_states
    assert obsolete_lifecycle_rows(renamed_graph, projection()) == [
        {
            "capability": "source.identity",
            "artifact": "SOURCE",
            "acceptance_id": "ID1",
            "reason": "CAPABILITY_NOT_IN_ENGINEERING_GRAPH",
        }
    ]

    policy_bound = projection()
    policy_bound["providers"][0]["acceptance_policy_fingerprint"] = "sha256:source-policy-v1"
    policy_bound["providers"][1]["acceptance_policy_fingerprint"] = "sha256:use-policy-v1"
    policy_states = lifecycle_states(
        GRAPH,
        MODEL,
        policy_bound,
        current_acceptance_policy_fingerprints={
            "source.identity": "sha256:source-policy-v2",
            "use.result": "sha256:use-policy-v1",
        },
    )
    assert policy_states["source.identity"]["state"] == "STALE", policy_states
    assert any(
        item.get("mode") == "ACCEPTANCE_POLICY"
        for item in policy_states["source.identity"]["mismatches"]
    ), policy_states
    assert policy_states["use.result"]["state"] == "STALE", policy_states

    print(
        "capability lifecycle: PASS "
        "(CURRENT/STALE/UNKNOWN + policy-bound REVALIDATE)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
