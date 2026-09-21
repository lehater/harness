#!/usr/bin/env python3
"""Canonical Engineering Concern activation derivation."""
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


def _capability_closure(doc: dict[str, Any], roots: list[str]) -> set[str]:
    productions: dict[str, dict[str, Any]] = {}
    for authority in doc.get("authorities", []) or []:
        if not isinstance(authority, dict):
            continue
        for production in authority.get("produces", []) or []:
            if isinstance(production, str):
                productions[production] = {"capability": production, "requires": []}
            elif isinstance(production, dict) and production.get("capability"):
                productions[production["capability"]] = production

    closure: set[str] = set()
    def include(capability: str) -> None:
        if capability in closure:
            return
        closure.add(capability)
        production = productions.get(capability)
        if not production:
            return
        for requirement in production.get("requires", []) or []:
            upstream = requirement if isinstance(requirement, str) else requirement.get("capability")
            if upstream:
                include(upstream)

    for capability in roots:
        include(capability)
    return closure


def _consumer_closure(doc: dict[str, Any], target_consumer: str) -> set[str]:
    consumers = {
        item.get("id"): item
        for item in doc.get("consumers", []) or []
        if isinstance(item, dict) and item.get("id")
    }
    if target_consumer not in consumers:
        return set()

    roots = []
    for requirement in consumers[target_consumer].get("requires", []) or []:
        capability = requirement if isinstance(requirement, str) else requirement.get("capability")
        if capability:
            roots.append(capability)
    return _capability_closure(doc, roots)


def project_signals(
    project_docs: list[dict[str, Any]],
    project_roles: dict[str, Any],
    target_consumer: str | None = None,
    scope_roots: list[str] | None = None,
) -> dict[str, set[str]]:
    capabilities: set[str] = set()
    knowledge_kinds: set[str] = set()
    authorities: set[str] = set()
    roles: set[str] = set()
    consumers: set[str] = set()

    scoped_capabilities: set[str] | None = None
    if target_consumer:
        consumers.add(target_consumer)
        closures = []
        for doc in project_docs:
            if doc.get("kind") != "harness-engineering-graph":
                continue
            consumer_scope = _consumer_closure(doc, target_consumer)
            if scope_roots:
                selected = _capability_closure(doc, scope_roots)
                unknown = set(scope_roots) - consumer_scope
                if unknown:
                    raise ValueError(
                        f"scope roots outside Consumer {target_consumer} closure: {sorted(unknown)}"
                    )
                consumer_scope &= selected
            closures.append(consumer_scope)
        nonempty = [value for value in closures if value]
        if nonempty:
            scoped_capabilities = set().union(*nonempty)

    for doc in project_docs:
        for authority in doc.get("authorities", []) or []:
            if isinstance(authority, dict):
                aid = authority.get("id")
                authority_in_scope = False
                for production in authority.get("produces", []) or []:
                    if isinstance(production, str):
                        cap = production
                        kind = None
                    elif isinstance(production, dict):
                        cap = production.get("capability")
                        kind = production.get("knowledge_kind")
                    else:
                        continue
                    if not cap:
                        continue
                    if scoped_capabilities is not None and cap not in scoped_capabilities:
                        continue
                    capabilities.add(cap)
                    authority_in_scope = True
                    if kind:
                        knowledge_kinds.add(kind)
                if aid and (scoped_capabilities is None or authority_in_scope):
                    authorities.add(aid)
        for artifact in doc.get("artifacts", []) or []:
            if isinstance(artifact, dict):
                provided=set(artifact.get("provides", []) or [])
                if scoped_capabilities is not None:
                    provided &= scoped_capabilities
                if provided:
                    if artifact.get("authority"):
                        authorities.add(artifact["authority"])
                    capabilities.update(provided)
        for binding in doc.get("bindings", []) or []:
            if isinstance(binding, dict):
                provided=set(binding.get("provides", []) or [])
                if scoped_capabilities is not None:
                    provided &= scoped_capabilities
                if provided:
                    if binding.get("authority"):
                        authorities.add(binding["authority"])
                    capabilities.update(provided)

    for authority, assigned in (project_roles.get("bindings", {}) or {}).items():
        if scoped_capabilities is None or authority in authorities:
            roles.update(assigned or [])

    return {
        "capabilities": capabilities,
        "knowledge_kinds": knowledge_kinds,
        "authorities": authorities,
        "authority_roles": roles,
        "consumers": consumers,
    }


def _contains_any(values: set[str], tokens: list[str]) -> bool:
    return any(token in value for value in values for token in tokens)


def rule_matches(rule: dict[str, Any], signals: dict[str, set[str]]) -> tuple[bool, list[str]]:
    when = rule.get("when", {}) or {}
    evidence: list[str] = []
    group_results: list[bool] = []

    kinds = when.get("knowledge_kinds_any", []) or []
    if kinds:
        hits = sorted(signals["knowledge_kinds"] & set(kinds))
        group_results.append(bool(hits))
        evidence.extend(f"knowledge_kind:{x}" for x in hits)

    roles = when.get("authority_roles_any", []) or []
    if roles:
        hits = sorted(signals["authority_roles"] & set(roles))
        group_results.append(bool(hits))
        evidence.extend(f"authority_role:{x}" for x in hits)

    tokens = when.get("capability_contains_any", []) or []
    if tokens:
        hits = [
            cap for cap in sorted(signals["capabilities"])
            if any(token in cap for token in tokens)
        ]
        group_results.append(bool(hits))
        evidence.extend(f"capability:{x}" for x in hits)

    consumer_tokens = when.get("consumer_contains_any", []) or []
    if consumer_tokens:
        hits = [
            consumer for consumer in sorted(signals["consumers"])
            if any(token in consumer for token in consumer_tokens)
        ]
        group_results.append(bool(hits))
        evidence.extend(f"consumer:{x}" for x in hits)

    mode = rule.get("match", "any")
    if mode not in {"any", "all"}:
        raise ValueError(f"activation rule {rule.get('id')} has invalid match mode: {mode}")
    if not group_results:
        return False, []
    matched = all(group_results) if mode == "all" else any(group_results)
    return matched, evidence if matched else []


def derive_activation(
    policy: dict[str, Any],
    project_roles: dict[str, Any],
    overlay: dict[str, Any],
    project_docs: list[dict[str, Any]],
    target_consumer: str | None = None,
) -> dict[str, Any]:
    target_consumer = target_consumer or overlay.get("consumer")
    scope_roots = list(overlay.get("scope_roots", []) or [])
    signals = project_signals(project_docs, project_roles, target_consumer, scope_roots)
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

    selected_scope = overlay.get("scope")

    def applies_to_scope(item: dict[str, Any]) -> bool:
        consumers = item.get("consumers", []) or []
        scopes = item.get("scopes", []) or []
        consumer_ok = not consumers or target_consumer is None or target_consumer in consumers
        scope_ok = not scopes or selected_scope is None or selected_scope in scopes
        return consumer_ok and scope_ok

    for item in overlay.get("activate", []) or []:
        if isinstance(item, str):
            concern = item
            rationale = None
            evidence = []
        else:
            if not applies_to_scope(item):
                continue
            concern = item["concern"]
            rationale = item.get("rationale")
            evidence = item.get("evidence", []) or []
        provenance.setdefault(concern, []).append({
            "source": "EXPLICIT_PROJECT_FACT",
            "rationale": rationale,
            "evidence": evidence,
        })

    decisions = {
        d["concern"]: d
        for d in overlay.get("decisions", []) or []
        if applies_to_scope(d)
    }
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
        "consumer": target_consumer,
        "scope_roots": scope_roots,
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
    p.add_argument("--consumer")
    args = p.parse_args()

    result = derive_activation(
        load(args.policy),
        load(args.project_roles),
        load(args.overlay),
        [load(x) for x in args.project_docs],
        args.consumer,
    )
    print(yaml.safe_dump(result, sort_keys=False, allow_unicode=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
