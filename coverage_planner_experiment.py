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


def _artifact_blocker_index(doc: dict[str, Any]) -> tuple[dict[str, set[str]], dict[str, set[str]]]:
    artifacts = {
        item.get("id"): item
        for item in doc.get("artifacts", []) or []
        if isinstance(item, dict) and item.get("id")
    }
    reverse: dict[str, set[str]] = {artifact_id: set() for artifact_id in artifacts}
    providers: dict[str, set[str]] = {}
    for artifact_id, artifact in artifacts.items():
        for dependency in artifact.get("depends_on", []) or []:
            if dependency in reverse:
                reverse[dependency].add(artifact_id)
        for capability in artifact.get("provides", []) or []:
            providers.setdefault(capability, set()).add(artifact_id)

    artifact_blockers: dict[str, set[str]] = {
        artifact_id: set() for artifact_id in artifacts
    }
    capability_blockers: dict[str, set[str]] = {}

    def affected(seed: str) -> set[str]:
        result = {seed}
        stack = list(reverse.get(seed, set()))
        while stack:
            current = stack.pop()
            if current in result:
                continue
            result.add(current)
            stack.extend(reverse.get(current, set()))
        return result

    for question in doc.get("questions", []) or []:
        if not isinstance(question, dict) or question.get("resolution") is not None:
            continue
        question_id = question.get("id")
        if not question_id:
            continue

        seeds = set(question.get("blocks", []) or [])
        for capability in question.get("blocks_capabilities", []) or []:
            capability_blockers.setdefault(capability, set()).add(question_id)
            seeds.update(providers.get(capability, set()))

        for seed in seeds:
            for artifact_id in affected(seed):
                if artifact_id in artifact_blockers:
                    artifact_blockers[artifact_id].add(question_id)

    return artifact_blockers, capability_blockers


def capability_realization(
    project_docs: list[dict[str, Any]],
    target_consumer: str | None = None,
    scope_roots: list[str] | None = None,
) -> dict[str, Any]:
    allowed: set[str] | None = None
    if target_consumer:
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
            allowed = set().union(*nonempty)

    providers_by_capability: dict[str, list[str]] = {}
    blockers_by_artifact: dict[str, set[str]] = {}
    direct_capability_blockers: dict[str, set[str]] = {}

    for doc in project_docs:
        artifact_blockers, capability_blockers = _artifact_blocker_index(doc)
        for artifact_id, blockers in artifact_blockers.items():
            blockers_by_artifact.setdefault(artifact_id, set()).update(blockers)
        for capability, blockers in capability_blockers.items():
            direct_capability_blockers.setdefault(capability, set()).update(blockers)

        for artifact in doc.get("artifacts", []) or []:
            if not isinstance(artifact, dict) or not artifact.get("id"):
                continue
            for capability in artifact.get("provides", []) or []:
                if allowed is not None and capability not in allowed:
                    continue
                providers_by_capability.setdefault(capability, []).append(artifact["id"])

        for binding in doc.get("bindings", []) or []:
            if not isinstance(binding, dict):
                continue
            artifact_id = binding.get("artifact")
            for capability in binding.get("provides", []) or []:
                if allowed is not None and capability not in allowed:
                    continue
                if artifact_id:
                    providers_by_capability.setdefault(capability, []).append(artifact_id)

    provided = set(providers_by_capability)
    usable: set[str] = set()
    blocked_capabilities: dict[str, list[str]] = {}
    for capability, providers in providers_by_capability.items():
        provider_blockers = {
            provider: sorted(blockers_by_artifact.get(provider, set()))
            for provider in providers
        }
        if any(not questions for questions in provider_blockers.values()):
            usable.add(capability)
        else:
            questions = sorted(
                {
                    question
                    for values in provider_blockers.values()
                    for question in values
                }
                | direct_capability_blockers.get(capability, set())
            )
            if questions:
                blocked_capabilities[capability] = questions
            else:
                usable.add(capability)

    return {
        "provided": provided,
        "usable": usable,
        "blocked": blocked_capabilities,
        "direct_blockers": {
            capability: sorted(values)
            for capability, values in direct_capability_blockers.items()
            if allowed is None or capability in allowed
        },
        "providers": {
            capability: sorted(set(values))
            for capability, values in providers_by_capability.items()
        },
    }


def realized_capabilities(
    project_docs: list[dict[str, Any]],
    target_consumer: str | None = None,
    scope_roots: list[str] | None = None,
) -> set[str]:
    return set(
        capability_realization(
            project_docs,
            target_consumer,
            scope_roots,
        )["usable"]
    )


def _normalize_claim(item: Any) -> dict[str, str]:
    if isinstance(item, str):
        return {"claim": item}
    if isinstance(item, dict) and isinstance(item.get("claim"), str):
        result = {"claim": item["claim"]}
        if item.get("subject") is not None:
            result["subject"] = item["subject"]
        return result
    raise ValueError(f"invalid semantic claim: {item!r}")


def capability_claim_index(
    bindings: dict[str, Any],
    project_docs: list[dict[str, Any]],
) -> dict[str, list[dict[str, str]]]:
    result: dict[str, list[dict[str, str]]] = {}
    for item in bindings.get("bindings", []) or []:
        capability=item["capability"]
        result.setdefault(capability, []).extend(
            _normalize_claim(value)
            for value in item.get("semantic_claims", []) or []
        )
    for doc in project_docs:
        for authority in doc.get("authorities", []) or []:
            for production in authority.get("produces", []) or []:
                if isinstance(production, dict):
                    capability = production.get("capability")
                    if capability:
                        result.setdefault(capability, []).extend(
                            _normalize_claim(value)
                            for value in production.get("semantic_claims", []) or []
                        )
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
    target_consumer: str | None = None,
) -> dict[str, Any]:
    proofs = concern_proofs(proof_contract)
    roles = role_claims(role_contract)
    cap_claims = capability_claim_index(capability_bindings, project_docs)
    scope_roots = list(overlay.get("scope_roots", []) or [])
    realization = capability_realization(project_docs, target_consumer, scope_roots)
    realized_caps = set(realization["usable"])
    provided_caps = set(realization["provided"])

    scoped_caps: set[str] | None = None
    if target_consumer:
        closures = []
        for doc in project_docs:
            if doc.get("kind") != "harness-engineering-graph":
                continue
            consumer_scope = _consumer_closure(doc, target_consumer)
            if scope_roots:
                consumer_scope &= _capability_closure(doc, scope_roots)
            closures.append(consumer_scope)
        nonempty=[value for value in closures if value]
        if nonempty:
            scoped_caps=set().union(*nonempty)

    producer_by_capability: dict[str, str] = {}
    production_by_capability: dict[str, dict[str, Any]] = {}
    for doc in project_docs:
        for authority in doc.get("authorities", []) or []:
            if not isinstance(authority, dict) or not authority.get("id"):
                continue
            for production in authority.get("produces", []) or []:
                if isinstance(production, str):
                    producer_by_capability[production] = authority["id"]
                    production_by_capability[production] = {
                        "capability": production,
                        "requires": [],
                    }
                elif isinstance(production, dict) and production.get("capability"):
                    producer_by_capability[production["capability"]] = authority["id"]
                    production_by_capability[production["capability"]] = production

    realized_claims: dict[str, list[str]] = {}
    for cap in sorted(realized_caps):
        for claim_info in cap_claims.get(cap, []):
            if claim_info.get("subject") is None:
                realized_claims.setdefault(claim_info["claim"], []).append(cap)

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

        blocked_proof_questions = sorted(
            {
                question
                for cap, claims_for_cap in cap_claims.items()
                if cap in provided_caps and cap not in realized_caps
                for claim_info in claims_for_cap
                if claim_info["claim"] in accepted
                for question in realization["blocked"].get(cap, [])
            }
        )
        if blocked_proof_questions:
            rows.append({
                "concern": concern,
                "state": "BLOCKED",
                "action": "RESOLVE_QUESTIONS",
                "accepted_semantic_claims": accepted,
                "questions": blocked_proof_questions,
            })
            continue

        subject_instances = []
        for cap, claims_for_cap in cap_claims.items():
            if scoped_caps is not None and cap not in scoped_caps:
                continue
            for claim_info in claims_for_cap:
                if claim_info["claim"] in accepted and claim_info.get("subject") is not None:
                    subject_instances.append({
                        "claim": claim_info["claim"],
                        "subject": claim_info["subject"],
                        "capability": cap,
                        "realized": cap in realized_caps,
                    })

        if subject_instances:
            missing_instances=[item for item in subject_instances if not item["realized"]]
            if not missing_instances:
                rows.append({
                    "concern": concern,
                    "state": "COVERED",
                    "action": "NONE",
                    "proof_instances": subject_instances,
                })
                continue
        else:
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

        production_candidates = []
        for cap, claims_for_cap in cap_claims.items():
            if scoped_caps is not None and cap not in scoped_caps:
                continue
            if cap in provided_caps:
                continue
            for claim_info in claims_for_cap:
                if claim_info["claim"] not in accepted:
                    continue
                production = production_by_capability.get(cap, {})
                prerequisites = []
                for requirement in production.get("requires", []) or []:
                    upstream = (
                        requirement
                        if isinstance(requirement, str)
                        else requirement.get("capability")
                    )
                    if upstream:
                        prerequisites.append(upstream)
                missing_prerequisites = sorted(
                    prerequisite
                    for prerequisite in prerequisites
                    if prerequisite not in realized_caps
                )
                direct_questions = realization["direct_blockers"].get(cap, [])
                production_candidates.append({
                    "claim": claim_info["claim"],
                    **(
                        {"subject": claim_info["subject"]}
                        if claim_info.get("subject") is not None
                        else {}
                    ),
                    "capability": cap,
                    "authority": producer_by_capability.get(cap),
                    "requires": sorted(prerequisites),
                    "missing_prerequisites": missing_prerequisites,
                    "questions": direct_questions,
                    "ready": not missing_prerequisites and not direct_questions,
                })

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
        elif production_candidates:
            ready_candidates = [
                item for item in production_candidates if item["ready"]
            ]
            blocked_questions = sorted(
                {
                    question
                    for item in production_candidates
                    for question in item.get("questions", [])
                }
            )
            row={
                "concern": concern,
                "state": "MISSING",
                "action": (
                    "PRODUCE_CAPABILITY"
                    if ready_candidates
                    else (
                        "RESOLVE_QUESTIONS"
                        if blocked_questions
                        else "WAIT_FOR_PREREQUISITES"
                    )
                ),
                "accepted_semantic_claims": accepted,
                "production_candidates": production_candidates,
                "ready_production_candidates": ready_candidates,
                **({"questions": blocked_questions} if blocked_questions else {}),
            }
            if subject_instances:
                row["missing_instances"]=[
                    item for item in subject_instances if not item["realized"]
                ]
                row["covered_instances"]=[
                    item for item in subject_instances if item["realized"]
                ]
            rows.append(row)
        elif routes:
            rows.append({
                "concern": concern,
                "state": "MISSING",
                "action": "MODEL_PRODUCTION_CONTRACT",
                "accepted_semantic_claims": accepted,
                "routes": routes,
                "reason": (
                    "A capable Authority role exists, but no in-scope Capability "
                    "declares an accepted semantic claim for this concern."
                ),
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
        "consumer": target_consumer,
        "scope_roots": scope_roots,
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
    p.add_argument("--consumer")
    args = p.parse_args()

    result = derive_plan(
        load(args.proof_contract),
        load(args.role_contract),
        load(args.project_roles),
        load(args.capability_bindings),
        load(args.overlay),
        [load(x) for x in args.project_docs],
        args.consumer,
    )
    print(yaml.safe_dump(result, sort_keys=False, allow_unicode=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
