#!/usr/bin/env python3
"""Validate and render an opt-in Harness-managed knowledge workspace."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

import yaml

from harness import CoreError, load_model
from target_state import evaluate_target_state, validate_profile

DEFAULT_OUTPUT = "docs/generated"
MANAGED_PREFIX = ".harness/knowledge/"
ID_TO_FILE = re.compile(r"[^a-z0-9]+")


def _load_yaml(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise CoreError(f"{path} must contain a mapping")
    return value


def _relative_path(value: str, field: str) -> Path:
    path = Path(value)
    if path.is_absolute() or ".." in path.parts:
        raise CoreError(f"{field} must be a repository-relative path")
    return path


def _validate_domain_model(document: dict[str, Any]) -> None:
    content = document.get("content")
    if not isinstance(content, dict):
        raise CoreError("domain-model/v1 content must be a mapping")

    purpose = content.get("purpose")
    if not isinstance(purpose, str) or not purpose.strip():
        raise CoreError("domain-model/v1 purpose is required")

    terms = content.get("terms", [])
    if not isinstance(terms, list):
        raise CoreError("domain-model/v1 terms must be a list")
    for item in terms:
        if (
            not isinstance(item, dict)
            or not isinstance(item.get("term"), str)
            or not item["term"].strip()
            or not isinstance(item.get("meaning"), str)
            or not item["meaning"].strip()
        ):
            raise CoreError("domain-model/v1 term requires term and meaning")

    concepts = content.get("concepts", [])
    if not isinstance(concepts, list):
        raise CoreError("domain-model/v1 concepts must be a list")
    for item in concepts:
        if not isinstance(item, dict) or not isinstance(item.get("name"), str) or not item["name"].strip():
            raise CoreError("domain-model/v1 concept name is required")
        identity = item.get("identity")
        if identity is not None and (not isinstance(identity, str) or not identity.strip()):
            raise CoreError("domain-model/v1 concept identity must be a non-empty string")
        responsibilities = item.get("responsibilities", [])
        if not isinstance(responsibilities, list) or any(
            not isinstance(value, str) or not value.strip() for value in responsibilities
        ):
            raise CoreError("domain-model/v1 concept responsibilities must be strings")

    invariants = content.get("invariants", [])
    if not isinstance(invariants, list):
        raise CoreError("domain-model/v1 invariants must be a list")
    seen: set[str] = set()
    for item in invariants:
        if (
            not isinstance(item, dict)
            or not isinstance(item.get("id"), str)
            or not item["id"].strip()
            or not isinstance(item.get("statement"), str)
            or not item["statement"].strip()
        ):
            raise CoreError("domain-model/v1 invariant requires id and statement")
        if item["id"] in seen:
            raise CoreError(f"duplicate domain invariant id: {item['id']}")
        seen.add(item["id"])


def _validate_product_requirements(document: dict[str, Any]) -> None:
    content = document.get("content")
    if not isinstance(content, dict):
        raise CoreError("product-requirements/v1 content must be a mapping")

    purpose = content.get("purpose")
    if not isinstance(purpose, str) or not purpose.strip():
        raise CoreError("product-requirements/v1 purpose is required")

    requirements = content.get("requirements")
    if not isinstance(requirements, list) or not requirements:
        raise CoreError("product-requirements/v1 requirements must be a non-empty list")

    seen: set[str] = set()
    for item in requirements:
        if not isinstance(item, dict):
            raise CoreError("product-requirements/v1 requirement must be a mapping")
        requirement_id = item.get("id")
        statement = item.get("statement")
        status = item.get("status")
        if not isinstance(requirement_id, str) or not requirement_id.strip():
            raise CoreError("product-requirements/v1 requirement id is required")
        if not requirement_id.startswith("REQ-"):
            raise CoreError(
                f"product-requirements/v1 requirement id must start with REQ-: {requirement_id}"
            )
        if requirement_id in seen:
            raise CoreError(f"duplicate product requirement id: {requirement_id}")
        seen.add(requirement_id)
        if not isinstance(statement, str) or not statement.strip():
            raise CoreError(
                f"product-requirements/v1 requirement {requirement_id} statement is required"
            )
        if status not in {"ACCEPTED", "RETIRED"}:
            raise CoreError(
                f"product-requirements/v1 requirement {requirement_id} status must be ACCEPTED or RETIRED"
            )
        source_refs = item.get("source_refs")
        if not isinstance(source_refs, list) or not source_refs or any(
            not isinstance(value, str) or not value.strip() for value in source_refs
        ):
            raise CoreError(
                f"product-requirements/v1 requirement {requirement_id} requires non-empty source_refs"
            )
        rationale = item.get("rationale")
        if rationale is not None and (
            not isinstance(rationale, str) or not rationale.strip()
        ):
            raise CoreError(
                f"product-requirements/v1 requirement {requirement_id} rationale must be non-empty when present"
            )

    non_goals = content.get("non_goals", [])
    if not isinstance(non_goals, list) or any(
        not isinstance(value, str) or not value.strip() for value in non_goals
    ):
        raise CoreError("product-requirements/v1 non_goals must be strings")


def _validate_test_design(document: dict[str, Any]) -> None:
    content = document.get("content")
    if not isinstance(content, dict):
        raise CoreError("test-design/v1 content must be a mapping")

    purpose = content.get("purpose")
    if not isinstance(purpose, str) or not purpose.strip():
        raise CoreError("test-design/v1 purpose is required")

    tests = content.get("tests")
    if not isinstance(tests, list) or not tests:
        raise CoreError("test-design/v1 tests must be a non-empty list")

    seen: set[str] = set()
    for item in tests:
        if not isinstance(item, dict):
            raise CoreError("test-design/v1 test must be a mapping")
        test_id = item.get("id")
        if not isinstance(test_id, str) or not test_id.strip():
            raise CoreError("test-design/v1 test id is required")
        if test_id in seen:
            raise CoreError(f"duplicate test design id: {test_id}")
        seen.add(test_id)

        verification_refs = item.get("verification_refs")
        if not isinstance(verification_refs, list) or not verification_refs or any(
            not isinstance(value, str) or not value.strip()
            for value in verification_refs
        ):
            raise CoreError(
                f"test-design/v1 test {test_id} requires non-empty verification_refs"
            )

        for field in ("precondition", "operation", "oracle"):
            value = item.get(field)
            if not isinstance(value, str) or not value.strip():
                raise CoreError(
                    f"test-design/v1 test {test_id} requires {field}"
                )


def _validate_verification_plan(document: dict[str, Any]) -> None:
    content = document.get("content")
    if not isinstance(content, dict):
        raise CoreError("verification-plan/v1 content must be a mapping")

    purpose = content.get("purpose")
    if not isinstance(purpose, str) or not purpose.strip():
        raise CoreError("verification-plan/v1 purpose is required")

    scope = content.get("scope")
    if not isinstance(scope, str) or not scope.strip():
        raise CoreError("verification-plan/v1 scope is required")

    checks = content.get("checks")
    if not isinstance(checks, list) or not checks:
        raise CoreError("verification-plan/v1 checks must be a non-empty list")
    seen: set[str] = set()
    for item in checks:
        if (
            not isinstance(item, dict)
            or not isinstance(item.get("id"), str)
            or not item["id"].strip()
            or not isinstance(item.get("objective"), str)
            or not item["objective"].strip()
        ):
            raise CoreError("verification-plan/v1 check requires id and objective")
        if item["id"] in seen:
            raise CoreError(f"duplicate verification check id: {item['id']}")
        seen.add(item["id"])
        verifies = item.get("verifies")
        if not isinstance(verifies, list) or not verifies or any(
            not isinstance(value, str) or not value.strip() for value in verifies
        ):
            raise CoreError(
                f"verification-plan/v1 check {item['id']} requires non-empty verifies refs"
            )
        method = item.get("method")
        if method not in {"TEST", "ANALYSIS", "INSPECTION", "DEMONSTRATION"}:
            raise CoreError(
                f"verification-plan/v1 check {item['id']} has unsupported method: {method}"
            )
        evidence = item.get("evidence")
        if not isinstance(evidence, list) or not evidence or any(
            not isinstance(value, str) or not value.strip() for value in evidence
        ):
            raise CoreError(
                f"verification-plan/v1 check {item['id']} requires non-empty evidence strings"
            )

    out_of_scope = content.get("out_of_scope", [])
    if not isinstance(out_of_scope, list) or any(
        not isinstance(value, str) or not value.strip() for value in out_of_scope
    ):
        raise CoreError("verification-plan/v1 out_of_scope must be strings")


SCHEMA_VALIDATORS = {
    "domain-model/v1": _validate_domain_model,
    "product-requirements/v1": _validate_product_requirements,
    "verification-plan/v1": _validate_verification_plan,
    "test-design/v1": _validate_test_design,
}


def validate_knowledge_document(document: dict[str, Any]) -> None:
    if document.get("version") != 1:
        raise CoreError("knowledge artifact version must be 1")
    if document.get("kind") != "harness-knowledge-artifact":
        raise CoreError("unexpected knowledge artifact kind")
    artifact = document.get("artifact")
    if not isinstance(artifact, str) or not artifact:
        raise CoreError("knowledge artifact id reference is required")
    title = document.get("title")
    if not isinstance(title, str) or not title.strip():
        raise CoreError(f"knowledge artifact {artifact} title is required")
    schema = document.get("schema")
    validator = SCHEMA_VALIDATORS.get(schema)
    if validator is None:
        raise CoreError(f"unsupported knowledge artifact schema: {schema}")
    validator(document)


def _render_domain_model(document: dict[str, Any]) -> str:
    content = document["content"]
    lines = [
        f"# {document['title']}",
        "",
        "> Generated from Harness canonical knowledge. Do not edit this file directly.",
        "",
        "## Purpose",
        "",
        content["purpose"].strip(),
    ]

    terms = content.get("terms", [])
    if terms:
        lines.extend(["", "## Ubiquitous language", ""])
        for item in terms:
            lines.append(f"- **{item['term']}** — {item['meaning']}")

    concepts = content.get("concepts", [])
    if concepts:
        lines.extend(["", "## Concepts", ""])
        for item in concepts:
            lines.append(f"### {item['name']}")
            identity = item.get("identity")
            if identity:
                lines.extend(["", f"Identity: {identity}"])
            responsibilities = item.get("responsibilities", [])
            if responsibilities:
                lines.extend(["", "Responsibilities:", ""])
                lines.extend(f"- {value}" for value in responsibilities)

    invariants = content.get("invariants", [])
    if invariants:
        lines.extend(["", "## Invariants", ""])
        for item in invariants:
            lines.append(f"- **{item['id']}** — {item['statement']}")

    return "\n".join(lines).rstrip() + "\n"


def _render_product_requirements(document: dict[str, Any]) -> str:
    content = document["content"]
    lines = [
        f"# {document['title']}",
        "",
        "> Generated from Harness canonical knowledge. Do not edit this file directly.",
        "",
        "## Purpose",
        "",
        content["purpose"].strip(),
        "",
        "## Requirements",
        "",
    ]

    for item in content["requirements"]:
        lines.extend(
            [
                f"### {item['id']}",
                "",
                item["statement"].strip(),
                "",
                f"Status: {item['status']}",
                "",
                "Sources:",
                "",
            ]
        )
        lines.extend(f"- {value}" for value in item["source_refs"])
        rationale = item.get("rationale")
        if rationale:
            lines.extend(["", "Rationale:", "", rationale.strip()])
        lines.append("")

    non_goals = content.get("non_goals", [])
    if non_goals:
        lines.extend(["## Non-goals", ""])
        lines.extend(f"- {value}" for value in non_goals)

    return "\n".join(lines).rstrip() + "\n"


def _render_test_design(document: dict[str, Any]) -> str:
    content = document["content"]
    lines = [
        f"# {document['title']}",
        "",
        "> Generated from Harness canonical knowledge. Do not edit this file directly.",
        "",
        "## Purpose",
        "",
        content["purpose"].strip(),
        "",
        "## Test contracts",
        "",
    ]
    for item in content["tests"]:
        lines.extend(
            [
                f"### {item['id']}",
                "",
                "Verification:",
                "",
            ]
        )
        lines.extend(f"- {value}" for value in item["verification_refs"])
        lines.extend(
            [
                "",
                f"**Precondition:** {item['precondition'].strip()}",
                "",
                f"**Operation:** {item['operation'].strip()}",
                "",
                f"**Oracle:** {item['oracle'].strip()}",
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def _render_verification_plan(document: dict[str, Any]) -> str:
    content = document["content"]
    lines = [
        f"# {document['title']}",
        "",
        "> Generated from Harness canonical knowledge. Do not edit this file directly.",
        "",
        "## Purpose",
        "",
        content["purpose"].strip(),
        "",
        "## Scope",
        "",
        content["scope"].strip(),
        "",
        "## Verification checks",
        "",
    ]

    for item in content["checks"]:
        lines.extend(
            [
                f"### {item['id']}",
                "",
                item["objective"].strip(),
                "",
                f"Method: {item['method']}",
                "",
                "Verifies:",
                "",
            ]
        )
        lines.extend(f"- {value}" for value in item["verifies"])
        lines.extend(["", "Evidence:", ""])
        lines.extend(f"- {value}" for value in item["evidence"])

    out_of_scope = content.get("out_of_scope", [])
    if out_of_scope:
        lines.extend(["", "## Out of scope", ""])
        lines.extend(f"- {value}" for value in out_of_scope)

    return "\n".join(lines).rstrip() + "\n"


SCHEMA_RENDERERS = {
    "domain-model/v1": _render_domain_model,
    "product-requirements/v1": _render_product_requirements,
    "verification-plan/v1": _render_verification_plan,
    "test-design/v1": _render_test_design,
}


def _validate_traceability(documents: dict[str, dict[str, Any]]) -> None:
    requirements: dict[str, dict[str, Any]] = {}
    verification_checks: dict[str, dict[str, Any]] = {}
    test_contracts: list[dict[str, Any]] = []

    for document in documents.values():
        schema = document["schema"]
        if schema == "product-requirements/v1":
            for item in document["content"]["requirements"]:
                if item["id"] in requirements:
                    raise CoreError(
                        f"duplicate requirement id across managed artifacts: {item['id']}"
                    )
                requirements[item["id"]] = item
        elif schema == "verification-plan/v1":
            for item in document["content"]["checks"]:
                if item["id"] in verification_checks:
                    raise CoreError(
                        f"duplicate verification check id across managed artifacts: {item['id']}"
                    )
                verification_checks[item["id"]] = item
        elif schema == "test-design/v1":
            test_contracts.extend(document["content"]["tests"])

    if requirements:
        covered_requirements = {
            ref
            for check in verification_checks.values()
            for ref in check["verifies"]
            if ref.startswith("REQ-")
        }
        unknown_requirement_refs = sorted(covered_requirements - set(requirements))
        if unknown_requirement_refs:
            raise CoreError(
                f"verification references unknown requirements: {unknown_requirement_refs}"
            )
        uncovered = sorted(
            requirement_id
            for requirement_id, requirement in requirements.items()
            if requirement["status"] == "ACCEPTED"
            and requirement_id not in covered_requirements
        )
        if uncovered:
            raise CoreError(
                f"accepted requirements without verification disposition: {uncovered}"
            )

    if verification_checks:
        known_test_refs = {
            ref
            for test in test_contracts
            for ref in test["verification_refs"]
        }
        unknown_verification_refs = sorted(
            known_test_refs - set(verification_checks)
        )
        if unknown_verification_refs:
            raise CoreError(
                f"test design references unknown verification checks: {unknown_verification_refs}"
            )
        missing_tests = sorted(
            check_id
            for check_id, check in verification_checks.items()
            if check["method"] == "TEST" and check_id not in known_test_refs
        )
        if missing_tests:
            raise CoreError(
                f"TEST verification checks without test-design contract: {missing_tests}"
            )


def load_workspace(root: str | Path) -> dict[str, Any]:
    root = Path(root)
    harness_dir = root / ".harness"
    graph_path = harness_dir / "graph.yaml"
    profile_path = harness_dir / "profile.yaml"
    if not graph_path.is_file():
        raise CoreError("managed workspace requires .harness/graph.yaml")
    if not profile_path.is_file():
        raise CoreError("managed workspace requires .harness/profile.yaml")

    model = load_model(graph_path)
    profile = _load_yaml(profile_path)
    validate_profile(profile, model)

    config_path = harness_dir / "config.yaml"
    config: dict[str, Any] = {}
    if config_path.is_file():
        config = _load_yaml(config_path)
        if config.get("version", 1) != 1 or config.get("kind", "harness-workspace-config") != "harness-workspace-config":
            raise CoreError("unexpected workspace config")
    generated = config.get("generated", {})
    if not isinstance(generated, dict):
        raise CoreError("workspace generated config must be a mapping")
    output = generated.get("output", DEFAULT_OUTPUT)
    if not isinstance(output, str) or not output:
        raise CoreError("generated output path is required")
    output_path = _relative_path(output, "generated output")

    graph_artifacts = {item["id"]: item for item in model.get("artifacts", [])}
    managed_by_path = {
        item["path"]: item
        for item in graph_artifacts.values()
        if item["path"].startswith(MANAGED_PREFIX)
    }

    documents: dict[str, dict[str, Any]] = {}
    knowledge_root = harness_dir / "knowledge"
    if knowledge_root.is_dir():
        for path in sorted(knowledge_root.rglob("*.yaml")):
            relative = path.relative_to(root).as_posix()
            document = _load_yaml(path)
            validate_knowledge_document(document)
            artifact_id = document["artifact"]
            if artifact_id in documents:
                raise CoreError(f"duplicate knowledge document for artifact: {artifact_id}")
            artifact = graph_artifacts.get(artifact_id)
            if artifact is None:
                raise CoreError(f"knowledge document references unknown graph artifact: {artifact_id}")
            if artifact["path"] != relative:
                raise CoreError(
                    f"knowledge document path mismatch for {artifact_id}: "
                    f"{relative} != {artifact['path']}"
                )
            documents[artifact_id] = document

    for path, artifact in managed_by_path.items():
        if artifact["id"] not in documents:
            raise CoreError(f"managed graph artifact has no knowledge document: {path}")

    _validate_traceability(documents)

    target_state = evaluate_target_state(profile, model)
    return {
        "root": root,
        "model": model,
        "profile": profile,
        "output": output_path,
        "documents": documents,
        "target_state": target_state,
    }


def _output_filename(artifact_id: str) -> str:
    stem = ID_TO_FILE.sub("-", artifact_id.lower()).strip("-")
    return f"{stem}.md"


def render_workspace(root: str | Path) -> dict[str, Any]:
    workspace = load_workspace(root)
    output_root = workspace["root"] / workspace["output"]
    output_root.mkdir(parents=True, exist_ok=True)

    generated: list[str] = []
    for artifact_id, document in sorted(workspace["documents"].items()):
        renderer = SCHEMA_RENDERERS[document["schema"]]
        path = output_root / _output_filename(artifact_id)
        path.write_text(renderer(document), encoding="utf-8")
        generated.append(path.relative_to(workspace["root"]).as_posix())

    return {
        "target_state": workspace["target_state"],
        "generated": generated,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Harness managed knowledge workspace")
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("validate", "render"):
        command = sub.add_parser(name)
        command.add_argument("root", nargs="?", default=".")
    artifact_command = sub.add_parser("validate-artifact")
    artifact_command.add_argument("path")

    args = parser.parse_args()
    if args.command == "validate":
        workspace = load_workspace(args.root)
        print(json.dumps({"valid": True, "target_state": workspace["target_state"]}, indent=2, sort_keys=True))
    elif args.command == "render":
        print(json.dumps(render_workspace(args.root), indent=2, sort_keys=True))
    else:
        document = _load_yaml(Path(args.path))
        validate_knowledge_document(document)
        print(
            json.dumps(
                {
                    "valid": True,
                    "artifact": document["artifact"],
                    "schema": document["schema"],
                },
                indent=2,
                sort_keys=True,
            )
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
