#!/usr/bin/env python3
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from semantic_acceptance import evaluate_artifact
from coverage_planner import capability_realization


def codes(result):
    return {item["code"] for item in result["findings"]}


def test_real_defect_regressions():
    # NAPMS: stale Resource UI semantics vs current domain truth.
    contract = {
        "authority": "INTERFACE-DESIGN",
        "owned_assertion_kinds": ["ui-fact"],
        "obligations": [{"id": "scope", "kind": "ui-fact", "subject": "Resource.scope"}],
        "semantic_claims": ["engineering.interface.human.journeys"],
    }
    sources = {"semantic_assertions": [
        {"id": "RC-SCOPE", "kind": "ui-fact", "subject": "Resource.scope",
         "semantic_value": "immutable AuthorityScopeRef"}
    ]}
    candidate = {"id": "RESOURCE-DETAIL-UI", "capability": "engineering.frontend.human-interface",
                 "semantic_assertions": [
        {"id": "UI-SCOPE", "kind": "ui-fact", "subject": "Resource.scope",
         "semantic_value": "temporal Responsibility Scope affiliations",
         "derived_from": ["RC-SCOPE"]}
    ]}
    r=evaluate_artifact(contract,sources,candidate)
    assert r["status"]=="REJECTED" and "SOURCE_FIDELITY_VIOLATION" in codes(r)

    # NAPMS: HTTP interface misses required Resource curation operations.
    required=["registerResource","addEndpoint","setEndpointAddress","clearEndpointAddress",
              "setSite","setResponsibility","getResourceHistory"]
    contract={"authority":"INTERFACE-DESIGN","owned_assertion_kinds":["operation"],
              "obligations":[{"id":"resource-ops","kind":"operation","subjects":required}],
              "semantic_claims":["engineering.interface.machine.contract"]}
    candidate={"id":"OPENAPI","capability":"engineering.interface.http-contract",
               "semantic_assertions":[
                   {"id":x,"kind":"operation","subject":x,"decision_authority":"INTERFACE-DESIGN"}
                   for x in ["registerResource","addEndpoint","setEndpointAddress"]
               ]}
    r=evaluate_artifact(contract,{"semantic_assertions":[]},candidate)
    assert r["status"]=="REJECTED" and "MISSING_SUBJECTS" in codes(r)

    # NAPMS: UI-required server interaction is absent from OpenAPI.
    contract={"authority":"INTERFACE-DESIGN","owned_assertion_kinds":["ui-operation"],
              "obligations":[{"id":"detail","kind":"ui-operation","subject":"getResourceDetail"}],
              "compatibility_obligations":[{"id":"ui-http","left_kind":"ui-operation","right_kind":"http-operation"}]}
    sources={"semantic_assertions":[
        {"id":"HTTP-GET","kind":"http-operation","subject":"getResource"}
    ]}
    candidate={"id":"RESOURCE-DETAIL-UI","capability":"engineering.frontend.human-interface",
               "semantic_assertions":[
        {"id":"UI-GET","kind":"ui-operation","subject":"getResourceDetail","decision_authority":"INTERFACE-DESIGN"}
    ]}
    r=evaluate_artifact(contract,sources,candidate)
    assert r["status"]=="REJECTED" and "INCOMPATIBLE_CONSUMER_CONTRACT" in codes(r)

    # NAPMS: required 413 is absent.
    contract={"authority":"INTERFACE-DESIGN","owned_assertion_kinds":["error"],
              "obligations":[{"id":"errors","kind":"error","subject":"http",
                              "required_values":["401","403","409","413","422","503"]}]}
    candidate={"id":"OPENAPI","capability":"engineering.interface.http-contract",
               "semantic_assertions":[
        {"id":f"E-{v}","kind":"error","subject":"http","semantic_value":v,
         "decision_authority":"INTERFACE-DESIGN"}
        for v in ["401","403","409","422","503"]
    ]}
    r=evaluate_artifact(contract,{"semantic_assertions":[]},candidate)
    assert r["status"]=="REJECTED" and "MISSING_VALUES" in codes(r)

    # Nutrition: Data Design imports Implementation-owned concrete stack semantics.
    contract={"authority":"DATA-DESIGN","owned_assertion_kinds":["data-model"]}
    sources={"semantic_assertions":[
        {"id":"STACK-SQLITE","kind":"implementation-stack","subject":"database",
         "semantic_value":"SQLite WAL synchronous=FULL"}
    ]}
    candidate={"id":"DATA-DESIGN","capability":"nutrition-management.data-design",
               "semantic_assertions":[
        {"id":"DATA-SQLITE","kind":"implementation-stack","subject":"database",
         "semantic_value":"SQLite WAL synchronous=FULL","derived_from":["STACK-SQLITE"]}
    ]}
    r=evaluate_artifact(contract,sources,candidate)
    assert r["status"]=="REJECTED" and "WRONG_AUTHORITY_OWNERSHIP" in codes(r)

    # Nutrition: Add Member requires an explicit member-identity operation.
    contract={"authority":"APPLICATION-DESIGN","owned_assertion_kinds":["operation"],
              "obligations":[{"id":"member-actions","kind":"operation",
                              "subjects":["createMember","saveMemberProfile"]}]}
    candidate={"id":"FRONTEND-APPLICATION-CONTRACTS",
               "capability":"nutrition-management.frontend.application-contracts",
               "semantic_assertions":[
        {"id":"SAVE","kind":"operation","subject":"saveMemberProfile",
         "decision_authority":"APPLICATION-DESIGN"}
    ]}
    r=evaluate_artifact(contract,{"semantic_assertions":[]},candidate)
    assert r["status"]=="REJECTED" and "MISSING_SUBJECTS" in codes(r)

    # Nutrition: pilot-only self-status contradicts main canonical registration.
    contract={"authority":"PURCHASE-PLANNING","owned_assertion_kinds":["lifecycle"],
              "obligations":[{"id":"status","kind":"lifecycle","subject":"canonical-status"}]}
    sources={"semantic_assertions":[
        {"id":"REG","kind":"lifecycle","subject":"canonical-status","semantic_value":"current-main"}
    ]}
    candidate={"id":"GAP-SUGGESTION-RANKING-DECISION",
               "capability":"nutrition-management.purchase-planning.gap-suggestion-ranking",
               "semantic_assertions":[
        {"id":"SELF","kind":"lifecycle","subject":"canonical-status",
         "semantic_value":"accepted-for-pilot-branch","derived_from":["REG"]}
    ]}
    r=evaluate_artifact(contract,sources,candidate)
    assert r["status"]=="REJECTED" and "SOURCE_FIDELITY_VIOLATION" in codes(r)


def test_coverage_gating_and_invalidation():
    graph={
        "kind":"harness-engineering-graph",
        "authorities":[
            {"id":"INTERFACE","produces":[
                {"capability":"project.http","requires":[],"semantic_claims":["engineering.interface.machine.contract"]}
            ]},
            {"id":"FRONTEND","produces":[
                {"capability":"project.frontend","requires":[{"capability":"project.http"}],
                 "semantic_claims":["engineering.frontend.architecture"]}
            ]},
        ],
        "consumers":[{"id":"IMPLEMENTATION","requires":[{"capability":"project.frontend"}]}],
    }
    realization={
        "artifacts":[
            {"id":"OPENAPI","provides":["project.http"]},
            {"id":"FRONTEND-ARCH","provides":["project.frontend"]},
        ]
    }
    rejected={
        "kind":"harness-artifact-semantic-evaluation","artifact":"OPENAPI",
        "capability":"project.http","status":"REJECTED",
        "semantic_claims":{"accepted":[]}
    }
    result=capability_realization([graph,realization,rejected],"IMPLEMENTATION")
    assert "project.http" not in result["usable"]
    assert "project.frontend" not in result["usable"]
    assert result["semantic_invalid"]["project.http"]==["project.http"]
    assert result["semantic_invalid"]["project.frontend"]==["project.http"]

    accepted=dict(rejected)
    accepted["status"]="ACCEPTED"
    accepted["semantic_claims"]={"accepted":["engineering.interface.machine.contract"]}
    result=capability_realization([graph,realization,accepted],"IMPLEMENTATION")
    assert {"project.http","project.frontend"} <= result["usable"]

    # Claim-level gating: ACCEPTED capability evidence does not authorize claims
    # omitted from the semantic evaluation.
    from coverage_planner import capability_claim_index
    bindings={"bindings":[{"capability":"project.http","semantic_claims":[
        "engineering.interface.machine.contract",
        "engineering.interface.machine.errors",
    ]}]}
    claims=capability_claim_index(bindings,[graph,realization,accepted])
    assert claims["project.http"]==[
        {"claim":"engineering.interface.machine.contract"}
    ]


def main():
    test_real_defect_regressions()
    test_coverage_gating_and_invalidation()
    print("semantic acceptance regression suite: PASS (7 real defects + gating/invalidation)")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
