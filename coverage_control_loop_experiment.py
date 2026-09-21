#!/usr/bin/env python3
"""Research-only end-to-end Engineering Coverage control loop."""
from __future__ import annotations
import argparse
from pathlib import Path
from typing import Any
import yaml

from concern_activation_experiment import derive_activation
from coverage_planner_experiment import derive_plan


def load(path: str) -> dict[str, Any]:
    value = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a mapping")
    return value


def evaluate(
    activation_policy: dict[str, Any],
    proof_contract: dict[str, Any],
    role_contract: dict[str, Any],
    project_roles: dict[str, Any],
    semantic_claim_bindings: dict[str, Any],
    activation_overlay: dict[str, Any],
    project_docs: list[dict[str, Any]],
) -> dict[str, Any]:
    activation = derive_activation(
        activation_policy,
        project_roles,
        activation_overlay,
        project_docs,
    )

    target_consumer = activation.get("consumer")
    decisions = []
    for item in activation_overlay.get("decisions", []) or []:
        consumers = item.get("consumers", []) or []
        if consumers and target_consumer is not None and target_consumer not in consumers:
            continue
        decisions.append(item)

    planner_overlay = {
        "project": activation_overlay.get("project"),
        "scope": activation_overlay.get("scope"),
        "required": [row["concern"] for row in activation["rows"]],
        "decisions": decisions,
    }

    plan = derive_plan(
        proof_contract,
        role_contract,
        project_roles,
        semantic_claim_bindings,
        planner_overlay,
        project_docs,
    )

    activation_by_concern = {
        row["concern"]: row["provenance"]
        for row in activation["rows"]
    }
    for row in plan["rows"]:
        row["activation_provenance"] = activation_by_concern.get(row["concern"], [])

    return {
        "version": 1,
        "kind": "harness-derived-engineering-coverage-control",
        "project": activation_overlay.get("project"),
        "scope": activation_overlay.get("scope"),
        "consumer": target_consumer,
        "completion_ready": plan["completion_ready"],
        "activated_count": activation["activated_count"],
        "summary": plan["summary"],
        "rows": plan["rows"],
    }


def main() -> int:
    p=argparse.ArgumentParser()
    p.add_argument("activation_policy")
    p.add_argument("proof_contract")
    p.add_argument("role_contract")
    p.add_argument("project_roles")
    p.add_argument("semantic_claim_bindings")
    p.add_argument("activation_overlay")
    p.add_argument("project_docs", nargs="+")
    args=p.parse_args()

    result=evaluate(
        load(args.activation_policy),
        load(args.proof_contract),
        load(args.role_contract),
        load(args.project_roles),
        load(args.semantic_claim_bindings),
        load(args.activation_overlay),
        [load(x) for x in args.project_docs],
    )
    print(yaml.safe_dump(result, sort_keys=False, allow_unicode=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
