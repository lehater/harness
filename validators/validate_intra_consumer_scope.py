#!/usr/bin/env python3
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))

from concern_activation_experiment import derive_activation, load
from coverage_planner_experiment import derive_plan

GRAPH=ROOT/"spec/research/scope-activation-fixture-graph.yaml"
ROLES=ROOT/"spec/research/scope-activation-fixture-roles.yaml"
CORE=ROOT/"spec/research/scope-activation-fixture-core.yaml"

def activation(root):
    return derive_activation(
        load(str(ROOT/"spec/research/concern-activation-policy-v1.yaml")),
        load(str(ROLES)),
        {
            "project":"SCOPE-ACTIVATION-FIXTURE",
            "scope":"selected",
            "scope_roots":[root],
            "activate":[],
            "decisions":[],
        },
        [load(str(GRAPH))],
        "IMPLEMENTATION",
    )

def plan(root, required):
    return derive_plan(
        load(str(ROOT/"spec/research/concern-semantic-proof-contract-v1.yaml")),
        load(str(ROOT/"spec/research/authority-role-contract-v1.yaml")),
        load(str(ROLES)),
        {"version":1,"kind":"harness-semantic-claim-bindings","bindings":[]},
        {
            "project":"SCOPE-ACTIVATION-FIXTURE",
            "scope":"selected",
            "scope_roots":[root],
            "required":required,
            "decisions":[],
        },
        [load(str(GRAPH)),load(str(CORE))],
        "IMPLEMENTATION",
    )

def main():
    mvp=activation("fixture.mvp.implementation-design")
    later=activation("fixture.later.implementation-design")
    ms={r["concern"] for r in mvp["rows"]}
    ls={r["concern"] for r in later["rows"]}

    assert "data.lifecycle" in ms
    assert "interface.human.accessibility" not in ms
    assert "interface.human.accessibility" in ls
    assert "data.lifecycle" not in ls

    mp={r["concern"]:r for r in plan(
        "fixture.mvp.implementation-design",
        ["data.model","interface.human.accessibility"],
    )["rows"]}
    lp={r["concern"]:r for r in plan(
        "fixture.later.implementation-design",
        ["data.model","interface.human.accessibility"],
    )["rows"]}

    assert mp["data.model"]["state"] == "COVERED"
    assert mp["interface.human.accessibility"]["state"] == "MISSING"
    assert lp["interface.human.accessibility"]["state"] == "COVERED"
    assert lp["data.model"]["state"] == "MISSING"

    try:
        activation("fixture.not-in-consumer")
    except ValueError:
        pass
    else:
        raise AssertionError("scope root outside Consumer closure must fail")

    print(f"intra-consumer scope: mvp={mvp['activated_count']} later={later['activated_count']}")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
