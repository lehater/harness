#!/usr/bin/env python3
"""Pinned, read-only CDR source-change and topology-change routing."""
from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from evals.cdr_contract_change import plan_change
from evals.project_discovery_snapshot import DiscoveryError


def git(root: Path, *args: str) -> str:
    return subprocess.check_output(
        ["git", "-C", str(root), *args], text=True,
        stderr=subprocess.DEVNULL,
    ).strip()


def write(root: Path, name: str, value: object) -> None:
    target = root / name
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        value if isinstance(value, str) else yaml.safe_dump(value, sort_keys=False),
        encoding="utf-8",
    )


def commit(root: Path, label: str) -> str:
    git(root, "add", ".")
    git(root, "commit", "-m", label)
    return git(root, "rev-parse", "HEAD")


def failure(call, expected: str) -> None:
    try:
        call()
    except DiscoveryError as exc:
        assert expected in str(exc), str(exc)
    else:
        raise AssertionError("expected rejection: " + expected)


with tempfile.TemporaryDirectory(prefix="harness-cdr-change-") as tmp:
    root = Path(tmp)
    git(root, "init")
    git(root, "config", "user.email", "cdreval@example.invalid")
    git(root, "config", "user.name", "CDR Test")
    graph = {
        "version": 1, "kind": "harness-engineering-graph", "id": "EXAMPLE",
        "authorities": [
            {"id": aid, "responsibility": "Own " + aid,
             "boundary": {
                 "semantic_cohesion": aid + " decisions",
                 "independent_change": aid + " independent decisions",
                 "public_contract": aid + " accepted knowledge"},
             "produces": [{"capability": cap,
                           "knowledge_kind": "domain-model",
                           "requires": [{"capability": p} for p in deps]}]}
            for aid, cap, deps in [
                ("PRODUCT", "x.product", []),
                ("MODEL", "x.model", ["x.product"]),
                ("INTERFACE", "x.interface", ["x.model"]),
            ]
        ],
        "consumers": [{"id": "TEST", "purpose": "Test public surface",
                       "requires": [{"capability": "x.interface"}]}],
        "terminal_capabilities": [],
    }
    core = {"questions": [], "artifacts": [
        {"id": cid, "authority": aid, "path": "docs/" + cid + ".md",
         "provides": [cid], "depends_on": []}
        for aid, cid in [("PRODUCT", "x.product"),
                         ("MODEL", "x.model"),
                         ("INTERFACE", "x.interface")]
    ]}
    baseline = {"reviews": [
        {"capability": cid, "revision": 1}
        for cid in ("x.product", "x.model", "x.interface")
    ]}
    write(root, ".harness/engineering-graph.yaml", graph)
    write(root, ".harness/core.yaml", core)
    write(root, ".harness/semantic-baseline.yaml", baseline)
    for cid in ("x.product", "x.model", "x.interface"):
        write(root, "docs/" + cid + ".md",
              "# Semantic output\n\nAccepted rule v1 for " + cid + ".\n")
    first = commit(root, "initial reviewed knowledge")
    no_change = plan_change(root, before_sha=first, after_sha=first)
    assert no_change["status"] == "NO_CDR_SCOPE_CHANGE_DETECTED"
    assert not no_change["cdr_review_targets"]
    assert no_change["automatic_writeback_allowed"] is False

    # Reviewed source revision: direct consumers may require CDR reconsideration;
    # indirect downstream stays Lifecycle-owned.
    write(root, "docs/x.product.md",
          "# Semantic output\n\nAccepted changed rule v2.\n")
    baseline["reviews"][0]["revision"] = 2
    write(root, ".harness/semantic-baseline.yaml", baseline)
    second = commit(root, "reviewed product change")
    change = plan_change(root, before_sha=first, after_sha=second)
    assert change["status"] == "REVIEW_REQUIRED"
    assert [x["capability"] for x in change["cdr_review_targets"]] == ["x.model"]
    assert change["lifecycle_only_transitive_scope"] == ["x.interface"]
    assert next(x for x in change["changed_capabilities"]
                if x["capability"] == "x.product")["reasons"] == [
                    "REVIEW_REVISION_CHANGED", "REVIEWED_SOURCE_CONTENT_CHANGED"]
    assert change["semantic_necessity_verified"] is False

    # Changed topology needs owner review; no graph update authorization.
    graph["authorities"][2]["produces"][0]["requires"].append(
        {"capability": "x.product"}
    )
    write(root, ".harness/engineering-graph.yaml", graph)
    third = commit(root, "changed topology")
    topology = plan_change(root, before_sha=second, after_sha=third)
    assert [x["capability"] for x in topology["cdr_review_targets"]] == ["x.interface"]
    assert "PREREQUISITE_TOPOLOGY_CHANGED" in topology["changed_capabilities"][0]["reasons"]
    assert topology["acceptance_or_graph_mutation_authorized"] is False

    # Source content without review revision is not accepted source change.
    write(root, "docs/x.product.md",
          "# Semantic output\n\nUnreviewed replacement.\n")
    fourth = commit(root, "unreviewed source update")
    unresolved = plan_change(root, before_sha=third, after_sha=fourth)
    assert unresolved["status"] == "BLOCKED_UNREVIEWED_SOURCE_CHANGE"
    assert unresolved["unreviewed_changes"] == ["x.product"]
    assert unresolved["automatic_writeback_allowed"] is False
    failure(lambda: plan_change(root, before_sha=fourth, after_sha=first),
            "project commit mismatch")
    failure(lambda: plan_change(root, before_sha="0" * 40, after_sha=fourth),
            "required pinned Git source unavailable")
    (root / "docs/x.model.md").write_text("dirty", encoding="utf-8")
    failure(lambda: plan_change(root, before_sha=third, after_sha=fourth),
            "project commit mismatch")

print("CDR contract change and lifecycle boundary: PASS")
