#!/usr/bin/env python3
"""Research-only projection of project Authorities onto reusable Harness roles."""
from __future__ import annotations
import argparse
from pathlib import Path
from typing import Any
import yaml

def load(path: str) -> dict[str, Any]:
    value=yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(value,dict):
        raise ValueError(f"{path} must contain a mapping")
    return value

def authority_ids(project_docs: list[dict[str,Any]]) -> set[str]:
    out=set()
    for doc in project_docs:
        for a in doc.get("authorities",[]) or []:
            if isinstance(a,dict) and a.get("id"):
                out.add(a["id"])
        for a in doc.get("artifacts",[]) or []:
            if isinstance(a,dict) and a.get("authority"):
                out.add(a["authority"])
        for b in doc.get("bindings",[]) or []:
            if isinstance(b,dict) and b.get("authority"):
                out.add(b["authority"])
    return out

def resolve(standard: dict[str,Any], aliases: dict[str,Any], project_docs: list[dict[str,Any]]) -> dict[str,Any]:
    ids=authority_ids(project_docs)
    std=standard.get("bindings",{}) or {}
    project=aliases.get("bindings",{}) or {}
    result={}
    provenance={}
    for aid in sorted(ids):
        roles=[]
        if aid in std:
            roles.extend(std[aid] or [])
            provenance.setdefault(aid,[]).append("STANDARD_ID")
        if aid in project:
            roles.extend(project[aid] or [])
            provenance.setdefault(aid,[]).append("PROJECT_ALIAS")
        if roles:
            result[aid]=sorted(set(roles))
    unresolved=sorted(ids-set(result))
    return {
        "version":1,
        "kind":"harness-derived-authority-role-bindings",
        "project":aliases.get("project"),
        "bindings":result,
        "provenance":provenance,
        "unresolved_authorities":unresolved,
    }

def main() -> int:
    p=argparse.ArgumentParser()
    p.add_argument("standard")
    p.add_argument("aliases")
    p.add_argument("project_docs",nargs="+")
    args=p.parse_args()
    result=resolve(load(args.standard),load(args.aliases),[load(x) for x in args.project_docs])
    print(yaml.safe_dump(result,sort_keys=False,allow_unicode=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
