"""Read-only audit of model-proposed *new* direct prerequisites.

This detects input-design circularity (target obligation copied from the
candidate provider) and existing transitive access through retained direct
sources. Neither condition proves that a direct edge is needed or unneeded.
The evaluator has no permission to alter the project graph.
"""
from __future__ import annotations

from collections import deque
from typing import Any


def _via_kept_sources(
    upstream: str,
    kept: set[str],
    productions: dict[str, dict[str, Any]],
) -> list[list[str]]:
    """Find shortest existing path via each retained immediate supplier."""
    paths: list[list[str]] = []
    for first in sorted(kept):
        if first == upstream:
            continue
        queue: deque[list[str]] = deque([[first]])
        seen = {first}
        while queue:
            path = queue.popleft()
            if path[-1] == upstream:
                paths.append(path)
                break
            for item in productions.get(path[-1], {}).get("requires", []):
                node = item.get("capability") if isinstance(item, dict) else None
                if isinstance(node, str) and node not in seen:
                    seen.add(node)
                    queue.append(path + [node])
    return paths


def audit_additions(
    case: dict[str, Any],
    prediction: dict[str, Any],
    *,
    existing_requires: set[str],
    productions: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    """Flag confounded direct edges without deciding them.

    The pilot's selected upstream source sections were imported into target
    obligations. If a proposed provider only supports obligations copied
    from its own source, its directness cannot be inferred from that evidence.
    """
    target = case["target"]
    origin = {
        ob["id"]: ob.get("source", {}).get("capability")
        for ob in target["output_obligations"]
    }
    proposed = set(prediction["proposed_requires"])
    kept = existing_requires & proposed
    output: list[dict[str, Any]] = []
    for provider in sorted(proposed - existing_requires):
        needs = [
            n for n in prediction["input_needs"]
            if isinstance(n, dict) and n.get("provider") == provider
        ]
        echoes = [
            n["obligation"] for n in needs
            if origin.get(n.get("obligation")) == provider
        ]
        non_echoes = [
            n["obligation"] for n in needs
            if origin.get(n.get("obligation")) != provider
        ]
        paths = _via_kept_sources(provider, kept, productions)
        reasons: list[str] = []
        if echoes:
            reasons.append("SUPPLIER_TEXT_COPIED_INTO_TARGET_OBLIGATION")
        if needs and not non_echoes:
            reasons.append("NO_NON_ECHO_DIRECT_CONSUMPTION_EVIDENCE")
        if paths:
            reasons.append("ALREADY_REACHABLE_VIA_RETAINED_DIRECT_SOURCE")
        # Even an unconfounded direct need is still a model hypothesis:
        # source references are not semantic entailment or necessity proof.
        reasons.append("INDEPENDENT_DIRECTNESS_NOT_ESTABLISHED")
        output.append({
            "provider": provider,
            "status": "DIRECTNESS_UNPROVEN",
            "source_echo_obligations": sorted(set(echoes)),
            "non_echo_obligations": sorted(set(non_echoes)),
            "existing_transitive_paths": paths,
            "reasons": reasons,
            "requires_independent_review": True,
            "automatic_writeback_allowed": False,
        })
    return output
