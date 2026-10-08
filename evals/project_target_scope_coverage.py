"""Source-anchored inventory of *draft* target-obligation coverage.

This report is not an agent oracle or an adopted target contract. It extracts
bounded source statements from the immutable accepted upstream artifact set
and points out which statements still need independent target-owner review.
Section-level cross-references are hints, never semantic-coverage evidence.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from evals.project_discovery_snapshot import (
    DiscoveryError, _commit, _required_yaml, _resolve,
    _heading_scope, _markdown_claims, _accepted_requirement_inventory,
)

SCOPE_TYPES = {"MARKDOWN_SECTION", "ACCEPTED_PRODUCT_REQUIREMENTS"}
SCOPE_ROLES = {
    "MODEL_CONTEXT", "CROSS_CONTEXT", "STRATEGIC_RESPONSIBILITY",
    "BOUNDARY_POLICY", "APPLICATION_SEPARATION", "PRODUCT_CONSTRAINTS",
}
REQUIRED_SCOPE_ROLES = {
    "MODEL_CONTEXT", "CROSS_CONTEXT", "STRATEGIC_RESPONSIBILITY",
    "BOUNDARY_POLICY", "PRODUCT_CONSTRAINTS",
}


def _accepted_sources(root: Path) -> dict[str, dict[str, Any]]:
    core = _required_yaml(root / ".harness/core.yaml")
    baseline = _required_yaml(root / ".harness/semantic-baseline.yaml")
    reviews = baseline.get("reviews")
    artifacts = core.get("artifacts")
    if not isinstance(reviews, list) or not isinstance(artifacts, list):
        raise DiscoveryError("Core or semantic baseline is incomplete")
    reviewed = {}
    for row in reviews:
        if not isinstance(row, dict):
            raise DiscoveryError("invalid review entry")
        capability = row.get("capability")
        if not isinstance(capability, str) or capability in reviewed:
            raise DiscoveryError("duplicate/invalid reviewed Capability")
        revision = row.get("revision")
        if type(revision) is not int or revision < 1:
            raise DiscoveryError("accepted source lacks valid semantic review revision")
        reviewed[capability] = revision
    accepted = {}
    for item in artifacts:
        if not isinstance(item, dict) or not isinstance(item.get("path"), str):
            raise DiscoveryError("invalid Core artifact")
        path = item["path"]
        if path in accepted:
            raise DiscoveryError("ambiguous Core artifact source path")
        provides = item.get("provides")
        if not isinstance(provides, list) or len(provides) != 1:
            continue  # This narrow, conservative pilot cannot disambiguate.
        cid = provides[0]
        if cid not in reviewed:
            continue
        filename = _resolve(root, path)
        if not filename.is_file():
            raise DiscoveryError("registered accepted source file missing")
        accepted[path] = {
            "provider": cid, "review_revision": reviewed[cid],
            "source_sha256": hashlib.sha256(filename.read_bytes()).hexdigest(),
        }
    return accepted


def _fragments(
    root: Path, entry: dict[str, Any]
) -> list[tuple[str, str]]:
    path, kind = entry["path"], entry["type"]
    filename = _resolve(root, path)
    if kind == "MARKDOWN_SECTION":
        if not path.endswith(".md"):
            raise DiscoveryError("Markdown scope must select a Markdown source")
        heading = entry.get("heading")
        if not isinstance(heading, str) or not heading:
            raise DiscoveryError("markdown scope heading required")
        texts = _markdown_claims(
            _heading_scope(filename.read_text(encoding="utf-8"), heading)
        )
        if not texts:
            raise DiscoveryError("source section has no auditable statements")
        return [(str(i), v) for i, v in enumerate(texts)]
    if kind == "ACCEPTED_PRODUCT_REQUIREMENTS":
        if "heading" in entry:
            raise DiscoveryError("product requirements source does not use headings")
        record = _required_yaml(filename)
        accepted = _accepted_requirement_inventory(record)
        units = list(accepted.items())
        content = record.get("content", {})
        non_goals = content.get("non_goals", [])
        if not isinstance(non_goals, list):
            raise DiscoveryError("accepted product non-goals must be a list")
        for index, text in enumerate(non_goals, start=1):
            if not isinstance(text, str) or not text.strip():
                raise DiscoveryError("invalid accepted product non-goal")
            units.append((f"NON_GOAL-{index:02d}", f"Non-goal: {text.strip()}"))
        return units
    raise DiscoveryError("unsupported source segment type")


def audit_draft_coverage(
    root: Path, *, sha: str, draft: dict[str, Any],
) -> dict[str, Any]:
    root = root.resolve()
    _commit(root, sha)
    if draft.get("kind") != "harness-cdr-target-output-contract-candidates":
        raise DiscoveryError("not a target output candidate artifact")
    if draft.get("source_commit") != sha or draft.get("status") != "OPERATOR_DRAFT_NOT_ACCEPTED":
        raise DiscoveryError("draft source snapshot or acceptance status mismatch")
    if draft.get("no_automatic_writeback") is not True:
        raise DiscoveryError("draft must unconditionally disable graph writeback")
    sources = _accepted_sources(root)
    graph = _required_yaml(root / ".harness/engineering-graph.yaml")
    producers = {}
    for a in graph.get("authorities", []):
        for item in a.get("produces", []):
            cid = item.get("capability")
            if cid in producers:
                raise DiscoveryError("duplicate target production")
            producers[cid] = a["id"]
    contracts = draft.get("target_contracts")
    if not isinstance(contracts, list) or not contracts:
        raise DiscoveryError("draft target contracts are missing")
    seen_targets: set[str] = set()
    reports: list[dict[str, Any]] = []
    for contract in contracts:
        target = contract.get("target_capability")
        if not isinstance(target, str) or target in seen_targets:
            raise DiscoveryError("duplicate or invalid draft target")
        seen_targets.add(target)
        if producers.get(target) != draft.get("owning_authority"):
            raise DiscoveryError("draft target must match production Authority")
        if contract.get("target_contract_status") != "NEEDS_INDEPENDENT_AUTHORITY_REVIEW":
            raise DiscoveryError("draft may not assert its own acceptance")
        obligations = contract.get("candidate_obligations")
        if not isinstance(obligations, list) or not obligations:
            raise DiscoveryError("draft obligations missing")
        obligation_sources: dict[str, set[tuple[str, str | None]]] = {}
        for ob in obligations:
            if not isinstance(ob, dict):
                raise DiscoveryError("invalid draft obligation")
            ident, desc = ob.get("id"), ob.get("description")
            if (not isinstance(ident, str) or not ident
                or ident in obligation_sources
                or not isinstance(desc, str) or len(desc.strip()) < 45
                or ob.get("status") != "CANDIDATE_NOT_ACCEPTED"):
                raise DiscoveryError("invalid or prematurely accepted draft obligation")
            refs = ob.get("upstream_scope")
            if not isinstance(refs, list) or not refs:
                raise DiscoveryError("draft obligation lacks upstream references")
            pairs = set()
            for src in refs:
                if not isinstance(src, dict):
                    raise DiscoveryError("malformed draft upstream source reference")
                path, heading = src.get("path"), src.get("heading")
                if not isinstance(path, str) or path not in sources or not isinstance(heading, str):
                    raise DiscoveryError("draft obligation upstream reference is not accepted")
                if not path.endswith(".md"):
                    raise DiscoveryError("draft obligation source selector must be Markdown")
                _heading_scope(_resolve(root, path).read_text(encoding="utf-8"), heading)
                pairs.add((path, heading))
            obligation_sources[ident] = pairs
        scopes = contract.get("coverage_scope")
        if not isinstance(scopes, list) or not scopes:
            raise DiscoveryError("coverage scope must enumerate accepted source sections")
        roles = set()
        selected: set[tuple[str, str, str | None]] = set()
        fragments: list[dict[str, Any]] = []
        by_role: dict[str, int] = {}
        for entry in scopes:
            if not isinstance(entry, dict):
                raise DiscoveryError("invalid coverage scope")
            path, kind, role = entry.get("path"), entry.get("type"), entry.get("role")
            if (not isinstance(path, str) or path not in sources
                or kind not in SCOPE_TYPES or role not in SCOPE_ROLES):
                raise DiscoveryError("invalid or unaccepted coverage scope")
            heading = entry.get("heading")
            key = (path, kind, heading)
            if key in selected:
                raise DiscoveryError("duplicated scoped source section")
            selected.add(key)
            if (kind == "ACCEPTED_PRODUCT_REQUIREMENTS") != (role == "PRODUCT_CONSTRAINTS"):
                raise DiscoveryError("product coverage must use product requirements role")
            roles.add(role)
            linked = sorted(
                ident for ident, refs in obligation_sources.items()
                if (path, heading) in refs
            )
            for local_id, claim in _fragments(root, entry):
                if len(claim.strip()) < 6:
                    raise DiscoveryError("empty source fragment")
                stable_id = hashlib.sha256(
                    (path + "\n" + str(heading) + "\n" + local_id + "\n" + claim).encode("utf-8")
                ).hexdigest()[:20]
                fragments.append({
                    "source_unit_id": stable_id,
                    "source_path": path,
                    "source_sha256": sources[path]["source_sha256"],
                    "source_heading": heading,
                    "source_local_id": local_id,
                    "source_provider": sources[path]["provider"],
                    "review_revision": sources[path]["review_revision"],
                    "scope_role": role,
                    "source_text": claim,
                    "source_unit_kind": (
                        "PRODUCT_NON_GOAL" if local_id.startswith("NON_GOAL-")
                        else ("ACCEPTED_PRODUCT_REQUIREMENT"
                              if kind == "ACCEPTED_PRODUCT_REQUIREMENTS"
                              else "ACCEPTED_SOURCE_SECTION_STATEMENT")
                    ),
                    # This is ONLY a heading-level association, not a
                    # claim that target meaning follows from the source.
                    "candidate_obligations_with_same_source_section": (
                        [] if kind == "ACCEPTED_PRODUCT_REQUIREMENTS" else linked
                    ),
                    "unit_semantic_disposition": "UNREVIEWED",
                    "output_obligation_fulfilment_verified": False,
                    "target_authority_approved": False,
                })
                by_role[role] = by_role.get(role, 0) + 1
        if not REQUIRED_SCOPE_ROLES.issubset(roles):
            raise DiscoveryError("scope lacks model, cross-context, strategic, boundary or product sources")
        missing_refs = {
            (p, h)
            for refs in obligation_sources.values() for p, h in refs
            if (p, "MARKDOWN_SECTION", h) not in selected
        }
        if missing_refs:
            raise DiscoveryError("candidate obligation uses source sections omitted from review scope")
        if len({x["source_unit_id"] for x in fragments}) != len(fragments):
            raise DiscoveryError("source unit IDs are ambiguous")
        reports.append({
            "target_capability": target,
            "status": "PENDING_SEMANTIC_SCOPE_REVIEW",
            "candidate_obligation_count": len(obligations),
            "source_unit_count": len(fragments),
            "units_by_role": by_role,
            "units_without_same_section_candidate": sum(
                not f["candidate_obligations_with_same_source_section"] for f in fragments
            ),
            "unreviewed_unit_count": len(fragments),
            "source_units": fragments,
            "accepted_target_contract_established": False,
            "semantic_completeness_established": False,
            "automatic_writeback_allowed": False,
        })
    return {
        "kind": "harness-cdr-target-scope-coverage-inventory",
        "version": 1,
        "status": "PENDING_INDEPENDENT_TARGET_SCOPE_REVIEW",
        "source_snapshot": sha,
        "draft_status": draft["status"],
        "cases": reports,
        "complete_accepted_upstream_catalog_proven": False,
        "complete_target_output_semantics_proven": False,
        "independent_authority_review_performed": False,
        "automatic_writeback_allowed": False,
    }


def main() -> int:
    p = argparse.ArgumentParser(description="Source evidence inventory for unaccepted target obligations")
    p.add_argument("--project-root", type=Path, required=True)
    p.add_argument("--commit", required=True)
    p.add_argument("--draft", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    try:
        draft = _required_yaml(args.draft)
        report = audit_draft_coverage(args.project_root, sha=args.commit, draft=draft)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        print(json.dumps({
            "status": report["status"],
            "source_snapshot": report["source_snapshot"],
            "cases": [
                {
                    "target": r["target_capability"],
                    "candidate_obligations": r["candidate_obligation_count"],
                    "source_units": r["source_unit_count"],
                    "unlinked_to_draft_section": r["units_without_same_section_candidate"],
                    "semantic_review_pending": r["unreviewed_unit_count"],
                } for r in report["cases"]
            ],
        }, ensure_ascii=False))
        return 0
    except (KeyError, DiscoveryError, TypeError, OSError, ValueError) as exc:
        print(json.dumps({"status": "INVALID", "error": str(exc)}, ensure_ascii=False))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
