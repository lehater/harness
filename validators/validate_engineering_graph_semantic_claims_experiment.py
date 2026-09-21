#!/usr/bin/env python3
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from engineering_graph import validate_engineering_graph, production_index

def main() -> int:
    graph = {
        "version": 1,
        "kind": "harness-engineering-graph",
        "id": "SEMANTIC-CLAIM-FIXTURE",
        "authorities": [
            {
                "id": "DATA",
                "responsibility": "Own data decisions.",
                "boundary": {
                    "semantic_cohesion": "Data decisions.",
                    "independent_change": "Data decisions can change independently.",
                    "public_contract": "Produces accepted data knowledge.",
                },
                "produces": [
                    {
                        "capability": "fixture.data-design",
                        "semantic_claims": [
                            "engineering.data.model",
                            {
                                "claim": "engineering.data.classification",
                                "subject": "CUSTOMER-DATA",
                            },
                        ],
                        "requires": [],
                    },
                    {
                        "capability": "fixture.coverage-only",
                        "semantic_claims": [
                            "engineering.data.lifecycle",
                        ],
                        "requires": [],
                    },
                ],
            }
        ],
        "consumers": [
            {
                "id": "IMPLEMENTATION",
                "purpose": "Consume accepted data design.",
                "requires": ["fixture.data-design"],
            }
        ],
        "terminal_capabilities": [],
    }

    validate_engineering_graph(graph)
    production = production_index(graph)["fixture.data-design"]
    assert "fixture.coverage-only" in production_index(graph)
    assert production["semantic_claims"] == [
        {"claim": "engineering.data.model"},
        {
            "claim": "engineering.data.classification",
            "subject": "CUSTOMER-DATA",
        },
    ]

    bad = {
        **graph,
        "authorities": [
            {
                **graph["authorities"][0],
                "produces": [
                    {
                        "capability": "fixture.data-design",
                        "semantic_claims": [
                            "engineering.data.model",
                            {"claim": "engineering.data.model"},
                        ],
                        "requires": [],
                    }
                ],
            }
        ],
    }
    try:
        validate_engineering_graph(bad)
    except Exception:
        pass
    else:
        raise AssertionError("duplicate semantic claims must be rejected")

    print("engineering graph semantic claims experiment: ok")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
