"""Opt-in CDR intake and post-evaluator reconciliation for new Capabilities.

Two phases: a SOURCE-ONLY blind request for an externally supplied evaluator,
then a graph-aware read-only review after predictions. A draft target contract,
even with valid citations, is never an accepted target contract or graph edit.
Unlike PREP-specific research pilots this supports a new Capability that does
not yet have an Engineering Graph production or a Core artifact.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any

from evals.project_discovery_snapshot import (
    DiscoveryError, _commit, _required_yaml, _resolve, _markdown_claims,
    _yaml_claims,
)
from evals.dependency_resolution_evidence import assess_predictions
from evals.project_discovery_directness import audit_additions
from evals.project_discovery_directness_review import review_packets

KIND = "harness-cdr-capability-intake-v1"


def _producers(root: Path) -> dict[str, dict[str, Any]]:
    graph = _required_yaml(root / ".harness/engineering-graph.yaml")
    authorities = graph.get("authorities")
    if not isinstance(authorities, list):
        raise DiscoveryError("Engineering Graph authorities must be a list")
    result = {}
    for authority in authorities:
        if not isinstance(authority, dict) or not isinstance(authority.get("id"), str):
            raise DiscoveryError("invalid Engineering Graph Authority")
        productions = authority.get("produces", [])
        if not isinstance(productions, list):
            raise DiscoveryError("invalid Authority productions")
        for item in productions:
            cid = item.get("capability") if isinstance(item, dict) else None
            if not isinstance(cid, str) or not cid or cid in result:
                raise DiscoveryError("missing or duplicate Capability production")
            requires = item.get("requires", [])
            if not isinstance(requires, list):
                raise DiscoveryError("invalid requires list")
            normalized=[]
            seen=set()
            for req in requires:
                upstream = req.get("capability") if isinstance(req, dict) else None
                if not isinstance(upstream, str) or not upstream or upstream in seen:
                    raise DiscoveryError("malformed or repeated direct requires entry")
                seen.add(upstream)
                normalized.append({"capability":upstream})
            result[cid] = {
                "authority":authority["id"],
                "knowledge_kind":item.get("knowledge_kind"),
                "requires":normalized,
            }
    return result


def _catalog(root: Path, productions: dict[str, Any]) -> list[dict[str, Any]]:
    core=_required_yaml(root/".harness/core.yaml")
    baseline=_required_yaml(root/".harness/semantic-baseline.yaml")
    if core.get("questions"):
        raise DiscoveryError("unresolved Core questions block accepted source discovery")
    reviews=baseline.get("reviews")
    artifacts=core.get("artifacts")
    if not isinstance(reviews,list) or not isinstance(artifacts,list):
        raise DiscoveryError("missing Core artifact or semantic review inventory")
    rev={}
    for review in reviews:
        if not isinstance(review,dict):
            raise DiscoveryError("malformed semantic baseline")
        cid=review.get("capability")
        if not isinstance(cid,str) or cid in rev:
            raise DiscoveryError("duplicate or malformed semantic review")
        version=review.get("revision")
        if type(version) is not int or version<1:
            raise DiscoveryError("invalid provider semantic revision")
        rev[cid]=version
    registered=set()
    providers=[]
    for artifact in artifacts:
        if not isinstance(artifact,dict):
            raise DiscoveryError("invalid Core artifact")
        path=artifact.get("path")
        provides=artifact.get("provides")
        if not isinstance(path,str) or not isinstance(provides,list):
            raise DiscoveryError("invalid Core registered source")
        for cid in provides:
            if not isinstance(cid,str) or cid in registered:
                raise DiscoveryError("duplicate or invalid Core provider")
            registered.add(cid)
            if cid not in rev:
                continue
            if cid not in productions:
                raise DiscoveryError("reviewed provider missing Engineering Graph production")
            if artifact.get("authority")!=productions[cid]["authority"]:
                raise DiscoveryError("reviewed Core producer Authority mismatch")
            fp=_resolve(root,path)
            raw=fp.read_bytes()
            claims=(_markdown_claims(raw.decode("utf-8")) if path.endswith(".md")
                    else _yaml_claims(_required_yaml(fp)))
            if not claims or len(claims)>500 or any(not isinstance(c,str) for c in claims):
                raise DiscoveryError("missing, invalid or excessive accepted semantic claims")
            providers.append({
                "capability":cid,
                "authority":productions[cid]["authority"],
                "evidence_status":"ACCEPTED_EVIDENCE",
                "source":path,
                "source_sha256":hashlib.sha256(raw).hexdigest(),
                "review_revision":rev[cid],
                "semantic_surface":claims,
            })
    return sorted(providers,key=lambda x:x["capability"])


def prepare_intake(root: Path, *, sha: str, intake: dict[str, Any]) -> dict[str, Any]:
    root=root.resolve()
    _commit(root,sha)
    if (intake.get("kind")!=KIND or intake.get("version")!=1
        or intake.get("status")!="DRAFT_NOT_ACCEPTED"
        or intake.get("source_commit")!=sha
        or intake.get("automatic_writeback_allowed") is not False):
        raise DiscoveryError("invalid, unpinned or self-accepted CDR intake")
    target=intake.get("target")
    if not isinstance(target,dict):
        raise DiscoveryError("target contract missing")
    capability=target.get("capability")
    authority=target.get("authority")
    kind=target.get("knowledge_kind")
    if any(not isinstance(x,str) or not x.strip() for x in (capability,authority,kind)):
        raise DiscoveryError("target identity, Authority and knowledge kind required")
    productions=_producers(root)
    if capability in productions and (
        productions[capability]["authority"]!=authority
        or productions[capability]["knowledge_kind"]!=kind
    ):
        raise DiscoveryError("target already has different declared production ownership")
    obligations=target.get("output_obligations")
    constraints=target.get("governing_constraints",[])
    if not isinstance(obligations,list) or not obligations or not isinstance(constraints,list):
        raise DiscoveryError("target obligations/constraints missing")
    ids=set()
    checked=[]
    for ob in obligations:
        if not isinstance(ob,dict) or set(ob)!={"id","description"}:
            raise DiscoveryError("output obligation requires only id and description")
        oid,desc=ob["id"],ob["description"]
        if (not isinstance(oid,str) or not oid or oid in ids
            or not isinstance(desc,str) or len(desc.strip())<45):
            raise DiscoveryError("ambiguous or empty target obligation")
        ids.add(oid)
        checked.append({"id":oid,"description":desc.strip()})
    used=set()
    checked_constraints=[]
    for c in constraints:
        if not isinstance(c,dict) or set(c)!={"id","description","applies_to_outputs"}:
            raise DiscoveryError("invalid governing constraint shape")
        cid,desc,applies=c["id"],c["description"],c["applies_to_outputs"]
        if (not isinstance(cid,str) or not cid or cid in ids or cid in used
            or not isinstance(desc,str) or len(desc.strip())<35
            or not isinstance(applies,list) or len(applies)!=len(set(applies))
            or not set(applies) or not set(applies).issubset(ids)):
            raise DiscoveryError("invalid or dangling governing constraint")
        used.add(cid)
        checked_constraints.append({"id":cid,"description":desc.strip(),"applies_to_outputs":applies})
    catalog=[p for p in _catalog(root,productions) if p["capability"]!=capability]
    if not catalog:
        raise DiscoveryError("no accepted reviewed providers available")
    # Avoid accidentally presenting a provider's entire quoted public claim
    # as the user's own accepted target obligation.
    provider_ids={x["capability"] for x in catalog}
    provider_claims={line.strip() for p in catalog for line in p["semantic_surface"]}
    if any(any(pid in ob["description"] for pid in provider_ids)
           or ob["description"] in provider_claims for ob in checked):
        raise DiscoveryError("target obligation copies or names a supplier")
    case={"id":"INTAKE-01",
          "source_snapshot":sha,
          "target":{"capability":capability,"authority":authority,
                    "knowledge_kind":kind,"output_obligations":checked,
                    "governing_constraints":checked_constraints},
          "provider_catalog":catalog,
          "known_uncertainties":[
              "TARGET_DRAFT_NOT_ACCEPTED",
              "PROVIDER_DIRECTNESS_NOT_INDEPENDENTLY_ADJUDICATED",
              "UPSTREAM_SEMANTIC_APPLICABILITY_NOT_PROVEN",
          ]}
    return {
        "version":1,
        "kind":"harness-dependency-resolution-calibration-inputs",
        "status":"OPERATIONAL_DRAFT_INTAKE_REVIEW_ONLY",
        "evidence_contract":"source-grounded-v1",
        "coverage_contract":"legacy",
        "source_snapshot":sha,
        "target_formulation_authority":"OPERATOR_DRAFT_NOT_ACCEPTED",
        "target_obligation_coverage":{
            "status":"PARTIAL_BY_CONSTRUCTION",
            "complete_upstream_obligation_coverage_established":False,
            "complete_target_output_obligation_coverage_established":False,
        },
        "cases":[case],
        "automatic_writeback_allowed":False,
    }


def reconcile_intake(root: Path, *, sha: str, intake: dict[str, Any],
                     predictions: dict[str, Any]) -> dict[str, Any]:
    # Reconstituting the corpus from immutable sources guards against
    # post-prepare provider-catalog and target-contract substitution.
    inputs=prepare_intake(root,sha=sha,intake=intake)
    cases=predictions.get("cases") if isinstance(predictions,dict) else None
    if (predictions.get("kind")!="harness-dependency-resolution-predictions"
        or predictions.get("version")!=1
        or not isinstance(cases,list) or len(cases)!=1
        or cases[0].get("id")!="INTAKE-01"):
        raise DiscoveryError("missing or unbound evaluator prediction")
    prediction=cases[0]
    evaluated=assess_predictions(inputs,predictions)
    if evaluated.get("status")=="INVALID":
        raise DiscoveryError("model proposal did not pass source reference checks")
    actual=prediction.get("proposed_requires")
    available={p["capability"] for p in inputs["cases"][0]["provider_catalog"]}
    if not isinstance(actual,list) or len(actual)!=len(set(actual)) or any(
        not isinstance(p,str) or p not in available for p in actual
    ):
        raise DiscoveryError("proposal references unavailable or duplicated supplier")
    described={x["id"] for x in inputs["cases"][0]["target"]["output_obligations"]}
    resolved=prediction.get("unresolved_obligations")
    if not isinstance(resolved,list) or len(resolved)!=len(set(resolved)):
        raise DiscoveryError("unresolved obligation list invalid")
    needs=prediction.get("input_needs")
    if not isinstance(needs,list):
        raise DiscoveryError("missing source-grounded direct needs")
    accounted={x.get("obligation") for x in needs if isinstance(x,dict)}|set(resolved)
    if accounted!=described:
        raise DiscoveryError("model silently skipped target output obligations")
    graph=_producers(root)
    target=inputs["cases"][0]["target"]["capability"]
    current={v["capability"] for v in graph.get(target,{}).get("requires",[])}
    audit=audit_additions(
        inputs["cases"][0],prediction,existing_requires=current,productions=graph
    )
    packets=review_packets(
        inputs["cases"][0],prediction,accepted_requires=current,
        productions=graph,directness_audit=audit,source_snapshot=sha,
        target_formulation_authority="OPERATOR_DRAFT_NOT_ACCEPTED",
    )
    return {
        "kind":"harness-cdr-intake-reconciliation-v1",
        "status":"REVIEW_REQUIRED",
        "source_snapshot":sha,
        "target_capability":target,
        "target_graph_presence":"DECLARED" if target in graph else "NOT_YET_DECLARED",
        "KEEP":sorted(current & set(actual)),
        "ADD":sorted(set(actual)-current),
        "UNASSESSED_EXISTING_EDGES":sorted(current-set(actual)),
        "REMOVE_CANDIDATE":[],
        "directness_audit":audit,
        "directness_review_packets":packets,
        "source_reference_assessment":evaluated,
        "unresolved_output_obligations":sorted(resolved),
        "target_contract_independently_accepted":False,
        "semantic_entailment_verified":False,
        "complete_target_output_obligation_coverage_established":False,
        "automatic_writeback_allowed":False,
    }


def main() -> int:
    p=argparse.ArgumentParser(description="Opt-in read-only Capability Dependency Resolution")
    p.add_argument("phase",choices=("prepare","reconcile"))
    p.add_argument("--project-root",type=Path,required=True)
    p.add_argument("--commit",required=True)
    p.add_argument("--intake",type=Path,required=True)
    p.add_argument("--predictions",type=Path)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    try:
        intake=_required_yaml(args.intake)
        if args.phase=="reconcile":
            if args.predictions is None:
                raise DiscoveryError("reconcile requires a prediction report")
            predictions=json.loads(args.predictions.read_text(encoding="utf-8"))
            result=reconcile_intake(args.project_root,sha=args.commit,
                                    intake=intake,predictions=predictions)
        else:
            if args.predictions is not None:
                raise DiscoveryError("prepare cannot receive evaluator predictions")
            result=prepare_intake(args.project_root,sha=args.commit,intake=intake)
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        print(json.dumps({
            "status":result["status"],
            "source_snapshot":result["source_snapshot"],
            "automatic_writeback_allowed":False,
        }))
        return 0
    except (DiscoveryError,ValueError,TypeError,KeyError,OSError) as e:
        print(json.dumps({"status":"INVALID","error":str(e)},ensure_ascii=False))
        return 2

if __name__=="__main__":
    raise SystemExit(main())
