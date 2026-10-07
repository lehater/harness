#!/usr/bin/env python3
from copy import deepcopy
from pathlib import Path
import sys

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from harness.assurance.semantic_derivation import evaluate_derivation
from harness.assurance.test_realization import evaluate as evaluate_test_realization
from harness.assurance.traceability_projection import build_traceability_projection

GRAPH = ROOT / "spec" / "scenario-suite" / "fixtures" / "external" / "prep-engineering-graph.yaml"


def _graph() -> dict:
    return yaml.safe_load(GRAPH.read_text(encoding="utf-8"))


def _interaction(*, apply_status: str = "REQUIRED") -> dict:
    items = [
        {
            "id": "OR-APPLY",
            "assertion": "IX-APPLY-SCOPE",
            "category": "ACTION",
            "status": apply_status,
            **(
                {"rationale": "Accepted explicit non-UI disposition."}
                if apply_status != "REQUIRED"
                else {}
            ),
        },
        {
            "id": "OR-CURRENT",
            "assertion": "IX-CURRENT-SCOPE",
            "category": "STATE",
            "status": "REQUIRED",
        },
    ]
    return {
        "capability": "prep.interaction-design",
        "semantic_assertions": [
            {
                "id": "IX-APPLY-SCOPE",
                "kind": "scope-obligation",
                "subject": "knowledge-scope",
                "semantic_value": "user-applies-required-capability-scope",
            },
            {
                "id": "IX-CURRENT-SCOPE",
                "kind": "scope-obligation",
                "subject": "knowledge-scope",
                "semantic_value": "selected-scope-is-observable",
            },
        ],
        "semantic_review": {
            "status": "ACCEPTED",
            "checks": ["observable-realization-applicability"],
            "observable_realization_obligations": items,
        },
    }


def _screen(*, extra_apply_realization: bool = False) -> dict:
    assertions = [
        {
            "id": "OBS-APPLY-SCOPE",
            "kind": "observable-realization",
            "observable_category": "ACTION",
            "subject": "knowledge-scope",
            "semantic_value": "user-can-apply-required-capability-scope",
            "derived_from": ["IX-APPLY-SCOPE"],
        },
        {
            "id": "OBS-CURRENT-SCOPE",
            "kind": "observable-realization",
            "observable_category": "STATE",
            "subject": "knowledge-scope",
            "semantic_value": "selected-scope-is-visible",
            "derived_from": ["IX-CURRENT-SCOPE"],
        },
    ]
    if extra_apply_realization:
        assertions.append(
            {
                "id": "OBS-APPLY-SCOPE-ALT",
                "kind": "observable-realization",
                "observable_category": "ACTION",
                "subject": "knowledge-scope",
                "semantic_value": "alternate-accepted-apply-mechanism",
                "derived_from": ["IX-APPLY-SCOPE"],
            }
        )
    return {
        "capability": "prep.screen-view-design",
        "semantic_assertions": assertions,
    }


def _test_design(*, include_apply_operation: bool = True) -> dict:
    operations = []
    if include_apply_operation:
        operations.append(
            {"id": "OP-APPLY", "description": "User applies/selects scope."}
        )
    operations.append({"id": "OP-CLEAR", "description": "User clears scope."})
    return {
        "version": 1,
        "kind": "harness-knowledge-artifact",
        "artifact": "GENERIC-TEST-DESIGN",
        "schema": "test-design/v1",
        "title": "Generic scope Test Design",
        "capability": "prep.frontend-test-design",
        "semantic_assertions": [
            {
                "id": "TEST-APPLY-SCOPE",
                "kind": "test-behavior",
                "subject": "TEST-SCOPE",
                "semantic_value": "contract-tests-apply-scope",
                "derived_from": ["OBS-APPLY-SCOPE"],
            },
            {
                "id": "TEST-CURRENT-SCOPE",
                "kind": "test-behavior",
                "subject": "TEST-SCOPE",
                "semantic_value": "contract-observes-selected-scope",
                "derived_from": ["OBS-CURRENT-SCOPE"],
            },
        ],
        "content": {
            "purpose": "Exercise the scoped Knowledge flow.",
            "tests": [
                {
                    "id": "TEST-SCOPE",
                    "verification_refs": ["VER-SCOPE"],
                    "precondition": "Knowledge is shown without optional scope.",
                    "operation": "Apply a scope, then clear it.",
                    "oracle": "Scoped results appear, then broader results are restored.",
                    "operation_obligations": operations,
                    "oracle_obligations": [
                        {
                            "id": "ORACLE-SCOPED",
                            "description": "Scoped result/context becomes observable.",
                        },
                        {
                            "id": "ORACLE-RESTORED",
                            "description": "Broader result/context is restored after clear.",
                        },
                    ],
                }
            ],
        },
    }


def _i2s_contract() -> dict:
    return {
        "version": 1,
        "kind": "harness-semantic-derivation-contract",
        "id": "generic-interaction-to-screen",
        "source_capability": "prep.interaction-design",
        "target_capability": "prep.screen-view-design",
        "obligations": [
            {
                "id": "observable-scope",
                "source_kind": "scope-obligation",
                "min_count": 2,
                "observable_realization": True,
            }
        ],
        "lifecycle_dependency": {"exhaustive": False},
        "semantic_judgement": {
            "required": True,
            "required_checks": ["observable-realization-correspondence"],
        },
    }


def _s2t_contract() -> dict:
    return {
        "version": 1,
        "kind": "harness-semantic-derivation-contract",
        "id": "generic-screen-to-test",
        "source_capability": "prep.screen-view-design",
        "target_capability": "prep.frontend-test-design",
        "obligations": [
            {
                "id": "screen-behavior",
                "source_kind": "observable-realization",
                "min_count": 2,
                "require_target_provenance": True,
            }
        ],
        "lifecycle_dependency": {"exhaustive": False},
        "semantic_judgement": {"required": False},
    }


def _accepted_i2s(*, include_apply: bool = True, extra_apply: bool = False) -> dict:
    screen = _screen(extra_apply_realization=extra_apply)
    links = [
        {
            "id": "I2S-CURRENT",
            "sources": ["IX-CURRENT-SCOPE"],
            "relation": "REALIZES",
            "targets": ["OBS-CURRENT-SCOPE"],
        }
    ]
    if include_apply:
        targets = ["OBS-APPLY-SCOPE"]
        if extra_apply:
            targets.append("OBS-APPLY-SCOPE-ALT")
        links.insert(
            0,
            {
                "id": "I2S-APPLY",
                "sources": ["IX-APPLY-SCOPE"],
                "relation": "REALIZES",
                "targets": targets,
            },
        )
    evidence = {
        "version": 1,
        "kind": "harness-semantic-derivation-evidence",
        "source_capability": "prep.interaction-design",
        "target_capability": "prep.screen-view-design",
        "links": links,
        "dispositions": [],
    }
    first = evaluate_derivation(
        graph=_graph(),
        contract=_i2s_contract(),
        source=_interaction(),
        candidate=screen,
        evidence=evidence,
    )
    request = first["semantic_judgement_request"]
    evidence["semantic_judgement"] = {
        "version": 1,
        "kind": "harness-semantic-derivation-judgement",
        "reviewer_kind": "HUMAN",
        "request_id": request["request_id"],
        "status": "ACCEPTED",
        "checks": ["observable-realization-correspondence"],
        "reviewed_links": [item["id"] for item in links],
        "findings": [],
    }
    return evaluate_derivation(
        graph=_graph(),
        contract=_i2s_contract(),
        source=_interaction(),
        candidate=screen,
        evidence=evidence,
    )


def _unresolved_i2s() -> dict:
    links = [
        {
            "id": "I2S-APPLY",
            "sources": ["IX-APPLY-SCOPE"],
            "relation": "REALIZES",
            "targets": ["OBS-APPLY-SCOPE"],
        },
        {
            "id": "I2S-CURRENT",
            "sources": ["IX-CURRENT-SCOPE"],
            "relation": "REALIZES",
            "targets": ["OBS-CURRENT-SCOPE"],
        },
    ]
    return evaluate_derivation(
        graph=_graph(),
        contract=_i2s_contract(),
        source=_interaction(),
        candidate=_screen(),
        evidence={
            "version": 1,
            "kind": "harness-semantic-derivation-evidence",
            "source_capability": "prep.interaction-design",
            "target_capability": "prep.screen-view-design",
            "links": links,
            "dispositions": [],
        },
    )


def _disposed_i2s() -> dict:
    source = _interaction(apply_status="NOT_APPLICABLE")
    evidence = {
        "version": 1,
        "kind": "harness-semantic-derivation-evidence",
        "source_capability": "prep.interaction-design",
        "target_capability": "prep.screen-view-design",
        "links": [
            {
                "id": "I2S-CURRENT",
                "sources": ["IX-CURRENT-SCOPE"],
                "relation": "REALIZES",
                "targets": ["OBS-CURRENT-SCOPE"],
            }
        ],
        "dispositions": [],
    }
    first = evaluate_derivation(
        graph=_graph(),
        contract=_i2s_contract(),
        source=source,
        candidate=_screen(),
        evidence=evidence,
    )
    request = first["semantic_judgement_request"]
    evidence["semantic_judgement"] = {
        "version": 1,
        "kind": "harness-semantic-derivation-judgement",
        "reviewer_kind": "HUMAN",
        "request_id": request["request_id"],
        "status": "ACCEPTED",
        "checks": ["observable-realization-correspondence"],
        "reviewed_links": ["I2S-CURRENT"],
        "findings": [],
    }
    return evaluate_derivation(
        graph=_graph(),
        contract=_i2s_contract(),
        source=source,
        candidate=_screen(),
        evidence=evidence,
    )


def _s2t(*, include_apply: bool = True) -> dict:
    links = [
        {
            "id": "S2T-CURRENT",
            "sources": ["OBS-CURRENT-SCOPE"],
            "relation": "REALIZES",
            "targets": ["TEST-CURRENT-SCOPE"],
        }
    ]
    if include_apply:
        links.insert(
            0,
            {
                "id": "S2T-APPLY",
                "sources": ["OBS-APPLY-SCOPE"],
                "relation": "REALIZES",
                "targets": ["TEST-APPLY-SCOPE"],
            },
        )
    return evaluate_derivation(
        graph=_graph(),
        contract=_s2t_contract(),
        source=_screen(),
        candidate=_test_design(),
        evidence={
            "version": 1,
            "kind": "harness-semantic-derivation-evidence",
            "source_capability": "prep.screen-view-design",
            "target_capability": "prep.frontend-test-design",
            "links": links,
            "dispositions": [],
        },
    )


def _realization_evidence(
    *, missing: str | None = None, split: bool = False
) -> tuple[dict, dict]:
    executables = [
        {
            "id": "EXEC-SCOPE-CYCLE",
            "test": "scope.spec::scope_cycle",
            "status": "PASSED",
        }
    ]
    if split:
        executables = [
            {
                "id": "EXEC-APPLY",
                "test": "scope.spec::apply",
                "status": "PASSED",
            },
            {
                "id": "EXEC-CLEAR",
                "test": "scope.spec::clear",
                "status": "PASSED",
            },
        ]
    bindings = []
    for obligation in [
        "OP-APPLY",
        "OP-CLEAR",
        "ORACLE-SCOPED",
        "ORACLE-RESTORED",
    ]:
        if obligation == missing:
            continue
        evidence_ref = "EXEC-SCOPE-CYCLE"
        if split:
            evidence_ref = (
                "EXEC-APPLY"
                if obligation in {"OP-APPLY", "ORACLE-SCOPED"}
                else "EXEC-CLEAR"
            )
        bindings.append(
            {
                "id": f"BIND-{obligation}",
                "obligation": obligation,
                "evidence": [evidence_ref],
            }
        )
    evidence = {
        "version": 1,
        "kind": "harness-test-realization-evidence",
        "test_contract": "TEST-SCOPE",
        "executables": executables,
        "bindings": bindings,
    }
    review = {
        "version": 1,
        "kind": "harness-test-realization-semantic-review",
        "status": "ACCEPTED",
        "checks": ["executable-correspondence"],
        "binding_reviews": [
            {
                "binding": item["id"],
                "status": "ACCEPTED",
                "rationale": "Reviewed against concrete executable behavior.",
            }
            for item in bindings
        ],
    }
    return evidence, review


def _h2(*, missing: str | None = None, split: bool = False) -> dict:
    evidence, review = _realization_evidence(missing=missing, split=split)
    return evaluate_test_realization(_test_design(), evidence, review)


def _request(*, extra_apply: bool = False) -> dict:
    screen_targets = ["OBS-APPLY-SCOPE"]
    if extra_apply:
        screen_targets.append("OBS-APPLY-SCOPE-ALT")
    return {
        "version": 1,
        "kind": "harness-traceability-projection-request",
        "trace_id": "TRACE-APPLY",
        "root": {
            "artifact": "GENERIC-INTERACTION",
            "assertion": "IX-APPLY-SCOPE",
            "category": "ACTION",
        },
        "interaction_to_screen": {
            "source_capability": "prep.interaction-design",
            "target_capability": "prep.screen-view-design",
            "source_assertion": "IX-APPLY-SCOPE",
            "target_assertions": screen_targets,
        },
        "screen_to_test_design": {
            "source_capability": "prep.screen-view-design",
            "target_capability": "prep.frontend-test-design",
            "source_assertions": ["OBS-APPLY-SCOPE"],
            "target_assertions": ["TEST-APPLY-SCOPE"],
        },
        "test_design": {
            "contract": "TEST-SCOPE",
            "obligations": [
                {"id": "OP-APPLY", "kind": "operation"},
                {"id": "ORACLE-SCOPED", "kind": "oracle"},
            ],
        },
    }


def _project(
    *,
    i2s: dict,
    s2t: dict | None,
    design: dict | None = None,
    h2: dict | None = None,
    request: dict | None = None,
    currentness: dict | None = None,
    extra_derivations: list[dict] | None = None,
) -> dict:
    derivations = [i2s]
    if s2t is not None:
        derivations.append(s2t)
    derivations.extend(extra_derivations or [])
    return build_traceability_projection(
        request or _request(),
        derivation_evaluations=derivations,
        test_design=design or _test_design(),
        test_realization_evaluations=[] if h2 is None else [h2],
        currentness=currentness,
    )


def test_t1_interaction_to_screen_missing_is_first() -> None:
    result = _project(i2s=_accepted_i2s(include_apply=False), s2t=None)
    assert result["overall_status"] == "INCOMPLETE", result
    assert result["first_missing_link"] == "INTERACTION_TO_SCREEN", result
    assert result["stages"]["screen"]["status"] == "MISSING", result
    assert result["stages"]["test_design"]["status"] == "BLOCKED_BY_UPSTREAM", result
    assert result["stages"]["executable"]["status"] == "BLOCKED_BY_UPSTREAM", result


def test_t2_screen_to_test_design_missing_is_first() -> None:
    result = _project(i2s=_accepted_i2s(), s2t=_s2t(include_apply=False))
    assert result["overall_status"] == "INCOMPLETE", result
    assert result["first_missing_link"] == "SCREEN_TO_TEST_DESIGN", result
    assert result["stages"]["executable"]["status"] == "BLOCKED_BY_UPSTREAM", result


def test_t3_test_design_contract_gap_is_first() -> None:
    result = _project(
        i2s=_accepted_i2s(),
        s2t=_s2t(),
        design=_test_design(include_apply_operation=False),
    )
    assert result["overall_status"] == "INCOMPLETE", result
    assert result["first_missing_link"] == "TEST_DESIGN_CONTRACT", result
    assert result["missing_obligation"] == "OP-APPLY", result


def test_t4_test_design_to_executable_missing_reuses_h2() -> None:
    result = _project(
        i2s=_accepted_i2s(),
        s2t=_s2t(),
        h2=_h2(missing="OP-APPLY"),
    )
    assert result["overall_status"] == "INCOMPLETE", result
    assert result["first_missing_link"] == "TEST_DESIGN_TO_EXECUTABLE", result
    assert result["missing_obligation"] == "OP-APPLY", result


def test_t5_unresolved_semantic_correspondence_stops_at_owning_edge() -> None:
    result = _project(i2s=_unresolved_i2s(), s2t=_s2t(), h2=_h2())
    assert result["overall_status"] == "QUESTION", result
    assert result["first_missing_link"] == "INTERACTION_TO_SCREEN", result
    assert result["stages"]["test_design"]["status"] == "BLOCKED_BY_UPSTREAM", result


def test_complete_chain_is_complete() -> None:
    result = _project(i2s=_accepted_i2s(), s2t=_s2t(), h2=_h2())
    assert result["overall_status"] == "COMPLETE", result
    assert result["first_missing_link"] is None, result
    assert result["stages"]["executable"]["status"] == "ACCEPTED", result


def test_legitimate_disposition_is_not_a_missing_link() -> None:
    result = _project(i2s=_disposed_i2s(), s2t=None)
    assert result["overall_status"] == "DISPOSITIONED", result
    assert result["first_missing_link"] is None, result
    assert result["stages"]["screen"]["status"] == "DISPOSITIONED", result
    assert result["stages"]["test_design"]["status"] == "NOT_EVALUABLE", result


def test_one_to_many_realization_accepts_one_valid_required_path() -> None:
    result = _project(
        i2s=_accepted_i2s(extra_apply=True),
        s2t=_s2t(),
        h2=_h2(),
        request=_request(extra_apply=True),
    )
    assert result["overall_status"] == "COMPLETE", result
    assert result["stages"]["screen"]["semantic_ids"] == [
        "OBS-APPLY-SCOPE",
        "OBS-APPLY-SCOPE-ALT",
    ], result


def test_unrelated_evidence_does_not_change_selected_trace() -> None:
    baseline = _project(i2s=_accepted_i2s(), s2t=_s2t(), h2=_h2())
    unrelated = {
        "version": 1,
        "kind": "harness-semantic-derivation-evaluation",
        "source_capability": "unrelated.source",
        "target_capability": "unrelated.target",
        "status": "REJECTED",
        "required_sources": ["OTHER"],
        "covered_sources": [],
        "dispositions": [],
        "links": [],
        "findings": [{"code": "UNDISPOSITIONED_SOURCE", "source": "OTHER"}],
    }
    changed = _project(
        i2s=_accepted_i2s(),
        s2t=_s2t(),
        h2=_h2(),
        extra_derivations=[unrelated],
    )
    assert changed == baseline


def test_implementation_freedom_preserves_projection_completeness() -> None:
    single = _project(i2s=_accepted_i2s(), s2t=_s2t(), h2=_h2(split=False))
    split = _project(i2s=_accepted_i2s(), s2t=_s2t(), h2=_h2(split=True))
    assert single["overall_status"] == split["overall_status"] == "COMPLETE"
    assert single["stages"] == split["stages"]


def test_existing_currentness_marks_earliest_unusable_link_without_recomputing() -> None:
    result = _project(
        i2s=_accepted_i2s(),
        s2t=_s2t(),
        h2=_h2(),
        currentness={"SCREEN_TO_TEST_DESIGN": "STALE"},
    )
    assert result["overall_status"] == "STALE", result
    assert result["first_missing_link"] == "SCREEN_TO_TEST_DESIGN", result
    assert result["stages"]["test_design"]["status"] == "STALE", result
    assert result["stages"]["executable"]["status"] == "BLOCKED_BY_UPSTREAM", result


def test_composed_vertical_chain_complete_then_exact_middle_mutation() -> None:
    complete = _project(i2s=_accepted_i2s(), s2t=_s2t(), h2=_h2())
    assert complete["overall_status"] == "COMPLETE", complete

    mutated = _project(
        i2s=_accepted_i2s(),
        s2t=_s2t(include_apply=False),
        h2=_h2(),
    )
    assert mutated["overall_status"] == "INCOMPLETE", mutated
    assert mutated["first_missing_link"] == "SCREEN_TO_TEST_DESIGN", mutated


def test_projection_is_deterministic_for_same_accepted_inputs() -> None:
    kwargs = {"i2s": _accepted_i2s(), "s2t": _s2t(), "h2": _h2()}
    assert _project(**kwargs) == _project(**kwargs)


def main() -> int:
    test_t1_interaction_to_screen_missing_is_first()
    test_t2_screen_to_test_design_missing_is_first()
    test_t3_test_design_contract_gap_is_first()
    test_t4_test_design_to_executable_missing_reuses_h2()
    test_t5_unresolved_semantic_correspondence_stops_at_owning_edge()
    test_complete_chain_is_complete()
    test_legitimate_disposition_is_not_a_missing_link()
    test_one_to_many_realization_accepts_one_valid_required_path()
    test_unrelated_evidence_does_not_change_selected_trace()
    test_implementation_freedom_preserves_projection_completeness()
    test_existing_currentness_marks_earliest_unusable_link_without_recomputing()
    test_composed_vertical_chain_complete_then_exact_middle_mutation()
    test_projection_is_deterministic_for_same_accepted_inputs()
    print(
        "traceability projection: ok "
        "(T1-T5 + first-break + disposition + one-to-many + freedom + currentness + composed vertical)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
