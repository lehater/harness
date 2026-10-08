#!/usr/bin/env python3
"""Join all 123 review-only PREP claim hypotheses against eight target drafts."""
from __future__ import annotations

import copy
import hashlib
from pathlib import Path
import sys

import yaml

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))

from evals.project_discovery_snapshot import DiscoveryError
from evals.project_strategy_claim_review import build_strategy_claim_review
from evals.project_target_claim_mapping import build_claim_mapping
from evals.project_target_semantic_audit import audit_target_obligations

PILOT=ROOT/"spec/dependency-resolution/project-pilots"
load=lambda x: yaml.safe_load((PILOT/x).read_text(encoding="utf-8"))
draft=load("prep-target-output-candidates-v1.yaml")
products=load("prep-claim-obligation-hypotheses-v1.yaml")
strategy=load("prep-strategy-claim-hypotheses-v1.yaml")
sha=draft["source_commit"]
targets=[c["target_capability"] for c in draft["target_contracts"]]
assert len(targets)==2
assert len(products["source_claims"])==21
assert sum(len(x["claims"]) for x in strategy["sections"])==102

def unit(path,heading,local,meaning,kind,provider,revision):
    key=hashlib.sha256(
        (path+"\n"+str(heading)+"\n"+local+"\n"+meaning).encode("utf-8")
    ).hexdigest()[:20]
    return {
        "source_unit_id":key,"source_path":path,"source_heading":heading,
        "source_local_id":local,"source_text":meaning,
        "source_sha256":hashlib.sha256((path+" fixture").encode()).hexdigest(),
        "source_provider":provider,"review_revision":revision,
        "scope_role":"MODEL_CONTEXT" if heading else "PRODUCT_CONSTRAINTS",
        "source_unit_kind":kind,
        "seen_by_target_capabilities":list(targets),
        "candidate_draft_obligation_ids_by_target":{t:[] for t in targets},
        "review_state":"UNREVIEWED",
        "semantic_route":"UNDETERMINED","semantic_effect":"UNDETERMINED",
        "target_output_obligation_mapping_verified":False,
        "automatic_writeback_allowed":False,
    }

units=[]
for section in strategy["sections"]:
    path=section["source_path"]
    provider=("prep.model-context-strategy" if "model-context-map" in path
              else "prep.domain-strategy")
    for x in section["claims"]:
        units.append(unit(
            path,section["source_heading"],str(x["index"]),
            x["expected_source_text"],"ACCEPTED_SOURCE_SECTION_STATEMENT",
            provider,1,
        ))
for x in products["source_claims"]:
    units.append(unit(
        x["source_path"],None,x["source_local_id"],
        "Accepted source statement for "+x["source_local_id"],
        x["source_unit_kind"],"prep.product-capabilities",1,
    ))
assert len(units)==123
assert len({x["source_unit_id"] for x in units})==123
worksheet={
    "kind":"harness-cdr-source-responsibility-worksheet",
    "status":"PENDING_INDEPENDENT_RESPONSIBILITY_REVIEW",
    "source_snapshot":sha,"source_targets":targets,
    "source_units":units,"distinct_source_unit_count":len(units),
    "independent_responsibility_adjudication_performed":False,
    "accepted_target_contract_established":False,
    "automatic_writeback_allowed":False,
}
p=build_claim_mapping(worksheet,draft,proposals=products)
s=build_strategy_claim_review(worksheet,draft,strategy)
report=audit_target_obligations(worksheet,draft,p,s)

assert report["status"]=="REVIEW_REQUIRED_NO_SEMANTIC_ORACLE"
assert report["source_unit_count"]==123
assert report["product_source_unit_count"]==21
assert report["strategy_source_unit_count"]==102
assert report["target_output_count"]==8
assert len(report["target_reports"])==2
assert len(report["cross_target_source_consumption"])>0
assert len(report["open_source_hypotheses"])>0
assert report["unreviewed_source_units"]==123
assert report["independent_authority_review_performed"] is False
assert report["complete_target_output_semantics_established"] is False
assert report["duplicate_authoritative_ownership_established"] is False
assert report["automatic_writeback_allowed"] is False
obligations={
    ob["id"]:ob
    for target in report["target_reports"]
    for ob in target["draft_obligations"]
}
assert len(obligations)==8
assert all(ob["independently_accepted"] is False for ob in obligations.values())
assert all(ob["meaning_fulfilled_by_sources_proven"] is False for ob in obligations.values())
assert all(ob["direct_dependency_proven"] is False for ob in obligations.values())
assert len(obligations["RH-PRESERVED-CONTEXT"]["source_claim_links"])>0
assert "SHARED_BOUNDARY_OR_OPEN_SCOPE_REQUIRES_REVIEW" in obligations["RH-PRESERVED-CONTEXT"]["review_flags"]
assert obligations["PI-KNOWLEDGE-AND-RELATIONS"]["source_origins"]==["MC_DS","PRODUCT"]
assert all(x["target_semantic_completeness_verified"] is False for x in report["target_reports"])
assert any(
    {"prep.preparation-information-model","prep.recorded-activity-history-model"}
    == set(x["candidate_target_capabilities"])
    for x in report["cross_target_source_consumption"]
)

def rejects(worksheet_,draft_,product_,strategy_,part):
    try:
        audit_target_obligations(worksheet_,draft_,product_,strategy_)
    except DiscoveryError as e:
        assert part in str(e),str(e)
    else:
        raise AssertionError("Expected rejection: "+part)

bad=copy.deepcopy(p)
bad["source_claims"].pop()
rejects(worksheet,draft,bad,s,"not every accepted source unit")
bad=copy.deepcopy(s)
bad["source_claims"].pop()
rejects(worksheet,draft,p,bad,"not every accepted source unit")
bad=copy.deepcopy(s)
bad["source_claims"][0]["source_text"]="Falsified strategic statement"
rejects(worksheet,draft,p,bad,"strategy evidence changed source provenance")
bad=copy.deepcopy(p)
bad["source_claims"][-1]["source_sha256"]="0"*64
rejects(worksheet,draft,bad,s,"product evidence changed source provenance")
bad=copy.deepcopy(s)
bad["source_claims"][0]["claim_semantically_adjudicated"]=True
rejects(worksheet,draft,p,bad,"promoted before Authority review")
bad=copy.deepcopy(p)
bad["source_claims"][0]["direct_provider_necessity_established"]=True
rejects(worksheet,draft,bad,s,"promoted before Authority review")
bad=copy.deepcopy(draft)
bad["target_contracts"][0]["candidate_obligations"][0]["status"]="ACCEPTED"
rejects(worksheet,bad,p,s,"not independently accepted")
bad=copy.deepcopy(p)
bad["source_snapshot"]="0"*40
rejects(worksheet,draft,bad,s,"wrong report")
bad=copy.deepcopy(worksheet)
bad["source_units"].append(copy.deepcopy(bad["source_units"][0]))
bad["distinct_source_unit_count"]+=1
rejects(bad,draft,p,s,"duplicate accepted source identifier")
bad=copy.deepcopy(p)
bad["source_claims"][0]["proposed_links"]=[{
    "target_capability":targets[0],
    "obligation_id":"FORGED",
    "relation":"CANDIDATE_SEMANTIC_CONSTRAINT",
}]
rejects(worksheet,draft,bad,s,"unknown draft output")

print("dependency resolution unified tactical semantic audit: PASS")
print(
    "Source units:",report["source_unit_count"],
    "draft outputs:",report["target_output_count"],
    "shared source consumption:",len(report["cross_target_source_consumption"]),
    "open hypotheses:",len(report["open_source_hypotheses"]),
)
