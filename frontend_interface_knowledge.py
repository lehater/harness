#!/usr/bin/env python3
"""Semantic closure checks for granular frontend UX knowledge."""
from __future__ import annotations
from typing import Any

def _finding(findings: list[dict[str, Any]], code: str, message: str, **ctx: Any) -> None:
    findings.append({"code": code, "message": message, **ctx})

def _task_rows(task_model: dict[str, Any]) -> dict[str, dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    def walk(items: Any) -> None:
        if not isinstance(items, list):
            return
        for item in items:
            if not isinstance(item, dict):
                continue
            tid=item.get("id")
            if isinstance(tid,str) and tid:
                rows[tid]=item
            walk(item.get("tasks"))
            walk(item.get("subtasks"))
    for goal in task_model.get("goals",[]) or []:
        if isinstance(goal,dict):
            walk(goal.get("tasks"))
    return rows

def _indexed(rows: Any, *, kind: str, findings: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    result={}
    if not isinstance(rows,list):
        _finding(findings,f"INVALID_{kind.upper()}_LIST",f"{kind} list must be a list")
        return result
    for row in rows:
        if not isinstance(row,dict) or not isinstance(row.get("id"),str) or not row["id"]:
            _finding(findings,f"INVALID_{kind.upper()}",f"{kind} requires non-empty id")
            continue
        rid=row["id"]
        if rid in result:
            _finding(findings,f"DUPLICATE_{kind.upper()}",f"duplicate {kind} id {rid}",id=rid)
            continue
        result[rid]=row
    return result

def required_screen_ids(topology: dict[str, Any]) -> set[str]:
    return {
        row["id"] for row in topology.get("views",[]) or []
        if isinstance(row,dict) and isinstance(row.get("id"),str) and row["id"]
        and row.get("screen_required",True) is not False
    }

def evaluate_frontend_ux_closure(task_model, conceptual_model, information_architecture, interaction_design, topology):
    findings=[]
    tasks=_task_rows(task_model)
    user_tasks={tid for tid,row in tasks.items() if row.get("responsibility")=="USER"}

    concepts=_indexed(conceptual_model.get("concepts",[]) or [],kind="concept",findings=findings)
    modes=_indexed(conceptual_model.get("modes",[]) or [],kind="mode",findings=findings)
    conceptual_ids=set(concepts)|set(modes)

    locations=_indexed(information_architecture.get("locations",[]) or [],kind="location",findings=findings)
    for lid,row in locations.items():
        if not isinstance(row.get("purpose"),str) or not row["purpose"].strip():
            _finding(findings,"MISSING_LOCATION_PURPOSE",f"location {lid} requires purpose",location=lid)
        for ref in row.get("concept_refs",[]) or []:
            if ref not in conceptual_ids:
                _finding(findings,"UNKNOWN_CONCEPT_REF",f"location {lid} references unknown conceptual id {ref}",location=lid,ref=ref)

    contexts=_indexed(interaction_design.get("contexts",[]) or [],kind="interaction_context",findings=findings)
    task_coverage=set()
    for cid,row in contexts.items():
        refs=row.get("task_refs",[]) or []
        if not isinstance(refs,list) or not refs:
            _finding(findings,"MISSING_INTERACTION_TASK_REF",f"interaction context {cid} requires task_refs",interaction_context=cid)
        for ref in refs:
            if ref not in tasks:
                _finding(findings,"UNKNOWN_TASK_REF",f"interaction context {cid} references unknown task {ref}",interaction_context=cid,task=ref)
            elif ref in user_tasks:
                task_coverage.add(ref)

    no_ui=set()
    for row in interaction_design.get("task_dispositions",[]) or []:
        if not isinstance(row,dict):
            continue
        task_ref=row.get("task_ref")
        if row.get("disposition")=="no-ui" and isinstance(task_ref,str):
            rationale=row.get("rationale")
            if not isinstance(rationale,str) or not rationale.strip():
                _finding(findings,"NO_UI_REQUIRES_RATIONALE",f"task {task_ref} no-ui disposition requires rationale",task=task_ref)
            elif task_ref not in user_tasks:
                _finding(findings,"NO_UI_UNKNOWN_USER_TASK",f"no-ui disposition references unknown/non-USER task {task_ref}",task=task_ref)
            else:
                no_ui.add(task_ref)
    for task in sorted(user_tasks-task_coverage-no_ui):
        _finding(findings,"UNCOVERED_USER_TASK",f"USER task {task} has no interaction context or no-ui disposition",task=task)

    views=_indexed(topology.get("views",[]) or [],kind="view",findings=findings)
    context_to_views={cid:set() for cid in contexts}
    for vid,row in views.items():
        if not isinstance(row.get("responsibility"),str) or not row["responsibility"].strip():
            _finding(findings,"MISSING_VIEW_RESPONSIBILITY",f"view {vid} requires one primary responsibility",view=vid)
        if row.get("location_ref") not in locations:
            _finding(findings,"UNKNOWN_VIEW_LOCATION",f"view {vid} references unknown IA location {row.get('location_ref')}",view=vid)
        refs=row.get("interaction_context_refs",[]) or []
        structural=row.get("structural",False) is True
        if (not isinstance(refs,list) or not refs) and not structural:
            _finding(findings,"MISSING_VIEW_INTERACTION_CONTEXT",f"non-structural view {vid} requires interaction_context_refs",view=vid)
        if structural and refs:
            _finding(findings,"STRUCTURAL_VIEW_HAS_TASK_CONTEXT",f"structural view {vid} must not claim task interaction contexts",view=vid)
        for ref in refs:
            if ref not in contexts:
                _finding(findings,"UNKNOWN_INTERACTION_CONTEXT_REF",f"view {vid} references unknown interaction context {ref}",view=vid,ref=ref)
            else:
                context_to_views[ref].add(vid)

    non_view=set()
    for row in topology.get("non_view_contexts",[]) or []:
        if not isinstance(row,dict):
            continue
        ref=row.get("interaction_context_ref")
        rationale=row.get("rationale")
        if ref in contexts and isinstance(rationale,str) and rationale.strip():
            non_view.add(ref)
    for cid,mapped in sorted(context_to_views.items()):
        if not mapped and cid not in non_view:
            _finding(findings,"UNMAPPED_INTERACTION_CONTEXT",f"interaction context {cid} has no topology view or non-view disposition",interaction_context=cid)

    for vid,row in views.items():
        parent=row.get("parent")
        if parent!="ROOT" and parent not in views:
            _finding(findings,"UNKNOWN_VIEW_PARENT",f"view {vid} parent {parent} is not ROOT or another view",view=vid)
        if parent==vid:
            _finding(findings,"SELF_PARENT_VIEW",f"view {vid} cannot parent itself",view=vid)
        for ref in row.get("exits",[]) or []:
            if ref not in views:
                _finding(findings,"UNKNOWN_VIEW_EXIT",f"view {vid} exits to unknown view {ref}",view=vid,ref=ref)

    task_to_view=set()
    for cid,row in contexts.items():
        if not context_to_views.get(cid):
            continue
        for task_ref in row.get("task_refs",[]) or []:
            if task_ref in user_tasks:
                task_to_view.add(task_ref)
    for task in sorted(user_tasks-task_to_view-no_ui):
        _finding(findings,"USER_TASK_WITHOUT_VIEW",f"USER task {task} does not reach any topology view",task=task)

    return {
        "version":1,
        "kind":"harness-frontend-ux-closure-evaluation",
        "status":"ACCEPTED" if not findings else "REJECTED",
        "user_tasks":sorted(user_tasks),
        "interaction_contexts":sorted(contexts),
        "views":sorted(views),
        "required_screen_ids":sorted(required_screen_ids(topology)),
        "findings":findings,
    }
