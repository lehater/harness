"""Read-only Phase B topology comparison for oracle-free project discovery.

May run only AFTER the blinded Phase A prediction has completed. It inspects
the pinned Engineering Graph baseline and reports review-required deltas.
Never publishes or changes canonical `requires`, Core, or project state.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

import yaml

from evals.project_discovery_snapshot import DiscoveryError, _commit, _required_yaml
from evals.dependency_resolution_evidence import assess_predictions
from evals.project_discovery_coverage import assess_coverage
from evals.project_discovery_directness import audit_additions
from evals.project_discovery_directness_review import review_packets
from evals.project_target_contract_readiness import audit_target_contracts

def compare(
    project_root: Path, *, sha: str,
    inputs: dict[str, Any], evaluation: dict[str, Any]
) -> dict[str, Any]:
    _commit(project_root.resolve(), sha)
    if inputs.get("source_snapshot") != sha:
        raise DiscoveryError("discovery input snapshot identity differs from project commit")
    if evaluation.get("source_snapshot") != sha:
        raise DiscoveryError("evaluator snapshot identity differs from project commit")
    if evaluation.get("status") != "DISCOVERY_REQUIRES_REVIEW":
        raise DiscoveryError("blinded evaluator did not reach reviewable discovery status")
    if evaluation.get("calibration_claim") != "NOT_APPLICABLE_NO_ORACLE":
        raise DiscoveryError("this comparison accepts only oracle-free project discovery")
    if evaluation.get("automatic_writeback_allowed") is not False:
        raise DiscoveryError("automatic writeback cannot be enabled")
    predictions = evaluation.get("bound_predictions")
    if not isinstance(predictions, dict) or predictions.get("version") != 1:
        raise DiscoveryError("missing bound discovery predictions")
    incoming = inputs.get("cases")
    if not isinstance(incoming, list) or not incoming:
        raise DiscoveryError("missing bound discovery cases")
    records = predictions.get("cases")
    if not isinstance(records, list):
        raise DiscoveryError("missing predicted case records")
    case_ids = {c["id"] for c in incoming}
    if (len(records) != len(incoming) or
        {r.get("id") for r in records} != case_ids or
        len({r.get("id") for r in records}) != len(records)):
        raise DiscoveryError("result case binding differs from original blind input")
    # Recalculate reference validity from model rows rather than trusting the
    # evaluation artifact's assertion that its evidence was assessed.
    rechecked = assess_predictions(inputs, predictions)
    if rechecked.get("status") == "INVALID":
        raise DiscoveryError("bound predictions fail source-reference verification")
    if rechecked != evaluation.get("evidence_assessment"):
        raise DiscoveryError("stored proof assessment differs from recomputed model evidence")
    coverage_check = assess_coverage(inputs, predictions)
    if coverage_check.get("status") == "INVALID":
        raise DiscoveryError("incomplete or inconsistent product coverage classification")
    if coverage_check != evaluation.get("coverage_assessment"):
        raise DiscoveryError("stored product coverage differs from recomputed prediction")
    coverage = inputs.get("target_obligation_coverage")
    if not isinstance(coverage, dict) or (
        coverage.get("status") != "PARTIAL_BY_CONSTRUCTION"
        or coverage.get("complete_upstream_obligation_coverage_established") is not False
    ):
        raise DiscoveryError("project pilot must explicitly declare incomplete target-obligation coverage")
    # A bounded source-section pilot cannot prove that an absent suggested
    # edge is semantically unnecessary. In particular, Product Capabilities
    # can constrain Tactical Domain outputs without being reprinted in MC-01
    # or MC-02 headings. Never emit removal candidates from incomplete scope.
    graph = _required_yaml(project_root / ".harness/engineering-graph.yaml")
    producers: dict[str, dict[str, Any]] = {}
    for auth in graph.get("authorities", []):
        for prod in auth.get("produces", []):
            cid = prod.get("capability")
            if cid in producers:
                raise DiscoveryError(f"duplicate Graph producer: {cid}")
            producers[cid] = prod

    by_input = {c["id"]: c for c in incoming}
    # Phase B only: target contract acceptance is checked against the pinned
    # Core and target's own semantic baseline; never leaked to Phase A.
    readiness = audit_target_contracts(
        project_root, sha=sha,
        targets=[c["target"]["capability"] for c in incoming],
    )
    readiness_by_capability = {
        f["target_capability"]: f for f in readiness["cases"]
    }
    findings = []
    for p in records:
        cid = p["id"]
        case = by_input[cid]
        target = case["target"]["capability"]
        if target not in producers:
            raise DiscoveryError(f"target production missing in graph: {target}")
        current = [x["capability"] for x in producers[target].get("requires", [])]
        proposed = p.get("proposed_requires")
        if not isinstance(proposed, list) or any(not isinstance(x, str) for x in proposed):
            raise DiscoveryError(f"invalid predicted direct provider set: {cid}")
        if len(proposed) != len(set(proposed)):
            raise DiscoveryError(f"duplicate proposed direct provider: {cid}")
        if any(x not in producers for x in proposed):
            raise DiscoveryError(f"unrecognized proposed provider: {cid}")
        if len(current) != len(set(current)):
            raise DiscoveryError(f"duplicate baseline requires: {cid}")
        current_set, proposed_set = set(current), set(proposed)
        directness = audit_additions(
            case, p, existing_requires=current_set, productions=producers,
        )
        review = review_packets(
            case, p, accepted_requires=current_set, productions=producers,
            directness_audit=directness, source_snapshot=sha,
            target_formulation_authority=inputs.get(
                "target_formulation_authority", "UNSPECIFIED"
            ),
        )
        assessment = evaluation.get("evidence_assessment", {})
        assessed = next((x for x in assessment.get("cases", []) if x.get("id") == cid), None)
        if not assessed:
            raise DiscoveryError(f"missing corresponding proof assessment for: {cid}")
        if assessed.get("status") not in {
            "REFERENCED_NOT_SEMANTICALLY_VERIFIED", "REVIEW_REQUIRED"
        }:
            raise DiscoveryError(f"invalid or unassessed source grounding: {cid}")
        findings.append({
            "id": cid,
            "target_capability": target,
            "prediction_status": p.get("status"),
            "proof_status": assessed["status"],
            "current_requires": sorted(current_set),
            "proposed_requires": sorted(proposed_set),
            "KEEP": sorted(current_set & proposed_set),
            "ADD": sorted(proposed_set - current_set),
            # ADD describes the model proposal only. Directness is UNPROVEN
            # even when a cited source claim and obligation are well-formed.
            "ADD_DIRECTNESS_AUDIT": directness,
            "ADD_DIRECTNESS_REVIEW_PACKETS": review,
            "TARGET_OUTPUT_CONTRACT_READINESS": readiness_by_capability[target],
            "ADD_PROMOTION_ALLOWED": False,
            # An omitted edge is unassessed, NOT a removal proposal, when
            # target obligations were sourced from selected sections only.
            "REMOVE_CANDIDATE": [],
            "UNASSESSED_EXISTING_EDGES": sorted(current_set - proposed_set),
            "removal_assessment": "BLOCKED_INCOMPLETE_TARGET_OBLIGATIONS",
            "target_obligation_coverage": coverage["status"],
            "target_formulation": inputs.get("target_formulation", "SOURCE_BOUND"),
            "target_formulation_authority": inputs.get(
                "target_formulation_authority", "UNSPECIFIED"
            ),
            "product_candidate_assessment": "REVIEW_REQUIRED",
            "product_candidates_accounted_for": next(
                (x.get("accepted_candidates_inventoried")
                 for x in coverage_check.get("cases", []) if x.get("id") == cid), 0
            ),
            # Every transition requires independent semantic review.
            "decision": "REVIEW_REQUIRED",
            "semantic_entailment_verified": False,
        })
    return {
        "status": "READ_ONLY_RECONCILIATION",
        "source_snapshot": sha,
        "target_formulation": inputs.get("target_formulation", "SOURCE_BOUND"),
        "target_formulation_authority": inputs.get(
            "target_formulation_authority", "UNSPECIFIED"
        ),
        "cases": findings,
        "target_output_contract_readiness": readiness,
        "automatic_writeback_allowed": False,
        "semantic_entailment_verified": False,
    }


def _extract_result(report: dict[str, Any]) -> dict[str, Any]:
    scenarios = report.get("scenarios", [])
    if not isinstance(scenarios, list) or len(scenarios) != 1:
        raise DiscoveryError("expected one project discovery scenario")
    steps = scenarios[0].get("steps", [])
    if not isinstance(steps, list):
        raise DiscoveryError("malformed scenario steps")
    for step in steps:
        if step.get("id") == "run":
            value = step.get("observations", {}).get("evaluation")
            if isinstance(value, dict):
                return value
    raise DiscoveryError("no bound run evaluation in scenario evidence")


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--project-root", type=Path, required=True)
    p.add_argument("--commit", required=True)
    p.add_argument("--inputs", type=Path, required=True)
    p.add_argument("--evidence", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    try:
        inputs = _required_yaml(args.inputs)
        report = json.loads(args.evidence.read_text(encoding="utf-8"))
        output = compare(args.project_root, sha=args.commit, inputs=inputs,
                         evaluation=_extract_result(report))
        args.output.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n",
                               encoding="utf-8")
        print("CDR_PROJECT_RECONCILIATION_BEGIN")
        print(json.dumps(output, ensure_ascii=False, indent=2))
        print("CDR_PROJECT_RECONCILIATION_END")
        return 0
    except (DiscoveryError, KeyError, ValueError, TypeError, OSError) as exc:
        print(json.dumps({"status": "INVALID", "error": str(exc)}, ensure_ascii=False))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
