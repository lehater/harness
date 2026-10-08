#!/usr/bin/env python3
"""Target output rewrite preserves every old claim without self-acceptance."""
from __future__ import annotations

import copy
from pathlib import Path
import sys
import yaml

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))

from evals.project_discovery_snapshot import DiscoveryError
from evals.project_target_obligation_revision import validate_revision

P=ROOT/"spec/dependency-resolution/project-pilots"
original=yaml.safe_load((P/"prep-target-output-candidates-v1.yaml").read_text(encoding="utf-8"))
revision=yaml.safe_load((P/"prep-target-obligation-revision-v2.yaml").read_text(encoding="utf-8"))

record=validate_revision(original,revision)
assert record["status"]=="REVISION_PROPOSAL_REQUIRES_AUTHORITY_REVIEW"
assert record["original_obligation_count"]==8
assert record["candidate_output_count"]==6
assert record["candidate_constraint_count"]==2
assert record["automatic_writeback_allowed"] is False
assert record["graph_mutation_authorized"] is False
assert record["independent_authority_review_performed"] is False
assert record["semantic_completeness_established"] is False
assert record["source_snapshot"]=="c52ff8ec1a4732285b2b299bf11dca9869fb2fee"
assert len(record["targets"])==2
expected={
    "prep.preparation-information-model":("PI-NEGATIVE-INVARIANTS",),
    "prep.recorded-activity-history-model":("RH-NEGATIVE-INVARIANTS",),
}
for row in record["targets"]:
    assert tuple(row["governing_constraint_ids"])==expected[row["target_capability"]]
    assert len(row["preserved_v1_obligation_ids"])==4
    assert len(row["candidate_output_ids"])==3
    assert row["action_counts"]=={"REFINE_OUTPUT":3,"RECAST_AS_GOVERNING_CONSTRAINT":1}
    assert row["target_contract_accepted"] is False

def fail(new,phrase):
    try:validate_revision(original,new)
    except DiscoveryError as e:
        assert phrase in str(e),str(e)
    else:raise AssertionError("Missing failure "+phrase)

x=copy.deepcopy(revision)
x["targets"][0]["candidate_outputs"].pop()
fail(x,"silently drops")
x=copy.deepcopy(revision)
x["targets"][0]["candidate_constraints"].clear()
fail(x,"silently drops")
x=copy.deepcopy(revision)
x["targets"][0]["candidate_outputs"][0]["supersedes_v1"]="RH-RECORDED-FACTS"
fail(x,"lineage")
x=copy.deepcopy(revision)
x["targets"][0]["candidate_outputs"][0]["id"]="PI-RENAMED"
fail(x,"stable obligation identifiers")
x=copy.deepcopy(revision)
x["targets"][0]["candidate_outputs"][0]["status"]="ACCEPTED"
fail(x,"proposed action or status")
x=copy.deepcopy(revision)
x["targets"][0]["candidate_outputs"][0]["source_sections"].clear()
fail(x,"revised source provenance")
x=copy.deepcopy(revision)
x["targets"][0]["candidate_outputs"][1]["source_sections"].pop()
fail(x,"discards v1 source")
x=copy.deepcopy(revision)
x["targets"][0]["candidate_constraints"][0]["applies_to_outputs"]=["RH-RECORDED-FACTS"]
fail(x,"recast cross-cutting constraint")
x=copy.deepcopy(revision)
x["targets"][0]["candidate_constraints"][0]["applies_to_outputs"].pop()
fail(x,"recast cross-cutting constraint")
x=copy.deepcopy(revision)
x["targets"][0]["candidate_constraints"][0]["proposal"]="REFINE_OUTPUT"
fail(x,"proposed action or status")
x=copy.deepcopy(revision)
x["independent_review_performed"]=True
fail(x,"cannot assert Authority acceptance")
x=copy.deepcopy(revision)
x["targets"][0]["candidate_outputs"][0]["requires"]=["prep.domain-strategy"]
fail(x,"cannot contain graph dependency edits")
x=copy.deepcopy(revision)
x["source_commit"]="0"*40
fail(x,"must preserve project source")
x=copy.deepcopy(revision)
x["targets"].pop()
fail(x,"omits an entire")
x=copy.deepcopy(revision)
x["targets"][0]["candidate_outputs"][0]["text"]=original["target_contracts"][0]["candidate_obligations"][0]["description"]
fail(x,"revised formulation")
print("dependency resolution tactical obligation revision: PASS")
print("v1 claims: 8 -> proposed outputs: 6 + governing constraints: 2; no acceptance")
