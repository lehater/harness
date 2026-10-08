"""Read-only Authority-facing CDR review boundary.

Build a source-bound, content-addressed packet and verify an independent
operator's *draft* review against an EXACT regeneration from the project and
the frozen Copilot response. This does not attest identity, accept semantic
claims, transition governance, or authorize graph mutation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from evals.project_discovery_snapshot import DiscoveryError
from evals.cdr_prep_accepted_target_pilot import (
    PIN, SOURCE_MODE_V3, TARGET, _registry, build, reconcile,
)
from evals.cdr_atomic_consumption_review import TESTS

KIND = "harness-cdr-atomic-authority-review-packet"
DRAFT_KIND = "harness-cdr-atomic-authority-review-draft"
FACETS = ("target_outputs", "export_ownership", "direct_consumption", "input_coverage")
VERDICTS = {
    "target_outputs": {"REVIEW_NEEDED", "LIKELY_IN_SCOPE", "REJECT_DRAFT"},
    "export_ownership": {"REVIEW_NEEDED", "LIKELY_OWNED", "REJECT_DRAFT"},
    "direct_consumption": {"UNDETERMINED", "LIKELY_DIRECT", "LIKELY_MEDIATED", "REJECT_DRAFT"},
    "input_coverage": {"UNRESOLVED", "DRAFT_SCOPE_PLAUSIBLE", "REJECT_DRAFT"},
}
NO_TRUST = {
    "reviewer_identity_verified": False,
    "independent_authority_decision_verified": False,
    "target_obligations_accepted": False,
    "exported_claim_ownership_accepted": False,
    "directness_accepted": False,
    "input_coverage_accepted": False,
    "graph_update_authorized": False,
    "automatic_writeback_allowed": False,
}


def digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(
        value, sort_keys=True, ensure_ascii=False, separators=(",", ":")
    ).encode("utf-8")).hexdigest()


def _unique(rows: list[dict[str, Any]], key: str) -> dict[str, dict[str, Any]]:
    found = {}
    for row in rows:
        if not isinstance(row, dict):
            raise DiscoveryError("malformed review row")
        value = row.get(key)
        if not isinstance(value, str) or not value or value in found:
            raise DiscoveryError("missing/duplicate review identity")
        found[value] = row
    return found


def build_packet(root: Path, *, sha: str, inputs: dict[str, Any],
                 request: dict[str, Any], response: dict[str, Any]) -> dict[str, Any]:
    # Regeneration is mandatory: do not trust a caller-provided contrast.
    contrast = reconcile(
        root, sha=sha, inputs=inputs, request=request, response=response,
        surface_mode=SOURCE_MODE_V3,
    )
    prep = build(root, sha=sha, surface_mode=SOURCE_MODE_V3)
    sources, reviews, _, _ = _registry(root)
    case = prep["inputs"]["cases"][0]
    if contrast["source_surface_protocol"] != SOURCE_MODE_V3:
        raise DiscoveryError("non-atomic source protocol supplied")
    review_packet = contrast["atomic_consumption_review_not_authorization"]
    if review_packet is None or contrast["effective_resolution"] != "NOT_RESOLVED":
        raise DiscoveryError("cannot construct independent review from accepted graph result")
    outputs = []
    for item in review_packet["per_obligation"]:
        outputs.append({
            "id": item["obligation_id"],
            "owner_capability": TARGET,
            "owner_authority": sources[TARGET]["authority"],
            "target_artifact_path": sources[TARGET]["path"],
            "target_review_revision": reviews[TARGET]["revision"],
            "model_scope_status": item["status"],
            "independently_accepted": False,
        })
    claims = []
    for provider in case["provider_catalog"]:
        cid = provider["capability"]
        for idx, claim_id in enumerate(provider["source_scope"]["claim_ids"]):
            claims.append({
                "id": cid + "/" + claim_id,
                "claim_id": claim_id,
                "owner_capability": cid,
                "owner_authority": sources[cid]["authority"],
                "source_path": provider["source"],
                "source_sha256": provider["source_sha256"],
                "semantic_review_revision": reviews[cid]["revision"],
                "claim_index": idx,
                "exact_unaccepted_export": provider["semantic_surface"][idx],
                "independently_accepted": False,
            })
    _unique(outputs, "id")
    _unique(claims, "id")
    needs = []
    for item in review_packet["per_obligation"]:
        for need in item["candidate_needs"]:
            needs.append({
                "id": item["obligation_id"] + "/" + need["provider"] +
                      "/" + need["atomic_claim_id"],
                "target_obligation": item["obligation_id"],
                "provider_claim_id": need["provider"] + "/" + need["atomic_claim_id"],
                "model_rationale_only": need["consumption_rationale_model_only"],
                "source_also_delegates_target_export":
                    need["provider_cites_target_as_distinct_export_owner"],
                "mandatory_tests": list(TESTS),
                "cycle_blocked": any(
                    x["provider"] == need["provider"]
                    for x in contrast["cycle_blocks"]
                ),
                "independently_accepted": False,
            })
    _unique(needs, "id")
    coverage = [{
        "id": TARGET,
        "scope": "THREE_SOURCE_OWNED_TARGET_OUTCOMES_ONLY",
        "unaccounted_obligations": contrast["unaccounted_target_obligations"],
        "provider_catalog_partial": not contrast["all_available_provider_contracts_covered"],
        "declared_existing_edges_unassessed":
            contrast["declared_not_suggested_not_removal_evidence"],
        "model_status_not_adopted": contrast["model_status"],
        "independently_accepted": False,
    }]
    packet = {
        "kind": KIND, "version": 1,
        "status": "AWAITING_INDEPENDENT_AUTHORITY_REVIEWS",
        "project_commit": sha,
        "target_capability": TARGET,
        "target_authority": sources[TARGET]["authority"],
        "request_id": request["request_id"],
        "source_manifest_sha256":
            prep["source_fingerprints"]["atomic_draft_manifest"],
        "review_facets": {
            "target_outputs": outputs,
            "export_ownership": claims,
            "direct_consumption": needs,
            "input_coverage": coverage,
        },
        "current_diagnostics": {
            "status": contrast["status"],
            "effective_resolution": contrast["effective_resolution"],
            "cycle_blocks": contrast["cycle_blocks"],
            "unaccounted_obligations": contrast["unaccounted_target_obligations"],
            "model_hypothesis_preserved": contrast["model_requires"],
        },
        "bound_original_model_sha256": digest(response),
        "bound_original_request_sha256": digest(request),
        "nonpromotable_reason": (
            "A Core semantic revision or review label is not an independently "
            "verified Authority acceptance of specific source claims, target "
            "obligations, directness and completeness. Identity/trust-bound "
            "approval and graph mutation require separate authorized systems."
        ),
        **NO_TRUST,
    }
    return {**packet, "packet_sha256": digest(packet)}


def draft_template(packet: dict[str, Any]) -> dict[str, Any]:
    return {
        "kind": DRAFT_KIND, "version": 1,
        "status": "OPERATOR_DRAFT_NOT_ACCEPTED",
        "packet_sha256": packet["packet_sha256"],
        "project_commit": packet["project_commit"],
        "request_id": packet["request_id"],
        "target_capability": packet["target_capability"],
        "facets": {
            name: [{
                "id": item["id"], "decision": "REVIEW_NEEDED"
                  if name in ("target_outputs", "export_ownership")
                  else "UNDETERMINED" if name == "direct_consumption"
                  else "UNRESOLVED",
                "evidence": (
                    "No independently reviewed obligation-specific evidence "
                    "is attached; preserve this facet as a provisional draft."
                ),
                "review_authority": (
                    item.get("owner_authority")
                    if name != "direct_consumption" else packet["target_authority"]
                ) or packet["target_authority"],
            } for item in packet["review_facets"][name]]
            for name in FACETS
        },
        **NO_TRUST,
    }


def validate_draft(packet: dict[str, Any], draft: dict[str, Any]) -> dict[str, Any]:
    original = {k: v for k, v in packet.items() if k != "packet_sha256"}
    if (packet.get("kind") != KIND or packet.get("version") != 1
            or packet.get("status") != "AWAITING_INDEPENDENT_AUTHORITY_REVIEWS"
            or digest(original) != packet.get("packet_sha256")
            or any(packet.get(k) is not False for k in NO_TRUST)):
        raise DiscoveryError("tampered/acceptance-asserting review packet")
    if (set(draft) != {
            "kind", "version", "status", "packet_sha256", "project_commit",
            "request_id", "target_capability", "facets", *NO_TRUST.keys()
         } or draft.get("kind") != DRAFT_KIND or draft.get("version") != 1
            or draft.get("status") != "OPERATOR_DRAFT_NOT_ACCEPTED"
            or draft.get("packet_sha256") != packet["packet_sha256"]
            or draft.get("project_commit") != packet["project_commit"]
            or draft.get("request_id") != packet["request_id"]
            or draft.get("target_capability") != packet["target_capability"]
            or any(draft.get(k) is not False for k in NO_TRUST)):
        raise DiscoveryError("review draft is unbound or claims acceptance")
    facets = draft.get("facets")
    if not isinstance(facets, dict) or set(facets) != set(FACETS):
        raise DiscoveryError("independent review facets incomplete")
    for name in FACETS:
        rows = facets[name]
        if not isinstance(rows, list):
            raise DiscoveryError("review facet rows missing")
        expected = _unique(packet["review_facets"][name], "id")
        actual = _unique(rows, "id")
        if set(actual) != set(expected):
            raise DiscoveryError("missing/extra review decisions")
        for key, row in actual.items():
            item = expected[key]
            if (set(row) != {"id", "decision", "evidence", "review_authority"}
                    or row["decision"] not in VERDICTS[name]
                    or not isinstance(row["evidence"], str)
                    or len(row["evidence"].strip()) < 45):
                raise DiscoveryError("unsubstantiated/acceptance-implying facet review")
            required_authority = (
                item.get("owner_authority")
                if name != "direct_consumption" else packet["target_authority"]
            ) or packet["target_authority"]
            if row["review_authority"] != required_authority:
                raise DiscoveryError("review routing violates source/target Authority")
            if name == "direct_consumption" and (
                item["cycle_blocked"] and row["decision"] == "LIKELY_DIRECT"
            ):
                raise DiscoveryError("cyclic provider cannot be even provisionally direct")
            if name == "input_coverage" and (
                (item["unaccounted_obligations"]
                 or item["provider_catalog_partial"]
                 or item["declared_existing_edges_unassessed"])
                and row["decision"] == "DRAFT_SCOPE_PLAUSIBLE"
            ):
                raise DiscoveryError("unreviewed scope cannot be called plausibly complete")
    # Four facets remain independent draft decisions. A tentative direct
    # need cannot inherit owner/export and output-scope review from a citation.
    outputs = _unique(facets["target_outputs"], "id")
    ownership = _unique(facets["export_ownership"], "id")
    directness = _unique(facets["direct_consumption"], "id")
    for item in packet["review_facets"]["direct_consumption"]:
        row = directness[item["id"]]
        if row["decision"] == "LIKELY_DIRECT":
            if (outputs[item["target_obligation"]]["decision"] != "LIKELY_IN_SCOPE"
                    or ownership[item["provider_claim_id"]]["decision"] != "LIKELY_OWNED"):
                raise DiscoveryError(
                    "likely-direct draft cannot silently inherit ownership "
                    "or target output scope from a model citation"
                )
    coverage = facets["input_coverage"][0]
    if coverage["decision"] == "DRAFT_SCOPE_PLAUSIBLE":
        if (any(row["decision"] != "LIKELY_IN_SCOPE" for row in outputs.values())
                or any(row["decision"] == "UNDETERMINED" for row in directness.values())
                or any(item["cycle_blocked"]
                       for item in packet["review_facets"]["direct_consumption"])):
            raise DiscoveryError(
                "coverage draft cannot bypass separate output/directness reviews"
            )
    return {
        "kind": "harness-cdr-authority-review-draft-validation",
        "packet_sha256": packet["packet_sha256"],
        "status": "DRAFT_CONSISTENT_NOT_AUTHORITY_DECIDED",
        "all_facets_accounted_for": True,
        **NO_TRUST,
    }


def _read(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise DiscoveryError("expected JSON mapping")
    return value


def _write(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False)
                    + "\n", encoding="utf-8")


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("phase", choices=("prepare", "check"))
    p.add_argument("--project-root", type=Path, required=True)
    p.add_argument("--commit", default=PIN)
    p.add_argument("--inputs", type=Path, required=True)
    p.add_argument("--request", type=Path, required=True)
    p.add_argument("--response", type=Path, required=True)
    p.add_argument("--packet", type=Path, required=True)
    p.add_argument("--draft", type=Path, required=True)
    p.add_argument("--output", type=Path)
    a = p.parse_args()
    try:
        packet = build_packet(a.project_root, sha=a.commit, inputs=_read(a.inputs),
                              request=_read(a.request), response=_read(a.response))
        if a.phase == "prepare":
            _write(a.packet, packet)
            _write(a.draft, draft_template(packet))
            print(json.dumps({"status": packet["status"],
                              "sha256": packet["packet_sha256"]}))
        else:
            if _read(a.packet) != packet:
                raise DiscoveryError("review packet does not match pinned project/response")
            result = validate_draft(packet, _read(a.draft))
            if a.output:
                _write(a.output, result)
            print(json.dumps(result))
        return 0
    except (OSError, ValueError, TypeError, KeyError, IndexError, DiscoveryError) as e:
        print(json.dumps({"status": "INVALID", "error": str(e)}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
