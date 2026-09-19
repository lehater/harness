#!/usr/bin/env python3
"""Validate the agent-facing Harness layer."""
from __future__ import annotations

import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from harness import CoreError  # noqa: E402
from target_state import validate_profile  # noqa: E402

REQUIRED_SKILLS = {
    "skills/core/bootstrap-existing-project/SKILL.md": (
        "# Bootstrap Existing Project",
        "## Trigger",
        "## Inputs",
        "## Procedure",
        "## Stop conditions",
        "## Output",
    ),
    "skills/core/design-profile/SKILL.md": (
        "# Design Profile",
        "## Trigger",
        "## Inputs",
        "## Procedure",
    ),
    "skills/artifacts/domain-model/SKILL.md": (
        "# Domain Model Artifact",
        "## Trigger",
        "## Inputs",
        "## Procedure",
        "## Output schema",
        "domain-model/v1",
    ),
    "skills/artifacts/verification-strategy/SKILL.md": (
        "# Verification Strategy Artifact",
        "## Trigger",
        "## Inputs",
        "## Procedure",
        "## Output schema",
        "verification-plan/v1",
    ),
    "skills/artifacts/source-classification-registry/SKILL.md": (
        "# Source Classification Registry",
        "## Trigger",
        "## Inputs",
        "## Procedure",
        "## Output contract",
        "project-native canonical artifact",
    ),
    "skills/artifacts/pinned-source-entity-set/SKILL.md": (
        "# Pinned Source Entity Set",
        "## Trigger",
        "## Inputs",
        "## Procedure",
        "## Output contract",
        "project-native",
    ),
}


def main() -> int:
    errors: list[str] = []

    for relative, required_fragments in REQUIRED_SKILLS.items():
        path = ROOT / relative
        if not path.is_file():
            errors.append(f"missing agent skill: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        if not text.startswith("---\n"):
            errors.append(f"skill missing frontmatter: {relative}")
        for fragment in required_fragments:
            if fragment not in text:
                errors.append(f"skill {relative} missing contract fragment: {fragment}")

    workbench = ROOT / "docs/design/agent-artifact-workbench-v0.md"
    if not workbench.is_file():
        errors.append("missing agent artifact workbench contract")

    starter = ROOT / "profiles/software-application-design-v0.yaml"
    if not starter.is_file():
        errors.append("missing software application starter profile")
    else:
        try:
            profile = yaml.safe_load(starter.read_text(encoding="utf-8"))
            if not isinstance(profile, dict):
                raise CoreError("starter profile must contain a mapping")
            validate_profile(profile)
            expected = {
                "PROBLEM": [],
                "REQUIREMENTS": ["PROBLEM"],
                "DOMAIN": ["REQUIREMENTS"],
                "ARCHITECTURE": ["DOMAIN"],
                "VERIFICATION": ["ARCHITECTURE"],
            }
            actual = {
                item["id"]: item.get("depends_on", [])
                for item in profile.get("expectations", [])
            }
            if actual != expected:
                raise CoreError(f"unexpected starter profile dependency chain: {actual!r}")
        except Exception as exc:
            errors.append(f"starter profile: {exc}")

    if errors:
        print("Harness agent-layer validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(f"Harness agent-layer validation passed ({len(REQUIRED_SKILLS)} skills)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
