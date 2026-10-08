"""Account for every accepted MC/DS source unit without certifying target meaning.

Operator-authored claim-level hypotheses are never accepted output obligations,
direct source dependencies, or permission to mutate canonical project data.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from evals.project_discovery_snapshot import DiscoveryError, _required_yaml

STRATEGY_SOURCES = {
    "docs/architecture/model-context-map.md",
    "docs/architecture/context-map.md",
}
DISPOSITIONS = {
    "TARGET_SEMANTIC_CANDIDATE", "SHARED_BOUNDARY_CANDIDATE",
    "NEGATIVE_INVARIANT_CANDIDATE", "APPLICATION_CONSUMER",
    "GOVERNANCE_CONDITION", "SCOPE_EXCLUSION",
    "STRUCTURAL_OR_TRACE_CONTEXT", "UNDETERMINED",
}
TARGET_LINK_KINDS = {
    "CANDIDATE_SEMANTIC_CONSTRAINT", "CANDIDATE_NEGATIVE_INVARIANT",
    "POSSIBLE_SHARED_BOUNDARY", "OPEN_SCOPE_QUESTION",
}
EXTERNAL_TRACKS = {
    "APPLICATION_DESIGN", "SHARED_CROSS_CONTEXT", "UNDETERMINED",
}


def build_strategy_claim_review(
    worksheet: dict[str, Any],
    draft_contracts: dict[str, Any],
    hypotheses: dict[str, Any],
) -> dict[str, Any]:
    if (worksheet.get("kind") != "harness-cdr-source-responsibility-worksheet"
        or worksheet.get("status") != "PENDING_INDEPENDENT_RESPONSIBILITY_REVIEW"
        or worksheet.get("independent_responsibility_adjudication_performed") is not False
        or worksheet.get("automatic_writeback_allowed") is not False):
        raise DiscoveryError("source responsibility worksheet must be unreviewed")
    sha = worksheet.get("source_snapshot")
    if (hypotheses.get("kind") != "harness-cdr-strategy-claim-review-hypotheses"
        or hypotheses.get("status") != "OPERATOR_DRAFT_NOT_ACCEPTED"
        or hypotheses.get("source_commit") != sha
        or hypotheses.get("automatic_writeback_allowed") is not False
        or draft_contracts.get("source_commit") != sha
        or draft_contracts.get("kind") != "harness-cdr-target-output-contract-candidates"
        or draft_contracts.get("status") != "OPERATOR_DRAFT_NOT_ACCEPTED"
        or draft_contracts.get("no_automatic_writeback") is not True):
        raise DiscoveryError("hypotheses and output draft must share pinned unaccepted snapshot")
    targets: dict[str, set[str]] = {}
    for target in draft_contracts.get("target_contracts", []):
        cid = target.get("target_capability")
        if not isinstance(cid, str) or cid in targets:
            raise DiscoveryError("invalid or repeated target")
        if target.get("target_contract_status") != "NEEDS_INDEPENDENT_AUTHORITY_REVIEW":
            raise DiscoveryError("draft target acceptance status is not pending")
        obs = target.get("candidate_obligations", [])
        if not isinstance(obs, list) or not obs:
            raise DiscoveryError("missing candidate output obligations")
        ids = [ob.get("id") for ob in obs]
        if (not all(isinstance(x, str) and x for x in ids)
            or len(ids) != len(set(ids))
            or any(ob.get("status") != "CANDIDATE_NOT_ACCEPTED" for ob in obs)):
            raise DiscoveryError("output obligations must be unique unaccepted candidates")
        targets[cid] = set(ids)
    if set(targets) != set(worksheet.get("source_targets", [])):
        raise DiscoveryError("target sets differ")
    selected: dict[tuple[str,str,int], dict[str, Any]] = {}
    for src in worksheet.get("source_units", []):
        if not isinstance(src, dict):
            raise DiscoveryError("invalid source unit")
        if (src.get("source_path") not in STRATEGY_SOURCES
            or src.get("source_unit_kind") != "ACCEPTED_SOURCE_SECTION_STATEMENT"):
            continue
        if (src.get("review_state") != "UNREVIEWED"
            or src.get("semantic_route") != "UNDETERMINED"
            or src.get("target_output_obligation_mapping_verified") is not False):
            raise DiscoveryError("source unit prematurely classified")
        lid = src.get("source_local_id")
        if not isinstance(lid, str) or not lid.isdecimal():
            raise DiscoveryError("strategy source local ID must be numeric")
        key = (src["source_path"], src["source_heading"], int(lid))
        if key in selected:
            raise DiscoveryError("duplicate selected strategy claim")
        selected[key] = src
    if not selected:
        raise DiscoveryError("no accepted MC/DS source units in worksheet")
    groups = hypotheses.get("sections")
    if not isinstance(groups, list) or not groups:
        raise DiscoveryError("strategy review sections missing")
    evaluated = set()
    rows = []
    for group in groups:
        if not isinstance(group, dict):
            raise DiscoveryError("malformed strategy section")
        path, heading = group.get("source_path"), group.get("source_heading")
        entries = group.get("claims")
        if path not in STRATEGY_SOURCES or not isinstance(heading, str) or not heading:
            raise DiscoveryError("unexpected strategy source selection")
        if not isinstance(entries, list) or not entries:
            raise DiscoveryError("empty strategy claim list")
        for item in entries:
            if not isinstance(item, dict):
                raise DiscoveryError("invalid source claim annotation")
            idx = item.get("index")
            if type(idx) is not int or idx < 0:
                raise DiscoveryError("invalid claim index")
            key = (path, heading, idx)
            if key not in selected or key in evaluated:
                raise DiscoveryError("unknown or duplicate MC/DS source claim index")
            evaluated.add(key)
            src = selected[key]
            if item.get("expected_source_text") != src["source_text"]:
                raise DiscoveryError("source wording differs from pinned claim")
            if ("source_unit_id" in item
                and item["source_unit_id"] != src["source_unit_id"]):
                raise DiscoveryError("source unit identity mismatch (snapshot/wording drift)")
            disposition = item.get("disposition")
            if disposition not in DISPOSITIONS:
                raise DiscoveryError("invalid tentative claim disposition")
            links = item.get("candidate_target_links")
            external = item.get("candidate_external_routes")
            if not isinstance(links, list) or not isinstance(external, list):
                raise DiscoveryError("claim links/external routes must be arrays")
            if (len(external) != len(set(external))
                or any(x not in EXTERNAL_TRACKS for x in external)):
                raise DiscoveryError("invalid external responsibility candidate")
            seen_links = set()
            for link in links:
                if not isinstance(link, dict):
                    raise DiscoveryError("malformed target link")
                cid,oid,kind = (
                    link.get("target_capability"), link.get("obligation_id"),
                    link.get("relation"))
                pair=(cid,oid)
                if (cid not in targets or oid not in targets[cid]
                    or kind not in TARGET_LINK_KINDS or pair in seen_links):
                    raise DiscoveryError("unknown or duplicate draft output obligation link")
                seen_links.add(pair)
            if (disposition in {"TARGET_SEMANTIC_CANDIDATE",
                                "NEGATIVE_INVARIANT_CANDIDATE"}
                and not links):
                raise DiscoveryError("target-owned semantic candidate needs target link")
            if (disposition in {"STRUCTURAL_OR_TRACE_CONTEXT",
                                "GOVERNANCE_CONDITION",
                                "SCOPE_EXCLUSION", "APPLICATION_CONSUMER"}
                and links):
                raise DiscoveryError("non-target semantic classification cannot assert target link")
            if disposition == "SHARED_BOUNDARY_CANDIDATE" and (
                not links and "SHARED_CROSS_CONTEXT" not in external
            ):
                raise DiscoveryError("shared boundary needs target or shared-contract review")
            if not isinstance(item.get("review_reason"), str) or len(item["review_reason"].strip()) < 25:
                raise DiscoveryError("claim-specific review rationale missing")
            rows.append({
                "source_unit_id": src["source_unit_id"],
                "source_path": path,
                "source_heading": heading,
                "source_local_id": src["source_local_id"],
                "source_text": src["source_text"],
                "source_sha256": src["source_sha256"],
                "source_review_revision": src["review_revision"],
                "source_provider": src["source_provider"],
                "source_role": src["scope_role"],
                "source_seen_by_targets": src["seen_by_target_capabilities"],
                "tentative_disposition": disposition,
                "candidate_target_links": links,
                "candidate_external_routes": external,
                "review_reason": item["review_reason"],
                "claim_semantically_adjudicated": False,
                "target_obligation_accepted": False,
                "direct_provider_necessity_proven": False,
                "automatic_writeback_allowed": False,
            })
    if evaluated != set(selected):
        absent=sorted(set(selected)-evaluated)
        raise DiscoveryError(
            f"not every selected accepted MC/DS claim was accounted for ({len(absent)} omitted)"
        )
    counts={name:sum(r["tentative_disposition"]==name for r in rows)
            for name in sorted(DISPOSITIONS)}
    by_target={cid:{
        "target_capability":cid,
        "candidate_obligations_with_source_claim_hypotheses":sorted({
            link["obligation_id"] for r in rows for link in r["candidate_target_links"]
            if link["target_capability"] == cid
        }),
        "candidate_obligations_without_source_claim_hypotheses":sorted(
            ids-{link["obligation_id"] for r in rows for link in r["candidate_target_links"]
                 if link["target_capability"] == cid}
        ),
        "semantic_coverage_verified":False,
        "target_accepted":False,
    } for cid,ids in targets.items()}
    return {
        "kind":"harness-cdr-strategy-claim-review",
        "version":1,
        "status":"PENDING_INDEPENDENT_STRATEGY_CLAIM_REVIEW",
        "source_snapshot":sha,
        "individual_accepted_source_units_accounted_for":len(rows),
        "source_units_remaining_unaccounted_for":0,
        "tentative_dispositions":counts,
        "target_drafts":list(by_target.values()),
        "source_claims":sorted(rows,key=lambda r:(
            r["source_path"],r["source_heading"],int(r["source_local_id"]))),
        "individual_semantic_reviews_performed":0,
        "accepted_target_output_obligations":False,
        "complete_target_output_semantics_proven":False,
        "direct_dependencies_verified":False,
        "automatic_writeback_allowed":False,
    }


def main() -> int:
    p=argparse.ArgumentParser(description="Read-only per-claim MC/DS review hypotheses")
    p.add_argument("--worksheet",type=Path,required=True)
    p.add_argument("--draft",type=Path,required=True)
    p.add_argument("--hypotheses",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    try:
        ws=json.loads(args.worksheet.read_text(encoding="utf-8"))
        draft=_required_yaml(args.draft)
        hyp=_required_yaml(args.hypotheses)
        report=build_strategy_claim_review(ws,draft,hyp)
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
        print(json.dumps({
            "status":report["status"],
            "accepted_MC_DS_units_accounted":report["individual_accepted_source_units_accounted_for"],
            "tentative_dispositions":report["tentative_dispositions"],
            "unreviewed":report["individual_semantic_reviews_performed"],
        },ensure_ascii=False))
        return 0
    except (DiscoveryError,KeyError,TypeError,OSError,ValueError) as exc:
        print(json.dumps({"status":"INVALID","error":str(exc)},ensure_ascii=False))
        return 2


if __name__=="__main__":
    raise SystemExit(main())
