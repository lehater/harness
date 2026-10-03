#!/usr/bin/env python3
from copy import deepcopy
from pathlib import Path
import sys
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from harness.workspace.frontend_interface_knowledge import (
    evaluate_frontend_ux_closure,
    evaluate_topology_screen_subject_coverage,
    required_screen_ids,
)
from harness.workspace.frontend_screen_contracts import evaluate_frontend_screen_contracts
from harness.application.ui_design_convergence import (
    evaluate_ui_design_convergence,
    ui_decision_rule_index,
)

EX = ROOT / "examples" / "user-facing-application" / "canonical"
UI_RULES = ROOT / "catalogs" / "ui" / "decision-rules-v0.yaml"


def load(path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def codes(result):
    return {x["code"] for x in result["findings"]}


def main() -> int:
    task = load(EX / "example-task-model.yaml")
    conceptual = load(EX / "example-conceptual-interface-model.yaml")
    ia = load(EX / "example-information-architecture.yaml")
    interaction = load(EX / "example-interaction-design.yaml")
    topology = load(EX / "example-interface-topology.yaml")

    result = evaluate_frontend_ux_closure(task, conceptual, ia, interaction, topology)
    assert result["status"] == "ACCEPTED", result
    assert set(result["required_screen_ids"]) == {"APPLICATION-SHELL", "RESOURCE-CATALOGUE", "RESOURCE-DETAIL"}

    bad = deepcopy(interaction)
    bad["contexts"] = [x for x in bad["contexts"] if x["id"] != "RESOURCE-DETAIL-CONTEXT"]
    r = evaluate_frontend_ux_closure(task, conceptual, ia, bad, topology)
    assert "UNCOVERED_USER_TASK" in codes(r), r

    bad_top = deepcopy(topology)
    bad_top["views"] = [x for x in bad_top["views"] if x["id"] != "RESOURCE-DETAIL"]
    r = evaluate_frontend_ux_closure(task, conceptual, ia, interaction, bad_top)
    assert "UNMAPPED_INTERACTION_CONTEXT" in codes(r), r
    assert "USER_TASK_WITHOUT_VIEW" in codes(r), r

    bad_structural = deepcopy(topology)
    shell = next(x for x in bad_structural["views"] if x["id"] == "APPLICATION-SHELL")
    shell["interaction_context_refs"] = ["RESOURCE-CATALOGUE-CONTEXT"]
    r = evaluate_frontend_ux_closure(task, conceptual, ia, interaction, bad_structural)
    assert "STRUCTURAL_VIEW_HAS_TASK_CONTEXT" in codes(r), r

    bad_ia = deepcopy(ia)
    bad_ia["locations"][0]["concept_refs"] = ["UNKNOWN"]
    r = evaluate_frontend_ux_closure(task, conceptual, bad_ia, interaction, topology)
    assert "UNKNOWN_CONCEPT_REF" in codes(r), r

    screens = load(EX / "example-screen-view-design.yaml")
    screen_ids = {row["id"] for row in screens.get("screens", [])}
    subject_coverage = evaluate_topology_screen_subject_coverage(topology, screen_ids)
    assert subject_coverage["status"] == "ACCEPTED", subject_coverage

    missing_subjects = evaluate_topology_screen_subject_coverage(
        topology,
        screen_ids - {"RESOURCE-DETAIL"},
    )
    assert missing_subjects["missing_subjects"] == ["RESOURCE-DETAIL"], missing_subjects

    presentation = load(EX / "example-presentation-system.yaml")
    r = evaluate_frontend_screen_contracts(
        presentation,
        screens,
        None,
        screen_ids=required_screen_ids(topology),
    )
    assert "MISSING_REQUIRED_SCREEN" not in codes(r), r

    missing = deepcopy(screens)
    missing["screens"] = [x for x in missing["screens"] if x["id"] != "RESOURCE-DETAIL"]
    r = evaluate_frontend_screen_contracts(
        presentation,
        missing,
        None,
        screen_ids=required_screen_ids(topology),
    )
    assert "MISSING_REQUIRED_SCREEN" in codes(r), r


    rule_catalog = load(UI_RULES)
    rule_index = ui_decision_rule_index(rule_catalog)
    assert set(rule_index) == {
        "UI-RULE-SYMBOLIC-EXACT-INSPECTION",
        "UI-RULE-TASK-CRITICAL-KEYBOARD",
    }

    convergence = {
        "version": 1,
        "kind": "harness-ui-design-convergence-evidence",
        "subject": "PREP / VIEW-KNOWLEDGE",
        "coverage": [
            {
                "id": "critical-task-disposition",
                "status": "COVERED",
                "evidence_refs": ["TASK-U-EXPLORE-KNOWLEDGE"],
            },
            {
                "id": "semantic-traceability",
                "status": "COVERED",
                "evidence_refs": ["IX-KNOWLEDGE", "VIEW-KNOWLEDGE"],
            },
            {
                "id": "accessibility-obligations",
                "status": "COVERED",
                "evidence_refs": ["IX-KNOWLEDGE.keyboard-path"],
            },
            {
                "id": "critical-executable-paths",
                "status": "COVERED",
                "evidence_refs": ["storybook:KnowledgeWorkspace"],
            },
            {
                "id": "prototype-contract-consistency",
                "status": "COVERED",
                "evidence_refs": ["storybook:KnowledgeWorkspace:contract-check"],
            },
        ],
        "material_decisions": [
            {
                "id": "KD-01",
                "axis": "knowledge-representation",
                "question": "Which representation carries exact symbolic inspection?",
                "materiality": "MATERIAL",
                "disposition": "DETERMINED",
                "selected": "structured-query-results-detail",
                "basis_refs": ["TASK-U-EXPLORE-KNOWLEDGE", "IX-KNOWLEDGE"],
                "applied_rules": ["UI-RULE-SYMBOLIC-EXACT-INSPECTION"],
                "residual_uncertainty": [],
                "controlled_freedom": ["table-vs-list-vs-card-within-structured-baseline"],
                "required_evidence_levels": ["E0", "E2"],
                "evaluation_evidence": {
                    "E0": ["prep-knowledge-semantic-closure"],
                    "E2": ["storybook:KnowledgeWorkspace"],
                },
            },
            {
                "id": "KD-04",
                "axis": "control-surface",
                "question": "May task-critical exploration depend on graph manipulation?",
                "materiality": "CRITICAL",
                "disposition": "DETERMINED",
                "selected": "semantic-keyboard-path-with-optional-direct-manipulation",
                "basis_refs": ["IX-KNOWLEDGE.keyboard-path"],
                "applied_rules": ["UI-RULE-TASK-CRITICAL-KEYBOARD"],
                "residual_uncertainty": [],
                "controlled_freedom": ["supplemental-pointer-and-spatial-controls"],
                "required_evidence_levels": ["E0", "E2"],
                "evaluation_evidence": {
                    "E0": ["interaction-contract"],
                    "E2": ["storybook:KnowledgeWorkspace"],
                },
            },
        ],
    }
    ready = evaluate_ui_design_convergence(
        rule_catalog=rule_catalog,
        evidence=convergence,
    )
    assert ready["status"] == "READY", ready
    assert ready["ui_design_ready"] is True, ready

    empirical = deepcopy(convergence)
    empirical["material_decisions"].append(
        {
            "id": "KD-02",
            "axis": "knowledge-representation",
            "question": "Should relationship visualization be the production default?",
            "materiality": "MATERIAL",
            "disposition": "EMPIRICAL_VALIDATION_REQUIRED",
            "basis_refs": ["TASK-U-EXPLORE-KNOWLEDGE", "J-KNOWLEDGE-ORIENTATION"],
            "applied_rules": [],
            "residual_uncertainty": [],
            "controlled_freedom": ["2d-vs-3d-prototype-form"],
            "required_evidence_levels": ["E3"],
            "evaluation_evidence": {},
        }
    )
    not_ready = evaluate_ui_design_convergence(
        rule_catalog=rule_catalog,
        evidence=empirical,
    )
    assert not_ready["status"] == "NOT_READY", not_ready
    assert "UI_EMPIRICAL_VALIDATION_REQUIRED" in codes(not_ready), not_ready
    assert "UI_REQUIRED_EVALUATION_EVIDENCE_MISSING" in codes(not_ready), not_ready

    unknown_rule = deepcopy(convergence)
    unknown_rule["material_decisions"][0]["applied_rules"] = ["UI-RULE-UNKNOWN"]
    r = evaluate_ui_design_convergence(
        rule_catalog=rule_catalog,
        evidence=unknown_rule,
    )
    assert "UI_UNKNOWN_DECISION_RULE" in codes(r), r

    unresolved_coverage = deepcopy(convergence)
    next(
        item
        for item in unresolved_coverage["coverage"]
        if item["id"] == "accessibility-obligations"
    )["status"] = "UNRESOLVED"
    r = evaluate_ui_design_convergence(
        rule_catalog=rule_catalog,
        evidence=unresolved_coverage,
    )
    assert "UI_COVERAGE_UNRESOLVED" in codes(r), r

    residual = deepcopy(convergence)
    residual["material_decisions"][0]["residual_uncertainty"] = [
        "production default still depends on representative task evidence"
    ]
    r = evaluate_ui_design_convergence(
        rule_catalog=rule_catalog,
        evidence=residual,
    )
    assert "UI_RESIDUAL_MATERIAL_UNCERTAINTY" in codes(r), r

    print("frontend UX closure: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
