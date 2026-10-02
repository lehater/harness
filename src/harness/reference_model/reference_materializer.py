#!/usr/bin/env python3
"""Experimental Reference Engineering Model validator/materializer."""
from __future__ import annotations
import argparse, copy, json, re
from pathlib import Path
from typing import Any
import yaml

from harness.project_model.engineering_graph import validate_engineering_graph
from harness.project_model.core import CoreError

_ALLOWED_PREDICATE_TYPES={"boolean","string","enum","number","string_list"}

__all__ = [
    'CoreError',
    'validate_engineering_graph',
    'load_yaml',
    'diag',
    'predicate_refs',
    'validate_expr',
    'eval_expr',
    'proof_claims',
    'authority_index',
    'validate_reference_model',
    'value_matches',
    'normalize_project_facts',
    'slug',
    'materialize',
    'main',
    'annotations',
    'argparse',
    'copy',
    'json',
    're',
    'Path',
    'Any',
    'yaml',
]

def load_yaml(path):
    value=yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    if not isinstance(value,dict): raise ValueError(f"{path}: expected mapping")
    return value

def diag(code,message,**extra): return {"code":code,"message":message,**extra}

def predicate_refs(expr):
    if expr is None or not isinstance(expr,dict): return set()
    if "predicate" in expr: return {expr["predicate"]} if isinstance(expr["predicate"],str) else set()
    out=set()
    for key in ("all","any"):
        for item in expr.get(key,[]) if isinstance(expr.get(key),list) else []: out|=predicate_refs(item)
    if "not" in expr: out|=predicate_refs(expr["not"])
    return out

def validate_expr(expr,predicates,where):
    if expr is None: return []
    if not isinstance(expr,dict): return [diag("INVALID_EXPRESSION",f"{where}: expression must be a mapping")]
    keys=set(expr)
    if "predicate" in expr:
        if keys-{"predicate","equals"}: return [diag("INVALID_EXPRESSION",f"{where}: predicate expression has unknown fields")]
        pid=expr.get("predicate")
        if pid not in predicates: return [diag("UNKNOWN_PREDICATE",f"{where}: unknown predicate {pid}",predicate=pid)]
        if "equals" not in expr: return [diag("INVALID_EXPRESSION",f"{where}: predicate expression requires equals")]
        if not value_matches(expr["equals"],predicates[pid]):
            return [diag("PREDICATE_LITERAL_TYPE",f"{where}: equals value does not match predicate type",predicate=pid)]
        return []
    if "all" in expr or "any" in expr:
        op="all" if "all" in expr else "any"
        if keys!={op} or not isinstance(expr[op],list) or not expr[op]: return [diag("INVALID_EXPRESSION",f"{where}: {op} requires a non-empty list")]
        out=[]
        for i,item in enumerate(expr[op]): out.extend(validate_expr(item,predicates,f"{where}.{op}[{i}]"))
        return out
    if "not" in expr:
        return validate_expr(expr["not"],predicates,f"{where}.not") if keys=={"not"} else [diag("INVALID_EXPRESSION",f"{where}: not expression has unknown fields")]
    return [diag("INVALID_EXPRESSION",f"{where}: unknown expression form")]

def eval_expr(expr,facts):
    if expr is None: return None
    if "predicate" in expr:
        return None if expr["predicate"] not in facts else facts[expr["predicate"]]==expr["equals"]
    if "all" in expr:
        vals=[eval_expr(x,facts) for x in expr["all"]]
        return False if any(v is False for v in vals) else (True if all(v is True for v in vals) else None)
    if "any" in expr:
        vals=[eval_expr(x,facts) for x in expr["any"]]
        return True if any(v is True for v in vals) else (False if all(v is False for v in vals) else None)
    if "not" in expr:
        v=eval_expr(expr["not"],facts); return None if v is None else not v
    return None

def proof_claims(proof):
    out={}
    for concern,row in (proof.get("proofs",{}) or {}).items():
        if isinstance(row,dict) and isinstance(row.get("accepted_semantic_claims"),list): out[concern]=list(row["accepted_semantic_claims"])
    return out

def authority_index(catalog):
    return {x["id"]:x for x in catalog.get("authorities",[]) or [] if isinstance(x,dict) and isinstance(x.get("id"),str)}

def validate_reference_model(model,authority_catalog,proof_contract):
    errors=[]
    if model.get("version")!=1 or model.get("kind")!="harness-reference-engineering-model":
        return [diag("REFERENCE_MODEL_HEADER","unexpected Reference Engineering Model header")]
    defs={}
    for row in model.get("predicates",[]) or []:
        if not isinstance(row,dict) or not isinstance(row.get("id"),str) or not row["id"]:
            errors.append(diag("PREDICATE_VOCABULARY_INVALID","predicate id is required")); continue
        pid=row["id"]
        if pid in defs: errors.append(diag("PREDICATE_DUPLICATE",f"duplicate predicate {pid}",predicate=pid)); continue
        if row.get("type") not in _ALLOWED_PREDICATE_TYPES: errors.append(diag("PREDICATE_TYPE_INVALID",f"{pid}: invalid type",predicate=pid))
        defs[pid]=row
    authorities=authority_index(authority_catalog); by_id={}; routes={}
    canonical={c for values in proof_claims(proof_contract).values() for c in values}
    for t in model.get("templates",[]) or []:
        if not isinstance(t,dict) or not isinstance(t.get("id"),str): errors.append(diag("TEMPLATE_ID_INVALID","template id is required")); continue
        tid=t["id"]
        if tid in by_id: errors.append(diag("TEMPLATE_DUPLICATE",f"duplicate template {tid}",template=tid)); continue
        by_id[tid]=t
        if t.get("authority_type") not in authorities: errors.append(diag("UNKNOWN_AUTHORITY_TYPE",f"{tid}: unknown Authority Type {t.get('authority_type')}",template=tid))
        surface=t.get("claim_surface",[]) or []; primary=t.get("primary_claims",[]) or []
        if not set(primary).issubset(set(surface)): errors.append(diag("PRIMARY_CLAIM_OUTSIDE_SURFACE",f"{tid}: primary claims must be inside claim_surface",template=tid))
        for claim in surface:
            if claim not in canonical: errors.append(diag("UNKNOWN_SEMANTIC_CLAIM",f"{tid}: unknown semantic claim {claim}",template=tid,claim=claim))
            routes.setdefault(claim,[]).append(tid)
        app=t.get("applicability",{}) or {}
        for key in ("candidate_when","required_when","not_applicable_when"):
            if key in app: errors.extend(validate_expr(app[key],defs,f"{tid}.applicability.{key}"))
        for pid in predicate_refs(app.get("candidate_when"))|predicate_refs(app.get("required_when")):
            pdef=defs.get(pid,{})
            if pdef.get("source_class")=="template-output" and pdef.get("producer_template")==tid:
                errors.append(diag("SELF_ACTIVATION",f"{tid}: activation depends on own output {pid}",template=tid,predicate=pid))
        scope=t.get("scope",{"mode":"singleton"})
        if not isinstance(scope,dict) or scope.get("mode") not in {"singleton","per_subject"}:
            errors.append(diag("SCOPE_SCHEMA_INVALID",f"{tid}: invalid scope schema",template=tid))
        elif scope.get("mode")=="per_subject":
            src=scope.get("subjects_from"); pdef=defs.get(src)
            if pdef is None: errors.append(diag("UNKNOWN_PREDICATE",f"{tid}: unknown subjects_from {src}",template=tid,predicate=src))
            elif pdef.get("type")!="string_list" or pdef.get("finite") is not True: errors.append(diag("UNBOUNDED_SCOPE",f"{tid}: subjects_from must be finite string_list",template=tid,predicate=src))
        for i,r in enumerate(t.get("requires",[]) or []):
            if not isinstance(r,dict) or not isinstance(r.get("template"),str): errors.append(diag("REQUIRES_INVALID",f"{tid}: invalid requirement {i}",template=tid)); continue
            if "when" in r: errors.extend(validate_expr(r["when"],defs,f"{tid}.requires[{i}].when"))
    for claim in sorted(canonical):
        rs=routes.get(claim,[])
        if not rs: errors.append(diag("CLAIM_UNROUTED",f"canonical claim has no template: {claim}",claim=claim))
        elif len(rs)>1: errors.append(diag("CLAIM_AMBIGUOUS",f"canonical claim has multiple templates: {claim}",claim=claim,templates=sorted(rs)))
    for tid,t in by_id.items():
        for r in t.get("requires",[]) or []:
            if isinstance(r,dict) and isinstance(r.get("template"),str) and r["template"] not in by_id: errors.append(diag("MISSING_TEMPLATE",f"{tid}: missing template {r['template']}",template=tid,dependency=r["template"]))
    deps={tid:{r["template"] for r in t.get("requires",[]) or [] if isinstance(r,dict) and r.get("template") in by_id} for tid,t in by_id.items()}
    visiting=set(); visited=set()
    for tid in sorted(by_id):
        if tid in visited: continue
        stack=[(tid,False)]
        while stack:
            current,expanded=stack.pop()
            if expanded:
                if current in visiting: visiting.remove(current)
                visited.add(current); continue
            if current in visited: continue
            if current in visiting:
                errors.append(diag("CAPABILITY_CYCLE",f"Reference Capability dependency cycle at {current}",template=current)); continue
            visiting.add(current); stack.append((current,True))
            for target in reversed(sorted(deps.get(current,()))):
                if target in visiting:
                    errors.append(diag("CAPABILITY_CYCLE",f"Reference Capability dependency cycle at {target}",template=target))
                elif target not in visited:
                    stack.append((target,False))
    return errors

def value_matches(value,d):
    k=d.get("type")
    if k=="boolean": return isinstance(value,bool)
    if k=="string": return isinstance(value,str) and bool(value)
    if k=="enum": return value in (d.get("allowed_values",[]) or [])
    if k=="number": return isinstance(value,(int,float)) and not isinstance(value,bool)
    if k=="string_list": return isinstance(value,list) and all(isinstance(x,str) and x for x in value) and len(value)==len(set(value))
    return False

def normalize_project_facts(model,doc):
    ds={x["id"]:x for x in model.get("predicates",[]) or []}; values={}; diags=[]
    if doc.get("version")!=1 or doc.get("kind")!="harness-project-facts": return {},[],[diag("PROJECT_FACTS_HEADER","unexpected project facts header")]
    for row in doc.get("facts",[]) or []:
        if not isinstance(row,dict) or not isinstance(row.get("predicate"),str): diags.append(diag("PROJECT_FACT_INVALID","project fact requires predicate")); continue
        pid=row["predicate"]
        if pid not in ds: diags.append(diag("UNKNOWN_PREDICATE",f"project facts use unknown predicate {pid}",predicate=pid)); continue
        if "value" not in row or not value_matches(row["value"],ds[pid]): diags.append(diag("PROJECT_FACT_TYPE",f"{pid}: value type mismatch",predicate=pid)); continue
        if pid in values and values[pid]!=row["value"]: diags.append(diag("PROJECT_EVIDENCE_CONFLICT",f"conflicting accepted values for {pid}",predicate=pid)); continue
        values[pid]=copy.deepcopy(row["value"])
    concerns=doc.get("activated_concerns",[]) or []
    if not isinstance(concerns,list) or any(not isinstance(x,str) or not x for x in concerns):
        diags.append(diag("PROJECT_CONCERN_INVALID","activated_concerns must be a list of non-empty strings"))
        return values,[],diags
    return values,sorted(set(concerns)),diags

def slug(v): return re.sub(r"[^a-z0-9]+","-",v.lower()).strip("-")

def materialize(model,authority_catalog,proof_contract,project_facts,request):
    ref_errors=validate_reference_model(model,authority_catalog,proof_contract)
    if ref_errors:return {"version":1,"kind":"harness-reference-materialization-result","status":"REFERENCE_MODEL_INVALID","diagnostics":ref_errors}
    facts,concerns,diags=normalize_project_facts(model,project_facts)
    codes={d["code"] for d in diags}
    if "PROJECT_EVIDENCE_CONFLICT" in codes:return {"version":1,"kind":"harness-reference-materialization-result","status":"PROJECT_EVIDENCE_CONFLICT","diagnostics":diags}
    if diags:return {"version":1,"kind":"harness-reference-materialization-result","status":"PROJECT_EVIDENCE_INVALID","diagnostics":diags}
    if request.get("version")!=1 or request.get("kind")!="harness-reference-materialization-request": return {"version":1,"kind":"harness-reference-materialization-result","status":"REQUEST_INVALID","diagnostics":[diag("REQUEST_HEADER","unexpected request header")]}
    project_id=request.get("project_id"); roots=request.get("roots",[]) or []; ts={x["id"]:x for x in model["templates"]}
    if not isinstance(project_id,str) or not project_id or not slug(project_id) or not isinstance(roots,list) or not roots or any(not isinstance(r,str) or r not in ts for r in roots): return {"version":1,"kind":"harness-reference-materialization-result","status":"REQUEST_INVALID","diagnostics":[diag("REQUEST_FIELDS","invalid project_id or roots")]}
    pm=proof_claims(proof_contract); claim_route={claim:t["id"] for t in model["templates"] for claim in t.get("claim_surface",[]) or []}
    states={}; active={tid:set() for tid in ts}
    for tid,t in ts.items():
        a=t.get("applicability",{}) or {}; rv=eval_expr(a.get("required_when"),facts); nv=eval_expr(a.get("not_applicable_when"),facts); cv=eval_expr(a.get("candidate_when"),facts)
        if rv is True and nv is True: states[tid]="UNRESOLVED"; diags.append(diag("APPLICABILITY_CONFLICT",f"{tid}: REQUIRED and N/A evidence both true",template=tid))
        elif rv is True: states[tid]="REQUIRED"
        elif nv is True: states[tid]="NOT_APPLICABLE"
        elif cv is True: states[tid]="UNRESOLVED"
        else: states[tid]="UNASSESSED"
    gap=False; conflict=any(d.get("code")=="APPLICABILITY_CONFLICT" for d in diags)
    for concern in concerns:
        cs=pm.get(concern)
        if not cs: diags.append(diag("REFERENCE_MODEL_GAP",f"activated concern has no canonical proof route: {concern}",concern=concern)); gap=True; continue
        for claim in cs:
            tid=claim_route.get(claim)
            if not tid: diags.append(diag("REFERENCE_MODEL_GAP",f"activated claim has no template: {claim}",claim=claim)); gap=True; continue
            if states[tid]=="NOT_APPLICABLE": diags.append(diag("MATERIALIZATION_CONFLICT",f"{concern} requires N/A template {tid}",concern=concern,template=tid)); conflict=True
            else: states[tid]="REQUIRED"; active[tid].add(claim)
    for tid in roots:
        if states[tid]=="NOT_APPLICABLE": diags.append(diag("MATERIALIZATION_CONFLICT",f"root is N/A: {tid}",template=tid)); conflict=True
        else: states[tid]="REQUIRED"
    unresolved=False; changed=True
    while changed:
        changed=False
        for tid in sorted(ts):
            if states[tid]!="REQUIRED": continue
            for r in ts[tid].get("requires",[]) or []:
                cond=eval_expr(r.get("when"),facts) if "when" in r else True
                if cond is False: continue
                if cond is None: diags.append(diag("DEPENDENCY_CONDITION_UNKNOWN",f"{tid}: dependency condition unknown for {r['template']}",template=tid,dependency=r["template"])); unresolved=True; continue
                target=r["template"]
                if states[target]=="NOT_APPLICABLE": diags.append(diag("MATERIALIZATION_CONFLICT",f"{tid} requires N/A template {target}",template=target,required_by=tid)); conflict=True; continue
                if states[target]!="REQUIRED": states[target]="REQUIRED"; changed=True
    status_rows=[{"template":tid,"status":states[tid]} for tid in sorted(states)]
    if conflict:return {"version":1,"kind":"harness-reference-materialization-result","status":"MATERIALIZATION_CONFLICT","template_status":status_rows,"diagnostics":diags}
    if gap:return {"version":1,"kind":"harness-reference-materialization-result","status":"REFERENCE_MODEL_GAP","template_status":status_rows,"diagnostics":diags}
    if unresolved or any(v=="UNRESOLVED" for v in states.values()):return {"version":1,"kind":"harness-reference-materialization-result","status":"UNRESOLVED","template_status":status_rows,"diagnostics":diags}
    required=[tid for tid in sorted(ts) if states[tid]=="REQUIRED"]; subjects={}; blocked=False
    for tid in required:
        scope=ts[tid].get("scope",{"mode":"singleton"})
        if scope.get("mode")=="singleton": subjects[tid]=[None]
        else:
            vals=facts.get(scope["subjects_from"])
            if not isinstance(vals,list) or not vals: diags.append(diag("SUBJECT_INVENTORY_REQUIRED",f"{tid}: subject inventory required",template=tid,predicate=scope["subjects_from"])); blocked=True
            else: subjects[tid]=list(vals)
    if blocked:return {"version":1,"kind":"harness-reference-materialization-result","status":"BLOCKED","template_status":status_rows,"diagnostics":diags}
    instances={}
    for tid in required:
        rows=[]
        for subject in subjects[tid]:
            cap=f"{slug(project_id)}.{slug(tid)}"+(f".{slug(subject)}" if subject is not None else "")
            rows.append({"capability":cap,"subject":subject})
        instances[tid]=rows
    consumed=set(); prods={}
    for tid in required:
        t=ts[tid]; claimset=sorted(set(t.get("primary_claims",[]) or [])|active[tid])
        for inst in instances[tid]:
            p={"capability":inst["capability"],"requires":[]}
            if t.get("knowledge_kind"):p["knowledge_kind"]=t["knowledge_kind"]
            if claimset:p["semantic_claims"]=[({"claim":claim,"subject":inst["subject"]} if inst["subject"] is not None else claim) for claim in claimset]
            rs={}
            for r in t.get("requires",[]) or []:
                cond=eval_expr(r.get("when"),facts) if "when" in r else True
                if cond is not True or r["template"] not in instances: continue
                for target in instances[r["template"]]:
                    item={"capability":target["capability"]}
                    if target["subject"] is not None:item["subject"]=str(target["subject"])
                    rs[(item["capability"],item.get("subject"))]=item; consumed.add(item["capability"])
            p["requires"]=[rs[k] for k in sorted(rs)]
            prods.setdefault(t["authority_type"],[]).append(p)
    consumer=[]
    for root in roots:
        for inst in instances.get(root,[]):
            item={"capability":inst["capability"]}
            if inst["subject"] is not None:item["subject"]=str(inst["subject"])
            consumer.append(item); consumed.add(inst["capability"])
    dead=[p["capability"] for rows in prods.values() for p in rows if p["capability"] not in consumed and not p.get("semantic_claims")]
    if dead:return {"version":1,"kind":"harness-reference-materialization-result","status":"REFERENCE_MODEL_GAP","template_status":status_rows,"diagnostics":diags+[diag("REFERENCE_MODEL_GAP","dead public materialized capability",capabilities=sorted(dead))]}
    ai=authority_index(authority_catalog); order=[x["id"] for x in authority_catalog.get("authorities",[]) or [] if isinstance(x,dict) and isinstance(x.get("id"),str)]
    authorities=[]
    for aid in order:
        if aid not in prods:continue
        src=ai[aid]; b=src.get("boundary",{}) or {}; resp=src.get("responsibility",aid)
        authorities.append({"id":aid,"responsibility":resp,"boundary":{"semantic_cohesion":b.get("semantic_cohesion",resp),"independent_change":b.get("independent_change",resp),"public_contract":b.get("public_contract",resp)},"produces":sorted(prods[aid],key=lambda x:x["capability"])})
    graph={"version":1,"kind":"harness-engineering-graph","id":slug(project_id).upper(),"default_subject":project_id,"authorities":authorities,"consumers":[{"id":request.get("consumer_id") or "TARGET","purpose":request.get("purpose") or "Consume materialized engineering knowledge.","requires":sorted(consumer,key=lambda x:(x["capability"],x.get("subject","")))}],"terminal_capabilities":[]}
    try:
        validate_engineering_graph(graph)
    except CoreError as exc:
        return {"version":1,"kind":"harness-reference-materialization-result","status":"REFERENCE_MODEL_GAP","template_status":status_rows,"diagnostics":diags+[diag("GENERATED_GRAPH_INVALID",str(exc))]}
    return {"version":1,"kind":"harness-reference-materialization-result","status":"STABLE","template_status":status_rows,"diagnostics":diags,"graph":graph}

def main():
    p=argparse.ArgumentParser(); sub=p.add_subparsers(dest="cmd",required=True)
    v=sub.add_parser("validate"); v.add_argument("model"); v.add_argument("--authorities",default="catalogs/software-authorities-v0.yaml"); v.add_argument("--proof",default="spec/engineering-coverage/semantic-proof-contract-v1.yaml")
    m=sub.add_parser("materialize"); m.add_argument("model"); m.add_argument("project_facts"); m.add_argument("request"); m.add_argument("--authorities",default="catalogs/software-authorities-v0.yaml"); m.add_argument("--proof",default="spec/engineering-coverage/semantic-proof-contract-v1.yaml")
    a=p.parse_args(); model=load_yaml(a.model); authorities=load_yaml(a.authorities); proof=load_yaml(a.proof)
    if a.cmd=="validate":
        ds=validate_reference_model(model,authorities,proof); print(json.dumps({"valid":not ds,"diagnostics":ds},indent=2,sort_keys=True)); return 0 if not ds else 1
    r=materialize(model,authorities,proof,load_yaml(a.project_facts),load_yaml(a.request)); print(json.dumps(r,indent=2,sort_keys=True)); return 0 if r["status"]=="STABLE" else 1
if __name__=="__main__": raise SystemExit(main())
