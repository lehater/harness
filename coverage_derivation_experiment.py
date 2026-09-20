#!/usr/bin/env python3
"""Research-only derived Engineering Coverage engine.

Inputs:
- concern catalog
- generic evidence mapping registry
- one or more project knowledge files
- minimal project overlay

The output is disposable derived state, never project truth.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path
from typing import Any
import yaml

SEMANTIC_STATES = {"COVERED","MISSING","BLOCKED","STALE","NOT_APPLICABLE","DEFERRED","UNASSESSED"}

def load(path: str) -> dict[str, Any]:
    value = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a mapping")
    return value

def flatten_catalog(catalog: dict[str, Any]) -> tuple[dict[str,dict[str,Any]], dict[str,list[str]]]:
    nodes: dict[str,dict[str,Any]] = {}
    children: dict[str,list[str]] = {}
    def visit(node: dict[str,Any]) -> None:
        cid=node["id"]
        if cid in nodes: raise ValueError(f"duplicate concern id: {cid}")
        nodes[cid]=node
        children[cid]=[c["id"] for c in node.get("children",[])]
        for c in node.get("children",[]): visit(c)
    for root in catalog.get("concerns",[]): visit(root)
    for leaf in catalog.get("quality_attribute_leaves",[]): visit(leaf)
    return nodes, children

def normalize_knowledge(files: list[dict[str,Any]]) -> dict[str,Any]:
    artifacts: dict[str,dict[str,Any]] = {}
    questions: list[dict[str,Any]] = []
    nodes_by_id: dict[str,dict[str,Any]] = {}

    for doc in files:
        for node in doc.get("nodes",[]) or []:
            nodes_by_id[node["id"]] = node
            artifacts.setdefault(node["id"],{
                "id": node["id"], "kind": node.get("kind"),
                "path": node.get("path"), "depends_on": node.get("depends_on",[]),
                "provides": [], "authority": None,
            })
        for a in doc.get("artifacts",[]) or []:
            artifacts[a["id"]] = {
                "id": a["id"], "kind": a.get("kind"), "path": a.get("path"),
                "depends_on": a.get("depends_on",[]), "provides": a.get("provides",[]) or [],
                "authority": a.get("authority"),
            }
        for b in doc.get("bindings",[]) or []:
            base = artifacts.setdefault(b["artifact"],{
                "id":b["artifact"],"kind":None,"path":None,"depends_on":[],"provides":[],"authority":None
            })
            base["authority"] = b.get("authority")
            base["provides"] = sorted(set(base.get("provides",[])) | set(b.get("provides",[]) or []))
            if b["artifact"] in nodes_by_id:
                node=nodes_by_id[b["artifact"]]
                base["kind"] = node.get("kind")
                base["path"] = node.get("path")
                base["depends_on"] = node.get("depends_on",[])
        questions.extend(doc.get("questions",[]) or [])

    capability_to_artifacts: dict[str,list[str]] = {}
    for aid,a in artifacts.items():
        for cap in a.get("provides",[]) or []:
            capability_to_artifacts.setdefault(cap,[]).append(aid)

    unresolved=[]
    for q in questions:
        if q.get("resolution"):
            continue
        unresolved.append(q)

    return {
        "artifacts": artifacts,
        "capability_to_artifacts": capability_to_artifacts,
        "questions": unresolved,
    }

def selector_matches(mapping: dict[str,Any], artifact: dict[str,Any]) -> bool:
    aid=artifact["id"]
    kind=artifact.get("kind")
    caps=artifact.get("provides",[]) or []
    if aid in mapping.get("artifact_ids",[]): return True
    if kind and kind in mapping.get("artifact_kinds",[]): return True
    for suffix in mapping.get("capability_suffixes",[]) or []:
        if any(cap.endswith(suffix) for cap in caps): return True
    for token in mapping.get("capability_contains",[]) or []:
        if any(token in cap for cap in caps): return True
    return False

def evidence_for(mapping: dict[str,Any], knowledge: dict[str,Any]) -> list[dict[str,Any]]:
    result=[]
    for artifact in knowledge["artifacts"].values():
        if selector_matches(mapping,artifact):
            result.append({
                "artifact":artifact["id"],
                "authority":artifact.get("authority"),
                "path":artifact.get("path"),
                "kind":artifact.get("kind"),
                "capabilities":artifact.get("provides",[]),
            })
    return result

def blocked_by(mapping: dict[str,Any], knowledge: dict[str,Any]) -> list[str]:
    mapped_caps=set()
    for artifact in knowledge["artifacts"].values():
        if selector_matches(mapping,artifact):
            mapped_caps.update(artifact.get("provides",[]) or [])
    blockers=[]
    for q in knowledge["questions"]:
        blocked=set(q.get("blocks_capabilities",[]) or [])
        if blocked & mapped_caps:
            blockers.append(q.get("id","QUESTION"))
    return blockers

def derive(catalog: dict[str,Any], registry: dict[str,Any], knowledge_docs: list[dict[str,Any]], overlay: dict[str,Any]) -> dict[str,Any]:
    nodes, children = flatten_catalog(catalog)
    mappings=registry.get("mappings",{})
    knowledge=normalize_knowledge(knowledge_docs)

    explicit={x["concern"]:x for x in overlay.get("decisions",[]) or []}
    required=set(overlay.get("required",[]) or [])
    freshness=overlay.get("freshness",{}) or {}

    subtree_defaults: dict[str,dict[str,Any]] = {}
    def leaves(cid:str)->list[str]:
        if not children[cid]: return [cid]
        out=[]
        for c in children[cid]: out.extend(leaves(c))
        return out
    for d in overlay.get("subtree_decisions",[]) or []:
        for leaf in leaves(d["concern"]):
            subtree_defaults[leaf]=d

    rows=[]
    for cid in sorted(nodes):
        if children[cid]:
            continue
        decision=explicit.get(cid) or subtree_defaults.get(cid)
        if decision:
            state=decision["state"]
            rows.append({"concern":cid,"state":state,"derivation":"EXPLICIT_APPLICABILITY","rationale":decision.get("rationale"),"evidence":decision.get("evidence",[])})
            continue

        mapping=mappings.get(cid)
        evidence=evidence_for(mapping,knowledge) if mapping else []
        blockers=blocked_by(mapping,knowledge) if mapping else []

        if blockers and cid in required:
            state="BLOCKED"
        elif evidence:
            state="COVERED"
        elif cid in required:
            state="MISSING"
        else:
            state="UNASSESSED"

        fresh=freshness.get(cid,"UNKNOWN")
        if state=="COVERED" and fresh=="STALE":
            state="STALE"

        rows.append({
            "concern":cid,
            "state":state,
            "derivation":"AUTO" if mapping else "NO_MAPPING",
            "evidence":evidence,
            "blockers":blockers,
            "freshness":fresh,
        })

    counts={}
    for row in rows: counts[row["state"]]=counts.get(row["state"],0)+1
    return {
        "version":1,
        "kind":"harness-derived-engineering-coverage",
        "project":overlay.get("project"),
        "scope":overlay.get("scope"),
        "catalog":catalog.get("id"),
        "rows":rows,
        "summary":{"counts":counts},
    }

def remaining_work(result: dict[str,Any]) -> list[dict[str,Any]]:
    return [r for r in result["rows"] if r["state"] in {"MISSING","BLOCKED","STALE","UNASSESSED"}]

def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument("catalog")
    ap.add_argument("mapping")
    ap.add_argument("overlay")
    ap.add_argument("knowledge", nargs="+")
    ap.add_argument("--remaining", action="store_true")
    args=ap.parse_args()
    result=derive(load(args.catalog),load(args.mapping),[load(p) for p in args.knowledge],load(args.overlay))
    if args.remaining:
        result={"project":result["project"],"remaining":remaining_work(result)}
    print(yaml.safe_dump(result,sort_keys=False,allow_unicode=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
