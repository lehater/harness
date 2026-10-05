#!/usr/bin/env python3
"""Canonical Consumer Pack v1 distribution acceptance."""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import venv
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from harness.application.consumer_pack import (  # noqa: E402
    PACK_MANIFEST,
    ConsumerPackError,
    load_yaml,
    materialize_pack,
    sync_binding,
    validate_binding,
    validate_definition,
    validate_pack,
)

REVISION = "a" * 40
REPRESENTATIVE_SCENARIOS = (
    "decision-autonomy.yaml",
    "canonical-alignment.yaml",
    "structural-provider-removal.yaml",
    "create-work-routing.yaml",
    "workspace-managed.yaml",
    "semantic-gap-question.yaml",
    "project-reconciliation.yaml",
)
REPRESENTATIVE_MODULES = (
    "harness.project_model.core",
    "harness.project_model.engineering_graph",
    "harness.integration.adapters.canonical_graph",
    "harness.workspace.workspace",
    "harness.workspace.structurizr_projection",
    "harness.workspace.dbml_projection",
    "harness.workspace.application_process_bpmn_projection",
    "harness.evidence.source_coverage",
    "harness.application.project_frontier",
    "harness.application.reconciliation",
    "harness.application.ui_design_convergence",
)


def expect_error(fn, contains: str) -> None:
    try:
        fn()
    except ConsumerPackError as exc:
        assert contains in str(exc), (contains, str(exc))
    else:
        raise AssertionError(f"expected ConsumerPackError containing {contains!r}")


def clean_env() -> dict[str, str]:
    env = dict(os.environ)
    env.pop("PYTHONPATH", None)
    env["PYTHONNOUSERSITE"] = "1"
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    return env


def isolated_python(root: Path) -> Path:
    interpreter = root / "interpreter"
    venv.EnvBuilder(with_pip=False).create(interpreter)
    python = (
        interpreter / "Scripts" / "python.exe"
        if os.name == "nt"
        else interpreter / "bin" / "python"
    )
    purelib = subprocess.check_output(
        [str(python), "-c", "import sysconfig; print(sysconfig.get_path('purelib'))"],
        cwd=root,
        env=clean_env(),
        text=True,
    ).strip()
    shutil.copytree(Path(yaml.__file__).parent, Path(purelib) / "yaml")
    return python


def run_pack_acceptance(pack: Path, python: Path) -> None:
    env = clean_env()

    for module in REPRESENTATIVE_MODULES:
        result = subprocess.run(
            [str(python), "-m", module, "--help"],
            cwd=pack,
            env=env,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, (module, result.stdout, result.stderr)

    scenario_probe = """
from pathlib import Path
from harness.application.scenario_suite import run_scenario

names = (
    "decision-autonomy.yaml",
    "canonical-alignment.yaml",
    "structural-provider-removal.yaml",
    "create-work-routing.yaml",
    "workspace-managed.yaml",
    "semantic-gap-question.yaml",
    "project-reconciliation.yaml",
)
root = Path("spec/scenario-suite/scenarios")
for name in names:
    result = run_scenario(root / name)
    assert result.status == "PASSED", (name, result.as_dict())
"""
    subprocess.run(
        [str(python), "-c", scenario_probe],
        cwd=pack,
        env=env,
        check=True,
    )

    cli = subprocess.run(
        [
            str(python),
            "-m",
            "harness.application.skill_router",
            "operation",
            "--surface",
            "consumer",
            "--operation",
            "project-engineering-status",
            "--root",
            str(pack),
        ],
        cwd=pack,
        env=env,
        capture_output=True,
        text=True,
        check=True,
    )
    assert json.loads(cli.stdout)["skill"] == (
        "skills/agent/project-engineering-status/SKILL.md"
    )

    reconcile_cli = subprocess.run(
        [
            str(python),
            "-m",
            "harness.application.skill_router",
            "operation",
            "--surface",
            "consumer",
            "--operation",
            "project-reconcile",
            "--root",
            str(pack),
        ],
        cwd=pack,
        env=env,
        capture_output=True,
        text=True,
        check=True,
    )
    assert json.loads(reconcile_cli.stdout)["skill"] == (
        "skills/agent/project-reconcile/SKILL.md"
    )

    validated = subprocess.run(
        [
            str(python),
            "-m",
            "harness.application.consumer_pack",
            "validate-pack",
            str(pack),
            "--revision",
            REVISION,
            "--consumer-api",
            "v1",
        ],
        cwd=pack,
        env=env,
        capture_output=True,
        text=True,
        check=True,
    )
    assert json.loads(validated.stdout) == {"status": "VALID", "consumer_api": "v1"}


def main() -> int:
    assert not list(ROOT.glob("*.py")), "root Python modules must remain empty"
    assert not (ROOT / "adapters").exists(), (
        "legacy top-level adapters tree must remain absent"
    )

    definition = load_yaml(ROOT / "spec/distribution/consumer-pack-v1.yaml")
    validate_definition(definition, ROOT)
    assert definition["consumer_api"] == "v1"
    assert definition["root_files"] == []
    assert "src/harness/application/scenario_suite.py" in definition["exact_files"]
    assert "src/harness/application/scenario_drivers.py" in definition["exact_files"]
    assert "src/harness/application/ui_design_convergence.py" in definition["exact_files"]

    valid = {
        "version": 1,
        "kind": "harness-consumer-binding",
        "consumer_api": "v1",
        "source": {
            "repository": "https://example.invalid/harness.git",
            "revision": REVISION,
        },
    }
    validate_binding(valid)
    for invalid_api in ("v0", "unknown", None):
        bad = dict(valid)
        bad["consumer_api"] = invalid_api
        expect_error(lambda bad=bad: validate_binding(bad), "expected v1")

    with tempfile.TemporaryDirectory(prefix="harness-pack-v1-") as tmp:
        root = Path(tmp)
        python = isolated_python(root)
        subprocess.run(
            [
                str(python),
                "-c",
                "import importlib.util; assert importlib.util.find_spec('harness') is None",
            ],
            cwd=root,
            env=clean_env(),
            check=True,
        )

        pack = root / "pack"
        manifest = materialize_pack(ROOT, pack, binding_revision=REVISION)
        assert manifest["consumer_api"] == "v1"
        validate_pack(pack, expected_revision=REVISION)
        assert not list(pack.glob("*.py"))
        assert (pack / "src/harness/application/skill_router.py").is_file()
        assert (pack / "src/harness/application/scenario_suite.py").is_file()
        assert (pack / "src/harness/application/ui_design_convergence.py").is_file()
        assert (pack / "catalogs/ui/decision-rules-v0.yaml").is_file()
        assert (
            pack / "src/harness/workspace/structurizr_projection.py"
        ).is_file()
        assert (
            pack / "src/harness/workspace/dbml_projection.py"
        ).is_file()
        assert (
            pack / "src/harness/workspace/application_process_bpmn_projection.py"
        ).is_file()
        assert (
            pack / "src/harness/workspace/projection_boundary.py"
        ).is_file()
        assert (
            pack / "skills/agent/architecture-c4-structurizr/SKILL.md"
        ).is_file()
        assert (
            pack / "skills/agent/data-model-dbml/SKILL.md"
        ).is_file()
        assert (
            pack / "skills/agent/application-process-bpmn/SKILL.md"
        ).is_file()
        assert (
            pack / "spec/projection/structurizr-c4-v1.yaml"
        ).is_file()
        assert (
            pack / "spec/projection/dbml-data-model-v1.yaml"
        ).is_file()
        assert (
            pack / "spec/projection/application-process-bpmn-v1.yaml"
        ).is_file()
        assert not (pack / "adapters").exists()

        run_pack_acceptance(pack, python)

        second = root / "pack-2"
        materialize_pack(ROOT, second, binding_revision=REVISION)
        assert (pack / PACK_MANIFEST).read_bytes() == (
            second / PACK_MANIFEST
        ).read_bytes()

        tracked = pack / "src/harness/application/skill_router.py"
        original = tracked.read_bytes()
        tracked.write_bytes(original + b"\n# tamper\n")
        expect_error(
            lambda: validate_pack(pack, expected_revision=REVISION),
            "hash mismatch",
        )
        tracked.write_bytes(original)
        validate_pack(pack, expected_revision=REVISION)

        for relative in (
            "unexpected.txt",
            "src/harness/application/__pycache__/unexpected.txt",
        ):
            extra = pack / relative
            extra.parent.mkdir(parents=True, exist_ok=True)
            extra.write_text("unexpected", encoding="utf-8")
            expect_error(
                lambda: validate_pack(pack, expected_revision=REVISION),
                "manifest/file set mismatch",
            )
            extra.unlink()

        binding = root / "binding.json"
        binding.write_text(json.dumps(valid), encoding="utf-8")
        synced = sync_binding(binding, root / "cache", dev_source=ROOT)
        validate_pack(synced, expected_revision=REVISION)
        assert synced == sync_binding(binding, root / "cache", dev_source=ROOT)

    print(
        "Harness canonical Consumer Pack v1: PASS "
        "(isolated interpreter + representative CLI/scenario acceptance)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
