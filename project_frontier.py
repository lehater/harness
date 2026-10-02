#!/usr/bin/env python3
"""Compose one application-level next-action frontier from Harness read models."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml

from harness.project_model.core import CoreError


DECISION_STATUSES = {
    "READY",
    "FAILED_VALIDATION",
    "BLOCKED",
    "WAITING",
    "INCOMPLETE",
    "COMPLETE",
}


def _load(path: str | Path) -> dict[str, Any]:
    value = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise CoreError(f"{path} must contain a mapping")
    return value


def _require_kind(
    document: dict[str, Any],
    kind: str,
    *,
    target_field: str | None = None,
    target: str | None = None,
) -> None:
    if document.get("version") != 1 or document.get("kind") != kind:
        raise CoreError(f"unexpected {kind} read model")
    if target_field is not None and target is not None:
        actual = document.get(target_field)
        if actual != target:
            raise CoreError(
                f"{kind} target mismatch: {actual!r} != {target!r}"
            )


def _routed_instruction_contracts(route: dict[str, Any]) -> list[str]:
    contracts = route.get("instruction_contracts")
    if (
        not isinstance(contracts, list)
        or not contracts
        or any(not isinstance(item, str) or not item for item in contracts)
    ):
        raise CoreError(
            "routed execution path requires non-empty instruction_contracts"
        )
    return list(contracts)


def _routing_index(
    create_routing: dict[str, Any] | None,
) -> dict[str, dict[str, Any]]:
    if create_routing is None:
        return {}
    result: dict[str, dict[str, Any]] = {}
    for bucket, status in (("routed", "ROUTED"), ("unrouted", "UNROUTED")):
        for item in create_routing.get(bucket, []) or []:
            if not isinstance(item, dict):
                continue
            for capability in item.get("capabilities", []) or []:
                if not isinstance(capability, str) or not capability:
                    continue
                route = {
                    "status": status,
                    **(
                        {"skill": item["skill"]}
                        if isinstance(item.get("skill"), str)
                        else {}
                    ),
                    **(
                        {
                            "instruction_contracts": _routed_instruction_contracts(
                                item
                            )
                        }
                        if status == "ROUTED"
                        else {}
                    ),
                    **(
                        {"reason": item["reason"]}
                        if isinstance(item.get("reason"), str)
                        else {}
                    ),
                }
                result[capability] = route
    return result


def compose_project_frontier(
    *,
    target: str,
    decision_roadmap: dict[str, Any],
    semantic_closure: dict[str, Any],
    engineering_coverage: dict[str, Any],
    create_routing: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Normalize peer projections without becoming another truth owner.

    Decision Roadmap owns capability execution readiness. Semantic Closure owns
    strict admission/currentness. Engineering Coverage owns applicability and
    completeness work. This function only removes cross-layer duplication and
    exposes one deterministic application frontier.
    """
    if not isinstance(target, str) or not target:
        raise CoreError("project frontier target is required")
    _require_kind(
        decision_roadmap,
        "harness-decision-roadmap",
        target_field="target",
        target=target,
    )
    _require_kind(
        semantic_closure,
        "harness-semantic-closure-evaluation",
        target_field="target",
        target=target,
    )
    _require_kind(
        engineering_coverage,
        "harness-engineering-coverage-evaluation",
        target_field="consumer",
        target=target,
    )

    decision_status = decision_roadmap.get("frontier_status")
    if decision_status not in DECISION_STATUSES:
        raise CoreError(
            "decision roadmap frontier_status must be one of "
            + ", ".join(sorted(DECISION_STATUSES))
        )

    routes = _routing_index(create_routing)
    next_actions: list[dict[str, Any]] = []
    blocked: list[dict[str, Any]] = []
    waiting: list[dict[str, Any]] = []
    gaps: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []

    capability_execution: dict[str, dict[str, Any]] = {}
    for item in decision_roadmap.get("ready", []) or []:
        capability = item["capability"]
        action = {
            "source": "DECISION_ROADMAP",
            "action": "RUN_CAPABILITY_PIPELINE",
            "capability": capability,
            "authority": item.get("authority"),
            "reason": item.get("reason"),
            "decision_request_mode": item.get("decision_request_mode"),
            "pipeline": list(item.get("pipeline", []) or []),
        }
        if capability in routes:
            action["execution_route"] = routes[capability]
        capability_execution[capability] = action
        next_actions.append(action)

    for item in decision_roadmap.get("failed_validation", []) or []:
        failures.append({"source": "DECISION_ROADMAP", **item})
    for item in decision_roadmap.get("blocked", []) or []:
        blocked.append({"source": "DECISION_ROADMAP", **item})
    for item in decision_roadmap.get("waiting_upstream", []) or []:
        waiting.append({"source": "DECISION_ROADMAP", **item})
    for item in decision_roadmap.get("lifecycle_gaps", []) or []:
        gaps.append({"source": "DECISION_ROADMAP", **item})

    for item in semantic_closure.get("question_frontier", []) or []:
        blocked.append({"source": "SEMANTIC_CLOSURE", **item})

    for item in semantic_closure.get("semantic_gaps", []) or []:
        capability = item.get("capability")
        code = item.get("code")
        if capability in capability_execution:
            capability_execution[capability].setdefault(
                "semantic_requirements", []
            ).append(code)
            continue
        if code == "SEMANTIC_QUESTION":
            blocked.append({"source": "SEMANTIC_CLOSURE", **item})
        elif code == "SEMANTIC_ADMISSION_REQUIRED":
            next_actions.append(
                {
                    "source": "SEMANTIC_CLOSURE",
                    "action": "VALIDATE_SEMANTICS",
                    **item,
                }
            )
        else:
            gaps.append({"source": "SEMANTIC_CLOSURE", **item})

    for item in semantic_closure.get("currentness_gaps", []) or []:
        capability = item.get("capability")
        if capability in capability_execution:
            capability_execution[capability].setdefault(
                "currentness_requirements", []
            ).append(item.get("state"))
            continue
        state = item.get("state")
        if state == "STALE":
            next_actions.append(
                {
                    "source": "SEMANTIC_CLOSURE",
                    "action": "REVALIDATE_SEMANTICS",
                    **item,
                }
            )
        else:
            gaps.append({"source": "SEMANTIC_CLOSURE", **item})

    for item in semantic_closure.get("pending", []) or []:
        waiting.append({"source": "SEMANTIC_CLOSURE", **item})

    for item in engineering_coverage.get("question_frontier", []) or []:
        blocked.append({"source": "ENGINEERING_COVERAGE", **item})

    capability_coverage: dict[str, list[dict[str, Any]]] = {}
    for item in engineering_coverage.get("work_items", []) or []:
        execution_route = item.get("execution_route")
        if (
            isinstance(execution_route, dict)
            and execution_route.get("status") == "ROUTED"
        ):
            _routed_instruction_contracts(execution_route)
        action = item.get("action")
        capability = item.get("capability")
        if (
            isinstance(capability, str)
            and capability in capability_execution
            and action in {
                "PRODUCE_CAPABILITY",
                "VALIDATE_SEMANTICS",
                "REVALIDATE_SEMANTICS",
            }
        ):
            capability_coverage.setdefault(capability, []).append(item)
            continue
        if action == "RESOLVE_QUESTIONS":
            blocked.append({"source": "ENGINEERING_COVERAGE", **item})
        elif action == "WAIT_FOR_PREREQUISITES":
            waiting.append({"source": "ENGINEERING_COVERAGE", **item})
        else:
            next_actions.append({"source": "ENGINEERING_COVERAGE", **item})

    for capability, items in capability_coverage.items():
        capability_execution[capability]["coverage_requirements"] = items

    def sort_key(item: dict[str, Any]) -> tuple[str, str, str, str]:
        return (
            str(item.get("source", "")),
            str(item.get("action", item.get("state", ""))),
            str(item.get("capability", item.get("concern", ""))),
            str(item.get("authority", "")),
        )

    next_actions.sort(key=sort_key)
    blocked.sort(key=sort_key)
    waiting.sort(key=sort_key)
    gaps.sort(key=sort_key)
    failures.sort(key=sort_key)

    if next_actions:
        status = "READY"
    elif failures:
        status = "FAILED_VALIDATION"
    elif blocked:
        status = "BLOCKED"
    elif gaps:
        status = "INCOMPLETE"
    elif waiting:
        status = "WAITING"
    elif (
        decision_status == "COMPLETE"
        and semantic_closure.get("status") == "COMPLETE"
        and engineering_coverage.get("completion_ready") is True
    ):
        status = "COMPLETE"
    else:
        status = "INCOMPLETE"
        gaps.append(
            {
                "source": "PROJECT_FRONTIER",
                "code": "CROSS_LAYER_CLOSURE_INCOMPLETE",
                "decision_status": decision_status,
                "semantic_status": semantic_closure.get("status"),
                "coverage_completion_ready": engineering_coverage.get(
                    "completion_ready"
                ),
            }
        )

    return {
        "version": 1,
        "kind": "harness-project-frontier",
        "target": target,
        "status": status,
        "next_actions": next_actions,
        "failed_validation": failures,
        "blocked": blocked,
        "waiting": waiting,
        "gaps": gaps,
        "source_status": {
            "decision": decision_status,
            "semantic": semantic_closure.get("status"),
            "structural": semantic_closure.get("structural_status"),
            "coverage_completion_ready": engineering_coverage.get(
                "completion_ready"
            ),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Compose Harness project next-action frontier"
    )
    parser.add_argument("target")
    parser.add_argument("decision_roadmap")
    parser.add_argument("semantic_closure")
    parser.add_argument("engineering_coverage")
    parser.add_argument("--create-routing")
    args = parser.parse_args()
    value = compose_project_frontier(
        target=args.target,
        decision_roadmap=_load(args.decision_roadmap),
        semantic_closure=_load(args.semantic_closure),
        engineering_coverage=_load(args.engineering_coverage),
        create_routing=(
            _load(args.create_routing) if args.create_routing else None
        ),
    )
    print(json.dumps(value, indent=2, sort_keys=False))
    return 0 if value["status"] == "COMPLETE" else 1


if __name__ == "__main__":
    raise SystemExit(main())
