#!/usr/bin/env python3
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# HARNESS-007 RED: this standard projection is intentionally absent at baseline.
from harness.assurance.traceability_projection import build_traceability_projection


def test_projection_reports_first_missing_interaction_to_screen() -> None:
    request = {
        "version": 1,
        "kind": "harness-traceability-projection-request",
        "trace_id": "TRACE-APPLY",
        "root": {
            "artifact": "GENERIC-INTERACTION",
            "assertion": "IX-APPLY-SCOPE",
            "category": "ACTION",
        },
        "interaction_to_screen": {
            "source_capability": "demo.interaction",
            "target_capability": "demo.screen",
            "source_assertion": "IX-APPLY-SCOPE",
            "target_assertions": ["OBS-APPLY-SCOPE"],
        },
        "screen_to_test_design": {
            "source_capability": "demo.screen",
            "target_capability": "demo.test-design",
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
    interaction_to_screen = {
        "version": 1,
        "kind": "harness-semantic-derivation-evaluation",
        "source_capability": "demo.interaction",
        "target_capability": "demo.screen",
        "status": "REJECTED",
        "required_sources": ["IX-APPLY-SCOPE"],
        "covered_sources": [],
        "dispositions": [],
        "links": [],
        "coverage": {"required": 1, "covered": 0, "disposed": 0, "unresolved": 1},
        "findings": [
            {
                "code": "UNDISPOSITIONED_SOURCE",
                "source": "IX-APPLY-SCOPE",
                "target_capability": "demo.screen",
            }
        ],
    }

    result = build_traceability_projection(
        request,
        derivation_evaluations=[interaction_to_screen],
        test_design={"schema": "test-design/v1", "content": {"tests": []}},
        test_realization_evaluations=[],
    )

    assert result["overall_status"] == "INCOMPLETE", result
    assert result["first_missing_link"] == "INTERACTION_TO_SCREEN", result
    assert result["stages"]["screen"]["status"] == "MISSING", result
    assert result["stages"]["test_design"]["status"] == "BLOCKED_BY_UPSTREAM", result
    assert result["stages"]["executable"]["status"] == "BLOCKED_BY_UPSTREAM", result


def main() -> int:
    test_projection_reports_first_missing_interaction_to_screen()
    print("traceability projection RED: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
