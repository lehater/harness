#!/usr/bin/env python3
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))

from coverage_planner_experiment import derive_plan, load

def run(consumer):
    return derive_plan(
        load(str(ROOT/"spec/research/concern-semantic-proof-contract-v1.yaml")),
        load(str(ROOT/"spec/research/authority-role-contract-v1.yaml")),
        load(str(ROOT/"spec/research/consumer-activation-fixture-roles.yaml")),
        {"version":1,"kind":"harness-semantic-claim-bindings","bindings":[]},
        {
            "project":"CONSUMER-ACTIVATION-FIXTURE",
            "scope":consumer.lower(),
            "required":[
                "data.model",
                "interface.human.accessibility",
            ],
            "decisions":[],
        },
        [
            load(str(ROOT/"spec/research/consumer-activation-fixture-graph.yaml")),
            load(str(ROOT/"spec/research/consumer-activation-fixture-core.yaml")),
        ],
        consumer,
    )

def main():
    backend=run("BACKEND")
    frontend=run("FRONTEND")
    b={r["concern"]:r for r in backend["rows"]}
    f={r["concern"]:r for r in frontend["rows"]}

    assert b["data.model"]["state"] == "COVERED"
    assert b["interface.human.accessibility"]["state"] == "MISSING"

    assert f["interface.human.accessibility"]["state"] == "COVERED"
    assert f["data.model"]["state"] == "MISSING"

    print("consumer scoped proof: ok")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
