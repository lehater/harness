"""Source-verifiable atomic public semantic contract *drafts* for CDR.

This read-only experimental contract models (a) candidate owned exports,
(b) explicit delegation of another Capability's exports, and (c) context.
Source quotation, owning Core registration, baseline review, exact source
snapshot and uniqueness are checked. Semantic ownership, independence and
Authority acceptance are NOT established by this validator.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from evals.project_discovery_snapshot import DiscoveryError, _required_yaml, _resolve, _sha256
from evals.cdr_contract_owner_conflicts import _explicit_target_export

KIND = "harness-cdr-public-semantic-contract-draft"
OWNED = "OWNED_EXPORT_CANDIDATE"
DELEGATED = "DELEGATED_EXPORT_REFERENCE"
CONTEXT = "CONTEXT_ONLY"
ALLOWED_ROLES = {OWNED, DELEGATED, CONTEXT}
DRAFT_STATUS = "RESEARCH_DRAFT_NOT_AUTHORITY_ACCEPTED"


def _section(text: str, label: str) -> str:
    lines = text.splitlines()
    found = []
    for i, line in enumerate(lines):
        m = re.fullmatch(r"(#{2,4})\s+(.+?)\s*", line)
        if m and m.group(2).strip() == label:
            found.append((i, len(m.group(1))))
    if len(found) != 1:
        raise DiscoveryError(f"unbound or duplicate contract section: {label}")
    start, level = found[0]
    end = len(lines)
    for i in range(start + 1, len(lines)):
        m = re.match(r"^(#{1,6})\s+", lines[i])
        if m and len(m.group(1)) <= level:
            end = i
            break
    return "\n".join(lines[start + 1:end])


def _check_exact_quote(source: Path, claim: dict[str, Any]) -> None:
    quote = claim["quote"]
    if source.suffix == ".md":
        if set(claim) - {"id", "role", "section", "quote", "delegates_to"} or "section" not in claim:
            raise DiscoveryError("Markdown claim must have a scoped section")
        bounded = _section(source.read_text(encoding="utf-8"), claim["section"])
        if bounded.count(quote) != 1:
            raise DiscoveryError("claim quote missing or nonunique in source section")
    elif source.suffix in (".yaml", ".yml"):
        if "section" in claim:
            raise DiscoveryError("YAML claim cannot use Markdown heading")
        doc = _required_yaml(source)
        if "requirement_id" in claim and "yaml_field" not in claim:
            if set(claim) - {"id", "role", "requirement_id", "quote", "delegates_to"}:
                raise DiscoveryError("unsupported structured requirement claim field")
            raw = doc.get("content", {}).get("requirements", [])
            entries = [v for v in raw if isinstance(v, dict)
                       and v.get("id") == claim["requirement_id"]]
            if (len(entries) != 1 or entries[0].get("status") != "ACCEPTED"
                    or entries[0].get("statement") != quote):
                raise DiscoveryError("quote is not exact individually accepted requirement")
        elif "yaml_field" in claim and "requirement_id" not in claim:
            if set(claim) - {"id", "role", "yaml_field", "quote", "delegates_to"}:
                raise DiscoveryError("unsupported structured YAML claim field")
            if doc.get(claim["yaml_field"]) != quote:
                raise DiscoveryError("YAML field differs from anchored semantic quote")
        else:
            raise DiscoveryError("YAML quote needs one explicit field selector")
    else:
        raise DiscoveryError("unsupported claimed source format")


def prepare_draft(root: Path, *, sha: str, manifest_path: Path,
                  target: str, expected: tuple[str, ...],
                  artifacts: dict[str, dict[str, Any]],
                  reviews: dict[str, dict[str, Any]]) -> dict[str, Any]:
    manifest_bytes = manifest_path.read_bytes()
    d = _required_yaml(manifest_path)
    if (set(d) != {"version", "kind", "status", "source_commit",
                   "target_capability", "reviewer_identity_verified",
                   "authority_acceptance_verified", "automatic_writeback_allowed",
                   "notes", "contracts"}
            or d["version"] != 1 or d["kind"] != KIND
            or d["status"] != DRAFT_STATUS or d["source_commit"] != sha
            or d["target_capability"] != target
            or d["reviewer_identity_verified"] is not False
            or d["authority_acceptance_verified"] is not False
            or d["automatic_writeback_allowed"] is not False):
        raise DiscoveryError("contract draft is unbound or claims unverified acceptance")
    if target not in artifacts or not isinstance(d["contracts"], list):
        raise DiscoveryError("target or contract entries unavailable")
    target_path = artifacts[target]["path"]
    by_id = {}
    for item in d["contracts"]:
        if not isinstance(item, dict) or set(item) != {"capability", "claims"}:
            raise DiscoveryError("unexpected provider contract shape")
        cid = item["capability"]
        if cid in by_id or cid not in expected or cid not in artifacts or cid not in reviews:
            raise DiscoveryError("duplicate or missing Core-registered provider contract")
        by_id[cid] = item
    if set(by_id) != set(expected):
        raise DiscoveryError("incomplete owned semantic contract catalog")
    path_by_id = {key: value["path"] for key, value in artifacts.items()}
    seen_claim_ids = set()
    providers = []
    delegations = []
    for cid in expected:
        item = by_id[cid]
        source = _resolve(root, artifacts[cid]["path"])
        fragments = []
        claim_ids = []
        owned = 0
        for claim in item["claims"]:
            if (not isinstance(claim, dict)
                    or not isinstance(claim.get("id"), str)
                    or not re.fullmatch(r"[A-Z][A-Z0-9-]{4,100}", claim["id"])
                    or claim["id"] in seen_claim_ids
                    or claim.get("role") not in ALLOWED_ROLES
                    or not isinstance(claim.get("quote"), str)
                    or len(claim["quote"].strip()) < 30
                    or claim["quote"] != claim["quote"].strip()):
                raise DiscoveryError("unbound/duplicate/non-substantive claim")
            seen_claim_ids.add(claim["id"])
            _check_exact_quote(source, claim)
            role = claim["role"]
            if role == DELEGATED:
                delegate = claim.get("delegates_to")
                if delegate == cid or delegate not in artifacts:
                    raise DiscoveryError("delegate must be a distinct Core provider")
                other_path = path_by_id[delegate]
                if _explicit_target_export(claim["quote"], other_path) is None:
                    raise DiscoveryError("delegation needs an explicit exact source-owned export attribution")
                delegations.append({
                    "source_capability": cid, "claim_id": claim["id"],
                    "delegates_to_capability": delegate,
                    "delegates_to_source": other_path,
                    "quote": claim["quote"], "source_sha256": _sha256(source.read_bytes()),
                })
            else:
                if "delegates_to" in claim:
                    raise DiscoveryError("an own/context claim cannot silently delegate")
                if role == OWNED:
                    for foreign, foreign_path in path_by_id.items():
                        if foreign != cid and _explicit_target_export(claim["quote"], foreign_path):
                            raise DiscoveryError("own-export candidate explicitly credits another artifact")
                    fragments.append("RESEARCH ATOMIC OWNED-EXPORT CANDIDATE ["
                                     + claim["id"] + "]: " + claim["quote"])
                    claim_ids.append(claim["id"])
                    owned += 1
        if not item["claims"] or owned == 0:
            raise DiscoveryError("provider lacks an owned export candidate")
        providers.append({
            "capability": cid,
            "source": artifacts[cid]["path"],
            "source_sha256": _sha256(source.read_bytes()),
            "review_revision": reviews[cid]["revision"],
            "evidence_status": "CONTRACT_ONLY",
            "semantic_surface": fragments,
            "source_scope": {
                "public_surface_truncated": False,
                "selection_scope_partial": True,
                "selection_mode": "ATOMIC_PUBLIC_CONTRACT_DRAFT_V1",
                "claim_role": "UNACCEPTED_OWNED_EXPORT_CANDIDATE",
                "claim_ids": claim_ids,
                "independent_ownership_review_verified": False,
                "all_source_contracts_included": False,
            },
        })
    return {
        "kind": KIND, "source_snapshot": sha, "target_capability": target,
        "manifest_sha256": _sha256(manifest_bytes),
        "provider_catalog": providers, "delegated_references": delegations,
        "authority_acceptance_verified": False,
        "independent_export_ownership_verified": False,
        "claim_set_exhaustive": False, "automatic_writeback_allowed": False,
        "status": "RESEARCH_ATOMIC_CONTRACT_CANDIDATES_NOT_ACCEPTED",
    }
