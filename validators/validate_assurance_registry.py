#!/usr/bin/env python3
"""Validate the initial Harness Assurance Registry seed and its meta-invariants."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import tempfile
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "spec/assurance/harness-assurance-registry-v0.yaml"
ACTIVE_EVIDENCE_STATUSES = {"implemented", "verified"}
VALID_EVIDENCE_STATUSES = {
    "designed",
    "ready",
    "implemented",
    "verified",
    "stale",
    "retired",
}
VALID_ABILITY_EXECUTION_NATURES = {"deterministic", "judgement-dependent", "mixed"}
VALID_EVIDENCE_EXECUTION_NATURES = {"deterministic", "judgement-dependent"}
VALID_SOURCE_TYPES = {
    "synthetic",
    "known-project",
    "independent-holdout",
    "inspection",
    "external",
}
TEST_LEVEL_RANK = {f"TL{i}": i for i in range(7)}
ORACLE_RANK = {f"O{i}": i for i in range(5)}


class RegistryError(ValueError):
    """Raised when assurance registry structure or references are invalid."""


def load_yaml(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RegistryError(f"{path.relative_to(ROOT)} must contain a mapping")
    return value


def canonical_ids(root: Path) -> tuple[set[str], set[str], set[str]]:
    owner = (root / "docs/design/harness-ability-to-evidence-v0.md").read_text(
        encoding="utf-8"
    )
    abilities = set(re.findall(r"\bHA-A\d{2}\b", owner))
    failure_modes = set(re.findall(r"\bA\d{2}-F\d{2}\b", owner))
    methods = set(re.findall(r"\bEM-\d{2}\b", owner))
    if not abilities or not failure_modes or not methods:
        raise RegistryError("canonical assurance identifiers could not be derived")
    return abilities, failure_modes, methods


def _mapping_list(value: Any, label: str) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        raise RegistryError(f"{label} must be a list")
    if not all(isinstance(item, dict) for item in value):
        raise RegistryError(f"{label} entries must be mappings")
    return value


def _index(records: list[dict[str, Any]], label: str) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for record in records:
        record_id = record.get("id")
        if not isinstance(record_id, str) or not record_id:
            raise RegistryError(f"{label} record has no stable id")
        if record_id in result:
            raise RegistryError(f"duplicate {label} id: {record_id}")
        result[record_id] = record
    return result


def validate_structure(registry: dict[str, Any], root: Path = ROOT) -> None:
    if registry.get("version") != 1:
        raise RegistryError("registry version must be 1")
    if registry.get("kind") != "harness-assurance-registry":
        raise RegistryError("registry kind must be harness-assurance-registry")

    policy = registry.get("policy")
    owner_ref = registry.get("semantic_owner")
    for label, relative in (("policy", policy), ("semantic_owner", owner_ref)):
        if not isinstance(relative, str) or not relative:
            raise RegistryError(f"{label} must be a repository path")
        if not (root / relative).is_file():
            raise RegistryError(f"{label} path does not exist: {relative}")

    canonical_abilities, canonical_failures, canonical_methods = canonical_ids(root)
    abilities = _mapping_list(registry.get("abilities"), "abilities")
    requirements = _mapping_list(registry.get("requirements"), "requirements")
    evidence = _mapping_list(registry.get("evidence"), "evidence")
    ability_by_id = _index(abilities, "ability")
    requirement_by_id = _index(requirements, "requirement")
    _index(evidence, "evidence")

    for ability_id, ability in ability_by_id.items():
        if ability_id not in canonical_abilities:
            raise RegistryError(f"unknown ability id: {ability_id}")
        if not isinstance(ability.get("release_critical"), bool):
            raise RegistryError(f"{ability_id}: release_critical must be boolean")
        if ability.get("execution_nature") not in VALID_ABILITY_EXECUTION_NATURES:
            raise RegistryError(f"{ability_id}: invalid execution_nature")
        contract_ref = ability.get("contract_ref")
        if not isinstance(contract_ref, dict):
            raise RegistryError(f"{ability_id}: contract_ref must be a mapping")
        contract_path = contract_ref.get("path")
        if contract_path != owner_ref:
            raise RegistryError(
                f"{ability_id}: contract_ref must point to canonical semantic owner"
            )

        failures = ability.get("failure_modes")
        if not isinstance(failures, list) or not failures:
            raise RegistryError(f"{ability_id}: failure_modes must be non-empty")
        for failure in failures:
            if failure not in canonical_failures:
                raise RegistryError(f"{ability_id}: unknown failure mode {failure}")

        req_ids = ability.get("requirements")
        if not isinstance(req_ids, list) or not req_ids:
            raise RegistryError(f"{ability_id}: requirements must be non-empty")
        for requirement_id in req_ids:
            requirement = requirement_by_id.get(requirement_id)
            if requirement is None:
                raise RegistryError(
                    f"{ability_id}: unknown requirement {requirement_id}"
                )
            if requirement.get("ability") != ability_id:
                raise RegistryError(
                    f"{requirement_id}: ability mismatch for {ability_id}"
                )

        if ability["release_critical"]:
            mapped = {
                failure
                for requirement_id in req_ids
                for failure in requirement_by_id[requirement_id].get(
                    "failure_modes", []
                )
            }
            orphaned = set(failures) - mapped
            if orphaned:
                raise RegistryError(
                    f"{ability_id}: orphan release-critical failure modes: "
                    + ", ".join(sorted(orphaned))
                )

    for requirement_id, requirement in requirement_by_id.items():
        ability_id = requirement.get("ability")
        ability = ability_by_id.get(ability_id)
        if ability is None:
            raise RegistryError(
                f"{requirement_id}: unknown ability id {ability_id!r}"
            )
        failures = requirement.get("failure_modes")
        if not isinstance(failures, list) or not failures:
            raise RegistryError(
                f"{requirement_id}: failure_modes must be non-empty"
            )
        for failure in failures:
            if failure not in canonical_failures:
                raise RegistryError(
                    f"{requirement_id}: unknown failure mode {failure}"
                )
            if failure not in ability["failure_modes"]:
                raise RegistryError(
                    f"{requirement_id}: failure mode {failure} is not registered "
                    f"for {ability_id}"
                )

        required = requirement.get("required")
        if not isinstance(required, dict):
            raise RegistryError(f"{requirement_id}: required must be a mapping")
        levels = required.get("test_levels")
        if (
            not isinstance(levels, list)
            or not levels
            or any(level not in TEST_LEVEL_RANK for level in levels)
        ):
            raise RegistryError(f"{requirement_id}: invalid test_levels")
        methods = required.get("methods_any")
        if (
            not isinstance(methods, list)
            or not methods
            or any(method not in canonical_methods for method in methods)
        ):
            raise RegistryError(f"{requirement_id}: invalid methods_any")
        oracle = required.get("oracle_minimum")
        if oracle not in ORACLE_RANK:
            raise RegistryError(f"{requirement_id}: invalid oracle_minimum")
        if not isinstance(required.get("judgement_execution"), bool):
            raise RegistryError(
                f"{requirement_id}: judgement_execution must be boolean"
            )
        substitution = requirement.get("substitution")
        if not isinstance(substitution, dict) or not isinstance(
            substitution.get("higher_level_alone_allowed"), bool
        ):
            raise RegistryError(
                f"{requirement_id}: invalid substitution policy"
            )
        if not isinstance(requirement.get("release_applicable"), bool):
            raise RegistryError(
                f"{requirement_id}: release_applicable must be boolean"
            )
        if requirement.get("status") != "required":
            raise RegistryError(f"{requirement_id}: status must be required")

    for evidence_item in evidence:
        evidence_id = evidence_item["id"]
        satisfies = evidence_item.get("satisfies")
        if not isinstance(satisfies, list) or not satisfies:
            raise RegistryError(f"{evidence_id}: satisfies must be non-empty")
        for requirement_id in satisfies:
            if requirement_id not in requirement_by_id:
                raise RegistryError(
                    f"{evidence_id}: unknown requirement {requirement_id}"
                )
        level = evidence_item.get("test_level")
        if level not in TEST_LEVEL_RANK:
            raise RegistryError(f"{evidence_id}: invalid test_level {level!r}")
        methods = evidence_item.get("methods")
        if (
            not isinstance(methods, list)
            or not methods
            or any(method not in canonical_methods for method in methods)
        ):
            raise RegistryError(f"{evidence_id}: invalid methods")
        oracle = evidence_item.get("oracle_class")
        if oracle not in ORACLE_RANK:
            raise RegistryError(f"{evidence_id}: invalid oracle_class")
        if evidence_item.get("execution_nature") not in VALID_EVIDENCE_EXECUTION_NATURES:
            raise RegistryError(f"{evidence_id}: invalid execution_nature")
        if evidence_item.get("source_type") not in VALID_SOURCE_TYPES:
            raise RegistryError(f"{evidence_id}: invalid source_type")
        if evidence_item.get("status") not in VALID_EVIDENCE_STATUSES:
            raise RegistryError(f"{evidence_id}: invalid evidence status")
        if "verified_at_revision" not in evidence_item:
            raise RegistryError(
                f"{evidence_id}: verified_at_revision field is required"
            )
        limitations = evidence_item.get("limitations")
        if not isinstance(limitations, list) or not all(
            isinstance(item, str) and item for item in limitations
        ):
            raise RegistryError(f"{evidence_id}: limitations must be a string list")
        providers = evidence_item.get("providers")
        if not isinstance(providers, list) or not providers:
            raise RegistryError(f"{evidence_id}: providers must be non-empty")
        refs = evidence_item.get("source_refs")
        if not isinstance(refs, list) or not refs:
            raise RegistryError(f"{evidence_id}: source_refs must be non-empty")
        for ref in refs:
            if not isinstance(ref, dict):
                raise RegistryError(
                    f"{evidence_id}: source_ref must be a mapping"
                )
            path = ref.get("path")
            if not isinstance(path, str) or not path:
                raise RegistryError(f"{evidence_id}: source_ref path is required")
            if not (root / path).is_file():
                raise RegistryError(
                    f"{evidence_id}: missing evidence reference {path}"
                )

        _validate_provider_run_binding(evidence_item, root)



def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _git_blob_sha(value: bytes) -> str:
    header = f"blob {len(value)}\0".encode("ascii")
    return hashlib.sha1(header + value).hexdigest()


def _validate_execution_bindings(
    run_record: dict[str, Any],
    *,
    root: Path,
    evidence_id: str,
) -> None:
    bindings = run_record.get("execution_bindings")
    if not isinstance(bindings, dict):
        raise RegistryError(
            f"{evidence_id}: provider run record requires execution_bindings"
        )
    files = _mapping_list(bindings.get("files"), f"{evidence_id} execution bindings")
    if not files:
        raise RegistryError(f"{evidence_id}: execution_bindings.files must be non-empty")
    seen: set[str] = set()
    for item in files:
        path = item.get("path")
        expected = item.get("git_blob_sha")
        if not isinstance(path, str) or not path:
            raise RegistryError(f"{evidence_id}: execution binding path is required")
        if path in seen:
            raise RegistryError(f"{evidence_id}: duplicate execution binding {path}")
        seen.add(path)
        if not isinstance(expected, str) or not re.fullmatch(r"[0-9a-f]{40}", expected):
            raise RegistryError(
                f"{evidence_id}: invalid git_blob_sha for execution binding {path}"
            )
        target = root / path
        if not target.is_file():
            raise RegistryError(
                f"{evidence_id}: missing execution-bound file {path}"
            )
        actual = _git_blob_sha(target.read_bytes())
        if actual != expected:
            raise RegistryError(
                f"{evidence_id}: execution binding is stale for {path}"
            )


def _validate_provider_case_runs(
    case: dict[str, Any],
    *,
    evidence_id: str,
    case_id: str,
    expected_runs: int,
    sequence: str | None,
) -> list[dict[str, Any]]:
    explicit_runs = case.get("runs")
    if explicit_runs is None:
        runs = [{
            key: case.get(key)
            for key in (
                "run_id",
                "run_status",
                "correctness",
                "resolved_model",
                "input_tokens",
                "output_tokens",
                "record_sha256",
            )
        }]
        explicit = False
    else:
        runs = _mapping_list(
            explicit_runs,
            f"{evidence_id} provider case {case_id} runs",
        )
        explicit = True

    if len(runs) != expected_runs:
        raise RegistryError(
            f"{evidence_id}: provider case {case_id} expected "
            f"{expected_runs} run(s), recorded {len(runs)}"
        )

    seen: set[str] = set()
    for index, run in enumerate(runs, start=1):
        run_id = run.get("run_id")
        if not isinstance(run_id, str) or not run_id:
            raise RegistryError(
                f"{evidence_id}: provider case {case_id} run {index} "
                "requires run_id"
            )
        if run_id in seen:
            raise RegistryError(
                f"{evidence_id}: provider case {case_id} duplicate run_id {run_id}"
            )
        seen.add(run_id)
        if run.get("run_status") != "COMPLETED" or run.get("correctness") != "PASS":
            raise RegistryError(
                f"{evidence_id}: provider case {case_id} run {run_id} "
                "is not an accepted PASS"
            )
        record_sha = run.get("record_sha256")
        if not isinstance(record_sha, str) or not re.fullmatch(
            r"[0-9a-f]{64}", record_sha
        ):
            raise RegistryError(
                f"{evidence_id}: provider case {case_id} run {run_id} "
                "has invalid record_sha256"
            )
        model = run.get("resolved_model")
        if not isinstance(model, str) or not model:
            raise RegistryError(
                f"{evidence_id}: provider case {case_id} run {run_id} "
                "requires resolved_model"
            )
        for field in ("input_tokens", "output_tokens"):
            value = run.get(field)
            if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                raise RegistryError(
                    f"{evidence_id}: provider case {case_id} run {run_id} "
                    f"has invalid {field}"
                )
        if explicit:
            if run.get("started_from_clean_context") is not True:
                raise RegistryError(
                    f"{evidence_id}: provider case {case_id} run {run_id} "
                    "must record clean-context execution"
                )
            prompt_bytes = run.get("provider_prompt_utf8_bytes")
            if (
                not isinstance(prompt_bytes, int)
                or isinstance(prompt_bytes, bool)
                or prompt_bytes <= 0
            ):
                raise RegistryError(
                    f"{evidence_id}: provider case {case_id} run {run_id} "
                    "has invalid provider_prompt_utf8_bytes"
                )

    if sequence is None:
        return runs
    if sequence != "bootstrap-idempotence":
        raise RegistryError(
            f"{evidence_id}: provider case {case_id} has unsupported "
            f"run sequence {sequence!r}"
        )
    if len(runs) != 2:
        raise RegistryError(
            f"{evidence_id}: bootstrap-idempotence case {case_id} "
            "must record exactly two runs"
        )
    first_context = runs[0].get("execution_context")
    second_context = runs[1].get("execution_context")
    if first_context != {
        "sequence": "bootstrap-idempotence",
        "step": 1,
        "phase": "bootstrap",
    }:
        raise RegistryError(
            f"{evidence_id}: bootstrap-idempotence case {case_id} "
            "has invalid first execution_context"
        )
    if second_context != {
        "sequence": "bootstrap-idempotence",
        "step": 2,
        "phase": "reconcile-existing",
    }:
        raise RegistryError(
            f"{evidence_id}: bootstrap-idempotence case {case_id} "
            "has invalid second execution_context"
        )
    derived = runs[1].get("derived_input_binding")
    if not isinstance(derived, dict):
        raise RegistryError(
            f"{evidence_id}: bootstrap-idempotence case {case_id} "
            "requires derived_input_binding on run 2"
        )
    if derived.get("prior_run_record_sha256") != runs[0]["record_sha256"]:
        raise RegistryError(
            f"{evidence_id}: bootstrap-idempotence case {case_id} "
            "does not bind run 2 to run 1"
        )
    core_sha = derived.get("core_model_sha256")
    if not isinstance(core_sha, str) or not re.fullmatch(r"[0-9a-f]{64}", core_sha):
        raise RegistryError(
            f"{evidence_id}: bootstrap-idempotence case {case_id} "
            "has invalid derived Core-model binding"
        )
    return runs


def _validate_provider_run_binding(
    evidence_item: dict[str, Any],
    root: Path,
) -> None:
    if (
        evidence_item.get("status") not in ACTIVE_EVIDENCE_STATUSES
        or evidence_item.get("execution_nature") != "judgement-dependent"
    ):
        return

    evidence_id = evidence_item["id"]
    run_ref = evidence_item.get("provider_run_ref")
    if not isinstance(run_ref, str) or not run_ref:
        raise RegistryError(
            f"{evidence_id}: active judgement evidence requires provider_run_ref"
        )
    run_path = root / run_ref
    if not run_path.is_file():
        raise RegistryError(f"{evidence_id}: missing provider run record {run_ref}")
    run_record = load_yaml(run_path)
    if run_record.get("version") != 1:
        raise RegistryError(f"{evidence_id}: provider run record version must be 1")
    if run_record.get("kind") != "harness-provider-behavioral-evidence":
        raise RegistryError(f"{evidence_id}: invalid provider run record kind")
    if run_record.get("status") != "accepted":
        raise RegistryError(f"{evidence_id}: provider run record is not accepted")
    _validate_execution_bindings(
        run_record,
        root=root,
        evidence_id=evidence_id,
    )
    revision = run_record.get("harness_revision")
    if not isinstance(revision, str) or not re.fullmatch(r"[0-9a-f]{40}", revision):
        raise RegistryError(f"{evidence_id}: invalid provider run revision")

    cases = _mapping_list(run_record.get("cases"), f"{evidence_id} provider cases")
    cases_by_id: dict[str, dict[str, Any]] = {}
    for case in cases:
        case_id = case.get("case_id")
        if not isinstance(case_id, str) or not case_id:
            raise RegistryError(
                f"{evidence_id}: provider case record has no stable case_id"
            )
        if case_id in cases_by_id:
            raise RegistryError(
                f"{evidence_id}: duplicate provider case_id {case_id}"
            )
        cases_by_id[case_id] = case
    selected = evidence_item.get("case_ids")
    if not isinstance(selected, list) or not selected or not all(
        isinstance(item, str) and item for item in selected
    ):
        raise RegistryError(f"{evidence_id}: active judgement evidence requires case_ids")

    for case_id in selected:
        case = cases_by_id.get(case_id)
        if case is None:
            raise RegistryError(
                f"{evidence_id}: provider run record missing case {case_id}"
            )
        for field, digest_field in (
            ("fixture", "fixture_sha256"),
            ("oracle", "oracle_sha256"),
        ):
            relative = case.get(field)
            expected = case.get(digest_field)
            if not isinstance(relative, str) or not relative:
                raise RegistryError(f"{evidence_id}: {case_id} missing {field} path")
            path = root / relative
            if not path.is_file():
                raise RegistryError(
                    f"{evidence_id}: {case_id} missing bound {field} {relative}"
                )
            actual = _sha256_bytes(path.read_bytes())
            if actual != expected:
                raise RegistryError(
                    f"{evidence_id}: {case_id} {field} binding is stale"
                )

        template_relative = case.get("template")
        expected_case = case.get("case_sha256")
        if not isinstance(template_relative, str) or not template_relative:
            raise RegistryError(f"{evidence_id}: {case_id} missing template path")
        template_path = root / template_relative
        if not template_path.is_file():
            raise RegistryError(
                f"{evidence_id}: {case_id} missing bound template {template_relative}"
            )
        rendered = template_path.read_text(encoding="utf-8")
        if "__HARNESS_REVISION__" not in rendered:
            raise RegistryError(
                f"{evidence_id}: {case_id} template lacks revision binding"
            )
        rendered = rendered.replace("__HARNESS_REVISION__", revision)
        if _sha256_bytes(rendered.encode("utf-8")) != expected_case:
            raise RegistryError(
                f"{evidence_id}: {case_id} case binding is stale"
            )
        rendered_case = yaml.safe_load(rendered)
        if not isinstance(rendered_case, dict):
            raise RegistryError(
                f"{evidence_id}: {case_id} rendered case must be a mapping"
            )
        run_plan = rendered_case.get("run_plan")
        if not isinstance(run_plan, dict):
            raise RegistryError(
                f"{evidence_id}: {case_id} rendered case lacks run_plan"
            )
        expected_runs = run_plan.get("runs")
        if (
            not isinstance(expected_runs, int)
            or isinstance(expected_runs, bool)
            or expected_runs < 1
        ):
            raise RegistryError(
                f"{evidence_id}: {case_id} rendered case has invalid run count"
            )
        sequence = run_plan.get("sequence")
        if sequence is not None and not isinstance(sequence, str):
            raise RegistryError(
                f"{evidence_id}: {case_id} rendered case has invalid run sequence"
            )
        _validate_provider_case_runs(
            case,
            evidence_id=evidence_id,
            case_id=case_id,
            expected_runs=expected_runs,
            sequence=sequence,
        )


def _level_admissible(
    evidence_level: str,
    required_levels: list[str],
    higher_level_alone_allowed: bool,
) -> bool:
    if evidence_level in required_levels:
        return True
    if not higher_level_alone_allowed:
        return False
    minimum = min(TEST_LEVEL_RANK[level] for level in required_levels)
    return TEST_LEVEL_RANK[evidence_level] >= minimum


def admissibility_reason(
    evidence: dict[str, Any],
    requirement: dict[str, Any],
) -> str | None:
    if evidence["status"] not in ACTIVE_EVIDENCE_STATUSES:
        return f"status={evidence['status']} is not active"

    required = requirement["required"]
    if not _level_admissible(
        evidence["test_level"],
        required["test_levels"],
        requirement["substitution"]["higher_level_alone_allowed"],
    ):
        return (
            f"test_level={evidence['test_level']} cannot satisfy "
            f"{required['test_levels']}"
        )

    if not set(evidence["methods"]) & set(required["methods_any"]):
        return "no acceptable evidence method"

    if ORACLE_RANK[evidence["oracle_class"]] < ORACLE_RANK[required["oracle_minimum"]]:
        return (
            f"oracle_class={evidence['oracle_class']} is weaker than "
            f"{required['oracle_minimum']}"
        )

    expected_execution = (
        "judgement-dependent"
        if required["judgement_execution"]
        else "deterministic"
    )
    if evidence["execution_nature"] != expected_execution:
        return (
            f"execution_nature={evidence['execution_nature']} does not satisfy "
            f"{expected_execution}"
        )
    return None


def assurance_report(registry: dict[str, Any]) -> dict[str, Any]:
    requirements = {item["id"]: item for item in registry["requirements"]}
    evidence = registry["evidence"]
    ability_report: dict[str, Any] = {}

    for ability in registry["abilities"]:
        satisfied: list[str] = []
        missing: list[str] = []
        insufficient: list[dict[str, str]] = []
        for requirement_id in ability["requirements"]:
            requirement = requirements[requirement_id]
            if not requirement["release_applicable"]:
                continue
            candidates = [
                item for item in evidence if requirement_id in item["satisfies"]
            ]
            admissible = False
            for candidate in candidates:
                reason = admissibility_reason(candidate, requirement)
                if reason is None:
                    admissible = True
                    break
                insufficient.append(
                    {
                        "requirement_id": requirement_id,
                        "evidence_id": candidate["id"],
                        "reason": reason,
                    }
                )
            if admissible:
                satisfied.append(requirement_id)
            else:
                missing.append(requirement_id)

        status = "SATISFIED" if not missing else "INCOMPLETE"
        ability_report[ability["id"]] = {
            "status": status,
            "satisfied_requirements": satisfied,
            "missing_requirements": missing,
            "insufficient_evidence": insufficient,
        }

    release_claim_ready = all(
        report["status"] == "SATISFIED"
        for ability_id, report in ability_report.items()
        if next(
            item for item in registry["abilities"] if item["id"] == ability_id
        )["release_critical"]
    )
    return {
        "abilities": ability_report,
        "summary": {"release_claim_ready": release_claim_ready},
    }


def _expect_invalid(registry: dict[str, Any], fragment: str) -> None:
    try:
        validate_structure(registry)
    except RegistryError as exc:
        if fragment not in str(exc):
            raise AssertionError((fragment, str(exc))) from exc
    else:
        raise AssertionError(f"expected RegistryError containing {fragment!r}")


def run_meta_self_tests(registry: dict[str, Any]) -> list[str]:
    passed: list[str] = []

    # Completeness is a mechanism oracle, not an assertion that today's live
    # provider evidence is current. A stale run must expose a gap, not fail CI.
    completeness_fixture = {
        "abilities": [{
            "id": "META-ABILITY", "release_critical": True,
            "requirements": ["META-R01", "META-R02"],
        }],
        "requirements": [{
            "id": requirement_id, "release_applicable": True,
            "required": {
                "test_levels": ["TL1"], "methods_any": ["EM-02"],
                "oracle_minimum": "O1", "judgement_execution": False,
            },
            "substitution": {"higher_level_alone_allowed": False},
        } for requirement_id in ("META-R01", "META-R02")],
        "evidence": [{
            "id": "META-EVIDENCE-1", "satisfies": ["META-R01"],
            "status": "implemented", "test_level": "TL1", "methods": ["EM-02"],
            "oracle_class": "O1", "execution_nature": "deterministic",
        }],
    }
    report = assurance_report(completeness_fixture)
    assert report["summary"]["release_claim_ready"] is False
    assert report["abilities"]["META-ABILITY"]["satisfied_requirements"] == ["META-R01"]
    assert report["abilities"]["META-ABILITY"]["missing_requirements"] == ["META-R02"]
    second = dict(completeness_fixture["evidence"][0])
    second.update(id="META-EVIDENCE-2", satisfies=["META-R02"])
    completeness_fixture["evidence"].append(second)
    assert assurance_report(completeness_fixture)["summary"]["release_claim_ready"] is True
    for status in ("stale", "retired"):
        second["status"] = status
        report = assurance_report(completeness_fixture)
        assert report["summary"]["release_claim_ready"] is False
        assert report["abilities"]["META-ABILITY"]["missing_requirements"] == ["META-R02"]
    passed.append("AR-M01")

    def candidate(
        evidence_id: str,
        *,
        level: str = "TL1",
        oracle: str = "O1",
        execution: str = "judgement-dependent",
        methods: list[str] | None = None,
        satisfies: list[str] | None = None,
        limitations: list[str] | None = None,
    ) -> dict[str, Any]:
        return {
            "id": evidence_id,
            "providers": ["validators/validate_assurance_registry.py"],
            "source_refs": [
                {"path": "validators/validate_assurance_registry.py"}
            ],
            "satisfies": satisfies or ["A05-R01"],
            "test_level": level,
            "methods": methods or ["EM-02"],
            "oracle_class": oracle,
            "execution_nature": execution,
            "source_type": "synthetic",
            "provider_run_ref": "spec/assurance/evidence/first-wave-provider-run-36928079710.yaml",
            "case_ids": ["TD-CAP-001"],
            "status": "implemented",
            "verified_at_revision": None,
            "limitations": limitations or ["meta-test fixture"],
        }

    requirements_by_id = {
        item["id"]: item for item in registry["requirements"]
    }
    cap_requirement = requirements_by_id["A05-R01"]

    wrong_level_candidate = candidate("META-WRONG-LEVEL", level="TL6")
    wrong_level_reason = admissibility_reason(
        wrong_level_candidate,
        cap_requirement,
    )
    assert wrong_level_reason is not None and "test_level=" in wrong_level_reason
    passed.append("AR-M02")

    weak_oracle_candidate = candidate("META-WEAK-ORACLE", oracle="O0")
    weak_oracle_reason = admissibility_reason(
        weak_oracle_candidate,
        cap_requirement,
    )
    assert weak_oracle_reason is not None and "oracle_class=" in weak_oracle_reason
    passed.append("AR-M03")

    wrong_execution_candidate = candidate(
        "META-WRONG-EXECUTION",
        execution="deterministic",
    )
    wrong_execution_reason = admissibility_reason(
        wrong_execution_candidate,
        cap_requirement,
    )
    assert (
        wrong_execution_reason is not None
        and "execution_nature=" in wrong_execution_reason
    )
    passed.append("AR-M04")

    missing_ref = copy.deepcopy(registry)
    bad = candidate("META-MISSING-REF")
    bad["source_refs"] = [{"path": "validators/does-not-exist.py"}]
    missing_ref["evidence"].append(bad)
    _expect_invalid(missing_ref, "missing evidence reference")
    passed.append("AR-M05")

    orphan = copy.deepcopy(registry)
    ability19 = next(item for item in orphan["abilities"] if item["id"] == "HA-A19")
    ability19["failure_modes"].append("A19-F05")
    _expect_invalid(orphan, "orphan release-critical failure modes")
    passed.append("AR-M06")

    unknown = copy.deepcopy(registry)
    bad = candidate("META-UNKNOWN-METHOD", methods=["EM-99"])
    unknown["evidence"].append(bad)
    _expect_invalid(unknown, "invalid methods")
    passed.append("AR-M07")

    limited = copy.deepcopy(registry)
    ability19 = next(item for item in limited["abilities"] if item["id"] == "HA-A19")
    ability19["requirements"].append("A19-R03")
    limited["requirements"].append(
        {
            "id": "A19-R03",
            "ability": "HA-A19",
            "failure_modes": ["A19-F06"],
            "purpose": "broader proof slot used only by the limitation meta-test",
            "required": {
                "test_levels": ["TL1"],
                "methods_any": ["EM-14"],
                "oracle_minimum": "O1",
                "judgement_execution": False,
            },
            "substitution": {"higher_level_alone_allowed": False},
            "release_applicable": True,
            "status": "required",
        }
    )
    limited["evidence"].append(
        candidate(
            "META-LIMITED-EVIDENCE",
            execution="deterministic",
            methods=["EM-14"],
            satisfies=["A19-R01"],
            limitations=["does not establish the broader A19-R03 obligation"],
        )
    )
    validate_structure(limited)
    limited_report = assurance_report(limited)
    assert "A19-R01" in limited_report["abilities"]["HA-A19"]["satisfied_requirements"]
    assert "A19-R03" in limited_report["abilities"]["HA-A19"]["missing_requirements"]
    passed.append("AR-M08")

    with tempfile.TemporaryDirectory() as tmpdir:
        binding_root = Path(tmpdir)
        bound_path = binding_root / "trusted-instruction.md"
        unrelated_path = binding_root / "unrelated.txt"
        original_bound = b"trusted instruction\n"
        bound_path.write_bytes(original_bound)
        unrelated_path.write_text("initial\n", encoding="utf-8")
        binding = {
            "execution_bindings": {
                "files": [
                    {
                        "path": "trusted-instruction.md",
                        "git_blob_sha": _git_blob_sha(original_bound),
                    }
                ]
            }
        }

        _validate_execution_bindings(
            binding,
            root=binding_root,
            evidence_id="META-CURRENT-PROVIDER-BINDING",
        )
        passed.append("AR-M09")

        bound_path.write_text("changed instruction\n", encoding="utf-8")
        try:
            _validate_execution_bindings(
                binding,
                root=binding_root,
                evidence_id="META-STALE-PROVIDER-BINDING",
            )
        except RegistryError as exc:
            assert "execution binding is stale" in str(exc)
        else:
            raise AssertionError("AR-M10 stale provider execution binding was accepted")
        passed.append("AR-M10")

        bound_path.write_bytes(original_bound)
        unrelated_path.write_text("changed but unrelated\n", encoding="utf-8")
        _validate_execution_bindings(
            binding,
            root=binding_root,
            evidence_id="META-UNRELATED-PROVIDER-MUTATION",
        )
        passed.append("AR-M11")

    sequence_case = {
        "runs": [
            {
                "run_id": "TD-BOOT-E04-R01-meta",
                "run_status": "COMPLETED",
                "correctness": "PASS",
                "resolved_model": "model-a",
                "input_tokens": 10,
                "output_tokens": 2,
                "provider_prompt_utf8_bytes": 100,
                "record_sha256": "1" * 64,
                "started_from_clean_context": True,
                "execution_context": {
                    "sequence": "bootstrap-idempotence",
                    "step": 1,
                    "phase": "bootstrap",
                },
            },
            {
                "run_id": "TD-BOOT-E04-R02-meta",
                "run_status": "COMPLETED",
                "correctness": "PASS",
                "resolved_model": "model-b",
                "input_tokens": 11,
                "output_tokens": 3,
                "provider_prompt_utf8_bytes": 101,
                "record_sha256": "2" * 64,
                "started_from_clean_context": True,
                "execution_context": {
                    "sequence": "bootstrap-idempotence",
                    "step": 2,
                    "phase": "reconcile-existing",
                },
                "derived_input_binding": {
                    "prior_run_record_sha256": "1" * 64,
                    "core_model_sha256": "3" * 64,
                },
            },
        ]
    }
    _validate_provider_case_runs(
        sequence_case,
        evidence_id="META-MULTI-RUN-BINDING",
        case_id="TD-BOOT-E04",
        expected_runs=2,
        sequence="bootstrap-idempotence",
    )
    broken_sequence = copy.deepcopy(sequence_case)
    broken_sequence["runs"][1]["derived_input_binding"][
        "prior_run_record_sha256"
    ] = "4" * 64
    try:
        _validate_provider_case_runs(
            broken_sequence,
            evidence_id="META-BROKEN-MULTI-RUN-BINDING",
            case_id="TD-BOOT-E04",
            expected_runs=2,
            sequence="bootstrap-idempotence",
        )
    except RegistryError as exc:
        assert "does not bind run 2 to run 1" in str(exc)
    else:
        raise AssertionError("AR-M12 broken multi-run sequence binding was accepted")
    passed.append("AR-M12")

    return passed


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--require-release-complete",
        action="store_true",
        help="Return non-zero when any release-critical proof slot is incomplete.",
    )
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    try:
        registry = load_yaml(REGISTRY_PATH)
        validate_structure(registry)
        meta_tests = run_meta_self_tests(registry)
        report = assurance_report(registry)
    except (OSError, yaml.YAMLError, RegistryError, AssertionError) as exc:
        print(f"Harness assurance registry validation failed: {exc}")
        return 1

    report["meta_self_tests"] = meta_tests
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print("Harness assurance registry validation passed")
        for ability_id, ability in report["abilities"].items():
            missing = ability["missing_requirements"]
            suffix = f" missing={','.join(missing)}" if missing else ""
            print(f"- {ability_id}: {ability['status']}{suffix}")
        print(f"- meta self-tests: {', '.join(meta_tests)}")
        print(
            "- release_claim_ready: "
            + str(report["summary"]["release_claim_ready"]).lower()
        )

    if args.require_release_complete and not report["summary"]["release_claim_ready"]:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
