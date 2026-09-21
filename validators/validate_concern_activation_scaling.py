#!/usr/bin/env python3
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))

from concern_activation_experiment import derive_activation, load

def run(example):
    return derive_activation(
        load(str(ROOT/"spec/research/concern-activation-policy-v1.yaml")),
        load(str(ROOT/f"examples/{example}/concern-role-bindings.research.yaml")),
        load(str(ROOT/f"examples/{example}/concern-activation-overlay.research.yaml")),
        [load(str(ROOT/f"examples/{example}/engineering-graph.yaml"))],
    )

def main() -> int:
    cli=run("greenfield-csv-deduplicator")
    ui=run("user-facing-application")

    cli_set={r["concern"] for r in cli["rows"]}
    ui_set={r["concern"] for r in ui["rows"]}

    assert cli["activated_count"] == 17, cli["activated_count"]
    assert ui["activated_count"] == 50, ui["activated_count"]
    assert "security.threat-analysis" not in cli_set
    assert "data.lifecycle" not in cli_set
    assert "operability.metrics" not in cli_set
    assert "interface.machine.contract" in cli_set
    assert "delivery.release" in cli_set

    assert "interface.human.accessibility" in ui_set
    assert "security.threat-analysis" in ui_set
    assert "quality.performance.latency" in ui_set
    assert "operability.health" in ui_set
    assert "data.lifecycle" not in ui_set

    assert cli["activated_count"] < ui["activated_count"]
    print(f"activation scaling: cli={cli['activated_count']} user-facing={ui['activated_count']}")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
