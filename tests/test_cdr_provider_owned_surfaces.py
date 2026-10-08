#!/usr/bin/env python3
"""Fail-closed source surface selection regression, without GitHub or LLM."""
from __future__ import annotations

import copy
import tempfile
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from evals.cdr_provider_owned_surfaces import (
    _markdown_section, load_selectors, selected_surface,
)
from evals.cdr_prep_accepted_target_pilot import PIN, TARGET, PROVIDER_IDS

path = ROOT / "spec/dependency-resolution/project-pilots/prep-provider-owned-surface-selectors-v1.yaml"
selectors, digest = load_selectors(path, pin=PIN, target=TARGET, expected=PROVIDER_IDS)
assert len(selectors) == 8
assert len(digest) == 64
assert set(selectors) == set(PROVIDER_IDS)
assert set(x["mode"] for x in selectors.values()) == {
    "markdown-sections", "yaml-fields", "accepted-product-requirements"
}

with tempfile.TemporaryDirectory(prefix="cdr-source-surface-") as td:
    root = Path(td)
    def save(name: str, content: str) -> dict:
        full = root / name
        full.parent.mkdir(parents=True, exist_ok=True)
        full.write_text(content, encoding="utf-8")
        return {"path": name}
    markdown = """# Provider
## Purpose

This is an owned public normative boundary, not a target dependency.
It fixes a stable semantic subject to which future users may refer.

## Not selected

Examples:
- this example is context only and should not be exported.

## Claim semantics

An independently described source rule can bound a consumer's meaning.
A different downstream operation cannot re-own this input contract.
"""
    src = save("docs/provider.md", markdown)
    surfaces, scope = selected_surface(
        root, src, {"mode": "markdown-sections",
                    "headings": ["Purpose", "Claim semantics"]}
    )
    assert len(surfaces) == 2
    assert all("Not selected" not in item for item in surfaces)
    assert all("Examples:" not in item for item in surfaces)
    assert scope["selection_scope_partial"] is True
    assert scope["independent_ownership_review_verified"] is False
    assert scope["public_surface_truncated"] is False
    assert scope["claim_count_supplied"] == 2
    assert scope["all_source_contracts_included"] is False

    yaml_source = save("docs/tasks.yaml", yaml.safe_dump({
        "purpose": "Describe an independent purpose with domain-specific boundaries",
        "boundaries": ["First published normative condition for downstream consumers.",
                       "Second published normative condition for downstream consumers."],
        "tasks": [{"id": "DOWNSTREAM", "depends_on": ["SECRET_LABEL"]}],
    }))
    chunks, scope = selected_surface(
        root, yaml_source,
        {"mode": "yaml-fields", "fields": ["purpose", "boundaries"]}
    )
    assert len(chunks) == 3
    assert "SECRET_LABEL" not in repr(chunks)
    assert scope["claim_role"] == "RESEARCH_CANDIDATE_NOT_AUTHORITY_APPROVED"

    product = save("docs/product.yaml", yaml.safe_dump({
        "content": {"requirements": [
            {"id": "R-A", "status": "ACCEPTED",
             "statement": "A normative business rule is published for consumers."},
            {"id": "R-B", "status": "ACCEPTED",
             "statement": "Another published requirement is separately identifiable."},
        ]}
    }))
    chunks, scope = selected_surface(
        root, product, {"mode": "accepted-product-requirements"}
    )
    assert len(chunks) == 2 and all("ACCEPTED PRODUCT" in x for x in chunks)
    assert scope["public_surface_truncated"] is False

    broken = yaml.safe_load((root / "docs/product.yaml").read_text())
    broken["content"]["requirements"][1]["status"] = "DRAFT"
    (root / "docs/product.yaml").write_text(yaml.safe_dump(broken))
    try:
        selected_surface(root, product, {"mode": "accepted-product-requirements"})
    except ValueError:
        pass
    else:
        raise AssertionError("unaccepted product statement cannot silently vanish")

    for headings in (["Not present"], ["Purpose", "Purpose"]):
        try:
            selected_surface(root, src, {"mode": "markdown-sections", "headings": headings})
        except ValueError:
            pass
        else:
            if headings == ["Not present"]:
                raise AssertionError("missing selector cannot be silently repaired")
            # Repetition is checked by the selector manifest, not section extraction.
    save("docs/provider.md", markdown + "\n## Purpose\n\nA duplicated independent published purpose must not be ambiguous.\n")
    try:
        _markdown_section((root / "docs/provider.md").read_text(), "Purpose")
    except ValueError:
        pass
    else:
        raise AssertionError("ambiguous headings should fail closed")

    for invalid in ([], ["duplicate", "duplicate"]):
        if invalid:
            copy_manifest = yaml.safe_load(path.read_text())
            copy_manifest["providers"][0]["headings"] = invalid
        else:
            copy_manifest = yaml.safe_load(path.read_text())
            copy_manifest["providers"] = copy_manifest["providers"][:-1]
        file = root / "manifest.yaml"
        file.write_text(yaml.safe_dump(copy_manifest), encoding="utf-8")
        try:
            load_selectors(file, pin=PIN, target=TARGET, expected=PROVIDER_IDS)
        except ValueError:
            pass
        else:
            raise AssertionError("incomplete or invalid manifest accepted")
print("CDR research-owned source surfaces: PASS")
