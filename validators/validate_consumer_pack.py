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


def test_context_dependencies(temp_root: Path) -> None:
    """Check migrated ownership and mutate imports against the architecture validator."""
    import shutil
    from validators import validate_context_boundaries as boundaries

    spec = boundaries.load_map()
    owner = {
        module: context
        for context, contract in spec["contexts"].items()
        for module in contract["modules"]
    }
    aliases, _ = boundaries._compatibility(boundaries.load_layout(), owner)
    assert spec["contexts"]["coverage"]["may_depend_on"] == ["project-model", "assurance"]
    for module in (
        "architecture_driver_closure", "concern_activation", "coverage_obligations",
        "coverage_planner", "engineering_coverage",
    ):
        canonical = "harness.coverage." + module
        assert owner[canonical] == "coverage"
        assert boundaries._resolve_target(module, owner, aliases) == canonical
        assert boundaries._resolve_target(canonical, owner, aliases) == canonical

    checkout = temp_root / "boundary-checkout"
    checkout.mkdir()
    for path in ROOT.glob("*.py"):
        shutil.copy2(path, checkout / path.name)
    for directory in ("src", "harness", "adapters", "distribution"):
        shutil.copytree(ROOT / directory, checkout / directory)
    for relative in (
        "spec/architecture/harness-context-map-v0.yaml",
        "spec/architecture/repository-layout-v0.yaml",
        "docs/design/repository-layout-v0.md",
    ):
        target = checkout / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / relative, target)
    command = [sys.executable, "-c", (
        "import sys; from pathlib import Path; "
        "import validators.validate_context_boundaries as v; "
        "v.ROOT=Path(sys.argv[1]); "
        "v.MAP=v.ROOT/'spec/architecture/harness-context-map-v0.yaml'; "
        "v.LAYOUT=v.ROOT/'spec/architecture/repository-layout-v0.yaml'; "
        "raise SystemExit(v.main())"
    ), str(checkout)]
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    target = checkout / "src/harness/coverage/coverage_planner.py"
    original = target.read_text()
    for statement, diagnostic in (
        ("import semantic_acceptance", "without an explicit symbol boundary"),
        ("from semantic_acceptance import validate_semantic_evaluation", "non-published symbols"),
    ):
        target.write_text(original + "\n" + statement + "\n")
        result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
        assert result.returncode != 0, statement
        assert "harness.coverage.coverage_planner (coverage)" in result.stderr, result.stderr
        assert diagnostic in result.stderr, result.stderr
    target.write_text(original)

    assert spec["contexts"]["workspace"]["may_depend_on"] == ["project-model", "integration"]
    for module in ("frontend_interface_knowledge", "frontend_screen_contracts", "human_projection", "workspace"):
        canonical = "harness.workspace." + module
        assert owner[canonical] == "workspace"
        assert boundaries._resolve_target(module, owner, aliases) == canonical
    target = checkout / "src/harness/workspace/human_projection.py"
    original = target.read_text()
    for statement in (
        "import project_frontier", "import engineering_coverage", "import semantic_acceptance",
    ):
        target.write_text(original + "\n" + statement + "\n")
        result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
        assert result.returncode != 0, statement
        assert "harness.workspace.human_projection (workspace)" in result.stderr, result.stderr
    target.write_text(original)


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
# Frozen from the root Coverage modules before physical migration.
coverage_exports = {
    "architecture_driver_closure": [
        "annotations",
        "Any",
        "BASELINE_CONCERNS",
        "TERMINAL_STATES",
        "evaluate"
    ],
    "concern_activation": [
        "annotations",
        "argparse",
        "Path",
        "Any",
        "yaml",
        "load",
        "project_signals",
        "rule_matches",
        "derive_activation",
        "main"
    ],
    "coverage_obligations": [
        "annotations",
        "Any",
        "re",
        "capability_claim_index",
        "capability_realization",
        "concern_proofs",
        "declared_capability_claim_index",
        "semantic_evaluation_required_claims",
        "coverage_assurance_view",
        "TERMINAL_STATES",
        "derive_subject_inventory_disposition",
        "validate_subject_obligations",
        "derive_subject_obligation_rows"
    ],
    "coverage_planner": [
        "annotations",
        "argparse",
        "Path",
        "Any",
        "yaml",
        "coverage_assurance_view",
        "coverage_invalidation_closure",
        "load",
        "capability_realization",
        "realized_capabilities",
        "declared_capability_claim_index",
        "capability_claim_index",
        "concern_proofs",
        "semantic_evaluation_required_claims",
        "role_claims",
        "authorities_for_claim",
        "derive_plan",
        "main"
    ],
    "engineering_coverage": [
        "annotations",
        "argparse",
        "copy",
        "json",
        "Path",
        "Any",
        "yaml",
        "derive_activation",
        "derive_plan",
        "derive_subject_inventory_disposition",
        "derive_subject_obligation_rows",
        "validate_engineering_graph",
        "validate_realization",
        "question_frontier",
        "ROOT",
        "load",
        "load_scope_source",
        "evaluate_coverage",
        "evaluate_with_repository_policy",
        "main"
    ]
}
import ast
import sys
# Import canonical Coverage with fail-fast sentinels for every root facade.
# Transitive unmigrated consumers were already loaded by the earlier probes.
for module in coverage_exports:
    assert 'harness.coverage.' + module not in sys.modules, module
    sys.modules[module] = None
for module, expected in coverage_exports.items():
    canonical = importlib.import_module('harness.coverage.' + module)
    assert canonical.__all__ == expected, module
    assert Path(canonical.__file__).resolve() == Path('src/harness/coverage/' + module + '.py').resolve()
    assert hasattr(canonical, 'main') == (module in ('concern_activation', 'coverage_planner', 'engineering_coverage'))
    tree = ast.parse(Path(canonical.__file__).read_text())
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            assert node.module not in coverage_exports or node.level == 1, (module, node.module)
            assert node.module not in ('harness', 'engineering_graph'), (module, node.module)
            if node.module == 'semantic_acceptance':
                assert {alias.name for alias in node.names} <= {'coverage_assurance_view', 'coverage_invalidation_closure'}
        if isinstance(node, ast.Import):
            assert all(alias.name != 'semantic_acceptance' and alias.name not in coverage_exports for alias in node.names)
for module, expected in coverage_exports.items():
    del sys.modules[module]
    legacy = importlib.import_module(module)
    canonical = importlib.import_module('harness.coverage.' + module)
    assert legacy.__all__ is canonical.__all__, module
    for name in expected:
        assert getattr(legacy, name) is getattr(canonical, name), (module, name)
    assert hasattr(legacy, 'main') == hasattr(canonical, 'main'), module
from harness.coverage import engineering_coverage, coverage_obligations, coverage_planner, concern_activation
assert engineering_coverage.ROOT == Path.cwd()
assert engineering_coverage.question_frontier is core.question_frontier
assert engineering_coverage.validate_engineering_graph is canonical_graph.validate_engineering_graph
assert engineering_coverage.validate_realization is canonical_graph.validate_realization
assert engineering_coverage.derive_activation is concern_activation.derive_activation
assert engineering_coverage.derive_plan is coverage_planner.derive_plan
assert engineering_coverage.derive_subject_obligation_rows is coverage_obligations.derive_subject_obligation_rows
assert coverage_obligations.capability_realization is coverage_planner.capability_realization

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

# Workspace migration: surfaces and AST digests frozen from main 725f377.
import hashlib
workspace_exports = {
    'frontend_interface_knowledge': [
        'Any',
        'annotations',
        'evaluate_frontend_ux_closure',
        'evaluate_topology_screen_subject_coverage',
        'required_screen_ids',
    ],
    'frontend_screen_contracts': [
        'Any',
        'HTTP_METHODS',
        'Iterable',
        'annotations',
        'evaluate_frontend_screen_contracts',
        'evaluate_presentation_provider_contract',
        'operation_ids',
        'operation_query_parameters',
        'operation_response_codes',
        're',
        'semantic_evaluation',
    ],
    'human_projection': [
        'Any',
        'CoreError',
        'Path',
        'annotations',
        'argparse',
        'capability_resolve',
        'compile_manifest',
        'derive_profile',
        'evaluate_engineering_target',
        'hashlib',
        'json',
        'main',
        'materialize_package',
        'realize_projection_model',
        'render_projection_documents',
        'resolve_visual_assets',
        'shutil',
        'validate_manifest_sources',
        'validate_model',
        'validate_project_alignment',
        'validate_projection_ir',
        'validate_recipe',
        'yaml',
    ],
    'workspace': [
        'Any',
        'CoreError',
        'DEFAULT_OUTPUT',
        'ID_TO_FILE',
        'MANAGED_PREFIX',
        'Path',
        'SCHEMA_RENDERERS',
        'SCHEMA_VALIDATORS',
        'annotations',
        'argparse',
        'evaluate_target_state',
        'json',
        'load_model',
        'load_workspace',
        'main',
        're',
        'render_workspace',
        'validate_knowledge_document',
        'validate_profile',
        'yaml',
    ],
}
workspace_baseline_ast = {
    'frontend_interface_knowledge': '0112d7b8629f8fcbe225189feaacd2227bd1ba68cc0648d8dfb1c869d553e052',
    'frontend_screen_contracts': '8fc2bae00c6e35a0d7be25fb8b0e1dc95a226ed0d6557599819a36978204e1b7',
    'human_projection': '3684f2555d3b0cbf2042f0891dcdc0d983c6354e71fda7aa4464cf91c9a98c0b',
    'workspace': 'c2e28b8dc9215e9fb961294dd35a2d27504ba3750f09570e1e4bdff1084babea',
}
# Fail immediately if canonical Workspace tries to load any of its root facades.
for module in workspace_exports:
    assert 'harness.workspace.' + module not in sys.modules, module
    sys.modules[module] = None
for module in workspace_exports:
    importlib.import_module('harness.workspace.' + module)
for module in workspace_exports:
    del sys.modules[module]
for module, expected in workspace_exports.items():
    canonical = importlib.import_module('harness.workspace.' + module)
    legacy = importlib.import_module(module)
    assert canonical.__all__ == expected, module
    assert legacy.__all__ is canonical.__all__, module
    assert sorted(name for name in vars(canonical) if not name.startswith('_')) == expected, module
    for name in expected:
        assert getattr(legacy, name) is getattr(canonical, name), (module, name)
    assert Path(canonical.__file__).resolve() == Path('src/harness/workspace/' + module + '.py').resolve()
    assert hasattr(canonical, 'main') == (module in ('human_projection', 'workspace'))
    assert hasattr(legacy, 'main') == hasattr(canonical, 'main')
    tree = ast.parse(Path(canonical.__file__).read_text())
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            assert node.module not in workspace_exports, (module, node.module)
            assert node.module not in ('harness', 'engineering_graph', 'target_state'), (module, node.module)
            if node.module == 'integration_alignment':
                assert module == 'human_projection'
                assert [alias.name for alias in node.names] == ['validate_project_alignment']
        elif isinstance(node, ast.Import):
            assert all(alias.name not in workspace_exports and alias.name not in ('integration_alignment', 'engineering_graph', 'target_state') for alias in node.names)
    # Full-module structural equivalence independently of behavioral checks:
    # remove explicit exports and reverse only the approved Project Model imports.
    tree.body = [node for node in tree.body if not (isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id == '__all__' for target in node.targets))]
    for node in tree.body:
        if isinstance(node, ast.ImportFrom):
            node.module = {'harness.project_model.core': 'harness', 'harness.project_model.engineering_graph': 'engineering_graph', 'harness.project_model.target_state': 'target_state'}.get(node.module, node.module)
    assert hashlib.sha256(ast.dump(tree).encode()).hexdigest() == workspace_baseline_ast[module], module
from harness.workspace import human_projection, workspace
import integration_alignment
assert human_projection.CoreError is workspace.CoreError is core.CoreError
assert human_projection.capability_resolve is core.capability_resolve
assert human_projection.validate_model is core.validate_model
assert human_projection.derive_profile is canonical_graph.derive_profile
assert human_projection.evaluate_engineering_target is canonical_graph.evaluate_engineering_target
assert human_projection.validate_project_alignment is integration_alignment.validate_project_alignment
assert workspace.load_model is core.load_model
from harness.project_model import target_state as canonical_target
assert workspace.evaluate_target_state is canonical_target.evaluate_target_state
assert workspace.validate_profile is canonical_target.validate_profile
from scenario_suite import run_scenario
for name in ('workspace-managed',):
    result = run_scenario(Path('spec/scenario-suite/scenarios/' + name + '.yaml'))
    assert result.status == 'PASSED', result.as_dict()

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
    # Fresh isolated-pack processes exercise both preserved Workspace CLIs.
    fixture = "spec/workspace-acceptance/minimal-domain"
    for command in ("validate", "render"):
        result = subprocess.run(
            [sys.executable, "workspace.py", command, fixture],
            cwd=pack, env=env, capture_output=True, text=True,
        )
        assert result.returncode == 0, result.stderr
        assert json.loads(result.stdout)["target_state"]["status"] == "COMPLETE"
    projection = temp_root / "projection-fixture"
    projection.mkdir()
    fixture = load_yaml(pack / "spec/unified-model-acceptance/napms-shape.yaml")
    for name in ("engineering_graph", "source_graph", "projection"):
        (projection / (name + ".yaml")).write_text(yaml.safe_dump(fixture[name]))
    manifest = projection / "manifest.yaml"
    plan = projection / "plan.yaml"
    result = subprocess.run(
        [sys.executable, "human_projection.py", "compile", str(projection / "engineering_graph.yaml"),
         "BACKEND-IMPLEMENTATION", "--source-graph", str(projection / "source_graph.yaml"),
         "--projection", str(projection / "projection.yaml"),
         "--recipe", "spec/human-projection-acceptance/backend-review.yaml",
         "--output-manifest", str(manifest), "--output-plan", str(plan)],
        cwd=pack, env=env, capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr
    assert load_yaml(manifest)["target"]["status"] == "COMPLETE"
    assert load_yaml(plan)["documents"]

    # Representative Coverage CLIs reuse distributed fixtures and authored function oracles.
    overlay = temp_root / "coverage-overlay.yaml"
    overlay.write_text(yaml.safe_dump({"activate": [], "decisions": []}), encoding="utf-8")
    policy = "spec/engineering-coverage/"
    research = "spec/research/"
    coverage_commands = (
        ("concern_activation", [policy + "activation-policy-v1.yaml", research + "consumer-activation-fixture-roles.yaml", str(overlay), research + "consumer-activation-fixture-graph.yaml", "--consumer", "BACKEND"],
         "m.derive_activation(m.load(a[0]), m.load(a[1]), m.load(a[2]), [m.load(a[3])], 'BACKEND')"),
        ("coverage_planner", [policy + "semantic-proof-contract-v1.yaml", policy + "authority-role-contract-v1.yaml", research + "coverage-planner-fixture-authorities.yaml", research + "coverage-planner-fixture-claims.yaml", research + "coverage-derivation-fixture-overlay.yaml", research + "coverage-derivation-fixture-knowledge.yaml"],
         "m.derive_plan(*[m.load(x) for x in a[:5]], [m.load(a[5])])"),
        ("engineering_coverage", [research + "scope-activation-fixture-graph.yaml", research + "scope-activation-fixture-core.yaml", "IMPLEMENTATION"],
         "m.evaluate_with_repository_policy(graph=m.load(a[0]), realization=m.load(a[1]), consumer=a[2], scope='default')"),
    )
    for module, arguments, expression in coverage_commands:
        oracle = subprocess.run(
            [sys.executable, "-c", "import importlib, json, sys; m=importlib.import_module('harness.coverage.'+sys.argv[1]); a=sys.argv[2:]; print(json.dumps(" + expression + "))", module, *arguments],
            cwd=pack, env=env, check=True, capture_output=True, text=True,
        )
        result = subprocess.run(
            [sys.executable, module + ".py", *arguments], cwd=pack, env=env,
            check=True, capture_output=True, text=True,
        )
        assert yaml.safe_load(result.stdout) == json.loads(oracle.stdout), module

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
        test_context_dependencies(temp_root)

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
