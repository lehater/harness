#!/usr/bin/env python3
"""Read-only target output contract readiness: evidence is not semantic truth."""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from evals.project_discovery_snapshot import DiscoveryError
from evals.project_target_contract_readiness import audit_target_contracts


def write(root: Path, relative: str, obj) -> None:
    dest = root / relative
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(yaml.safe_dump(obj, sort_keys=False), encoding="utf-8")


def git(root: Path, *args: str) -> str:
    return subprocess.check_output(
        ["git", "-C", str(root), *args], text=True,
        stderr=subprocess.DEVNULL,
    ).strip()


with tempfile.TemporaryDirectory(prefix="cdr-target-readiness-") as tmp:
    root = Path(tmp)
    git(root, "init")
    git(root, "config", "user.email", "test@example.invalid")
    git(root, "config", "user.name", "Target Readiness Test")
    graph = {
        "authorities": [
            {"id": "TACTICAL", "responsibility": "Own domain invariants",
             "boundary": {"public_contract": "Provides accepted domain meaning"},
             "produces": [{"capability": "x.target", "knowledge_kind": "domain-model",
                           "requires": []}]},
        ]
    }
    core = {"artifacts": [], "questions": []}
    baseline = {"reviews": []}
    write(root, ".harness/engineering-graph.yaml", graph)
    write(root, ".harness/core.yaml", core)
    write(root, ".harness/semantic-baseline.yaml", baseline)
    git(root, "add", ".")
    git(root, "commit", "-m", "planned output")
    first = git(root, "rev-parse", "HEAD")
    planned = audit_target_contracts(root, sha=first, targets=["x.target"])
    x = planned["cases"][0]
    assert x["status"] == "NOT_INDEPENDENTLY_ACCEPTED"
    assert x["producer"]["authority"] == "TACTICAL"
    assert "TARGET_CORE_ARTIFACT_NOT_REGISTERED_UNIQUELY" in x["blockers"]
    assert "TARGET_SEMANTIC_BASELINE_REVIEW_MISSING_OR_AMBIGUOUS" in x["blockers"]
    assert x["directness_review_eligible"] is False
    assert x["automatic_writeback_allowed"] is False

    core["artifacts"].append({
        "id": "TACTICAL-MODEL", "authority": "TACTICAL",
        "path": "docs/target-output.yaml", "provides": ["x.target"],
        "depends_on": [],
    })
    baseline["reviews"].append({
        "capability": "x.target", "revision": 1,
        "basis": "A recorded review of the model vocabulary and semantics.",
    })
    write(root, ".harness/core.yaml", core)
    write(root, ".harness/semantic-baseline.yaml", baseline)
    write(root, "docs/target-output.yaml", {
        "kind": "domain-model",
        "content": {
            "output_obligations": [
                {"id": "MODEL-01",
                 "description": "The model shall distinguish the meanings of recorded events."},
                {"id": "MODEL-02",
                 "description": "The model shall preserve links to the information the event concerns."},
            ],
        },
    })
    git(root, "add", ".")
    git(root, "commit", "-m", "registered, reviewed output")
    second = git(root, "rev-parse", "HEAD")
    with_artifact = audit_target_contracts(root, sha=second, targets=["x.target"])
    record = with_artifact["cases"][0]
    assert record["target_artifact"]["path"] == "docs/target-output.yaml"
    assert len(record["target_artifact"]["sha256"]) == 64
    assert record["semantic_baseline"]["revision"] == 1
    assert record["explicit_output_obligation_ids"] == ["MODEL-01", "MODEL-02"]
    assert record["blockers"] == ["INDEPENDENT_TARGET_OBLIGATION_ADJUDICATION_NOT_PROVEN"]
    assert record["independent_target_obligation_review_verified"] is False
    assert record["directness_review_eligible"] is False
    assert with_artifact["automatic_writeback_allowed"] is False

    # A markdown note containing text or copied strategic clauses is not
    # a separately machine-verifiable independent output obligation contract.
    core["artifacts"][0]["path"] = "docs/target-output.md"
    write(root, ".harness/core.yaml", core)
    (root / "docs/target-output.md").write_text(
        "# Domain\n\n## Output obligations\n\n- Preserve a key distinction.\n",
        encoding="utf-8",
    )
    git(root, "add", ".")
    git(root, "commit", "-m", "unstructured output")
    third = git(root, "rev-parse", "HEAD")
    markdown = audit_target_contracts(root, sha=third, targets=["x.target"])["cases"][0]
    assert markdown["explicit_output_obligation_ids"] == []
    assert "TARGET_STANDALONE_OUTPUT_OBLIGATIONS_NOT_VERIFIABLE" in markdown["blockers"]

    # A tracked source modification or mismatched commit must be rejected.
    try:
        audit_target_contracts(root, sha=second, targets=["x.target"])
    except DiscoveryError:
        pass
    else:
        raise AssertionError("must reject stale snapshot")
    (root / "docs/target-output.md").write_text("modified\n", encoding="utf-8")
    try:
        audit_target_contracts(root, sha=third, targets=["x.target"])
    except DiscoveryError:
        pass
    else:
        raise AssertionError("must reject tracked modifications")
    try:
        audit_target_contracts(root, sha=third, targets=["x.target", "x.target"])
    except DiscoveryError:
        pass
    else:
        raise AssertionError("must reject repeated targets")

print("dependency resolution target output readiness: PASS")
