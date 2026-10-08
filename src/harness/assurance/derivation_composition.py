"""Read-only composition of accepted, local semantic derivation links."""
from __future__ import annotations

from typing import Any


def compose_derivations(evaluations: list[dict[str, Any]]) -> dict[str, Any]:
    """Trace semantic atoms across adjacent accepted derivations, without adding graph edges."""
    if len(evaluations) < 2:
        return {"status": "REJECTED", "findings": [{"code": "CHAIN_TOO_SHORT"}], "links": []}

    findings: list[dict[str, Any]] = []
    for i, evaluation in enumerate(evaluations):
        if evaluation.get("status") != "ACCEPTED":
            findings.append({"code": "DERIVATION_NOT_ACCEPTED", "index": i})
        if i and evaluations[i - 1].get("target_capability") != evaluation.get("source_capability"):
            findings.append({"code": "CHAIN_DISCONNECTED", "index": i})

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
