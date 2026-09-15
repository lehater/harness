#!/usr/bin/env python3
"""Validate the repository-independent Harness surface."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FRONTMATTER = re.compile(r"\A---\n(?P<body>.*?)\n---(?:\n|$)", re.DOTALL)
NAME = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")

REQUIRED_FILES = [
    "AGENTS.md",
    "README.md",
    "docs/methodology/core/decision-protocol.md",
    "docs/methodology/core/document-lifecycle.md",
    "docs/methodology/core/working-loop.md",
    "docs/methodology/software-product/change-lifecycle.md",
    "docs/methodology/ddd/domain-change-protocol.md",
    "docs/methodology/ddd/strategic-ddd-convergence.md",
    "docs/methodology/ddd/tactical-ddd-stage.md",
    "skills/core/agent-harness-design/SKILL.md",
    "skills/core/record-project-knowledge/SKILL.md",
    "skills/core/resolve-decision/SKILL.md",
    "skills/software-product/architecture-review/SKILL.md",
    "skills/ddd/domain-model-change/SKILL.md",
]

FORBIDDEN_PATHS = [
    "contracts/project-binding.md",
    "runtime/README.md",
]


def main() -> int:
    errors: list[str] = []

    for relative in REQUIRED_FILES:
        if not (ROOT / relative).is_file():
            errors.append(f"missing required Harness file: {relative}")

    for relative in FORBIDDEN_PATHS:
        if (ROOT / relative).exists():
            errors.append(f"hard project binding/runtime contract must not exist: {relative}")

    for path in sorted(ROOT.glob("skills/*/*/SKILL.md")):
        text = path.read_text(encoding="utf-8").replace("\r\n", "\n")
        match = FRONTMATTER.match(text)
        if not match:
            errors.append(f"{path.relative_to(ROOT)}: missing YAML frontmatter")
            continue
        fields: dict[str, str] = {}
        for line in match.group("body").splitlines():
            if ":" not in line or line.startswith((" ", "\t")):
                continue
            key, value = line.split(":", 1)
            fields[key.strip()] = value.strip().strip('"').strip("'")
        name = fields.get("name", "")
        description = fields.get("description", "")
        if name != path.parent.name or not NAME.fullmatch(name):
            errors.append(f"{path.relative_to(ROOT)}: invalid/mismatched skill name")
        if not description:
            errors.append(f"{path.relative_to(ROOT)}: description is required")

    combined = "\n".join(
        p.read_text(encoding="utf-8")
        for p in [ROOT / "AGENTS.md", ROOT / "README.md"]
        if p.is_file()
    )
    for marker in [".harness/project.yaml", "pinned Harness revision", "project binding"]:
        if marker in combined:
            errors.append(f"Harness root guidance must not require hard project coupling: {marker}")

    if errors:
        print("Harness validation failed:", file=sys.stderr)
        for item in errors:
            print(f"- {item}", file=sys.stderr)
        return 1

    print("Harness validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
