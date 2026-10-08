"""Noncanonical source-blind Reference Model Copilot CDR pilot.

Prepare sees only reference templates without requires; evaluation invokes an
existing tool-disabled provider adapter. The declared graph is read ONLY in
reconcile after a frozen model reply. No automatic project writeback.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from evals.cdr_reference_audit import (
    DEFAULT_AUTHORITIES, DEFAULT_MODEL, DEFAULT_PROOF, prepare as prepare_corpus,
    audit as audit_corpus,
)
from evals.dependency_resolution_process_driver import build_blinded_request
from evals.dependency_resolution_evidence import assess_predictions
from harness.reference_model.reference_materializer import load_yaml

PROFILE_PATH = Path("spec/dependency-resolution/reference-provider-pilot-v1.yaml")
ADAPTER = "evals.adapters.copilot_dependency_resolution_evaluator"
NO_ADOPTION = {
    "authority_acceptance": False,
    "independence_attested": False,
    "semantic_directness_proven": False,
    "automatic_writeback_allowed": False,
}


def _digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _path(root: Path, value: str) -> Path:
    return root / value


def _output_excerpt(root: Path, kind: str | None) -> tuple[str | None, str | None]:
    if not kind:
        return None, None
    path = root / "skills" / "artifacts" / kind / "SKILL.md"
    if not path.is_file():
        return None, None
    content = path.read_text(encoding="utf-8")
    marker = "## Output contract\n"
    if marker not in content:
        return None, None
    section = content.split(marker, 1)[1].split("\n## ", 1)[0]
    section = " ".join(section.strip().split())
    if not section:
        return None, None
    # Cut at a bounded word boundary so all providers have uniform context.
    excerpt = section[:720].rsplit(" ", 1)[0] if len(section) > 720 else section
    return excerpt, "sha256:" + _digest(path.read_bytes())


def _snapshot(root: Path, *, profile: Path, model: Path,
              authorities: Path, proof: Path) -> dict[str, str]:
    docs = {
        "reference_model": model,
        "authorities": authorities,
        "proof_contract": proof,
        "pilot_profile": profile,
    }
    return {name: "sha256:" + _digest((_path(root, str(path))).read_bytes())
            for name, path in docs.items()}


def build(root: Path, *, profile_path: str = str(PROFILE_PATH),
          model_path: str = DEFAULT_MODEL,
          authorities_path: str = DEFAULT_AUTHORITIES,
          proof_path: str = DEFAULT_PROOF) -> dict[str, Any]:
    profile = load_yaml(root / profile_path)
    if profile.get("kind") != "harness-cdr-reference-provider-pilot" or profile.get("version") != 1:
        raise ValueError("invalid research pilot profile")
    allowed = {"id", "target_template", "output_obligations"}
    cases = profile.get("cases")
    if not isinstance(cases, list) or not cases or len(cases) > 8:
        raise ValueError("expected 1..8 pilot cases")
    if len({c.get("id") for c in cases}) != len(cases):
        raise ValueError("duplicate pilot case ID")
    if len({c.get("target_template") for c in cases}) != len(cases):
        raise ValueError("duplicate pilot target template")
    model = load_yaml(root / model_path)
    owners = load_yaml(root / authorities_path)
    proof = load_yaml(root / proof_path)
    fingerprints = _snapshot(root, profile=Path(profile_path),
                             model=Path(model_path),
                             authorities=Path(authorities_path),
                             proof=Path(proof_path))
    blind = prepare_corpus(model, owners, proof, fingerprints)
    refs = {row["id"]: row for row in blind["templates"]}
    descriptions = {}
    skill_digests = {}
    for row in blind["templates"]:
        descr, digest = _output_excerpt(root, row.get("knowledge_kind"))
        descriptions[row["id"]] = descr
        if digest:
            skill_digests[row["id"]] = digest

    items = []
    for c in cases:
        if not isinstance(c, dict) or set(c) != allowed:
            raise ValueError("pilot cases may contain only label-free output fields")
        target_id = c["target_template"]
        if target_id not in refs:
            raise ValueError(f"unknown pilot target {target_id}")
        obligations = c["output_obligations"]
        if not isinstance(obligations, list) or not 1 <= len(obligations) <= 8:
            raise ValueError("target output obligations must contain 1..8 items")
        if any(not isinstance(x, dict) or set(x) != {"id", "description"}
               or not isinstance(x["id"], str) or len(x["id"]) < 3
               or not isinstance(x["description"], str)
               or len(x["description"].strip()) < 40 for x in obligations):
            raise ValueError("pilot obligation must have id and substantive description")
        if len({x["id"] for x in obligations}) != len(obligations):
            raise ValueError("duplicate pilot output obligation id")
        row = refs[target_id]
        providers = []
        # Full source-only catalog: no graph-based selection, no target edges.
        for p in blind["templates"]:
            if p["id"] == target_id:
                continue
            claim_labels = list(p.get("claim_surface", []))
            excerpt = descriptions[p["id"]]
            surface = ([f"Public production output contract: {excerpt}"] if excerpt else [])
            surface.extend(f"Research claim vocabulary (not project acceptance): {claim}" for claim in claim_labels)
            if not surface:
                surface.append("Research template with no explicit output surface; output semantics unresolved")
            providers.append({
                "capability": "reference." + p["id"].lower().replace("_", "-"),
                "authority": p["authority_type"],
                "evidence_status": "CONTRACT_ONLY",
                "semantic_surface": surface,
            })
        items.append({
            "id": c["id"],
            "target": {
                "capability": "reference." + target_id.lower().replace("_", "-"),
                "authority": row["authority_type"],
                "knowledge_kind": row.get("knowledge_kind"),
                "output_obligations": obligations,
            },
            "provider_catalog": providers,
            "known_uncertainties": [
                "Reference templates and artifact SKILL outputs are not project-accepted knowledge.",
                "Operator-authored target output obligations are candidates, not independently accepted.",
                "Source claim IDs do not establish full semantic sufficiency or directness.",
                "The whole 40-template catalog is present; applicability to a project is not established.",
            ],
        })
    inputs = {
        "version": 1,
        "kind": "harness-dependency-resolution-calibration-inputs",
        "evidence_contract": "source-grounded-v1",
        "source_snapshot": {"sources": fingerprints, "skill_output_contracts": skill_digests},
        "cases": items,
    }
    run_id = "REFERENCE-PILOT-" + _digest(json.dumps(
        inputs, sort_keys=True, ensure_ascii=False).encode("utf-8"))[:20]
    request = build_blinded_request(
        inputs, run_id=run_id,
        adapter_binding={"provider": "github-copilot", "mode": "fresh-tool-free"},
    )
    # Strict phase boundary: no target requires, expert decision, or Phase B path.
    for case in request["cases"]:
        if set(case) != {"case_request_id", "target", "provider_catalog", "known_uncertainties"}:
            raise ValueError("unexpected blind evaluator case fields")
        if any("requires" in item for item in [case["target"], *case["provider_catalog"]]):
            raise ValueError("target graph leaked to pilot discovery request")
    return {"inputs": inputs, "request": request, "status": "BLINDED_RESEARCH_PILOT_PREPARED",
            **NO_ADOPTION}


def reconcile(root: Path, *, inputs: dict[str, Any], request: dict[str, Any],
              response: dict[str, Any],
              profile_path: str = str(PROFILE_PATH),
              model_path: str = DEFAULT_MODEL,
              authorities_path: str = DEFAULT_AUTHORITIES,
              proof_path: str = DEFAULT_PROOF) -> dict[str, Any]:
    fresh = build(root, profile_path=profile_path, model_path=model_path,
                  authorities_path=authorities_path, proof_path=proof_path)
    if inputs != fresh["inputs"] or request != fresh["request"]:
        raise ValueError("stale or unbound reference pilot inputs")
    if (response.get("kind") != "harness-dependency-resolution-evaluator-response"
            or response.get("version") != 1
            or response.get("request_id") != request["request_id"]):
        raise ValueError("unbound evaluator response")
    by_req = {row["case_request_id"]: i for i, row in enumerate(request["cases"])}
    got = response.get("results")
    if not isinstance(got, list) or len(got) != len(by_req):
        raise ValueError("incomplete evaluator case set")
    remapped = {}
    for row in got:
        if not isinstance(row, dict):
            raise ValueError("invalid evaluator result row")
        bid = row.get("case_request_id")
        if bid not in by_req or bid in remapped:
            raise ValueError("unknown or duplicated evaluator case")
        ci = by_req[bid]
        origin = inputs["cases"][ci]
        proposed = row.get("proposed_requires")
        needs = row.get("input_needs")
        unresolved = row.get("unresolved_obligations")
        valid_provider_ids = {x["capability"] for x in origin["provider_catalog"]}
        output_ids = {o["id"] for o in origin["target"]["output_obligations"]}
        if (row.get("status") not in ("RESOLVED", "UNRESOLVED")
                or not isinstance(proposed, list)
                or not isinstance(needs, list)
                or not isinstance(unresolved, list)
                or len(proposed) != len(set(proposed))
                or not set(proposed) <= valid_provider_ids
                or not set(unresolved) <= output_ids):
            raise ValueError("invalid model-proposed edge or status")
        for need in needs:
            if (not isinstance(need, dict)
                    or need.get("obligation") not in output_ids
                    or need.get("provider") not in valid_provider_ids
                    or need.get("provider") not in proposed
                    or type(need.get("claim_index")) is not int
                    or need.get("basis") != "PLANNED_CONTRACT"):
                raise ValueError("invalid reference-only claim grounding")
            p = next(x for x in origin["provider_catalog"] if x["capability"] == need["provider"])
            if not 0 <= need["claim_index"] < len(p["semantic_surface"]):
                raise ValueError("out of range research contract claim")
        if set(proposed) != {x["provider"] for x in needs}:
            raise ValueError("candidate edge has no direct output need")
        remapped[ci] = {
            "id": origin["id"],
            "status": row["status"],
            "proposed_requires": proposed,
            "input_needs": needs,
            "unresolved_obligations": unresolved,
        }
    predictions = {"version": 1, "kind": "harness-dependency-resolution-predictions",
                   "cases": [remapped[i] for i in range(len(by_req))]}
    evidence = assess_predictions(inputs, predictions)
    model = load_yaml(root / model_path)
    owners = load_yaml(root / authorities_path)
    proof = load_yaml(root / proof_path)
    graph = audit_corpus(model, owners, proof, {})
    edges = {row["id"]: set() for row in model["templates"]}
    for row in graph["edge_review_packets"]:
        edges[row["target"]].add("reference." + row["provider"].lower().replace("_", "-"))
    # Combine model-suggested links with all declared links for a
    # conservative candidate DAG check. The original response stays intact.
    # Existing graph edges are prerequisite links: target -> supplier.
    template_names = {
        "reference." + row["id"].lower().replace("_", "-"): row["id"]
        for row in model["templates"]
    }
    proposed_by_id = {x["id"]: set(x["proposed_requires"])
                      for x in predictions["cases"]}
    pilot_targets = {x["id"]: x["target_template"]
                     for x in load_yaml(root / profile_path)["cases"]}
    candidate = {target: set(suppliers) for target, suppliers in edges.items()}
    for cid, suppliers in proposed_by_id.items():
        candidate[pilot_targets[cid]].update(suppliers)

    def cycle_path(provider: str, target: str) -> list[str] | None:
        # Supplier reaches target => adding target -> supplier closes a cycle.
        queue = [(provider, [provider])]
        seen = set()
        while queue:
            node, route = queue.pop(0)
            if node == target:
                return route
            if node in seen:
                continue
            seen.add(node)
            for nxt in sorted(candidate.get(node, [])):
                next_template = template_names[nxt]
                if next_template not in seen:
                    queue.append((next_template, route + [next_template]))
        return None

    contrast = []
    for c in inputs["cases"]:
        prediction = next(x for x in predictions["cases"] if x["id"] == c["id"])
        target = next(row["target_template"] for row in
                      load_yaml(root / profile_path)["cases"] if row["id"] == c["id"])
        proposed = set(prediction["proposed_requires"])
        declared = edges[target]
        invalid_new = []
        for provider in sorted(proposed - declared):
            supplier_template = template_names[provider]
            route = cycle_path(supplier_template, target)
            if route is not None:
                invalid_new.append({
                    "provider": provider,
                    "reason": "PROPOSED_EDGE_INTRODUCES_CAPABILITY_CYCLE",
                    "cycle": [target] + route,
                    "must_not_adopt": True,
                })
        contrast.append({
            "case_id": c["id"], "target_template": target,
            "structural_candidate_status": (
                "BLOCKED_BY_CYCLE" if invalid_new
                else "NO_CYCLE_FOUND_NOT_SEMANTICALLY_VERIFIED"
            ),
            "invalid_new_edge_candidates": invalid_new,
            "proposed_provider_count": len(proposed),
            "declared_provider_count": len(declared),
            "both_provisional": sorted(proposed & declared),
            "new_candidate_not_accepted": sorted(proposed - declared),
            "declared_not_suggested_review_only": sorted(declared - proposed),
            "unresolved_obligations": prediction["unresolved_obligations"],
            "directness_decision": "UNDETERMINED_PENDING_AUTHORITY",
            "declared_edge_omission_is_not_removal_evidence": True,
        })
    return {
        "kind": "harness-cdr-reference-provider-reconciliation-v1",
        "status": "PROVIDER_HYPOTHESES_REQUIRE_INDEPENDENT_ADJUDICATION",
        "request_id": request["request_id"],
        "source_snapshot": inputs["source_snapshot"],
        "provider_provenance": response.get("provenance"),
        "evidence_assessment": evidence,
        "contrasts": contrast,
        "predictions": predictions,
        **NO_ADOPTION,
    }


def _write(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True)
                    + "\n", encoding="utf-8")


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("phase", choices=("prepare", "evaluate", "reconcile"))
    p.add_argument("--root", type=Path, default=Path("."))
    p.add_argument("--input", type=Path)
    p.add_argument("--request", type=Path)
    p.add_argument("--response", type=Path)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    try:
        if args.phase == "prepare":
            if not args.request:
                raise ValueError("prepare requires --request")
            result = build(args.root)
            _write(args.output, result["inputs"])
            _write(args.request, result["request"])
            print(json.dumps({"status": result["status"],
                              "cases": len(result["inputs"]["cases"]),
                              "provider_edges_hidden": True}))
        elif args.phase == "evaluate":
            if not args.request:
                raise ValueError("evaluate requires --request")
            from evals.adapters.copilot_dependency_resolution_evaluator import evaluate_request
            response = evaluate_request(json.loads(args.request.read_text(encoding="utf-8")))
            _write(args.output, response)
            print(json.dumps({"status": "EVALUATED_PROVIDER_RESULT_UNAPPROVED",
                              "results": len(response["results"])}))
        else:
            if not args.input or not args.request or not args.response:
                raise ValueError("reconcile requires --input, --request and --response")
            result = reconcile(
                args.root,
                inputs=json.loads(args.input.read_text(encoding="utf-8")),
                request=json.loads(args.request.read_text(encoding="utf-8")),
                response=json.loads(args.response.read_text(encoding="utf-8")),
            )
            _write(args.output, result)
            print(json.dumps({"status": result["status"],
                              "cases": len(result["contrasts"]),
                              "graph_edit_authorized": False}))
        return 0
    except (OSError, ValueError, KeyError, TypeError, RuntimeError) as exc:
        print(json.dumps({"status": "INVALID", "error": str(exc)}, ensure_ascii=False))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
