#!/usr/bin/env python3
"""Validate the active agent-facing Harness layer."""
from __future__ import annotations

import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from harness import CoreError  # noqa: E402
from target_state import validate_profile  # noqa: E402


def _skill_files(namespace: str) -> list[Path]:
    return sorted((ROOT / "skills" / namespace).glob("*/SKILL.md"))


def _validate_frontmatter(path: Path, text: str, errors: list[str]) -> None:
    if not text.startswith("---\n"):
        errors.append(f"skill missing frontmatter: {path.relative_to(ROOT)}")
        return
    end = text.find("\n---\n", 4)
    if end < 0:
        errors.append(f"skill has unterminated frontmatter: {path.relative_to(ROOT)}")
        return
    try:
        metadata = yaml.safe_load(text[4:end])
    except yaml.YAMLError as exc:
        errors.append(f"skill invalid frontmatter {path.relative_to(ROOT)}: {exc}")
        return
    if not isinstance(metadata, dict):
        errors.append(f"skill frontmatter must be a mapping: {path.relative_to(ROOT)}")
        return
    for key in ("name", "description"):
        if not isinstance(metadata.get(key), str) or not metadata[key].strip():
            errors.append(f"skill frontmatter missing {key}: {path.relative_to(ROOT)}")


def _require(path: Path, text: str, fragments: tuple[str, ...], errors: list[str]) -> None:
    for fragment in fragments:
        if fragment not in text:
            errors.append(
                f"skill {path.relative_to(ROOT)} missing contract fragment: {fragment}"
            )


def _validate_agent_skills(errors: list[str]) -> int:
    paths = _skill_files("agent")
    if not paths:
        errors.append("no active agent skills under skills/agent/**")
        return 0
    for path in paths:
        text = path.read_text(encoding="utf-8")
        _validate_frontmatter(path, text, errors)
        _require(path, text, ("## Trigger", "## Inputs", "## Procedure"), errors)
    return len(paths)


def _validate_artifact_skills(errors: list[str]) -> int:
    decision_governed = {
        "application-design",
        "domain-model",
        "implementation-design",
        "system-architecture",
    }
    paths = _skill_files("artifacts")
    if not paths:
        errors.append("no active artifact skills under skills/artifacts/**")
        return 0
    for path in paths:
        text = path.read_text(encoding="utf-8")
        _validate_frontmatter(path, text, errors)
        _require(
            path,
            text,
            (
                "## Trigger",
                "## Inputs",
                "## Read boundary",
                "## Procedure",
                "## Stop conditions",
                "## Registration",
                "## Human projection",
            ),
            errors,
        )
        if "## Output schema" not in text and "## Output contract" not in text:
            errors.append(
                f"artifact skill {path.relative_to(ROOT)} must define Output schema or Output contract"
            )
        if "acceptance" not in text.lower():
            errors.append(
                f"artifact skill {path.relative_to(ROOT)} must define acceptance checks"
            )
        if path.parent.name in decision_governed:
            _require(path, text, ("## Decision exploration",), errors)
    return len(paths)


def _validate_starter_profile(errors: list[str]) -> None:
    starter = ROOT / "profiles/software-application-design-v0.yaml"
    if not starter.is_file():
        errors.append("missing software application starter profile")
        return
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
            raise CoreError(
                f"unexpected starter profile dependency chain: {actual!r}"
            )
    except Exception as exc:
        errors.append(f"starter profile: {exc}")


def main() -> int:
    errors: list[str] = []

    agent_count = _validate_agent_skills(errors)
    artifact_count = _validate_artifact_skills(errors)

    workbench = ROOT / "docs/design/agent-artifact-workbench-v0.md"
    if not workbench.is_file():
        errors.append("missing agent artifact workbench contract")

    _validate_starter_profile(errors)

    if errors:
        print("Harness agent-layer validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(
        "Harness agent-layer validation passed "
        f"({agent_count} agent skills, {artifact_count} artifact skills)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
