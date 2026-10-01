#!/usr/bin/env python3
"""Validate the initial Harness Assurance Registry seed and its meta-invariants."""
from __future__ import annotations

import argparse
import copy
import json
import re
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

    report = assurance_report(registry)
    assert report["summary"]["release_claim_ready"] is False
    assert set(report["abilities"]["HA-A05"]["missing_requirements"]) == {
        "A05-R01", "A05-R02", "A05-R03"
    }
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
            "status": "implemented",
            "verified_at_revision": None,
            "limitations": limitations or ["meta-test fixture"],
        }

    wrong_level = copy.deepcopy(registry)
    wrong_level["evidence"].append(candidate("META-WRONG-LEVEL", level="TL6"))
    validate_structure(wrong_level)
    assert "A05-R01" in assurance_report(wrong_level)["abilities"]["HA-A05"]["missing_requirements"]
    passed.append("AR-M02")

    weak_oracle = copy.deepcopy(registry)
    weak_oracle["evidence"].append(candidate("META-WEAK-ORACLE", oracle="O0"))
    validate_structure(weak_oracle)
    assert "A05-R01" in assurance_report(weak_oracle)["abilities"]["HA-A05"]["missing_requirements"]
    passed.append("AR-M03")

    wrong_execution = copy.deepcopy(registry)
    wrong_execution["evidence"].append(
        candidate("META-WRONG-EXECUTION", execution="deterministic")
    )
    validate_structure(wrong_execution)
    assert "A05-R01" in assurance_report(wrong_execution)["abilities"]["HA-A05"]["missing_requirements"]
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
