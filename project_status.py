#!/usr/bin/env python3
"""Experimental project Authority applicability registry and status projection."""
from __future__ import annotations
import argparse, json
from pathlib import Path
from typing import Any
import yaml

STATES = {"UNASSESSED", "REQUIRED", "NOT_APPLICABLE", "UNRESOLVED"}

def load(path):
    value = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    if not isinstance(value, dict):
        raise ValueError(f"{path}: expected mapping")
    return value

def catalog_ids(catalog):
    return [a["id"] for a in catalog.get("authorities", [])]

def bootstrap_registry(catalog, existing=None, core=None, authority_migrations=None):
    existing = existing or {}
    records = {r["authority_id"]: dict(r) for r in existing.get("assessments", [])}
    artifact_authorities = {a.get("authority") for a in (core or {}).get("artifacts", [])}
    unresolved_authorities = {q.get("authority") for q in (core or {}).get("questions", []) if q.get("resolution") is None}
    result = []
    migrations = authority_migrations or {}
    retired = {old for old in migrations if old not in catalog_ids(catalog)}
    conflicts = []
    for old in retired:
        if old in records and records[old].get("applicability") != "UNASSESSED":
            conflicts.append({"retired_authority": old, "previous_assessment": records[old], "replacements": migrations[old], "resolution": "MANUAL-DECISION"})
    for authority_id in catalog_ids(catalog):
        if authority_id in records:
            result.append(records[authority_id]); continue
        if authority_id in artifact_authorities:
            result.append({"authority_id": authority_id, "applicability": "REQUIRED",
                           "derivation": "EXISTING_CANONICAL_ARTIFACT",
                           "evidence": [f"core:authority:{authority_id}"],
                           "rationale": "Existing canonical project knowledge is owned by this Authority.",
                           "depends_on_evidence": [f"core:authority:{authority_id}"],
                           "reopening_conditions": ["canonical ownership/evidence changes"]})
        elif authority_id in unresolved_authorities:
            result.append({"authority_id": authority_id, "applicability": "UNRESOLVED",
                           "derivation": "EXISTING_UNRESOLVED_QUESTION",
                           "evidence": [f"core:question-authority:{authority_id}"],
                           "rationale": "Existing unresolved project question requires this Authority.",
                           "depends_on_evidence": [f"core:question-authority:{authority_id}"],
                           "reopening_conditions": ["question is resolved or project evidence changes"]})
        else:
            result.append({"authority_id": authority_id, "applicability": "UNASSESSED"})
    out = {"version": 1, "kind": "harness-project-authority-assessments", "assessments": result}
    if conflicts: out["migration_conflicts"] = conflicts
    return out

def validate_registry(catalog, registry):
    expected = set(catalog_ids(catalog)); rows = registry.get("assessments", [])
    ids = [r.get("authority_id") for r in rows]
    errors = []
    if len(ids) != len(set(ids)): errors.append("duplicate authority assessment")
    if set(ids) != expected: errors.append("registry must cover catalog exactly")
    for r in rows:
        state = r.get("applicability")
        if state not in STATES: errors.append(f"{r.get('authority_id')}: invalid applicability {state}")
        if state != "UNASSESSED":
            for f in ("evidence","rationale","depends_on_evidence","reopening_conditions"):
                if not r.get(f): errors.append(f"{r.get('authority_id')}: {f} required")
    return errors

def status(catalog, registry, core=None):
    core = core or {}
    artifacts = core.get("artifacts", [])
    questions = [q for q in core.get("questions", []) if q.get("resolution") is None]
    by_id = {r["authority_id"]: r for r in registry.get("assessments", [])}
    rows=[]
    for aid in catalog_ids(catalog):
        a=by_id[aid]; app=a["applicability"]
        owned=[x["id"] for x in artifacts if x.get("authority")==aid]
        blockers=[q["id"] for q in questions if q.get("authority")==aid]
        operational=None
        if app=="REQUIRED":
            operational="BLOCKED" if blockers else ("IN_PROGRESS" if owned else "NOT_STARTED")
        rows.append({"authority":aid,"applicability":app,"operational_status":operational,
                     "artifacts":owned,"blocking":blockers})
    return {"version":1,"kind":"harness-project-engineering-status","rows":rows}

def main():
    p=argparse.ArgumentParser(); sub=p.add_subparsers(dest="cmd",required=True)
    for name in ("bootstrap","reconcile","validate","status"):
        q=sub.add_parser(name); q.add_argument("--catalog",required=True); q.add_argument("--registry"); q.add_argument("--core"); q.add_argument("--write")
    a=p.parse_args(); catalog=load(a.catalog); reg=load(a.registry) if a.registry else None; core=load(a.core) if a.core else None
    if a.cmd in ("bootstrap","reconcile"):
        out=bootstrap_registry(catalog,reg,core)
    elif a.cmd=="validate":
        out={"valid": not (errs:=validate_registry(catalog,reg or {})),"errors":errs}
    else:
        errs=validate_registry(catalog,reg or {})
        if errs: raise SystemExit("; ".join(errs))
        out=status(catalog,reg or {},core)
    text=yaml.safe_dump(out,sort_keys=False)
    if a.write: Path(a.write).write_text(text,encoding="utf-8")
    else: print(text,end="")

if __name__=="__main__": main()
