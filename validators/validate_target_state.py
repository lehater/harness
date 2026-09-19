#!/usr/bin/env python3
"""Validate Harness design target-state acceptance fixtures."""
from __future__ import annotations

import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from harness import CoreError  # noqa: E402
from target_state import evaluate_target_state, validate_profile  # noqa: E402


def main() -> int:
    errors: list[str] = []
    fixtures = sorted((ROOT / "spec/target-state-acceptance").glob("*.yaml"))
    if not fixtures:
        errors.append("no target-state acceptance fixtures found")

    for path in fixtures:
        try:
            doc = yaml.safe_load(path.read_text(encoding="utf-8"))
            if doc.get("kind") != "harness-target-state-acceptance":
                raise CoreError("unexpected target-state acceptance fixture kind")
            profile = doc["profile"]
            validate_profile(profile)

            for model_key, expect_key in (
                ("empty_model", "empty"),
                ("partial_model", "partial"),
                ("complete_model", "complete"),
            ):
                actual = evaluate_target_state(profile, doc[model_key])
                expected = doc["expect"][expect_key]
                if actual != expected:
                    raise CoreError(
                        f"{model_key} mismatch: {actual!r} != {expected!r}"
                    )
        except Exception as exc:
            errors.append(f"{path.relative_to(ROOT)}: {exc}")

    if errors:
        print("Harness target-state validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(f"Harness target-state validation passed ({len(fixtures)} acceptance fixture(s))")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
