#!/usr/bin/env python3
"""Research-only acceptance for derived Engineering Coverage."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from coverage_derivation_experiment import derive, load, remaining_work

def main() -> int:
    catalog = load(str(ROOT / "spec/research/engineering-concerns-v1.yaml"))
    mapping = load(str(ROOT / "spec/research/concern-evidence-mapping-v1.yaml"))
    overlay = load(str(ROOT / "spec/research/coverage-derivation-fixture-overlay.yaml"))
    knowledge = [load(str(ROOT / "spec/research/coverage-derivation-fixture-knowledge.yaml"))]

    result = derive(catalog, mapping, knowledge, overlay)
    rows = {row["concern"]: row for row in result["rows"]}

    assert rows["operability.logging"]["state"] == "COVERED"
    assert rows["interface.human.accessibility"]["state"] == "NOT_APPLICABLE"
    assert rows["data.classification"]["state"] == "MISSING"
    assert rows["reliability.recovery"]["state"] == "MISSING"
    assert rows["security.threat-analysis"]["state"] == "UNASSESSED"
    assert not rows["security.threat-analysis"]["attention_required"]

    remaining = {row["concern"] for row in remaining_work(result)}
    assert "data.classification" in remaining
    assert "reliability.recovery" in remaining
    assert "security.threat-analysis" not in remaining

    print("derived engineering coverage experiment: ok")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
