#!/usr/bin/env python3
from __future__ import annotations

import copy
import sys
from pathlib import Path

import yaml

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))

from reference_materializer import load_yaml, materialize
from reference_model_evolution import analyze_evolution, fingerprint, materialized_capabilities

MODEL=ROOT/"spec/research/reference-engineering-model-v0.yaml"
AUTHORITIES=ROOT/"catalogs/software-authorities-v0.yaml"
PROOF=ROOT/"spec/engineering-coverage/semantic-proof-contract-v1.yaml"
HOLDOUTS=ROOT/"spec/research/reference-materializer-fixtures/holdouts-v0.yaml"


def load(path):
    value=yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    assert isinstance(value,dict),path
    return value


def rename_template(model,old,new):
    out=copy.deepcopy(model)
    target=next(x for x in out["templates"] if x["id"]==old)
    target["id"]=new
    for template in out["templates"]:
        for req in template.get("requires",[]) or []:
            if req.get("template")==old:
                req["template"]=new
    for predicate in out.get("predicates",[]) or []:
        if predicate.get("producer_template")==old:
            predicate["producer_template"]=new
    return out


def replace_predicate_ref(expr,old,new):
    if not isinstance(expr,dict):
        return
    if expr.get("predicate")==old:
        expr["predicate"]=new
    for key in ("all","any"):
        for item in expr.get(key,[]) or []:
            replace_predicate_ref(item,old,new)
    if isinstance(expr.get("not"),dict):
        replace_predicate_ref(expr["not"],old,new)


def rename_predicate(model,old,new):
    out=copy.deepcopy(model)
    next(x for x in out["predicates"] if x["id"]==old)["id"]=new
    for template in out["templates"]:
        app=template.get("applicability",{}) or {}
        for key in ("candidate_when","required_when","not_applicable_when"):
            replace_predicate_ref(app.get(key),old,new)
        scope=template.get("scope",{}) or {}
        if scope.get("subjects_from")==old:
            scope["subjects_from"]=new
        for req in template.get("requires",[]) or []:
            replace_predicate_ref(req.get("when"),old,new)
    return out


def main():
    model=load_yaml(MODEL); authorities=load_yaml(AUTHORITIES); proof=load_yaml(PROOF)
    scenario=load(HOLDOUTS)["scenarios"][0]
    facts=copy.deepcopy(scenario["project_facts"]); request=copy.deepcopy(scenario["request"])

    # Historical reproducibility exists while the exact model snapshot is retained.
    first=materialize(model,authorities,proof,facts,request)
    second=materialize(model,authorities,proof,facts,request)
    assert first["status"]=="STABLE" and first==second
    assert fingerprint(model)==fingerprint(copy.deepcopy(model))
    assert "reference_model_fingerprint" not in first

    unchanged=analyze_evolution(model,copy.deepcopy(model),{"version":1,"kind":"harness-reference-model-migration","operations":[]})
    assert unchanged["status"]=="UNCHANGED" and unchanged["requires_rematerialization"] is False

    # Rename: explicit mapping is required, and old project capability becomes obsolete.
    renamed=rename_template(model,"IMPLEMENTATION-STACK","IMPLEMENTATION-TOOLCHAIN")
    missing=analyze_evolution(model,renamed,{"version":1,"kind":"harness-reference-model-migration","operations":[]})
    assert missing["status"]=="INVALID"
    assert any(x["code"]=="MIGRATION_MAP_INCOMPLETE" for x in missing["diagnostics"])

    mapped=analyze_evolution(model,renamed,{
        "version":1,"kind":"harness-reference-model-migration",
        "operations":[{"op":"rename_template","from":"IMPLEMENTATION-STACK","to":"IMPLEMENTATION-TOOLCHAIN"}],
    })
    assert mapped["status"]=="MAPPED_CHANGE" and mapped["requires_rematerialization"] is True
    after=materialize(renamed,authorities,proof,facts,request)
    assert after["status"]=="STABLE"
    obsolete=materialized_capabilities(first)-materialized_capabilities(after)
    added=materialized_capabilities(after)-materialized_capabilities(first)
    assert any(x.endswith(".implementation-stack") for x in obsolete),obsolete
    assert any(x.endswith(".implementation-toolchain") for x in added),added

    # Predicate rename: explicit fact migration can preserve the project graph while model identity changes.
    pred_new=rename_predicate(model,"toolchain_selection_material","implementation_stack_material")
    migrated_facts=copy.deepcopy(facts)
    for row in migrated_facts["facts"]:
        if row["predicate"]=="toolchain_selection_material":
            row["predicate"]="implementation_stack_material"
    pred_analysis=analyze_evolution(model,pred_new,{
        "version":1,"kind":"harness-reference-model-migration",
        "operations":[{"op":"rename_predicate","from":"toolchain_selection_material","to":"implementation_stack_material"}],
    })
    assert pred_analysis["status"]=="MAPPED_CHANGE"
    pred_result=materialize(pred_new,authorities,proof,migrated_facts,request)
    assert pred_result["status"]=="STABLE"
    assert pred_result["graph"]==first["graph"]

    # Split and merge identities are recognized only through explicit mappings.
    split=copy.deepcopy(model)
    old=next(x for x in split["templates"] if x["id"]=="APPLICATION-FAILURE-CONTRACT")
    split["templates"].remove(old)
    left=copy.deepcopy(old); left["id"]="APPLICATION-FAILURE-INPUT"
    right=copy.deepcopy(old); right["id"]="APPLICATION-FAILURE-RECOVERY"
    split["templates"].extend([left,right])
    split_analysis=analyze_evolution(model,split,{
        "version":1,"kind":"harness-reference-model-migration",
        "operations":[{"op":"split_template","from":"APPLICATION-FAILURE-CONTRACT","to":["APPLICATION-FAILURE-INPUT","APPLICATION-FAILURE-RECOVERY"]}],
    })
    assert split_analysis["status"]=="MAPPED_CHANGE"

    merged=copy.deepcopy(model)
    merged["templates"]=[x for x in merged["templates"] if x["id"] not in {"IMPLEMENTATION-STACK","IMPLEMENTATION-PLAN"}]
    combined=copy.deepcopy(next(x for x in model["templates"] if x["id"]=="IMPLEMENTATION-STACK"))
    combined["id"]="IMPLEMENTATION-REALIZATION"
    merged["templates"].append(combined)
    merge_analysis=analyze_evolution(model,merged,{
        "version":1,"kind":"harness-reference-model-migration",
        "operations":[{"op":"merge_templates","from":["IMPLEMENTATION-STACK","IMPLEMENTATION-PLAN"],"to":"IMPLEMENTATION-REALIZATION"}],
    })
    assert merge_analysis["status"]=="MAPPED_CHANGE"

    print("reference model evolution research: PASS")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
