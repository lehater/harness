"""Read-only cross-authority audit of *draft* tactical output obligations.

This joins the previously bound product and MC/DS evidence **after** those
claim-level hypotheses have been generated. An edge in this joined evidence
is NOT an accepted target obligation, semantic entailment, or direct requires.
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from evals.project_discovery_snapshot import DiscoveryError, _required_yaml

PRODUCT_KINDS = {"ACCEPTED_PRODUCT_REQUIREMENT", "PRODUCT_NON_GOAL"}
POTENTIALLY_OWNED = {
    "TARGET_SEMANTIC_CANDIDATE",
    "NEGATIVE_INVARIANT_CANDIDATE",
    "SHARED_BOUNDARY_CANDIDATE",
    "UNDETERMINED",
}
UNCERTAIN_RELATIONS = {"OPEN_SCOPE_QUESTION", "POSSIBLE_SHARED_BOUNDARY"}


def _checked_report(report: dict[str, Any], kind: str, status: str, sha: str) -> list[dict[str, Any]]:
    if (report.get("kind") != kind or report.get("status") != status
        or report.get("source_snapshot") != sha
        or report.get("automatic_writeback_allowed") is not False):
        raise DiscoveryError("wrong report, snapshot or writeback contract: " + kind)
    source = report.get("source_claims")
    if not isinstance(source, list):
        raise DiscoveryError("missing source claim rows: " + kind)
    return source


def audit_target_obligations(
    worksheet: dict[str, Any],
    draft: dict[str, Any],
    product: dict[str, Any],
    strategy: dict[str, Any],
) -> dict[str, Any]:
    sha = worksheet.get("source_snapshot")
    if (worksheet.get("kind") != "harness-cdr-source-responsibility-worksheet"
        or worksheet.get("status") != "PENDING_INDEPENDENT_RESPONSIBILITY_REVIEW"
        or worksheet.get("automatic_writeback_allowed") is not False
        or worksheet.get("independent_responsibility_adjudication_performed") is not False
        or worksheet.get("accepted_target_contract_established") is not False
        or not isinstance(sha, str) or len(sha) != 40):
        raise DiscoveryError("unreviewed source worksheet with pinned snapshot required")
    if (draft.get("kind") != "harness-cdr-target-output-contract-candidates"
        or draft.get("status") != "OPERATOR_DRAFT_NOT_ACCEPTED"
        or draft.get("source_commit") != sha
        or draft.get("no_automatic_writeback") is not True):
        raise DiscoveryError("unaccepted target output draft must share snapshot")
    product_rows = _checked_report(
        product, "harness-cdr-target-claim-mapping-review",
        "PENDING_INDEPENDENT_CLAIM_TO_OBLIGATION_REVIEW", sha
    )
    strategy_rows = _checked_report(
        strategy, "harness-cdr-strategy-claim-review",
        "PENDING_INDEPENDENT_STRATEGY_CLAIM_REVIEW", sha
    )
    if (product.get("authority_review_performed") is not False
        or product.get("target_obligations_independently_accepted") is not False
        or strategy.get("accepted_target_output_obligations") is not False
        or strategy.get("individual_semantic_reviews_performed") != 0):
        raise DiscoveryError("an input has claimed semantic acceptance")
    contracts = draft.get("target_contracts")
    if not isinstance(contracts, list) or not contracts:
        raise DiscoveryError("missing target contracts")
    targets: dict[str, dict[str, Any]] = {}
    for item in contracts:
        cid = item.get("target_capability")
        if (not isinstance(cid, str) or cid in targets
            or item.get("target_contract_status") != "NEEDS_INDEPENDENT_AUTHORITY_REVIEW"):
            raise DiscoveryError("invalid, repeated or accepted target contract")
        obligations = item.get("candidate_obligations")
        if not isinstance(obligations, list) or not obligations:
            raise DiscoveryError("target output obligations missing")
        entries = {}
        for ob in obligations:
            if not isinstance(ob, dict):
                raise DiscoveryError("invalid draft output")
            oid = ob.get("id")
            desc = ob.get("description")
            if (not isinstance(oid, str) or not oid or oid in entries
                or not isinstance(desc, str) or len(desc.strip()) < 45
                or ob.get("status") != "CANDIDATE_NOT_ACCEPTED"):
                raise DiscoveryError("draft output obligation not independently accepted")
            entries[oid] = ob
        questions = item.get("unresolved_scope_questions")
        if not isinstance(questions, list) or any(
            not isinstance(q, str) or len(q.strip()) < 25 for q in questions
        ):
            raise DiscoveryError("missing valid independently unresolved scope questions")
        targets[cid] = {"obligations": entries, "questions": questions}
    if set(targets) != set(worksheet.get("source_targets", [])):
        raise DiscoveryError("draft and source worksheet targets differ")

    sources = worksheet.get("source_units")
    if not isinstance(sources, list) or len(sources) != worksheet.get("distinct_source_unit_count"):
        raise DiscoveryError("missing or changed accepted source inventory")
    by_uid: dict[str, dict[str, Any]] = {}
    for src in sources:
        uid = src.get("source_unit_id")
        if not isinstance(uid, str) or not uid or uid in by_uid:
            raise DiscoveryError("invalid or duplicate accepted source identifier")
        if (src.get("review_state") != "UNREVIEWED"
            or src.get("target_output_obligation_mapping_verified") is not False
            or src.get("automatic_writeback_allowed") is not False):
            raise DiscoveryError("source evidence was silently adjudicated")
        by_uid[uid] = src

    expected_product = {
        uid for uid, src in by_uid.items() if src["source_unit_kind"] in PRODUCT_KINDS
    }
    expected_strategy = set(by_uid) - expected_product
    if (len(product_rows) != product.get("source_claim_count")
        or len(strategy_rows) != strategy.get("individual_accepted_source_units_accounted_for")
        or len(product_rows) != len(by_uid)
        or len(strategy_rows) != len(expected_strategy)):
        raise DiscoveryError("not every accepted source unit accounted for")

    product_ids, strategy_ids = set(), set()
    for row in product_rows:
        uid = row.get("source_unit_id")
        if uid not in by_uid or uid in product_ids:
            raise DiscoveryError("unknown or duplicate product report source identifier")
        product_ids.add(uid)
        src = by_uid[uid]
        for attr in ("source_path", "source_sha256", "source_provider", "source_local_id",
                     "source_unit_kind", "source_text"):
            if row.get(attr) != src.get(attr):
                raise DiscoveryError("product evidence changed source provenance: " + attr)
        if (row.get("source_semantics_adjudicated") is not False
            or row.get("target_obligation_accepted") is not False
            or row.get("direct_provider_necessity_established") is not False
            or row.get("automatic_writeback_allowed") is not False):
            raise DiscoveryError("product claim promoted before Authority review")
        if uid in expected_product and row.get("classification_state") != "OPERATOR_HYPOTHESIS_NOT_REVIEWED":
            raise DiscoveryError("accepted product claim lacks review hypothesis")
        if uid not in expected_product and (
            row.get("classification_state") != "UNCLASSIFIED_REQUIRES_REVIEW"
            or row.get("proposed_links")
        ):
            raise DiscoveryError("strategy claims cannot leak into product hypotheses")
    for row in strategy_rows:
        uid = row.get("source_unit_id")
        if uid not in expected_strategy or uid in strategy_ids:
            raise DiscoveryError("unknown or duplicate MC/DS source identifier")
        strategy_ids.add(uid)
        src = by_uid[uid]
        for attr, prop in (
            ("source_path", "source_path"), ("source_sha256", "source_sha256"),
            ("source_provider", "source_provider"), ("source_local_id", "source_local_id"),
            ("source_text", "source_text"), ("review_revision", "source_review_revision"),
            ("source_heading", "source_heading")
        ):
            if row.get(prop) != src.get(attr):
                raise DiscoveryError("strategy evidence changed source provenance: " + attr)
        if (row.get("claim_semantically_adjudicated") is not False
            or row.get("target_obligation_accepted") is not False
            or row.get("direct_provider_necessity_proven") is not False
            or row.get("automatic_writeback_allowed") is not False):
            raise DiscoveryError("strategy claim promoted before Authority review")
    if product_ids != set(by_uid) or strategy_ids != expected_strategy:
        raise DiscoveryError("product and strategy reports omit accepted source units")

    # Both generators may contain identical *hints*, but only actual
    # claim-level proposal links are aggregated; source-section hints cannot
    # count as target obligation evidence.
    edges: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    per_source: dict[str, list[tuple[str, str, str]]] = defaultdict(list)
    uncertain: list[dict[str, Any]] = []
    for origin, rows, field in (
        ("PRODUCT", product_rows, "proposed_links"),
        ("MC_DS", strategy_rows, "candidate_target_links"),
    ):
        for row in rows:
            uid = row["source_unit_id"]
            links = row.get(field)
            if not isinstance(links, list):
                raise DiscoveryError("claim mapping must explicitly contain link list")
            local_seen = set()
            for link in links:
                cid,oid,relation = (
                    link.get("target_capability"), link.get("obligation_id"),
                    link.get("relation")
                )
                if cid not in targets or oid not in targets[cid]["obligations"]:
                    raise DiscoveryError("source mapping references unknown draft output")
                if not isinstance(relation, str) or not relation:
                    raise DiscoveryError("source mapping relation absent")
                if (cid,oid) in local_seen:
                    raise DiscoveryError("claim has duplicated target output mapping")
                local_seen.add((cid,oid))
                evidence = {
                    "source_unit_id": uid,
                    "source_path": row["source_path"],
                    "source_provider": row["source_provider"],
                    "source_claim_id": row["source_local_id"],
                    "source_text": row["source_text"],
                    "source_sha256": row["source_sha256"],
                    "candidate_relation": relation,
                    "hypothesis_origin": origin,
                    "semantically_verified": False,
                }
                edges[(cid,oid)].append(evidence)
                per_source[uid].append((cid,oid,relation))
                if relation in ("OPEN_SCOPE_QUESTION", "POSSIBLE_SHARED_BOUNDARY"):
                    uncertain.append({
                        "source_unit_id":uid,"target_capability":cid,
                        "obligation_id":oid,"reason":"OPEN_OR_SHARED_CLAIM_LINK"
                    })
    for row in strategy_rows:
        if (row["tentative_disposition"] in POTENTIALLY_OWNED
            and not row["candidate_target_links"]
            and not row.get("candidate_external_routes")):
            uncertain.append({
                "source_unit_id":row["source_unit_id"],
                "reason":"CANDIDATE_SCOPE_HAS_NO_TARGET_OR_EXTERNAL_ROUTE"
            })
        if row["tentative_disposition"] == "UNDETERMINED":
            uncertain.append({
                "source_unit_id":row["source_unit_id"],
                "reason":"SOURCE_CLAIM_DISPOSITION_UNDETERMINED"
            })

    # A source constraining both models may be a legitimately shared
    # boundary or negative invariant; flag the ownership question rather
    # than count it as a semantic contradiction.
    cross_target = []
    for uid, refs in sorted(per_source.items()):
        affected = sorted({r[0] for r in refs})
        if len(affected) > 1:
            cross_target.append({
                "source_unit_id":uid,
                "source_text":by_uid[uid]["source_text"],
                "candidate_target_capabilities":affected,
                "obligations":sorted({cid + ":" + oid for cid,oid,_ in refs}),
                "review_question": (
                    "Which meaning is uniquely owned by each model, and "
                    "which constraint belongs in their shared contract?"
                ),
                "duplicated_authoritative_ownership_proven": False,
            })

    reports=[]
    for cid,record in sorted(targets.items()):
        obligations=[]
        for oid, ob in sorted(record["obligations"].items()):
            evid=sorted(edges[(cid,oid)],key=lambda e:(
                e["hypothesis_origin"],e["source_path"],e["source_unit_id"]
            ))
            src_types=sorted({e["hypothesis_origin"] for e in evid})
            flags=[]
            if not evid:
                flags.append("NO_CLAIM_LEVEL_EVIDENCE_HYPOTHESIS")
            if not any(e["hypothesis_origin"]=="MC_DS" for e in evid):
                flags.append("NO_MODEL_OR_STRATEGY_CLAIM_LINK")
            if any(e["candidate_relation"] in UNCERTAIN_RELATIONS for e in evid):
                flags.append("SHARED_BOUNDARY_OR_OPEN_SCOPE_REQUIRES_REVIEW")
            if any(e["source_unit_id"] in {x["source_unit_id"] for x in cross_target} for e in evid):
                flags.append("CROSS_TARGET_CONSUMPTION_REQUIRES_BOUNDARY_REVIEW")
            obligations.append({
                "id":oid,"description":ob["description"],
                "status":"CANDIDATE_NOT_ACCEPTED",
                "source_claim_links":evid,
                "source_origins":src_types,
                "review_flags":flags,
                "independently_accepted":False,
                "meaning_fulfilled_by_sources_proven":False,
                "direct_dependency_proven":False,
            })
        reports.append({
            "target_capability":cid,
            "status":"PENDING_TARGET_OBLIGATION_REVIEW",
            "draft_obligations":obligations,
            "unresolved_original_scope_questions":record["questions"],
            "target_semantic_completeness_verified":False,
            "independent_authority_adjudication_performed":False,
        })
    return {
        "kind":"harness-cdr-cross-authority-target-semantic-audit",
        "version":1,"status":"REVIEW_REQUIRED_NO_SEMANTIC_ORACLE",
        "source_snapshot":sha,
        "source_unit_count":len(by_uid),
        "product_source_unit_count":len(expected_product),
        "strategy_source_unit_count":len(expected_strategy),
        "target_output_count":sum(len(x["draft_obligations"]) for x in reports),
        "target_reports":reports,
        "cross_target_source_consumption":cross_target,
        "open_source_hypotheses":uncertain,
        "source_claims_with_no_candidate_target_link":sum(
            not refs for uid,refs in per_source.items()
        ) if False else sum(uid not in per_source for uid in by_uid),
        "unreviewed_source_units":len(by_uid),
        "independent_authority_review_performed":False,
        "complete_target_output_semantics_established":False,
        "duplicate_authoritative_ownership_established":False,
        "automatic_writeback_allowed":False,
    }


def main() -> int:
    parser=argparse.ArgumentParser(description="Unaccepted cross-authority draft target audit")
    parser.add_argument("--worksheet",type=Path,required=True)
    parser.add_argument("--draft",type=Path,required=True)
    parser.add_argument("--product",type=Path,required=True)
    parser.add_argument("--strategy",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    try:
        report=audit_target_obligations(
            json.loads(args.worksheet.read_text(encoding="utf-8")),
            _required_yaml(args.draft),
            json.loads(args.product.read_text(encoding="utf-8")),
            json.loads(args.strategy.read_text(encoding="utf-8")),
        )
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        print(json.dumps({
            "status":report["status"],
            "accepted_source_units":report["source_unit_count"],
            "draft_target_obligations":report["target_output_count"],
            "cross_target_review_sources":len(report["cross_target_source_consumption"]),
            "uncertain_claim_links":len(report["open_source_hypotheses"]),
            "semantic_completeness_established":report["complete_target_output_semantics_established"],
        },ensure_ascii=False))
        return 0
    except (DiscoveryError,KeyError,ValueError,TypeError,OSError) as exc:
        print(json.dumps({"status":"INVALID","error":str(exc)},ensure_ascii=False))
        return 2


if __name__=="__main__":
    raise SystemExit(main())
