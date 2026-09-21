#!/usr/bin/env python3
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))

from coverage_control_loop_experiment import evaluate, load

def main() -> int:
    result=evaluate(
        load(str(ROOT/"spec/research/concern-activation-policy-v1.yaml")),
        load(str(ROOT/"spec/research/concern-semantic-proof-contract-v1.yaml")),
        load(str(ROOT/"spec/research/authority-role-contract-v1.yaml")),
        load(str(ROOT/"spec/research/coverage-planner-fixture-authorities.yaml")),
        load(str(ROOT/"spec/research/coverage-planner-fixture-claims.yaml")),
        load(str(ROOT/"spec/research/concern-activation-fixture-overlay.yaml")),
        [load(str(ROOT/"spec/research/coverage-derivation-fixture-knowledge.yaml"))],
    )
    rows={r["concern"]:r for r in result["rows"]}
    assert not result["completion_ready"]
    assert rows["data.classification"]["state"] == "MISSING"
    assert rows["data.classification"]["routes"]["engineering.data.classification"] == ["DATA"]
    assert rows["governance.privacy"]["state"] == "BLOCKED"
    assert rows["governance.privacy"]["action"] == "ASSIGN_AUTHORITY"
    assert rows["intent.behavior"]["activation_provenance"][0]["source"] == "BASELINE"
    print("coverage control loop experiment: ok")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
