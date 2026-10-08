"""Read-only CDR reconsideration preflight across two pinned project commits.

Lifecycle already owns semantic currentness and prerequisite-topology staleness.
This module identifies potentially affected dependency decisions only.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path, PurePosixPath
from typing import Any

import yaml

from evals.project_discovery_snapshot import DiscoveryError, _commit
from harness.project_model.engineering_graph import (
    producer_index, production_index, validate_engineering_graph,
)

GRAPH = ".harness/engineering-graph.yaml"
CORE = ".harness/core.yaml"
BASELINE = ".harness/semantic-baseline.yaml"


def _git(root: Path, *args: str) -> bytes:
    try:
        return subprocess.check_output(
            ["git", "-C", str(root), *args], stderr=subprocess.DEVNULL, timeout=15
        )
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
        raise DiscoveryError("required pinned Git source unavailable") from exc


def _path(value: str) -> str:
    if (not isinstance(value, str) or not value or "\\" in value
            or PurePosixPath(value).is_absolute()
            or ".." in PurePosixPath(value).parts):
        raise DiscoveryError("invalid canonical source path")
    return value


def _at(root: Path, sha: str, path: str) -> bytes:
    return _git(root, "show", f"{sha}:{_path(path)}")


def _yaml_at(root: Path, sha: str, path: str) -> dict[str, Any]:
    try:
        value = yaml.safe_load(_at(root, sha, path))
    except yaml.YAMLError as exc:
        raise DiscoveryError(f"invalid pinned YAML: {path}") from exc
    if not isinstance(value, dict):
        raise DiscoveryError(f"invalid pinned mapping: {path}")
    return value


def _accepted_sources(root: Path, sha: str, graph: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Project-native review inventory; no inferred or fabricated acceptance."""
    baseline = _yaml_at(root, sha, BASELINE)
    core = _yaml_at(root, sha, CORE)
    reviews: dict[str, int] = {}
    for item in baseline.get("reviews", []):
        if not isinstance(item, dict):
            raise DiscoveryError("invalid semantic review record")
        cid, revision = item.get("capability"), item.get("revision")
        if (not isinstance(cid, str) or not cid or cid in reviews
                or type(revision) is not int or revision < 1):
            raise DiscoveryError("duplicate or invalid semantic review revision")
        reviews[cid] = revision
    if not isinstance(baseline.get("reviews"), list):
        raise DiscoveryError("semantic review inventory missing")
    artifacts = core.get("artifacts")
    if not isinstance(artifacts, list):
        raise DiscoveryError("Core artifact inventory missing")
    registrations: dict[str, dict[str, str]] = {}
    for artifact in artifacts:
        if not isinstance(artifact, dict) or not isinstance(artifact.get("provides"), list):
            raise DiscoveryError("invalid Core artifact registration")
        for cid in artifact["provides"]:
            if not isinstance(cid, str) or not cid or cid in registrations:
                raise DiscoveryError("ambiguous Core Capability provider")
            registrations[cid] = {"path": _path(artifact.get("path")),
                                  "authority": artifact.get("authority")}
    owners = producer_index(graph)
    result: dict[str, dict[str, Any]] = {}
    for cid, revision in reviews.items():
        registered = registrations.get(cid)
        if registered is None or owners.get(cid) != registered["authority"]:
            raise DiscoveryError(f"reviewed provider lacks matching Core/Authority: {cid}")
        source = registered["path"]
        result[cid] = {
            "revision": revision,
            "path": source,
            "sha256": hashlib.sha256(_at(root, sha, source)).hexdigest(),
        }
    return result


def _snapshot(root: Path, sha: str) -> dict[str, Any]:
    graph = _yaml_at(root, sha, GRAPH)
    validate_engineering_graph(graph)
    productions = production_index(graph)
    if len(productions) > 5000:
        raise DiscoveryError("CDR change preflight exceeds 5000 Capabilities")
    authorities = {item["id"]: item for item in graph["authorities"]}
    return {
        "owners": producer_index(graph),
        "productions": productions,
        "public_contracts": {
            aid: value["boundary"]["public_contract"]
            for aid, value in authorities.items()
        },
        "sources": _accepted_sources(root, sha, graph),
    }


def evaluate_changes(before: dict[str, Any], after: dict[str, Any]) -> dict[str, Any]:
    """Pure, deterministic conservative routing of semantic dependency risks."""
    old, new = before["productions"], after["productions"]
    changed: dict[str, list[str]] = {}
    for cid in sorted(set(old) | set(new)):
        reasons: list[str] = []
        a, b = old.get(cid), new.get(cid)
        if a is None:
            reasons.append("PRODUCTION_ADDED")
        elif b is None:
            reasons.append("PRODUCTION_REMOVED")
        else:
            if before["owners"][cid] != after["owners"][cid]:
                reasons.append("AUTHORITY_CHANGED")
            if (a.get("knowledge_kind") != b.get("knowledge_kind")
                    or a.get("semantic_claims") != b.get("semantic_claims")):
                reasons.append("PRODUCTION_OUTPUT_CONTRACT_CHANGED")
            if ({r["capability"] for r in a["requires"]}
                    != {r["capability"] for r in b["requires"]}):
                reasons.append("PREREQUISITE_TOPOLOGY_CHANGED")
            if (a["requires"] != b["requires"]
                    and "PREREQUISITE_TOPOLOGY_CHANGED" not in reasons):
                # Changed subject is material; list ordering is not.
                if ({json.dumps(r, sort_keys=True) for r in a["requires"]}
                        != {json.dumps(r, sort_keys=True) for r in b["requires"]}):
                    reasons.append("PREREQUISITE_SUBJECT_CHANGED")
        owner_before = before["owners"].get(cid)
        owner_after = after["owners"].get(cid)
        if (owner_before in before["public_contracts"]
                and owner_after in after["public_contracts"]
                and before["public_contracts"][owner_before] != after["public_contracts"][owner_after]):
            reasons.append("AUTHORITY_PUBLIC_CONTRACT_CHANGED")
        source_before = before["sources"].get(cid)
        source_after = after["sources"].get(cid)
        if source_before is None and source_after is not None:
            reasons.append("SEMANTIC_REVIEW_REGISTERED")
        elif source_before is not None and source_after is None:
            reasons.append("SEMANTIC_REVIEW_WITHDRAWN")
        elif source_before is not None and source_after is not None:
            if source_before["path"] != source_after["path"]:
                reasons.append("ACCEPTED_SOURCE_REGISTRATION_CHANGED")
            if source_before["revision"] != source_after["revision"]:
                reasons.append("REVIEW_REVISION_CHANGED")
            if source_before["sha256"] != source_after["sha256"]:
                reasons.append(
                    "REVIEWED_SOURCE_CONTENT_CHANGED"
                    if source_before["revision"] != source_after["revision"]
                    else "SOURCE_CHANGED_WITHOUT_REVIEW_REVISION"
                )
        if reasons:
            changed[cid] = reasons

    reverse: dict[str, set[str]] = {cid: set() for cid in new}
    for target, prod in new.items():
        for entry in prod["requires"]:
            reverse[entry["capability"]].add(target)
    direct = {target for source in changed for target in reverse.get(source, ())}
    contract_reasons = {
        "PRODUCTION_ADDED", "AUTHORITY_CHANGED",
        "PRODUCTION_OUTPUT_CONTRACT_CHANGED",
        "PREREQUISITE_TOPOLOGY_CHANGED",
        "PREREQUISITE_SUBJECT_CHANGED",
        "AUTHORITY_PUBLIC_CONTRACT_CHANGED",
    }
    own_review = {
        cid for cid, reasons in changed.items()
        if cid in new and contract_reasons.intersection(reasons)
    }
    review = sorted(own_review | direct)
    affected = set(review)
    queue = list(review)
    while queue:
        for child in reverse.get(queue.pop(), ()):
            if child not in affected:
                affected.add(child)
                queue.append(child)
    return {
        "changed_capabilities": [
            {"capability": cid, "reasons": reasons}
            for cid, reasons in changed.items()
        ],
        "cdr_review_targets": [
            {
                "capability": cid,
                "reasons": (["OWN_CONTRACT_OR_EVIDENCE_CHANGED"] if cid in own_review else [])
                           + (["DIRECT_PROVIDER_CHANGED"] if cid in direct else []),
            }
            for cid in review
        ],
        "lifecycle_only_transitive_scope": sorted(affected - set(review)),
        "unreviewed_changes": sorted(
            cid for cid, reasons in changed.items()
            if "SOURCE_CHANGED_WITHOUT_REVIEW_REVISION" in reasons
        ),
        "semantic_necessity_verified": False,
        "acceptance_or_graph_mutation_authorized": False,
        "automatic_writeback_allowed": False,
    }


def plan_change(root: Path, *, before_sha: str, after_sha: str) -> dict[str, Any]:
    root = root.resolve()
    _commit(root, after_sha)
    if not re.fullmatch(r"[a-f0-9]{40}", before_sha or ""):
        raise DiscoveryError("before pin must be full Git SHA")
    _git(root, "merge-base", "--is-ancestor", before_sha, after_sha)
    before = _snapshot(root, before_sha)
    after = _snapshot(root, after_sha)
    analysis = evaluate_changes(before, after)
    return {
        "kind": "harness-cdr-contract-change-preflight-v1",
        "before_snapshot": before_sha,
        "after_snapshot": after_sha,
        "status": (
            "BLOCKED_UNREVIEWED_SOURCE_CHANGE" if analysis["unreviewed_changes"]
            else "REVIEW_REQUIRED" if analysis["cdr_review_targets"]
            else "NO_CDR_SCOPE_CHANGE_DETECTED"
        ),
        **analysis,
    }


def main() -> int:
    p = argparse.ArgumentParser(
        description="Read-only CDR contract-change reconsideration preflight"
    )
    p.add_argument("--project-root", type=Path, required=True)
    p.add_argument("--before", required=True)
    p.add_argument("--after", required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    try:
        result = plan_change(
            args.project_root, before_sha=args.before, after_sha=args.after
        )
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(result, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(json.dumps({
            "status": result["status"],
            "review_targets": len(result["cdr_review_targets"]),
            "automatic_writeback_allowed": False,
        }))
        return 2 if result["status"].startswith("BLOCKED_") else 0
    except (DiscoveryError, ValueError, TypeError, KeyError, OSError) as exc:
        print(json.dumps({"status": "INVALID", "error": str(exc)}, ensure_ascii=False))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
