#!/usr/bin/env python3
"""Synthetic filesystem adversarial tests for the accepted PREP target pilot."""
from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from evals.cdr_prep_accepted_target_pilot import (
    TARGET, PROVIDER_IDS, build, reconcile,
)


def emit(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def git(root: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(root), *args], text=True).strip()


with tempfile.TemporaryDirectory(prefix="harness-cdr-real-target-") as temp:
    project = Path(temp)
    git(project, "init", "-q")
    core = []
    reviews = []
    for i, capability in enumerate([TARGET, *PROVIDER_IDS]):
        source = ("docs/domain/relation-classification-catalog.yaml"
                  if capability == TARGET else f"docs/providers/p{i}.md")
        core.append({
            "id": f"ART-{i}",
            "authority": ("TACTICAL-DOMAIN-DESIGN" if i == 0 else "OTHER-AUTHORITY"),
            "path": source,
            "provides": [capability],
        })
        reviews.append({
            "capability": capability,
            "revision": i + 1,
            "basis": "The independent artifact source has a recorded semantic revision.",
        })
        if i:
            emit(project / source,
                 "# Published public semantics\n\nA published contract describes "
                 f"the specific independently declared meaning of {capability}, "
                 "and it is not the target output itself.\n")
    outcomes = {
        name: {
            "meaning": f"Accepted catalog handling semantics for the result {name}, "
                       "preserving explicit subject-knowledge boundaries.",
            "required_output": ["reason", "evidence"],
        } for name in ["matched", "candidate_needed", "insufficient_evidence"]
    }
    emit(project / core[0]["path"], yaml.safe_dump({
        "kind": "prep-relation-classification-catalog",
        "status": "canonical",
        "classification_outcomes": outcomes,
    }))
    emit(project / ".harness/core.yaml", yaml.safe_dump({"artifacts": core}))
    emit(project / ".harness/semantic-baseline.yaml", yaml.safe_dump({"reviews": reviews}))
    author_produces = [{
        "capability": TARGET,
        "requires": [{"capability": PROVIDER_IDS[0]}, {"capability": PROVIDER_IDS[1]}],
    }] + [{
        "capability": cid, "requires": [{"capability": TARGET}]
        if cid == "prep.knowledge-model" else []
    } for cid in PROVIDER_IDS]
    emit(project / ".harness/engineering-graph.yaml",
         yaml.safe_dump({"authorities": [{
             "id": "TACTICAL-DOMAIN-DESIGN", "produces": author_produces
         }]}))
    git(project, "add", ".")
    git(project, "-c", "user.name=Test", "-c", "user.email=test@example.invalid",
        "commit", "-qm", "fixture")
    sha = git(project, "rev-parse", "HEAD")

    phase_a = build(project, sha=sha)
    request = phase_a["request"]
    inputs = phase_a["inputs"]
    assert phase_a["independent_target_obligation_review_verified"] is False
    assert len(inputs["cases"]) == 1
    assert len(request["cases"][0]["provider_catalog"]) == len(PROVIDER_IDS)
    assert all(x["evidence_status"] == "ACCEPTED_EVIDENCE"
               for x in request["cases"][0]["provider_catalog"])
    assert len(request["cases"][0]["target"]["output_obligations"]) == 3
    assert '"requires"' not in json.dumps(request)
    assert '"expected_requires"' not in json.dumps(request)
    assert request["request_id"] == build(project, sha=sha)["request"]["request_id"]

    supplier_a = PROVIDER_IDS[0]
    supplier_b = "prep.knowledge-model"
    reply = {
        "version": 1,
        "kind": "harness-dependency-resolution-evaluator-response",
        "request_id": request["request_id"],
        "results": [{
            "case_request_id": request["cases"][0]["case_request_id"],
            "status": "UNRESOLVED",
            "proposed_requires": [supplier_a, supplier_b],
            "input_needs": [
                {"provider": cid, "claim_index": 0,
                 "obligation": "classification-outcome-matched",
                 "basis": "DIRECT_ACCEPTED",
                 "consumption_rationale": "This is only a synthetic direction-test fixture."}
                for cid in [supplier_a, supplier_b]
            ],
            "unresolved_obligations": [
                o["id"] for o in inputs["cases"][0]["target"]["output_obligations"]
            ],
        }],
    }
    reviewed = reconcile(project, sha=sha, inputs=inputs, request=request, response=reply)
    assert reviewed["status"] == "READ_ONLY_REVIEW_NOT_AUTHORITY_ACCEPTANCE"
    assert reviewed["same_as_existing"] == [supplier_a]
    assert reviewed["cycle_blocks"] == [{
        "provider": supplier_b,
        "cycle": [TARGET, supplier_b, TARGET],
        "disposition": "BLOCKED_BY_CYCLE",
    }]
    assert reviewed["automatic_writeback_allowed"] is False
    assert reviewed["target_contract_per_obligation_acceptance"] == "NOT_ESTABLISHED"
    assert supplier_b in reviewed["proposed_additions_not_approved"]

    altered = copy.deepcopy(reply)
    altered["request_id"] = "wrong"
    try:
        reconcile(project, sha=sha, inputs=inputs, request=request, response=altered)
    except ValueError:
        pass
    else:
        raise AssertionError("unbound reply accepted")

    # Editing an accepted source without a new pinned reviewed commit fails.
    path = project / core[0]["path"]
    path.write_text(path.read_text() + "\n# UNREVIEWED CHANGE\n")
    try:
        build(project, sha=sha)
    except ValueError:
        pass
    else:
        raise AssertionError("dirty reviewed target was accepted")
print("CDR PREP accepted real-target pilot fixture: PASS")
