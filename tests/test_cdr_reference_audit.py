#!/usr/bin/env python3
"""Regression of CDR reference corpus blinding and conservative edge flags."""
from __future__ import annotations

import copy
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from evals.cdr_reference_audit import (
    DEFAULT_AUTHORITIES, DEFAULT_MODEL, DEFAULT_PROOF, audit, prepare, run,
)
from harness.reference_model.reference_materializer import load_yaml
from harness.project_model.core import CoreError

model = load_yaml(ROOT / DEFAULT_MODEL)
authorities = load_yaml(ROOT / DEFAULT_AUTHORITIES)
proof = load_yaml(ROOT / DEFAULT_PROOF)
pins = {"model": "model", "authorities": "owners", "proof": "claims"}

blind = prepare(model, authorities, proof, pins)
assert blind["status"] == "EXPERIMENTAL_SOURCE_ONLY_NOT_ACCEPTED"
assert len(blind["templates"]) == 40
assert blind["automatic_writeback_allowed"] is False
assert blind["target_output_obligation_completeness_proven"] is False
assert all("requires" not in row and "existing_direct_edges" not in row
           for row in blind["templates"])
assert "requires" not in json.dumps(blind)
assert not any("independent_directness" in row for row in blind["templates"])

report = audit(model, authorities, proof, pins)
assert report["template_count"] == 40
assert report["direct_edge_count"] == 94
assert report["conditional_edge_count"] == 41
assert report["structural_transitive_flag_count"] == 40
assert len(report["targets_without_explicit_primary_claims"]) == 12
assert len(report["edge_review_packets"]) == 94
assert report["independent_directness_verified"] is False
assert report["automatic_writeback_allowed"] is False
assert all(x["independent_directness"] == "UNDETERMINED" for x in report["edge_review_packets"])
assert all(x["authority_decision"] == "NOT_ACCEPTED" for x in report["edge_review_packets"])
assert all(len(x["review_questions"]) == 5 for x in report["edge_review_packets"])
assert audit(model, authorities, proof, pins) == report

by_edge = {(x["target"], x["provider"]): x for x in report["edge_review_packets"]}
topology = by_edge[("INTERFACE-TOPOLOGY", "INFORMATION-ARCHITECTURE")]
assert topology["structural_transitive_flag"] is True
assert any(p["templates"] == [
    "INTERFACE-TOPOLOGY", "INTERACTION-DESIGN", "INFORMATION-ARCHITECTURE"
] and not p["conditional_hops"] for p in topology["alternative_structural_paths"])
conditional = by_edge[("DOMAIN-MODEL", "DOMAIN-STRATEGY")]
assert conditional["structural_transitive_flag"] is True
assert conditional["direct_condition"] is not None
assert all(not p["all_conditions_satisfiable_proven"] and
           not p["semantic_mediation_proven"]
           for p in conditional["alternative_structural_paths"])
assert by_edge[("PRODUCT-INTENT", "PROBLEM-EVIDENCE")]["structural_transitive_flag"]

modified = copy.deepcopy(model)
top = next(x for x in modified["templates"] if x["id"] == "INTERFACE-TOPOLOGY")
top["requires"] = [x for x in top["requires"] if x["template"] != "INFORMATION-ARCHITECTURE"]
changed = audit(modified, authorities, proof, pins)
assert changed["direct_edge_count"] == 93
assert ("INTERFACE-TOPOLOGY", "INFORMATION-ARCHITECTURE") not in {
    (x["target"], x["provider"]) for x in changed["edge_review_packets"]
}

invalid = copy.deepcopy(model)
first = next(x for x in invalid["templates"] if x["id"] == "PROBLEM-EVIDENCE")
first["requires"] = [{"template": "COMPLETION-CRITERIA"}]
try:
    audit(invalid, authorities, proof, pins)
except CoreError as exc:
    assert "CAPABILITY_CYCLE" in str(exc)
else:
    raise AssertionError("reference cyclic model must fail")

with tempfile.TemporaryDirectory(prefix="cdr-reference-") as d:
    generated = run(phase="audit", model_path=ROOT / DEFAULT_MODEL,
                    authorities_path=ROOT / DEFAULT_AUTHORITIES,
                    proof_path=ROOT / DEFAULT_PROOF)
    assert generated["source_fingerprints"]["model"] != pins["model"]
    assert generated["direct_edge_count"] == report["direct_edge_count"]
    assert run(phase="prepare", model_path=ROOT / DEFAULT_MODEL,
               authorities_path=ROOT / DEFAULT_AUTHORITIES,
               proof_path=ROOT / DEFAULT_PROOF)["templates"] == blind["templates"]

print("CDR reference template corpus and conservative audit: PASS")
