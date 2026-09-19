#!/usr/bin/env python3
"""Validate the managed knowledge workspace acceptance scenario."""
from __future__ import annotations

import shutil
import sys
import tempfile
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from harness import CoreError  # noqa: E402
from workspace import load_workspace, render_workspace, validate_knowledge_document  # noqa: E402


def main() -> int:
    errors: list[str] = []
    fixture = ROOT / "spec/workspace-acceptance/minimal-domain"
    required = [
        fixture / ".harness/graph.yaml",
        fixture / ".harness/profile.yaml",
        fixture / ".harness/config.yaml",
        fixture / ".harness/knowledge/application-domain.yaml",
        fixture / ".harness/knowledge/application-verification.yaml",
        fixture / "expected/application-domain.md",
        fixture / "expected/application-verification.md",
    ]
    for path in required:
        if not path.is_file():
            errors.append(f"missing workspace acceptance file: {path.relative_to(ROOT)}")

    if not errors:
        try:
            workspace = load_workspace(fixture)
            if workspace["target_state"]["status"] != "COMPLETE":
                raise CoreError(f"expected COMPLETE target state: {workspace['target_state']!r}")

            invalid = yaml.safe_load(
                (fixture / ".harness/knowledge/application-domain.yaml").read_text(encoding="utf-8")
            )
            invalid["content"]["purpose"] = ""
            try:
                validate_knowledge_document(invalid)
            except CoreError:
                pass
            else:
                raise CoreError("invalid domain knowledge passed schema validation")

            with tempfile.TemporaryDirectory() as temp_dir:
                target = Path(temp_dir) / "project"
                shutil.copytree(fixture, target)
                result = render_workspace(target)
                if result["target_state"]["status"] != "COMPLETE":
                    raise CoreError("render changed target-state result")
                actual = (target / "docs/generated/application-domain.md").read_text(encoding="utf-8")
                expected = (fixture / "expected/application-domain.md").read_text(encoding="utf-8")
                if actual != expected:
                    raise CoreError("generated domain document does not match acceptance output")

                actual = (target / "docs/generated/application-verification.md").read_text(encoding="utf-8")
                expected = (fixture / "expected/application-verification.md").read_text(encoding="utf-8")
                if actual != expected:
                    raise CoreError("generated verification document does not match acceptance output")
        except Exception as exc:
            errors.append(f"workspace acceptance: {exc}")

    if errors:
        print("Harness workspace validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print("Harness workspace validation passed (1 acceptance scenario)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
