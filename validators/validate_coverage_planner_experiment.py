#!/usr/bin/env python3
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from coverage_planner_experiment import capability_realization, derive_plan, load

def test_capability_question_granularity() -> None:
    graph = {
        "kind": "harness-engineering-graph",
        "authorities": [
            {
                "id": "PRODUCT",
                "produces": [
                    {"capability": "demo.intent", "requires": []},
                    {"capability": "demo.acceptance", "requires": []},
                ],
            },
            {
                "id": "APPLICATION",
                "produces": [
                    {
                        "capability": "demo.application",
                        "requires": ["demo.acceptance"],
                    }
                ],
            },
        ],
    }
    realization = {
        "artifacts": [
            {
                "id": "REQUIREMENTS",
                "provides": ["demo.intent", "demo.acceptance"],
                "depends_on": [],
            },
            {
                "id": "APPLICATION",
                "provides": ["demo.application"],
                "depends_on": ["REQUIREMENTS"],
            },
        ],
        "questions": [
            {
                "id": "Q-ACCEPTANCE",
                "blocks_capabilities": ["demo.acceptance"],
            }
        ],
    }
    result = capability_realization([graph, realization])
    assert "demo.intent" in result["usable"], result
    assert result["blocked"]["demo.acceptance"] == ["Q-ACCEPTANCE"], result
    assert result["blocked"]["demo.application"] == ["Q-ACCEPTANCE"], result


def main() -> int:
    test_capability_question_granularity()
    result = derive_plan(
        load(str(ROOT / "spec/research/concern-semantic-proof-contract-v1.yaml")),
        load(str(ROOT / "spec/research/authority-role-contract-v1.yaml")),
        load(str(ROOT / "spec/research/coverage-planner-fixture-authorities.yaml")),
        load(str(ROOT / "spec/research/coverage-planner-fixture-claims.yaml")),
        load(str(ROOT / "spec/research/coverage-derivation-fixture-overlay.yaml")),
        [load(str(ROOT / "spec/research/coverage-derivation-fixture-knowledge.yaml"))],
    )
    rows = {x["concern"]: x for x in result["rows"]}
    assert rows["reliability.recovery"]["state"] == "MISSING"
    assert rows["reliability.recovery"]["routes"]["engineering.reliability.recovery"] == ["RELIABILITY"]
    assert rows["data.classification"]["state"] == "MISSING"
    assert rows["data.classification"]["routes"]["engineering.data.classification"] == ["DATA"]
    print("coverage planner experiment: ok")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
