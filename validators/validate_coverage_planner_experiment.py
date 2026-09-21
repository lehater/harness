#!/usr/bin/env python3
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from coverage_planner_experiment import derive_plan, load

def main() -> int:
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
