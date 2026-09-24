#!/usr/bin/env python3
from pathlib import Path
import sys, yaml
ROOT=Path(__file__).resolve().parents[1]
DOC=yaml.safe_load((ROOT/"spec/research/ddd-authority-decomposition-v1.yaml").read_text())
ALLOWED={"public-domain-strategy","public-context-strategy","public-tactical-model","context-relationship-pattern","modeling-practice","external-authority"}

def main():
    errors=[]
    pats=DOC.get("patterns",[])
    names=[p.get("name") for p in pats]
    if len(pats)!=45: errors.append(f"expected 45 reference patterns, got {len(pats)}")
    if len(names)!=len(set(names)): errors.append("duplicate pattern")
    for p in pats:
        if p.get("class") not in ALLOWED: errors.append(f"{p.get('name')}: invalid class")
        if p.get("class")=="external-authority" and not p.get("owner"): errors.append(f"{p.get('name')}: external owner missing")
        if p.get("class")=="modeling-practice" and p.get("owner"): errors.append(f"{p.get('name')}: practice auto-owns public knowledge")
    for flow in DOC.get("knowledge_flows",[]):
        for k in ("producer","output","consumer","consumer_output","necessity","encapsulation"):
            if not flow.get(k): errors.append(f"knowledge flow missing {k}")
    for v in DOC.get("boundary_variants",[]):
        invalid=bool(v.get("contexts_source")=="product-capabilities" or v.get("invalid_reason_markers"))
        actual="FAIL" if invalid else "PASS"
        if actual!=v.get("expect"): errors.append(f"{v.get('id')}: expected {v.get('expect')} got {actual}")
    cls={p["name"]:p["class"] for p in pats}
    if cls.get("Core Domain")==cls.get("Bounded Context"): errors.append("strategic dimensions conflated")
    if cls.get("Aggregate")!="public-tactical-model": errors.append("aggregate classification wrong")
    if cls.get("Layered Architecture")!="external-authority": errors.append("architecture ownership wrong")
    if errors:
        print("DDD decomposition validation failed:",file=sys.stderr)
        for e in errors: print("- "+e,file=sys.stderr)
        return 1
    print(f"DDD decomposition validation passed ({len(pats)} patterns, {len(DOC.get('boundary_variants',[]))} variants)")
    return 0
if __name__=="__main__": raise SystemExit(main())
