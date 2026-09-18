#!/usr/bin/env python3
"""Validate integration adapters without extending Core v0 semantics."""
from __future__ import annotations

import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from adapters.canonical_graph import project_model  # noqa: E402
from harness import (  # noqa: E402
    CoreError,
    blocked,
    capability_owner,
    capability_resolve,
    unresolved_questions,
)


def main() -> int:
    errors: list[str] = []
    fixtures = sorted((ROOT / "spec/adapter-acceptance").glob("*.yaml"))
    if not fixtures:
        errors.append("no adapter acceptance fixtures found")

    for path in fixtures:
        try:
            doc = yaml.safe_load(path.read_text(encoding="utf-8"))
            if doc.get("kind") != "harness-adapter-acceptance":
                raise CoreError("unexpected adapter acceptance fixture kind")

            model = project_model(doc["source_graph"], doc["projection"])
            expect = doc["expect"]
            artifacts = {item["id"]: item for item in model["artifacts"]}

            if set(artifacts) != set(expect["artifacts"]):
                raise CoreError("projected artifact set mismatch")
            for artifact_id, artifact_expect in expect["artifacts"].items():
                actual = artifacts[artifact_id]
                if actual["path"] != artifact_expect["path"]:
                    raise CoreError(f"{artifact_id}: projected path mismatch")
                if actual["depends_on"] != sorted(artifact_expect["depends_on"]):
                    raise CoreError(f"{artifact_id}: projected dependencies mismatch")

            cap = expect["capability"]
            if capability_resolve(model, cap["id"]) != sorted(cap["providers"]):
                raise CoreError("projected capability resolve mismatch")
            if capability_owner(model, cap["id"]) != cap["owner"]:
                raise CoreError("projected capability owner mismatch")

            if unresolved_questions(model) != sorted(expect["questions"]["unresolved"]):
                raise CoreError("projected questions mismatch")

            block = expect["blocked"]
            if blocked(model, block["artifact"]) != sorted(block["by"]):
                raise CoreError("projected blocking mismatch")
        except Exception as exc:
            errors.append(f"{path.relative_to(ROOT)}: {exc}")

    if errors:
        print("Harness adapter validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(f"Harness adapter validation passed ({len(fixtures)} acceptance fixture(s))")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
