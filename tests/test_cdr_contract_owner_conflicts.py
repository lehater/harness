#!/usr/bin/env python3
"""CDR exported-output owner conflict: strong negative control only."""
from __future__ import annotations

import copy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from evals.cdr_contract_owner_conflicts import (
    _explicit_target_export, delegated_target_claims,
)

target_file = "docs/domain/relation-classification-catalog.yaml"
delegated = (
    "RESEARCH-SELECTED SECTION [Relational Subject Knowledge]: A proposition "
    "records its participants and conditions. "
    "The " + chr(96) + target_file + chr(96) +
    " provides the reusable predicate vocabulary and classifier. "
    "The proposition is distinct from its predicate."
)
assert _explicit_target_export(delegated, target_file) is not None
assert "provides the reusable predicate vocabulary" in _explicit_target_export(
    delegated, target_file)
for text in (
    "Provider discusses the topic of predicate classification generally.",
    "The " + chr(96) + target_file + chr(96) + " is cited as contextual reading.",
    "The file docs/domain/other-model.yaml provides its own distinct output.",
    "The " + chr(96) + target_file + chr(96) + " does not provide graph storage.",
    "Someother/" + target_file + " provides its independent contract.",
):
    assert _explicit_target_export(text, target_file) is None, repr(text)

case = {
    "target": {
        "capability": "prep.knowledge-relation-classification",
        "output_obligations": [{"id": "CLASS-MATCH",
                                "source": {"path": target_file}}],
    },
    "provider_catalog": [{
        "capability": "prep.knowledge-model",
        "source": "docs/domain/knowledge-model.md",
        "semantic_surface": [delegated],
    }],
}
prediction = {"input_needs": [{
    "provider": "prep.knowledge-model",
    "obligation": "CLASS-MATCH", "claim_index": 0,
}]}
issues = delegated_target_claims(case, prediction)
assert len(issues) == 1
assert issues[0]["provider"] == "prep.knowledge-model"
assert issues[0]["target_export_artifact"] == target_file
assert issues[0]["disposition"] == "BLOCK_PROVIDER_AS_TARGET_EXPORT_OWNER_EVIDENCE"
assert issues[0]["independent_ownership_dispute_review_required"] is True
assert issues[0]["semantic_directness_adjudicated"] is False

not_our_source = copy.deepcopy(case)
not_our_source["provider_catalog"][0]["source"] = target_file
assert delegated_target_claims(not_our_source, prediction) == []

not_an_export = copy.deepcopy(case)
not_an_export["provider_catalog"][0]["semantic_surface"][0] = (
    "A provider may cite this document as context, but that does not "
    "establish producer ownership."
)
assert delegated_target_claims(not_an_export, prediction) == []

missing = copy.deepcopy(case)
missing["target"]["output_obligations"][0].pop("source")
assert delegated_target_claims(missing, prediction) == []
print("CDR export-owner conflict negative controls: PASS")
