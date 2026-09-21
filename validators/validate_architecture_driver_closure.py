#!/usr/bin/env python3
from copy import deepcopy
from pathlib import Path
import sys
import yaml

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))

from architecture_driver_closure import BASELINE_CONCERNS, evaluate


def load(path):
    with open(path,"r",encoding="utf-8") as stream:
        return yaml.safe_load(stream)


def main():
    contract=load(ROOT/"spec/architecture-driver-closure/contract-v1.yaml")
    simple=load(ROOT/"spec/architecture-driver-closure/simple-batch.yaml")

    assert contract["ownership"]["authority"]=="SYSTEM-ARCHITECTURE"
    assert "smallest-satisfying-architecture" in contract["principles"]
    assert set(contract["baseline_concerns"])==set(BASELINE_CONCERNS)

    result=evaluate(simple)
    assert result["complete"], result

    missing=deepcopy(simple)
    missing["drivers"]=[d for d in missing["drivers"] if d["concern"]!="availability"]
    missing_result=evaluate(missing)
    assert not missing_result["complete"]
    assert {"code":"DRIVER_UNCLASSIFIED","concern":"availability"} in missing_result["errors"]

    questioned=deepcopy(simple)
    for d in questioned["drivers"]:
        if d["concern"]=="growth-horizon":
            d.clear()
            d.update({
                "concern":"growth-horizon",
                "state":"QUESTION",
                "architecture_impact":"material",
                "rationale":"future scale can change topology",
                "question":"Q-GROWTH-HORIZON",
            })
    questioned_result=evaluate(questioned)
    assert not questioned_result["complete"]
    codes={e["code"] for e in questioned_result["errors"]}
    assert "UNRESOLVED_DRIVER_QUESTION" in codes

    deferred=deepcopy(simple)
    for d in deferred["drivers"]:
        if d["concern"]=="latency-freshness":
            d.clear()
            d.update({
                "concern":"latency-freshness",
                "state":"DEFERRED",
                "architecture_impact":"material",
                "rationale":"unknown for now",
            })
    deferred_result=evaluate(deferred)
    assert not deferred_result["complete"]
    assert "MATERIAL_DRIVER_DEFERRED" in {e["code"] for e in deferred_result["errors"]}

    harmless=deepcopy(simple)
    for d in harmless["drivers"]:
        if d["concern"]=="growth-horizon":
            d.clear()
            d.update({
                "concern":"growth-horizon",
                "state":"DEFERRED",
                "architecture_impact":"none",
                "rationale":"accepted MVP has no growth-sensitive topology decision",
            })
    harmless_result=evaluate(harmless)
    assert harmless_result["complete"], harmless_result

    print("architecture driver closure: ok (positive + missing/question/material-deferred regressions)")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
