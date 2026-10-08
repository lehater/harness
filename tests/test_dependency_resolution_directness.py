#!/usr/bin/env python3
"""Source echo / existing transitive access are review signals, not edges."""
from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from evals.project_discovery_directness import audit_additions

productions = {
    "x.product": {"requires": []},
    "x.domain": {"requires": [{"capability": "x.product"}]},
    "x.model-context": {"requires": [{"capability": "x.domain"}]},
    "x.tactical": {"requires": [
        {"capability": "x.model-context"}, {"capability": "x.product"}
    ]},
}
case = {
    "target": {
        "output_obligations": [
            {"id": "mc", "description": "Source-selected model context scope",
             "source": {"capability": "x.model-context"}},
            {"id": "ds", "description": "Source-selected strategic section",
             "source": {"capability": "x.domain"}},
        ],
    },
}
result = {
    "proposed_requires": ["x.product", "x.model-context", "x.domain"],
    "input_needs": [
        {"obligation": "ds", "provider": "x.domain"},
        {"obligation": "mc", "provider": "x.model-context"},
    ],
}
old = {"x.product", "x.model-context"}
audit = audit_additions(case, result, existing_requires=old, productions=productions)
assert len(audit) == 1
x = audit[0]
assert x["provider"] == "x.domain"
assert x["status"] == "DIRECTNESS_UNPROVEN"
assert x["source_echo_obligations"] == ["ds"]
assert x["non_echo_obligations"] == []
assert x["existing_transitive_paths"] == [["x.model-context", "x.domain"]]
assert "SUPPLIER_TEXT_COPIED_INTO_TARGET_OBLIGATION" in x["reasons"]
assert "NO_NON_ECHO_DIRECT_CONSUMPTION_EVIDENCE" in x["reasons"]
assert x["requires_independent_review"]
assert x["automatic_writeback_allowed"] is False

# New neutral target prevents self-citation by construction but cannot
# magically establish the *necessity* of the strategic direct edge.
neutral = {"target": {"output_obligations": [
    {"id": "neutral-tactical-output", "description": "Operator test paraphrase"}
]}}
result_neutral = {
    "proposed_requires": result["proposed_requires"],
    "input_needs": [{"obligation": "neutral-tactical-output", "provider": "x.domain"}],
}
audited = audit_additions(
    neutral, result_neutral, existing_requires=old, productions=productions
)[0]
assert audited["source_echo_obligations"] == []
assert audited["non_echo_obligations"] == ["neutral-tactical-output"]
assert "SUPPLIER_TEXT_COPIED_INTO_TARGET_OBLIGATION" not in audited["reasons"]
assert audited["existing_transitive_paths"] == [["x.model-context", "x.domain"]]
assert audited["status"] == "DIRECTNESS_UNPROVEN"

# A modeled upstream path, without a source-echo, is never a deterministic
# reason to remove an accepted direct prerequisite either.
no_paths = audit_additions(
    neutral, result_neutral,
    existing_requires={"x.product"},
    productions=productions,
)[0]
assert no_paths["existing_transitive_paths"] == []
assert no_paths["status"] == "DIRECTNESS_UNPROVEN"

assert audit_additions(
    neutral,
    {"proposed_requires": sorted(old), "input_needs": []},
    existing_requires=old,
    productions=productions,
) == []
print("dependency resolution directness confound audit: PASS")
