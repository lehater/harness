"""Read-only composition of accepted, local semantic derivation links."""
from __future__ import annotations

from typing import Any

from harness.assurance.semantic_fingerprint import semantic_assertion_fingerprints


def compose_derivations(evaluations: list[dict[str, Any]], *, current_assertion_ids: dict[str, list[str]] | None = None, current_semantics: dict[str, dict[str, Any]] | None = None) -> dict[str, Any]:
    """Trace semantic atoms across adjacent accepted derivations, without adding graph edges."""
    if len(evaluations) < 2:
        return {"status": "REJECTED", "findings": [{"code": "CHAIN_TOO_SHORT"}], "links": []}

    findings: list[dict[str, Any]] = []
    for i, evaluation in enumerate(evaluations):
        if evaluation.get("status") != "ACCEPTED":
            findings.append({"code": "DERIVATION_NOT_ACCEPTED", "index": i})
        if i and evaluations[i - 1].get("target_capability") != evaluation.get("source_capability"):
            findings.append({"code": "CHAIN_DISCONNECTED", "index": i})

    if current_assertion_ids is not None:
        for i, evaluation in enumerate(evaluations):
            source_cap = evaluation.get("source_capability")
            target_cap = evaluation.get("target_capability")
            if source_cap not in current_assertion_ids or target_cap not in current_assertion_ids:
                findings.append({"code": "CURRENT_SCOPE_MISSING", "index": i})
                continue
            source_ids = set(current_assertion_ids[source_cap])
            target_ids = set(current_assertion_ids[target_cap])
            missing_required = sorted(set(evaluation.get("required_sources", [])) - source_ids)
            if missing_required:
                findings.append({"code": "STALE_REQUIRED_SOURCE_IDS", "index": i, "sources": missing_required})
            for link in evaluation.get("links", []):
                if set(link.get("sources", [])) - source_ids or set(link.get("targets", [])) - target_ids:
                    findings.append({"code": "STALE_LINK_IDS", "index": i})
                    break

    if current_semantics is not None:
        current = {cap: semantic_assertion_fingerprints(doc) for cap, doc in current_semantics.items()}
        for i, evaluation in enumerate(evaluations):
            pairs = (
                ("source", evaluation.get("source_capability")),
                ("target", evaluation.get("target_capability")),
            )
            accepted = evaluation.get("assertion_fingerprints")
            if not isinstance(accepted, dict):
                findings.append({"code": "ACCEPTED_FINGERPRINTS_MISSING", "index": i})
                continue
            for side, cap in pairs:
                if cap not in current:
                    findings.append({"code": "CURRENT_SEMANTICS_MISSING", "index": i, "capability": cap})
                    continue
                recorded = accepted.get(side)
                if not isinstance(recorded, dict):
                    findings.append({"code": "ACCEPTED_FINGERPRINTS_MISSING", "index": i, "side": side})
                    continue
                if recorded != current[cap]:
                    findings.append({"code": "SEMANTIC_FINGERPRINT_MISMATCH", "index": i, "side": side, "capability": cap})

    if findings:
        return {"status": "REJECTED", "findings": findings, "links": []}

    first = evaluations[0]
    paths: dict[str, set[str]] = {}
    for link in first.get("links", []):
        for src in link.get("sources", []):
            paths.setdefault(src, set()).update(link.get("targets", []))

    if not paths:
        findings.append({"code": "CHAIN_HAS_NO_SOURCE_LINKS"})

    for evaluation in evaluations[1:]:
        mapping: dict[str, set[str]] = {}
        for link in evaluation.get("links", []):
            for src in link.get("sources", []):
                mapping.setdefault(src, set()).update(link.get("targets", []))
        paths = {
            origin: {end for mid in mids for end in mapping.get(mid, set())}
            for origin, mids in paths.items()
        }

    missing = sorted(origin for origin, targets in paths.items() if not targets)
    if missing:
        findings.append({"code": "CHAIN_TRACE_LOST", "sources": missing})
    return {
        "status": "REJECTED" if findings else "ACCEPTED",
        "source_capability": first["source_capability"],
        "target_capability": evaluations[-1]["target_capability"],
        "links": [
            {"source": origin, "targets": sorted(targets)}
            for origin, targets in sorted(paths.items()) if targets
        ],
        "findings": findings,
    }
