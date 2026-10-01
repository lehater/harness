#!/usr/bin/env python3
"""Prevent root AGENTS.md from regressing into a task-procedure/router monolith."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AGENTS = ROOT / "AGENTS.md"

FORBIDDEN_HEADINGS = (
    "## Consumer startup",
    "## Scenario Suite discipline",
    "## Audit and evolution capture discipline",
    "## LLM execution cost policy",
)

REQUIRED_BOOTSTRAP_MARKERS = (
    "Ordinary work in this repository uses the Maintainer Skill Surface",
    "skills/maintainer-operation-registry-v0.yaml",
    "skills/consumer-operation-registry-v0.yaml",
    "skills/consumer-method-registry-v0.yaml",
    "skills/artifact-skill-registry-v0.yaml",
    "skill_router.py",
    "Do not reconstruct task-specific procedures from this file.",
    "instruction_contracts",
    "canonical instruction trust boundary",
    "Never push or commit changes directly to",
)

CANONICAL_POLICY_FILES = (
    "spec/assurance/llm-execution-policy-v1.yaml",
    "docs/audit/README.md",
    "docs/design/core-v0.md",
    "docs/design/scenario-suite-v0.md",
)


def main() -> int:
    text = AGENTS.read_text(encoding="utf-8")
    errors: list[str] = []

    for heading in FORBIDDEN_HEADINGS:
        if heading in text:
            errors.append(
                f"root AGENTS.md must not own task-specific procedure section: {heading}"
            )

    for marker in REQUIRED_BOOTSTRAP_MARKERS:
        if marker not in text:
            errors.append(f"root AGENTS.md missing bootstrap invariant/pointer: {marker}")

    for relative in CANONICAL_POLICY_FILES:
        if not (ROOT / relative).is_file():
            errors.append(f"canonical policy/contract missing: {relative}")

    instruction_architecture = (
        ROOT / "docs/design/agent-instruction-architecture-v0.md"
    ).read_text(encoding="utf-8")
    for marker in (
        "## Content trust boundary",
        "delivery channel and registered",
        "data/evidence by default",
        "tool/provider results",
        "instruction_contracts",
    ):
        if marker not in instruction_architecture:
            errors.append(
                "agent instruction architecture missing trust-boundary marker: "
                + marker
            )

    for forbidden_detail in (
        "use GPT-6 Luna as the default",
        "auto-routed non-Luna result",
        "normal context/reasoning tier",
    ):
        if forbidden_detail in text:
            errors.append(
                "conditional provider-backed assurance detail leaked into root "
                f"AGENTS.md: {forbidden_detail}"
            )

    if errors:
        print("Harness instruction ownership validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Harness instruction ownership validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
