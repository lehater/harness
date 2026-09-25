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


def granular_frontend_eval(semantic_evaluations=None):
    graph = load(ROOT / "examples/user-facing-application/engineering-graph.yaml")
    realization = load(ROOT / "examples/user-facing-application/core-state-complete.yaml")
    return evaluate_with_repository_policy(
        graph=graph,
        realization=realization,
        consumer="FRONTEND-IMPLEMENTATION",
        scope="granular-frontend",
        project_overlay={
            "subject_inventory": {
                "state": "NOT_APPLICABLE",
                "rationale": "This fixture validates shared frontend knowledge concerns rather than per-screen subjects.",
            }
        },
        semantic_evaluations=semantic_evaluations,
    )


def frontend_presentation_eval(semantic_evaluations=None):
    graph = load(ROOT / "examples/frontend-legacy-compatibility/engineering-graph.yaml")
    realization = load(ROOT / "examples/frontend-legacy-compatibility/core-state-complete.yaml")
    return evaluate_with_repository_policy(
        graph=graph,
        realization=realization,
        consumer="FRONTEND-IMPLEMENTATION",
        scope="legacy-frontend",
        project_overlay={
            "subject_inventory": {
                "state": "NOT_APPLICABLE",
                "rationale": "Compatibility fixture validates migration and strict shared frontend claims.",
            }
        },
        semantic_evaluations=semantic_evaluations,
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

    # Granular frontend providers are structurally present but strict semantic
    # claims remain unusable until explicit semantic acceptance evidence exists.
    granular_missing = granular_frontend_eval()
    granular_rows = {row["concern"]: row for row in granular_missing["rows"]}
    granular_caps = {
        "interface.human.conceptual-model": "example.frontend.conceptual-model",
        "interface.human.information-architecture": "example.frontend.information-architecture",
        "interface.human.interaction": "example.frontend.interaction",
        "interface.human.navigation-topology": "example.frontend.topology",
    }
    for concern, capability in granular_caps.items():
        assert granular_rows[concern]["state"] == "MISSING", granular_rows[concern]
        assert granular_rows[concern]["action"] == "VALIDATE_SEMANTICS", granular_rows[concern]
        assert granular_rows[concern]["capabilities"] == [capability], granular_rows[concern]

    granular_evidence = {
        "version": 1,
        "kind": "harness-semantic-evaluation-set",
        "semantic_evaluations": [
            {
                "kind": "harness-artifact-semantic-evaluation",
                "artifact": f"ACCEPT-{capability}",
                "capability": capability,
                "status": "ACCEPTED",
                "semantic_claims": {"accepted": [claim]},
            }
            for capability, claim in (
                ("example.frontend.conceptual-model", "engineering.interface.human.conceptual-model"),
                ("example.frontend.information-architecture", "engineering.interface.human.information-architecture"),
                ("example.frontend.interaction", "engineering.interface.human.interaction"),
                ("example.frontend.topology", "engineering.interface.human.navigation-topology"),
            )
        ],
    }
    granular_accepted = granular_frontend_eval(granular_evidence)
    granular_accepted_rows = {
        row["concern"]: row for row in granular_accepted["rows"]
    }
    for concern in granular_caps:
        assert granular_accepted_rows[concern]["state"] == "COVERED", granular_accepted_rows[concern]

    # Frontend identity and presentation/composition cannot be declared complete
    # merely because provider artifacts exist. These concerns require explicit
    # semantic acceptance evidence.
    presentation_missing = frontend_presentation_eval()
    presentation_rows = {
        row["concern"]: row for row in presentation_missing["rows"]
    }

    # Consumer-driven activation must surface missing granular frontend knowledge
    # even when a legacy project graph only declares the broad human-interface
    # capability. Reconcile remains non-destructive; Engineering Coverage is the
    # independent migration/completeness lens.
    for concern in (
        "interface.human.conceptual-model",
        "interface.human.information-architecture",
        "interface.human.interaction",
        "interface.human.navigation-topology",
    ):
        assert concern in presentation_rows, (concern, presentation_rows)
        assert presentation_rows[concern]["state"] == "MISSING", presentation_rows[concern]
        assert presentation_rows[concern]["action"] == "MODEL_PRODUCTION_CONTRACT", presentation_rows[concern]
        routes = presentation_rows[concern].get("routes", {})
        accepted = presentation_rows[concern]["accepted_semantic_claims"]
        assert accepted, presentation_rows[concern]
        for claim in accepted:
            assert "HUMAN-INTERFACE-DESIGN" in routes.get(claim, []), presentation_rows[concern]
    for concern, capability in {
        "security.identity": "legacy.frontend.security",
        "interface.human.presentation-system": "legacy.frontend.presentation-system",
        "interface.human.screen-composition": "legacy.frontend.screen-view",
        "verification.interface.presentation": "legacy.frontend.verification",
    }.items():
        assert concern in presentation_rows
        assert presentation_rows[concern]["state"] == "MISSING"
        assert presentation_rows[concern]["action"] == "VALIDATE_SEMANTICS"
        assert presentation_rows[concern]["capabilities"] == [capability]
        expected_rule = (
            "FRONTEND-SECURITY-IDENTITY"
            if concern == "security.identity"
            else "FRONTEND-PRESENTATION"
        )
        assert any(
            item.get("rule") == expected_rule
            for item in presentation_rows[concern]["activation_provenance"]
        )

    accepted_evidence = {
        "version": 1,
        "kind": "harness-semantic-evaluation-set",
        "semantic_evaluations": [
            {
                "kind": "harness-artifact-semantic-evaluation",
                "artifact": "LEGACY-SECURITY",
                "capability": "legacy.frontend.security",
                "status": "ACCEPTED",
                "semantic_claims": {
                    "accepted": [
                        "engineering.security.identity"
                    ]
                },
            },
            {
                "kind": "harness-artifact-semantic-evaluation",
                "artifact": "LEGACY-PRESENTATION",
                "capability": "legacy.frontend.presentation-system",
                "status": "ACCEPTED",
                "semantic_claims": {
                    "accepted": [
                        "engineering.interface.human.presentation-system"
                    ]
                },
            },
            {
                "kind": "harness-artifact-semantic-evaluation",
                "artifact": "LEGACY-SCREEN",
                "capability": "legacy.frontend.screen-view",
                "status": "ACCEPTED",
                "semantic_claims": {
                    "accepted": [
                        "engineering.interface.human.screen-composition"
                    ]
                },
            },
            {
                "kind": "harness-artifact-semantic-evaluation",
                "artifact": "LEGACY-VERIFICATION",
                "capability": "legacy.frontend.verification",
                "status": "ACCEPTED",
                "semantic_claims": {
                    "accepted": [
                        "engineering.verification.interface.presentation"
                    ]
                },
            },
        ],
    }
    presentation_accepted = frontend_presentation_eval(accepted_evidence)
    accepted_rows = {
        row["concern"]: row for row in presentation_accepted["rows"]
    }
    for concern in (
        "security.identity",
        "interface.human.presentation-system",
        "interface.human.screen-composition",
        "verification.interface.presentation",
    ):
        assert accepted_rows[concern]["state"] == "COVERED"

    print(
        "unified engineering coverage evaluator: ok "
        f"(mvp={mvp['activated_count']}, later={later['activated_count']})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
