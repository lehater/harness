#!/usr/bin/env python3
"""Experimental capability-granular lifecycle evaluation.

Lifecycle metadata is a separate projection so Core v0 remains unchanged.
Semantic invalidation is keyed by Capability acceptance assertions, not artifact revisions.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path
from typing import Any
import yaml
from engineering_graph import derive_profile, production_index, validate_realization
from harness import CoreError, blocked, capability_blockers

def _load(path: str | Path) -> dict[str, Any]:
    value=yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(value,dict): raise CoreError(f"{path} must contain a mapping")
    return value

def lifecycle_index(projection: dict[str,Any]) -> dict[str,dict[str,Any]]:
    if projection.get("version")!=1 or projection.get("kind")!="harness-capability-lifecycle":
        raise CoreError("unexpected capability lifecycle projection")
    result={}
    for item in projection.get("providers",[]):
        if not isinstance(item,dict): raise CoreError("lifecycle provider must be a mapping")
        capability,artifact,acceptance_id=item.get("capability"),item.get("artifact"),item.get("acceptance_id")
        baseline=item.get("accepted_prerequisites",{})
        if not all(isinstance(v,str) and v for v in (capability,artifact,acceptance_id)):
            raise CoreError("lifecycle provider artifact/capability/acceptance_id are required")
        if capability in result: raise CoreError(f"duplicate lifecycle capability: {capability}")
        if not isinstance(baseline,dict) or any(not isinstance(k,str) or not k or not isinstance(v,str) or not v for k,v in baseline.items()):
            raise CoreError(f"invalid prerequisite baseline for {capability}")
        result[capability]=item
    return result

def validate_projection(graph,model,projection):
    realized=validate_realization(graph,model); productions=production_index(graph)
    lifecycle=lifecycle_index(projection); artifacts={a["id"]:a for a in realized.get("artifacts",[])}
    for capability,item in lifecycle.items():
        artifact=artifacts.get(item["artifact"])
        if artifact is None or capability not in (artifact.get("provides",[]) or []):
            raise CoreError(f"lifecycle provider does not match Core provider: {capability}")
        production=productions.get(capability)
        expected=set() if production is None else {r["capability"] for r in production["requires"]}
        actual=set(item.get("accepted_prerequisites",{}))
        if actual!=expected:
            raise CoreError(f"lifecycle baseline for {capability} must cover exactly production prerequisites; expected {sorted(expected)}, got {sorted(actual)}")
    return lifecycle

def lifecycle_states(graph,model,projection):
    lifecycle=validate_projection(graph,model,projection); productions=production_index(graph); memo={}
    def state(capability):
        if capability in memo: return memo[capability]
        item=lifecycle.get(capability)
        if item is None:
            result={"state":"UNKNOWN","capability":capability,"reason":"lifecycle coverage unavailable"}; memo[capability]=result; return result
        production=productions.get(capability); required=[] if production is None else [r["capability"] for r in production["requires"]]
        mismatches=[]; baseline=item.get("accepted_prerequisites",{})
        for prerequisite in required:
            upstream=state(prerequisite); current=lifecycle.get(prerequisite,{}).get("acceptance_id")
            if upstream["state"]!="CURRENT" or baseline.get(prerequisite)!=current:
                mismatches.append({"capability":prerequisite,"accepted_acceptance_id":baseline.get(prerequisite),"current_acceptance_id":current,"upstream_state":upstream["state"]})
        result={"state":"STALE" if mismatches else "CURRENT","capability":capability,"artifact":item["artifact"],"acceptance_id":item["acceptance_id"]}
        if mismatches: result["mismatches"]=mismatches
        memo[capability]=result; return result
    for capability in productions: state(capability)
    return memo

def evaluate_lifecycle_target(graph,target,model,projection):
    realized=validate_realization(graph,model); profile=derive_profile(graph,target); states=lifecycle_states(graph,realized,projection)
    artifacts=realized.get("artifacts",[]); expectations={e["id"]:e for e in profile["expectations"]}
    satisfied=[]; create=[]; revalidate=[]; wait=[]; pending=[]; lifecycle_gaps=[]; remaining=set(expectations)
    while remaining:
        progressed=False
        for eid in sorted(remaining):
            e=expectations[eid]; deps=e.get("depends_on",[])
            if any(dep not in satisfied for dep in deps): continue
            capability=e["capability"]; providers=[a for a in artifacts if capability in (a.get("provides",[]) or [])]
            if not providers:
                blockers=capability_blockers(realized,capability); item={"expectation":eid,"capability":capability,"authority":e["authority"]}
                if blockers: wait.append({"action":"WAIT",**item,"questions":blockers})
                else: create.append({"action":"CREATE",**item})
            else:
                blockers=sorted({q for a in providers for q in blocked(realized,a["id"])})
                if blockers: wait.append({"action":"WAIT","expectation":eid,"capability":capability,"authority":e["authority"],"questions":blockers})
                elif states[capability]["state"]=="CURRENT": satisfied.append(eid)
                elif states[capability]["state"]=="STALE": revalidate.append({"action":"REVALIDATE","expectation":eid,"capability":capability,"authority":e["authority"],"lifecycle":states[capability]})
                else: lifecycle_gaps.append({"expectation":eid,"capability":capability,"authority":e["authority"],"lifecycle":states[capability]})
            remaining.remove(eid); progressed=True
        if not progressed: break
    for eid in sorted(remaining):
        e=expectations[eid]; pending.append({"action":"PENDING","expectation":eid,"capability":e["capability"],"authority":e["authority"],"depends_on":[d for d in e.get("depends_on",[]) if d not in satisfied]})
    return {"status":"COMPLETE" if len(satisfied)==len(expectations) else ("READY" if create or revalidate else ("INCOMPLETE" if lifecycle_gaps else "BLOCKED")),"satisfied":sorted(satisfied),"create":create,"revalidate":revalidate,"wait":wait,"pending":pending,"lifecycle_gaps":lifecycle_gaps}

def main():
    p=argparse.ArgumentParser(); p.add_argument("graph"); p.add_argument("target"); p.add_argument("model"); p.add_argument("lifecycle"); a=p.parse_args()
    print(json.dumps(evaluate_lifecycle_target(_load(a.graph),a.target,_load(a.model),_load(a.lifecycle)),indent=2,sort_keys=True)); return 0
if __name__=="__main__": raise SystemExit(main())
