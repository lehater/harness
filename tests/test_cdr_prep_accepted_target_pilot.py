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
            statement = ("# Published public semantics\n\nA published contract describes "
                         f"the specific independently declared meaning of {capability}, "
                         "and it is not the target output itself.\n")
            if capability == "prep.knowledge-model":
                statement = statement.replace(
                    "\n\nA published contract", "\n\nConceptually:\n\nA published contract"
                )
            if capability == "prep.domain-strategy":
                statement += "\n## Extended source claims\n\n" + "".join(
                    f"- Independent synthetic claim {n}: public source constraints "
                    "remain distinct from the target's accepted outcome contract.\n"
                    for n in range(55)
                )
            emit(project / source, statement)
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
    assert reviewed["status"] == "INVALID_PROPOSED_TOPOLOGY"
    assert reviewed["effective_resolution"] == "NOT_RESOLVED"
    assert reviewed["model_resolution_is_not_accepted"] is True
    assert reviewed["all_available_provider_contracts_covered"] is False
    assert reviewed["truncated_provider_ids"] == ["prep.domain-strategy"]
    assert reviewed["provider_claim_entailment_verified"] is False
    assert any(x["provider"] == supplier_b and x["reason"] ==
               "NON_SUBSTANTIVE_SOURCE_FRAGMENT"
               for x in reviewed["non_substantive_cited_claims"])
    assert reviewed["same_as_existing"] == [supplier_a]
    assert reviewed["cycle_blocks"] == [{
        "provider": supplier_b,
        "cycle": [TARGET, supplier_b, TARGET],
        "disposition": "BLOCKED_BY_CYCLE",
    }]
    assert reviewed["automatic_writeback_allowed"] is False
    assert reviewed["target_contract_per_obligation_acceptance"] == "NOT_ESTABLISHED"
    assert supplier_b in reviewed["proposed_additions_not_approved"]

    no_cycle = copy.deepcopy(reply)
    no_cycle["results"][0]["proposed_requires"] = [supplier_a]
    no_cycle["results"][0]["input_needs"] = [
        x for x in no_cycle["results"][0]["input_needs"]
        if x["provider"] == supplier_a
    ]
    still_blocked = reconcile(
        project, sha=sha, inputs=inputs, request=request, response=no_cycle
    )
    assert still_blocked["status"] == "BLOCKED_INCOMPLETE_PROVIDER_SURFACES"
    assert still_blocked["effective_resolution"] == "NOT_RESOLVED"
    assert still_blocked["cycle_blocks"] == []
    assert still_blocked["semantic_directness_proven"] is False

    contradiction = copy.deepcopy(reply)
    contradiction["results"][0]["status"] = "RESOLVED"
    try:
        reconcile(project, sha=sha, inputs=inputs, request=request,
                  response=contradiction)
    except ValueError:
        pass
    else:
        raise AssertionError("RESOLVED with unresolved obligations must fail")

    altered = copy.deepcopy(reply)
    altered["request_id"] = "wrong"
    try:
        reconcile(project, sha=sha, inputs=inputs, request=request, response=altered)
    except ValueError:
        pass
    else:
        raise AssertionError("unbound reply accepted")

    # Research-selected public sections must be source-bound, still partial,
    # and cannot turn a model RESOLVED into an accepted graph decision.
    import evals.cdr_prep_accepted_target_pilot as pilot
    for artifact in core[1:]:
        p = project / artifact["path"]
        previous = p.read_text(encoding="utf-8")
        p.write_text(previous.replace(
            "# Published public semantics\n\n",
            "# Published public semantics\n\n## Purpose\n\n",
            1,
        ), encoding="utf-8")
    git(project, "add", ".")
    git(project, "-c", "user.name=Test", "-c", "user.email=test@example.invalid",
        "commit", "-qm", "add explicit provider-public Purpose sections")
    newer_sha = git(project, "rev-parse", "HEAD")
    manifest_path = project / "research-selector.yaml"
    manifest_path.write_text(yaml.safe_dump({
        "version": 1,
        "kind": "harness-cdr-research-owned-surface-selectors",
        "status": "UNACCEPTED_OPERATOR_RESEARCH_SELECTION",
        "source_commit": newer_sha,
        "target_capability": TARGET,
        "providers": [{"capability": cid, "mode": "markdown-sections",
                       "headings": ["Purpose"]} for cid in PROVIDER_IDS],
    }), encoding="utf-8")
    previous_manifest = pilot.SELECTOR_MANIFEST
    pilot.SELECTOR_MANIFEST = manifest_path
    try:
        selected = pilot.build(
            project, sha=newer_sha, surface_mode=pilot.SOURCE_MODE_V2
        )
        new_request = selected["request"]
        assert selected["inputs"]["source_surface_protocol"] == pilot.SOURCE_MODE_V2
        assert all(len(s["semantic_surface"]) == 1
                   and s["source_scope"]["selection_scope_partial"]
                   and not s["source_scope"]["independent_ownership_review_verified"]
                   for s in selected["inputs"]["cases"][0]["provider_catalog"])
        assert '"requires"' not in json.dumps(new_request)
        candidate = {
            "version": 1,
            "kind": "harness-dependency-resolution-evaluator-response",
            "request_id": new_request["request_id"],
            "results": [{
                "case_request_id": new_request["cases"][0]["case_request_id"],
                "status": "RESOLVED",
                "proposed_requires": [supplier_a],
                "input_needs": [{
                    "provider": supplier_a, "claim_index": 0,
                    "obligation": "classification-outcome-matched",
                    "basis": "DIRECT_ACCEPTED",
                    "consumption_rationale": "This is a provisional output-only source review."
                }],
                "unresolved_obligations": [],
            }],
        }
        contrast = pilot.reconcile(
            project, sha=newer_sha, inputs=selected["inputs"],
            request=new_request, response=candidate,
            surface_mode=pilot.SOURCE_MODE_V2,
        )
        assert contrast["model_status"] == "RESOLVED"
        assert contrast["status"] == "BLOCKED_OPERATOR_SELECTED_PROVIDER_SURFACES"
        assert contrast["all_available_provider_contracts_covered"] is False
        assert contrast["operator_selected_partial_provider_ids"] == sorted(PROVIDER_IDS)
        assert contrast["automatic_writeback_allowed"] is False
        try:
            pilot.reconcile(
                project, sha=newer_sha, inputs=selected["inputs"],
                request=new_request, response=candidate,
                surface_mode=pilot.SOURCE_MODE_V1,
            )
        except ValueError:
            pass
        else:
            raise AssertionError("raw and selected provider protocols cannot be interchanged")
    finally:
        pilot.SELECTOR_MANIFEST = previous_manifest

    # Editing an accepted source without a new pinned reviewed commit fails.
    sha = newer_sha
    path = project / core[0]["path"]
    path.write_text(path.read_text() + "\n# UNREVIEWED CHANGE\n")
    try:
        build(project, sha=sha)
    except ValueError:
        pass
    else:
        raise AssertionError("dirty reviewed target was accepted")
print("CDR PREP accepted real-target pilot fixture: PASS")
