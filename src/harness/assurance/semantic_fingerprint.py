#!/usr/bin/env python3
"""Stable fingerprints for accepted semantic assertions."""
from __future__ import annotations

import hashlib
import json
from typing import Any

from harness.project_model.core import CoreError

# Physical source placement is provenance metadata. Lifecycle dependency
# currentness tracks semantic atom identity/content; Authority and all other
# assertion fields remain fingerprinted.
_NON_SEMANTIC_FIELDS = {"source_artifact"}


def semantic_assertion_fingerprint(assertion: dict[str, Any]) -> str:
    if not isinstance(assertion, dict):
        raise CoreError("semantic assertion fingerprint requires a mapping")
    assertion_id = assertion.get("id")
    if not isinstance(assertion_id, str) or not assertion_id:
        raise CoreError("semantic assertion fingerprint requires id")
    payload = {
        key: value
        for key, value in assertion.items()
        if key not in _NON_SEMANTIC_FIELDS
    }
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return "SAF-" + hashlib.sha256(encoded).hexdigest()


def semantic_assertion_fingerprints(
    document: dict[str, Any],
) -> dict[str, str]:
    result: dict[str, str] = {}
    for assertion in document.get("semantic_assertions", []) or []:
        if not isinstance(assertion, dict):
            raise CoreError("semantic assertion must be a mapping")
        assertion_id = assertion.get("id")
        if not isinstance(assertion_id, str) or not assertion_id:
            raise CoreError("semantic assertion requires id")
        if assertion_id in result:
            raise CoreError(f"duplicate semantic assertion: {assertion_id}")
        result[assertion_id] = semantic_assertion_fingerprint(assertion)
    return result


__all__ = [
    'Any',
    'CoreError',
    'annotations',
    'hashlib',
    'json',
    'semantic_assertion_fingerprint',
    'semantic_assertion_fingerprints',
]
