#!/usr/bin/env python3
"""Every pinned MC/DS claim must be accounted for; no semantics self-certified."""
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

config=yaml.safe_load((ROOT/"spec/dependency-resolution/project-pilots/"
    "prep-strategy-claim-hypotheses-v1.yaml").read_text(encoding="utf-8"))
targets={
    "prep.preparation-information-model":[
        "PI-SEMANTIC-CONCEPTS","PI-KNOWLEDGE-AND-RELATIONS",
        "PI-BOUNDARY-TO-HISTORY","PI-NEGATIVE-INVARIANTS"],
    "prep.recorded-activity-history-model":[
        "RH-RECORDED-FACTS","RH-REFERENCED-INFORMATION",
        "RH-PRESERVED-CONTEXT","RH-NEGATIVE-INVARIANTS"],
}
sha=config["source_commit"]
draft={
    "kind":"harness-cdr-target-output-contract-candidates",
    "status":"OPERATOR_DRAFT_NOT_ACCEPTED","source_commit":sha,
    "no_automatic_writeback":True,
    "target_contracts":[{
        "target_capability":cid,
        "target_contract_status":"NEEDS_INDEPENDENT_AUTHORITY_REVIEW",
        "candidate_obligations":[{"id":oid,"status":"CANDIDATE_NOT_ACCEPTED"}
                                 for oid in ids],
    } for cid,ids in targets.items()],
}
units=[]
for section in config["sections"]:
    path,heading=section["source_path"],section["source_heading"]
    for item in section["claims"]:
        local=str(item["index"])
        text=item["expected_source_text"]
        uid=hashlib.sha256(
            (path+"\n"+str(heading)+"\n"+local+"\n"+text).encode("utf-8")
        ).hexdigest()[:20]
        units.append({
            "source_unit_id":uid, "source_path":path,
            "source_heading":heading,"source_local_id":local,
            "source_sha256":"a"*64,
            "review_revision":3,"source_provider":"x.accepted-strategy",
            "source_role":"MODEL_CONTEXT",
            "source_unit_kind":"ACCEPTED_SOURCE_SECTION_STATEMENT",
            "scope_role":"MODEL_CONTEXT",
            "source_text":text,
            "seen_by_target_capabilities":list(targets),
            "review_state":"UNREVIEWED",
            "semantic_route":"UNDETERMINED",
            "target_output_obligation_mapping_verified":False,
        })
assert len(units)==102
assert len({x["source_unit_id"] for x in units})==102
worksheet={
    "kind":"harness-cdr-source-responsibility-worksheet",
    "status":"PENDING_INDEPENDENT_RESPONSIBILITY_REVIEW",
    "source_snapshot":sha,
    "source_targets":list(targets),
    "source_units":units,
    "independent_responsibility_adjudication_performed":False,
    "automatic_writeback_allowed":False,
}
report=build_strategy_claim_review(worksheet,draft,config)
assert report["status"]=="PENDING_INDEPENDENT_STRATEGY_CLAIM_REVIEW"
assert report["individual_accepted_source_units_accounted_for"]==102
assert report["source_units_remaining_unaccounted_for"]==0
assert report["tentative_dispositions"]=={
    "APPLICATION_CONSUMER":14,
    "GOVERNANCE_CONDITION":14,
    "NEGATIVE_INVARIANT_CANDIDATE":9,
    "SCOPE_EXCLUSION":17,
    "SHARED_BOUNDARY_CANDIDATE":12,
    "STRUCTURAL_OR_TRACE_CONTEXT":13,
    "TARGET_SEMANTIC_CANDIDATE":21,
    "UNDETERMINED":2,
}
assert report["individual_semantic_reviews_performed"]==0
assert report["accepted_target_output_obligations"] is False
assert report["complete_target_output_semantics_proven"] is False
assert report["direct_dependencies_verified"] is False
assert report["automatic_writeback_allowed"] is False
assert all(
    row["claim_semantically_adjudicated"] is False
    and row["direct_provider_necessity_proven"] is False
    and row["target_obligation_accepted"] is False
    for row in report["source_claims"]
)
def pick(path,heading,idx):
    return next(row for row in report["source_claims"]
                if row["source_path"]==path and row["source_heading"]==heading
                and row["source_local_id"]==str(idx))
mc="docs/architecture/model-context-map.md"
ds="docs/architecture/context-map.md"
assert pick(mc,"MC-01 Preparation Information",10)["tentative_disposition"]=="NEGATIVE_INVARIANT_CANDIDATE"
assert pick(mc,"TR-01 Preparation Information and Recorded Activity History",5)["tentative_disposition"]=="SHARED_BOUNDARY_CANDIDATE"
assert pick(mc,"Behaviors without independent model contexts",2)["tentative_disposition"]=="UNDETERMINED"
assert pick(ds,"DS-01 Preparation Information — CORE",2)["tentative_disposition"]=="STRUCTURAL_OR_TRACE_CONTEXT"
assert pick(ds,"Consumers",1)["tentative_disposition"]=="GOVERNANCE_CONDITION"
assert pick(ds,"Reopening conditions",3)["tentative_disposition"]=="GOVERNANCE_CONDITION"
assert set(x["target_capability"] for x in report["target_drafts"])==set(targets)
assert all(x["semantic_coverage_verified"] is False for x in report["target_drafts"])

def rejects(fn,part):
    try:fn()
    except DiscoveryError as ex:
        assert part in str(ex),str(ex)
    else:raise AssertionError("Expected rejection: "+part)

bad=copy.deepcopy(config)
bad["sections"][0]["claims"].pop()
rejects(lambda:build_strategy_claim_review(worksheet,draft,bad),"not every selected")
bad=copy.deepcopy(config)
bad["sections"][0]["claims"].append(copy.deepcopy(bad["sections"][0]["claims"][0]))
rejects(lambda:build_strategy_claim_review(worksheet,draft,bad),"unknown or duplicate")
bad=copy.deepcopy(config)
bad["sections"][0]["claims"][0]["expected_source_text"]="Falsified accepted wording"
rejects(lambda:build_strategy_claim_review(worksheet,draft,bad),"source wording differs")
bad=copy.deepcopy(config)
bad["sections"][0]["claims"][0]["disposition"]="ACCEPTED"
rejects(lambda:build_strategy_claim_review(worksheet,draft,bad),"invalid tentative")
bad=copy.deepcopy(config)
bad["sections"][0]["claims"][0]["candidate_target_links"][0]["obligation_id"]="FAKE-OBLIGATION"
rejects(lambda:build_strategy_claim_review(worksheet,draft,bad),"unknown or duplicate draft")
bad=copy.deepcopy(config)
bad["sections"][0]["claims"][1]["candidate_target_links"]=[
    {"target_capability":list(targets)[0],
     "obligation_id":"PI-SEMANTIC-CONCEPTS",
     "relation":"CANDIDATE_SEMANTIC_CONSTRAINT"}
]
rejects(lambda:build_strategy_claim_review(worksheet,draft,bad),"non-target semantic")
bad=copy.deepcopy(config)
bad["source_commit"]="0"*40
rejects(lambda:build_strategy_claim_review(worksheet,draft,bad),"share pinned")
bad=copy.deepcopy(config)
bad["sections"][0]["claims"][0]["review_reason"]="ok"
rejects(lambda:build_strategy_claim_review(worksheet,draft,bad),"rationale missing")
bad=copy.deepcopy(worksheet)
bad["source_units"][0]["review_state"]="ACCEPTED"
rejects(lambda:build_strategy_claim_review(bad,draft,config),"prematurely classified")
bad=copy.deepcopy(draft)
bad["target_contracts"][0]["candidate_obligations"][0]["status"]="ACCEPTED"
rejects(lambda:build_strategy_claim_review(worksheet,bad,config),"unaccepted candidates")
print("dependency resolution strategy claim review: PASS")
