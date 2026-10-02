#!/usr/bin/env python3
"""Deterministic binding and validation for live semantic evaluator calibration."""
from __future__ import annotations

import copy
import hashlib
import json
from typing import Any

from harness.project_model.core import CoreError
from harness.assurance.semantic_judgement_calibration import evaluate_judgement_calibration

RUN_STATES = {"COMPLETED", "FAILED", "INTERRUPTED", "UNAVAILABLE"}
VERDICTS = {"ACCEPTED", "REJECTED"}


def _canonical_bytes(value: Any, where: str) -> bytes:
    try:
        rendered = json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        )
    except (TypeError, ValueError) as exc:
        raise CoreError(f"{where} must be JSON-serializable") from exc
    return rendered.encode("utf-8")


def _fingerprint(prefix: str, value: Any, where: str) -> str:
    digest = hashlib.sha256(_canonical_bytes(value, where)).hexdigest()
    return f"{prefix}-{digest}"


def _require_string(value: Any, where: str) -> str:
    if not isinstance(value, str) or not value:
        raise CoreError(f"{where} must be a non-empty string")
    return value


def _validate_corpus(corpus: dict[str, Any]) -> list[dict[str, Any]]:
    # Reuse the existing scorer as the canonical corpus validator. Empty
    # predictions intentionally produce INCOMPLETE after corpus validation.
    evaluate_judgement_calibration(corpus=corpus, predictions=[])
    cases = corpus.get("cases", []) or []
    for item in cases:
        for field in ("source", "target", "relation"):
            if field not in item:
                raise CoreError(f"calibration case {item['id']} requires {field}")
        _require_string(
            item.get("relation"),
            f"calibration case {item['id']} relation",
        )
    return cases


def _validate_protocol(protocol: dict[str, Any]) -> None:
    if protocol.get("version") != 1:
        raise CoreError("live semantic evaluator protocol version must be 1")
    if protocol.get("kind") != "harness-live-semantic-evaluator-protocol":
        raise CoreError("unexpected live semantic evaluator protocol kind")
    _require_string(protocol.get("id"), "live semantic evaluator protocol id")
    _require_string(
        protocol.get("instruction"),
        "live semantic evaluator protocol instruction",
    )


def _validate_evaluator(evaluator: dict[str, Any]) -> None:
    if evaluator.get("version") != 1:
        raise CoreError("semantic evaluator descriptor version must be 1")
    if evaluator.get("kind") != "harness-semantic-evaluator-descriptor":
        raise CoreError("unexpected semantic evaluator descriptor kind")
    for field in ("id", "provider", "model", "model_version"):
        _require_string(
            evaluator.get(field),
            f"semantic evaluator descriptor {field}",
        )
    configuration = evaluator.get("configuration")
    if not isinstance(configuration, dict):
        raise CoreError(
            "semantic evaluator descriptor configuration must be a mapping"
        )
    adapter = evaluator.get("adapter")
    if not isinstance(adapter, dict):
        raise CoreError("semantic evaluator descriptor adapter must be a mapping")
    _require_string(adapter.get("id"), "semantic evaluator descriptor adapter id")
    _require_string(
        adapter.get("version"),
        "semantic evaluator descriptor adapter version",
    )
    _canonical_bytes(evaluator, "semantic evaluator descriptor")


def _binding(
    corpus: dict[str, Any],
    protocol: dict[str, Any],
    evaluator: dict[str, Any],
) -> dict[str, Any]:
    cases = _validate_corpus(corpus)
    _validate_protocol(protocol)
    _validate_evaluator(evaluator)
    return {
        "cases": cases,
        "corpus": {
            "id": _require_string(
                corpus.get("id"),
                "semantic calibration corpus id",
            ),
            "version": corpus["version"],
            "fingerprint": _fingerprint(
                "LCCORPUS",
                corpus,
                "semantic calibration corpus",
            ),
        },
        "protocol": {
            "id": protocol["id"],
            "version": protocol["version"],
            "fingerprint": _fingerprint(
                "LCPROTO",
                protocol,
                "live semantic evaluator protocol",
            ),
        },
        "evaluator": {
            "id": evaluator["id"],
            "provider": evaluator["provider"],
            "model": evaluator["model"],
            "model_version": evaluator["model_version"],
            "fingerprint": _fingerprint(
                "LCEVAL",
                evaluator,
                "semantic evaluator descriptor",
            ),
        },
    }


def build_live_calibration_request(
    *,
    corpus: dict[str, Any],
    protocol: dict[str, Any],
    evaluator: dict[str, Any],
    run_id: str,
) -> dict[str, Any]:
    """Build a label-blind request bound to one evaluator configuration and run."""
    run_id = _require_string(run_id, "live calibration run_id")
    bound = _binding(corpus, protocol, evaluator)
    request_payload = {
        "version": 1,
        "kind": "harness-live-semantic-calibration-request-binding",
        "run_id": run_id,
        "corpus": bound["corpus"],
        "protocol": bound["protocol"],
        "evaluator": bound["evaluator"],
    }
    request_id = _fingerprint(
        "LCREQ",
        request_payload,
        "live calibration request binding",
    )

    blinded_cases: list[dict[str, Any]] = []
    for ordinal, case in enumerate(bound["cases"]):
        case_request_id = _fingerprint(
            "LCCASE",
            {"request_id": request_id, "ordinal": ordinal},
            "live calibration case binding",
        )
        blinded_cases.append(
            {
                "case_request_id": case_request_id,
                "source": copy.deepcopy(case["source"]),
                "target": copy.deepcopy(case["target"]),
                "relation": case["relation"],
            }
        )

    return {
        "version": 1,
        "kind": "harness-live-semantic-calibration-request",
        "request_id": request_id,
        "run_id": run_id,
        "corpus": bound["corpus"],
        "protocol": {
            **bound["protocol"],
            "instruction": protocol["instruction"],
        },
        "evaluator": bound["evaluator"],
        "cases": blinded_cases,
    }


def _base_evaluation(
    *,
    request: dict[str, Any],
    evaluator: dict[str, Any],
) -> dict[str, Any]:
    return {
        "version": 1,
        "kind": "harness-live-semantic-calibration-evaluation",
        "run_id": request["run_id"],
        "request_id": request["request_id"],
        "corpus": copy.deepcopy(request["corpus"]),
        "protocol": {
            key: copy.deepcopy(value)
            for key, value in request["protocol"].items()
            if key != "instruction"
        },
        "evaluator": {
            **copy.deepcopy(evaluator),
            "fingerprint": request["evaluator"]["fingerprint"],
        },
        "independence": {
            "status": "UNVERIFIED",
            "harness_guarantees": [
                "EXPERT_LABELS_WITHHELD_FROM_EVALUATOR_REQUEST",
                "REQUEST_BOUND_RESPONSE_VALIDATION",
            ],
        },
    }


def _invalid(
    base: dict[str, Any],
    code: str,
    **details: Any,
) -> dict[str, Any]:
    return {
        **base,
        "status": "INVALID",
        "findings": [{"code": code, **details}],
        "calibration": None,
        "predictions": [],
    }


def evaluate_live_calibration_run(
    *,
    corpus: dict[str, Any],
    protocol: dict[str, Any],
    evaluator: dict[str, Any],
    run: Any,
) -> dict[str, Any]:
    """Validate one live run and score only request-bound predictions."""
    if not isinstance(run, dict):
        bound = _binding(corpus, protocol, evaluator)
        base = {
            "version": 1,
            "kind": "harness-live-semantic-calibration-evaluation",
            "run_id": None,
            "request_id": None,
            "corpus": bound["corpus"],
            "protocol": bound["protocol"],
            "evaluator": {
                **copy.deepcopy(evaluator),
                "fingerprint": bound["evaluator"]["fingerprint"],
            },
            "independence": {
                "status": "UNVERIFIED",
                "harness_guarantees": [],
            },
        }
        return _invalid(base, "LIVE_CALIBRATION_RUN_INVALID")

    run_id = run.get("run_id")
    if not isinstance(run_id, str) or not run_id:
        bound = _binding(corpus, protocol, evaluator)
        base = {
            "version": 1,
            "kind": "harness-live-semantic-calibration-evaluation",
            "run_id": None,
            "request_id": None,
            "corpus": bound["corpus"],
            "protocol": bound["protocol"],
            "evaluator": {
                **copy.deepcopy(evaluator),
                "fingerprint": bound["evaluator"]["fingerprint"],
            },
            "independence": {
                "status": "UNVERIFIED",
                "harness_guarantees": [],
            },
        }
        return _invalid(base, "LIVE_CALIBRATION_RUN_ID_INVALID")

    request = build_live_calibration_request(
        corpus=corpus,
        protocol=protocol,
        evaluator=evaluator,
        run_id=run_id,
    )
    base = _base_evaluation(request=request, evaluator=evaluator)

    if (
        run.get("version") != 1
        or run.get("kind") != "harness-live-semantic-calibration-run"
    ):
        return _invalid(base, "LIVE_CALIBRATION_RUN_INVALID")

    if run.get("request_id") != request["request_id"]:
        return _invalid(
            base,
            "LIVE_CALIBRATION_REQUEST_BINDING_MISMATCH",
            expected=request["request_id"],
            actual=run.get("request_id"),
        )

    state = run.get("state")
    if state not in RUN_STATES:
        return _invalid(
            base,
            "LIVE_CALIBRATION_RUN_STATE_INVALID",
            state=state,
        )
    if state != "COMPLETED":
        return {
            **base,
            "status": "INCOMPLETE",
            "findings": [
                {
                    "code": "LIVE_CALIBRATION_RUN_NOT_COMPLETED",
                    "state": state,
                }
            ],
            "calibration": None,
            "predictions": [],
        }

    results = run.get("results")
    if not isinstance(results, list):
        return _invalid(base, "LIVE_CALIBRATION_RESULTS_INVALID")

    case_map = {
        item["case_request_id"]: case["id"]
        for item, case in zip(
            request["cases"],
            _validate_corpus(corpus),
        )
    }
    seen: set[str] = set()
    predictions: list[dict[str, str]] = []
    evidence: list[dict[str, Any]] = []

    for index, item in enumerate(results):
        if not isinstance(item, dict):
            return _invalid(
                base,
                "LIVE_CALIBRATION_RESULT_INVALID",
                index=index,
            )
        case_request_id = item.get("case_request_id")
        if not isinstance(case_request_id, str) or not case_request_id:
            return _invalid(
                base,
                "LIVE_CALIBRATION_CASE_BINDING_INVALID",
                index=index,
            )
        if case_request_id in seen:
            return _invalid(
                base,
                "LIVE_CALIBRATION_DUPLICATE_RESULT",
                case_request_id=case_request_id,
            )
        seen.add(case_request_id)
        if case_request_id not in case_map:
            return _invalid(
                base,
                "LIVE_CALIBRATION_UNKNOWN_CASE_BINDING",
                case_request_id=case_request_id,
            )

        status = item.get("status")
        if status not in VERDICTS:
            return _invalid(
                base,
                "LIVE_CALIBRATION_VERDICT_INVALID",
                case_request_id=case_request_id,
                status=status,
            )

        rationale = item.get("rationale")
        if rationale is not None and not isinstance(rationale, str):
            return _invalid(
                base,
                "LIVE_CALIBRATION_RATIONALE_INVALID",
                case_request_id=case_request_id,
            )

        findings = item.get("findings", [])
        if not isinstance(findings, list):
            return _invalid(
                base,
                "LIVE_CALIBRATION_FINDINGS_INVALID",
                case_request_id=case_request_id,
            )

        case_id = case_map[case_request_id]
        predictions.append({"id": case_id, "status": status})
        evidence.append(
            {
                "case_id": case_id,
                "case_request_id": case_request_id,
                "status": status,
                "rationale": rationale,
                "findings": copy.deepcopy(findings),
            }
        )

    calibration = evaluate_judgement_calibration(
        corpus=corpus,
        predictions=predictions,
    )
    return {
        **base,
        "status": calibration["status"],
        "findings": [],
        "calibration": calibration,
        "predictions": evidence,
    }


def _runtime_binding(evaluation: dict[str, Any]) -> tuple[Any, ...] | None:
    execution = evaluation.get("execution")
    if not isinstance(execution, dict):
        return None
    provenance = execution.get("provider_provenance")
    if not isinstance(provenance, dict):
        return None
    return (
        provenance.get("provider"),
        provenance.get("requested_model"),
        provenance.get("resolved_model"),
        provenance.get("resolved_model_source"),
        provenance.get("observed_cli_version"),
    )


def evaluate_live_calibration_stability(
    *,
    evaluations: list[dict[str, Any]],
) -> dict[str, Any]:
    """Detect evaluator instability without inventing consensus semantics."""
    if not isinstance(evaluations, list) or len(evaluations) < 2:
        raise CoreError(
            "live calibration stability requires at least two evaluations"
        )

    first = evaluations[0]
    required_binding = (
        first.get("corpus", {}).get("fingerprint"),
        first.get("protocol", {}).get("fingerprint"),
        first.get("evaluator", {}).get("fingerprint"),
    )
    required_runtime_binding = _runtime_binding(first)
    run_ids: set[str] = set()
    verdicts: dict[str, set[str]] = {}

    for evaluation in evaluations:
        if evaluation.get("status") not in {"PASS", "FAIL"}:
            return {
                "version": 1,
                "kind": "harness-live-semantic-calibration-stability",
                "status": "INCOMPLETE",
                "findings": [
                    {"code": "LIVE_CALIBRATION_SERIES_RUN_NOT_SCORABLE"}
                ],
                "unstable_cases": [],
            }

        current_binding = (
            evaluation.get("corpus", {}).get("fingerprint"),
            evaluation.get("protocol", {}).get("fingerprint"),
            evaluation.get("evaluator", {}).get("fingerprint"),
        )
        if current_binding != required_binding:
            return {
                "version": 1,
                "kind": "harness-live-semantic-calibration-stability",
                "status": "INVALID",
                "findings": [
                    {"code": "LIVE_CALIBRATION_SERIES_BINDING_MISMATCH"}
                ],
                "unstable_cases": [],
            }

        current_runtime_binding = _runtime_binding(evaluation)
        if current_runtime_binding != required_runtime_binding:
            return {
                "version": 1,
                "kind": "harness-live-semantic-calibration-stability",
                "status": "INVALID",
                "findings": [
                    {
                        "code": "LIVE_CALIBRATION_SERIES_RUNTIME_BINDING_MISMATCH",
                        "expected": required_runtime_binding,
                        "actual": current_runtime_binding,
                    }
                ],
                "unstable_cases": [],
            }

        run_id = evaluation.get("run_id")
        if (
            not isinstance(run_id, str)
            or not run_id
            or run_id in run_ids
        ):
            return {
                "version": 1,
                "kind": "harness-live-semantic-calibration-stability",
                "status": "INVALID",
                "findings": [
                    {"code": "LIVE_CALIBRATION_SERIES_RUN_ID_INVALID"}
                ],
                "unstable_cases": [],
            }
        run_ids.add(run_id)

        for prediction in evaluation.get("predictions", []) or []:
            verdicts.setdefault(
                prediction["case_id"],
                set(),
            ).add(prediction["status"])

    unstable = sorted(
        case_id
        for case_id, statuses in verdicts.items()
        if len(statuses) > 1
    )
    return {
        "version": 1,
        "kind": "harness-live-semantic-calibration-stability",
        "status": "UNSTABLE" if unstable else "STABLE",
        "run_ids": sorted(run_ids),
        "unstable_cases": unstable,
        "findings": (
            [
                {
                    "code": "LIVE_CALIBRATION_UNSTABLE_VERDICTS",
                    "cases": unstable,
                }
            ]
            if unstable
            else []
        ),
    }


__all__ = [
    'Any',
    'CoreError',
    'RUN_STATES',
    'VERDICTS',
    'annotations',
    'build_live_calibration_request',
    'copy',
    'evaluate_judgement_calibration',
    'evaluate_live_calibration_run',
    'evaluate_live_calibration_stability',
    'hashlib',
    'json',
]
