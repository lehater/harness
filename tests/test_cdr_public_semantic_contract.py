#!/usr/bin/env python3
"""Fail-closed research atomic public contract: source proof is not adoption."""
from __future__ import annotations

import copy
import json
import sys
import tempfile
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from evals.cdr_public_semantic_contract import prepare_draft

with tempfile.TemporaryDirectory(prefix="cdr-public-contract-") as td:
    base = Path(td)
    (base / "docs").mkdir()
    target = "demo.target-classifier"
    source = "demo.source"
    auxiliary = "demo.other-source"
    target_path = "docs/target.yaml"
    source_path = "docs/source.md"
    other_path = "docs/other.yaml"
    target_text = "A specific target-owned classifier must be independently produced."
    source_owned = "This producer owns a stable public concept and distinction across contexts."
    delegated = ("The " + chr(96) + target_path + chr(96) +
                 " provides an independently owned predicate classifier.")
    (base / target_path).write_text(yaml.safe_dump({"meaning": target_text}), encoding="utf-8")
    (base / source_path).write_text(
        "# Source\n\n## Public outputs\n\n" + source_owned + "\n\n" +
        delegated + "\n\n## Examples\n\nAn illustrative unrelated use only.\n",
        encoding="utf-8",
    )
    (base / other_path).write_text(yaml.safe_dump({
        "purpose": "A separately published and independently framed output contract.",
        "content": {"requirements": [{
            "id": "REQ-ONE", "status": "ACCEPTED",
            "statement": "A source requirement constrains the system's observable use without claiming the target output.",
        }]},
    }), encoding="utf-8")
    core = {
        target: {"path": target_path},
        source: {"path": source_path},
        auxiliary: {"path": other_path},
    }
    review = {
        source: {"revision": 3},
        auxiliary: {"revision": 2},
        target: {"revision": 4},
    }
    pin = "a" * 40
    manifest = {
        "version": 1, "kind": "harness-cdr-public-semantic-contract-draft",
        "status": "RESEARCH_DRAFT_NOT_AUTHORITY_ACCEPTED",
        "source_commit": pin, "target_capability": target,
        "reviewer_identity_verified": False,
        "authority_acceptance_verified": False,
        "automatic_writeback_allowed": False,
        "notes": "This draft is not a contract acceptance event.",
        "contracts": [
            {"capability": source, "claims": [
                {"id": "SOURCE-OWNED-CLAIM", "role": "OWNED_EXPORT_CANDIDATE",
                 "section": "Public outputs", "quote": source_owned},
                {"id": "SOURCE-DELEGATION", "role": "DELEGATED_EXPORT_REFERENCE",
                 "section": "Public outputs", "delegates_to": target, "quote": delegated},
            ]},
            {"capability": auxiliary, "claims": [
                {"id": "OTHER-OUTPUT", "role": "OWNED_EXPORT_CANDIDATE",
                 "yaml_field": "purpose",
                 "quote": "A separately published and independently framed output contract."},
            ]},
        ],
    }
    path = base / "contract.yaml"
    def run(doc, *, good=True):
        path.write_text(yaml.safe_dump(doc, sort_keys=False), encoding="utf-8")
        try:
            value = prepare_draft(
                base, sha=pin, manifest_path=path, target=target,
                expected=(source, auxiliary), artifacts=core, reviews=review
            )
        except ValueError:
            if good:
                raise
            return None
        if not good:
            raise AssertionError("invalid contract escaped validation")
        return value
    result = run(manifest)
    assert result["status"] == "RESEARCH_ATOMIC_CONTRACT_CANDIDATES_NOT_ACCEPTED"
    assert result["authority_acceptance_verified"] is False
    assert result["claim_set_exhaustive"] is False
    assert result["automatic_writeback_allowed"] is False
    assert len(result["provider_catalog"]) == 2
    first = result["provider_catalog"][0]
    assert first["evidence_status"] == "CONTRACT_ONLY"
    assert len(first["semantic_surface"]) == 1
    assert source_owned in first["semantic_surface"][0]
    assert "classifier" not in first["semantic_surface"][0]
    assert first["source_scope"]["claim_ids"] == ["SOURCE-OWNED-CLAIM"]
    assert first["source_scope"]["selection_scope_partial"] is True
    assert len(result["delegated_references"]) == 1
    assert result["delegated_references"][0]["delegates_to_capability"] == target

    def bad(change):
        data = copy.deepcopy(manifest)
        change(data)
        run(data, good=False)
    bad(lambda d: d.update(authority_acceptance_verified=True))
    bad(lambda d: d.update(status="ACCEPTED"))
    bad(lambda d: d["contracts"][0]["claims"][0].update(quote="Fabricated source-owned normative public export sentence."))
    bad(lambda d: d["contracts"][0]["claims"][1].update(role="OWNED_EXPORT_CANDIDATE"))
    bad(lambda d: d["contracts"][0]["claims"][1].update(delegates_to=auxiliary))
    bad(lambda d: d["contracts"][0]["claims"][1].pop("delegates_to"))
    bad(lambda d: d["contracts"][1]["claims"][0].update(quote="Published something different from the source."))
    bad(lambda d: d["contracts"][0]["claims"][0].update(id="OTHER-OUTPUT"))
    bad(lambda d: d["contracts"].pop())
    bad(lambda d: d["contracts"][0]["claims"][0].update(accepted=True))
    bad(lambda d: d.update(source_commit="b"*40))

    path_req = base / other_path
    text = path_req.read_text(encoding="utf-8")
    obj = yaml.safe_load(text)
    obj["content"]["requirements"][0]["status"] = "DRAFT"
    path_req.write_text(yaml.safe_dump(obj), encoding="utf-8")
    product_doc = copy.deepcopy(manifest)
    product_doc["contracts"][1]["claims"] = [{
        "id": "OTHER-REQUIREMENT", "role": "OWNED_EXPORT_CANDIDATE",
        "requirement_id": "REQ-ONE",
        "quote": "A source requirement constrains the system's observable use without claiming the target output.",
    }]
    run(product_doc, good=False)
    obj["content"]["requirements"][0]["status"] = "ACCEPTED"
    path_req.write_text(yaml.safe_dump(obj), encoding="utf-8")
    result = run(product_doc)
    assert result["provider_catalog"][1]["source_scope"]["claim_ids"] == ["OTHER-REQUIREMENT"]
    assert result["independent_export_ownership_verified"] is False

print("CDR atomic public semantic contract draft validation: PASS")
