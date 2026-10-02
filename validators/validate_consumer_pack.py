#!/usr/bin/env python3
"""Acceptance checks for Harness Consumer Pack distribution and binding."""
from __future__ import annotations

import copy
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from consumer_pack import (  # noqa: E402
    ConsumerPackError,
    PACK_MANIFEST,
    load_yaml,
    materialize_pack,
    sync_binding,
    validate_binding,
    validate_definition,
    validate_pack,
)


def _git_head() -> str:
    result = subprocess.run(
        ["git", "-C", str(ROOT), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def test_pack_execution(pack: Path, temp_root: Path) -> None:
    """Exercise the distributed files, without inheriting checkout import paths."""
    env = dict(os.environ)
    env.pop("PYTHONPATH", None)
    env["PYTHONNOUSERSITE"] = "1"
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    probe = """
from pathlib import Path
import harness
from harness import CoreError, validate_model
from harness.project_model import core
assert CoreError is core.CoreError
assert validate_model is core.validate_model
assert harness.__all__ is core.__all__
for name in core.__all__:
    assert getattr(harness, name) is getattr(core, name), name
assert Path(harness.__file__).resolve() == Path('harness/__init__.py').resolve()
assert Path(core.__file__).resolve() == Path('src/harness/project_model/core.py').resolve()
import engineering_graph
from harness.project_model import engineering_graph as canonical_graph
assert engineering_graph.__all__ is canonical_graph.__all__
for name in canonical_graph.__all__:
    assert getattr(engineering_graph, name) is getattr(canonical_graph, name), name
assert Path(canonical_graph.__file__).resolve() == Path('src/harness/project_model/engineering_graph.py').resolve()
import target_state
from harness.project_model import target_state as canonical
assert target_state.validate_profile is canonical.validate_profile
assert target_state.evaluate_target_state is canonical.evaluate_target_state
assert target_state.__all__ is canonical.__all__
assert Path(canonical.__file__).resolve() == Path("src/harness/project_model/target_state.py").resolve()
assert engineering_graph.CoreError is core.CoreError
assert target_state.CoreError is core.CoreError
import importlib
for module in ('project_status', 'reference_materializer', 'reference_model_evolution'):
    legacy = importlib.import_module(module)
    canonical = importlib.import_module('harness.reference_model.' + module)
    assert legacy.__all__ is canonical.__all__
    for name in canonical.__all__:
        assert getattr(legacy, name) is getattr(canonical, name), (module, name)
    assert Path(canonical.__file__).resolve() == Path('src/harness/reference_model/' + module + '.py').resolve()
import reference_model_evolution
import reference_materializer
assert not hasattr(reference_model_evolution, 'main')
assert reference_materializer.CoreError is core.CoreError
assert reference_materializer.validate_engineering_graph is canonical_graph.validate_engineering_graph
for module in ('source_boundary', 'source_coverage', 'source_set'):
    legacy = importlib.import_module(module)
    canonical = importlib.import_module('harness.evidence.' + module)
    assert legacy.__all__ is canonical.__all__
    for name in canonical.__all__:
        assert getattr(legacy, name) is getattr(canonical, name), (module, name)
    assert canonical.CoreError is core.CoreError
    assert Path(canonical.__file__).resolve() == Path('src/harness/evidence/' + module + '.py').resolve()
# Public names frozen from the four root modules before the Decision move.
decision_exports = {
    "decision_execution_assurance": [
        "annotations",
        "Any",
        "CoreError",
        "ASSURANCE",
        "effective_execution_assurance",
        "evaluate_execution_assurance"
    ],
    "decision_exploration": [
        "annotations",
        "json",
        "Any",
        "validate_explorer_request_binding",
        "CoreError",
        "EXPLORATION",
        "APPLICABILITY",
        "AUTHORITATIVE_SOURCES",
        "DECISION_SPACE_REVIEW_CHECKS",
        "evaluate_decision_exploration"
    ],
    "decision_explorer_contract": [
        "annotations",
        "hashlib",
        "json",
        "Any",
        "CoreError",
        "build_decision_explorer_request",
        "validate_explorer_request_binding"
    ],
    "decision_governance": [
        "annotations",
        "Any",
        "CoreError",
        "EXPLORATION",
        "AUTONOMY",
        "ALT_STATES",
        "DISPOSITIONS",
        "decision_contract_index",
        "effective_policy",
        "axis_policies",
        "evaluate_decision_governance"
    ]
}
for module, expected in decision_exports.items():
    legacy = importlib.import_module(module)
    canonical = importlib.import_module('harness.decision.' + module)
    assert canonical.__all__ == expected, module
    assert legacy.__all__ is canonical.__all__, module
    for name in expected:
        assert getattr(legacy, name) is getattr(canonical, name), (module, name)
    assert canonical.CoreError is core.CoreError, module
    assert Path(canonical.__file__).resolve() == Path('src/harness/decision/' + module + '.py').resolve()
    assert not hasattr(legacy, 'main'), module
    assert not hasattr(canonical, 'main'), module
from harness.decision import decision_exploration, decision_explorer_contract
assert decision_exploration.validate_explorer_request_binding is decision_explorer_contract.validate_explorer_request_binding
# Reuse authored Decision scenarios through the distributed Application/drivers.
from scenario_suite import run_scenario
for scenario in sorted(Path('spec/scenario-suite/scenarios').glob('decision-*.yaml')):
    result = run_scenario(scenario)
    assert result.status == 'PASSED', result.as_dict()
"""
    result = subprocess.run(
        [sys.executable, "-c", probe], cwd=pack, env=env,
        capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr
    fixture = load_yaml(pack / "spec/acceptance/core-v0-cross-authority-change.yaml")
    model_path = temp_root / "core-model.yaml"
    model_path.write_text(yaml.safe_dump(fixture["model"]), encoding="utf-8")
    result = subprocess.run(
        [sys.executable, "harness.py", "validate", str(model_path)],
        cwd=pack, env=env, check=True, capture_output=True, text=True,
    )
    assert json.loads(result.stdout) == {"valid": True}, result.stdout

    target_fixture = load_yaml(next((pack / "spec/target-state-acceptance").glob("*.yaml")))
    profile_path = temp_root / "target-profile.yaml"
    profile_path.write_text(yaml.safe_dump(target_fixture["profile"]), encoding="utf-8")
    model_path.write_text(yaml.safe_dump(target_fixture["complete_model"]), encoding="utf-8")
    result = subprocess.run(
        [sys.executable, "target_state.py", str(profile_path), str(model_path)],
        cwd=pack, env=env, check=True, capture_output=True, text=True,
    )
    assert json.loads(result.stdout) == target_fixture["expect"]["complete"], result.stdout

    graph_fixture = load_yaml(pack / "spec/engineering-graph-acceptance/basic.yaml")
    graph_path = temp_root / "engineering-graph.yaml"
    graph_path.write_text(yaml.safe_dump(graph_fixture["graph"]), encoding="utf-8")
    model_path.write_text(yaml.safe_dump(graph_fixture["cases"]["empty"]["model"]), encoding="utf-8")
    target = graph_fixture.get("target", "IMPLEMENTATION")
    outputs = {}
    for command, arguments in (
        ("validate", [str(graph_path)]),
        ("profile", [str(graph_path), target]),
        ("evaluate", [str(graph_path), target, str(model_path)]),
    ):
        result = subprocess.run(
            [sys.executable, "engineering_graph.py", command, *arguments],
            cwd=pack, env=env, check=True, capture_output=True, text=True,
        )
        outputs[command] = json.loads(result.stdout)
    assert outputs["validate"] == {"valid": True}
    assert sorted(item["capability"] for item in outputs["profile"]["expectations"]) == sorted(graph_fixture["expect_profile"]["capabilities"])
    assert outputs["evaluate"]["profile"] == outputs["profile"]
    expected = graph_fixture["cases"]["empty"]["expect"]
    assert outputs["evaluate"]["status"] == expected["status"]
    assert sorted(item["capability"] for item in outputs["evaluate"]["create"]) == expected["create"]

    catalog_path = temp_root / "authority-catalog.yaml"
    registry_path = temp_root / "authority-registry.yaml"
    catalog_path.write_text(yaml.safe_dump({"authorities": [{"id": "PRODUCT"}]}), encoding="utf-8")
    result = subprocess.run(
        [sys.executable, "project_status.py", "bootstrap", "--catalog", str(catalog_path),
         "--write", str(registry_path)],
        cwd=pack, env=env, check=True, capture_output=True, text=True,
    )
    assert load_yaml(registry_path)["assessments"] == [
        {"authority_id": "PRODUCT", "applicability": "UNASSESSED"}
    ]
    result = subprocess.run(
        [sys.executable, "project_status.py", "status", "--catalog", str(catalog_path),
         "--registry", str(registry_path)],
        cwd=pack, env=env, check=True, capture_output=True, text=True,
    )
    assert yaml.safe_load(result.stdout)["rows"] == [
        {"authority": "PRODUCT", "applicability": "UNASSESSED", "operational_status": None,
         "artifacts": [], "blocking": []}
    ]

    result = subprocess.run(
        [sys.executable, "reference_materializer.py", "validate",
         "spec/research/reference-engineering-model-v0.yaml"],
        cwd=pack, env=env, check=True, capture_output=True, text=True,
    )
    assert json.loads(result.stdout) == {"valid": True, "diagnostics": []}
    holdout = next(row for row in load_yaml(
        pack / "spec/research/reference-materializer-fixtures/holdouts-v0.yaml"
    )["scenarios"] if row["id"] == "holdout-ephemeral-cli")
    facts_path = temp_root / "project-facts.yaml"
    request_path = temp_root / "materialization-request.yaml"
    facts_path.write_text(yaml.safe_dump(holdout["project_facts"]), encoding="utf-8")
    request_path.write_text(yaml.safe_dump(holdout["request"]), encoding="utf-8")
    result = subprocess.run(
        [sys.executable, "reference_materializer.py", "materialize",
         "spec/research/reference-engineering-model-v0.yaml", str(facts_path), str(request_path)],
        cwd=pack, env=env, check=True, capture_output=True, text=True,
    )
    materialized = json.loads(result.stdout)
    assert materialized["status"] == holdout["expect"]["status"] == "STABLE"
    required = {row["template"] for row in materialized["template_status"] if row["status"] == "REQUIRED"}
    assert set(holdout["expect"]["required_templates"]) <= required
    assert not set(holdout["expect"]["forbidden_templates"]) & required

    source_path = temp_root / "raw-source.txt"
    source_path.write_text("A source statement.\n", encoding="utf-8")
    boundary_path = temp_root / "source-boundary.yaml"
    boundary_path.write_text(yaml.safe_dump({
        "version": 1, "kind": "harness-source-boundary", "id": "BOUNDARY",
        "source_baseline": "fixture@v1",
        "source_sha256": hashlib.sha256(source_path.read_bytes()).hexdigest(),
        "segments": [{"id": "S1", "start_line": 1, "end_line": 1}],
    }), encoding="utf-8")
    coverage_path = temp_root / "source-coverage.yaml"
    coverage_path.write_text(yaml.safe_dump({
        "version": 1, "kind": "harness-source-coverage", "id": "COVERAGE",
        "source_baseline": "fixture@v1", "coverage_status": "COMPLETE",
        "statements": [{"id": "S1", "source_ref": "raw-source.txt#1", "text": "A source statement."}],
        "dispositions": [{"statement_id": "S1", "classification": "ADMITTED",
                          "admitted_ref": "knowledge.yaml#S1", "sanitized_statement": "A source statement."}],
    }), encoding="utf-8")
    contract_path = temp_root / "source-set-contract.yaml"
    contract_path.write_text(yaml.safe_dump({
        "version": 1, "kind": "harness-source-set-contract", "id": "CONTRACT",
        "scope": "fixture", "requirements": [{"id": "requirements", "min_items": 1}],
    }), encoding="utf-8")
    inventory_path = temp_root / "source-set.yaml"
    inventory_path.write_text(yaml.safe_dump({
        "version": 1, "kind": "harness-source-set", "id": "INVENTORY", "contract_id": "CONTRACT",
        "channels": [{"id": "requirements", "state": "COMPLETE", "items": [{"source_ref": "raw-source.txt"}]}],
    }), encoding="utf-8")
    for script, arguments, expected in (
        ("source_boundary.py", [str(source_path), str(boundary_path)],
         {"status": "ACCEPTED", "covered_line_count": 1, "findings": []}),
        ("source_coverage.py", ["validate", str(coverage_path)],
         {"valid": True, "coverage_status": "COMPLETE", "statement_count": 1, "questions": []}),
        ("source_coverage.py", ["report", str(coverage_path)],
         {"valid": True, "coverage_status": "COMPLETE", "statement_count": 1, "questions": []}),
        ("source_set.py", [str(contract_path), str(inventory_path)],
         {"status": "ACCEPTED", "required_channel_count": 1, "reviewed_channel_count": 1, "findings": []}),
    ):
        result = subprocess.run(
            [sys.executable, script, *arguments], cwd=pack, env=env,
            check=True, capture_output=True, text=True,
        )
        actual = json.loads(result.stdout)
        assert all(actual[key] == value for key, value in expected.items()), (script, actual)

def main() -> int:
    definition = load_yaml(ROOT / "spec/distribution/consumer-pack-v0.yaml")
    validate_definition(definition, ROOT)

    revision = "a" * 40
    with tempfile.TemporaryDirectory(prefix="consumer-pack-validation-") as temp:
        temp_root = Path(temp)
        pack = temp_root / "pack"
        manifest = materialize_pack(
            ROOT,
            pack,
            binding_revision=revision,
            effective_revision="dev-source",
        )
        assert manifest["consumer_api"] == "v0"
        assert manifest["binding_revision"] == revision
        test_pack_execution(pack, temp_root)

        surface = load_yaml(pack / "skills/skill-surface-registry-v0.yaml")
        entries = surface["skills"]
        assert entries
        assert all(item["surface"] == "consumer" for item in entries)
        assert all(item["lifecycle"] == "active" for item in entries)
        assert all(item["route_status"] == "routed" for item in entries)
        ids = {item["id"] for item in entries}
        assert "capture-harness-observation" not in ids
        assert "change-harness" not in ids
        assert "change-transition-design" not in ids
        assert "product-requirements" in ids
        assert "reliability-analysis" in ids
        assert "project-bootstrap-reconcile" in ids

        assert not (pack / "skills/maintainer").exists()
        assert not (pack / "docs/audit").exists()
        assert not (pack / "docs/plans").exists()
        assert not (pack / "docs/legacy").exists()
        assert (pack / "method_router.py").is_file()
        assert (pack / PACK_MANIFEST).is_file()

        first_manifest = (pack / PACK_MANIFEST).read_text(encoding="utf-8")
        second = temp_root / "pack-2"
        materialize_pack(
            ROOT,
            second,
            binding_revision=revision,
            effective_revision="dev-source",
        )
        second_manifest = (second / PACK_MANIFEST).read_text(encoding="utf-8")
        assert first_manifest == second_manifest, "Consumer Pack must be deterministic"

        tampered = pack / "harness.py"
        original = tampered.read_text(encoding="utf-8")
        tampered.write_text(original + "\n# tampered\n", encoding="utf-8")
        try:
            validate_pack(pack, expected_revision=revision)
        except ConsumerPackError as exc:
            assert "hash mismatch" in str(exc)
        else:
            raise AssertionError("tampered Consumer Pack must be rejected")

        binding = {
            "version": 1,
            "kind": "harness-consumer-binding",
            "consumer_api": "v0",
            "source": {
                "repository": str(ROOT),
                "revision": revision,
            },
        }
        validate_binding(binding)

        invalid = copy.deepcopy(binding)
        invalid["source"]["revision"] = "main"
        try:
            validate_binding(invalid)
        except ConsumerPackError as exc:
            assert "40-hex" in str(exc)
        else:
            raise AssertionError("moving branch binding must be rejected")

        binding_path = temp_root / "binding.yaml"
        binding_path.write_text(
            yaml.safe_dump(binding, sort_keys=False),
            encoding="utf-8",
        )
        dev_cache = temp_root / "dev-cache"
        dev_pack = sync_binding(
            binding_path,
            dev_cache,
            dev_source=ROOT,
        )
        dev_manifest = validate_pack(
            dev_pack,
            expected_revision=revision,
        )
        assert dev_manifest["binding_revision"] == revision
        assert dev_manifest["effective_revision"]

        actual_revision = _git_head()
        pinned = copy.deepcopy(binding)
        pinned["source"]["revision"] = actual_revision
        pinned_path = temp_root / "pinned.yaml"
        pinned_path.write_text(
            yaml.safe_dump(pinned, sort_keys=False),
            encoding="utf-8",
        )
        pinned_cache = temp_root / "pinned-cache"
        pinned_pack = sync_binding(pinned_path, pinned_cache)
        pinned_manifest = validate_pack(
            pinned_pack,
            expected_revision=actual_revision,
        )
        assert pinned_manifest["effective_revision"] == actual_revision

        # A second sync is idempotent and reuses the validated immutable cache.
        assert sync_binding(pinned_path, pinned_cache) == pinned_pack

    print("Harness Consumer Pack validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
