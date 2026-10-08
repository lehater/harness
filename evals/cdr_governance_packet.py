"""Read-only, independently-reviewable CDR decision dossier.

A human or another system can record an *operator draft* review, but neither
that assertion nor a passing schema check is proof of accepted semantics.
There is no operation to accept, rewrite or promote Engineering Graph edges.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from evals.project_discovery_snapshot import DiscoveryError, _required_yaml
from evals.cdr_operational import reconcile_intake
from evals.project_target_contract_readiness import audit_target_contracts
from evals.project_discovery_directness_review import REQUIRED_TESTS


def digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(
        value, sort_keys=True, separators=(",",":"), ensure_ascii=False
    ).encode("utf-8")).hexdigest()


def build_decision_dossier(
    root: Path, *, sha: str, intake: dict[str, Any],
    predictions: dict[str, Any],
) -> dict[str, Any]:
    reconciliation=reconcile_intake(root,sha=sha,intake=intake,predictions=predictions)
    target=reconciliation["target_capability"]
    audit=audit_target_contracts(root,sha=sha,targets=[target])
    target_readiness=audit["cases"][0]
    needs=predictions["cases"][0]["input_needs"]
    outputs={x["id"]:x["description"] for x in intake["target"]["output_obligations"]}
    constraints={x["id"]:x for x in intake["target"]["governing_constraints"]}
    affected={}
    for need in needs:
        ident=need["obligation"]
        affected.setdefault(ident,[]).append({
            "provider":need["provider"],
            "claim_index":need["claim_index"],
            "consumption_rationale":need["consumption_rationale"],
        })
    source_review=reconciliation["source_reference_assessment"]
    evidence_case=source_review["cases"][0]
    citations=evidence_case.get("referenced_claims",[])
    referenced={(x["obligation"],x["provider"],x["claim_index"]):x for x in citations}
    obligations=[]
    for oid,description in outputs.items():
        items=[]
        for link in affected.get(oid,[]):
            key=(oid,link["provider"],link["claim_index"])
            verified=referenced.get(key)
            if verified is None:
                raise DiscoveryError("missing source-grounded reference in reviewer packet")
            items.append({
                "provider":link["provider"],"claim_index":link["claim_index"],
                "accepted_source_claim":verified["claim_text"],
                "consumption_rationale":link["consumption_rationale"],
                "semantic_entailment_verified":False,
            })
        obligations.append({
            "id":oid,"description":description,
            "candidate_provider_needs":items,
            "status":"TARGET_OBLIGATION_NOT_INDEPENDENTLY_ACCEPTED",
            "owner_review_question":(
                "Is the obligation an independently required target output, "
                "and have all materially applicable source constraints been considered?"
            ),
        })
    packets=reconciliation["directness_review_packets"]
    proposals=[{
        "provider":packet["provider"],
        "proposed_action":"ADD",
        "source_snapshot":sha,
        "existing_transitive_paths":packet["existing_transitive_paths"],
        "source_echo_obligations":packet["source_echo_obligations"],
        "claim_evidence":packet["individual_need_evidence"],
        "required_directness_tests":list(REQUIRED_TESTS),
        "review_conclusion":"INDETERMINATE",
        "authority_adjudication_pending":True,
    } for packet in packets]
    dossier={
        "kind":"harness-cdr-governance-decision-dossier",
        "version":1,
        "source_snapshot":sha,
        "target_capability":target,
        "target_owner_authority":intake["target"]["authority"],
        "target_output_obligations":obligations,
        "governing_constraints":list(constraints.values()),
        "readiness_blockers":target_readiness["blockers"],
        "target_artifact":target_readiness["target_artifact"],
        "target_semantic_baseline":target_readiness["semantic_baseline"],
        "KEEP":reconciliation["KEEP"],
        "proposed_ADD":proposals,
        "UNASSESSED_EXISTING_EDGES":reconciliation["UNASSESSED_EXISTING_EDGES"],
        "unresolved_output_obligations":reconciliation["unresolved_output_obligations"],
        "removal_eligible":False,
        "independent_target_acceptance_proven":False,
        "directness_semantically_adjudicated":False,
        "authority_approval_verified":False,
        "automatic_writeback_allowed":False,
        "status":"REVIEW_DOSSIER_NOT_AUTHORIZATION",
    }
    return {**dossier,"dossier_sha256":digest(dossier)}


def validate_draft_review(
    dossier: dict[str, Any], review: dict[str, Any]
) -> dict[str, Any]:
    # Validate linkage to a generated, internally consistent dossier.
    original={k:v for k,v in dossier.items() if k!="dossier_sha256"}
    if (dossier.get("kind")!="harness-cdr-governance-decision-dossier"
        or dossier.get("status")!="REVIEW_DOSSIER_NOT_AUTHORIZATION"
        or dossier.get("automatic_writeback_allowed") is not False
        or dossier.get("authority_approval_verified") is not False
        or digest(original)!=dossier.get("dossier_sha256")):
        raise DiscoveryError("invalid or tampered review dossier")
    if (review.get("kind")!="harness-cdr-independent-review-draft"
        or review.get("status")!="PROPOSED_NOT_ACCEPTED"
        or review.get("dossier_sha256")!=dossier["dossier_sha256"]
        or review.get("source_snapshot")!=dossier["source_snapshot"]
        or review.get("target_capability")!=dossier["target_capability"]
        or review.get("automatic_writeback_allowed") is not False):
        raise DiscoveryError("review draft is unbound or claims acceptance")
    rows=review.get("output_findings")
    if not isinstance(rows,list):
        raise DiscoveryError("output review rows missing")
    required={x["id"] for x in dossier["target_output_obligations"]}
    seen=set()
    for row in rows:
        if not isinstance(row,dict):
            raise DiscoveryError("invalid output finding")
        key=row.get("obligation_id")
        if key not in required or key in seen:
            raise DiscoveryError("duplicate or unknown output finding")
        seen.add(key)
        if row.get("decision") not in ("REVIEW_NEEDED","REVISE_DRAFT","REJECT_DRAFT"):
            raise DiscoveryError("owner review may not be self-recorded as acceptance")
        if not isinstance(row.get("reason"),str) or len(row["reason"].strip())<35:
            raise DiscoveryError("source-specific output review reason required")
    edges=review.get("directness_findings")
    if not isinstance(edges,list):
        raise DiscoveryError("directness review rows missing")
    wanted={x["provider"] for x in dossier["proposed_ADD"]}
    got=set()
    for row in edges:
        if not isinstance(row,dict):
            raise DiscoveryError("malformed directness draft")
        supplier=row.get("provider")
        if supplier not in wanted or supplier in got:
            raise DiscoveryError("unknown or duplicate directness review provider")
        got.add(supplier)
        if row.get("decision") not in (
            "UNDETERMINED","LIKELY_DIRECT","LIKELY_INHERITED","REJECT_DRAFT"
        ):
            raise DiscoveryError("review draft cannot assert accepted directness")
        tests=row.get("tests")
        if not isinstance(tests,list):
            raise DiscoveryError("directness test rows missing")
        labels=set()
        for test in tests:
            if not isinstance(test,dict) or test.get("test") not in REQUIRED_TESTS:
                raise DiscoveryError("unknown directness test")
            if test["test"] in labels:
                raise DiscoveryError("duplicate directness test")
            labels.add(test["test"])
            if test.get("finding") not in ("UNREVIEWED","SUPPORTS_DIRECT","SUPPORTS_INHERITED","INCONCLUSIVE"):
                raise DiscoveryError("malformed directness review finding")
            if not isinstance(test.get("evidence"),str) or len(test["evidence"].strip())<35:
                raise DiscoveryError("directness review needs specific evidence")
        if labels!=set(REQUIRED_TESTS):
            raise DiscoveryError("missing independent directness test")
    if seen!=required or got!=wanted:
        raise DiscoveryError("review draft omits outputs or proposed direct suppliers")
    return {
        "status":"DRAFT_COMPLETE_FOR_AUTHORITY_CONSIDERATION",
        "dossier_sha256":dossier["dossier_sha256"],
        "record_count":len(rows)+len(edges),
        "reviewer_identity_verified":False,
        "target_contract_independently_accepted":False,
        "semantic_necessity_proven":False,
        "governance_transition_authorized":False,
        "automatic_writeback_allowed":False,
    }


def main()->int:
    parser=argparse.ArgumentParser(description="Non-authorizing CDR governance review packet")
    parser.add_argument("phase",choices=("prepare","check-draft"))
    parser.add_argument("--project-root",type=Path)
    parser.add_argument("--commit")
    parser.add_argument("--intake",type=Path)
    parser.add_argument("--predictions",type=Path)
    parser.add_argument("--dossier",type=Path)
    parser.add_argument("--review",type=Path)
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    try:
        if args.phase=="prepare":
            if not all([args.project_root,args.commit,args.intake,args.predictions]):
                raise DiscoveryError("prepare requires source project, pin, intake, and prediction file")
            result=build_decision_dossier(
                args.project_root,sha=args.commit,
                intake=_required_yaml(args.intake),
                predictions=json.loads(args.predictions.read_text(encoding="utf-8")),
            )
        else:
            if not all([args.project_root,args.commit,args.intake,args.predictions,
                        args.dossier,args.review]):
                raise DiscoveryError("check-draft requires pinned source evidence, dossier and review")
            expected=build_decision_dossier(
                args.project_root,sha=args.commit,
                intake=_required_yaml(args.intake),
                predictions=json.loads(args.predictions.read_text(encoding="utf-8")),
            )
            supplied=json.loads(args.dossier.read_text(encoding="utf-8"))
            if supplied!=expected:
                raise DiscoveryError("review dossier differs from freshly regenerated pinned source evidence")
            result=validate_draft_review(expected,_required_yaml(args.review))
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
        print(json.dumps({"status":result["status"],"automatic_writeback_allowed":False}))
        return 0
    except (DiscoveryError,KeyError,TypeError,ValueError,OSError) as exc:
        print(json.dumps({"status":"INVALID","error":str(exc)},ensure_ascii=False))
        return 2


if __name__=="__main__":
    raise SystemExit(main())
