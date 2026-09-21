#!/usr/bin/env python3
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))

from concern_activation_experiment import derive_activation, load

def run(consumer):
    return derive_activation(
        load(str(ROOT/"spec/research/concern-activation-policy-v1.yaml")),
        load(str(ROOT/"spec/research/consumer-activation-fixture-roles.yaml")),
        {
            "version":1,
            "kind":"harness-concern-activation-overlay",
            "project":"CONSUMER-ACTIVATION-FIXTURE",
            "scope":consumer.lower(),
            "activate":[
                {
                    "concern":"governance.data",
                    "rationale":"Shared project fact.",
                    "consumers":["BACKEND","FRONTEND"],
                },
                {
                    "concern":"quality.performance.latency",
                    "rationale":"Frontend-only interaction concern.",
                    "consumers":["FRONTEND"],
                },
            ],
            "decisions":[],
        },
        [load(str(ROOT/"spec/research/consumer-activation-fixture-graph.yaml"))],
        consumer,
    )

def main():
    backend=run("BACKEND")
    frontend=run("FRONTEND")
    b={r["concern"] for r in backend["rows"]}
    f={r["concern"] for r in frontend["rows"]}

    assert "data.lifecycle" in b
    assert "interface.human.accessibility" not in b
    assert "security.threat-analysis" not in b

    assert "interface.human.accessibility" in f
    assert "security.threat-analysis" in f
    assert "data.lifecycle" not in f

    assert "architecture.structure" in b and "architecture.structure" in f
    assert "delivery.release" in b and "delivery.release" in f
    assert "governance.data" in b and "governance.data" in f
    assert "quality.performance.latency" not in b
    assert "quality.performance.latency" in f

    print(f"consumer scoped activation: backend={backend['activated_count']} frontend={frontend['activated_count']}")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
