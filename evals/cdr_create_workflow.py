"""Experimental end-to-end CREATE CDR handoff; no graph adoption.

Owns orchestration only. Reuses source-blind generic discovery, request-bound
external evaluator format, cycle-checked post-model reconciliation, and
existing CDR governance dossier. It never updates Core/Engineering Graph and
never treats operator-draft reviews as trusted Authority acceptance.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any

from evals.cdr_operational import prepare_intake, reconcile_intake
from evals.cdr_governance_packet import (
    build_decision_dossier, validate_draft_review, digest,
)
from evals.dependency_resolution_process_driver import build_blinded_request
from evals.project_discovery_snapshot import DiscoveryError, _required_yaml

KIND = "harness-cdr-create-experimental-handoff"
GATE_KIND = "harness-cdr-create-readiness-v1"


def prepare(root: Path, *, sha: str, intake: dict[str, Any]) -> dict[str, Any]:
    inputs = prepare_intake(root, sha=sha, intake=intake)
    target = inputs["cases"][0]["target"]["capability"]
    run_id = "CDR-CREATE-" + hashlib.sha256(json.dumps({
        "project_commit": sha, "target": target, "intake": intake,
    }, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()[:24]
    request = build_blinded_request(inputs, run_id=run_id,
                                    adapter_binding={"provider": "github-copilot",
                                                     "mode": "tool-free"})
    if "declared_requires" in json.dumps(request):
        raise DiscoveryError("provider request would reveal target edges")
    record = {
        "kind": KIND, "version": 1, "phase": "AWAITING_EXTERNAL_EVALUATOR",
        "project_commit": sha, "target_capability": target,
        "source_intake_sha256": digest(intake),
        "inputs": inputs, "request": request,
        "provider_catalog_discovered_automatically": True,
        "provider_catalog_size": len(inputs["cases"][0]["provider_catalog"]),
        "target_obligations_independently_accepted": False,
        "source_export_ownership_independently_accepted": False,
        "automatic_writeback_allowed": False,
    }
    return {**record, "handoff_sha256": digest(record)}


def _verify(root: Path, sha: str, intake: dict[str, Any],
            handoff: dict[str, Any]) -> None:
    fresh = prepare(root, sha=sha, intake=intake)
    if handoff != fresh:
        raise DiscoveryError("stale, modified or foreign CREATE CDR handoff")


def _predictions(handoff: dict[str, Any],
                 response: dict[str, Any]) -> dict[str, Any]:
    request = handoff["request"]
    if (response.get("version") != 1
            or response.get("kind") != "harness-dependency-resolution-evaluator-response"
            or response.get("request_id") != request["request_id"]
            or not isinstance(response.get("results"), list)
            or len(response["results"]) != 1):
        raise DiscoveryError("unbound external evaluator response")
    row = response["results"][0]
    if row.get("case_request_id") != request["cases"][0]["case_request_id"]:
        raise DiscoveryError("external response case binding mismatch")
    if (row.get("status") not in ("RESOLVED", "UNRESOLVED")
            or row.get("status") == "RESOLVED"
            and row.get("unresolved_obligations")):
        raise DiscoveryError("contradictory evaluator resolution status")
    return {
        "kind": "harness-dependency-resolution-predictions",
        "version": 1,
        "cases": [{
            "id": handoff["inputs"]["cases"][0]["id"],
            "status": row["status"],
            "proposed_requires": row.get("proposed_requires"),
            "input_needs": row.get("input_needs"),
            "unresolved_obligations": row.get("unresolved_obligations"),
        }],
    }


def reconcile(root: Path, *, sha: str, intake: dict[str, Any],
              handoff: dict[str, Any], response: dict[str, Any]) -> dict[str, Any]:
    _verify(root, sha, intake, handoff)
    predicted = _predictions(handoff, response)
    comparison = reconcile_intake(root, sha=sha, intake=intake,
                                  predictions=predicted)
    dossier = build_decision_dossier(root, sha=sha, intake=intake,
                                    predictions=predicted)
    if (comparison["status"] not in ("REVIEW_REQUIRED",
                                    "INVALID_PROPOSED_TOPOLOGY")
            or dossier.get("status") != "REVIEW_DOSSIER_NOT_AUTHORIZATION"
            or dossier["automatic_writeback_allowed"] is not False):
        raise DiscoveryError("CDR governance dossier unexpectedly authorizes writes")
    status = ("BLOCKED_INVALID_PROPOSED_TOPOLOGY"
              if comparison["cycle_blocks"]
              else "BLOCKED_PENDING_INDEPENDENT_AUTHORITY_DECISIONS")
    gate = {
        "kind": GATE_KIND, "version": 1,
        "status": status,
        "project_commit": sha,
        "target_capability": handoff["target_capability"],
        "source_intake_sha256": handoff["source_intake_sha256"],
        "handoff_sha256": handoff["handoff_sha256"],
        "request_id": handoff["request"]["request_id"],
        "frozen_provider_response_sha256": digest(response),
        "dossier_sha256": dossier["dossier_sha256"],
        "proposed_new_edges_not_approved": comparison["ADD"],
        "existing_edges_not_removed": comparison["UNASSESSED_EXISTING_EDGES"],
        "cycle_blocks": comparison["cycle_blocks"],
        "target_contract_independently_accepted": False,
        "provider_ownership_independently_accepted": False,
        "directness_semantically_adjudicated": False,
        "input_set_complete": False,
        "trusted_authority_transition_verified": False,
        "automatic_writeback_allowed": False,
    }
    result = {
        "kind": "harness-cdr-create-reviewed-handoff-v1", "version": 1,
        "status": "DRAFT_REVIEW_NOT_GRAPH_AUTHORIZATION",
        "gate": gate, "reconciliation": comparison, "dossier": dossier,
        "predictions": predicted,
        "automatic_writeback_allowed": False,
    }
    return {**result, "review_sha256": digest(result)}


def check_draft(root: Path, *, sha: str, intake: dict[str, Any],
                handoff: dict[str, Any], response: dict[str, Any],
                review: dict[str, Any], draft: dict[str, Any]) -> dict[str, Any]:
    actual = reconcile(root, sha=sha, intake=intake, handoff=handoff,
                       response=response)
    if actual != review:
        raise DiscoveryError("review changed since accepted source/model regeneration")
    verdict = validate_draft_review(actual["dossier"], draft)
    if verdict["governance_transition_authorized"] is not False:
        raise DiscoveryError("operator draft cannot authorize governance transition")
    return {
        "status": "DRAFT_VALIDATED_PENDING_TRUSTED_AUTHORITY",
        "source_snapshot": sha,
        "handoff_sha256": handoff["handoff_sha256"],
        "review_sha256": actual["review_sha256"],
        "review_result": verdict,
        "gate": actual["gate"],
        "automatic_writeback_allowed": False,
    }


def _write(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True,
                               indent=2) + "\n", encoding="utf-8")


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("phase", choices=("prepare", "reconcile", "check"))
    p.add_argument("--project-root", type=Path, required=True)
    p.add_argument("--commit", required=True)
    p.add_argument("--intake", type=Path, required=True)
    p.add_argument("--handoff", type=Path)
    p.add_argument("--response", type=Path)
    p.add_argument("--review", type=Path)
    p.add_argument("--draft", type=Path)
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()
    try:
        intake = _required_yaml(a.intake)
        if a.phase == "prepare":
            if a.handoff or a.response or a.review or a.draft:
                raise DiscoveryError("Phase A cannot receive hidden evaluation material")
            result = prepare(a.project_root, sha=a.commit, intake=intake)
        else:
            if not a.handoff or not a.response:
                raise DiscoveryError("Phase B needs frozen handoff and model response")
            handoff = json.loads(a.handoff.read_text(encoding="utf-8"))
            response = json.loads(a.response.read_text(encoding="utf-8"))
            if a.phase == "reconcile":
                if a.review or a.draft:
                    raise DiscoveryError("reconciliation cannot consume a reviewer conclusion")
                result = reconcile(a.project_root, sha=a.commit, intake=intake,
                                   handoff=handoff, response=response)
            else:
                if not a.review or not a.draft:
                    raise DiscoveryError("review check requires a dossier and a draft")
                result = check_draft(
                    a.project_root, sha=a.commit, intake=intake, handoff=handoff,
                    response=response,
                    review=json.loads(a.review.read_text(encoding="utf-8")),
                    draft=json.loads(a.draft.read_text(encoding="utf-8")),
                )
        _write(a.output, result)
        print(json.dumps({"status": result["status"],
                          "automatic_writeback_allowed": False}))
        return 0
    except (DiscoveryError, OSError, ValueError, TypeError, KeyError,
            IndexError) as e:
        print(json.dumps({"status": "INVALID", "error": str(e)}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
