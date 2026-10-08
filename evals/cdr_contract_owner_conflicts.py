"""Conservative cross-artifact export-owner conflict detection for CDR.

This is a narrow, inspectable negative-evidence check, NOT an autonomous
semantic ownership or directness classifier. An accepted source may describe
another artifact's published output; that paragraph is not, by itself,
evidence that the quoting source exports the quoted target's meaning.
"""
from __future__ import annotations

import re
from typing import Any


_EXPORT_VERBS = re.compile(
    r"^[\x60'\"\s]*(?:explicitly\s+)?"
    r"(?:provides|defines|owns|publishes|is\s+responsible\s+for)\b",
    re.IGNORECASE,
)


def _explicit_target_export(claim: str, target_path: str) -> str | None:
    """Find a direct textual reference declaring the target file as producer.

    Do not infer ownership from mere filename occurrence, embeddings, graph
    paths, keywords or topic similarity. Return a bounded unmodified quote.
    """
    if not isinstance(target_path, str) or not target_path:
        return None
    pattern = re.compile(r"(?<![A-Za-z0-9_/-])" + re.escape(target_path) +
                         r"(?![A-Za-z0-9_./-])", flags=re.IGNORECASE)
    for match in pattern.finditer(claim):
        suffix = claim[match.end():match.end() + 140]
        if _EXPORT_VERBS.match(suffix):
            return claim[max(0, match.start() - 30):
                         min(len(claim), match.end() + 150)]
    return None


def delegated_target_claims(case: dict[str, Any],
                            prediction: dict[str, Any]) -> list[dict[str, Any]]:
    """Flag model citations to passages that explicitly delegate to target.

    Does not depend on original requires and never approves a proposed edge.
    """
    target = case["target"]
    obligations = target["output_obligations"]
    paths = {
        o["source"]["path"] for o in obligations
        if isinstance(o.get("source"), dict)
        and isinstance(o["source"].get("path"), str)
    }
    if len(paths) != 1:
        return []  # No unambiguous source-owned target artifact available.
    target_path = next(iter(paths))
    providers = {p["capability"]: p for p in case["provider_catalog"]}
    conflicts = []
    for need in prediction.get("input_needs", []):
        provider = providers[need["provider"]]
        provider_path = provider.get("source")
        if provider_path == target_path:
            continue
        index = need["claim_index"]
        claim = provider["semantic_surface"][index]
        excerpt = _explicit_target_export(claim, target_path)
        if excerpt is None:
            continue
        conflicts.append({
            "provider": need["provider"],
            "obligation": need["obligation"],
            "claim_index": index,
            "provider_source_path": provider_path,
            "target_export_artifact": target_path,
            "exact_delegation_excerpt": excerpt,
            "disposition": "BLOCK_PROVIDER_AS_TARGET_EXPORT_OWNER_EVIDENCE",
            "independent_ownership_dispute_review_required": True,
            "semantic_directness_adjudicated": False,
        })
    return conflicts
