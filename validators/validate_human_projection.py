#!/usr/bin/env python3
from __future__ import annotations

import copy
import sys
import tempfile
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from adapters.canonical_graph import project_model  # noqa: E402
from harness import CoreError  # noqa: E402
from human_projection import (  # noqa: E402
    compile_manifest,
    materialize_package,
    validate_manifest_sources,
    validate_projection_ir,
    validate_recipe,
)


def load(path: Path):
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise CoreError(f"{path} must contain a mapping")
    return value


def expect_error(fn, contains: str):
    try:
        fn()
    except CoreError as exc:
        if contains not in str(exc):
            raise AssertionError((contains, str(exc))) from exc
    else:
        raise AssertionError(f"expected CoreError containing {contains!r}")


def main() -> int:
    fixture = load(ROOT / "spec/unified-model-acceptance/napms-shape.yaml")
    recipe = load(ROOT / "spec/human-projection-acceptance/backend-review.yaml")
    ir_template = load(ROOT / "spec/human-projection-acceptance/backend-review-ir.yaml")

    model = project_model(fixture["source_graph"], fixture["projection"])
    manifest = compile_manifest(
        fixture["engineering_graph"],
        model,
        "BACKEND-IMPLEMENTATION",
        harness_version="research-fixture",
        project_revision="fixture-revision",
        recipe_id=recipe["id"],
    )

    assert manifest["consumer"] == "BACKEND-IMPLEMENTATION"
    assert manifest["target"]["status"] == "COMPLETE"
    assert "REQUIREMENTS" in manifest["direct_provider_artifacts"]
    assert "IMPLEMENTATION-DESIGN" in manifest["direct_provider_artifacts"]
    assert {item["artifact"] for item in manifest["sources"]} == {
        "REQUIREMENTS",
        "JOURNEY",
        "ARCHITECTURE",
        "ASYNC-NA",
        "INTERFACE",
        "IMPLEMENTATION-DESIGN",
    }
    assert manifest["unresolved"] == []

    plan = validate_recipe(recipe, manifest)
    overview = next(item for item in plan["documents"] if item["id"] == "overview")
    product = next(item for item in overview["sections"] if item["id"] == "product-boundary")
    assert product["sources"] == ["REQUIREMENTS"]

    ir = copy.deepcopy(ir_template)
    ir["manifest_digest"] = manifest["manifest_digest"]
    validate_projection_ir(ir, plan)

    with tempfile.TemporaryDirectory() as temp_dir:
        source_root = Path(temp_dir) / "source-project"
        for source in manifest["sources"]:
            path = source_root / source["path"]
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(source["artifact"] + "\n", encoding="utf-8")

        hashed_manifest = compile_manifest(
            fixture["engineering_graph"],
            model,
            "BACKEND-IMPLEMENTATION",
            harness_version="research-fixture",
            project_revision="fixture-revision",
            recipe_id=recipe["id"],
            source_root=source_root,
        )
        hashed_plan = validate_recipe(recipe, hashed_manifest)
        hashed_ir = copy.deepcopy(ir_template)
        hashed_ir["manifest_digest"] = hashed_manifest["manifest_digest"]
        validate_projection_ir(hashed_ir, hashed_plan)
        validate_manifest_sources(hashed_manifest, source_root)

        evidence_ir = copy.deepcopy(hashed_ir)
        for document in evidence_ir["documents"]:
            for section in document["sections"]:
                for claim in section["claims"]:
                    claim["evidence"] = [
                        {"source": source_id, "excerpt": source_id}
                        for source_id in claim["sources"]
                    ]
        validate_projection_ir(
            evidence_ir,
            hashed_plan,
            manifest=hashed_manifest,
            source_root=source_root,
            require_evidence=True,
        )

        missing_evidence_ir = copy.deepcopy(evidence_ir)
        del missing_evidence_ir["documents"][0]["sections"][0]["claims"][0]["evidence"]
        expect_error(
            lambda: validate_projection_ir(
                missing_evidence_ir,
                hashed_plan,
                manifest=hashed_manifest,
                source_root=source_root,
                require_evidence=True,
            ),
            "requires evidence",
        )

        bad_excerpt_ir = copy.deepcopy(evidence_ir)
        bad_excerpt_ir["documents"][0]["sections"][0]["claims"][0]["evidence"][0]["excerpt"] = "NOT-IN-SOURCE"
        expect_error(
            lambda: validate_projection_ir(
                bad_excerpt_ir,
                hashed_plan,
                manifest=hashed_manifest,
                source_root=source_root,
                require_evidence=True,
            ),
            "excerpt not found",
        )

        changed = source_root / hashed_manifest["sources"][0]["path"]
        changed.write_text("changed\n", encoding="utf-8")
        expect_error(
            lambda: validate_manifest_sources(hashed_manifest, source_root),
            "canonical source is stale",
        )
        changed.write_text(
            hashed_manifest["sources"][0]["artifact"] + "\n",
            encoding="utf-8",
        )

        review_root = Path(temp_dir) / "review"
        review_result = materialize_package(
            manifest,
            plan,
            ir,
            review_root,
            mode="REVIEW",
        )
        assert review_result["documents"] == ["implementation.md", "overview.md"]
        assert (review_root / "README.md").is_file()
        assert (review_root / "manifest.yaml").is_file()
        assert (review_root / "documents/overview.md").is_file()
        assert not (review_root / "sources").exists()

        handoff_root = Path(temp_dir) / "handoff"
        handoff_result = materialize_package(
            manifest,
            plan,
            ir,
            handoff_root,
            mode="HANDOFF",
            source_root=source_root,
        )
        assert len(handoff_result["sources"]) == len(manifest["sources"])
        assert (handoff_root / "sources/docs/requirements.yaml").is_file()

    bad_recipe = copy.deepcopy(recipe)
    bad_recipe["documents"][0]["sections"][0]["select"]["artifacts"] = ["UNKNOWN"]
    expect_error(
        lambda: validate_recipe(bad_recipe, manifest),
        "outside manifest",
    )

    bad_ir = copy.deepcopy(ir)
    bad_ir["documents"][0]["sections"][0]["claims"][0]["sources"] = ["INTERFACE"]
    expect_error(
        lambda: validate_projection_ir(bad_ir, plan),
        "outside section scope",
    )

    missing_ir = copy.deepcopy(ir)
    missing_ir["documents"][0]["sections"] = missing_ir["documents"][0]["sections"][:1]
    expect_error(
        lambda: validate_projection_ir(missing_ir, plan),
        "missing planned sections",
    )

    widened_graph = copy.deepcopy(fixture["engineering_graph"])
    interface = next(
        item for item in widened_graph["authorities"]
        if item["id"] == "INTERFACE"
    )
    interface["produces"].append(
        {
            "capability": "example.documentation-context",
            "requires": ["example.requirements"],
        }
    )
    widened_graph["terminal_capabilities"].append(
        {
            "capability": "example.documentation-context",
            "authority": "INTERFACE",
            "reason": "Research fixture: accepted context useful for overview documentation.",
        }
    )
    widened_model = copy.deepcopy(model)
    widened_model["artifacts"].append(
        {
            "id": "DOC-CONTEXT",
            "authority": "INTERFACE",
            "path": "docs/documentation-context.yaml",
            "provides": ["example.documentation-context"],
            "depends_on": ["REQUIREMENTS"],
        }
    )
    widened_manifest = compile_manifest(
        widened_graph,
        widened_model,
        "BACKEND-IMPLEMENTATION",
        extra_capabilities=["example.documentation-context"],
    )
    assert widened_manifest["scope"]["extra_capabilities"] == [
        "example.documentation-context"
    ]
    assert "DOC-CONTEXT" in {
        item["artifact"] for item in widened_manifest["sources"]
    }

    partial_model = copy.deepcopy(model)
    implementation = next(
        item for item in partial_model["artifacts"]
        if item["id"] == "IMPLEMENTATION-DESIGN"
    )
    implementation["provides"] = []
    partial_manifest = compile_manifest(
        fixture["engineering_graph"],
        partial_model,
        "BACKEND-IMPLEMENTATION",
    )
    assert partial_manifest["target"]["status"] == "READY"
    assert any(
        item["capability"] == "example.implementation-design"
        for item in partial_manifest["unresolved"]
    )

    print("Human projection compiler acceptance PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
