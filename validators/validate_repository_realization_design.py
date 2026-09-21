#!/usr/bin/env python3
from pathlib import Path
import sys
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from repository_realization import evaluate

def load(path):
    with open(path, "r", encoding="utf-8") as stream:
        return yaml.safe_load(stream)

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

    nutrition_result = evaluate(nutrition)
    napms_result = evaluate(napms)
    assert nutrition_result["complete"], nutrition_result
    assert napms_result["complete"], napms_result

    assert nutrition["repository_topology"] != napms["repository_topology"]
    assert len(nutrition["module_realizations"]) > len(napms["module_realizations"])

    broken = dict(nutrition)
    broken["obligations"] = [
        {"id": "architecture-dependencies", "applicability": "REQUIRED"}
    ]
    broken_result = evaluate(broken)
    assert not broken_result["complete"]
    assert "REQUIRED_ENFORCEMENT_MISSING" in {
        issue["code"] for issue in broken_result["errors"]
    }

    questioned = dict(nutrition)
    questioned["obligations"] = [
        {"id": "tooling-choice", "applicability": "QUESTION"}
    ]
    questioned_result = evaluate(questioned)
    assert not questioned_result["complete"]
    assert "UNRESOLVED_QUESTION" in {
        issue["code"] for issue in questioned_result["errors"]
    }

    print("repository realization design: ok (2 structurally different pilots + negative completeness cases)")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
