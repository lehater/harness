#!/usr/bin/env python3
"""Claim-level draft mapping is exhaustive for product claims, never accepted."""
from __future__ import annotations

import copy
from pathlib import Path
import sys
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from evals.project_discovery_snapshot import DiscoveryError
from evals.project_target_claim_mapping import build_claim_mapping

SHA = "a" * 40
P = "x.preparation-model"
H = "x.history-model"
source = ".harness/knowledge/product-capabilities.yaml"
units = [
    {"source_unit_id": "1"*20, "source_path": source, "source_sha256": "b"*64,
     "source_provider": "x.product", "source_local_id": "REQ-1",
     "source_unit_kind": "ACCEPTED_PRODUCT_REQUIREMENT",
     "source_text": "Use distinguishable meanings and relationships.",
     "review_state": "UNREVIEWED", "semantic_route": "UNDETERMINED",
     "semantic_effect": "UNDETERMINED",
     "seen_by_target_capabilities": [P,H],
     "candidate_draft_obligation_ids_by_target": {P:[],H:[]},
     "target_output_obligation_mapping_verified": False,
     "automatic_writeback_allowed": False},
    {"source_unit_id": "2"*20, "source_path": source, "source_sha256": "b"*64,
     "source_provider": "x.product", "source_local_id": "NON_GOAL-01",
     "source_unit_kind": "PRODUCT_NON_GOAL",
     "source_text": "Do not infer mastery from retained information.",
     "review_state": "UNREVIEWED", "semantic_route": "UNDETERMINED",
     "semantic_effect": "UNDETERMINED",
     "seen_by_target_capabilities": [P,H],
     "candidate_draft_obligation_ids_by_target": {P:[],H:[]},
     "target_output_obligation_mapping_verified": False,
     "automatic_writeback_allowed": False},
    {"source_unit_id": "3"*20, "source_path": "docs/strategy.md",
     "source_sha256": "c"*64, "source_provider": "x.strategy",
     "source_local_id": "0", "source_unit_kind": "ACCEPTED_SOURCE_SECTION_STATEMENT",
     "source_text": "Keep historical reference meanings independent.",
     "review_state": "UNREVIEWED", "semantic_route": "UNDETERMINED",
     "semantic_effect": "UNDETERMINED",
     "seen_by_target_capabilities": [P,H],
     "candidate_draft_obligation_ids_by_target": {P:["PI-01"], H:["RH-01"]},
     "target_output_obligation_mapping_verified": False,
     "automatic_writeback_allowed": False},
]
worksheet = {
    "kind":"harness-cdr-source-responsibility-worksheet",
    "status":"PENDING_INDEPENDENT_RESPONSIBILITY_REVIEW",
    "source_snapshot":SHA, "source_targets":[P,H],
    "source_units":units, "distinct_source_unit_count":len(units),
    "independent_responsibility_adjudication_performed":False,
    "accepted_target_contract_established":False, "automatic_writeback_allowed":False,
}
draft = {
    "kind":"harness-cdr-target-output-contract-candidates",
    "status":"OPERATOR_DRAFT_NOT_ACCEPTED", "source_commit":SHA,
    "no_automatic_writeback":True,
    "target_contracts":[
        {"target_capability":P, "target_contract_status":"NEEDS_INDEPENDENT_AUTHORITY_REVIEW",
         "candidate_obligations":[{"id":"PI-01","status":"CANDIDATE_NOT_ACCEPTED"}]},
        {"target_capability":H, "target_contract_status":"NEEDS_INDEPENDENT_AUTHORITY_REVIEW",
         "candidate_obligations":[{"id":"RH-01","status":"CANDIDATE_NOT_ACCEPTED"}]},
    ],
}
hypotheses = {
    "kind":"harness-cdr-claim-obligation-mapping-hypotheses",
    "status":"OPERATOR_DRAFT_NOT_ACCEPTED", "source_commit":SHA,
    "automatic_writeback_allowed":False,
    "source_claims":[
        {"source_path":source,"source_local_id":"REQ-1",
         "source_unit_kind":"ACCEPTED_PRODUCT_REQUIREMENT",
         "status":"CANDIDATE_NOT_ACCEPTED",
         "candidate_target_links":[
             {"target_capability":P,"obligation_id":"PI-01",
              "relation":"CANDIDATE_SEMANTIC_CONSTRAINT"}],
         "candidate_external_routes":["APPLICATION_DESIGN"],
         "rationale":"Accepted product rule may constrain meaning but is not a domain-only behavior."},
        {"source_path":source,"source_local_id":"NON_GOAL-01",
         "source_unit_kind":"PRODUCT_NON_GOAL","status":"CANDIDATE_NOT_ACCEPTED",
         "candidate_target_links":[
             {"target_capability":H,"obligation_id":"RH-01",
              "relation":"CANDIDATE_NEGATIVE_INVARIANT"}],
         "candidate_external_routes":[],
         "rationale":"The negative rule may constrain the interpretation of historical recorded facts."},
    ],
}
result=build_claim_mapping(worksheet,draft,proposals=hypotheses)
assert result["status"]=="PENDING_INDEPENDENT_CLAIM_TO_OBLIGATION_REVIEW"
assert result["source_claim_count"]==3
assert result["product_claims_in_scope"]==2
assert result["operator_classified_product_claim_count"]==2
assert result["other_source_units_unclassified"]==1
assert result["automatic_writeback_allowed"] is False
assert result["authority_review_performed"] is False
assert result["target_obligations_independently_accepted"] is False
mapped={x["source_local_id"]:x for x in result["source_claims"]}
assert mapped["REQ-1"]["proposed_links"][0]["obligation_id"]=="PI-01"
assert mapped["NON_GOAL-01"]["proposed_links"][0]["relation"]=="CANDIDATE_NEGATIVE_INVARIANT"
assert mapped["0"]["classification_state"]=="UNCLASSIFIED_REQUIRES_REVIEW"
assert mapped["0"]["source_section_draft_obligation_hints"]=={P:["PI-01"],H:["RH-01"]}
assert all(not x["direct_provider_necessity_established"] for x in mapped.values())
assert result["target_draft_coverage"][0]["semantic_coverage_verified"] is False
assert result["target_draft_coverage"][1]["semantic_coverage_verified"] is False
unproposed=build_claim_mapping(worksheet,draft)
assert unproposed["operator_classified_product_claim_count"]==0
assert unproposed["other_source_units_unclassified"]==3

def must_fail(callback,expected):
    try:callback()
    except DiscoveryError as e:
        assert expected in str(e),str(e)
    else:raise AssertionError("Expected failure "+expected)

def wrong(change,err):
    obj=copy.deepcopy(hypotheses)
    change(obj)
    must_fail(lambda:build_claim_mapping(worksheet,draft,proposals=obj),err)

wrong(lambda d:d["source_claims"].pop(),"every accepted product")
wrong(lambda d:d["source_claims"].append(copy.deepcopy(d["source_claims"][0])),"duplicate product")
wrong(lambda d:d["source_claims"][0].update(source_local_id="REQ-FAKE"),"unknown or duplicate")
wrong(lambda d:d["source_claims"][0].update(status="ACCEPTED"),"cannot declare acceptance")
wrong(lambda d:d["source_claims"][0].update(source_sha256="0"*64),"digest differs")
wrong(lambda d:d["source_claims"][0]["candidate_target_links"][0].update(
    obligation_id="MISSING"),"unknown, invalid")
wrong(lambda d:d["source_claims"][0]["candidate_target_links"].append(
    copy.deepcopy(d["source_claims"][0]["candidate_target_links"][0])),"unknown, invalid")
wrong(lambda d:d["source_claims"][0].update(
    candidate_target_links=[],candidate_external_routes=[]),"explicit external")
wrong(lambda d:d.update(source_commit="0"*40),"must be pinned")

bad_draft=copy.deepcopy(draft)
bad_draft["target_contracts"][0]["candidate_obligations"][0]["status"]="ACCEPTED"
must_fail(lambda:build_claim_mapping(worksheet,bad_draft,proposals=hypotheses),"not unaccepted")
bad_worksheet=copy.deepcopy(worksheet)
bad_worksheet["source_units"][0]["review_state"]="REVIEWED"
must_fail(lambda:build_claim_mapping(bad_worksheet,draft,proposals=hypotheses),"prematurely adjudicated")
bad_worksheet=copy.deepcopy(worksheet)
bad_worksheet["source_units"].append(copy.deepcopy(units[0]))
bad_worksheet["distinct_source_unit_count"]+=1
must_fail(lambda:build_claim_mapping(bad_worksheet,draft,proposals=hypotheses),"duplicate source unit")

# Check all actual PREP hypotheses IDs and non-goals in the experimental
# source file. The exact pinned PREP checkout is separately verified by the
# integration workflow; this fixture does not claim expert semantic truth.
actual=yaml.safe_load((ROOT/"spec/dependency-resolution/project-pilots/"
    "prep-claim-obligation-hypotheses-v1.yaml").read_text(encoding="utf-8"))
ids={c["source_local_id"] for c in actual["source_claims"]}
assert len(actual["source_claims"])==21
assert len(ids)==21
assert sum(x["source_unit_kind"]=="PRODUCT_NON_GOAL" for x in actual["source_claims"])==6
assert actual["status"]=="OPERATOR_DRAFT_NOT_ACCEPTED"
assert actual["automatic_writeback_allowed"] is False
assert actual["source_commit"]=="c52ff8ec1a4732285b2b299bf11dca9869fb2fee"
print("dependency resolution per-claim obligation mapping: PASS")
