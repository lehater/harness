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
        fixture / ".harness/knowledge/application-requirements.yaml",
        fixture / ".harness/knowledge/application-domain.yaml",
        fixture / ".harness/knowledge/application-verification.yaml",
        fixture / ".harness/knowledge/application-test-design.yaml",
        fixture / "expected/application-requirements.md",
        fixture / "expected/application-domain.md",
        fixture / "expected/application-verification.md",
        fixture / "expected/application-test-design.md",
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

            invalid_requirements = yaml.safe_load(
                (fixture / ".harness/knowledge/application-requirements.yaml").read_text(encoding="utf-8")
            )
            invalid_requirements["content"]["requirements"].append(
                dict(invalid_requirements["content"]["requirements"][0])
            )
            try:
                validate_knowledge_document(invalid_requirements)
            except CoreError:
                pass
            else:
                raise CoreError("duplicate requirement id passed schema validation")

            invalid_verification = yaml.safe_load(
                (fixture / ".harness/knowledge/application-verification.yaml").read_text(encoding="utf-8")
            )
            invalid_verification["content"]["checks"] = []
            try:
                validate_knowledge_document(invalid_verification)
            except CoreError:
                pass
            else:
                raise CoreError("invalid verification knowledge passed schema validation")

            with tempfile.TemporaryDirectory() as temp_dir:
                target = Path(temp_dir) / "project"
                shutil.copytree(fixture, target)
                result = render_workspace(target)
                if result["target_state"]["status"] != "COMPLETE":
                    raise CoreError("render changed target-state result")
                for name in (
                    "application-requirements",
                    "application-domain",
                    "application-verification",
                    "application-test-design",
                ):
                    actual = (target / f"docs/generated/{name}.md").read_text(encoding="utf-8")
                    expected = (fixture / f"expected/{name}.md").read_text(encoding="utf-8")
                    if actual != expected:
                        raise CoreError(
                            f"generated {name} document does not match acceptance output"
                        )

            with tempfile.TemporaryDirectory() as temp_dir:
                target = Path(temp_dir) / "uncovered-requirement"
                shutil.copytree(fixture, target)
                verification_path = target / ".harness/knowledge/application-verification.yaml"
                verification = yaml.safe_load(verification_path.read_text(encoding="utf-8"))
                verification["content"]["checks"][0]["verifies"] = [
                    "APPLICATION-COMPONENT-UNIQUE"
                ]
                verification_path.write_text(
                    yaml.safe_dump(verification, sort_keys=False),
                    encoding="utf-8",
                )
                try:
                    load_workspace(target)
                except CoreError as exc:
                    if "accepted requirements without verification disposition" not in str(exc):
                        raise
                else:
                    raise CoreError("uncovered accepted requirement passed workspace validation")

            with tempfile.TemporaryDirectory() as temp_dir:
                target = Path(temp_dir) / "missing-test-contract"
                shutil.copytree(fixture, target)
                test_path = target / ".harness/knowledge/application-test-design.yaml"
                test_design = yaml.safe_load(test_path.read_text(encoding="utf-8"))
                test_design["content"]["tests"][0]["verification_refs"] = [
                    "VER-CANONICAL-GENERATION"
                ]
                test_path.write_text(
                    yaml.safe_dump(test_design, sort_keys=False),
                    encoding="utf-8",
                )
                try:
                    load_workspace(target)
                except CoreError as exc:
                    if "TEST verification checks without test-design contract" not in str(exc):
                        raise
                else:
                    raise CoreError("TEST verification without Test Design passed workspace validation")
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
