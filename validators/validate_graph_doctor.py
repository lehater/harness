#!/usr/bin/env python3
"""Acceptance regression for canonical Graph Doctor v1 diagnostics."""
from __future__ import annotations

import copy
import sys
import tempfile
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from adapters.canonical_graph import project_model  # noqa: E402
from graph_doctor import diagnose_project  # noqa: E402


def load(path: Path):
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def codes(report):
    return {item["code"] for item in report["findings"]}


def assert_has(report, *expected):
    actual = codes(report)
    missing = set(expected) - actual
    assert not missing, (missing, actual, report)


def main() -> int:
    fixture = load(ROOT / "spec/unified-model-acceptance/napms-shape.yaml")
    graph = fixture["engineering_graph"]
    source = fixture["source_graph"]
    projection = fixture["projection"]
    model = project_model(source, projection)

    # Baseline should have no structural errors.
    with tempfile.TemporaryDirectory() as temp_dir:
        source_root = Path(temp_dir)
        for artifact in model["artifacts"]:
            path = source_root / artifact["path"]
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(artifact["id"] + "\n", encoding="utf-8")
        baseline = diagnose_project(
            graph,
            model=model,
            target="BACKEND-IMPLEMENTATION",
            source_root=source_root,
        )
        assert baseline["summary"]["ERROR"] == 0, baseline

    # Nutrition-like regression: dead public capability.
    dead_graph = copy.deepcopy(graph)
    architecture = next(
        item for item in dead_graph["authorities"]
        if item["id"] == "ARCHITECTURE"
    )
    architecture["produces"].append(
        {
            "capability": "example.dead-public-output",
            "requires": ["example.architecture"],
        }
    )
    dead_report = diagnose_project(dead_graph, model=model)
    assert_has(dead_report, "CAPABILITY_DEAD_PUBLIC")

    # Nutrition-like regression: stale path and duplicate canonical ownership.
    broken_model = copy.deepcopy(model)
    broken_model["artifacts"].append(
        {
            "id": "STALE-REDESIGN-ALIAS",
            "authority": "PRODUCT",
            "path": "docs/architecture.yaml",
            "provides": [],
            "depends_on": ["REQUIREMENTS"],
        }
    )
    target_artifact = next(
        item for item in broken_model["artifacts"]
        if item["id"] == "IMPLEMENTATION-DESIGN"
    )
    target_artifact["path"] = "docs/missing-implementation-design.yaml"

    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        for artifact in model["artifacts"]:
            path = root / artifact["path"]
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(artifact["id"] + "\n", encoding="utf-8")
        broken_report = diagnose_project(
            graph,
            model=broken_model,
            source_root=root,
        )
    assert_has(
        broken_report,
        "ARTIFACT_DUPLICATE_PATH",
        "ARTIFACT_FILE_MISSING",
    )

    # Stale Question blockers.
    stale_question = copy.deepcopy(model)
    stale_question["questions"].append(
        {
            "id": "Q-STALE",
            "authority": "INTERFACE",
            "text": "Stale blocker fixture.",
            "blocks": ["NO-SUCH-ARTIFACT"],
            "blocks_capabilities": ["example.no-such-capability"],
        }
    )
    stale_report = diagnose_project(
        graph,
        model=stale_question,
    )
    assert_has(
        stale_report,
        "QUESTION_BLOCKS_UNKNOWN_ARTIFACT",
        "QUESTION_BLOCKS_UNKNOWN_CAPABILITY",
    )

    # Generated projection accidentally registered as canonical.
    generated_model = copy.deepcopy(model)
    generated_model["artifacts"].append(
        {
            "id": "GENERATED-DOC",
            "authority": "PRODUCT",
            "path": "docs-generated/system-overview.md",
            "provides": [],
            "depends_on": ["REQUIREMENTS"],
        }
    )
    generated_report = diagnose_project(graph, model=generated_model)
    assert_has(generated_report, "CANONICAL_POINTS_TO_GENERATED")

    # NAPMS-like hidden dependency.
    hidden_source = copy.deepcopy(source)
    interface = next(
        item for item in hidden_source["nodes"]
        if item["id"] == "INTERFACE"
    )
    interface["depends_on"].append("JOURNEY")
    hidden_report = diagnose_project(
        graph,
        source_graph=hidden_source,
        projection=projection,
        target="BACKEND-IMPLEMENTATION",
    )
    assert_has(hidden_report, "ALIGNMENT_HIDDEN_DEPENDENCY")

    # NAPMS-like phantom dependency.
    phantom_source = copy.deepcopy(source)
    interface = next(
        item for item in phantom_source["nodes"]
        if item["id"] == "INTERFACE"
    )
    interface["depends_on"] = []
    phantom_report = diagnose_project(
        graph,
        source_graph=phantom_source,
        projection=projection,
        target="BACKEND-IMPLEMENTATION",
    )
    assert_has(phantom_report, "ALIGNMENT_PHANTOM_DEPENDENCY")

    # Provider ownership mismatch.
    owner_model = copy.deepcopy(model)
    interface_artifact = next(
        item for item in owner_model["artifacts"]
        if item["id"] == "INTERFACE"
    )
    interface_artifact["authority"] = "ARCHITECTURE"
    owner_report = diagnose_project(graph, model=owner_model)
    assert_has(owner_report, "PROVIDER_OWNER_MISMATCH")

    # Missing artifact dependency.
    dependency_model = copy.deepcopy(model)
    implementation = next(
        item for item in dependency_model["artifacts"]
        if item["id"] == "IMPLEMENTATION-DESIGN"
    )
    implementation["depends_on"].append("NO-SUCH-ARTIFACT")
    dependency_report = diagnose_project(graph, model=dependency_model)
    assert_has(dependency_report, "ARTIFACT_DEPENDENCY_MISSING")

    # Incomplete target is information, not a defect.
    incomplete_model = copy.deepcopy(model)
    implementation = next(
        item for item in incomplete_model["artifacts"]
        if item["id"] == "IMPLEMENTATION-DESIGN"
    )
    implementation["provides"] = []
    incomplete_report = diagnose_project(
        graph,
        model=incomplete_model,
        target="BACKEND-IMPLEMENTATION",
    )
    assert_has(incomplete_report, "TARGET_INCOMPLETE")
    target_row = next(
        item for item in incomplete_report["findings"]
        if item["code"] == "TARGET_INCOMPLETE"
    )
    assert target_row["severity"] == "INFO"

    print("Graph Doctor v1 acceptance PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
