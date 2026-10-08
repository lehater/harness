"""Evidence-grade preflight for a target's independently accepted output contract.

A production declaration, accepted *upstream* provider, and a model's proposal
do not constitute an independently accepted target artifact. This read-only
audit reports the gap against a pinned project checkout; even a registered
artifact cannot self-certify reviewer independence or semantic sufficiency.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from evals.project_discovery_snapshot import (
    DiscoveryError, _commit, _required_yaml, _resolve,
)


def _recorded_obligation_ids(file_path: Path) -> list[str]:
    """Detect an explicit standalone obligation section; do not infer one.

    This is a structural indicator only. Free-form prose and descriptive
    domain-model files are not silently promoted into an accepted contract.
    """
    suffix = file_path.suffix.lower()
    if suffix in (".yaml", ".yml"):
        record = _required_yaml(file_path)
        obligations = record.get("output_obligations")
        if obligations is None and isinstance(record.get("content"), dict):
            obligations = record["content"].get("output_obligations")
        if not isinstance(obligations, list) or not obligations:
            return []
        ids: list[str] = []
        for item in obligations:
            if not isinstance(item, dict):
                return []
            ident, desc = item.get("id"), item.get("description")
            if not isinstance(ident, str) or not ident.strip():
                return []
            if not isinstance(desc, str) or len(desc.strip()) < 30:
                return []
            ids.append(ident)
        return ids if len(ids) == len(set(ids)) else []
    # Markdown has no machine-stable output-obligation IDs in the PREP
    # project's current accepted artifact contract. Do not treat arbitrary
    # headings/paragraphs as independent executable requirements.
    return []


def audit_target_contracts(
    project_root: Path, *, sha: str, targets: list[str]
) -> dict[str, Any]:
    """Return nonauthorizing evidence for requested targets at exact git HEAD."""
    root = project_root.resolve()
    _commit(root, sha)
    if not isinstance(targets, list) or not targets or any(
        not isinstance(x, str) or not x for x in targets
    ) or len(targets) != len(set(targets)):
        raise DiscoveryError("nonempty unique target CapabilityIds required")
    core = _required_yaml(root / ".harness/core.yaml")
    baseline = _required_yaml(root / ".harness/semantic-baseline.yaml")
    graph = _required_yaml(root / ".harness/engineering-graph.yaml")
    records = core.get("artifacts")
    authorities = graph.get("authorities")
    reviews = baseline.get("reviews")
    if not isinstance(records, list) or not isinstance(authorities, list) or not isinstance(reviews, list):
        raise DiscoveryError("missing project Core, graph or semantic review inventory")

    producers: dict[str, list[dict[str, Any]]] = {}
    for authority in authorities:
        if not isinstance(authority, dict) or not isinstance(authority.get("id"), str):
            raise DiscoveryError("invalid Authority production")
        for prod in authority.get("produces", []):
            if not isinstance(prod, dict) or not isinstance(prod.get("capability"), str):
                raise DiscoveryError("invalid capability production")
            producers.setdefault(prod["capability"], []).append({
                "authority": authority["id"],
                "responsibility": authority.get("responsibility"),
                "public_contract": (authority.get("boundary") or {}).get("public_contract"),
                "knowledge_kind": prod.get("knowledge_kind"),
            })

    registered: dict[str, list[dict[str, Any]]] = {}
    for art in records:
        if not isinstance(art, dict):
            raise DiscoveryError("malformed Core artifact")
        for cid in art.get("provides", []):
            registered.setdefault(cid, []).append(art)

    reviews_by_target: dict[str, list[dict[str, Any]]] = {}
    for row in reviews:
        if not isinstance(row, dict) or not isinstance(row.get("capability"), str):
            raise DiscoveryError("malformed semantic baseline review")
        reviews_by_target.setdefault(row["capability"], []).append(row)

    findings = []
    for cid in targets:
        production = producers.get(cid, [])
        artifacts = registered.get(cid, [])
        semantic_reviews = reviews_by_target.get(cid, [])
        blockers = []
        if len(production) != 1:
            blockers.append("TARGET_PRODUCTION_MISSING_OR_AMBIGUOUS")
        if len(artifacts) != 1:
            blockers.append("TARGET_CORE_ARTIFACT_NOT_REGISTERED_UNIQUELY")
        if len(semantic_reviews) != 1:
            blockers.append("TARGET_SEMANTIC_BASELINE_REVIEW_MISSING_OR_AMBIGUOUS")
        if len(production) == 1 and len(artifacts) == 1 and (
            artifacts[0].get("authority") != production[0]["authority"]
        ):
            blockers.append("TARGET_ARTIFACT_AUTHORITY_MISMATCH")

        artifact_evidence: dict[str, Any] | None = None
        ids: list[str] = []
        if len(artifacts) == 1:
            path = artifacts[0].get("path")
            if not isinstance(path, str):
                blockers.append("TARGET_ARTIFACT_PATH_INVALID")
            else:
                file_path = _resolve(root, path)
                if not file_path.is_file():
                    blockers.append("TARGET_ARTIFACT_FILE_MISSING")
                else:
                    raw = file_path.read_bytes()
                    artifact_evidence = {
                        "path": path,
                        "sha256": hashlib.sha256(raw).hexdigest(),
                        "core_artifact_id": artifacts[0].get("id"),
                    }
                    ids = _recorded_obligation_ids(file_path)
                    if not ids:
                        blockers.append("TARGET_STANDALONE_OUTPUT_OBLIGATIONS_NOT_VERIFIABLE")

        review_evidence = None
        if len(semantic_reviews) == 1:
            revision = semantic_reviews[0].get("revision")
            basis = semantic_reviews[0].get("basis")
            review_evidence = {
                "revision": revision,
                "basis_present": isinstance(basis, str) and len(basis.strip()) >= 30,
            }
            if type(revision) is not int or revision < 1 or not review_evidence["basis_present"]:
                blockers.append("TARGET_REVIEW_REVISION_OR_BASIS_INVALID")

        # Current PREP semantic baseline has a textual basis, but no separate
        # machine-verifiable evidence of independent review of each target
        # output obligation. NEVER infer independence from the baseline alone.
        blockers.append("INDEPENDENT_TARGET_OBLIGATION_ADJUDICATION_NOT_PROVEN")

        findings.append({
            "target_capability": cid,
            "status": "NOT_INDEPENDENTLY_ACCEPTED",
            "producer": production[0] if len(production) == 1 else None,
            "target_artifact": artifact_evidence,
            "semantic_baseline": review_evidence,
            "explicit_output_obligation_ids": ids,
            "blockers": sorted(set(blockers)),
            "accepted_upstream_constraints_are_not_target_acceptance": True,
            "independent_target_obligation_review_verified": False,
            "directness_review_eligible": False,
            "automatic_writeback_allowed": False,
        })
    return {
        "kind": "harness-cdr-target-output-readiness",
        "version": 1,
        "source_snapshot": sha,
        "status": "BLOCKED_PENDING_INDEPENDENT_TARGET_ACCEPTANCE",
        "cases": findings,
        "semantic_correctness_independently_verified_by_code": False,
        "automatic_writeback_allowed": False,
    }


def main() -> int:
    p = argparse.ArgumentParser(description="Read-only pinned target output acceptance audit")
    p.add_argument("--project-root", type=Path, required=True)
    p.add_argument("--commit", required=True)
    p.add_argument("--config", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    try:
        config = _required_yaml(args.config)
        selections = config.get("targets")
        if not isinstance(selections, list):
            raise DiscoveryError("target pilot configuration missing")
        result = audit_target_contracts(
            args.project_root, sha=args.commit,
            targets=[t["capability"] for t in selections],
        )
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print("CDR_TARGET_OUTPUT_READINESS_BEGIN")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        print("CDR_TARGET_OUTPUT_READINESS_END")
        return 0
    except (DiscoveryError, KeyError, OSError, ValueError, TypeError) as exc:
        print(json.dumps({"status": "INVALID", "error": str(exc)}, ensure_ascii=False))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
