"""Combine source-unit ledgers into a global *unreviewed* responsibility worksheet.

Do not infer an accepted semantic owner from a section heading, provider
Authority, product wording, or two targets citing the same source. Product
behaviors and their domain-semantic constraints are distinct review facets.
No decisions made here may change PREP target acceptance or dependency edges.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

from evals.project_discovery_snapshot import DiscoveryError, _required_yaml

TRACKS = (
    "PREPARATION_INFORMATION",
    "RECORDED_ACTIVITY_HISTORY",
    "SHARED_CROSS_CONTEXT",
    "APPLICATION_DESIGN",
    "UNDETERMINED",
)
EFFECTS = (
    "DOMAIN_SEMANTICS",
    "SHARED_BOUNDARY",
    "APPLICATION_BEHAVIOR",
    "PROHIBITED_INFERENCE",
    "REOPENING_OR_GOVERNANCE",
    "UNDETERMINED",
)
SECTION_HINTS = {
    "MC-01 Preparation Information": ("PREPARATION_INFORMATION",),
    "MC-02 Recorded Activity History": ("RECORDED_ACTIVITY_HISTORY",),
    "TR-01 Preparation Information and Recorded Activity History": ("SHARED_CROSS_CONTEXT",),
    "DS-01 Preparation Information — CORE": ("PREPARATION_INFORMATION",),
    "DS-02 Recorded Activity History — CORE": ("RECORDED_ACTIVITY_HISTORY",),
}
FIELDS = ("source_unit_id", "source_path", "source_sha256", "source_heading",
          "source_local_id", "source_provider", "review_revision", "scope_role",
          "source_text", "source_unit_kind")


def _effect_hints(unit: dict[str, Any]) -> list[str]:
    """Section-role candidates only; never adjudicate source claim meaning."""
    if unit["source_unit_kind"] == "PRODUCT_NON_GOAL":
        return ["PROHIBITED_INFERENCE"]
    role = unit["scope_role"]
    return {
        "MODEL_CONTEXT": ["DOMAIN_SEMANTICS", "PROHIBITED_INFERENCE"],
        "CROSS_CONTEXT": ["SHARED_BOUNDARY", "PROHIBITED_INFERENCE"],
        "STRATEGIC_RESPONSIBILITY": ["DOMAIN_SEMANTICS", "SHARED_BOUNDARY"],
        "BOUNDARY_POLICY": ["PROHIBITED_INFERENCE", "REOPENING_OR_GOVERNANCE"],
        "APPLICATION_SEPARATION": ["APPLICATION_BEHAVIOR", "SHARED_BOUNDARY"],
        "PRODUCT_CONSTRAINTS": ["DOMAIN_SEMANTICS", "APPLICATION_BEHAVIOR"],
    }.get(role, ["UNDETERMINED"])


def _hint(unit: dict[str, Any]) -> tuple[list[str], str]:
    heading = unit["source_heading"]
    if heading in SECTION_HINTS:
        return list(SECTION_HINTS[heading]), "ACCEPTED_SECTION_NAME_ONLY"
    if unit["scope_role"] == "APPLICATION_SEPARATION":
        return ["APPLICATION_DESIGN", "SHARED_CROSS_CONTEXT"], "SECTION_CONSUMER_OR_EXCLUSION_ONLY"
    return ["UNDETERMINED"], "NO_SEMANTIC_OWNER_INFERRED"


def build_routing_worksheet(
    inventory: dict[str, Any], *,
    product_proposals: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if inventory.get("kind") != "harness-cdr-target-scope-coverage-inventory":
        raise DiscoveryError("wrong source inventory kind")
    if inventory.get("status") != "PENDING_INDEPENDENT_TARGET_SCOPE_REVIEW":
        raise DiscoveryError("source inventory is not a pending unreviewed scope")
    if inventory.get("complete_target_output_semantics_proven") is not False:
        raise DiscoveryError("scope inventory must not claim complete semantics")
    if inventory.get("independent_authority_review_performed") is not False:
        raise DiscoveryError("source inventory must not claim review was performed")
    if inventory.get("automatic_writeback_allowed") is not False:
        raise DiscoveryError("scope inventory must disable topology writeback")
    sha = inventory.get("source_snapshot")
    if not isinstance(sha, str) or len(sha) != 40:
        raise DiscoveryError("source snapshot SHA missing")
    cases = inventory.get("cases")
    if not isinstance(cases, list) or not cases:
        raise DiscoveryError("source inventory cases missing")
    observed_targets: set[str] = set()
    units: dict[str, dict[str, Any]] = {}
    product_ids: set[str] = set()
    for case in cases:
        target = case.get("target_capability")
        if not isinstance(target, str) or target in observed_targets:
            raise DiscoveryError("duplicate or malformed target")
        observed_targets.add(target)
        if (case.get("status") != "PENDING_SEMANTIC_SCOPE_REVIEW"
            or case.get("accepted_target_contract_established") is not False
            or case.get("semantic_completeness_established") is not False):
            raise DiscoveryError("source case claims premature acceptance")
        fragments = case.get("source_units")
        if not isinstance(fragments, list) or len(fragments) != case.get("source_unit_count"):
            raise DiscoveryError("missing source unit evidence")
        local_seen = set()
        for src in fragments:
            if not isinstance(src, dict):
                raise DiscoveryError("malformed source evidence")
            uid = src.get("source_unit_id")
            if not isinstance(uid, str) or len(uid) != 20 or uid in local_seen:
                raise DiscoveryError("duplicate/invalid source unit within target")
            local_seen.add(uid)
            if any(field not in src for field in FIELDS):
                raise DiscoveryError("source unit missing immutable provenance")
            source_digest = src["source_sha256"]
            revision = src["review_revision"]
            if (not isinstance(source_digest, str)
                or not re.fullmatch(r"[0-9a-f]{64}", source_digest)
                or type(revision) is not int or revision < 1):
                raise DiscoveryError("source unit has invalid accepted provenance")
            for field in ("source_path", "source_provider", "source_local_id", "source_text"):
                if not isinstance(src[field], str) or not src[field].strip():
                    raise DiscoveryError("source unit has invalid textual provenance")
            expected_uid = hashlib.sha256(
                (src["source_path"] + "\n" + str(src["source_heading"])
                 + "\n" + src["source_local_id"] + "\n" + src["source_text"]).encode("utf-8")
            ).hexdigest()[:20]
            if uid != expected_uid:
                raise DiscoveryError("source unit digest does not match quoted evidence")
            if (src.get("unit_semantic_disposition") != "UNREVIEWED"
                or src.get("output_obligation_fulfilment_verified") is not False
                or src.get("target_authority_approved") is not False):
                raise DiscoveryError("source unit was prematurely adjudicated")
            if src.get("source_unit_kind") in ("ACCEPTED_PRODUCT_REQUIREMENT", "PRODUCT_NON_GOAL"):
                if src.get("source_heading") is not None:
                    raise DiscoveryError("product source unit may not have heading")
                if src.get("source_unit_kind") == "ACCEPTED_PRODUCT_REQUIREMENT":
                    product_ids.add(src["source_local_id"])
            stored = units.get(uid)
            facts = {key: src[key] for key in FIELDS}
            if stored is None:
                guesses, reason = _hint(src)
                stored = {
                    **facts,
                    "seen_by_target_capabilities": [],
                    "candidate_draft_obligation_ids_by_target": {},
                    "provisional_responsibility_tracks": guesses,
                    "provisional_hint_basis": reason,
                    "provisional_effect_candidates": _effect_hints(src),
                    "hint_is_semantic_evidence": False,
                    "semantic_route": "UNDETERMINED",
                    "semantic_effect": "UNDETERMINED",
                    "target_output_obligation_mapping_verified": False,
                    "review_state": "UNREVIEWED",
                    "automatic_writeback_allowed": False,
                }
                units[uid] = stored
            elif any(stored[key] != facts[key] for key in FIELDS):
                raise DiscoveryError("inconsistent source provenance across targets")
            stored["seen_by_target_capabilities"].append(target)
            stored["candidate_draft_obligation_ids_by_target"][target] = list(
                src.get("candidate_obligations_with_same_source_section", [])
            )

    proposals: dict[str, dict[str, Any]] = {}
    if product_proposals is not None:
        if (product_proposals.get("kind") != "harness-cdr-product-routing-hypotheses"
            or product_proposals.get("status") != "OPERATOR_DRAFT_NOT_ACCEPTED"
            or product_proposals.get("source_commit") != sha
            or product_proposals.get("automatic_writeback_allowed") is not False):
            raise DiscoveryError("routing hypotheses are not pinned, unaccepted draft")
        entries = product_proposals.get("product_requirements")
        if not isinstance(entries, list):
            raise DiscoveryError("product routing hypothesis list missing")
        for item in entries:
            if not isinstance(item, dict):
                raise DiscoveryError("malformed product routing draft")
            reqid = item.get("requirement_id")
            if not isinstance(reqid, str) or reqid in proposals:
                raise DiscoveryError("duplicate product routing hypothesis")
            if item.get("status") != "CANDIDATE_NOT_ACCEPTED":
                raise DiscoveryError("routing draft may not assert acceptance")
            tracks = item.get("candidate_tracks")
            if not isinstance(tracks, list) or not tracks or (
                len(tracks) != len(set(tracks))
            ) or any(x not in TRACKS for x in tracks):
                raise DiscoveryError("invalid draft responsibility tracks")
            if "UNDETERMINED" in tracks and len(tracks) != 1:
                raise DiscoveryError("ambiguous undetermined track")
            if not isinstance(item.get("review_question"), str) or len(item["review_question"]) < 20:
                raise DiscoveryError("routing hypothesis missing review question")
            proposals[reqid] = item
        if set(proposals) != product_ids:
            raise DiscoveryError(
                "product routing hypotheses must cover every accepted product requirement exactly"
            )
        for unit in units.values():
            if unit["source_unit_kind"] == "ACCEPTED_PRODUCT_REQUIREMENT":
                proposal = proposals[unit["source_local_id"]]
                unit["provisional_responsibility_tracks"] = list(proposal["candidate_tracks"])
                unit["provisional_hint_basis"] = "OPERATOR_DRAFT_PER_ACCEPTED_REQUIREMENT"
                unit["draft_review_question"] = proposal["review_question"]

    ordered = sorted(units.values(), key=lambda x: (
        x["source_path"], x["source_heading"] or "",
        x["source_local_id"], x["source_unit_id"]
    ))
    return {
        "kind": "harness-cdr-source-responsibility-worksheet",
        "version": 1,
        "status": "PENDING_INDEPENDENT_RESPONSIBILITY_REVIEW",
        "source_snapshot": sha,
        "source_targets": sorted(observed_targets),
        "distinct_source_unit_count": len(ordered),
        "accepted_product_requirement_count": len(product_ids),
        "per_source_unit_route_set": list(TRACKS),
        "per_source_unit_effect_set": list(EFFECTS),
        "source_units": ordered,
        "duplicated_across_targets": sum(
            len(u["seen_by_target_capabilities"]) > 1 for u in ordered
        ),
        "unit_semantics_reviewed": 0,
        "independent_responsibility_adjudication_performed": False,
        "accepted_target_contract_established": False,
        "all_target_output_obligations_covered": False,
        "automatic_writeback_allowed": False,
    }


def validate_unaccepted_review_draft(
    worksheet: dict[str, Any], draft: dict[str, Any],
) -> dict[str, Any]:
    """Structural completeness of a candidate review; never an approval."""
    if worksheet.get("kind") != "harness-cdr-source-responsibility-worksheet":
        raise DiscoveryError("wrong worksheet")
    if draft.get("kind") != "harness-cdr-source-routing-review-draft":
        raise DiscoveryError("wrong review draft kind")
    if draft.get("status") != "OPERATOR_DRAFT_NOT_ACCEPTED":
        raise DiscoveryError("review draft cannot assert acceptance")
    if draft.get("source_snapshot") != worksheet.get("source_snapshot"):
        raise DiscoveryError("routing draft snapshot mismatch")
    if draft.get("automatic_writeback_allowed") is not False:
        raise DiscoveryError("routing draft must disable graph writeback")
    units = {u["source_unit_id"]: u for u in worksheet["source_units"]}
    assessments = draft.get("assessments")
    if not isinstance(assessments, list):
        raise DiscoveryError("review draft assessment rows missing")
    seen = set()
    for item in assessments:
        if not isinstance(item, dict):
            raise DiscoveryError("invalid source unit review row")
        uid = item.get("source_unit_id")
        if uid not in units or uid in seen:
            raise DiscoveryError("unknown or duplicate reviewed source unit")
        seen.add(uid)
        if (item.get("source_sha256") != units[uid]["source_sha256"]
            or item.get("source_provider") != units[uid]["source_provider"]):
            raise DiscoveryError("draft review source identity mismatch")
        if item.get("proposed_route") not in TRACKS or item.get("proposed_effect") not in EFFECTS:
            raise DiscoveryError("invalid proposed route/effect")
        mapped = item.get("affected_targets")
        if not isinstance(mapped, list) or len(mapped) != len(set(mapped)) or any(
            t not in worksheet["source_targets"] for t in mapped
        ):
            raise DiscoveryError("invalid affected target references")
        if item.get("state") != "NEEDS_AUTHORITY_REVIEW":
            raise DiscoveryError("review draft cannot record self-adjudication")
        if not isinstance(item.get("rationale"), str) or len(item["rationale"].strip()) < 35:
            raise DiscoveryError("review draft needs substantive rationale")
    return {
        "status": "DRAFT_COMPLETE_FOR_REVIEW" if seen == set(units) else "DRAFT_PARTIAL_FOR_REVIEW",
        "rows_present": len(seen),
        "rows_required": len(units),
        "independent_authority_review_performed": False,
        "target_output_contract_accepted": False,
        "automatic_writeback_allowed": False,
    }


def main() -> int:
    p = argparse.ArgumentParser(description="Create an unreviewed source responsibility worksheet")
    p.add_argument("--inventory", type=Path, required=True)
    p.add_argument("--product-hypotheses", type=Path)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    try:
        inventory = json.loads(args.inventory.read_text(encoding="utf-8"))
        proposals = _required_yaml(args.product_hypotheses) if args.product_hypotheses else None
        output = build_routing_worksheet(inventory, product_proposals=proposals)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({
            "status": output["status"],
            "source_snapshot": output["source_snapshot"],
            "distinct_units": output["distinct_source_unit_count"],
            "duplicated_across_targets": output["duplicated_across_targets"],
            "product_requirements": output["accepted_product_requirement_count"],
            "reviewed": output["unit_semantics_reviewed"],
        }))
        return 0
    except (DiscoveryError, OSError, ValueError, TypeError, KeyError) as exc:
        print(json.dumps({"status": "INVALID", "error": str(exc)}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
