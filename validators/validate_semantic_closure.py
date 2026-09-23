#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import copy
import sys
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from semantic_closure import evaluate_semantic_closure


GRAPH = {
    "version": 1,
    "kind": "harness-engineering-graph",
    "id": "CLOSURE",
    "authorities": [
        {
            "id": "DISCOVERY",
            "responsibility": "Own needs.",
            "boundary": {
                "semantic_cohesion": "Needs.",
                "independent_change": "Needs change.",
                "public_contract": "Needs.",
            },
            "produces": [
                {
                    "capability": "needs",
                    "knowledge_kind": "user-needs",
                    "requires": [],
                }
            ],
        },
        {
            "id": "PRODUCT",
            "responsibility": "Own requirements.",
            "boundary": {
                "semantic_cohesion": "Requirements.",
                "independent_change": "Requirements change.",
                "public_contract": "Requirements.",
            },
            "produces": [
                {
                    "capability": "requirements",
                    "knowledge_kind": "product-requirements",
                    "requires": ["needs"],
                }
            ],
        },
        {
            "id": "DOMAIN",
            "responsibility": "Own domain.",
            "boundary": {
                "semantic_cohesion": "Domain.",
                "independent_change": "Domain changes.",
                "public_contract": "Domain.",
            },
            "produces": [
                {
                    "capability": "domain",
                    "knowledge_kind": "domain-model",
                    "requires": ["requirements"],
                }
            ],
        },
    ],
    "consumers": [
        {
            "id": "IMPLEMENTATION",
            "purpose": "Implement.",
            "requires": ["domain"],
        }
    ],
    "terminal_capabilities": [],
}

MODEL = {
    "artifacts": [
        {
            "id": "NEEDS",
            "authority": "DISCOVERY",
            "path": "needs.yaml",
            "provides": ["needs"],
            "depends_on": [],
        },
        {
            "id": "REQ",
            "authority": "PRODUCT",
            "path": "requirements.yaml",
            "provides": ["requirements"],
            "depends_on": ["NEEDS"],
        },
        {
            "id": "DOMAIN",
            "authority": "DOMAIN",
            "path": "domain.yaml",
            "provides": ["domain"],
            "depends_on": ["REQ"],
        },
    ],
    "questions": [],
}

LIFECYCLE = {
    "version": 1,
    "kind": "harness-capability-lifecycle",
    "providers": [
        {
            "artifact": "NEEDS",
            "capability": "needs",
            "acceptance_id": "N1",
            "accepted_prerequisites": {},
        },
        {
            "artifact": "REQ",
            "capability": "requirements",
            "acceptance_id": "R1",
            "accepted_prerequisites": {"needs": "N1"},
        },
        {
            "artifact": "DOMAIN",
            "capability": "domain",
            "acceptance_id": "D1",
            "accepted_prerequisites": {"requirements": "R1"},
        },
    ],
}


def evaluation(artifact, capability, acceptance_id):
    return {
        "version": 1,
        "kind": "harness-artifact-semantic-evaluation",
        "artifact": artifact,
        "capability": capability,
        "status": "ACCEPTED",
        "obligations": {"expected": [], "satisfied": []},
        "findings": [],
        "semantic_claims": {"accepted": []},
        "admission": {
            "status": "ACCEPTED",
            "acceptance_id": acceptance_id,
        },
    }


EVALUATIONS = {
    "version": 1,
    "kind": "harness-semantic-evaluation-set",
    "semantic_evaluations": [
        evaluation("NEEDS", "needs", "N1"),
        evaluation("REQ", "requirements", "R1"),
        evaluation("DOMAIN", "domain", "D1"),
    ],
}


def load_registry():
    return yaml.safe_load(
        (ROOT / "skills/artifact-skill-registry-v0.yaml").read_text(
            encoding="utf-8"
        )
    )


def main() -> int:
    result = evaluate_semantic_closure(
        graph=GRAPH,
        model=MODEL,
        target="IMPLEMENTATION",
        skill_registry=load_registry(),
        semantic_evaluations=EVALUATIONS,
        lifecycle=LIFECYCLE,
    )
    assert result["status"] == "COMPLETE", result

    missing = copy.deepcopy(EVALUATIONS)
    missing["semantic_evaluations"] = [
        item
        for item in missing["semantic_evaluations"]
        if item["capability"] != "requirements"
    ]
    result = evaluate_semantic_closure(
        graph=GRAPH,
        model=MODEL,
        target="IMPLEMENTATION",
        skill_registry=load_registry(),
        semantic_evaluations=missing,
        lifecycle=LIFECYCLE,
    )
    assert result["status"] == "INCOMPLETE", result
    assert any(
        item["code"] == "SEMANTIC_ADMISSION_REQUIRED"
        for item in result["semantic_gaps"]
    )

    changed = copy.deepcopy(LIFECYCLE)
    changed["providers"][0]["acceptance_id"] = "N2"
    result = evaluate_semantic_closure(
        graph=GRAPH,
        model=MODEL,
        target="IMPLEMENTATION",
        skill_registry=load_registry(),
        semantic_evaluations=EVALUATIONS,
        lifecycle=changed,
    )
    assert result["status"] == "INCOMPLETE", result
    assert result["revalidate"], result
    assert result["revalidate"][0]["capability"] == "requirements", result

    legacy = copy.deepcopy(EVALUATIONS)
    legacy["semantic_evaluations"][1].pop("admission")
    result = evaluate_semantic_closure(
        graph=GRAPH,
        model=MODEL,
        target="IMPLEMENTATION",
        skill_registry=load_registry(),
        semantic_evaluations=legacy,
        lifecycle=LIFECYCLE,
    )
    assert result["status"] == "INCOMPLETE", result

    print("semantic closure: PASS (strict admission + lifecycle currentness)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
