"""Existing authored synthetic CDR cases as post-model-only directional holdout.

No scoring labels, accepted oracle or baseline target requires reach the provider.
The v1 authored expectations are not expert-validated semantic truth.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from evals.dependency_resolution_process_driver import build_blinded_request
from evals.dependency_resolution_calibration import load, score

INPUT_PATH = "spec/dependency-resolution/calibration-inputs-v1.yaml"
ORACLE_PATH = "spec/dependency-resolution/calibration-oracle-v1.yaml"
NO_WRITEBACK = {
    "authority_acceptance": False,
    "oracle_is_expert_validated": False,
    "semantic_directness_proven": False,
    "automatic_writeback_allowed": False,
}


def build(root: Path) -> dict[str, Any]:
    # Phase A MUST NOT load the oracle.
    source = load(str(root / INPUT_PATH))
    cases = [x for x in source["cases"] if x.get("archetype") == "synthetic"]
    if len(cases) != 4 or {x["id"] for x in cases} != {"CDR-01", "CDR-02", "CDR-03", "CDR-04"}:
        raise ValueError("unexpected synthetic holdout cases")
    inputs = {key: val for key, val in source.items() if key != "cases"}
    inputs["cases"] = cases
    fingerprint = hashlib.sha256(
        (root / INPUT_PATH).read_bytes()).hexdigest()
    request = build_blinded_request(
        inputs,
        run_id="CDR-AUTHORED-SYNTHETIC-HOLDOUT-" + fingerprint[:16],
        adapter_binding={"provider": "github-copilot", "mode": "tool-disabled"},
    )
    hidden = json.dumps(request, sort_keys=True)
    for forbidden in ("expected_requires", "baseline_requires", "expected_direct_needs",
                      "expected_status", "expert_oracle", "review_status"):
        if forbidden in hidden:
            raise ValueError("holdout scoring label leaked into provider request")
    return {
        "inputs": inputs, "request": request,
        "source_fingerprint": "sha256:" + fingerprint,
        "status": "AUTHOR_DRAFT_HOLDOUT_PREPARED_NOT_REVIEWED",
        **NO_WRITEBACK,
    }


def reconcile(root: Path, *, inputs: dict[str, Any],
              request: dict[str, Any], response: dict[str, Any]) -> dict[str, Any]:
    fresh = build(root)
    if inputs != fresh["inputs"] or request != fresh["request"]:
        raise ValueError("holdout source or request drift")
    if (response.get("version") != 1
            or response.get("kind") != "harness-dependency-resolution-evaluator-response"
            or response.get("request_id") != request["request_id"]):
        raise ValueError("holdout response not bound to generated request")
    original = request["cases"]
    responses = response.get("results")
    if not isinstance(responses, list) or len(responses) != len(original):
        raise ValueError("incomplete holdout response")
    rmap = {}
    for row in responses:
        if not isinstance(row, dict):
            raise ValueError("malformed holdout result")
        rid = row.get("case_request_id")
        if rid in rmap or rid not in {x["case_request_id"] for x in original}:
            raise ValueError("unknown or duplicated case binding")
        if row.get("status") not in ("RESOLVED", "UNRESOLVED"):
            raise ValueError("invalid holdout model status")
        for field in ("proposed_requires", "input_needs", "unresolved_obligations"):
            if not isinstance(row.get(field), list):
                raise ValueError("missing holdout model output field")
        rmap[rid] = row
    predictions = {
        "version": 1,
        "kind": "harness-dependency-resolution-predictions",
        "cases": [
            {"id": src["id"],
             "status": rmap[case["case_request_id"]]["status"],
             "proposed_requires": rmap[case["case_request_id"]]["proposed_requires"],
             "input_needs": rmap[case["case_request_id"]]["input_needs"],
             "unresolved_obligations": rmap[case["case_request_id"]]["unresolved_obligations"]}
            for src, case in zip(inputs["cases"], original)
        ],
    }
    # Only Phase B loads the authored oracle, after the provider result is frozen.
    authored_oracle = load(str(root / ORACLE_PATH))
    subset = {**authored_oracle,
              "cases": [x for x in authored_oracle["cases"]
                        if x["id"] in {c["id"] for c in inputs["cases"]}]}
    result = score(inputs, subset, predictions)
    return {
        "kind": "harness-cdr-direction-author-draft-holdout-v1",
        "status": "UNVERIFIED_AUTHOR_DRAFT_COMPARISON",
        "request_id": request["request_id"],
        "source_fingerprint": fresh["source_fingerprint"],
        "comparison": result,
        "predictions": predictions,
        "provider_provenance": response.get("provenance"),
        **NO_WRITEBACK,
    }


def _write(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False)
                    + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("phase", choices=["prepare", "evaluate", "reconcile"])
    ap.add_argument("--root", type=Path, default=Path("."))
    ap.add_argument("--input", type=Path)
    ap.add_argument("--request", type=Path)
    ap.add_argument("--response", type=Path)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    try:
        if args.phase == "prepare":
            if args.request is None:
                raise ValueError("prepare requires --request")
            payload = build(args.root)
            _write(args.output, payload["inputs"])
            _write(args.request, payload["request"])
            print(json.dumps({"status": payload["status"], "cases": 4}))
        elif args.phase == "evaluate":
            if args.request is None:
                raise ValueError("evaluate requires --request")
            from evals.adapters.copilot_dependency_resolution_evaluator import evaluate_request
            result = evaluate_request(json.loads(args.request.read_text(encoding="utf-8")))
            _write(args.output, result)
            print(json.dumps({"status": "PROVIDER_RESPONSE_FROZEN_UNSCORED",
                              "rows": len(result["results"])}))
        else:
            if not (args.input and args.request and args.response):
                raise ValueError("reconcile requires input, request, response")
            result = reconcile(
                args.root,
                inputs=json.loads(args.input.read_text(encoding="utf-8")),
                request=json.loads(args.request.read_text(encoding="utf-8")),
                response=json.loads(args.response.read_text(encoding="utf-8")),
            )
            _write(args.output, result)
            print(json.dumps({"status": result["status"],
                              "matched": result["comparison"]["edge_comparison"]["matched"],
                              "accepted": False}))
        return 0
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(json.dumps({"status": "INVALID", "error": str(exc)}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
