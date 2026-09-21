#!/usr/bin/env python3
"""Research-only coverage planning experiment.

Turns activated concern gaps into Authority-routed work by combining:
- concern proof contract
- reusable Authority role competence
- project Authority role bindings
- project capability -> semantic-claim bindings
- project canonical artifact realization
- project applicability/required overlay
"""
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


def realized_capabilities(project_docs: list[dict[str, Any]]) -> set[str]:
    result: set[str] = set()
    for doc in project_docs:
        for artifact in doc.get("artifacts", []) or []:
            result.update(artifact.get("provides", []) or [])
        for binding in doc.get("bindings", []) or []:
            result.update(binding.get("provides", []) or [])
    return result


def capability_claim_index(bindings: dict[str, Any], project_docs: list[dict[str, Any]]) -> dict[str, set[str]]:
    result: dict[str, set[str]] = {}
    for item in bindings.get("bindings", []) or []:
        result.setdefault(item["capability"], set()).update(item.get("semantic_claims", []) or [])
    for doc in project_docs:
        for authority in doc.get("authorities", []) or []:
            for production in authority.get("produces", []) or []:
                if isinstance(production, dict):
                    capability = production.get("capability")
                    if capability:
                        result.setdefault(capability, set()).update(production.get("semantic_claims", []) or [])
    return result


def concern_proofs(contract: dict[str, Any]) -> dict[str, set[str]]:
    result: dict[str, set[str]] = {}
    for concern, spec in (contract.get("proofs", {}) or {}).items():
        result[concern] = set(spec.get("accepted_semantic_claims", []) or [])
    return result


def role_claims(contract: dict[str, Any]) -> dict[str, set[str]]:
    return {
        role: set(spec.get("can_produce_claims", []) or [])
        for role, spec in (contract.get("roles", {}) or {}).items()
    }


def authorities_for_claim(
    semantic_claim: str,
    roles: dict[str, set[str]],
    project_roles: dict[str, Any],
) -> list[str]:
    capable_roles = {role for role, claims in roles.items() if semantic_claim in claims}
    result = []
    for authority, assigned_roles in (project_roles.get("bindings", {}) or {}).items():
        if capable_roles & set(assigned_roles or []):
            result.append(authority)
    return sorted(result)


def derive_plan(
    proof_contract: dict[str, Any],
    role_contract: dict[str, Any],
    project_roles: dict[str, Any],
    capability_bindings: dict[str, Any],
    overlay: dict[str, Any],
    project_docs: list[dict[str, Any]],
) -> dict[str, Any]:
    proofs = concern_proofs(proof_contract)
    roles = role_claims(role_contract)
    cap_claims = capability_claim_index(capability_bindings, project_docs)
    realized_caps = realized_capabilities(project_docs)

    realized_claims: dict[str, list[str]] = {}
    for cap in sorted(realized_caps):
        for claim in sorted(cap_claims.get(cap, set())):
            realized_claims.setdefault(claim, []).append(cap)

    explicit = {d["concern"]: d for d in overlay.get("decisions", []) or []}
    required = list(overlay.get("required", []) or [])
    rows = []

    for concern in required:
        decision = explicit.get(concern)
        if decision and decision.get("state") in {"NOT_APPLICABLE", "DEFERRED"}:
            rows.append({
                "concern": concern,
                "state": decision["state"],
                "action": "NONE",
                "reason": "explicit project applicability decision",
            })
            continue

        accepted = sorted(proofs.get(concern, set()))
        present = {
            claim: realized_claims[claim]
            for claim in accepted
            if claim in realized_claims
        }
        if present:
            rows.append({
                "concern": concern,
                "state": "COVERED",
                "action": "NONE",
                "proof": present,
            })
            continue

        routes: dict[str, list[str]] = {}
        for claim in accepted:
            auths = authorities_for_claim(claim, roles, project_roles)
            if auths:
                routes[claim] = auths

        if not accepted:
            rows.append({
                "concern": concern,
                "state": "BLOCKED",
                "action": "MODEL_PROOF_CONTRACT",
                "reason": "concern has no accepted semantic-claim proof contract",
            })
        elif routes:
            rows.append({
                "concern": concern,
                "state": "MISSING",
                "action": "PRODUCE_KNOWLEDGE",
                "accepted_semantic_claims": accepted,
                "routes": routes,
            })
        else:
            rows.append({
                "concern": concern,
                "state": "BLOCKED",
                "action": "ASSIGN_AUTHORITY",
                "accepted_semantic_claims": accepted,
                "reason": "project has no Authority bound to a role that can produce an accepted semantic claim",
            })

    counts: dict[str, int] = {}
    actions: dict[str, int] = {}
    for row in rows:
        counts[row["state"]] = counts.get(row["state"], 0) + 1
        actions[row["action"]] = actions.get(row["action"], 0) + 1

    completion_ready = all(
        row["state"] in {"COVERED", "NOT_APPLICABLE", "DEFERRED"}
        for row in rows
    )
    return {
        "version": 1,
        "kind": "harness-derived-engineering-work-plan",
        "project": overlay.get("project"),
        "scope": overlay.get("scope"),
        "completion_ready": completion_ready,
        "summary": {"states": counts, "actions": actions},
        "rows": rows,
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("proof_contract")
    p.add_argument("role_contract")
    p.add_argument("project_roles")
    p.add_argument("capability_bindings")
    p.add_argument("overlay")
    p.add_argument("project_docs", nargs="+")
    args = p.parse_args()

    result = derive_plan(
        load(args.proof_contract),
        load(args.role_contract),
        load(args.project_roles),
        load(args.capability_bindings),
        load(args.overlay),
        [load(x) for x in args.project_docs],
    )
    print(yaml.safe_dump(result, sort_keys=False, allow_unicode=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
