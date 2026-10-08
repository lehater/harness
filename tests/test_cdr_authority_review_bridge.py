#!/usr/bin/env python3
"""CDR independent Authority facets are complete, source-bound and NON-ACCEPTING."""
from __future__ import annotations

import copy
import sys
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from evals import cdr_authority_review_bridge as bridge

sha = "a" * 40
input_case = {
    "id": "FAKE-PREP",
    "target": {
        "capability": bridge.TARGET,
        "output_obligations": [{"id": "O-A"}, {"id": "O-B"}],
    },
    "provider_catalog": [{
        "capability": "prep.knowledge-model",
        "source": "docs/knowledge.md",
        "source_sha256": "1" * 64,
        "semantic_surface": ["Atomic knowledge-model meaning"],
        "source_scope": {"claim_ids": ["KM-OWNED"]},
    }],
}
fake_prep = {
    "inputs": {"cases": [input_case]},
    "source_fingerprints": {"atomic_draft_manifest": "f" * 64},
}
fake_contrast = {
    "source_surface_protocol": bridge.SOURCE_MODE_V3,
    "effective_resolution": "NOT_RESOLVED",
    "atomic_consumption_review_not_authorization": {
        "per_obligation": [
            {"obligation_id": "O-A",
             "status": "MODEL_CANDIDATE_NOT_AUTHORITY_PROOF",
             "candidate_needs": [{
                "provider": "prep.knowledge-model",
                "atomic_claim_id": "KM-OWNED",
                "consumption_rationale_model_only": "The source looks similar to the target",
                "provider_cites_target_as_distinct_export_owner": True,
             }]},
            {"obligation_id": "O-B",
             "status": "UNACCOUNTED_NO_NONAPPLICABILITY_JUSTIFICATION",
             "candidate_needs": []},
        ],
    },
    "all_available_provider_contracts_covered": False,
    "declared_not_suggested_not_removal_evidence": ["prep.model-context-strategy"],
    "unaccounted_target_obligations": ["O-B"],
    "model_status": "RESOLVED",
    "model_requires": ["prep.knowledge-model"],
    "status": "INVALID_PROPOSED_TOPOLOGY",
    "cycle_blocks": [{"provider": "prep.knowledge-model",
                      "cycle": [bridge.TARGET, "prep.knowledge-model", bridge.TARGET]}],
}
target_core = {
    bridge.TARGET: {
        "path": "docs/target.yaml", "authority": "TACTICAL-DOMAIN-DESIGN"},
    "prep.knowledge-model": {
        "path": "docs/knowledge.md", "authority": "TACTICAL-DOMAIN-DESIGN"},
}
review = {bridge.TARGET: {"revision": 5},
          "prep.knowledge-model": {"revision": 6}}
inputs = {"cases": [input_case]}
request = {"request_id": "source-bound-request"}
response = {"kind": "frozen-provider", "results": ["one"]}
with (
    patch.object(bridge, "reconcile", return_value=fake_contrast),
    patch.object(bridge, "build", return_value=fake_prep),
    patch.object(bridge, "_registry", return_value=(target_core, review, b"", b"")),
):
    packet = bridge.build_packet(ROOT, sha=sha, inputs=inputs,
                                 request=request, response=response)
assert packet["review_facets"]["export_ownership"][0]["id"] == "prep.knowledge-model/KM-OWNED"
assert packet["review_facets"]["direct_consumption"][0]["cycle_blocked"] is True
assert packet["review_facets"]["input_coverage"][0]["unaccounted_obligations"] == ["O-B"]
assert packet["bound_original_model_sha256"] == bridge.digest(response)
assert packet["packet_sha256"] == bridge.digest(
    {k: v for k, v in packet.items() if k != "packet_sha256"})
assert packet["automatic_writeback_allowed"] is False

draft = bridge.draft_template(packet)
result = bridge.validate_draft(packet, draft)
assert result["status"] == "DRAFT_CONSISTENT_NOT_AUTHORITY_DECIDED"
assert result["all_facets_accounted_for"] is True
assert result["independent_authority_decision_verified"] is False

def rejected(mutator, original=draft):
    trial = copy.deepcopy(original)
    mutator(trial)
    try:
        bridge.validate_draft(packet, trial)
    except ValueError:
        return
    raise AssertionError("invalid draft accepted")

rejected(lambda d: d.update(status="ACCEPTED"))
rejected(lambda d: d.update(independent_authority_decision_verified=True))
rejected(lambda d: d.update(graph_update_authorized=True))
rejected(lambda d: d.update(reviewer_identity_verified=True))
rejected(lambda d: d.update(packet_sha256="0" * 64))
rejected(lambda d: d["facets"]["target_outputs"].pop())
rejected(lambda d: d["facets"]["export_ownership"][0].update(id="forged"))
rejected(lambda d: d["facets"]["export_ownership"][0].update(decision="ACCEPTED"))
rejected(lambda d: d["facets"]["export_ownership"][0].update(review_authority="PRODUCT-REQUIREMENTS"))
rejected(lambda d: d["facets"]["direct_consumption"][0].update(decision="LIKELY_DIRECT"))
rejected(lambda d: d["facets"]["input_coverage"][0].update(decision="DRAFT_SCOPE_PLAUSIBLE"))
rejected(lambda d: d["facets"]["target_outputs"][0].update(evidence="ok"))
rejected(lambda d: d["facets"].update({"approval": []}))
rejected(lambda d: d.update(signature="spoofed"))

# Allowed *tentative* interpretations do not become authorization.
tentative = copy.deepcopy(draft)
tentative["facets"]["export_ownership"][0]["decision"] = "LIKELY_OWNED"
tentative["facets"]["target_outputs"][0]["decision"] = "LIKELY_IN_SCOPE"
tentative["facets"]["direct_consumption"][0]["decision"] = "LIKELY_MEDIATED"
assert bridge.validate_draft(packet, tentative)["graph_update_authorized"] is False
assert bridge.validate_draft(packet, tentative)["exported_claim_ownership_accepted"] is False

tampered = copy.deepcopy(packet)
tampered["review_facets"]["input_coverage"][0]["unaccounted_obligations"] = []
try:
    bridge.validate_draft(tampered, draft)
except ValueError:
    pass
else:
    raise AssertionError("tampered packet accepted")
print("CDR source-bound independent Authority draft facets: PASS")
