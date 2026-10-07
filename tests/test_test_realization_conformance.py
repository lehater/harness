#!/usr/bin/env python3
from copy import deepcopy

from harness.assurance.test_realization import evaluate


def _test_design() -> dict:
    return {
        "version": 1,
        "kind": "harness-knowledge-artifact",
        "artifact": "GENERIC-TEST-DESIGN",
        "schema": "test-design/v1",
        "title": "Generic Test Design",
        "content": {
            "purpose": "Exercise executable Test Design conformance.",
            "tests": [
                {
                    "id": "TEST-SCOPE",
                    "verification_refs": ["VER-SCOPE"],
                    "precondition": "Collection is shown without optional scope.",
                    "operation": "Apply a scope, then clear it.",
                    "oracle": "Scoped results appear, then broader results are restored.",
                    "operation_obligations": [
                        {
                            "id": "OP-APPLY",
                            "description": "User applies/selects scope.",
                        },
                        {
                            "id": "OP-CLEAR",
                            "description": "User clears scope.",
                        },
                    ],
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


def _evidence() -> dict:
    return {
        "version": 1,
        "kind": "harness-test-realization-evidence",
        "test_contract": "TEST-SCOPE",
        "executables": [
            {
                "id": "EXEC-SCOPE-CYCLE",
                "test": "tests/e2e/scope.spec::scope-cycle",
                "status": "PASSED",
            }
        ],
        "bindings": [
            {
                "id": "BIND-APPLY",
                "obligation": "OP-APPLY",
                "evidence": ["EXEC-SCOPE-CYCLE"],
            },
            {
                "id": "BIND-CLEAR",
                "obligation": "OP-CLEAR",
                "evidence": ["EXEC-SCOPE-CYCLE"],
            },
            {
                "id": "BIND-SCOPED",
                "obligation": "ORACLE-SCOPED",
                "evidence": ["EXEC-SCOPE-CYCLE"],
            },
            {
                "id": "BIND-RESTORED",
                "obligation": "ORACLE-RESTORED",
                "evidence": ["EXEC-SCOPE-CYCLE"],
            },
        ],
    }


def _review(*binding_ids: str) -> dict:
    return {
        "version": 1,
        "kind": "harness-test-realization-semantic-review",
        "status": "ACCEPTED",
        "checks": ["executable-correspondence"],
        "binding_reviews": [
            {
                "binding": binding_id,
                "status": "ACCEPTED",
                "rationale": "Reviewed against the concrete executable behavior.",
            }
            for binding_id in binding_ids
        ],
    }


def _all_binding_ids(evidence: dict) -> tuple[str, ...]:
    return tuple(item["id"] for item in evidence["bindings"])


def test_test_design_realization_rejects_missing_operation() -> None:
    evidence = _evidence()
    evidence["bindings"] = [
        item for item in evidence["bindings"] if item["obligation"] != "OP-APPLY"
    ]

    result = evaluate(
        _test_design(),
        evidence,
        _review(*_all_binding_ids(evidence)),
    )

    assert result["status"] == "REJECTED", result
    assert any(
        finding["code"] == "TEST_REALIZATION_OPERATION_MISSING"
        and finding.get("obligation") == "OP-APPLY"
        for finding in result["findings"]
    ), result


def test_test_design_realization_rejects_missing_oracle() -> None:
    evidence = _evidence()
    evidence["bindings"] = [
        item
        for item in evidence["bindings"]
        if item["obligation"] != "ORACLE-RESTORED"
    ]

    result = evaluate(
        _test_design(),
        evidence,
        _review(*_all_binding_ids(evidence)),
    )

    assert result["status"] == "REJECTED", result
    assert any(
        finding["code"] == "TEST_REALIZATION_ORACLE_MISSING"
        and finding.get("obligation") == "ORACLE-RESTORED"
        for finding in result["findings"]
    ), result


def test_binding_claim_does_not_count_without_semantic_correspondence_review() -> None:
    evidence = _evidence()
    reviewed = tuple(
        binding_id
        for binding_id in _all_binding_ids(evidence)
        if binding_id != "BIND-APPLY"
    )

    result = evaluate(_test_design(), evidence, _review(*reviewed))

    assert result["status"] == "REJECTED", result
    assert any(
        finding["code"] == "TEST_REALIZATION_BINDING_UNREVIEWED"
        and finding.get("binding") == "BIND-APPLY"
        for finding in result["findings"]
    ), result
    assert any(
        finding["code"] == "TEST_REALIZATION_OPERATION_MISSING"
        and finding.get("obligation") == "OP-APPLY"
        for finding in result["findings"]
    ), result


def test_full_test_design_realization_is_accepted() -> None:
    evidence = _evidence()

    result = evaluate(
        _test_design(),
        evidence,
        _review(*_all_binding_ids(evidence)),
    )

    assert result["status"] == "ACCEPTED", result
    assert result["coverage"] == {
        "operations": {"required": 2, "covered": 2},
        "oracles": {"required": 2, "covered": 2},
    }


def test_materially_different_test_organizations_can_realize_same_contract() -> None:
    design = _test_design()
    single_test = _evidence()
    single_result = evaluate(
        design,
        single_test,
        _review(*_all_binding_ids(single_test)),
    )
    assert single_result["status"] == "ACCEPTED", single_result

    split_tests = deepcopy(single_test)
    split_tests["executables"] = [
        {
            "id": "EXEC-APPLY",
            "test": "behavior/scope_apply",
            "status": "PASSED",
        },
        {
            "id": "EXEC-CLEAR",
            "test": "integration/scope_clear_and_restore",
            "status": "PASSED",
        },
    ]
    for binding in split_tests["bindings"]:
        if binding["obligation"] in {"OP-APPLY", "ORACLE-SCOPED"}:
            binding["evidence"] = ["EXEC-APPLY"]
        else:
            binding["evidence"] = ["EXEC-CLEAR"]

    split_result = evaluate(
        design,
        split_tests,
        _review(*_all_binding_ids(split_tests)),
    )

    assert split_result["status"] == "ACCEPTED", split_result
    assert split_result["coverage"] == single_result["coverage"]
