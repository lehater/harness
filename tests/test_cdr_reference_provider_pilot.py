#!/usr/bin/env python3
"""Full-catalog, label-blind reference-provider pilot with no adoption."""
from __future__ import annotations

import copy
import json
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from evals.cdr_reference_provider_pilot import build, reconcile

data = build(ROOT)
request = data["request"]
inputs = data["inputs"]
assert data["status"] == "BLINDED_RESEARCH_PILOT_PREPARED"
assert data["automatic_writeback_allowed"] is False
assert len(inputs["cases"]) == 3
assert len(request["cases"]) == 3
assert len({x["case_request_id"] for x in request["cases"]}) == 3
assert all(len(x["provider_catalog"]) == 39 for x in request["cases"])
assert all(x["evidence_status"] == "CONTRACT_ONLY"
           for c in request["cases"] for x in c["provider_catalog"])
assert all("requires" not in c["target"]
           for c in request["cases"])
assert all("requires" not in p
           for c in request["cases"] for p in c["provider_catalog"])
assert "declared_requires" not in json.dumps(request)
assert "expected_requires" not in json.dumps(request)
assert all(c["target"]["output_obligations"] for c in request["cases"])
assert all(len({x["capability"] for x in c["provider_catalog"]}) == 39
           for c in request["cases"])
assert request["request_id"] == build(ROOT)["request"]["request_id"]

fake = {
    "version": 1,
    "kind": "harness-dependency-resolution-evaluator-response",
    "request_id": request["request_id"],
    "provenance": {"provider": "synthetic-test-not-a-model", "independence": "NONE"},
    "results": [],
}
for case in request["cases"]:
    fake["results"].append({
        "case_request_id": case["case_request_id"],
        "status": "UNRESOLVED",
        "proposed_requires": [],
        "input_needs": [],
        "unresolved_obligations": [x["id"] for x in case["target"]["output_obligations"]],
    })
out = reconcile(ROOT, inputs=inputs, request=request, response=fake)
assert out["status"] == "PROVIDER_HYPOTHESES_REQUIRE_INDEPENDENT_ADJUDICATION"
assert out["automatic_writeback_allowed"] is False
assert out["semantic_directness_proven"] is False
assert len(out["contrasts"]) == 3
assert all(x["directness_decision"] == "UNDETERMINED_PENDING_AUTHORITY"
           and x["declared_edge_omission_is_not_removal_evidence"]
           and not x["new_candidate_not_accepted"]
           for x in out["contrasts"])
assert all(x["declared_provider_count"] > 0 for x in out["contrasts"])

# A model-proposed edge is still nonauthoritative and must bind an exact
# planned-contract claim rather than have a free-floating provider name.
bound = copy.deepcopy(fake)
c0 = request["cases"][0]
candidate = next(x for x in c0["provider_catalog"]
                 if x["capability"] == "reference.information-architecture")
bound["results"][0]["proposed_requires"] = [candidate["capability"]]
bound["results"][0]["input_needs"] = [{
    "obligation": c0["target"]["output_obligations"][0]["id"],
    "provider": candidate["capability"],
    "claim_index": 0,
    "basis": "PLANNED_CONTRACT",
    "consumption_rationale": "Synthetic negative-proof fixture only",
}]
review = reconcile(ROOT, inputs=inputs, request=request, response=bound)
assert review["contrasts"][0]["both_provisional"] == ["reference.information-architecture"]
assert review["authority_acceptance"] is False

# A proposed upstream link to a downstream Screen/View producer would
# introduce a cycle: Screen/View already requires Interface Topology.
cyclic = copy.deepcopy(fake)
topology = request["cases"][1]
screen = next(x for x in topology["provider_catalog"]
              if x["capability"] == "reference.screen-view-design")
cyclic["results"][1]["proposed_requires"] = [screen["capability"]]
cyclic["results"][1]["input_needs"] = [{
    "obligation": topology["target"]["output_obligations"][0]["id"],
    "provider": screen["capability"],
    "claim_index": 0,
    "basis": "PLANNED_CONTRACT",
    "consumption_rationale": "Tempting but reverse-ordered reference input",
}]
cycle = reconcile(ROOT, inputs=inputs, request=request, response=cyclic)
topology_contrast = cycle["contrasts"][1]
assert topology_contrast["structural_candidate_status"] == "BLOCKED_BY_CYCLE"
assert topology_contrast["invalid_new_edge_candidates"] == [{
    "provider": "reference.screen-view-design",
    "reason": "PROPOSED_EDGE_INTRODUCES_CAPABILITY_CYCLE",
    "cycle": ["INTERFACE-TOPOLOGY", "SCREEN-VIEW-DESIGN", "INTERFACE-TOPOLOGY"],
    "must_not_adopt": True,
}]
assert "reference.screen-view-design" in topology_contrast["new_candidate_not_accepted"]
assert cycle["automatic_writeback_allowed"] is False
assert all(x["structural_candidate_status"] ==
           "NO_CYCLE_FOUND_NOT_SEMANTICALLY_VERIFIED"
           for i, x in enumerate(cycle["contrasts"]) if i != 1)

for key in ("response", "request"):
    tampered = copy.deepcopy(fake if key == "response" else request)
    tampered["request_id"] = "invalid"
    try:
        reconcile(ROOT, inputs=inputs, request=tampered if key == "request" else request,
                  response=tampered if key == "response" else fake)
    except ValueError:
        pass
    else:
        raise AssertionError("unbound reference evidence must fail")

unknown = copy.deepcopy(fake)
unknown["results"][0]["proposed_requires"] = ["reference.fake-source"]
try:
    reconcile(ROOT, inputs=inputs, request=request, response=unknown)
except ValueError:
    pass
else:
    raise AssertionError("unknown provider should fail")

unrelated = copy.deepcopy(fake)
unrelated["results"][0]["unresolved_obligations"] = ["made-up"]
try:
    reconcile(ROOT, inputs=inputs, request=request, response=unrelated)
except ValueError:
    pass
else:
    raise AssertionError("unknown output obligation should fail")

# No old graph is used to select the Phase A provider set or output cases.
# Changing one safe declared edge changes the provenance fingerprint and
# reconciliation state, NOT the blinded request cases.
with tempfile.TemporaryDirectory(prefix="cdr-reference-pilot-") as td:
    work = Path(td)
    for filename in [
        "spec/research/reference-engineering-model-v0.yaml",
        "spec/dependency-resolution/reference-provider-pilot-v1.yaml",
        "catalogs/software-authorities-v0.yaml",
        "spec/engineering-coverage/semantic-proof-contract-v1.yaml",
    ]:
        p = work / filename
        p.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / filename, p)
    shutil.copytree(ROOT / "skills/artifacts", work / "skills/artifacts")
    model_file = work / "spec/research/reference-engineering-model-v0.yaml"
    model = json.loads(model_file.read_text(encoding="utf-8"))
    target = next(x for x in model["templates"] if x["id"] == "INTERACTION-DESIGN")
    before = len(target["requires"])
    target["requires"] = [x for x in target["requires"]
                          if x["template"] != "INFORMATION-ARCHITECTURE"]
    assert len(target["requires"]) == before - 1
    model_file.write_text(json.dumps(model, indent=2) + "\n", encoding="utf-8")
    mutated = build(work)
    # Provenance-linked opaque case IDs must change with the source fingerprint,
    # while the actual model-visible obligations and provider catalog stay same.
    def content_only(req):
        return [{key: value for key, value in case.items()
                 if key != "case_request_id"} for case in req["cases"]]
    assert content_only(mutated["request"]) == content_only(request)
    assert mutated["request"]["request_id"] != request["request_id"]
    try:
        reconcile(work, inputs=inputs, request=request, response=fake)
    except ValueError:
        pass
    else:
        raise AssertionError("stale source model must be detected")

print("CDR Reference Model provider-blind research pilot: PASS")
