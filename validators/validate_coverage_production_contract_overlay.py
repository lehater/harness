#!/usr/bin/env python3
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))

from engineering_coverage import evaluate_with_repository_policy, load


def main():
    graph=load(ROOT/"spec/research/scope-activation-fixture-graph.yaml")
    core=load(ROOT/"spec/research/scope-activation-fixture-core.yaml")

    result=evaluate_with_repository_policy(
        graph=graph,
        realization=core,
        consumer="IMPLEMENTATION",
        scope="mvp",
        scope_roots=["fixture.mvp.implementation-design"],
        project_overlay={
            "activate":[
                {
                    "concern":"data.lifecycle",
                    "rationale":"Fixture requires explicit data lifecycle.",
                }
            ],
            "decisions":[],
        },
        production_contract_overlay={
            "version":1,
            "kind":"harness-production-contract-overlay",
            "productions":[
                {
                    "authority":"DATA-DESIGN",
                    "capability":"fixture.mvp.data-lifecycle-design",
                    "semantic_claims":["engineering.data.lifecycle"],
                    "requires":["fixture.mvp.data-design"],
                }
            ],
        },
    )

    rows={row["concern"]:row for row in result["rows"]}
    lifecycle=rows["data.lifecycle"]

    assert lifecycle["state"] == "MISSING"
    assert lifecycle["action"] == "PRODUCE_CAPABILITY"
    assert lifecycle["ready_production_candidates"] == [
        {
            "claim":"engineering.data.lifecycle",
            "capability":"fixture.mvp.data-lifecycle-design",
            "authority":"DATA-DESIGN",
            "requires":["fixture.mvp.data-design"],
            "missing_prerequisites":[],
            "questions":[],
            "ready":True,
        }
    ]

    items=[
        item for item in result["work_items"]
        if item.get("capability")=="fixture.mvp.data-lifecycle-design"
    ]
    assert len(items)==1
    assert items[0]["authority"]=="DATA-DESIGN"
    assert items[0]["concerns"]==["data.lifecycle"]

    # The new Coverage-only capability must not become an activation signal.
    assert "fixture.mvp.data-lifecycle-design" not in result["activation_signals"]["capabilities"]

    print("production contract overlay: ok")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
