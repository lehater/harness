#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml

APPLICABILITY = {"REQUIRED", "NOT_APPLICABLE", "DEFERRED", "QUESTION"}


def load_yaml(path: str | Path) -> dict[str, Any]:
    with open(path, "r", encoding="utf-8") as stream:
        data = yaml.safe_load(stream)
    if not isinstance(data, dict):
        raise ValueError("repository realization must be a YAML mapping")
    return data


def evaluate(model: dict[str, Any]) -> dict[str, Any]:
    errors: list[dict[str, str]] = []

    def error(code: str, path: str, message: str) -> None:
        errors.append({"code": code, "path": path, "message": message})

    if model.get("kind") != "repository-realization-design":
        error("INVALID_KIND", "kind", "kind must be repository-realization-design")

    modules = model.get("module_realizations", [])
    if not isinstance(modules, list) or not modules:
        error("MODULE_REALIZATION_MISSING", "module_realizations", "at least one physical module realization is required")
    else:
        for i, item in enumerate(modules):
            if not isinstance(item, dict):
                error("INVALID_MODULE", f"module_realizations[{i}]", "module realization must be a mapping")
                continue
            if not item.get("semantic_owner"):
                error("MODULE_OWNER_MISSING", f"module_realizations[{i}].semantic_owner", "semantic owner is required")
            if not item.get("physical_root"):
                error("MODULE_ROOT_MISSING", f"module_realizations[{i}].physical_root", "physical root is required")

    for i, item in enumerate(model.get("dependency_rules", [])):
        if not isinstance(item, dict) or not item.get("rule"):
            error("DEPENDENCY_RULE_INVALID", f"dependency_rules[{i}]", "dependency rule text/id is required")
            continue
        if not item.get("enforcement"):
            error("DEPENDENCY_ENFORCEMENT_MISSING", f"dependency_rules[{i}].enforcement", "architectural dependency rules require mechanical enforcement")

    obligations = model.get("obligations", [])
    if not isinstance(obligations, list) or not obligations:
        error("OBLIGATION_INVENTORY_MISSING", "obligations", "explicit obligation applicability inventory is required")
    else:
        ids: set[str] = set()
        for i, item in enumerate(obligations):
            path = f"obligations[{i}]"
            if not isinstance(item, dict):
                error("INVALID_OBLIGATION", path, "obligation must be a mapping")
                continue
            oid = item.get("id")
            if not oid:
                error("OBLIGATION_ID_MISSING", f"{path}.id", "obligation id is required")
            elif oid in ids:
                error("DUPLICATE_OBLIGATION", f"{path}.id", f"duplicate obligation {oid}")
            else:
                ids.add(oid)
            state = item.get("applicability")
            if state not in APPLICABILITY:
                error("INVALID_APPLICABILITY", f"{path}.applicability", f"expected one of {sorted(APPLICABILITY)}")
            elif state == "REQUIRED" and not item.get("enforcement"):
                error("REQUIRED_ENFORCEMENT_MISSING", f"{path}.enforcement", "required obligation needs deterministic enforcement")
            elif state in {"NOT_APPLICABLE", "DEFERRED"} and not item.get("rationale"):
                error("DISPOSITION_RATIONALE_MISSING", f"{path}.rationale", f"{state} requires rationale")
            elif state == "QUESTION":
                error("UNRESOLVED_QUESTION", path, "QUESTION blocks repository-realization completeness")

    for i, item in enumerate(model.get("generated_artifacts", [])):
        path = f"generated_artifacts[{i}]"
        if not isinstance(item, dict):
            error("INVALID_GENERATED_ARTIFACT", path, "generated artifact must be a mapping")
            continue
        if not item.get("source_of_truth"):
            error("GENERATED_SOURCE_MISSING", f"{path}.source_of_truth", "generated artifact needs canonical source")
        if not item.get("regenerate"):
            error("GENERATED_REGEN_MISSING", f"{path}.regenerate", "generated artifact needs deterministic regeneration command/mechanism")

    environment = model.get("environment")
    if not isinstance(environment, dict):
        error("ENVIRONMENT_MISSING", "environment", "dependency/tool environment realization is required")
    else:
        state = environment.get("reproducibility", "REQUIRED")
        if state == "REQUIRED" and not environment.get("lock_or_equivalent"):
            error("REPRODUCIBILITY_MISSING", "environment.lock_or_equivalent", "required reproducibility needs a lock/resolution equivalent")
        elif state in {"NOT_APPLICABLE", "DEFERRED"} and not environment.get("rationale"):
            error("REPRODUCIBILITY_RATIONALE_MISSING", "environment.rationale", f"{state} reproducibility needs rationale")

    gate_policy = model.get("gate_policy")
    gates = model.get("quality_gates", [])
    if gate_policy is None:
        gate_state = "REQUIRED" if gates else "QUESTION"
    elif not isinstance(gate_policy, dict):
        gate_state = None
        error("INVALID_GATE_POLICY", "gate_policy", "gate policy must be a mapping")
    else:
        gate_state = gate_policy.get("applicability")
        if gate_state not in APPLICABILITY:
            error("INVALID_GATE_APPLICABILITY", "gate_policy.applicability", f"expected one of {sorted(APPLICABILITY)}")
        elif gate_state in {"NOT_APPLICABLE", "DEFERRED"} and not gate_policy.get("rationale"):
            error("GATE_DISPOSITION_RATIONALE_MISSING", "gate_policy.rationale", f"{gate_state} gate policy requires rationale")
        elif gate_state == "QUESTION":
            error("UNRESOLVED_GATE_QUESTION", "gate_policy", "QUESTION blocks repository-realization completeness")

    blocking = [g for g in gates if isinstance(g, dict) and g.get("blocking") is True]
    if gate_state == "REQUIRED" and not blocking:
        error("AUTHORITATIVE_GATE_MISSING", "quality_gates", "required merge/release gating needs at least one authoritative blocking gate")
    if gate_state in {"NOT_APPLICABLE", "DEFERRED"} and gates:
        error("GATE_DISPOSITION_CONFLICT", "quality_gates", f"{gate_state} gate policy cannot declare active quality gates")

    for i, gate in enumerate(gates):
        if not isinstance(gate, dict):
            error("INVALID_GATE", f"quality_gates[{i}]", "gate must be a mapping")
            continue
        if not gate.get("command"):
            error("GATE_COMMAND_MISSING", f"quality_gates[{i}].command", "gate needs a deterministic command/check entrypoint")
        if not gate.get("trigger"):
            error("GATE_TRIGGER_MISSING", f"quality_gates[{i}].trigger", "gate trigger is required")

    return {
        "kind": "harness-repository-realization-evaluation",
        "id": model.get("id"),
        "complete": not errors,
        "error_count": len(errors),
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate repository-realization design completeness.")
    parser.add_argument("artifact")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = evaluate(load_yaml(args.artifact))
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("COMPLETE" if result["complete"] else "INCOMPLETE")
        for issue in result["errors"]:
            print(f'{issue["code"]}: {issue["path"]}: {issue["message"]}')
    return 0 if result["complete"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
