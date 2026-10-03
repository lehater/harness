#!/usr/bin/env python3
"""Dedicated greenfield bootstrap behavioural evaluation runner."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import uuid
from pathlib import Path
from typing import Any

import yaml

from evals.behavioral_eval import (
    BehavioralEvalError,
    ProcessExecutionAdapter,
    build_execution_request,
    load_agent_descriptor,
    load_case,
)


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _require_string_list(
    value: Any,
    label: str,
    *,
    nonempty: bool = True,
) -> list[str]:
    if not isinstance(value, list):
        raise BehavioralEvalError(f"{label} must be a list")
    if nonempty and not value:
        raise BehavioralEvalError(f"{label} must be non-empty")
    if not all(isinstance(item, str) and item for item in value):
        raise BehavioralEvalError(f"{label} must contain non-empty strings")
    return value


def _derive_initial_frontier(
    capabilities: list[dict[str, Any]],
    questions: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    blocked_capabilities = {
        tuple(sorted(question["blocks_atoms"]))
        for question in questions
    }
    frontier: list[dict[str, Any]] = []
    for capability in capabilities:
        support = capability["support_atoms"]
        if capability["prerequisite_atoms"]:
            disposition = "PENDING"
        elif tuple(support) in blocked_capabilities:
            disposition = "WAIT"
        else:
            disposition = "CREATE"
        frontier.append({
            "support_atoms": support,
            "disposition": disposition,
        })
    return frontier


def canonical_greenfield_bootstrap(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise BehavioralEvalError(f"{label} must be a mapping")

    capabilities = value.get("capabilities")
    questions = value.get("questions")
    frontier = value.get("frontier")
    if not all(isinstance(item, list) for item in (capabilities, questions)):
        raise BehavioralEvalError(
            f"{label}.capabilities/questions must be lists"
        )
    if frontier is not None and not isinstance(frontier, list):
        raise BehavioralEvalError(f"{label}.frontier must be a list when present")

    normalized_capabilities: list[dict[str, Any]] = []
    for index, item in enumerate(capabilities):
        if not isinstance(item, dict):
            raise BehavioralEvalError(
                f"{label}.capabilities[{index}] must be a mapping"
            )
        support = sorted(set(_require_string_list(
            item.get("support_atoms"),
            f"{label}.capabilities[{index}].support_atoms",
        )))
        prerequisites = sorted(set(_require_string_list(
            item.get("prerequisite_atoms", []),
            f"{label}.capabilities[{index}].prerequisite_atoms",
            nonempty=False,
        )))
        normalized_capabilities.append({
            "support_atoms": support,
            "prerequisite_atoms": prerequisites,
        })

    normalized_questions: list[dict[str, Any]] = []
    for index, item in enumerate(questions):
        if not isinstance(item, dict):
            raise BehavioralEvalError(
                f"{label}.questions[{index}] must be a mapping"
            )
        support = sorted(set(_require_string_list(
            item.get("support_atoms"),
            f"{label}.questions[{index}].support_atoms",
        )))
        blocks = sorted(set(_require_string_list(
            item.get("blocks_atoms"),
            f"{label}.questions[{index}].blocks_atoms",
        )))
        normalized_questions.append({
            "support_atoms": support,
            "blocks_atoms": blocks,
        })

    key = lambda item: json.dumps(item, sort_keys=True)
    normalized_capabilities = sorted(normalized_capabilities, key=key)
    normalized_questions = sorted(normalized_questions, key=key)

    if frontier is None:
        normalized_frontier = _derive_initial_frontier(
            normalized_capabilities,
            normalized_questions,
        )
    else:
        normalized_frontier: list[dict[str, Any]] = []
        for index, item in enumerate(frontier):
            if not isinstance(item, dict):
                raise BehavioralEvalError(
                    f"{label}.frontier[{index}] must be a mapping"
                )
            support = sorted(set(_require_string_list(
                item.get("support_atoms"),
                f"{label}.frontier[{index}].support_atoms",
            )))
            disposition = item.get("disposition")
            if disposition not in {"CREATE", "WAIT", "PENDING", "COMPLETE"}:
                raise BehavioralEvalError(
                    f"{label}.frontier[{index}].disposition is invalid"
                )
            normalized_frontier.append({
                "support_atoms": support,
                "disposition": disposition,
            })

    return {
        "capabilities": normalized_capabilities,
        "questions": normalized_questions,
        "frontier": sorted(normalized_frontier, key=key),
    }


def normalize_result(binding, response: dict[str, Any]) -> dict[str, Any]:
    dimensions = binding.case["normalization_profile"]["dimensions"]
    if dimensions != ["greenfield_bootstrap"]:
        raise BehavioralEvalError(
            "greenfield runner requires exactly greenfield_bootstrap dimension"
        )
    output = response.get("output")
    if not isinstance(output, dict):
        raise BehavioralEvalError("response output must be a mapping")
    return {
        "greenfield_bootstrap": canonical_greenfield_bootstrap(
            output.get("greenfield_bootstrap"),
            "greenfield bootstrap",
        )
    }


def _questions_materially_compatible(
    expected: list[dict[str, Any]],
    actual: list[dict[str, Any]],
) -> bool:
    if len(expected) != len(actual):
        return False
    remaining = list(actual)
    for expected_question in expected:
        expected_blocks = set(expected_question["blocks_atoms"])
        expected_support = set(expected_question["support_atoms"])
        match_index = next(
            (
                index
                for index, candidate in enumerate(remaining)
                if set(candidate["blocks_atoms"]) == expected_blocks
            ),
            None,
        )
        if match_index is None:
            return False
        candidate = remaining.pop(match_index)
        actual_support = set(candidate["support_atoms"])
        if not expected_support <= actual_support:
            return False
        if not actual_support <= expected_support | expected_blocks:
            return False
    return not remaining


def _materially_compatible(expected: dict[str, Any], actual: dict[str, Any]) -> bool:
    return (
        actual["capabilities"] == expected["capabilities"]
        and actual["frontier"] == expected["frontier"]
        and _questions_materially_compatible(
            expected["questions"],
            actual["questions"],
        )
    )


def score_result(binding, normalized: dict[str, Any]) -> dict[str, Any]:
    required = binding.case["pass_criteria"].get("require_dimensions")
    if required != ["greenfield_bootstrap"]:
        raise BehavioralEvalError(
            "greenfield pass criteria must require greenfield_bootstrap"
        )
    oracle_value = binding.oracle["dimensions"].get("greenfield_bootstrap")
    expected = canonical_greenfield_bootstrap(
        oracle_value,
        "oracle greenfield_bootstrap",
    )
    actual = normalized["greenfield_bootstrap"]
    passed = _materially_compatible(expected, actual)
    return {
        "status": "PASS" if passed else "FAIL",
        "dimensions": {
            "greenfield_bootstrap": {
                "status": "PASS" if passed else "FAIL",
                "expected": expected,
                "actual": actual,
            }
        },
        "findings": [] if passed else [{
            "code": "WRONG_GREENFIELD_BOOTSTRAP",
            "dimension": "greenfield_bootstrap",
        }],
    }


def build_run_record(
    binding,
    *,
    run_id: str,
    agent_descriptor: dict[str, Any],
    agent_descriptor_sha256: str,
    response: dict[str, Any],
) -> dict[str, Any]:
    run_status = response["run_status"]
    normalized: dict[str, Any] | None = None
    correctness: dict[str, Any] = {
        "status": "NOT_SCORED",
        "dimensions": {},
        "findings": [],
    }
    if run_status == "COMPLETED":
        try:
            normalized = normalize_result(binding, response)
            correctness = score_result(binding, normalized)
        except BehavioralEvalError as exc:
            run_status = "INCOMPLETE"
            correctness = {
                "status": "NOT_SCORED",
                "dimensions": {},
                "findings": [{
                    "code": "STRUCTURALLY_INVALID_OUTPUT",
                    "message": str(exc),
                }],
            }

    provenance = response.get("provenance", {})
    record = {
        "version": 1,
        "kind": "harness-agent-behavioral-eval-run",
        "run_id": run_id,
        "case_id": binding.case["case_id"],
        "harness_revision": binding.case["harness_revision"],
        "fixture_revision": binding.case["fixture_revision"],
        "consumer_pack_revision": binding.case.get("consumer_pack_revision"),
        "agent_descriptor": agent_descriptor,
        "bindings": {
            "case_sha256": binding.case_sha256,
            "fixture_sha256": binding.fixture_sha256,
            "oracle_sha256": binding.oracle_sha256,
            "agent_descriptor_sha256": agent_descriptor_sha256,
        },
        "started_from_clean_context": bool(
            provenance.get("fresh_home")
            and provenance.get("isolated_working_directory")
        ),
        "selected_operation": response.get("selected_operation"),
        "resolved_routes": response.get("resolved_routes", []),
        "output_refs": response.get("output_refs", []),
        "normalization_result": normalized,
        "validator_results": response.get("validator_results", []),
        "execution_findings": response.get("execution_findings", []),
        "trace": response.get("trace", []),
        "run_status": run_status,
        "correctness": correctness,
        "provenance": provenance,
    }
    canonical = json.dumps(
        record,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )
    record["record_sha256"] = _sha256(canonical.encode("utf-8"))
    return record


def write_run_record(path: Path, record: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as handle:
        json.dump(record, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")


def execute_case(
    binding,
    *,
    adapter: ProcessExecutionAdapter,
    agent_descriptor: dict[str, Any],
    agent_descriptor_sha256: str,
    output_dir: Path,
) -> list[dict[str, Any]]:
    if binding.case["run_plan"].get("sequence") is not None:
        raise BehavioralEvalError("greenfield runner does not support run sequences")
    records: list[dict[str, Any]] = []
    for index in range(1, binding.case["run_plan"]["runs"] + 1):
        run_id = f"{binding.case['case_id']}-R{index:02d}-{uuid.uuid4().hex[:12]}"
        request = build_execution_request(
            binding,
            run_id=run_id,
            agent_descriptor=agent_descriptor,
            agent_descriptor_sha256=agent_descriptor_sha256,
        )
        response = adapter.execute(request, agent_descriptor=agent_descriptor)
        record = build_run_record(
            binding,
            run_id=run_id,
            agent_descriptor=agent_descriptor,
            agent_descriptor_sha256=agent_descriptor_sha256,
            response=response,
        )
        write_run_record(output_dir / f"{run_id}.json", record)
        records.append(record)
    return records


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run one Harness greenfield bootstrap behavioral eval case"
    )
    parser.add_argument("case")
    parser.add_argument("--agent-descriptor", required=True)
    parser.add_argument("--adapter-executable", required=True)
    parser.add_argument("--adapter-arg", action="append", default=[])
    parser.add_argument("--timeout-seconds", type=float, default=180.0)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--json-summary")
    args = parser.parse_args()

    try:
        binding = load_case(args.case)
        descriptor, descriptor_sha = load_agent_descriptor(args.agent_descriptor)
        records = execute_case(
            binding,
            adapter=ProcessExecutionAdapter(
                args.adapter_executable,
                args.adapter_arg,
                timeout_seconds=args.timeout_seconds,
            ),
            agent_descriptor=descriptor,
            agent_descriptor_sha256=descriptor_sha,
            output_dir=Path(args.output_dir),
        )
    except (BehavioralEvalError, OSError, yaml.YAMLError, json.JSONDecodeError) as exc:
        print(f"Greenfield behavioral eval failed: {exc}", file=os.sys.stderr)
        return 2

    summary = {
        "case_id": binding.case["case_id"],
        "runs": len(records),
        "run_statuses": [record["run_status"] for record in records],
        "correctness": [record["correctness"]["status"] for record in records],
        "all_completed": all(
            record["run_status"] == "COMPLETED" for record in records
        ),
        "all_passed": all(
            record["correctness"]["status"] == "PASS" for record in records
        ),
    }
    if args.json_summary:
        Path(args.json_summary).write_text(
            json.dumps(summary, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    print(json.dumps(summary, sort_keys=True))
    return 0 if summary["all_completed"] and summary["all_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
