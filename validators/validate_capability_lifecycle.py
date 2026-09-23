#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import copy
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from capability_lifecycle import evaluate_lifecycle_target
from harness import CoreError


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


def main() -> int:
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
    try:
        evaluate_lifecycle_target(GRAPH, "IMPLEMENTATION", MODEL, bad)
    except CoreError:
        pass
    else:
        raise AssertionError("invalid lifecycle baseline must fail")

    print("capability lifecycle: PASS (CURRENT/STALE/UNKNOWN + REVALIDATE)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
