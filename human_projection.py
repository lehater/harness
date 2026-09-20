#!/usr/bin/env python3
"""Research prototype: compile source-bounded human-documentation projections.

This module is intentionally outside Core semantics. It consumes an accepted
Engineering Graph + Core realization and derives a deterministic documentation
scope for one Consumer.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import yaml

from engineering_graph import derive_profile, evaluate_engineering_target
from harness import CoreError, capability_resolve, validate_model


def _artifacts(model: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {item["id"]: item for item in model.get("artifacts", []) or []}


def _artifact_closure(
    roots: list[str],
    artifacts: dict[str, dict[str, Any]],
) -> list[str]:
    seen: set[str] = set()
    stack = list(reversed(roots))
    while stack:
        artifact_id = stack.pop()
        if artifact_id in seen:
            continue
        artifact = artifacts.get(artifact_id)
        if artifact is None:
            raise CoreError(f"projection root/dependency references unknown artifact: {artifact_id}")
        seen.add(artifact_id)
        for dep in reversed(artifact.get("depends_on", []) or []):
            if dep not in seen:
                stack.append(dep)
    return sorted(seen)


def _question_rows(model: dict[str, Any], selected_artifacts: set[str], selected_caps: set[str]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for question in model.get("questions", []) or []:
        blocked_artifacts = sorted(set(question.get("blocks", []) or []) & selected_artifacts)
        blocked_capabilities = sorted(
            set(question.get("blocks_capabilities", []) or []) & selected_caps
        )
        if not blocked_artifacts and not blocked_capabilities:
            continue
        rows.append(
            {
                "id": question["id"],
                "authority": question["authority"],
                "text": question["text"],
                "blocks": blocked_artifacts,
                "blocks_capabilities": blocked_capabilities,
            }
        )
    return sorted(rows, key=lambda item: item["id"])


def compile_manifest(
    engineering_graph: dict[str, Any],
    model: dict[str, Any],
    consumer_id: str,
    *,
    harness_version: str | None = None,
    project_revision: str | None = None,
    recipe_id: str | None = None,
) -> dict[str, Any]:
    validate_model(model)
    profile = derive_profile(engineering_graph, consumer_id)
    target = evaluate_engineering_target(engineering_graph, consumer_id, model)

    artifacts = _artifacts(model)
    selected_capabilities = [item["capability"] for item in profile["expectations"]]
    selected_cap_set = set(selected_capabilities)

    providers_by_capability: dict[str, list[str]] = {}
    direct_roots: list[str] = []
    unresolved: list[dict[str, Any]] = []

    target_by_capability: dict[str, tuple[str, dict[str, Any]]] = {}
    for bucket in ("complete", "create", "wait", "pending"):
        for item in target.get(bucket, []) or []:
            target_by_capability[item["capability"]] = (bucket.upper(), item)

    for capability in selected_capabilities:
        try:
            providers = capability_resolve(model, capability)
        except CoreError:
            providers = []
        providers_by_capability[capability] = sorted(providers)
        direct_roots.extend(providers)
        if not providers:
            state, detail = target_by_capability.get(
                capability, ("UNKNOWN", {"capability": capability})
            )
            unresolved.append(
                {
                    "capability": capability,
                    "state": state,
                    "authority": detail.get("authority"),
                    "blocked_by": sorted(detail.get("blocked_by", []) or []),
                }
            )

    direct_roots = list(dict.fromkeys(direct_roots))
    closure_ids = _artifact_closure(direct_roots, artifacts)
    closure_set = set(closure_ids)

    source_rows: list[dict[str, Any]] = []
    for artifact_id in closure_ids:
        artifact = artifacts[artifact_id]
        source_rows.append(
            {
                "artifact": artifact_id,
                "authority": artifact["authority"],
                "path": artifact["path"],
                "provides": sorted(artifact.get("provides", []) or []),
                "depends_on": sorted(artifact.get("depends_on", []) or []),
                "direct_provider": artifact_id in direct_roots,
            }
        )

    questions = _question_rows(model, closure_set, selected_cap_set)

    manifest: dict[str, Any] = {
        "version": 1,
        "kind": "harness-human-projection-manifest",
        "consumer": consumer_id,
        "recipe": recipe_id,
        "baseline": {
            "harness_version": harness_version,
            "project_revision": project_revision,
        },
        "target": {
            "status": target["status"],
            "create": sorted(item["capability"] for item in target.get("create", []) or []),
            "wait": sorted(item["capability"] for item in target.get("wait", []) or []),
            "pending": sorted(item["capability"] for item in target.get("pending", []) or []),
        },
        "capabilities": [
            {
                "capability": capability,
                "providers": providers_by_capability[capability],
            }
            for capability in selected_capabilities
        ],
        "direct_provider_artifacts": direct_roots,
        "sources": source_rows,
        "questions": questions,
        "unresolved": sorted(unresolved, key=lambda item: item["capability"]),
    }

    semantic = json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode("utf-8")
    manifest["manifest_digest"] = hashlib.sha256(semantic).hexdigest()
    return manifest


def validate_recipe(recipe: dict[str, Any], manifest: dict[str, Any]) -> dict[str, Any]:
    if recipe.get("version") != 1:
        raise CoreError("human projection recipe version must be 1")
    if recipe.get("kind") != "harness-human-projection":
        raise CoreError("unexpected human projection recipe kind")
    if recipe.get("consumer") != manifest["consumer"]:
        raise CoreError(
            f"recipe consumer {recipe.get('consumer')} does not match manifest consumer {manifest['consumer']}"
        )

    source_artifacts = {item["artifact"] for item in manifest["sources"]}
    source_capabilities = {
        item["capability"] for item in manifest["capabilities"]
    }
    source_authorities = {item["authority"] for item in manifest["sources"]}

    seen_docs: set[str] = set()
    seen_sections: set[tuple[str, str]] = set()
    normalized_docs: list[dict[str, Any]] = []

    documents = recipe.get("documents")
    if not isinstance(documents, list) or not documents:
        raise CoreError("human projection recipe requires documents")

    for document in documents:
        if not isinstance(document, dict):
            raise CoreError("projection document must be a mapping")
        doc_id = document.get("id")
        title = document.get("title")
        if not isinstance(doc_id, str) or not doc_id:
            raise CoreError("projection document id is required")
        if doc_id in seen_docs:
            raise CoreError(f"duplicate projection document id: {doc_id}")
        seen_docs.add(doc_id)
        if not isinstance(title, str) or not title.strip():
            raise CoreError(f"projection document {doc_id} title is required")

        sections = document.get("sections")
        if not isinstance(sections, list) or not sections:
            raise CoreError(f"projection document {doc_id} requires sections")
        normalized_sections: list[dict[str, Any]] = []

        for section in sections:
            section_id = section.get("id")
            if not isinstance(section_id, str) or not section_id:
                raise CoreError(f"projection document {doc_id} section id is required")
            key = (doc_id, section_id)
            if key in seen_sections:
                raise CoreError(f"duplicate projection section: {doc_id}/{section_id}")
            seen_sections.add(key)

            select = section.get("select", {}) or {}
            if not isinstance(select, dict):
                raise CoreError(f"projection section {doc_id}/{section_id} select must be mapping")
            unknown = set(select) - {"artifacts", "capabilities", "authorities"}
            if unknown:
                raise CoreError(
                    f"projection section {doc_id}/{section_id} unknown selectors: {sorted(unknown)}"
                )

            selected: set[str] = set()
            explicit_artifacts = select.get("artifacts", []) or []
            for artifact_id in explicit_artifacts:
                if artifact_id not in source_artifacts:
                    raise CoreError(
                        f"projection section {doc_id}/{section_id} selects artifact outside manifest: {artifact_id}"
                    )
                selected.add(artifact_id)

            caps = select.get("capabilities", []) or []
            for capability in caps:
                if capability not in source_capabilities:
                    raise CoreError(
                        f"projection section {doc_id}/{section_id} selects capability outside Consumer closure: {capability}"
                    )
                for row in manifest["capabilities"]:
                    if row["capability"] == capability:
                        selected.update(row["providers"])

            authorities = select.get("authorities", []) or []
            for authority in authorities:
                if authority not in source_authorities:
                    raise CoreError(
                        f"projection section {doc_id}/{section_id} selects Authority outside manifest: {authority}"
                    )
                selected.update(
                    item["artifact"]
                    for item in manifest["sources"]
                    if item["authority"] == authority
                )

            if not selected:
                raise CoreError(
                    f"projection section {doc_id}/{section_id} selects no canonical sources"
                )

            normalized_sections.append(
                {
                    "id": section_id,
                    "title": section.get("title") or section_id.replace("-", " ").title(),
                    "purpose": section.get("purpose", ""),
                    "renderer": section.get("renderer", "narrative"),
                    "sources": sorted(selected),
                }
            )

        normalized_docs.append(
            {
                "id": doc_id,
                "title": title,
                "sections": normalized_sections,
            }
        )

    return {
        "version": 1,
        "kind": "harness-human-projection-plan",
        "projection": recipe.get("id"),
        "consumer": manifest["consumer"],
        "manifest_digest": manifest["manifest_digest"],
        "documents": normalized_docs,
    }


def validate_projection_ir(
    projection_ir: dict[str, Any],
    plan: dict[str, Any],
) -> None:
    if projection_ir.get("version") != 1 or projection_ir.get("kind") != "harness-human-projection-ir":
        raise CoreError("unexpected human projection IR")
    if projection_ir.get("manifest_digest") != plan["manifest_digest"]:
        raise CoreError("projection IR manifest digest does not match current projection plan")

    allowed: dict[tuple[str, str], set[str]] = {}
    for document in plan["documents"]:
        for section in document["sections"]:
            allowed[(document["id"], section["id"])] = set(section["sources"])

    seen: set[tuple[str, str]] = set()
    for document in projection_ir.get("documents", []) or []:
        doc_id = document.get("id")
        for section in document.get("sections", []) or []:
            section_id = section.get("id")
            key = (doc_id, section_id)
            if key not in allowed:
                raise CoreError(f"projection IR contains unknown section: {doc_id}/{section_id}")
            seen.add(key)
            claims = section.get("claims")
            if not isinstance(claims, list) or not claims:
                raise CoreError(f"projection IR section {doc_id}/{section_id} requires claims")
            for claim in claims:
                text = claim.get("text")
                sources = claim.get("sources")
                if not isinstance(text, str) or not text.strip():
                    raise CoreError(f"projection claim in {doc_id}/{section_id} requires text")
                if not isinstance(sources, list) or not sources:
                    raise CoreError(
                        f"projection claim in {doc_id}/{section_id} requires source artifacts"
                    )
                outside = sorted(set(sources) - allowed[key])
                if outside:
                    raise CoreError(
                        f"projection claim in {doc_id}/{section_id} references sources outside section scope: {outside}"
                    )

    missing = sorted(set(allowed) - seen)
    if missing:
        raise CoreError(f"projection IR missing planned sections: {missing}")


def _load(path: str | Path) -> dict[str, Any]:
    value = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise CoreError(f"{path} must contain a mapping")
    return value


def main() -> int:
    parser = argparse.ArgumentParser(description="Research human documentation projection compiler")
    sub = parser.add_subparsers(dest="command", required=True)

    compile_cmd = sub.add_parser("compile")
    compile_cmd.add_argument("engineering_graph")
    compile_cmd.add_argument("core_model")
    compile_cmd.add_argument("consumer")
    compile_cmd.add_argument("--recipe")
    compile_cmd.add_argument("--harness-version")
    compile_cmd.add_argument("--project-revision")
    compile_cmd.add_argument("--output-manifest")
    compile_cmd.add_argument("--output-plan")

    ir_cmd = sub.add_parser("validate-ir")
    ir_cmd.add_argument("plan")
    ir_cmd.add_argument("projection_ir")

    args = parser.parse_args()

    if args.command == "compile":
        recipe = _load(args.recipe) if args.recipe else None
        manifest = compile_manifest(
            _load(args.engineering_graph),
            _load(args.core_model),
            args.consumer,
            harness_version=args.harness_version,
            project_revision=args.project_revision,
            recipe_id=recipe.get("id") if recipe else None,
        )
        plan = validate_recipe(recipe, manifest) if recipe else None
        if args.output_manifest:
            Path(args.output_manifest).write_text(
                yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8"
            )
        else:
            print(yaml.safe_dump(manifest, sort_keys=False), end="")
        if plan is not None and args.output_plan:
            Path(args.output_plan).write_text(
                yaml.safe_dump(plan, sort_keys=False), encoding="utf-8"
            )
        return 0

    validate_projection_ir(_load(args.projection_ir), _load(args.plan))
    print("Human projection IR valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
