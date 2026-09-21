#!/usr/bin/env python3
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))

from coverage_obligations import derive_subject_obligation_rows


PROOF={
    "proofs":{
        "interface.human.journeys":{
            "accepted_semantic_claims":["engineering.interface.human.journeys"]
        }
    }
}

GRAPH={
    "version":1,
    "kind":"harness-engineering-graph",
    "id":"OBLIGATION-FIXTURE",
    "authorities":[
        {
            "id":"INTERFACE-DESIGN",
            "produces":[
                {
                    "capability":"fixture.ui.resource",
                    "requires":[],
                    "semantic_claims":[
                        {"claim":"engineering.interface.human.journeys","subject":"Resource"}
                    ],
                },
                {
                    "capability":"fixture.ui.application",
                    "requires":[],
                    "semantic_claims":[
                        {"claim":"engineering.interface.human.journeys","subject":"Application"}
                    ],
                },
                {
                    "capability":"fixture.ui.broad",
                    "requires":[],
                    "semantic_claims":["engineering.interface.human.journeys"],
                },
                {
                    "capability":"fixture.cli",
                    "requires":[],
                    "semantic_claims":[
                        {"claim":"engineering.interface.human.journeys","subject":"CLI"}
                    ],
                },
            ],
        }
    ],
    "consumers":[
        {
            "id":"FRONTEND-IMPLEMENTATION",
            "requires":[
                {"capability":"fixture.ui.resource"},
                {"capability":"fixture.ui.application"},
                {"capability":"fixture.ui.broad"},
            ],
        },
        {
            "id":"CLI-IMPLEMENTATION",
            "requires":[{"capability":"fixture.cli"}],
        },
    ],
}

SOURCE={
    "content":{
        "requirements":[
            {"id":"REQ-RESOURCE","status":"ACCEPTED"},
            {"id":"REQ-APPLICATION","status":"ACCEPTED"},
        ]
    }
}

BINDINGS={"bindings":[]}


def realization(*caps):
    return {
        "artifacts":[
            {"id":f"A-{i}","provides":[cap]}
            for i,cap in enumerate(caps)
        ]
    }


def obligations(application_state="REQUIRED"):
    app={
        "subject":"Application",
        "concerns":["interface.human.journeys"],
        "requirement_refs":["REQ-APPLICATION"],
        "state":application_state,
    }
    if application_state!="REQUIRED":
        app["rationale"]="fixture disposition"
    return {
        "version":1,
        "kind":"harness-coverage-subject-obligations",
        "consumer":"FRONTEND-IMPLEMENTATION",
        "scope":"mvp",
        "subjects":[
            {
                "subject":"Resource",
                "concerns":["interface.human.journeys"],
                "requirement_refs":["REQ-RESOURCE"],
            },
            app,
        ],
        "excluded_requirements":[],
    }


def run(ob, source=SOURCE, realized=("fixture.ui.resource","fixture.ui.broad")):
    return derive_subject_obligation_rows(
        obligations=ob,
        source=source,
        graph=GRAPH,
        project_docs=[GRAPH,realization(*realized)],
        proof_contract=PROOF,
        capability_bindings=BINDINGS,
        consumer="FRONTEND-IMPLEMENTATION",
        scope="mvp",
    )


def main():
    partial=run(obligations())
    by_subject={r.get("subject"):r for r in partial["rows"] if r.get("subject")!="__accepted_scope__"}
    assert not partial["completion_ready"]
    assert by_subject["Resource"]["state"]=="COVERED"
    assert by_subject["Application"]["state"]=="MISSING"
    # Broad subjectless proof must not close a required subject.
    assert by_subject["Application"]["action"]=="PRODUCE_CAPABILITY"

    assert run(obligations("NOT_APPLICABLE"))["completion_ready"]
    assert run(obligations("DEFERRED"))["completion_ready"]

    both=run(
        obligations(),
        realized=("fixture.ui.resource","fixture.ui.application","fixture.ui.broad"),
    )
    assert both["completion_ready"]
    states=[r["state"] for r in both["rows"] if r["concern"]=="interface.human.journeys"]
    assert states==["COVERED","COVERED"]

    # Upstream accepted-scope growth invalidates the result until classified.
    changed={
        "content":{
            "requirements":SOURCE["content"]["requirements"]+
            [{"id":"REQ-NEW","status":"ACCEPTED"}]
        }
    }
    stale=run(obligations(),source=changed,realized=("fixture.ui.resource","fixture.ui.application"))
    meta=[r for r in stale["rows"] if r["concern"]=="meta.subject-inventory"]
    assert meta and meta[0]["state"]=="MISSING"
    assert meta[0]["requirement_refs"]==["REQ-NEW"]

    # Consumer isolation: frontend obligations cannot be proven by a CLI-only capability.
    isolated=derive_subject_obligation_rows(
        obligations={
            "version":1,
            "kind":"harness-coverage-subject-obligations",
            "consumer":"CLI-IMPLEMENTATION",
            "scope":"mvp",
            "subjects":[{
                "subject":"Resource",
                "concerns":["interface.human.journeys"],
                "requirement_refs":["REQ-RESOURCE"],
            }],
            "excluded_requirements":[{
                "requirement":"REQ-APPLICATION",
                "rationale":"not part of CLI fixture",
            }],
        },
        source=SOURCE,
        graph=GRAPH,
        project_docs=[GRAPH,realization("fixture.ui.resource","fixture.cli")],
        proof_contract=PROOF,
        capability_bindings=BINDINGS,
        consumer="CLI-IMPLEMENTATION",
        scope="mvp",
    )
    resource=[r for r in isolated["rows"] if r.get("subject")=="Resource"][0]
    assert resource["state"]=="MISSING"

    print("subject obligation coverage: ok")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
