#!/usr/bin/env python3
from copy import deepcopy
from pathlib import Path
import sys, yaml
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from frontend_interface_knowledge import evaluate_frontend_ux_closure, required_screen_ids
from frontend_screen_contracts import evaluate_frontend_screen_contracts
from agent_router import load_yaml, route_create_work
from engineering_graph import evaluate_engineering_target, validate_engineering_graph

BASE=ROOT/"examples"/"frontend-ux-closure"
EX=BASE/"canonical"
GRAPH=load_yaml(BASE/"engineering-graph.yaml")
REGISTRY=load_yaml(ROOT/"skills"/"artifact-skill-registry-v0.yaml")
def load(p): return yaml.safe_load(p.read_text(encoding="utf-8"))
def codes(r): return {x["code"] for x in r["findings"]}

def main():
    validate_engineering_graph(GRAPH)
    expected=[
        ("core-state-empty.yaml",{("task-model","APPLICATION-DESIGN")}),
        ("core-state-with-task.yaml",{("user-journey-design","APPLICATION-DESIGN")}),
        ("core-state-with-journeys.yaml",{("conceptual-interface-model","HUMAN-INTERFACE-DESIGN")}),
        ("core-state-with-conceptual.yaml",{
            ("information-architecture-design","HUMAN-INTERFACE-DESIGN"),
            ("interaction-design","HUMAN-INTERFACE-DESIGN"),
        }),
        ("core-state-with-ia-interaction.yaml",{("interface-topology-design","HUMAN-INTERFACE-DESIGN")}),
        ("core-state-with-topology.yaml",{
            ("presentation-system-design","HUMAN-INTERFACE-DESIGN"),
            ("verification-strategy","VERIFICATION-DESIGN"),
        }),
        ("core-state-with-foundations.yaml",{("screen-view-design","HUMAN-INTERFACE-DESIGN")}),
        ("core-state-with-screen.yaml",{("verification-strategy","VERIFICATION-DESIGN")}),
        ("core-state-with-verification.yaml",{("implementation-design","IMPLEMENTATION-DESIGN")}),
    ]
    for filename,want in expected:
        routed=route_create_work(GRAPH,"FRONTEND-IMPLEMENTATION",load_yaml(BASE/filename),REGISTRY)
        got={(x["knowledge_kind"],x["authority"]) for x in routed["routed"]}
        assert got==want,(filename,got,routed)
        assert not routed["unrouted"],(filename,routed["unrouted"])
    complete=evaluate_engineering_target(GRAPH,"FRONTEND-IMPLEMENTATION",load_yaml(BASE/"core-state-complete.yaml"))
    assert complete["status"]=="COMPLETE",complete

    task=load(EX/"task-model.yaml")
    conceptual=load(EX/"conceptual-interface-model.yaml")
    ia=load(EX/"information-architecture.yaml")
    interaction=load(EX/"interaction-design.yaml")
    topology=load(EX/"interface-topology.yaml")
    result=evaluate_frontend_ux_closure(task,conceptual,ia,interaction,topology)
    assert result["status"]=="ACCEPTED",result
    assert set(result["required_screen_ids"])=={"RESOURCE-CATALOGUE","RESOURCE-DETAIL"}

    bad=deepcopy(interaction)
    bad["contexts"]=[x for x in bad["contexts"] if x["id"]!="RESOURCE-DETAIL-CONTEXT"]
    r=evaluate_frontend_ux_closure(task,conceptual,ia,bad,topology)
    assert "UNCOVERED_USER_TASK" in codes(r),r

    bad_top=deepcopy(topology)
    bad_top["views"]=[x for x in bad_top["views"] if x["id"]!="RESOURCE-DETAIL"]
    r=evaluate_frontend_ux_closure(task,conceptual,ia,interaction,bad_top)
    assert "UNMAPPED_INTERACTION_CONTEXT" in codes(r),r
    assert "USER_TASK_WITHOUT_VIEW" in codes(r),r

    bad_ia=deepcopy(ia)
    bad_ia["locations"][0]["concept_refs"]=["UNKNOWN"]
    r=evaluate_frontend_ux_closure(task,conceptual,bad_ia,interaction,topology)
    assert "UNKNOWN_CONCEPT_REF" in codes(r),r

    presentation=load(ROOT/"examples"/"user-facing-application"/"canonical"/"example-presentation-system.yaml")
    screens=load(ROOT/"examples"/"user-facing-application"/"canonical"/"example-screen-view-design.yaml")
    r=evaluate_frontend_screen_contracts(presentation,screens,None,screen_ids=required_screen_ids(topology))
    assert "MISSING_REQUIRED_SCREEN" not in codes(r),r

    missing=deepcopy(screens)
    missing["screens"]=[x for x in missing["screens"] if x["id"]!="RESOURCE-DETAIL"]
    r=evaluate_frontend_screen_contracts(presentation,missing,None,screen_ids=required_screen_ids(topology))
    assert "MISSING_REQUIRED_SCREEN" in codes(r),r
    print("frontend UX closure: PASS")
    return 0
if __name__=="__main__":
    raise SystemExit(main())
