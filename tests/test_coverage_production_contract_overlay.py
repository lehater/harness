#!/usr/bin/env python3
from pathlib import Path
import copy
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))

from harness.application.coverage_application import evaluate_project_coverage
from harness.coverage.engineering_coverage import evaluate_with_repository_policy, load
from harness.application.skill_router import GLOBAL_INSTRUCTION_CONTRACTS


def main():
    graph=load(ROOT/"spec/research/scope-activation-fixture-graph.yaml")
    core=load(ROOT/"spec/research/scope-activation-fixture-core.yaml")

    pure=evaluate_with_repository_policy(
        graph=graph,
        realization=core,
        consumer="IMPLEMENTATION",
        scope="mvp",
        scope_roots=["fixture.mvp.implementation-design"],
        project_overlay={
            "activate":[
                {
                    "concern":"data.lifecycle",
                    "rationale":"Fixture requires explicit data lifecycle.",
                }
            ],
            "decisions":[],
        },
        production_contract_overlay={
            "version":1,
            "kind":"harness-production-contract-overlay",
            "productions":[
                {
                    "authority":"DATA-DESIGN",
                    "capability":"fixture.mvp.data-lifecycle-design",
                    "semantic_claims":["engineering.data.lifecycle"],
                    "knowledge_kind":"data-design",
                    "requires":["fixture.mvp.data-design"],
                }
            ],
        },
    )

    pure_items=[item for item in pure["work_items"] if item.get("capability")=="fixture.mvp.data-lifecycle-design"]
    assert len(pure_items)==1
    assert "execution_route" not in pure_items[0]
    assert "routed_production_count" not in pure

    result=evaluate_project_coverage(
        graph=graph,
        realization=core,
        consumer="IMPLEMENTATION",
        scope="mvp",
        scope_roots=["fixture.mvp.implementation-design"],
        project_overlay={"activate":[{"concern":"data.lifecycle","rationale":"Fixture requires explicit data lifecycle."}],"decisions":[]},
        production_contract_overlay={
            "version":1,
            "kind":"harness-production-contract-overlay",
            "productions":[{
                "authority":"DATA-DESIGN",
                "capability":"fixture.mvp.data-lifecycle-design",
                "semantic_claims":["engineering.data.lifecycle"],
                "knowledge_kind":"data-design",
                "requires":["fixture.mvp.data-design"],
            }],
        },
    )

    rows={row["concern"]:row for row in result["rows"]}
    lifecycle=rows["data.lifecycle"]

    assert lifecycle["state"] == "MISSING"
    assert lifecycle["action"] == "PRODUCE_CAPABILITY"
    assert lifecycle["ready_production_candidates"] == [
        {
            "claim":"engineering.data.lifecycle",
            "capability":"fixture.mvp.data-lifecycle-design",
            "authority":"DATA-DESIGN",
            "knowledge_kind":"data-design",
            "requires":["fixture.mvp.data-design"],
            "missing_prerequisites":[],
            "questions":[],
            "ready":True,
        }
    ]

    items=[
        item for item in result["work_items"]
        if item.get("capability")=="fixture.mvp.data-lifecycle-design"
    ]
    assert len(items)==1
    assert items[0]["authority"]=="DATA-DESIGN"
    assert items[0]["concerns"]==["data.lifecycle"]
    assert items[0]["execution_route"] == {
        "status":"ROUTED",
        "knowledge_kind":"data-design",
        "skill":"skills/artifacts/data-design/SKILL.md",
        "instruction_contracts": list(GLOBAL_INSTRUCTION_CONTRACTS),
    }
    assert result["routed_production_count"] == 1

    # The new Coverage-only capability must not become an activation signal.
    assert "fixture.mvp.data-lifecycle-design" not in result["activation_signals"]["capabilities"]

    # HARN-008: a Core row cannot make a Coverage-only production proposal
    # authoritative. Until Project Model adopts the Capability into the accepted
    # Engineering Graph, it remains missing work and cannot close Coverage.
    phantom_core=copy.deepcopy(core)
    phantom_core.setdefault("artifacts",[]).append({
        "id":"UNACCEPTED-DATA-LIFECYCLE",
        "authority":"DATA-DESIGN",
        "path":"docs/unaccepted-data-lifecycle.yaml",
        "provides":["fixture.mvp.data-lifecycle-design"],
        "depends_on":[],
    })
    phantom=evaluate_with_repository_policy(
        graph=graph,
        realization=phantom_core,
        consumer="IMPLEMENTATION",
        scope="mvp",
        scope_roots=["fixture.mvp.implementation-design"],
        project_overlay={
            "activate":[
                {
                    "concern":"data.lifecycle",
                    "rationale":"Fixture requires explicit data lifecycle.",
                }
            ],
            "decisions":[],
        },
        production_contract_overlay={
            "version":1,
            "kind":"harness-production-contract-overlay",
            "productions":[{
                "authority":"DATA-DESIGN",
                "capability":"fixture.mvp.data-lifecycle-design",
                "semantic_claims":["engineering.data.lifecycle"],
                "knowledge_kind":"data-design",
                "requires":["fixture.mvp.data-design"],
            }],
        },
    )
    phantom_lifecycle={row["concern"]:row for row in phantom["rows"]}["data.lifecycle"]
    assert phantom_lifecycle["state"] == "MISSING", phantom_lifecycle
    assert phantom_lifecycle["action"] == "PRODUCE_CAPABILITY", phantom_lifecycle
    assert not phantom["completion_ready"], phantom

    # Strict semantic claims must preserve produce -> validate ordering.
    # A declared Process production contract with no provider is CREATE work,
    # not another MODEL_PRODUCTION_CONTRACT gap.
    process_graph = {
        "version": 1,
        "kind": "harness-engineering-graph",
        "id": "STRICT-PRODUCE-THEN-VALIDATE",
        "default_subject": "STRICT-PRODUCE-THEN-VALIDATE",
        "authorities": [
            {
                "id": "APPLICATION-DESIGN",
                "responsibility": "Own application design and process semantics.",
                "boundary": {
                    "semantic_cohesion": "Application composition.",
                    "independent_change": "Application composition changes independently.",
                    "public_contract": "Accepted application contracts.",
                },
                "produces": [
                    {
                        "capability": "fixture.application",
                        "knowledge_kind": "application-design",
                        "semantic_claims": ["engineering.application.orchestration"],
                        "requires": [],
                    },
                    {
                        "capability": "fixture.application-process",
                        "knowledge_kind": "application-process-design",
                        "semantic_claims": ["engineering.application.process"],
                        "requires": ["fixture.application"],
                    },
                ],
            }
        ],
        "consumers": [
            {
                "id": "IMPLEMENTATION",
                "purpose": "Consume process semantics.",
                "requires": ["fixture.application-process"],
            }
        ],
        "terminal_capabilities": [],
    }
    process_realization = {
        "artifacts": [
            {
                "id": "APPLICATION",
                "authority": "APPLICATION-DESIGN",
                "path": "docs/application.yaml",
                "provides": ["fixture.application"],
                "depends_on": [],
            }
        ],
        "questions": [],
    }
    process_result = evaluate_project_coverage(
        graph=process_graph,
        realization=process_realization,
        consumer="IMPLEMENTATION",
        scope="default",
        project_overlay={
            "subject_inventory": {
                "state": "NOT_APPLICABLE",
                "rationale": "Single process fixture.",
            }
        },
    )
    process_row = {
        row["concern"]: row for row in process_result["rows"]
    }["application.process"]
    assert process_row["state"] == "MISSING", process_row
    assert process_row["action"] == "PRODUCE_CAPABILITY", process_row
    process_items = [
        item for item in process_result["work_items"]
        if item.get("capability") == "fixture.application-process"
    ]
    assert len(process_items) == 1, process_items
    assert process_items[0]["execution_route"]["knowledge_kind"] == (
        "application-process-design"
    ), process_items[0]

    print("production contract overlay: ok")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
