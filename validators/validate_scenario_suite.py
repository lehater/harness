#!/usr/bin/env python3
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scenario_suite import load_driver_modules, run_suite  # noqa: E402
from scenario_drivers import get_driver  # noqa: E402


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

    semantic = next(
        item
        for item in report["scenarios"]
        if item["id"] == "semantic-gap-routes-question"
    )
    question_step = next(
        item for item in semantic["steps"] if item["id"] == "questions"
    )
    assert (
        question_step["observations"]["question_authority"]
        == "APPLICATION-DESIGN"
    ), question_step

    with tempfile.TemporaryDirectory() as temp_dir:
        module_path = Path(temp_dir) / "scenario_external_probe.py"
        module_path.write_text(
            "from scenario_drivers import scenario_driver\n"
            "@scenario_driver('external.probe')\n"
            "def probe(*, value):\n"
            "    return {'value': value}\n",
            encoding="utf-8",
        )
        sys.path.insert(0, temp_dir)
        try:
            load_driver_modules(["scenario_external_probe"])
            assert get_driver("external.probe")(value="ok") == {"value": "ok"}
        finally:
            sys.path.remove(temp_dir)
            sys.modules.pop("scenario_external_probe", None)

    print(
        "Harness scenario suite passed "
        f"({report['scenario_count']} scenarios; "
        f"{len(report['coverage']['requirements'])} required behaviors covered)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
