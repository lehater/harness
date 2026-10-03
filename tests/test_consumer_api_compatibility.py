#!/usr/bin/env python3
"""Cross-revision Consumer API v1 compatibility acceptance."""
from __future__ import annotations

import copy
import re
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
BASELINE = ROOT / "spec/distribution/consumer-api-v1-baseline.yaml"


class CompatibilityError(AssertionError):
    pass


def load_yaml(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise CompatibilityError(f"{path} must contain a mapping")
    return value


def current_identities(root: Path) -> dict[str, Any]:
    definition = load_yaml(root / "spec/distribution/consumer-pack-v1.yaml")
    operations = load_yaml(root / "skills/consumer-operation-registry-v0.yaml")
    methods = load_yaml(root / "skills/consumer-method-registry-v0.yaml")
    artifacts = load_yaml(root / "skills/artifact-skill-registry-v0.yaml")

    exact_files = set(definition.get("exact_files", []))
    runtime_modules = {
        module
        for module, relative in {
            "harness.application.consumer_pack": "src/harness/application/consumer_pack.py",
            "harness.application.skill_router": "src/harness/application/skill_router.py",
            "harness.application.scenario_suite": "src/harness/application/scenario_suite.py",
        }.items()
        if relative in exact_files
    }
    public_operations = {
        item["operation"]
        for item in operations.get("routes", [])
        if isinstance(item, dict) and item.get("exposure") == "public"
    }
    method_ids = {
        item["method"]
        for item in methods.get("routes", [])
        if isinstance(item, dict) and isinstance(item.get("method"), str)
    }
    artifact_kinds = {
        item["knowledge_kind"]
        for item in artifacts.get("routes", [])
        if isinstance(item, dict) and isinstance(item.get("knowledge_kind"), str)
    }
    return {
        "consumer_api": definition.get("consumer_api"),
        "runtime_modules": runtime_modules,
        "public_operations": public_operations,
        "methods": method_ids,
        "artifact_kinds": artifact_kinds,
    }


def validate_compatible(baseline: dict[str, Any], current: dict[str, Any]) -> None:
    if baseline.get("version") != 1 or baseline.get("kind") != "harness-consumer-api-baseline":
        raise CompatibilityError("invalid Consumer API compatibility baseline")
    revision = baseline.get("baseline_revision")
    if not isinstance(revision, str) or not re.fullmatch(r"[0-9a-f]{40}", revision):
        raise CompatibilityError("baseline_revision must be an immutable 40-hex commit")
    if baseline.get("breaking_change_policy") != "new-consumer-api":
        raise CompatibilityError("breaking Consumer identity changes must require a new consumer_api")
    if current.get("consumer_api") != baseline.get("consumer_api"):
        raise CompatibilityError("current Consumer Pack no longer implements the baseline consumer_api")

    published = baseline.get("published_identities")
    if not isinstance(published, dict):
        raise CompatibilityError("published_identities must be a mapping")
    for surface in ("runtime_modules", "public_operations", "methods", "artifact_kinds"):
        expected = published.get(surface)
        if not isinstance(expected, list) or not expected or not all(
            isinstance(item, str) and item for item in expected
        ):
            raise CompatibilityError(f"baseline {surface} must be non-empty string identities")
        if len(expected) != len(set(expected)):
            raise CompatibilityError(f"baseline {surface} contains duplicate identities")
        missing = sorted(set(expected) - set(current.get(surface, set())))
        if missing:
            raise CompatibilityError(
                f"Consumer API {baseline['consumer_api']} removed published {surface}: "
                + ", ".join(missing)
                + "; preserve the v1 identity or introduce a new consumer_api"
            )


baseline = load_yaml(BASELINE)
current = current_identities(ROOT)
validate_compatible(baseline, current)

# Additive evolution is compatible: PR #180 added an internal operation and Pack file
# without changing any published v1 identity.
additive = copy.deepcopy(current)
additive["public_operations"] = set(additive["public_operations"]) | {"future-public-operation"}
validate_compatible(baseline, additive)

# Renames/removals under the same API identity fail closed.
for surface in ("runtime_modules", "public_operations", "methods", "artifact_kinds"):
    mutated = copy.deepcopy(current)
    victim = next(iter(baseline["published_identities"][surface]))
    mutated[surface] = set(mutated[surface]) - {victim}
    try:
        validate_compatible(baseline, mutated)
    except CompatibilityError as exc:
        assert victim in str(exc), (surface, exc)
    else:
        raise AssertionError(f"published {surface} removal was accepted")

wrong_api = copy.deepcopy(current)
wrong_api["consumer_api"] = "v2"
try:
    validate_compatible(baseline, wrong_api)
except CompatibilityError:
    pass
else:
    raise AssertionError("same baseline was accepted under a different consumer_api")

print(
    "Consumer API v1 cross-revision compatibility: PASS "
    f"(baseline={baseline['baseline_revision']}; current identities preserved)"
)
