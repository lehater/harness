#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml

REVIEW_CHECK = "executable-correspondence"
REVIEW_STATUSES = {"ACCEPTED", "REJECTED", "QUESTION"}


def load_yaml(path: str | Path) -> dict[str, Any]:
    with open(path, "r", encoding="utf-8") as stream:
        data = yaml.safe_load(stream)
    if not isinstance(data, dict):
        raise ValueError("test realization input must be a YAML mapping")
    return data


def _finding(
    findings: list[dict[str, Any]],
    code: str,
    path: str,
    message: str,
    **details: Any,
) -> None:
    finding: dict[str, Any] = {
        "code": code,
        "path": path,
        "message": message,
    }
    finding.update(details)
    findings.append(finding)


def _canonical_contract(
    test_design: dict[str, Any],
    contract_id: str | None,
    findings: list[dict[str, Any]],
) -> dict[str, Any] | None:
    if test_design.get("schema") != "test-design/v1":
        _finding(
            findings,
            "TEST_DESIGN_SCHEMA_INVALID",
            "test_design.schema",
            "canonical Test Design must use schema test-design/v1",
        )
        return None

    content = test_design.get("content")
    tests = content.get("tests") if isinstance(content, dict) else None
    if not isinstance(tests, list):
        _finding(
            findings,
            "TEST_DESIGN_CONTRACTS_INVALID",
            "test_design.content.tests",
            "canonical Test Design tests must be a list",
        )
        return None

    if not isinstance(contract_id, str) or not contract_id.strip():
        _finding(
            findings,
            "TEST_REALIZATION_CONTRACT_REF_MISSING",
            "evidence.test_contract",
            "test realization evidence must reference one Test Design contract",
        )
        return None

    matches = [
        item
        for item in tests
        if isinstance(item, dict) and item.get("id") == contract_id
    ]
    if len(matches) != 1:
        _finding(
            findings,
            "TEST_REALIZATION_CONTRACT_UNRESOLVED",
            "evidence.test_contract",
            f"expected exactly one canonical Test Design contract {contract_id}",
            test_contract=contract_id,
        )
        return None
    return matches[0]


def _obligation_ids(
    contract: dict[str, Any],
    field: str,
    obligation_kind: str,
    findings: list[dict[str, Any]],
) -> list[str]:
    raw = contract.get(field)
    if not isinstance(raw, list) or not raw:
        _finding(
            findings,
            "TEST_CONTRACT_OBLIGATIONS_UNADDRESSABLE",
            f"test_design.{field}",
            (
                f"selected Test Design contract requires non-empty {field} "
                "with stable obligation ids"
            ),
            obligation_kind=obligation_kind,
        )
        return []

    result: list[str] = []
    seen: set[str] = set()
    for index, item in enumerate(raw):
        path = f"test_design.{field}[{index}]"
        if not isinstance(item, dict):
            _finding(
                findings,
                "TEST_CONTRACT_OBLIGATION_INVALID",
                path,
                "Test Design obligation must be a mapping",
                obligation_kind=obligation_kind,
            )
            continue
        obligation_id = item.get("id")
        description = item.get("description")
        if not isinstance(obligation_id, str) or not obligation_id.strip():
            _finding(
                findings,
                "TEST_CONTRACT_OBLIGATION_ID_MISSING",
                f"{path}.id",
                "Test Design obligation requires a stable id",
                obligation_kind=obligation_kind,
            )
            continue
        if obligation_id in seen:
            _finding(
                findings,
                "TEST_CONTRACT_OBLIGATION_DUPLICATE",
                f"{path}.id",
                f"duplicate Test Design obligation id {obligation_id}",
                obligation=obligation_id,
                obligation_kind=obligation_kind,
            )
            continue
        if not isinstance(description, str) or not description.strip():
            _finding(
                findings,
                "TEST_CONTRACT_OBLIGATION_DESCRIPTION_MISSING",
                f"{path}.description",
                f"Test Design obligation {obligation_id} requires a description",
                obligation=obligation_id,
                obligation_kind=obligation_kind,
            )
            continue
        seen.add(obligation_id)
        result.append(obligation_id)
    return result


def evaluate(
    test_design: dict[str, Any],
    evidence: dict[str, Any],
    semantic_review: dict[str, Any],
) -> dict[str, Any]:
    findings: list[dict[str, Any]] = []

    if evidence.get("version") != 1:
        _finding(
            findings,
            "TEST_REALIZATION_EVIDENCE_VERSION_INVALID",
            "evidence.version",
            "test realization evidence version must be 1",
        )
    if evidence.get("kind") != "harness-test-realization-evidence":
        _finding(
            findings,
            "TEST_REALIZATION_EVIDENCE_KIND_INVALID",
            "evidence.kind",
            "kind must be harness-test-realization-evidence",
        )

    contract_id = evidence.get("test_contract")
    contract = _canonical_contract(test_design, contract_id, findings)

    operation_ids: list[str] = []
    oracle_ids: list[str] = []
    if contract is not None:
        operation_ids = _obligation_ids(
            contract,
            "operation_obligations",
            "operation",
            findings,
        )
        oracle_ids = _obligation_ids(
            contract,
            "oracle_obligations",
            "oracle",
            findings,
        )
        overlap = set(operation_ids) & set(oracle_ids)
        for obligation_id in sorted(overlap):
            _finding(
                findings,
                "TEST_CONTRACT_OBLIGATION_KIND_COLLISION",
                "test_design",
                (
                    f"obligation id {obligation_id} is used by both an operation "
                    "and an oracle"
                ),
                obligation=obligation_id,
            )

    executables = evidence.get("executables")
    executable_ids: set[str] = set()
    passed_executable_ids: set[str] = set()
    if not isinstance(executables, list) or not executables:
        _finding(
            findings,
            "TEST_REALIZATION_EXECUTABLE_EVIDENCE_MISSING",
            "evidence.executables",
            "at least one executable test evidence item is required",
        )
        executables = []
    for index, executable in enumerate(executables):
        path = f"evidence.executables[{index}]"
        if not isinstance(executable, dict):
            _finding(
                findings,
                "TEST_REALIZATION_EXECUTABLE_INVALID",
                path,
                "executable evidence must be a mapping",
            )
            continue
        executable_id = executable.get("id")
        locator = executable.get("test")
        status = executable.get("status")
        if not isinstance(executable_id, str) or not executable_id.strip():
            _finding(
                findings,
                "TEST_REALIZATION_EXECUTABLE_ID_MISSING",
                f"{path}.id",
                "executable evidence requires a stable id",
            )
            continue
        if executable_id in executable_ids:
            _finding(
                findings,
                "TEST_REALIZATION_EXECUTABLE_DUPLICATE",
                f"{path}.id",
                f"duplicate executable evidence id {executable_id}",
                executable=executable_id,
            )
            continue
        executable_ids.add(executable_id)
        if not isinstance(locator, str) or not locator.strip():
            _finding(
                findings,
                "TEST_REALIZATION_EXECUTABLE_LOCATOR_MISSING",
                f"{path}.test",
                f"executable evidence {executable_id} requires a test locator",
                executable=executable_id,
            )
        if status != "PASSED":
            _finding(
                findings,
                "TEST_REALIZATION_EXECUTABLE_NOT_PASSED",
                f"{path}.status",
                f"executable evidence {executable_id} must record PASSED",
                executable=executable_id,
            )
        else:
            passed_executable_ids.add(executable_id)

    required_ids = set(operation_ids) | set(oracle_ids)
    bindings = evidence.get("bindings")
    binding_by_id: dict[str, dict[str, Any]] = {}
    if not isinstance(bindings, list):
        _finding(
            findings,
            "TEST_REALIZATION_BINDINGS_INVALID",
            "evidence.bindings",
            "bindings must be a list",
        )
        bindings = []

    for index, binding in enumerate(bindings):
        path = f"evidence.bindings[{index}]"
        if not isinstance(binding, dict):
            _finding(
                findings,
                "TEST_REALIZATION_BINDING_INVALID",
                path,
                "binding must be a mapping",
            )
            continue
        binding_id = binding.get("id")
        obligation_id = binding.get("obligation")
        evidence_refs = binding.get("evidence")
        if not isinstance(binding_id, str) or not binding_id.strip():
            _finding(
                findings,
                "TEST_REALIZATION_BINDING_ID_MISSING",
                f"{path}.id",
                "binding requires a stable id",
            )
            continue
        if binding_id in binding_by_id:
            _finding(
                findings,
                "TEST_REALIZATION_BINDING_DUPLICATE",
                f"{path}.id",
                f"duplicate binding id {binding_id}",
                binding=binding_id,
            )
            continue
        binding_by_id[binding_id] = binding

        if obligation_id not in required_ids:
            _finding(
                findings,
                "TEST_REALIZATION_BINDING_OBLIGATION_UNKNOWN",
                f"{path}.obligation",
                f"binding {binding_id} references unknown obligation {obligation_id}",
                binding=binding_id,
                obligation=obligation_id,
            )
        if (
            not isinstance(evidence_refs, list)
            or not evidence_refs
            or any(
                not isinstance(value, str) or not value.strip()
                for value in evidence_refs
            )
        ):
            _finding(
                findings,
                "TEST_REALIZATION_BINDING_EVIDENCE_MISSING",
                f"{path}.evidence",
                f"binding {binding_id} requires executable evidence refs",
                binding=binding_id,
                obligation=obligation_id,
            )
            continue
        unknown_evidence = sorted(set(evidence_refs) - executable_ids)
        if unknown_evidence:
            _finding(
                findings,
                "TEST_REALIZATION_BINDING_EVIDENCE_UNKNOWN",
                f"{path}.evidence",
                (
                    f"binding {binding_id} references unknown executable evidence "
                    f"{unknown_evidence}"
                ),
                binding=binding_id,
                obligation=obligation_id,
            )

    review_ok = True
    if not isinstance(semantic_review, dict):
        review_ok = False
        _finding(
            findings,
            "TEST_REALIZATION_SEMANTIC_REVIEW_MISSING",
            "semantic_review",
            "semantic correspondence review is required",
        )
        semantic_review = {}

    if semantic_review.get("version") != 1:
        review_ok = False
        _finding(
            findings,
            "TEST_REALIZATION_SEMANTIC_REVIEW_VERSION_INVALID",
            "semantic_review.version",
            "semantic review version must be 1",
        )
    if semantic_review.get("kind") != "harness-test-realization-semantic-review":
        review_ok = False
        _finding(
            findings,
            "TEST_REALIZATION_SEMANTIC_REVIEW_KIND_INVALID",
            "semantic_review.kind",
            "kind must be harness-test-realization-semantic-review",
        )
    if semantic_review.get("status") != "ACCEPTED":
        review_ok = False
        _finding(
            findings,
            "TEST_REALIZATION_SEMANTIC_REVIEW_NOT_ACCEPTED",
            "semantic_review.status",
            "semantic correspondence review must be ACCEPTED",
        )
    checks = semantic_review.get("checks")
    if not isinstance(checks, list) or REVIEW_CHECK not in checks:
        review_ok = False
        _finding(
            findings,
            "TEST_REALIZATION_CORRESPONDENCE_CHECK_MISSING",
            "semantic_review.checks",
            f"semantic review must include {REVIEW_CHECK}",
        )

    binding_reviews = semantic_review.get("binding_reviews")
    accepted_bindings: set[str] = set()
    reviewed_bindings: set[str] = set()
    if not isinstance(binding_reviews, list):
        review_ok = False
        _finding(
            findings,
            "TEST_REALIZATION_BINDING_REVIEWS_INVALID",
            "semantic_review.binding_reviews",
            "binding_reviews must be a list",
        )
        binding_reviews = []

    for index, review in enumerate(binding_reviews):
        path = f"semantic_review.binding_reviews[{index}]"
        if not isinstance(review, dict):
            _finding(
                findings,
                "TEST_REALIZATION_BINDING_REVIEW_INVALID",
                path,
                "binding review must be a mapping",
            )
            continue
        binding_id = review.get("binding")
        status = review.get("status")
        if binding_id not in binding_by_id:
            _finding(
                findings,
                "TEST_REALIZATION_BINDING_REVIEW_UNKNOWN",
                f"{path}.binding",
                f"semantic review references unknown binding {binding_id}",
                binding=binding_id,
            )
            continue
        if binding_id in reviewed_bindings:
            _finding(
                findings,
                "TEST_REALIZATION_BINDING_REVIEW_DUPLICATE",
                f"{path}.binding",
                f"binding {binding_id} is reviewed more than once",
                binding=binding_id,
            )
            continue
        reviewed_bindings.add(binding_id)
        if status not in REVIEW_STATUSES:
            _finding(
                findings,
                "TEST_REALIZATION_BINDING_REVIEW_STATUS_INVALID",
                f"{path}.status",
                f"expected one of {sorted(REVIEW_STATUSES)}",
                binding=binding_id,
            )
            continue
        if status == "ACCEPTED":
            accepted_bindings.add(binding_id)

    for binding_id in sorted(set(binding_by_id) - reviewed_bindings):
        _finding(
            findings,
            "TEST_REALIZATION_BINDING_UNREVIEWED",
            "semantic_review.binding_reviews",
            f"binding {binding_id} has no semantic correspondence review",
            binding=binding_id,
        )

    credible_obligations: set[str] = set()
    if review_ok:
        for binding_id in accepted_bindings:
            binding = binding_by_id[binding_id]
            obligation_id = binding.get("obligation")
            evidence_refs = binding.get("evidence")
            if obligation_id not in required_ids or not isinstance(evidence_refs, list):
                continue
            if evidence_refs and set(evidence_refs) <= passed_executable_ids:
                credible_obligations.add(obligation_id)

    for obligation_id in operation_ids:
        if obligation_id not in credible_obligations:
            _finding(
                findings,
                "TEST_REALIZATION_OPERATION_MISSING",
                "evidence.bindings",
                (
                    f"required operation obligation {obligation_id} has no "
                    "accepted executable evidence binding"
                ),
                obligation=obligation_id,
                obligation_kind="operation",
            )

    for obligation_id in oracle_ids:
        if obligation_id not in credible_obligations:
            _finding(
                findings,
                "TEST_REALIZATION_ORACLE_MISSING",
                "evidence.bindings",
                (
                    f"required oracle obligation {obligation_id} has no "
                    "accepted executable evidence binding"
                ),
                obligation=obligation_id,
                obligation_kind="oracle",
            )

    return {
        "kind": "harness-test-realization-evaluation",
        "test_contract": contract_id,
        "status": "ACCEPTED" if not findings else "REJECTED",
        "coverage": {
            "operations": {
                "required": len(operation_ids),
                "covered": len(set(operation_ids) & credible_obligations),
            },
            "oracles": {
                "required": len(oracle_ids),
                "covered": len(set(oracle_ids) & credible_obligations),
            },
        },
        "findings": findings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Evaluate executable-test evidence against one accepted Test Design "
            "contract and its semantic correspondence review."
        )
    )
    parser.add_argument("test_design")
    parser.add_argument("evidence")
    parser.add_argument("semantic_review")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    result = evaluate(
        load_yaml(args.test_design),
        load_yaml(args.evidence),
        load_yaml(args.semantic_review),
    )
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(result["status"])
        for finding in result["findings"]:
            suffix = (
                f" [{finding['obligation']}]"
                if finding.get("obligation")
                else ""
            )
            print(f"{finding['code']}{suffix}: {finding['message']}")
    return 0 if result["status"] == "ACCEPTED" else 1


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "REVIEW_CHECK",
    "REVIEW_STATUSES",
    "evaluate",
    "load_yaml",
    "main",
]
