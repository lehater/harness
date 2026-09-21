#!/usr/bin/env python3
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]

def load(path):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def main():
    contract = load(ROOT / "spec/repository-realization/contract-v1.yaml")
    nutrition = load(ROOT / "spec/repository-realization/pilots/nutrition-management.yaml")
    napms = load(ROOT / "spec/repository-realization/pilots/napms.yaml")

    assert contract["ownership"]["authority"] == "IMPLEMENTATION-DESIGN"
    assert contract["ownership"]["knowledge_kind"] == "implementation-design"
    assert "folder-layout" not in contract["principles"]
    assert {"module-realization", "dependency-enforcement", "ci-quality-gates"} <= set(contract["facets"])
    assert contract["applicability_states"] == ["REQUIRED", "NOT_APPLICABLE", "DEFERRED", "QUESTION"]
    assert "no-unresolved-question-remains" in contract["completeness"]

    for pilot in (nutrition, napms):
        assert pilot["result"] == "PASS"
        for item in pilot["obligations"]:
            assert item["applicability"] in contract["applicability_states"]
            if item["applicability"] == "REQUIRED":
                assert item.get("enforcement")
            if item["applicability"] in {"NOT_APPLICABLE", "DEFERRED"}:
                assert item.get("rationale")
        assert pilot["decisions"]["authoritative_gate"] == "pull-request-ci"

    assert nutrition["decisions"]["repository_topology"] != napms["decisions"]["repository_topology"]
    print("repository realization design: ok (2 structurally different pilots)")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
