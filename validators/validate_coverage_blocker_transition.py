#!/usr/bin/env python3
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))

from engineering_coverage import evaluate_with_repository_policy, load


def run(core_name):
    return evaluate_with_repository_policy(
        graph=load(ROOT/"spec/research/coverage-blocker-fixture-graph.yaml"),
        realization=load(ROOT/f"spec/research/{core_name}"),
        consumer="IMPLEMENTATION",
        scope="all",
        project_overlay={
            "activate":[
                {
                    "concern":"security.threat-analysis",
                    "rationale":"Fixture threat analysis is required.",
                }
            ],
            "decisions":[],
        },
    )


def main():
    unresolved=run("coverage-blocker-fixture-core-unresolved.yaml")
    resolved=run("coverage-blocker-fixture-core-resolved.yaml")

    ur={row["concern"]:row for row in unresolved["rows"]}["security.threat-analysis"]
    rr={row["concern"]:row for row in resolved["rows"]}["security.threat-analysis"]

    assert ur["state"] == "MISSING"
    assert ur["action"] == "RESOLVE_QUESTIONS"
    assert ur["questions"] == ["Q-THREAT"]
    assert unresolved["question_frontier"] == [
        {
            "action":"ASK",
            "question":"Q-THREAT",
            "authority":"SECURITY-ANALYSIS",
            "text":"What trust-boundary threat decision is required?",
        }
    ]

    assert rr["state"] == "MISSING"
    assert rr["action"] == "PRODUCE_CAPABILITY"
    assert rr["ready_production_candidates"][0]["capability"] == "fixture.security.threat-analysis"
    assert rr["ready_production_candidates"][0]["authority"] == "SECURITY-ANALYSIS"
    assert resolved["question_frontier"] == []

    print("coverage blocker transition: ok")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
