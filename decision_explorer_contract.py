#!/usr/bin/env python3
"""Pure Decision Explorer request contract and binding validation."""
from __future__ import annotations

import hashlib
import json
from typing import Any

from harness import CoreError


def _canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )


def _request_id(payload: dict[str, Any]) -> str:
    digest = hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()
    return f"sha256:{digest}"


def build_decision_explorer_request(
    *,
    capability: str,
    knowledge_kind: str,
    authority: str,
    authority_context: dict[str, Any],
    contract: dict[str, Any] | None,
    axis_policies: dict[str, dict[str, str]] | None,
    prerequisite_baseline: dict[str, str],
    model: dict[str, Any],
    mode: str = "CREATE",
    current_provider_baseline: dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    """Build the candidate-free request from already-derived Decision inputs."""
    if contract is None or not contract.get("required") or axis_policies is None:
        return None
    if mode not in {"CREATE", "REVISION", "REDO"}:
        raise CoreError("decision option request mode must be CREATE, REVISION or REDO")
    if mode == "CREATE" and current_provider_baseline is not None:
        raise CoreError("CREATE decision option request cannot include current provider")
    if mode in {"REVISION", "REDO"} and current_provider_baseline is None:
        raise CoreError(f"{mode} decision option request requires current provider baseline")

    if authority_context.get("authority") != authority:
        raise CoreError("decision explorer Authority context mismatch")
    if capability not in (authority_context.get("selected_outputs", []) or []):
        raise CoreError("decision explorer capability is outside Authority context")

    inputs: list[dict[str, Any]] = []
    for bucket in ("input_artifacts", "supporting_input_artifacts"):
        for item in authority_context.get(bucket, []) or []:
            if not isinstance(item, dict):
                continue
            inputs.append(
                {
                    "id": item["id"],
                    "authority": item["authority"],
                    "path": item["path"],
                    "provides": sorted(item.get("provides", []) or []),
                }
            )
    if current_provider_baseline is not None:
        inputs.append(
            {
                "id": current_provider_baseline["id"],
                "authority": current_provider_baseline["authority"],
                "path": current_provider_baseline["path"],
                "provides": sorted(
                    current_provider_baseline.get("provides", []) or []
                ),
                "purpose": "CURRENT_ACCEPTED_BASELINE",
            }
        )

    inputs = sorted(
        {item["id"]: item for item in inputs}.values(),
        key=lambda item: item["id"],
    )

    axes = []
    for axis, axis_contract in contract["axes"].items():
        effective = axis_policies[axis]
        axes.append(
            {
                "axis": axis,
                "exploration": effective["exploration"],
                "material_dimensions": list(axis_contract["material_dimensions"]),
                "challenge_strategies": list(
                    axis_contract["challenge_strategies"]
                ),
                "minimum_probes": axis_contract["minimum_probes"],
            }
        )

    payload = {
        "version": 1,
        "kind": "harness-decision-explorer-request",
        "capability": capability,
        "knowledge_kind": knowledge_kind,
        "authority": authority,
        "mode": mode,
        "accepted_prerequisites": dict(sorted(prerequisite_baseline.items())),
        "canonical_inputs": inputs,
        "downstream_consumers": authority_context.get(
            "downstream_consumers", []
        ),
        "axes": axes,
        "forbidden_inputs": [
            "future_candidate",
            "decision_review",
            "preferred_solution",
            "selected_solution",
            "write_set",
        ],
    }
    return {**payload, "request_id": _request_id(payload)}


def validate_explorer_request_binding(
    *,
    expected_request: dict[str, Any] | None,
    evidence: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    if expected_request is None:
        return []
    if not isinstance(evidence, dict):
        return []
    actual = evidence.get("explorer_request_id")
    expected = expected_request["request_id"]
    if actual != expected:
        return [
            {
                "code": "DECISION_EXPLORER_REQUEST_MISMATCH",
                "expected": expected,
                "actual": actual,
            }
        ]
    return []
