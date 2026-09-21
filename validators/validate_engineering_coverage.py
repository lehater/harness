#!/usr/bin/env python3
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from engineering_coverage import evaluate_with_repository_policy, load


def scope_eval(root, scope):
    return evaluate_with_repository_policy(
        graph=load(ROOT / "spec/research/scope-activation-fixture-graph.yaml"),
        realization=load(ROOT / "spec/research/scope-activation-fixture-core.yaml"),
        consumer="IMPLEMENTATION",
        scope=scope,
        scope_roots=[root],
    )


def subject_eval(core):
    return evaluate_with_repository_policy(
        graph=load(ROOT / "spec/research/subject-coverage-fixture-graph.yaml"),
        realization=load(ROOT / f"spec/research/{core}"),
        consumer="IMPLEMENTATION",
        scope="all",
        project_overlay={
            "activate": [
                {
                    "concern": "domain.model",
                    "rationale": "Both bounded contexts need independent domain models.",
                }
            ],
            "decisions": [],
        },
    )


def main() -> int:
    mvp = scope_eval("fixture.mvp.implementation-design", "mvp")
    later = scope_eval("fixture.later.implementation-design", "later")

    mvp_rows = {row["concern"]: row for row in mvp["rows"]}
    later_rows = {row["concern"]: row for row in later["rows"]}

    assert mvp["kind"] == "harness-engineering-coverage-evaluation"
    assert mvp["consumer"] == "IMPLEMENTATION"
    assert mvp["scope_roots"] == ["fixture.mvp.implementation-design"]
    assert "data.lifecycle" in mvp_rows
    # Implementation completeness must not depend on an already-declared
    # component-design capability. The consumer itself activates these concerns.
    for concern in (
        "engineering.principles",
        "engineering.components",
        "engineering.code-quality",
    ):
        assert concern in mvp_rows
        assert mvp_rows[concern]["state"] != "COVERED"
    assert mvp_rows["engineering.components"]["action"] in {
        "ASSIGN_AUTHORITY",
        "MODEL_PRODUCTION_CONTRACT",
        "PRODUCE_CAPABILITY",
    }
    assert "interface.human.accessibility" not in mvp_rows
    assert "interface.human.accessibility" in later_rows
    assert "data.lifecycle" not in later_rows
    assert mvp["remaining_work_count"] == len(mvp["remaining_work"])
    assert mvp["work_item_count"] == len(mvp["work_items"])
    assert not mvp["completion_ready"]

    partial = subject_eval("subject-coverage-fixture-core-partial.yaml")
    complete = subject_eval("subject-coverage-fixture-core-complete.yaml")

    p = {row["concern"]: row for row in partial["rows"]}["domain.model"]
    c = {row["concern"]: row for row in complete["rows"]}["domain.model"]

    assert p["state"] == "MISSING"
    assert {item["subject"] for item in p["covered_instances"]} == {"BC-A"}
    assert {item["subject"] for item in p["missing_instances"]} == {"BC-B"}
    assert p["action"] == "PRODUCE_CAPABILITY"
    subject_work = [
        item for item in partial["work_items"]
        if item.get("capability") == "fixture.domain.model.bc-b"
    ]
    assert len(subject_work) == 1
    assert subject_work[0]["authority"] == "TACTICAL-DOMAIN-DESIGN"
    assert subject_work[0]["concerns"] == ["domain.model"]
    assert subject_work[0]["semantic_claims"] == [
        {"claim": "engineering.domain.model", "subject": "BC-B"}
    ]

    assert c["state"] == "COVERED"
    assert {item["subject"] for item in c["proof_instances"]} == {"BC-A", "BC-B"}

    # Standard Authority IDs are resolved without project aliases.
    assert partial["authority_roles"]["bindings"]["TACTICAL-DOMAIN-DESIGN"] == ["domain"]
    assert partial["authority_roles"]["bindings"]["IMPLEMENTATION-DESIGN"] == ["delivery"]

    print(
        "unified engineering coverage evaluator: ok "
        f"(mvp={mvp['activated_count']}, later={later['activated_count']})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
