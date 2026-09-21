#!/usr/bin/env python3
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))

from coverage_planner_experiment import derive_plan, load

def run(core_name):
    return derive_plan(
        load(str(ROOT/"spec/research/concern-semantic-proof-contract-v1.yaml")),
        load(str(ROOT/"spec/research/authority-role-contract-v1.yaml")),
        load(str(ROOT/"spec/research/subject-coverage-fixture-roles.yaml")),
        {"version":1,"kind":"harness-semantic-claim-bindings","bindings":[]},
        {
            "project":"SUBJECT-COVERAGE-FIXTURE",
            "scope":"all",
            "required":["domain.model"],
            "decisions":[],
        },
        [
            load(str(ROOT/"spec/research/subject-coverage-fixture-graph.yaml")),
            load(str(ROOT/f"spec/research/{core_name}")),
        ],
        "IMPLEMENTATION",
    )

def main():
    partial=run("subject-coverage-fixture-core-partial.yaml")
    complete=run("subject-coverage-fixture-core-complete.yaml")

    p={r["concern"]:r for r in partial["rows"]}["domain.model"]
    c={r["concern"]:r for r in complete["rows"]}["domain.model"]

    assert p["state"] == "MISSING"
    assert {x["subject"] for x in p["covered_instances"]} == {"BC-A"}
    assert {x["subject"] for x in p["missing_instances"]} == {"BC-B"}

    assert c["state"] == "COVERED"
    assert {x["subject"] for x in c["proof_instances"]} == {"BC-A","BC-B"}

    print("subject-scoped coverage proof: ok")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
