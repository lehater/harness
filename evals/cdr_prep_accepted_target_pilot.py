"""Read-only CDR pilot on a reviewed, Core-registered PREP target.

Unlike the old planned-only project pilot, Phase A uses an existing *target*
artifact's actual structured output contract. The artifact and provider
revision records are real; per-obligation independent Authority approval is
NOT established. The target's declared requires are never read in Phase A.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from evals.project_discovery_snapshot import (
    DiscoveryError, _commit, _required_yaml, _resolve, _sha256,
    _markdown_claims, _yaml_claims,
)
from evals.dependency_resolution_process_driver import build_blinded_request
from evals.dependency_resolution_evidence import assess_predictions
from evals.cdr_provider_owned_surfaces import load_selectors, selected_surface
from evals.cdr_contract_owner_conflicts import delegated_target_claims
from evals.cdr_public_semantic_contract import prepare_draft

TARGET = "prep.knowledge-relation-classification"
PIN = "d9adf4ca51049894437f1ed3d4f74fe94936c896"
SOURCE_MODE_V1 = "RAW_PREFIX_V1"
SOURCE_MODE_V2 = "CANDIDATE_OWNED_SECTIONS_V2"
SOURCE_MODE_V3 = "ATOMIC_PUBLIC_CONTRACT_DRAFT_V1"
ATOMIC_MANIFEST = (
    Path(__file__).resolve().parents[1] /
    "spec/dependency-resolution/project-pilots/prep-public-semantic-contract-draft-v1.yaml"
)
SELECTOR_MANIFEST = (
    Path(__file__).resolve().parents[1] /
    "spec/dependency-resolution/project-pilots/prep-provider-owned-surface-selectors-v1.yaml"
)
PROVIDER_IDS = (
    "prep.model-context-strategy",
    "prep.product-capabilities",
    "prep.domain-strategy",
    "prep.knowledge-model",
    "prep.learning-design",
    "prep.learner-model",
    "prep.task-model",
    "prep.application-design",
)
NO_APPROVAL = {
    "independent_target_obligation_review_verified": False,
    "target_contract_per_obligation_acceptance": "NOT_ESTABLISHED",
    "semantic_directness_proven": False,
    "automatic_writeback_allowed": False,
}


def _registry(root: Path) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]], bytes, bytes]:
    core_path = root / ".harness/core.yaml"
    baseline_path = root / ".harness/semantic-baseline.yaml"
    core = _required_yaml(core_path)
    baseline = _required_yaml(baseline_path)
    by_provider: dict[str, dict[str, Any]] = {}
    for artifact in core.get("artifacts", []):
        if not isinstance(artifact, dict):
            raise DiscoveryError("malformed Core artifact")
        for name in artifact.get("provides", []):
            if name in by_provider:
                raise DiscoveryError(f"ambiguous Core provider {name}")
            by_provider[name] = artifact
    by_review: dict[str, dict[str, Any]] = {}
    for review in baseline.get("reviews", []):
        name = review.get("capability")
        if not isinstance(name, str) or name in by_review:
            raise DiscoveryError("invalid/duplicate baseline review")
        if type(review.get("revision")) is not int or review["revision"] < 1:
            raise DiscoveryError("invalid review revision")
        if not isinstance(review.get("basis"), str) or len(review["basis"].strip()) < 25:
            raise DiscoveryError("missing meaningful review basis")
        by_review[name] = review
    return by_provider, by_review, core_path.read_bytes(), baseline_path.read_bytes()


def _claims(root: Path, artifact: dict[str, Any], *, max_claims: int = 48
            ) -> tuple[list[str], dict[str, Any]]:
    source = artifact["path"]
    file = _resolve(root, source)
    raw = file.read_bytes()
    if file.suffix == ".md":
        all_claims = _markdown_claims(raw.decode("utf-8"))
    elif file.suffix in (".yaml", ".yml"):
        all_claims = _yaml_claims(_required_yaml(file))
    else:
        raise DiscoveryError("unsupported provider artifact format")
    if not all_claims:
        raise DiscoveryError(f"provider has no published claim surface: {source}")
    return all_claims[:max_claims], {
        "path": source,
        "sha256": _sha256(raw),
        "claim_count_in_source": len(all_claims),
        "claim_count_supplied": min(len(all_claims), max_claims),
        "public_surface_truncated": len(all_claims) > max_claims,
    }


def build(root: Path, *, sha: str = PIN,
          surface_mode: str = SOURCE_MODE_V1) -> dict[str, Any]:
    root = root.resolve()
    _commit(root, sha)
    if surface_mode not in {SOURCE_MODE_V1, SOURCE_MODE_V2, SOURCE_MODE_V3}:
        raise DiscoveryError("invalid owned-surface research protocol")
    selectors = None
    manifest_hash = None
    if surface_mode == SOURCE_MODE_V2:
        selectors, manifest_hash = load_selectors(
            SELECTOR_MANIFEST, pin=sha, target=TARGET, expected=PROVIDER_IDS
        )
    core, reviews, core_bytes, baseline_bytes = _registry(root)
    atomic = (
        prepare_draft(
            root, sha=sha, manifest_path=ATOMIC_MANIFEST, target=TARGET,
            expected=PROVIDER_IDS, artifacts=core, reviews=reviews,
        ) if surface_mode == SOURCE_MODE_V3 else None
    )
    atomic_sources = (
        {r["capability"]: r for r in atomic["provider_catalog"]}
        if atomic is not None else {}
    )
    if TARGET not in core or TARGET not in reviews:
        raise DiscoveryError("the target needs its own Core artifact and semantic review")
    target_artifact = core[TARGET]
    if target_artifact.get("authority") != "TACTICAL-DOMAIN-DESIGN":
        raise DiscoveryError("unexpected target Authority")
    target_file = _resolve(root, target_artifact["path"])
    target_doc = _required_yaml(target_file)
    if target_doc.get("kind") != "prep-relation-classification-catalog" or target_doc.get("status") != "canonical":
        raise DiscoveryError("wrong accepted target output document")
    outputs = target_doc.get("classification_outcomes")
    if not isinstance(outputs, dict) or set(outputs) != {
        "matched", "candidate_needed", "insufficient_evidence",
    }:
        raise DiscoveryError("changed target-owned outcome contract")
    obligations = []
    for name, fields in outputs.items():
        if not isinstance(fields, dict) or not isinstance(fields.get("meaning"), str):
            raise DiscoveryError("malformed target outcome meaning")
        required = fields.get("required_output")
        if not isinstance(required, list) or not required or any(
            not isinstance(x, str) or not x for x in required
        ) or len(required) != len(set(required)):
            raise DiscoveryError("target outcome has invalid required fields")
        obligations.append({
            "id": "classification-outcome-" + name.replace("_", "-"),
            "description": (
                "Define the reusable Subject Knowledge relation classification "
                "outcome '" + name + "' and its public semantics: "
                + fields["meaning"].strip()
                + " Its required output fields are "
                + ", ".join(required) + ". "
                "Do not assign target-requirement, learner-state or "
                "application execution meaning to a subject predicate."
            ),
            "source": {
                "path": target_artifact["path"],
                "json_pointer": "/classification_outcomes/" + name,
                "sha256": _sha256(target_file.read_bytes()),
                "target_review_revision": reviews[TARGET]["revision"],
                "independent_obligation_adjudication": "NOT_PROVEN",
            },
        })
    providers = []
    fingerprints = {
        "core_sha256": _sha256(core_bytes),
        "baseline_sha256": _sha256(baseline_bytes),
        "target_sha256": _sha256(target_file.read_bytes()),
    }
    for cid in PROVIDER_IDS:
        if cid == TARGET or cid not in core or cid not in reviews:
            raise DiscoveryError(f"provider missing Core and review: {cid}")
        art = core[cid]
        if atomic is not None:
            provider_data = atomic_sources[cid]
            surface = provider_data["semantic_surface"]
            evidence = {
                "sha256": provider_data["source_sha256"],
                "claim_count_in_source": "NOT_EXHAUSTIVELY_INVENTORIED",
                "claim_count_supplied": len(surface),
                "public_surface_truncated": False,
                **provider_data["source_scope"],
            }
        else:
            surface, evidence = (
                selected_surface(root, art, selectors[cid])
                if selectors is not None else _claims(root, art)
            )
        providers.append({
            "capability": cid,
            "authority": art["authority"],
            "evidence_status": ("CONTRACT_ONLY" if atomic else "ACCEPTED_EVIDENCE"),
            "source": art["path"],
            "source_sha256": evidence["sha256"],
            "review_revision": reviews[cid]["revision"],
            "semantic_surface": surface,
            "source_scope": {
                "claim_count_in_source": evidence["claim_count_in_source"],
                "claim_count_supplied": evidence["claim_count_supplied"],
                "public_surface_truncated": evidence["public_surface_truncated"],
                "selection_scope_partial": evidence.get("selection_scope_partial", False),
                "claim_role": evidence.get("claim_role", "UNCLASSIFIED_RAW_FRAGMENT"),
                "claim_ids": evidence.get("claim_ids", []),
                "independent_ownership_review_verified": False,
            },
        })
        fingerprints[cid] = evidence["sha256"]
    if manifest_hash:
        fingerprints["research_selector_manifest"] = manifest_hash
    if atomic is not None:
        fingerprints["atomic_draft_manifest"] = atomic["manifest_sha256"]
    inputs = {
        "version": 1,
        "kind": "harness-dependency-resolution-calibration-inputs",
        "evidence_contract": "source-grounded-v1",
        "source_snapshot": sha,
        "source_surface_protocol": surface_mode,
        "source_claim_role_evidence": [{
            "provider": need["provider"],
            "obligation": need["obligation"],
            "claim_index": need["claim_index"],
            "claim_id": providers_by_id[need["provider"]]["source_scope"].get(
                "claim_ids", []
            )[need["claim_index"]] if surface_mode == SOURCE_MODE_V3 else None,
            "independently_accepted": False,
        } for need in prediction["input_needs"]],
        "documented_delegations_not_dependencies": fresh[
            "draft_delegation_refs_for_post_model_review"
        ],
        "target_output_obligation_coverage": "THREE_EXPLICIT_TARGET_OUTCOMES_ONLY",
        "cases": [{
            "id": "PREP-CURRENT-RELATION-CLASSIFICATION",
            "target": {
                "capability": TARGET,
                "authority": target_artifact["authority"],
                "knowledge_kind": "domain-model",
                "output_obligations": obligations,
            },
            "provider_catalog": providers,
            "known_uncertainties": [
                "The target document is Core-registered and reviewed, but no "
                "independent decision per output obligation has been verified.",
                "Provider claims are bounded excerpts; their full semantic "
                "sufficiency and directness are not verified by source registration.",
                "Candidate providers were selected without inspecting target requires; "
                "the bounded catalog is not established as globally complete.",
                "In owned-section mode all excerpts are operator-selected, "
                "not independently accepted exports and not source-complete.",
            ],
        }],
    }
    run_id = hashlib.sha256(json.dumps(
        {"inputs": inputs, "fingerprints": fingerprints}, sort_keys=True,
        ensure_ascii=False).encode("utf-8")).hexdigest()[:20]
    request = build_blinded_request(inputs, run_id="PREP-ACTUAL-TARGET-" + run_id,
                                    adapter_binding={"provider": "github-copilot", "mode": "tool-free"})
    raw_request = json.dumps(request, ensure_ascii=False)
    for marker in ('"declared_requires"', '"baseline_requires"', '"target_requires"',
                   '"expected_requires"', '"provider_requires"'):
        if marker in raw_request:
            raise DiscoveryError(f"hidden graph input exposed: {marker}")
    return {
        "status": "BLINDED_REAL_TARGET_PROVISIONAL_INPUTS",
        "inputs": inputs, "request": request,
        "source_fingerprints": fingerprints,
        "draft_delegation_refs_for_post_model_review": (
            atomic["delegated_references"] if atomic else []
        ), **NO_APPROVAL,
    }


def _shortest_path(edges: dict[str, set[str]], start: str, finish: str) -> list[str] | None:
    queue = [(start, [start])]
    seen = set()
    while queue:
        node, route = queue.pop(0)
        if node == finish:
            return route
        if node in seen:
            continue
        seen.add(node)
        queue.extend((nxt, route + [nxt]) for nxt in sorted(edges.get(node, set()))
                     if nxt not in seen)
    return None


def reconcile(root: Path, *, sha: str, inputs: dict[str, Any],
              request: dict[str, Any], response: dict[str, Any],
              surface_mode: str = SOURCE_MODE_V1) -> dict[str, Any]:
    fresh = build(root, sha=sha, surface_mode=surface_mode)
    if inputs != fresh["inputs"] or request != fresh["request"]:
        raise DiscoveryError("stale real-target source or request")
    if (response.get("kind") != "harness-dependency-resolution-evaluator-response"
            or response.get("version") != 1
            or response.get("request_id") != request["request_id"]):
        raise DiscoveryError("model response not bound to the frozen request")
    rows = response.get("results")
    if not isinstance(rows, list) or len(rows) != 1:
        raise DiscoveryError("missing or extra model result")
    row = rows[0]
    case = request["cases"][0]
    if row.get("case_request_id") != case["case_request_id"]:
        raise DiscoveryError("incorrect model case binding")
    if row.get("status") not in ("RESOLVED", "UNRESOLVED"):
        raise DiscoveryError("malformed model status")
    if row["status"] == "RESOLVED" and row.get("unresolved_obligations"):
        raise DiscoveryError("RESOLVED model output contradicts unresolved obligations")
    prediction = {
        "id": inputs["cases"][0]["id"],
        "status": row["status"],
        "proposed_requires": row.get("proposed_requires"),
        "input_needs": row.get("input_needs"),
        "unresolved_obligations": row.get("unresolved_obligations"),
    }
    reviewed = assess_predictions(inputs, {
        "version": 1, "kind": "harness-dependency-resolution-predictions",
        "cases": [prediction],
    })
    if reviewed.get("status") == "INVALID":
        raise DiscoveryError("model source grounding is malformed")
    declared = _required_yaml(root / ".harness/engineering-graph.yaml")
    edges: dict[str, set[str]] = {}
    for auth in declared.get("authorities", []):
        for prod in auth.get("produces", []):
            cid = prod["capability"]
            if cid in edges:
                raise DiscoveryError("ambiguous project Capability producer")
            edges[cid] = {x["capability"] for x in prod.get("requires", [])}
    if TARGET not in edges:
        raise DiscoveryError("target is missing from project graph")
    proposed = set(prediction["proposed_requires"])
    if any(s not in edges for s in proposed):
        raise DiscoveryError("model provider not in accepted graph")
    original = edges[TARGET]
    cycle_blocks = []
    for supplier in sorted(proposed - original):
        path = _shortest_path(edges, supplier, TARGET)
        if path:
            cycle_blocks.append({
                "provider": supplier,
                "cycle": [TARGET] + path,
                "disposition": "BLOCKED_BY_CYCLE",
            })
    bounded_providers = inputs["cases"][0]["provider_catalog"]
    truncated = sorted(
        source["capability"] for source in bounded_providers
        if source.get("source_scope", {}).get("public_surface_truncated") is True
    )
    selected_partial = sorted(
        source["capability"] for source in bounded_providers
        if source.get("source_scope", {}).get("selection_scope_partial") is True
    )
    # The model's RESOLVED is a self-assessment. Never upgrade it when its
    # candidate edges are invalid, any public source was cropped, or target
    # obligation acceptance has not been individually established.
    providers_by_id = {p["capability"]: p
                       for p in inputs["cases"][0]["provider_catalog"]}
    low_information = []
    for need in prediction["input_needs"]:
        source = providers_by_id[need["provider"]]
        snippet = source["semantic_surface"][need["claim_index"]]
        # This is deliberately a narrow lexical *negative* check, not a
        # general claim entailment oracle. A heading that merely announces
        # an example or concept cannot itself entail a binding domain rule.
        body = snippet.rsplit(": ", 1)[-1].strip().casefold().rstrip(":")
        if body in {"examples", "conceptually", "illustration", "notes"}:
            low_information.append({
                "provider": need["provider"],
                "claim_index": need["claim_index"],
                "claim_text": snippet,
                "reason": "NON_SUBSTANTIVE_SOURCE_FRAGMENT",
                "must_not_treat_as_normative_evidence": True,
            })
    target_export_delegation_conflicts = delegated_target_claims(
        inputs["cases"][0], prediction
    )
    if cycle_blocks:
        effective_status = "INVALID_PROPOSED_TOPOLOGY"
    elif target_export_delegation_conflicts:
        effective_status = "BLOCKED_PROVIDER_CITES_TARGET_AS_EXPORT_OWNER"
    elif low_information:
        effective_status = "BLOCKED_NON_SUBSTANTIVE_SOURCE_CLAIMS"
    elif truncated:
        effective_status = "BLOCKED_INCOMPLETE_PROVIDER_SURFACES"
    elif selected_partial:
        effective_status = (
            "BLOCKED_UNACCEPTED_ATOMIC_EXPORT_CANDIDATES"
            if surface_mode == SOURCE_MODE_V3
            else "BLOCKED_OPERATOR_SELECTED_PROVIDER_SURFACES"
        )
    else:
        effective_status = "REVIEW_REQUIRED_TARGET_AND_DIRECTNESS_ACCEPTANCE"
    return {
        "kind": "harness-cdr-current-prep-real-target-contrast-v1",
        "status": effective_status,
        "effective_resolution": "NOT_RESOLVED",
        "model_resolution_is_not_accepted": True,
        "all_available_provider_contracts_covered": not (truncated or selected_partial),
        "truncated_provider_ids": truncated,
        "operator_selected_partial_provider_ids": selected_partial,
        "source_surface_protocol": surface_mode,
        "non_substantive_cited_claims": low_information,
        "explicit_target_export_delegation_conflicts": target_export_delegation_conflicts,
        "provider_source_ownership_independently_adjudicated": False,
        "provider_claim_entailment_verified": False,
        "accepted_project_dependency_topology_validated": False,
        "project_commit": sha,
        "target": TARGET,
        "request_id": request["request_id"],
        "model_status": prediction["status"],
        "model_requires": sorted(proposed),
        "existing_requires": sorted(original),
        "same_as_existing": sorted(original & proposed),
        "proposed_additions_not_approved": sorted(proposed - original),
        "declared_not_suggested_not_removal_evidence": sorted(original - proposed),
        "cycle_blocks": cycle_blocks,
        "grounding": reviewed,
        "provider_provenance": response.get("provenance"),
        **NO_APPROVAL,
    }


def _write(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False) + "\n",
                    encoding="utf-8")


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("phase", choices=["prepare", "evaluate", "reconcile"])
    p.add_argument("--project-root", type=Path, required=True)
    p.add_argument("--commit", default=PIN)
    p.add_argument("--surface-mode", default=SOURCE_MODE_V1,
                   choices=[SOURCE_MODE_V1, SOURCE_MODE_V2, SOURCE_MODE_V3])
    p.add_argument("--inputs", type=Path)
    p.add_argument("--request", type=Path)
    p.add_argument("--response", type=Path)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    try:
        if args.phase == "prepare":
            if not args.request:
                raise ValueError("prepare needs --request")
            result = build(args.project_root, sha=args.commit,
                           surface_mode=args.surface_mode)
            _write(args.inputs if args.inputs else args.output, result["inputs"])
            _write(args.request, result["request"])
            if args.inputs:
                _write(args.output, {"status": result["status"],
                                     "source_fingerprints": result["source_fingerprints"],
                                     **NO_APPROVAL})
            print(json.dumps({"status": result["status"], "providers": len(PROVIDER_IDS)}))
        elif args.phase == "evaluate":
            if not args.request:
                raise ValueError("evaluate needs --request")
            from evals.adapters.copilot_dependency_resolution_evaluator import evaluate_request
            result = evaluate_request(json.loads(args.request.read_text(encoding="utf-8")))
            _write(args.output, result)
            print(json.dumps({"status": "PROVIDER_RESULT_UNAPPROVED",
                              "rows": len(result["results"])}))
        else:
            if not args.inputs or not args.request or not args.response:
                raise ValueError("reconcile needs --inputs, --request, --response")
            result = reconcile(args.project_root, sha=args.commit,
                               inputs=json.loads(args.inputs.read_text(encoding="utf-8")),
                               request=json.loads(args.request.read_text(encoding="utf-8")),
                               response=json.loads(args.response.read_text(encoding="utf-8")),
                               surface_mode=args.surface_mode)
            _write(args.output, result)
            print(json.dumps({"status": result["status"],
                              "added": len(result["proposed_additions_not_approved"]),
                              "removed": 0}))
        return 0
    except (DiscoveryError, ValueError, TypeError, KeyError, OSError) as exc:
        print(json.dumps({"status": "INVALID", "error": str(exc)}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
