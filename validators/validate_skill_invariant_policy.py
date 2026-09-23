#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from agent_router import validate_skill_registry
from semantic_admission import knowledge_contract_index


def load(path: Path):
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise AssertionError(f"{path} must contain a mapping")
    return value


def main() -> int:
    registry = load(ROOT / "skills/artifact-skill-registry-v0.yaml")
    validate_skill_registry(registry, root=ROOT)
    contracts_doc = load(
        ROOT / "spec/semantic-acceptance/knowledge-kind-contracts-v1.yaml"
    )
    contracts = knowledge_contract_index(contracts_doc)
    policy = load(
        ROOT / "spec/semantic-acceptance/skill-invariant-policy-v1.yaml"
    )

    assert policy.get("version") == 1
    assert policy.get("kind") == "harness-skill-invariant-policy"

    active = {
        path.relative_to(ROOT).as_posix()
        for path in (ROOT / "skills/artifacts").glob("*/SKILL.md")
    }
    routes = {
        item["knowledge_kind"]: item["skill"]
        for item in registry.get("routes", []) or []
    }
    enforced = {
        item["knowledge_kind"]: item["skill"]
        for item in policy.get("enforced", []) or []
    }
    judgement = {
        item["skill"]: item.get("rationale")
        for item in policy.get("judgement_only", []) or []
    }

    assert routes == enforced, (routes, enforced)
    assert set(routes) == set(contracts), (
        sorted(set(routes) - set(contracts)),
        sorted(set(contracts) - set(routes)),
    )
    assert not (set(enforced.values()) & set(judgement))
    assert active == set(enforced.values()) | set(judgement), (
        sorted(active - (set(enforced.values()) | set(judgement))),
        sorted((set(enforced.values()) | set(judgement)) - active),
    )
    assert all(isinstance(value, str) and value.strip() for value in judgement.values())

    product_checks = set(
        contracts["product-requirements"].get("required_review_checks", []) or []
    )
    assert "observable-product-level" in product_checks
    assert "no-downstream-design-promotion" in product_checks

    print(
        "skill invariant policy: PASS "
        f"({len(enforced)} enforced routes, {len(judgement)} judgement-only skills)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
