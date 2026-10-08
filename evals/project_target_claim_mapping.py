"""Per-claim, read-only draft mapping from accepted evidence to target obligations.

Inputs come from the immutable scope inventory and deduplicated responsibility
worksheet; human-written hypotheses may suggest mappings but are neither
Authority review nor complete target semantics.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from evals.project_discovery_snapshot import DiscoveryError, _required_yaml

PRODUCT_KINDS = {"ACCEPTED_PRODUCT_REQUIREMENT", "PRODUCT_NON_GOAL"}
RELATIONS = {
    "CANDIDATE_SEMANTIC_CONSTRAINT", "CANDIDATE_NEGATIVE_INVARIANT",
    "POSSIBLE_SHARED_BOUNDARY", "POSSIBLE_APPLICATION_CONSUMER",
    "OPEN_SCOPE_QUESTION",
}
FURTHER_ROUTES = {
    "APPLICATION_DESIGN", "SHARED_CROSS_CONTEXT", "UNDETERMINED"
}


def build_claim_mapping(
    worksheet: dict[str, Any], draft_contracts: dict[str, Any], *,
    proposals: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if (worksheet.get("kind") != "harness-cdr-source-responsibility-worksheet"
        or worksheet.get("status") != "PENDING_INDEPENDENT_RESPONSIBILITY_REVIEW"
        or worksheet.get("independent_responsibility_adjudication_performed") is not False
        or worksheet.get("accepted_target_contract_established") is not False
        or worksheet.get("automatic_writeback_allowed") is not False):
        raise DiscoveryError("only unreviewed source responsibility worksheet accepted")
    sha = worksheet.get("source_snapshot")
    if (not isinstance(sha, str) or len(sha) != 40
        or draft_contracts.get("source_commit") != sha
        or draft_contracts.get("kind") != "harness-cdr-target-output-contract-candidates"
        or draft_contracts.get("status") != "OPERATOR_DRAFT_NOT_ACCEPTED"
        or draft_contracts.get("no_automatic_writeback") is not True):
        raise DiscoveryError("target draft must be pinned, unaccepted, nonmutating")
    targets: dict[str, set[str]] = {}
    for target in draft_contracts.get("target_contracts", []):
        if (not isinstance(target, dict)
            or target.get("target_contract_status") != "NEEDS_INDEPENDENT_AUTHORITY_REVIEW"):
            raise DiscoveryError("draft target is not pending Authority review")
        cid = target.get("target_capability")
        if not isinstance(cid, str) or cid in targets:
            raise DiscoveryError("duplicate or invalid target draft")
        obligations = target.get("candidate_obligations")
        if not isinstance(obligations, list) or not obligations:
            raise DiscoveryError("target draft has no candidate obligations")
        ids = set()
        for ob in obligations:
            if not isinstance(ob, dict) or ob.get("status") != "CANDIDATE_NOT_ACCEPTED":
                raise DiscoveryError("draft output obligation is not unaccepted")
            oid = ob.get("id")
            if not isinstance(oid, str) or not oid or oid in ids:
                raise DiscoveryError("invalid or repeated obligation id")
            ids.add(oid)
        targets[cid] = ids
    if not targets or set(targets) != set(worksheet.get("source_targets", [])):
        raise DiscoveryError("source worksheet target list differs from target draft")
    sources = worksheet.get("source_units")
    if not isinstance(sources, list) or len(sources) != worksheet.get("distinct_source_unit_count"):
        raise DiscoveryError("inconsistent source unit ledger")
    source_by_key: dict[tuple[str, str, str], dict[str, Any]] = {}
    source_ids = set()
    for unit in sources:
        if not isinstance(unit, dict):
            raise DiscoveryError("malformed source unit")
        uid = unit.get("source_unit_id")
        if uid in source_ids:
            raise DiscoveryError("duplicate source unit")
        source_ids.add(uid)
        if (unit.get("review_state") != "UNREVIEWED"
            or unit.get("semantic_route") != "UNDETERMINED"
            or unit.get("semantic_effect") != "UNDETERMINED"
            or unit.get("target_output_obligation_mapping_verified") is not False
            or unit.get("automatic_writeback_allowed") is not False):
            raise DiscoveryError("source unit was prematurely adjudicated")
        if unit.get("source_unit_kind") in PRODUCT_KINDS:
            key = (unit["source_path"], unit["source_local_id"], unit["source_unit_kind"])
            if key in source_by_key:
                raise DiscoveryError("duplicate product semantic identity")
            source_by_key[key] = unit
    suggestions: dict[str, dict[str, Any]] = {}
    if proposals is not None:
        if (proposals.get("kind") != "harness-cdr-claim-obligation-mapping-hypotheses"
            or proposals.get("status") != "OPERATOR_DRAFT_NOT_ACCEPTED"
            or proposals.get("source_commit") != sha
            or proposals.get("automatic_writeback_allowed") is not False):
            raise DiscoveryError("mapping hypotheses must be pinned unaccepted draft")
        entries = proposals.get("source_claims")
        if not isinstance(entries, list):
            raise DiscoveryError("mapping proposal claim list missing")
        observed_keys = set()
        for item in entries:
            if not isinstance(item, dict):
                raise DiscoveryError("invalid mapping hypothesis")
            key = (item.get("source_path"), item.get("source_local_id"), item.get("source_unit_kind"))
            if key not in source_by_key or key in observed_keys:
                raise DiscoveryError("unknown or duplicate product claim mapping")
            observed_keys.add(key)
            unit = source_by_key[key]
            if ("source_sha256" in item
                and item["source_sha256"] != unit["source_sha256"]):
                raise DiscoveryError("mapping source digest differs from immutable snapshot")
            if item.get("status") != "CANDIDATE_NOT_ACCEPTED":
                raise DiscoveryError("mapping candidate cannot declare acceptance")
            links = item.get("candidate_target_links")
            if not isinstance(links, list):
                raise DiscoveryError("candidate_target_links must be an array")
            found_links = set()
            for link in links:
                if not isinstance(link, dict):
                    raise DiscoveryError("invalid candidate link")
                cid, oid, relation = (
                    link.get("target_capability"), link.get("obligation_id"), link.get("relation")
                )
                key2 = (cid, oid)
                if (cid not in targets or oid not in targets[cid]
                    or relation not in RELATIONS or key2 in found_links):
                    raise DiscoveryError("unknown, invalid, or duplicate target obligation link")
                found_links.add(key2)
            other = item.get("candidate_external_routes")
            if (not isinstance(other, list) or len(other) != len(set(other))
                or any(v not in FURTHER_ROUTES for v in other)):
                raise DiscoveryError("invalid candidate external routing")
            if not links and not other:
                raise DiscoveryError("unmapped claim needs explicit external/undetermined review")
            if (not isinstance(item.get("rationale"), str)
                or len(item["rationale"].strip()) < 35):
                raise DiscoveryError("substantive draft rationale required")
            suggestions[unit["source_unit_id"]] = item
        if observed_keys != set(source_by_key):
            raise DiscoveryError("draft mapping must account for every accepted product claim and non-goal exactly once")

    rows = []
    for unit in sources:
        ident = unit["source_unit_id"]
        proposed = suggestions.get(ident)
        rows.append({
            "source_unit_id": ident,
            "source_path": unit["source_path"],
            "source_sha256": unit["source_sha256"],
            "source_provider": unit["source_provider"],
            "source_local_id": unit["source_local_id"],
            "source_unit_kind": unit["source_unit_kind"],
            "source_text": unit["source_text"],
            "seen_by_target_capabilities": unit["seen_by_target_capabilities"],
            "source_section_draft_obligation_hints": unit["candidate_draft_obligation_ids_by_target"],
            "proposed_links": [] if proposed is None else proposed["candidate_target_links"],
            "proposed_external_routes": [] if proposed is None else proposed["candidate_external_routes"],
            "proposal_rationale": None if proposed is None else proposed["rationale"],
            "classification_state": (
                "OPERATOR_HYPOTHESIS_NOT_REVIEWED" if proposed is not None
                else "UNCLASSIFIED_REQUIRES_REVIEW"
            ),
            "source_semantics_adjudicated": False,
            "direct_provider_necessity_established": False,
            "target_obligation_accepted": False,
            "automatic_writeback_allowed": False,
        })
    per_target = []
    for cid, ids in sorted(targets.items()):
        candidate_linked = {
            v["obligation_id"]
            for unit in rows for v in unit["proposed_links"]
            if v["target_capability"] == cid
        }
        per_target.append({
            "target_capability": cid,
            "draft_output_obligations": sorted(ids),
            "draft_obligations_with_candidate_claim_links": sorted(candidate_linked),
            "draft_obligations_without_candidate_claim_links": sorted(ids - candidate_linked),
            "semantic_coverage_verified": False,
            "direct_dependencies_verified": False,
        })
    return {
        "kind": "harness-cdr-target-claim-mapping-review",
        "version": 1,
        "status": "PENDING_INDEPENDENT_CLAIM_TO_OBLIGATION_REVIEW",
        "source_snapshot": sha,
        "source_claim_count": len(rows),
        "operator_classified_product_claim_count": len(suggestions),
        "product_claims_in_scope": len(source_by_key),
        "other_source_units_unclassified": sum(
            x["classification_state"] == "UNCLASSIFIED_REQUIRES_REVIEW"
            for x in rows
        ),
        "target_draft_coverage": per_target,
        "source_claims": rows,
        "all_accepted_source_semantics_covered": False,
        "target_obligations_independently_accepted": False,
        "authority_review_performed": False,
        "automatic_writeback_allowed": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build claim-level unaccepted tactical obligation mapping")
    parser.add_argument("--worksheet", type=Path, required=True)
    parser.add_argument("--draft", type=Path, required=True)
    parser.add_argument("--hypotheses", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        worksheet = json.loads(args.worksheet.read_text(encoding="utf-8"))
        draft = _required_yaml(args.draft)
        hypotheses = _required_yaml(args.hypotheses) if args.hypotheses else None
        result = build_claim_mapping(worksheet, draft, proposals=hypotheses)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        print(json.dumps({
            "status": result["status"],
            "source_claims": result["source_claim_count"],
            "product_claims_accounted_for": result["operator_classified_product_claim_count"],
            "other_units_pending_review": result["other_source_units_unclassified"],
            "target_draft_unlinked_obligations": {
                x["target_capability"]: x["draft_obligations_without_candidate_claim_links"]
                for x in result["target_draft_coverage"]
            },
        }, ensure_ascii=False))
        return 0
    except (DiscoveryError, KeyError, TypeError, OSError, ValueError) as exc:
        print(json.dumps({"status":"INVALID", "error":str(exc)}, ensure_ascii=False))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
