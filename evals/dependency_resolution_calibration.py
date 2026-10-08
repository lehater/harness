#!/usr/bin/env python3
"""Experimental, deterministic fixture validation and label-separated scoring.

This tool does not run an LLM, endorse oracle truth, or mutate Engineering Graph.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any
import yaml

from evals.dependency_resolution_evidence import assess_predictions

VALID_STATUSES = {"RESOLVED", "UNRESOLVED", "INVALID"}
VALID_REVIEW_STATUSES = {"AUTHOR_DRAFT", "PROJECT_HYPOTHESIS", "INDEPENDENTLY_REVIEWED"}


def load(path: str) -> dict[str, Any]:
    doc = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(doc, dict):
        raise ValueError(f"{path}: expected YAML mapping")
    return doc


def unique_list(items: list[Any], context: str) -> None:
    if len(set(items)) != len(items):
        raise ValueError(f"{context}: duplicate identifiers")


def sorted_unique_strings(value: Any, context: str) -> list[str]:
    if not isinstance(value, list) or not all(isinstance(x, str) and x for x in value):
        raise ValueError(f"{context}: expected string array")
    unique_list(value, context)
    return sorted(value)


def needs(value: Any, context: str) -> set[tuple[str, str]]:
    if not isinstance(value, list):
        raise ValueError(f"{context}: expected list")
    output: set[tuple[str, str]] = set()
    for item in value:
        if not isinstance(item, dict) or not isinstance(item.get("obligation"), str) or not isinstance(item.get("provider"), str):
            raise ValueError(f"{context}: each direct need requires obligation + provider")
        pair = (item["obligation"], item["provider"])
        if pair in output:
            raise ValueError(f"{context}: duplicate need mapping {pair}")
        output.add(pair)
    return output


def validate(inputs: dict[str, Any], oracle: dict[str, Any]) -> dict[str, Any]:
    if inputs.get("kind") != "harness-dependency-resolution-calibration-inputs" or inputs.get("version") != 1:
        raise ValueError("Unexpected input corpus kind/version")
    if oracle.get("kind") != "harness-dependency-resolution-calibration-oracle" or oracle.get("version") != 1:
        raise ValueError("Unexpected oracle kind/version")
    if oracle.get("privacy") != "NEVER_SEND_TO_EVALUATED_AGENT":
        raise ValueError("Oracle privacy policy must forbid evaluator disclosure")
    input_cases = inputs.get("cases")
    oracle_cases = oracle.get("cases")
    if not isinstance(input_cases, list) or not isinstance(oracle_cases, list) or not input_cases:
        raise ValueError("Missing calibration cases")
    input_ids = [x.get("id") for x in input_cases]
    oracle_ids = [x.get("id") for x in oracle_cases]
    unique_list(input_ids, "input case ids")
    unique_list(oracle_ids, "oracle case ids")
    if set(input_ids) != set(oracle_ids):
        raise ValueError("Input and oracle case id sets differ")
    by_id = {x["id"]: x for x in oracle_cases}
    counts = {}
    for item in input_cases:
        cid = item["id"]
        if not isinstance(cid, str) or not cid:
            raise ValueError("Each case needs a nonempty id")
        # Target edge labels must be hidden from Phase A fixture.
        if any(key in item for key in ("declared_requires", "baseline_requires", "expected_requires", "expected_direct_needs", "expert_oracle", "expected_status")):
            raise ValueError(f"{cid}: target edge or expert labels leaked to discovery fixture")
        t = item.get("target")
        if not isinstance(t, dict) or not isinstance(t.get("capability"), str):
            raise ValueError(f"{cid}: missing target Capability")
        if any(key in t for key in ("requires", "baseline_requires", "declared_requires")):
            raise ValueError(f"{cid}: target requires leaked inside target object")
        obligations = t.get("output_obligations")
        if not isinstance(obligations, list) or not obligations:
            raise ValueError(f"{cid}: target has no obligations")
        obligation_ids = [v.get("id") for v in obligations]
        unique_list(obligation_ids, f"{cid}: obligations")
        providers = item.get("provider_catalog")
        if not isinstance(providers, list) or not providers:
            raise ValueError(f"{cid}: missing provider catalog")
        provider_ids = [p.get("capability") for p in providers]
        unique_list(provider_ids, f"{cid}: provider catalog")
        if t["capability"] in provider_ids:
            raise ValueError(f"{cid}: target cannot be its own upstream provider")
        o = by_id[cid]
        if o.get("review_status") not in VALID_REVIEW_STATUSES:
            raise ValueError(f"{cid}: unknown review status")
        if o.get("expected_status") not in VALID_STATUSES:
            raise ValueError(f"{cid}: unknown expected status")
        baseline = set(sorted_unique_strings(o.get("baseline_requires"), f"{cid}: baseline"))
        expected = set(sorted_unique_strings(o.get("expected_requires"), f"{cid}: expected"))
        if not baseline <= set(provider_ids) or not expected <= set(provider_ids):
            raise ValueError(f"{cid}: unknown baseline or expected provider")
        expected_needs = needs(o.get("expected_direct_needs"), f"{cid}: needs")
        if any(ob not in obligation_ids or prov not in expected for ob,prov in expected_needs):
            raise ValueError(f"{cid}: expected need refers to unknown obligation/provider")
        if {prov for _, prov in expected_needs} != expected:
            raise ValueError(f"{cid}: proposed edge lacks direct need justification")
        unresolved = set(sorted_unique_strings(o.get("expected_unresolved_obligations"), f"{cid}: unresolved"))
        if not unresolved <= set(obligation_ids):
            raise ValueError(f"{cid}: unknown unresolved obligation")
        if o["expected_status"] == "RESOLVED" and unresolved:
            raise ValueError(f"{cid}: resolved oracle has unresolved obligations")
        if o["expected_status"] == "UNRESOLVED" and not unresolved:
            raise ValueError(f"{cid}: unresolved oracle lacks unmet obligations")
        rec = o.get("expected_reconciliation", {})
        if not isinstance(rec, dict):
            raise ValueError(f"{cid}: invalid expected reconciliation")
        for name, correct in (("KEEP", baseline & expected), ("ADD", expected - baseline), ("REMOVE_CANDIDATE", baseline - expected)):
            observed = set(sorted_unique_strings(rec.get(name), f"{cid}: {name}"))
            if observed != correct:
                raise ValueError(f"{cid}: reconciliation {name} disagrees with baseline vs expected")
        counts[o["review_status"]] = counts.get(o["review_status"], 0) + 1
    return {"status": "VALID", "cases": len(input_cases), "oracle_review_statuses": counts,
            "calibration_claim": "NOT_ESTABLISHED"}


def score(inputs: dict[str, Any], oracle: dict[str, Any], predictions: dict[str, Any]) -> dict[str, Any]:
    manifest = validate(inputs, oracle)
    if predictions.get("version") != 1 or predictions.get("kind") != "harness-dependency-resolution-predictions":
        raise ValueError("Unexpected prediction kind/version")
    rows = predictions.get("cases", [])
    if not isinstance(rows, list):
        raise ValueError("Prediction cases must be a list")
    pred_ids = [r.get("id") for r in rows]
    unique_list(pred_ids, "prediction ids")
    unknown = set(pred_ids) - {x["id"] for x in inputs["cases"]}
    if unknown:
        raise ValueError(f"Predictions have unknown cases: {sorted(unknown)}")
    pmap = {r["id"]: r for r in rows}
    results = []
    tp = fp = fn = 0
    all_matched = True
    for o in oracle["cases"]:
        cid = o["id"]
        if cid not in pmap:
            all_matched = False
            results.append({"id": cid, "status": "MISSING_PREDICTION", "review_status": o["review_status"]})
            continue
        pred = pmap[cid]
        provided = set(sorted_unique_strings(pred.get("proposed_requires"), f"{cid}: predicted requires"))
        approved = set(o["expected_requires"])
        observed_need_pairs = needs(pred.get("input_needs"), f"{cid}: predicted needs")
        expected_need_pairs = needs(o["expected_direct_needs"], f"{cid}: expected needs")
        unresolved = set(sorted_unique_strings(pred.get("unresolved_obligations"), f"{cid}: predicted unresolved"))
        correct_status = pred.get("status") == o["expected_status"]
        extra = sorted(provided - approved)
        missed = sorted(approved - provided)
        matched = not extra and not missed and correct_status and observed_need_pairs == expected_need_pairs and unresolved == set(o["expected_unresolved_obligations"])
        tp += len(provided & approved); fp += len(extra); fn += len(missed)
        all_matched &= matched
        results.append({
            "id": cid, "status": "MATCHES_DRAFT_ORACLE" if matched else "DIFFERS_FROM_DRAFT_ORACLE",
            "review_status": o["review_status"], "false_positive_edges": extra,
            "missing_edges": missed,
            "missing_direct_needs": [list(z) for z in sorted(expected_need_pairs - observed_need_pairs)],
            "extra_direct_needs": [list(z) for z in sorted(observed_need_pairs - expected_need_pairs)],
            "status_correct": correct_status,
            "unresolved_correct": unresolved == set(o["expected_unresolved_obligations"]),
        })
    evidence_assessment = assess_predictions(inputs, predictions)
    if evidence_assessment["status"] == "INVALID":
        all_matched = False
    return {
        "status": "MATCHES_DRAFT_ORACLE" if all_matched else "DIFFERS_OR_INCOMPLETE",
        "evidence_assessment": evidence_assessment,
        "automatic_writeback_allowed": False,
        "oracle_is_expert_validated": all(x["review_status"] == "INDEPENDENTLY_REVIEWED" for x in oracle["cases"]),
        "calibration_claim": "NOT_ESTABLISHED",
        "cases": results,
        "edge_comparison": {"matched": tp, "false_positive": fp, "false_negative": fn,
                            "precision": (tp / (tp + fp)) if tp + fp else None,
                            "recall": (tp / (tp + fn)) if tp + fn else None},
        "fixture_validation": manifest,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["validate", "score"])
    parser.add_argument("inputs")
    parser.add_argument("oracle")
    parser.add_argument("predictions", nargs="?")
    args = parser.parse_args()
    if args.command == "score" and not args.predictions:
        parser.error("score requires a predictions YAML path")
    try:
        result = (validate(load(args.inputs), load(args.oracle)) if args.command == "validate"
                  else score(load(args.inputs), load(args.oracle), load(args.predictions)))
    except (ValueError, OSError, yaml.YAMLError) as exc:
        print(json.dumps({"status": "INVALID", "error": str(exc)}, ensure_ascii=False, indent=2))
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["status"] in {"VALID", "MATCHES_DRAFT_ORACLE"} else 1


if __name__ == "__main__":
    raise SystemExit(main())