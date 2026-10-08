#!/usr/bin/env python3
"""CDR creation-intake and independent whole-graph auditor, pinned and read-only."""
from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from evals.cdr_operational import prepare_intake, reconcile_intake
from evals.cdr_graph_audit import audit_graph
from evals.cdr_governance_packet import build_decision_dossier, validate_draft_review, digest
from evals.project_discovery_directness_review import REQUIRED_TESTS
from evals.dependency_resolution_process_driver import build_blinded_request
from evals.project_discovery_snapshot import DiscoveryError


def git(root:Path,*args:str)->str:
    return subprocess.check_output(
        ["git","-C",str(root),*args],text=True,stderr=subprocess.DEVNULL
    ).strip()


def save(root:Path,path:str,content)->None:
    p=root/path
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(content if isinstance(content,str) else yaml.safe_dump(
        content,sort_keys=False),encoding="utf-8")


with tempfile.TemporaryDirectory(prefix="harness-cdr-mvp-") as tmp:
    root=Path(tmp)
    git(root,"init")
    git(root,"config","user.email","test@example.invalid")
    git(root,"config","user.name","CDR Integration Test")
    graph={
        "authorities":[
            {"id":"PRODUCT","produces":[
                {"capability":"x.product","knowledge_kind":"requirements","requires":[]}]},
            {"id":"STRATEGY","produces":[
                {"capability":"x.strategy","knowledge_kind":"domain-strategy",
                 "requires":[{"capability":"x.product"}]}]},
            {"id":"MODEL","produces":[
                {"capability":"x.model","knowledge_kind":"model-context",
                 "requires":[{"capability":"x.strategy"},{"capability":"x.product"}]}]},
        ],
    }
    save(root,".harness/engineering-graph.yaml",graph)
    save(root,".harness/core.yaml",{
        "questions":[],
        "artifacts":[
            {"id":"P","authority":"PRODUCT","path":"docs/product.yaml",
             "provides":["x.product"],"depends_on":[]},
            {"id":"S","authority":"STRATEGY","path":"docs/strategy.md",
             "provides":["x.strategy"],"depends_on":["P"]},
            {"id":"M","authority":"MODEL","path":"docs/model.md",
             "provides":["x.model"],"depends_on":["S"]},
        ],
    })
    save(root,".harness/semantic-baseline.yaml",{"reviews":[
        {"capability":"x.product","revision":1},
        {"capability":"x.strategy","revision":2},
        {"capability":"x.model","revision":3},
    ]})
    save(root,"docs/product.yaml",{"content":{"requirements":[
        {"id":"REQ-1","statement":"Preserve meaning of accepted user information.",
         "status":"ACCEPTED"},
        {"id":"REQ-2","statement":"Draft administrative feature.",
         "status":"DRAFT"},
    ]}})
    save(root,"docs/strategy.md",
         "# Accepted Strategy\n\n## Definition\n\n"
         "The accepted domain strategy governs meaningful account information.\n"
         "No conclusion about learner mastery follows from possessing information.\n")
    save(root,"docs/model.md",
         "# Accepted Model Context\n\n## Concepts\n\n"
         "The model distinguishes current accounts and historical records.\n"
         "Relationships preserve source context across later changes.\n")
    git(root,"add",".")
    git(root,"commit","-m","source scope")
    sha=git(root,"rev-parse","HEAD")
    intake={
        "kind":"harness-cdr-capability-intake-v1","version":1,
        "status":"DRAFT_NOT_ACCEPTED","source_commit":sha,
        "automatic_writeback_allowed":False,
        "target":{
            "capability":"x.new-target",
            "authority":"TACTICAL",
            "knowledge_kind":"domain-model",
            "output_obligations":[
                {"id":"CURRENT","description":
                 "Define current information and its semantic distinctions, including what its presence does not mean."},
                {"id":"HISTORY","description":
                 "Define historical recorded facts with preserved meaning through later changes to their referents."},
            ],
            "governing_constraints":[{
                "id":"NO_INFERENCES",
                "description":"Historical activity and current information shall not establish learner mastery.",
                "applies_to_outputs":["CURRENT","HISTORY"],
            }],
        },
    }
    prepared=prepare_intake(root,sha=sha,intake=intake)
    assert prepared["status"]=="OPERATIONAL_DRAFT_INTAKE_REVIEW_ONLY"
    assert prepared["automatic_writeback_allowed"] is False
    case=prepared["cases"][0]
    assert case["target"]["capability"]=="x.new-target"
    assert len(case["provider_catalog"])==3
    assert all(x["evidence_status"]=="ACCEPTED_EVIDENCE" for x in case["provider_catalog"])
    assert not any("REQ-2" in x for v in case["provider_catalog"]
                   for x in v["semantic_surface"])
    assert "requires" not in repr(case["target"])
    request=build_blinded_request(prepared,run_id="test-cdr-operational",
                                 adapter_binding={"id":"fake-isolated"})
    assert "requires" not in repr(request["cases"][0]["target"])
    catalog={p["capability"]:p for p in case["provider_catalog"]}
    pi=next(i for i,s in enumerate(catalog["x.product"]["semantic_surface"])
            if s.startswith("REQ-1:"))
    mi=0
    prediction={
        "version":1,"kind":"harness-dependency-resolution-predictions",
        "cases":[{
            "id":"INTAKE-01","status":"RESOLVED",
            "proposed_requires":["x.model","x.product"],
            "input_needs":[
                {"obligation":"CURRENT","provider":"x.product",
                 "claim_index":pi,"basis":"DIRECT_ACCEPTED",
                 "consumption_rationale":"Accepted product semantics constrain the current information output."},
                {"obligation":"HISTORY","provider":"x.model",
                 "claim_index":mi,"basis":"DIRECT_ACCEPTED",
                 "consumption_rationale":"The accepted public model contract distinguishes history and current meaning."},
            ],
            "unresolved_obligations":[],
        }],
    }
    result=reconcile_intake(root,sha=sha,intake=intake,predictions=prediction)
    assert result["status"]=="REVIEW_REQUIRED"
    assert result["target_graph_presence"]=="NOT_YET_DECLARED"
    assert result["KEEP"]==[]
    assert result["ADD"]==["x.model","x.product"]
    assert result["REMOVE_CANDIDATE"]==[]
    assert len(result["directness_audit"])==2
    assert len(result["directness_review_packets"])==2
    assert all(not x["automatic_writeback_allowed"] for x in result["directness_review_packets"])
    assert result["source_reference_assessment"]["status"]!="INVALID"
    assert result["target_contract_independently_accepted"] is False
    assert result["automatic_writeback_allowed"] is False
    assert result["semantic_entailment_verified"] is False

    dossier=build_decision_dossier(root,sha=sha,intake=intake,predictions=prediction)
    assert dossier["status"]=="REVIEW_DOSSIER_NOT_AUTHORIZATION"
    assert dossier["target_capability"]=="x.new-target"
    assert len(dossier["target_output_obligations"])==2
    assert len(dossier["proposed_ADD"])==2
    assert dossier["authority_approval_verified"] is False
    assert dossier["independent_target_acceptance_proven"] is False
    assert "TARGET_PRODUCTION_MISSING_OR_AMBIGUOUS" in dossier["readiness_blockers"]
    assert "INDEPENDENT_TARGET_OBLIGATION_ADJUDICATION_NOT_PROVEN" in dossier["readiness_blockers"]
    assert all(len(p["required_directness_tests"])==5 for p in dossier["proposed_ADD"])
    review_draft={
        "kind":"harness-cdr-independent-review-draft",
        "status":"PROPOSED_NOT_ACCEPTED",
        "dossier_sha256":dossier["dossier_sha256"],
        "source_snapshot":sha,"target_capability":"x.new-target",
        "automatic_writeback_allowed":False,
        "output_findings":[{
            "obligation_id":ob["id"],
            "decision":"REVIEW_NEEDED",
            "reason":"Accepted source evidence does not independently establish this target draft's semantic completeness.",
        } for ob in dossier["target_output_obligations"]],
        "directness_findings":[{
            "provider":packet["provider"],"decision":"UNDETERMINED",
            "tests":[{
                "test":test,"finding":"INCONCLUSIVE",
                "evidence":"The intermediate contract and the source-specific target consumption have not been independently reviewed.",
            } for test in REQUIRED_TESTS],
        } for packet in dossier["proposed_ADD"]],
    }
    validation=validate_draft_review(dossier,review_draft)
    assert validation["status"]=="DRAFT_COMPLETE_FOR_AUTHORITY_CONSIDERATION"
    assert validation["governance_transition_authorized"] is False
    assert validation["target_contract_independently_accepted"] is False
    assert validation["automatic_writeback_allowed"] is False
    bad_review=copy.deepcopy(review_draft)
    bad_review["directness_findings"][0]["decision"]="DIRECT_REQUIRED"
    try:validate_draft_review(dossier,bad_review)
    except DiscoveryError:pass
    else:raise AssertionError("operator draft must not self-approve")
    bad_review=copy.deepcopy(review_draft)
    bad_review["directness_findings"][0]["decision"]="LIKELY_DIRECT"
    try:validate_draft_review(dossier,bad_review)
    except DiscoveryError as e:
        assert "conflicts with review findings" in str(e)
    else:raise AssertionError("inconclusive evidence must not support likely-direct decision")
    bad_review=copy.deepcopy(review_draft)
    bad_review["output_findings"].pop()
    try:validate_draft_review(dossier,bad_review)
    except DiscoveryError:pass
    else:raise AssertionError("operator draft must cover all outputs")
    bad_dossier=copy.deepcopy(dossier)
    bad_dossier["proposed_ADD"][0]["provider"]="forged.upstream"
    try:validate_draft_review(bad_dossier,review_draft)
    except DiscoveryError:pass
    else:raise AssertionError("governance dossier digest must bind immutable proposals")

    # Exercise Harness operator-facing make commands, not just Python API.
    save(root,"cdr-intake.yaml",intake)
    save(root,"cdr-prediction.json",json.dumps(prediction))
    common=[
        "make","-s","-C",str(ROOT),
        "PROJECT_ROOT="+str(root),
        "PROJECT_COMMIT="+sha,
        "CDR_INTAKE="+str(root/"cdr-intake.yaml"),
    ]
    generated=root/"operational-input.json"
    subprocess.run(common+["cdr-prepare","CDR_OUTPUT="+str(generated)],
                   check=True,capture_output=True,text=True)
    assert json.loads(generated.read_text(encoding="utf-8"))==prepared
    projected=root/"operational-reconciliation.json"
    subprocess.run(
        common+["cdr-reconcile",
                "CDR_PREDICTIONS="+str(root/"cdr-prediction.json"),
                "CDR_OUTPUT="+str(projected)],
        check=True,capture_output=True,text=True,
    )
    assert json.loads(projected.read_text(encoding="utf-8"))==result
    dossier_path=root/"cdr-decision-dossier.json"
    subprocess.run(
        common+["cdr-dossier",
                "CDR_PREDICTIONS="+str(root/"cdr-prediction.json"),
                "CDR_OUTPUT="+str(dossier_path)],
        check=True,capture_output=True,text=True,
    )
    assert json.loads(dossier_path.read_text(encoding="utf-8"))==dossier
    review_path=root/"cdr-review-draft.yaml"
    save(root,"cdr-review-draft.yaml",review_draft)
    check=root/"cdr-draft-check.json"
    subprocess.run(
        common+["cdr-check-review",
                "CDR_PREDICTIONS="+str(root/"cdr-prediction.json"),
                "CDR_DOSSIER="+str(dossier_path),
                "CDR_REVIEW="+str(review_path),
                "CDR_OUTPUT="+str(check)],
        check=True,capture_output=True,text=True,
    )
    assert json.loads(check.read_text(encoding="utf-8"))==validation
    # A self-consistent JSON hash is not authentication: the reviewer check
    # must independently regenerate pinned project evidence.
    forged=copy.deepcopy(dossier)
    forged["proposed_ADD"][0]["provider"]="fake.accepted.provider"
    forged["dossier_sha256"]=digest({
        key:value for key,value in forged.items() if key!="dossier_sha256"
    })
    dossier_path.write_text(json.dumps(forged),encoding="utf-8")
    failed=subprocess.run(
        common+["cdr-check-review",
                "CDR_PREDICTIONS="+str(root/"cdr-prediction.json"),
                "CDR_DOSSIER="+str(dossier_path),
                "CDR_REVIEW="+str(review_path),
                "CDR_OUTPUT="+str(check)],
        capture_output=True,text=True,check=False,
    )
    assert failed.returncode!=0
    assert "differs from freshly regenerated pinned source evidence" in failed.stdout
    dossier_path.write_text(json.dumps(dossier),encoding="utf-8")
    assert git(root,"status","--porcelain","--untracked-files=no")==""


    def fails(call,part):
        try:call()
        except DiscoveryError as e: assert part in str(e),str(e)
        else:raise AssertionError("Expected "+part)
    bad=copy.deepcopy(prediction)
    bad["cases"][0]["input_needs"].pop()
    bad["cases"][0]["proposed_requires"]=["x.product"]
    fails(lambda:reconcile_intake(root,sha=sha,intake=intake,predictions=bad),
          "silently skipped")
    bad=copy.deepcopy(prediction)
    bad["cases"][0]["input_needs"][0]["provider"]="not-accepted"
    fails(lambda:reconcile_intake(root,sha=sha,intake=intake,predictions=bad),
          "source reference checks")
    bad=copy.deepcopy(intake)
    bad["status"]="ACCEPTED"
    fails(lambda:prepare_intake(root,sha=sha,intake=bad),"invalid, unpinned")
    bad=copy.deepcopy(intake)
    bad["target"]["output_obligations"][0]["description"] = catalog["x.model"]["semantic_surface"][0]
    fails(lambda:prepare_intake(root,sha=sha,intake=bad),"copies or names")
    bad=copy.deepcopy(intake)
    bad["target"]["governing_constraints"][0]["applies_to_outputs"]=["FORGED"]
    fails(lambda:prepare_intake(root,sha=sha,intake=bad),"dangling")
    fails(lambda:prepare_intake(root,sha="0"*40,intake=intake),"project commit mismatch")
    audit=audit_graph(root,sha=sha)
    saved_audit=root/"operational-graph-audit.json"
    subprocess.run([
        "make","-s","-C",str(ROOT),"cdr-audit",
        "PROJECT_ROOT="+str(root),"PROJECT_COMMIT="+sha,
        "CDR_OUTPUT="+str(saved_audit),
    ],check=True,capture_output=True,text=True)
    assert json.loads(saved_audit.read_text(encoding="utf-8"))==audit
    assert audit["status"]=="STRUCTURAL_REVIEW_ONLY"
    assert audit["capability_count"]==3
    assert audit["direct_edge_count"]==3
    assert audit["unknown_provider_edges"]==[]
    assert audit["self_dependencies"]==[]
    assert audit["cycles"]==[]
    assert len(audit["structural_transitive_edge_flags"])==1
    flag=audit["structural_transitive_edge_flags"][0]
    assert flag["target_capability"]=="x.model"
    assert flag["direct_provider"]=="x.product"
    assert flag["alternative_structural_paths"]==[
        ["x.model","x.strategy","x.product"]
    ]
    assert flag["semantic_redundancy_proven"] is False
    assert flag["remove_candidate_allowed"] is False
    impact=next(x for x in audit["change_impact"] if x["changed_provider"]=="x.product")
    assert impact["direct_consumers"]==["x.model","x.strategy"]
    assert audit["REMOVE_CANDIDATE"]==[]
    assert audit["automatic_writeback_allowed"] is False

    graph["authorities"][0]["produces"][0]["requires"]=[
        {"capability":"x.model"},{"capability":"unknown.provider"}
    ]
    save(root,".harness/engineering-graph.yaml",graph)
    git(root,"add",".")
    git(root,"commit","-m","introduce structural faults")
    badsha=git(root,"rev-parse","HEAD")
    invalid=audit_graph(root,sha=badsha)
    assert invalid["status"]=="INVALID_STRUCTURE_REQUIRES_REVIEW"
    assert invalid["unknown_provider_edges"]==[
        {"consumer":"x.product","provider":"unknown.provider"}
    ]
    assert invalid["cycles"]
    assert invalid["automatic_writeback_allowed"] is False
    (root/"docs/model.md").write_text("dirty tracked change",encoding="utf-8")
    try:audit_graph(root,sha=badsha)
    except DiscoveryError:pass
    else:raise AssertionError("dirty graph audit should fail")

print("CDR operational create/reconcile + on-demand graph audit: PASS")
