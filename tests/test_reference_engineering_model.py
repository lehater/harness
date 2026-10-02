#!/usr/bin/env python3
from __future__ import annotations
import copy,sys
from pathlib import Path
from typing import Any
import yaml
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT))
from harness.project_model.engineering_graph import validate_engineering_graph
from harness.reference_model.reference_materializer import load_yaml,materialize,validate_reference_model
MODEL=ROOT/"spec/research/reference-engineering-model-v0.yaml"; AUTHORITIES=ROOT/"catalogs/software-authorities-v0.yaml"; PROOF=ROOT/"spec/engineering-coverage/semantic-proof-contract-v1.yaml"
HOLDOUTS=ROOT/"spec/research/reference-materializer-fixtures/holdouts-v0.yaml"; HOLDOUTS_V1=ROOT/"spec/research/reference-materializer-fixtures/holdouts-v1.yaml"; REGRESSIONS=ROOT/"spec/research/reference-materializer-fixtures/regressions-v0.yaml"
def load(path):
    v=yaml.safe_load(path.read_text(encoding="utf-8")) or {}; assert isinstance(v,dict),path; return v
def required(r): return {x["template"] for x in r.get("template_status",[]) or [] if x.get("status")=="REQUIRED"}
def codes(r): return {x["code"] for x in r.get("diagnostics",[]) or []}
def run_holdouts(model,authorities,proof,path):
    suite=load(path); assert suite["kind"]=="harness-reference-materializer-fixtures"
    for s in suite["scenarios"]:
        r=materialize(model,authorities,proof,s["project_facts"],s["request"]); e=s["expect"]; assert r["status"]==e["status"],(s["id"],r)
        actual=required(r); assert set(e.get("required_templates",[]))<=actual,(s["id"],actual); assert not(set(e.get("forbidden_templates",[]))&actual),(s["id"],actual)
        if r["status"]=="STABLE":
            validate_engineering_graph(r["graph"]); again=materialize(model,authorities,proof,s["project_facts"],s["request"]); assert again==r,s["id"]
            rev=copy.deepcopy(s["project_facts"]); rev["facts"]=list(reversed(rev["facts"])); assert materialize(model,authorities,proof,rev,s["request"])==r,s["id"]
def run_mutations(model,authorities,proof):
    base=copy.deepcopy(next(s for s in load(HOLDOUTS)["scenarios"] if s["id"]=="holdout-ephemeral-cli"))
    m=copy.deepcopy(model); next(t for t in m["templates"] if t["id"]=="PROBLEM-EVIDENCE").setdefault("requires",[]).append({"template":"COMPLETION-CRITERIA"}); assert "CAPABILITY_CYCLE" in {e["code"] for e in validate_reference_model(m,authorities,proof)}
    m=copy.deepcopy(model); next(t for t in m["templates"] if t["id"]=="PROBLEM-EVIDENCE").setdefault("requires",[]).append({"template":"DOES-NOT-EXIST"}); assert "MISSING_TEMPLATE" in {e["code"] for e in validate_reference_model(m,authorities,proof)}
    m=copy.deepcopy(model); next(t for t in m["templates"] if t["id"]=="PRODUCT-INTENT")["applicability"]={"candidate_when":{"predicate":"unknown_predicate","equals":True}}; assert "UNKNOWN_PREDICATE" in {e["code"] for e in validate_reference_model(m,authorities,proof)}
    m=copy.deepcopy(model); m["predicates"].append({"id":"product_output_exists","type":"boolean","source_class":"template-output","producer_template":"PRODUCT-INTENT"}); next(t for t in m["templates"] if t["id"]=="PRODUCT-INTENT")["applicability"]={"candidate_when":{"predicate":"product_output_exists","equals":True}}; assert "SELF_ACTIVATION" in {e["code"] for e in validate_reference_model(m,authorities,proof)}
    pf=copy.deepcopy(base["project_facts"]); pf["facts"].append({"predicate":"durable_state","value":True}); r=materialize(model,authorities,proof,pf,base["request"]); assert r["status"]=="PROJECT_EVIDENCE_CONFLICT",r
    m=copy.deepcopy(model); data=next(t for t in m["templates"] if t["id"]=="DATA-DESIGN"); data["applicability"]={"candidate_when":{"predicate":"durable_state","equals":True},"required_when":{"predicate":"durable_state","equals":True},"not_applicable_when":{"predicate":"durable_state","equals":True}}
    pf=copy.deepcopy(base["project_facts"])
    for row in pf["facts"]:
        if row["predicate"]=="durable_state":row["value"]=True
        if row["predicate"]=="persistence_independent":row["value"]=False
    r=materialize(m,authorities,proof,pf,base["request"]); assert r["status"]=="MATERIALIZATION_CONFLICT" and "APPLICABILITY_CONFLICT" in codes(r),r
    m=copy.deepcopy(model); next(t for t in m["templates"] if t["id"]=="COMPLETION-CRITERIA").setdefault("requires",[]).append({"template":"DATA-DESIGN"}); r=materialize(m,authorities,proof,base["project_facts"],base["request"]); assert r["status"]=="MATERIALIZATION_CONFLICT",r
    pf=copy.deepcopy(base["project_facts"]); pf["facts"]=[x for x in pf["facts"] if x["predicate"]!="machine_interface_subjects"]; r=materialize(model,authorities,proof,pf,base["request"]); assert r["status"]=="BLOCKED" and "SUBJECT_INVENTORY_REQUIRED" in codes(r),r
    m=copy.deepcopy(model); pd=next(x for x in m["predicates"] if x["id"]=="machine_interface_subjects"); pd["type"]="string"; pd.pop("finite",None); assert "UNBOUNDED_SCOPE" in {e["code"] for e in validate_reference_model(m,authorities,proof)}
    m=copy.deepcopy(model); next(t for t in m["templates"] if t["id"]=="PRODUCT-INTENT")["applicability"]={"candidate_when":{"predicate":"durable_state","equals":"true"}}; assert "PREDICATE_LITERAL_TYPE" in {e["code"] for e in validate_reference_model(m,authorities,proof)}
    pf=copy.deepcopy(base["project_facts"]); pf["activated_concerns"]=["valid.concern",42]; r=materialize(model,authorities,proof,pf,base["request"]); assert r["status"]=="PROJECT_EVIDENCE_INVALID" and "PROJECT_CONCERN_INVALID" in codes(r),r
    req=copy.deepcopy(base["request"]); req["project_id"]="###"; r=materialize(model,authorities,proof,base["project_facts"],req); assert r["status"]=="REQUEST_INVALID",r
    req=copy.deepcopy(base["request"]); req["consumer_id"]=authorities["authorities"][0]["id"]; r=materialize(model,authorities,proof,base["project_facts"],req); assert r["status"]=="REFERENCE_MODEL_GAP" and "GENERATED_GRAPH_INVALID" in codes(r),r
def kinds(graph): return {p["knowledge_kind"] for a in graph.get("authorities",[]) or [] for p in a.get("produces",[]) or [] if p.get("knowledge_kind")}
def run_regressions(model,authorities,proof):
    for s in load(REGRESSIONS)["scenarios"]:
        r=materialize(model,authorities,proof,s["project_facts"],s["request"]); e=s["expect"]; assert r["status"]==e["status"],(s["id"],r); validate_engineering_graph(r["graph"])
        generated=kinds(r["graph"]); existing=kinds(load(ROOT/s["existing_graph"])); aliases=e.get("legacy_kind_equivalents",{}) or {}; covered={k for k in generated if k in existing or aliases.get(k) in existing}; ratio=len(covered)/len(generated) if generated else 1.0
        assert ratio>=float(e["minimum_kind_coverage"]),{"scenario":s["id"],"ratio":ratio,"generated":sorted(generated),"existing":sorted(existing),"uncovered":sorted(generated-covered)}
def main():
    model=load_yaml(MODEL); authorities=load_yaml(AUTHORITIES); proof=load_yaml(PROOF); errors=validate_reference_model(model,authorities,proof); assert not errors,errors; assert len(model["templates"])==39; assert len(model["predicates"])==46
    canonical={claim for row in (proof.get("proofs",{}) or {}).values() for claim in (row.get("accepted_semantic_claims",[]) or [])}; routed={claim for t in model["templates"] for claim in t.get("claim_surface",[]) or []}; assert routed==canonical; assert len(canonical)==118
    run_holdouts(model,authorities,proof,HOLDOUTS); run_holdouts(model,authorities,proof,HOLDOUTS_V1); run_mutations(model,authorities,proof); run_regressions(model,authorities,proof); print("reference engineering model v0: PASS"); return 0
if __name__=="__main__": raise SystemExit(main())
