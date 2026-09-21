#!/usr/bin/env python3
"""Generic subject-obligation derivation and proof for Engineering Coverage."""
from __future__ import annotations
from typing import Any
import re

from coverage_planner import (
    _coverage_extended_scope,
    capability_claim_index,
    capability_realization,
    concern_proofs,
    declared_capability_claim_index,
)


TERMINAL_STATES = {"COVERED", "NOT_APPLICABLE", "DEFERRED"}


def _accepted_requirement_ids(source: dict[str, Any]) -> set[str]:
    """Extract accepted atomic requirement identities from an adapted canonical source."""
    if source.get("kind") == "harness-markdown-scope-source":
        text = source.get("text", "")
        if not isinstance(text, str):
            raise ValueError("markdown scope source text must be a string")
        status_match = re.search(r"(?im)^Status:\\s*[:]?\\s*`?([^\\n`]+)`?\\.?\\s*$", text)
        if not status_match or "accepted" not in status_match.group(1).lower():
            return set()
        return {
            match.group("id")
            for match in re.finditer(
                r"(?m)^\\s*-\\s+\\[(?P<id>[A-Z][A-Z0-9_.-]+)\\]\\s+",
                text,
            )
        }

    content = source.get("content", {}) or {}
    requirements = content.get("requirements", []) or []
    result: set[str] = set()
    for item in requirements:
        if not isinstance(item, dict):
            continue
        requirement_id = item.get("id")
        if item.get("status") == "ACCEPTED" and isinstance(requirement_id, str) and requirement_id:
            result.add(requirement_id)
    return result

def validate_subject_obligations(
    obligations: dict[str, Any],
    source: dict[str, Any],
    *,
    consumer: str,
    scope: str,
) -> dict[str, Any]:
    if obligations.get("version") != 1:
        raise ValueError("subject obligations version must be 1")
    if obligations.get("kind") != "harness-coverage-subject-obligations":
        raise ValueError("unexpected subject obligations kind")
    if obligations.get("consumer") != consumer:
        raise ValueError(
            f"subject obligations consumer mismatch: {obligations.get('consumer')} != {consumer}"
        )
    if obligations.get("scope") != scope:
        raise ValueError(
            f"subject obligations scope mismatch: {obligations.get('scope')} != {scope}"
        )

    accepted = _accepted_requirement_ids(source)
    classified: set[str] = set()
    seen_instances: set[tuple[str, str]] = set()

    for item in obligations.get("subjects", []) or []:
        if not isinstance(item, dict):
            raise ValueError("subject obligation must be a mapping")
        subject = item.get("subject")
        concerns = item.get("concerns", []) or []
        refs = item.get("requirement_refs", []) or []
        state = item.get("state", "REQUIRED")
        if not isinstance(subject, str) or not subject:
            raise ValueError("subject obligation subject is required")
        if state not in {"REQUIRED", "NOT_APPLICABLE", "DEFERRED", "QUESTION"}:
            raise ValueError(f"invalid subject obligation state: {state}")
        if state != "REQUIRED" and not str(item.get("rationale", "")).strip():
            raise ValueError(f"{state} subject obligation {subject} requires rationale")
        if not isinstance(concerns, list) or not concerns:
            raise ValueError(f"subject obligation {subject} must declare concerns")
        if not isinstance(refs, list) or not refs:
            raise ValueError(f"subject obligation {subject} must reference accepted requirements")
        for concern in concerns:
            if not isinstance(concern, str) or not concern:
                raise ValueError(f"subject obligation {subject} has invalid concern")
            key = (concern, subject)
            if key in seen_instances:
                raise ValueError(f"duplicate subject obligation instance: {concern}/{subject}")
            seen_instances.add(key)
        unknown = set(refs) - accepted
        if unknown:
            raise ValueError(
                f"subject obligation {subject} references unknown/non-accepted requirements: {sorted(unknown)}"
            )
        classified.update(refs)

    for item in obligations.get("excluded_requirements", []) or []:
        if not isinstance(item, dict):
            raise ValueError("excluded requirement must be a mapping")
        requirement_id = item.get("requirement")
        rationale = str(item.get("rationale", "")).strip()
        if requirement_id not in accepted:
            raise ValueError(
                f"excluded requirement is unknown/non-accepted: {requirement_id}"
            )
        if not rationale:
            raise ValueError(f"excluded requirement {requirement_id} requires rationale")
        classified.add(requirement_id)

    unclassified = sorted(accepted - classified)
    return {
        "accepted_requirement_count": len(accepted),
        "classified_requirement_count": len(classified & accepted),
        "unclassified_requirements": unclassified,
        "source_complete": not unclassified,
    }


def derive_subject_obligation_rows(
    *,
    obligations: dict[str, Any],
    source: dict[str, Any],
    graph: dict[str, Any],
    project_docs: list[dict[str, Any]],
    proof_contract: dict[str, Any],
    capability_bindings: dict[str, Any],
    consumer: str,
    scope: str,
    scope_roots: list[str] | None = None,
    extension_capabilities: set[str] | None = None,
) -> dict[str, Any]:
    validation = validate_subject_obligations(
        obligations, source, consumer=consumer, scope=scope
    )
    proofs = concern_proofs(proof_contract)
    declared = declared_capability_claim_index(capability_bindings, project_docs)
    usable_claims = capability_claim_index(capability_bindings, project_docs)
    realization = capability_realization(
        project_docs,
        consumer,
        scope_roots,
        extension_capabilities,
    )
    realized_caps = set(realization["usable"])
    provided_caps = set(realization["provided"])
    scoped_caps = _coverage_extended_scope(
        graph,
        consumer,
        scope_roots,
        extension_capabilities,
    )

    rows: list[dict[str, Any]] = []
    if validation["unclassified_requirements"]:
        rows.append(
            {
                "concern": "meta.subject-inventory",
                "subject": "__accepted_scope__",
                "state": "MISSING",
                "action": "CLASSIFY_ACCEPTED_SCOPE",
                "requirement_refs": validation["unclassified_requirements"],
                "reason": "accepted requirements exist without a subject or explicit exclusion",
            }
        )

    for item in obligations.get("subjects", []) or []:
        subject = item["subject"]
        requirement_refs = sorted(set(item.get("requirement_refs", []) or []))
        declared_state = item.get("state", "REQUIRED")

        for concern in item.get("concerns", []) or []:
            base = {
                "concern": concern,
                "subject": subject,
                "requirement_refs": requirement_refs,
                "obligation_provenance": item.get("provenance", []) or [],
            }
            if declared_state in {"NOT_APPLICABLE", "DEFERRED"}:
                rows.append(
                    {
                        **base,
                        "state": declared_state,
                        "action": "NONE",
                        "reason": item["rationale"],
                    }
                )
                continue
            if declared_state == "QUESTION":
                rows.append(
                    {
                        **base,
                        "state": "BLOCKED",
                        "action": "RESOLVE_QUESTION",
                        "reason": item["rationale"],
                        **({"question": item["question"]} if item.get("question") else {}),
                    }
                )
                continue

            accepted_claims = sorted(proofs.get(concern, set()))
            exact_proofs = []
            candidates = []
            for cap, claims in usable_claims.items():
                if cap not in scoped_caps:
                    continue
                for claim in claims:
                    if claim["claim"] in accepted_claims and claim.get("subject") == subject:
                        if cap in realized_caps:
                            exact_proofs.append(
                                {"claim": claim["claim"], "subject": subject, "capability": cap}
                            )
            if exact_proofs:
                rows.append(
                    {
                        **base,
                        "state": "COVERED",
                        "action": "NONE",
                        "proof_instances": exact_proofs,
                    }
                )
                continue

            for cap, claims in declared.items():
                if cap not in scoped_caps or cap in provided_caps:
                    continue
                for claim in claims:
                    if claim["claim"] in accepted_claims and claim.get("subject") == subject:
                        candidates.append(
                            {
                                "capability": cap,
                                "claim": claim["claim"],
                                "subject": subject,
                            }
                        )
            rows.append(
                {
                    **base,
                    "state": "MISSING",
                    "action": "PRODUCE_CAPABILITY" if candidates else "MODEL_PRODUCTION_CONTRACT",
                    "accepted_semantic_claims": accepted_claims,
                    **({"production_candidates": candidates} if candidates else {}),
                    "reason": (
                        "required subject has declared subject-scoped proof capability that is not realized"
                        if candidates
                        else "required subject has no in-scope subject-scoped proof contract"
                    ),
                }
            )

    remaining = [row for row in rows if row["state"] not in TERMINAL_STATES]
    return {
        "kind": "harness-derived-subject-obligation-evaluation",
        "consumer": consumer,
        "scope": scope,
        "source_validation": validation,
        "rows": rows,
        "remaining_work": remaining,
        "completion_ready": not remaining,
    }
