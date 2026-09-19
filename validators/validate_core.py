#!/usr/bin/env python3
"""Validate Harness Core v0 and its acceptance fixtures."""
from __future__ import annotations

import copy
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from harness import (  # noqa: E402
    CoreError,
    affected,
    blocked,
    capability_owner,
    next_action,
    capability_resolve,
    completeness,
    design_frontier,
    question_frontier,
    resolve_question,
    unresolved_questions,
    validate_model,
)


def main() -> int:
    errors: list[str] = []
    required = [ROOT / "harness.py", ROOT / "docs/design/core-v0.md"]
    for path in required:
        if not path.is_file():
            errors.append(f"missing Core v0 file: {path.relative_to(ROOT)}")

    fixtures = sorted((ROOT / "spec/acceptance").glob("*.yaml"))
    if not fixtures:
        errors.append("no Core v0 acceptance fixtures found")

    for path in fixtures:
        try:
            doc = yaml.safe_load(path.read_text(encoding="utf-8"))
            if doc.get("kind") != "harness-core-acceptance":
                raise CoreError("unexpected acceptance fixture kind")
            model = doc["model"]
            expect = doc["expect"]
            validate_model(model)

            affected_expect = expect["affected"]
            actual = affected(model, affected_expect["artifact"])
            missing = sorted(set(affected_expect.get("contains", [])) - set(actual))
            if missing:
                raise CoreError(f"affected missing expected artifacts: {missing}")

            cap = expect["capability"]
            if capability_resolve(model, cap["id"]) != sorted(cap["providers"]):
                raise CoreError("capability resolve mismatch")
            if capability_owner(model, cap["id"]) != cap["owner"]:
                raise CoreError("capability owner mismatch")

            completeness_expect = expect.get("completeness")
            if completeness_expect:
                expectations = completeness_expect["expectations"]
                coverage = completeness_expect["coverage"]
                actual_missing = completeness(expectations, coverage)
                if actual_missing != completeness_expect["missing"]:
                    raise CoreError(
                        f"completeness mismatch: {actual_missing!r} != {completeness_expect['missing']!r}"
                    )
                frontier_expect = completeness_expect.get("frontier")
                if frontier_expect is not None:
                    actual_frontier = design_frontier(model, expectations, coverage)
                    if actual_frontier != frontier_expect:
                        raise CoreError(
                            f"design frontier mismatch: {actual_frontier!r} != {frontier_expect!r}"
                        )
                    question_expect = completeness_expect.get("question_frontier")
                    if question_expect is not None:
                        blocker_ids = [
                            question
                            for item in actual_frontier["wait"]
                            for question in item.get("questions", [])
                        ]
                        actual_questions = question_frontier(model, blocker_ids)
                        if actual_questions != question_expect:
                            raise CoreError(
                                f"question frontier mismatch: {actual_questions!r} != {question_expect!r}"
                            )

                complete_coverage = completeness_expect.get("complete_coverage")
                if complete_coverage is not None:
                    actual_complete = design_frontier(model, expectations, complete_coverage)
                    expected_complete = {"status": "COMPLETE", "design": [], "wait": []}
                    if actual_complete != expected_complete:
                        raise CoreError(
                            f"complete frontier mismatch: {actual_complete!r} != {expected_complete!r}"
                        )

            action = expect.get("next_action")
            if action:
                actual_action = next_action(model, action["capability"])
                for key, value in action.items():
                    if key == "capability":
                        continue
                    if actual_action.get(key) != value:
                        raise CoreError(
                            f"next-action {key} mismatch: {actual_action.get(key)!r} != {value!r}"
                        )

            if unresolved_questions(model) != sorted(expect["questions"]["unresolved"]):
                raise CoreError("questions mismatch")

            block = expect["blocked"]
            if blocked(model, block["artifact"]) != sorted(block["by"]):
                raise CoreError("blocked mismatch")

            resolution = expect["resolution"]
            resolved = resolve_question(copy.deepcopy(model), resolution["question"], resolution["artifact"])
            after_action = resolution.get("next_action")
            if after_action:
                actual_after = next_action(resolved, after_action["capability"])
                for key, value in after_action.items():
                    if key == "capability":
                        continue
                    if actual_after.get(key) != value:
                        raise CoreError(
                            f"resolved next-action {key} mismatch: {actual_after.get(key)!r} != {value!r}"
                        )
            if unresolved_questions(resolved) != sorted(resolution["unresolved_after"]):
                raise CoreError("resolve-question did not clear unresolved question")
            if blocked(resolved, block["artifact"]) != sorted(resolution["blocked_after"]):
                raise CoreError("resolve-question did not clear blocking")
        except Exception as exc:
            errors.append(f"{path.relative_to(ROOT)}: {exc}")

    if errors:
        print("Harness Core validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(f"Harness Core validation passed ({len(fixtures)} acceptance fixture(s))")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
