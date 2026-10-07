#!/usr/bin/env python3
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from harness.integration.repository_realization import evaluate


def _base_realization() -> dict:
    return {
        "kind": "repository-realization-design",
        "id": "TEST-REALIZATION-CONFORMANCE",
        "module_realizations": [
            {
                "semantic_owner": "IMPLEMENTATION-DESIGN",
                "physical_root": "src",
            }
        ],
        "obligations": [
            {
                "id": "test-execution",
                "applicability": "REQUIRED",
                "enforcement": "project test command",
            }
        ],
        "environment": {
            "lock_or_equivalent": "project lock",
        },
        "gate_policy": {
            "applicability": "NOT_APPLICABLE",
            "rationale": "Regression fixture has no merge/release gate.",
        },
        "quality_gates": [],
    }


def test_test_design_realization_rejects_missing_operation() -> None:
    realization = _base_realization()
    realization["test_realizations"] = [
        {
            "test_contract": {
                "id": "TEST-SCOPE",
                "operation_obligations": [
                    {"id": "OP-APPLY", "description": "User applies/selects scope."},
                    {"id": "OP-CLEAR", "description": "User clears scope."},
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
            },
            "executable_evidence": [
                {
                    "id": "EXEC-SCOPE-CYCLE",
                    "test": "tests/e2e/scope.spec::scope-cycle",
                }
            ],
            "bindings": [
                {
                    "id": "BIND-SCOPED",
                    "obligation": "ORACLE-SCOPED",
                    "evidence": ["EXEC-SCOPE-CYCLE"],
                },
                {
                    "id": "BIND-CLEAR",
                    "obligation": "OP-CLEAR",
                    "evidence": ["EXEC-SCOPE-CYCLE"],
                },
                {
                    "id": "BIND-RESTORED",
                    "obligation": "ORACLE-RESTORED",
                    "evidence": ["EXEC-SCOPE-CYCLE"],
                },
            ],
            "semantic_review": {
                "status": "ACCEPTED",
                "bindings": [
                    {"binding": "BIND-SCOPED", "status": "ACCEPTED"},
                    {"binding": "BIND-CLEAR", "status": "ACCEPTED"},
                    {"binding": "BIND-RESTORED", "status": "ACCEPTED"},
                ],
            },
        }
    ]

    result = evaluate(realization)

    assert not result["complete"], result
    assert any(
        issue["code"] == "TEST_REALIZATION_OPERATION_MISSING"
        and issue.get("obligation") == "OP-APPLY"
        for issue in result["errors"]
    ), result


def main() -> int:
    test_test_design_realization_rejects_missing_operation()
    print("test realization conformance RED unexpectedly passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
