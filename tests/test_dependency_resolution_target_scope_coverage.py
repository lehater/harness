#!/usr/bin/env python3
"""Pin-bound accepted source-unit ledger cannot certify draft target coverage."""
from __future__ import annotations

import copy
from pathlib import Path
import subprocess
import sys
import tempfile

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from evals.project_discovery_snapshot import DiscoveryError
from evals.project_target_scope_coverage import audit_draft_coverage


def put(root: Path, path: str, value) -> None:
    dest = root / path
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(
        value if isinstance(value, str) else yaml.safe_dump(value, sort_keys=False),
        encoding="utf-8",
    )


def git(root: Path, *args: str) -> str:
    return subprocess.check_output(
        ["git", "-C", str(root), *args], text=True,
        stderr=subprocess.DEVNULL,
    ).strip()


with tempfile.TemporaryDirectory(prefix="cdr-scope-units-") as dirname:
    root = Path(dirname)
    git(root, "init")
    git(root, "config", "user.name", "Coverage Fixture")
    git(root, "config", "user.email", "fixture@example.invalid")
    source = "docs/accepted.md"
    put(root, source, (
        "# Accepted Scope\n\n"
        "## Current Information\n\n"
        "The target needs semantically distinguishable meanings of information.\n\n"
        "- Relationships shall preserve their independently meaningful types.\n"
        "- Knowledge meaning does not imply mastery of that knowledge.\n\n"
        "## Cross Information Contract\n\n"
        "References to historical facts cannot redefine current information meanings.\n\n"
        "## Strategic Ownership\n\n"
        "The semantic owner defines domain responsibility independently from the application.\n\n"
        "## Negative Boundaries\n\n"
        "The domain model does not own UI, persistence, runtime or learner assessment.\n\n"
        "## Application Activities\n\n"
        "Exploration and selection are consumer workflows, not separately owned domain meanings.\n"
    ))
    put(root, "docs/product.yaml", {
        "content": {
            "requirements": [
                {"id": "REQ-1", "status": "ACCEPTED",
                 "statement": "Preserve every meaningful relationship type."},
                {"id": "REQ-2", "status": "ACCEPTED",
                 "statement": "Allow presentation of meaningful information to users."},
                {"id": "REQ-3", "status": "DRAFT",
                 "statement": "Create a mandatory fixed knowledge taxonomy."},
            ]
        }
    })
    put(root, ".harness/core.yaml", {
        "artifacts": [
            {"id": "SCOPE", "authority": "MODEL", "path": source,
             "provides": ["x.accepted-scope"]},
            {"id": "PRODUCT", "authority": "PRODUCT", "path": "docs/product.yaml",
             "provides": ["x.product"]},
        ],
    })
    put(root, ".harness/semantic-baseline.yaml", {
        "reviews": [
            {"capability": "x.accepted-scope", "revision": 2},
            {"capability": "x.product", "revision": 1},
        ],
    })
    put(root, ".harness/engineering-graph.yaml", {
        "authorities": [{
            "id": "TACTICAL",
            "produces": [{"capability": "x.target", "knowledge_kind": "model"}],
        }],
    })
    git(root, "add", ".")
    git(root, "commit", "-m", "accepted upstream only")
    sha = git(root, "rev-parse", "HEAD")
    headings = [
        ("Current Information", "MODEL_CONTEXT"),
        ("Cross Information Contract", "CROSS_CONTEXT"),
        ("Strategic Ownership", "STRATEGIC_RESPONSIBILITY"),
        ("Negative Boundaries", "BOUNDARY_POLICY"),
        ("Application Activities", "APPLICATION_SEPARATION"),
    ]
    base = {
        "kind": "harness-cdr-target-output-contract-candidates",
        "status": "OPERATOR_DRAFT_NOT_ACCEPTED",
        "source_commit": sha,
        "owning_authority": "TACTICAL",
        "no_automatic_writeback": True,
        "target_contracts": [{
            "target_capability": "x.target",
            "target_contract_status": "NEEDS_INDEPENDENT_AUTHORITY_REVIEW",
            "coverage_scope": [
                {"type": "MARKDOWN_SECTION", "role": role,
                 "path": source, "heading": heading}
                for heading, role in headings
            ] + [
                {"type": "ACCEPTED_PRODUCT_REQUIREMENTS", "role": "PRODUCT_CONSTRAINTS",
                 "path": "docs/product.yaml"},
            ],
            "candidate_obligations": [{
                "id": "T-1",
                "status": "CANDIDATE_NOT_ACCEPTED",
                "description": "Define the model meanings and prevent inappropriate assessment of people.",
                "upstream_scope": [{"path": source, "heading": "Current Information"}],
            }],
        }],
    }
    good = audit_draft_coverage(root, sha=sha, draft=base)
    assert good["status"] == "PENDING_INDEPENDENT_TARGET_SCOPE_REVIEW"
    assert good["independent_authority_review_performed"] is False
    assert good["automatic_writeback_allowed"] is False
    case = good["cases"][0]
    assert case["target_capability"] == "x.target"
    assert case["candidate_obligation_count"] == 1
    assert case["source_unit_count"] >= 8
    assert case["unreviewed_unit_count"] == case["source_unit_count"]
    assert case["units_without_same_section_candidate"] > 0
    assert case["accepted_target_contract_established"] is False
    assert case["semantic_completeness_established"] is False
    assert len({x["source_unit_id"] for x in case["source_units"]}) == case["source_unit_count"]
    accepted_reqs = {
        x["source_local_id"] for x in case["source_units"]
        if x["scope_role"] == "PRODUCT_CONSTRAINTS"
    }
    assert accepted_reqs == {"REQ-1", "REQ-2"}
    assert "REQ-3" not in repr(good)
    assert any(
        x["candidate_obligations_with_same_source_section"] == ["T-1"]
        for x in case["source_units"]
    )
    assert any(
        not x["candidate_obligations_with_same_source_section"]
        for x in case["source_units"]
    )

    # Under the same accepted sources, an apparently comprehensive draft
    # cannot assert itself as accepted or automatically cover all source units.
    illegal = copy.deepcopy(base)
    illegal["target_contracts"][0]["candidate_obligations"][0]["status"] = "ACCEPTED"
    try:
        audit_draft_coverage(root, sha=sha, draft=illegal)
    except DiscoveryError:
        pass
    else:
        raise AssertionError("draft acceptance promotion must be rejected")

    illegal = copy.deepcopy(base)
    illegal["target_contracts"][0]["coverage_scope"].pop(1)
    try:
        audit_draft_coverage(root, sha=sha, draft=illegal)
    except DiscoveryError:
        pass
    else:
        raise AssertionError("cross-context scope omission must fail closed")

    illegal = copy.deepcopy(base)
    illegal["target_contracts"][0]["coverage_scope"].append(
        illegal["target_contracts"][0]["coverage_scope"][0]
    )
    try:
        audit_draft_coverage(root, sha=sha, draft=illegal)
    except DiscoveryError:
        pass
    else:
        raise AssertionError("duplicated source scope must fail closed")

    illegal = copy.deepcopy(base)
    illegal["target_contracts"][0]["candidate_obligations"][0]["upstream_scope"] = [
        {"path": source, "heading": "A heading not in the accepted source"}
    ]
    try:
        audit_draft_coverage(root, sha=sha, draft=illegal)
    except DiscoveryError:
        pass
    else:
        raise AssertionError("nonexistent upstream source heading must fail closed")

    illegal = copy.deepcopy(base)
    illegal["target_contracts"][0]["coverage_scope"][0]["path"] = "docs/unregistered.md"
    try:
        audit_draft_coverage(root, sha=sha, draft=illegal)
    except DiscoveryError:
        pass
    else:
        raise AssertionError("unaccepted source must fail closed")

    try:
        audit_draft_coverage(root, sha="0" * 40, draft=base)
    except DiscoveryError:
        pass
    else:
        raise AssertionError("incorrect snapshot must fail closed")

    # Tracked source drift must be caught even with the same declared SHA.
    (root / source).write_text("modified\n", encoding="utf-8")
    try:
        audit_draft_coverage(root, sha=sha, draft=base)
    except DiscoveryError:
        pass
    else:
        raise AssertionError("dirty source must fail closed")

print("dependency resolution target scope source-unit coverage: PASS")
