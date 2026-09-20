#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[2]
SKILL_REGISTRY = ROOT / "skills/artifact-skill-registry-v0.yaml"
PROFILE_REGISTRY = ROOT / "docs/research/artifact-schema-registry-experiment.yaml"
OUTPUT_REGISTRY = ROOT / "docs/research/skill-output-profile-registry-experiment.yaml"


class RegistryError(ValueError):
    pass


def load(path: Path):
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RegistryError(f"{path}: expected mapping")
    return value


skills = load(SKILL_REGISTRY)
profiles = load(PROFILE_REGISTRY)
outputs = load(OUTPUT_REGISTRY)

active_routes = {}
for route in skills.get("routes", []):
    kind = route.get("knowledge_kind")
    skill_path = route.get("skill", "")
    if not kind or not skill_path:
        raise RegistryError("active skill route requires knowledge_kind and skill")
    skill_name = Path(skill_path).parent.name
    if kind in active_routes:
        raise RegistryError(f"duplicate active knowledge_kind: {kind}")
    active_routes[kind] = skill_name

profile_ids = {item.get("id") for item in profiles.get("profiles", []) if isinstance(item, dict)}
if None in profile_ids:
    raise RegistryError("profile id is required")

seen_skills = set()
for item in outputs.get("skills", []):
    skill = item.get("skill")
    kind = item.get("knowledge_kind")
    if not skill or not kind:
        raise RegistryError("output registry entry requires skill and knowledge_kind")
    if skill in seen_skills:
        raise RegistryError(f"duplicate output skill: {skill}")
    seen_skills.add(skill)
    if active_routes.get(kind) != skill:
        raise RegistryError(
            f"{skill}: knowledge_kind {kind} does not match active routing "
            f"{active_routes.get(kind)!r}"
        )
    declared = item.get("outputs", [])
    if not isinstance(declared, list) or not declared:
        raise RegistryError(f"{skill}: at least one output profile is required")
    for output in declared:
        if not isinstance(output, dict):
            raise RegistryError(f"{skill}: output must be mapping")
        profile = output.get("profile")
        mode = output.get("mode")
        if profile != "project-native" and profile not in profile_ids:
            raise RegistryError(f"{skill}: unknown profile {profile}")
        if mode not in {"harness-managed", "standard-native", "project-native"}:
            raise RegistryError(f"{skill}/{profile}: unsupported mode {mode}")

print(
    "skill-output profile registry PASS "
    f"({len(seen_skills)} skills, {len(profile_ids)} registered profiles)"
)
