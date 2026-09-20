#!/usr/bin/env python3
"""Research-only hierarchical Engineering Coverage Map renderer/validator."""

from __future__ import annotations
import argparse
from pathlib import Path
from typing import Any
import yaml

LEAF_STATES = {
    "COVERED", "MISSING", "BLOCKED", "STALE",
    "NOT_APPLICABLE", "DEFERRED", "UNASSESSED",
}

def load(path: str) -> dict[str, Any]:
    with Path(path).open(encoding="utf-8") as f:
        return yaml.safe_load(f)

def flatten_catalog(catalog: dict[str, Any]) -> tuple[dict[str, dict[str, Any]], dict[str, list[str]]]:
    nodes: dict[str, dict[str, Any]] = {}
    children: dict[str, list[str]] = {}

    def visit(node: dict[str, Any], parent: str | None = None) -> None:
        cid = node["id"]
        if cid in nodes:
            raise ValueError(f"duplicate concern id: {cid}")
        nodes[cid] = node
        children[cid] = [c["id"] for c in node.get("children", [])]
        for child in node.get("children", []):
            visit(child, cid)

    for root in catalog.get("concerns", []):
        visit(root)
    for leaf in catalog.get("quality_attribute_leaves", []):
        visit(leaf)
    return nodes, children

def aggregate(states: list[str]) -> str:
    if not states:
        return "UNASSESSED"
    s = set(states)
    if s == {"NOT_APPLICABLE"}:
        return "NOT_APPLICABLE"
    if s == {"UNASSESSED"}:
        return "UNASSESSED"
    if s == {"DEFERRED"}:
        return "DEFERRED"
    if s <= {"COVERED", "NOT_APPLICABLE"} and "COVERED" in s:
        return "COVERED"
    if "STALE" in s:
        return "STALE" if s <= {"STALE", "NOT_APPLICABLE"} else "PARTIAL"
    if "BLOCKED" in s:
        return "BLOCKED" if s <= {"BLOCKED", "NOT_APPLICABLE"} else "PARTIAL"
    if "MISSING" in s:
        return "MISSING" if s <= {"MISSING", "NOT_APPLICABLE"} else "PARTIAL"
    return "PARTIAL"

def validate(catalog: dict[str, Any], project: dict[str, Any]) -> list[str]:
    nodes, children = flatten_catalog(catalog)
    errors: list[str] = []
    seen: set[str] = set()
    for row in project.get("rows", []):
        cid = row.get("concern")
        state = row.get("state")
        if cid in seen:
            errors.append(f"duplicate row: {cid}")
        seen.add(cid)
        if cid not in nodes:
            errors.append(f"unknown concern: {cid}")
            continue
        if children.get(cid):
            errors.append(f"persisted parent state is forbidden: {cid}")
        if state not in LEAF_STATES:
            errors.append(f"invalid leaf state {state!r}: {cid}")
        if state == "NOT_APPLICABLE" and not (row.get("rationale") or row.get("applicability")):
            errors.append(f"NOT_APPLICABLE lacks rationale/evidence: {cid}")
        if state == "DEFERRED":
            d = row.get("deferral", {})
            for key in ("rationale", "owner", "reopen_when"):
                if not d.get(key):
                    errors.append(f"DEFERRED lacks {key}: {cid}")
        if state == "COVERED" and not any(row.get(k) for k in ("capabilities", "artifacts", "requirements", "evidence")):
            errors.append(f"COVERED lacks semantic evidence: {cid}")
        if state == "STALE" and not row.get("freshness"):
            errors.append(f"STALE lacks lifecycle freshness evidence: {cid}")
    return errors

def derive_tree(catalog: dict[str, Any], project: dict[str, Any]) -> dict[str, str]:
    nodes, children = flatten_catalog(catalog)
    rows = {r["concern"]: r["state"] for r in project.get("rows", [])}
    out: dict[str, str] = {}

    def state(cid: str) -> str:
        if not children[cid]:
            out[cid] = rows.get(cid, "UNASSESSED")
            return out[cid]
        out[cid] = aggregate([state(c) for c in children[cid]])
        return out[cid]

    for root in catalog.get("concerns", []):
        state(root["id"])
    return out

def should_expand(cid: str, children: dict[str, list[str]], states: dict[str, str]) -> bool:
    kids = children.get(cid, [])
    if not kids:
        return False
    child_states = [states[k] for k in kids]
    parent = states[cid]
    if parent in {"PARTIAL", "MISSING", "BLOCKED", "STALE"}:
        return True
    if any(s in {"MISSING", "BLOCKED", "STALE", "UNASSESSED"} for s in child_states):
        return True
    return len(set(child_states)) > 1

def render(catalog: dict[str, Any], project: dict[str, Any], expanded: bool = False) -> str:
    nodes, children = flatten_catalog(catalog)
    states = derive_tree(catalog, project)
    lines = [f"# Engineering Coverage Map — {project.get('project', 'project')}", ""]
    def emit(cid: str, depth: int) -> None:
        lines.append(f"{'  ' * depth}- **{nodes[cid].get('title', cid)}** [{states[cid]}]  \n  `{cid}`")
        if expanded or should_expand(cid, children, states):
            for child in children.get(cid, []):
                emit(child, depth + 1)
    for root in catalog.get("concerns", []):
        emit(root["id"], 0)
    return "\n".join(lines) + "\n"

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("catalog")
    ap.add_argument("project")
    ap.add_argument("--expanded", action="store_true")
    args = ap.parse_args()
    catalog, project = load(args.catalog), load(args.project)
    errors = validate(catalog, project)
    if errors:
        for e in errors:
            print(f"ERROR: {e}")
        return 2
    print(render(catalog, project, args.expanded), end="")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
