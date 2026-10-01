#!/usr/bin/env python3
"""Stable acceptance-policy identity for semantic admission currentness."""
from __future__ import annotations

import hashlib
import json
from typing import Any

EVALUATOR_CONTRACT = "strict-semantic-admission/v1"


def _canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )


def build_acceptance_policy_baseline(
    *,
    knowledge_kind: str,
    semantic_contract: dict[str, Any],
    decision_contract: dict[str, Any] | None,
    decision_axis_policies: dict[str, dict[str, str]] | None,
    execution_assurance: str | None,
) -> dict[str, Any]:
    """Return an opaque baseline for every rule that can change admission.

    The fingerprint intentionally uses effective rules instead of source-file
    identity. Reordering or metadata changes that do not survive normalization
    therefore need not invalidate accepted knowledge.
    """
    decision_rules = None
    if decision_contract is not None:
        decision_rules = {
            key: value
            for key, value in decision_contract.items()
            if key != "policy_defaults"
        }

    payload = {
        "version": 1,
        "knowledge_kind": knowledge_kind,
        "evaluator_contract": EVALUATOR_CONTRACT,
        "semantic_contract": semantic_contract,
        "decision_contract": decision_rules,
        "decision_axis_policies": decision_axis_policies,
        "execution_assurance": execution_assurance,
    }
    digest = hashlib.sha256(
        _canonical_json(payload).encode("utf-8")
    ).hexdigest()
    return {
        "version": 1,
        "kind": "harness-acceptance-policy-baseline",
        "evaluator_contract": EVALUATOR_CONTRACT,
        "fingerprint": f"sha256:{digest}",
    }
