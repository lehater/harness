#!/usr/bin/env python3
"""Research-only Reference Engineering Model evolution analysis."""
from __future__ import annotations

import hashlib
import json
from typing import Any


def fingerprint(value: dict[str, Any]) -> str:
    payload=json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _ids(model: dict[str, Any], field: str) -> set[str]:
    return {
        row["id"]
        for row in model.get(field,[]) or []
        if isinstance(row,dict) and isinstance(row.get("id"),str) and row["id"]
    }


def analyze_evolution(old_model: dict[str, Any], new_model: dict[str, Any], migration: dict[str, Any] | None=None) -> dict[str, Any]:
    old_templates=_ids(old_model,"templates"); new_templates=_ids(new_model,"templates")
    old_predicates=_ids(old_model,"predicates"); new_predicates=_ids(new_model,"predicates")
    removed_templates=old_templates-new_templates; added_templates=new_templates-old_templates
    removed_predicates=old_predicates-new_predicates; added_predicates=new_predicates-old_predicates
    mapped_removed_templates=set(); mapped_added_templates=set()
    mapped_removed_predicates=set(); mapped_added_predicates=set()
    diagnostics=[]

    manifest=migration or {"operations":[]}
    if manifest.get("version")!=1 or manifest.get("kind")!="harness-reference-model-migration":
        diagnostics.append({"code":"MIGRATION_HEADER","message":"unexpected migration manifest header"})
        operations=[]
    else:
        operations=manifest.get("operations",[]) or []
        if not isinstance(operations,list):
            diagnostics.append({"code":"MIGRATION_OPERATIONS","message":"operations must be a list"})
            operations=[]

    def one(value):
        return isinstance(value,str) and bool(value)

    for i,op in enumerate(operations):
        if not isinstance(op,dict):
            diagnostics.append({"code":"MIGRATION_OPERATION_INVALID","message":f"operation {i} must be a mapping"}); continue
        kind=op.get("op")
        if kind=="rename_template":
            src,dst=op.get("from"),op.get("to")
            if not one(src) or not one(dst) or src not in old_templates or dst not in new_templates:
                diagnostics.append({"code":"MIGRATION_OPERATION_INVALID","message":f"invalid template rename at {i}"}); continue
            mapped_removed_templates.add(src); mapped_added_templates.add(dst)
        elif kind=="split_template":
            src,dst=op.get("from"),op.get("to")
            if not one(src) or src not in old_templates or not isinstance(dst,list) or len(dst)<2 or any(not one(x) or x not in new_templates for x in dst):
                diagnostics.append({"code":"MIGRATION_OPERATION_INVALID","message":f"invalid template split at {i}"}); continue
            mapped_removed_templates.add(src); mapped_added_templates.update(dst)
        elif kind=="merge_templates":
            src,dst=op.get("from"),op.get("to")
            if not isinstance(src,list) or len(src)<2 or any(not one(x) or x not in old_templates for x in src) or not one(dst) or dst not in new_templates:
                diagnostics.append({"code":"MIGRATION_OPERATION_INVALID","message":f"invalid template merge at {i}"}); continue
            mapped_removed_templates.update(src); mapped_added_templates.add(dst)
        elif kind=="rename_predicate":
            src,dst=op.get("from"),op.get("to")
            if not one(src) or not one(dst) or src not in old_predicates or dst not in new_predicates:
                diagnostics.append({"code":"MIGRATION_OPERATION_INVALID","message":f"invalid predicate rename at {i}"}); continue
            mapped_removed_predicates.add(src); mapped_added_predicates.add(dst)
        else:
            diagnostics.append({"code":"MIGRATION_OPERATION_UNKNOWN","message":f"unknown migration operation {kind!r} at {i}"})

    missing_templates=sorted(removed_templates-mapped_removed_templates)
    missing_predicates=sorted(removed_predicates-mapped_removed_predicates)
    if missing_templates or missing_predicates:
        diagnostics.append({
            "code":"MIGRATION_MAP_INCOMPLETE",
            "message":"removed reference identities require explicit migration mapping",
            "templates":missing_templates,
            "predicates":missing_predicates,
        })

    old_fp=fingerprint(old_model); new_fp=fingerprint(new_model)
    changed=old_fp!=new_fp
    status="UNCHANGED" if not changed and not diagnostics else ("MAPPED_CHANGE" if changed and not diagnostics else "INVALID")
    return {
        "version":1,
        "kind":"harness-reference-model-evolution-result",
        "status":status,
        "old_fingerprint":old_fp,
        "new_fingerprint":new_fp,
        "requires_rematerialization":changed,
        "removed_templates":sorted(removed_templates),
        "added_templates":sorted(added_templates),
        "removed_predicates":sorted(removed_predicates),
        "added_predicates":sorted(added_predicates),
        "unmapped_added_templates":sorted(added_templates-mapped_added_templates),
        "unmapped_added_predicates":sorted(added_predicates-mapped_added_predicates),
        "diagnostics":diagnostics,
    }


def materialized_capabilities(result: dict[str, Any]) -> set[str]:
    graph=result.get("graph",{}) or {}
    return {
        production["capability"]
        for authority in graph.get("authorities",[]) or []
        for production in authority.get("produces",[]) or []
        if isinstance(production,dict) and isinstance(production.get("capability"),str)
    }
