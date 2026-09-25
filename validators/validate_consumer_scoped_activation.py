#!/usr/bin/env python3
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))

from concern_activation import derive_activation, load

def run(consumer):
    return derive_activation(
        load(str(ROOT/"spec/engineering-coverage/activation-policy-v1.yaml")),
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
    # Implementation structure is derived from implementation-design in the
    # Consumer closure, not from a naming convention in the Consumer id.
    assert "engineering.components" in b and "engineering.components" in f
    assert "engineering.principles" in b and "engineering.principles" in f
    assert "engineering.code-quality" in b and "engineering.code-quality" in f
    assert "delivery.release" in b and "delivery.release" in f
    assert "governance.data" in b and "governance.data" in f
    assert "quality.performance.latency" not in b
    assert "quality.performance.latency" in f

    # Regression: frontend applicability must not depend on already-existing
    # human-interface design knowledge. The Consumer itself is an independent signal.
    frontend_without_ui={
        "version":1,
        "kind":"harness-engineering-graph",
        "id":"FRONTEND-WITHOUT-UI",
        "authorities":[
            {
                "id":"PRODUCT",
                "produces":[
                    {"capability":"fixture.requirements","requires":[]},
                ],
            },
            {
                "id":"IMPLEMENTATION-DESIGN",
                "produces":[
                    {
                        "capability":"fixture.frontend.implementation-design",
                        "knowledge_kind":"implementation-design",
                        "requires":[{"capability":"fixture.requirements"}],
                    },
                ],
            },
        ],
        "consumers":[
            {
                "id":"FRONTEND-IMPLEMENTATION",
                "requires":[{"capability":"fixture.frontend.implementation-design"}],
            },
        ],
    }
    missing_ui=derive_activation(
        load(str(ROOT/"spec/engineering-coverage/activation-policy-v1.yaml")),
        {"bindings":{}},
        {
            "project":"FRONTEND-WITHOUT-UI",
            "scope":"mvp",
            "activate":[],
            "decisions":[],
        },
        [frontend_without_ui],
        "FRONTEND-IMPLEMENTATION",
    )
    missing_ui_concerns={r["concern"] for r in missing_ui["rows"]}
    assert "interface.human.journeys" in missing_ui_concerns
    assert "interface.human.usability" in missing_ui_concerns
    assert "interface.human.accessibility" in missing_ui_concerns
    assert "verification.interface.human" in missing_ui_concerns

    print(f"consumer scoped activation: backend={backend['activated_count']} frontend={frontend['activated_count']}")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
