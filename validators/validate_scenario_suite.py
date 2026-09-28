#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scenario_suite import run_suite  # noqa: E402


def main() -> int:
    report = run_suite(
        ROOT / "spec/scenario-suite/scenarios",
        ROOT / "spec/scenario-suite/catalog-v1.yaml",
    )
    if report["status"] != "PASS":
        print("Harness scenario suite failed:", file=sys.stderr)
        for scenario in report["scenarios"]:
            if scenario["status"] != "PASSED":
                print(
                    f"- {scenario['id']}: {scenario.get('error')}",
                    file=sys.stderr,
                )
        for finding in report["coverage"]["findings"]:
            print(f"- coverage: {finding}", file=sys.stderr)
        return 1

    print(
        "Harness scenario suite passed "
        f"({report['scenario_count']} scenarios; "
        f"{len(report['coverage']['requirements'])} required behaviors covered)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
