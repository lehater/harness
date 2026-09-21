#!/usr/bin/env python3
"""Research-only Engineering Concern activation derivation."""
from __future__ import annotations
import argparse
from pathlib import Path
from typing import Any
import yaml


def load(path: str) -> dict[str, Any]:
    value = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a mapping")
    return value


def project_signals(project_docs: list[dict[str, Any]], project_roles: dict[str, Any]) -> dict[str, set[str]]:
    capabilities: set[str] = set()
    knowledge_kinds: set[str] = set()
    authorities: set[str] = set()
    roles: set[str] = set()

    for doc in project_docs:
        for authority in doc.get("authorities", []) or []:
            if isinstance(authority, dict):
                aid = authority.get("id")
                if aid:
                    authorities.add(aid)
                for production in authority.get("produces", []) or []:
                    if isinstance(production, str):
                        capabilities.add(production)
                    elif isinstance(production, dict):
                        cap = production.get("capability")
                        if cap:
                            capabilities.add(cap)
                        kind = production.get("knowledge_kind")
                        if kind:
                            knowledge_kinds.add(kind)
        for artifact in doc.get("artifacts", []) or []:
            if isinstance(artifact, dict):
                authorities.add(artifact.get("authority")) if artifact.get("authority") else None
                capabilities.update(artifact.get("provides", []) or [])
        for binding in doc.get("bindings", []) or []:
            if isinstance(binding, dict):
                if binding.get("authority"):
                    authorities.add(binding["authority"])
                capabilities.update(binding.get("provides", []) or [])

    for authority, assigned in (project_roles.get("bindings", {}) or {}).items():
        authorities.add(authority)
        roles.update(assigned or [])

    return {
        "capabilities": capabilities,
        "knowledge_kinds": knowledge_kinds,
        "authorities": authorities,
        "authority_roles": roles,
    }


def _contains_any(values: set[str], tokens: list[str]) -> bool:
    return any(token in value for value in values for token in tokens)


def rule_matches(rule: dict[str, Any], signals: dict[str, set[str]]) -> tuple[bool, list[str]]:
    when = rule.get("when", {}) or {}
    matched: list[str] = []

    kinds = when.get("knowledge_kinds_any", []) or []
    if kinds:
        hits = sorted(signals["knowledge_kinds"] & set(kinds))
        if hits:
            matched.extend(f"knowledge_kind:{x}" for x in hits)

    roles = when.get("authority_roles_any", []) or []
    if roles:
        hits = sorted(signals["authority_roles"] & set(roles))
        if hits:
            matched.extend(f"authority_role:{x}" for x in hits)

    tokens = when.get("capability_contains_any", []) or []
    if tokens:
        for cap in sorted(signals["capabilities"]):
            if any(token in cap for token in tokens):
                matched.append(f"capability:{cap}")

    # Rule semantics: any declared structural signal group may activate.
    # Rules that need conjunction must encode a more specific machine signal instead.
    return bool(matched), matched


def derive_activation(
    policy: dict[str, Any],
    project_roles: dict[str, Any],
    overlay: dict[str, Any],
    project_docs: list[dict[str, Any]],
) -> dict[str, Any]:
    signals = project_signals(project_docs, project_roles)
    provenance: dict[str, list[dict[str, Any]]] = {}

    for concern in policy.get("baseline", []) or []:
        provenance.setdefault(concern, []).append({
            "source": "BASELINE",
            "policy": policy.get("id"),
        })

    for rule in policy.get("rules", []) or []:
        matched, evidence = rule_matches(rule, signals)
        if not matched:
            continue
        for concern in rule.get("activate", []) or []:
            provenance.setdefault(concern, []).append({
                "source": "RULE",
                "rule": rule["id"],
                "signals": evidence,
            })

    for item in overlay.get("activate", []) or []:
        if isinstance(item, str):
            concern = item
            rationale = None
            evidence = []
        else:
            concern = item["concern"]
            rationale = item.get("rationale")
            evidence = item.get("evidence", []) or []
        provenance.setdefault(concern, []).append({
            "source": "EXPLICIT_PROJECT_FACT",
            "rationale": rationale,
            "evidence": evidence,
        })

    decisions = {d["concern"]: d for d in overlay.get("decisions", []) or []}
    rows = []
    for concern in sorted(provenance):
        decision = decisions.get(concern)
        rows.append({
            "concern": concern,
            "activated": True,
            "provenance": provenance[concern],
            **({"applicability_decision": decision} if decision else {}),
        })

    return {
        "version": 1,
        "kind": "harness-derived-concern-activation",
        "project": overlay.get("project"),
        "scope": overlay.get("scope"),
        "activated_count": len(rows),
        "rows": rows,
        "signals": {
            key: sorted(values)
            for key, values in signals.items()
        },
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("policy")
    p.add_argument("project_roles")
    p.add_argument("overlay")
    p.add_argument("project_docs", nargs="+")
    args = p.parse_args()

    result = derive_activation(
        load(args.policy),
        load(args.project_roles),
        load(args.overlay),
        [load(x) for x in args.project_docs],
    )
    print(yaml.safe_dump(result, sort_keys=False, allow_unicode=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
