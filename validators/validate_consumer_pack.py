#!/usr/bin/env python3
"""Acceptance checks for Harness Consumer Pack distribution and binding."""
from __future__ import annotations

import copy
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
import target_state
from harness.project_model import target_state as canonical
assert target_state.validate_profile is canonical.validate_profile
assert target_state.evaluate_target_state is canonical.evaluate_target_state
assert target_state.__all__ is canonical.__all__
assert Path(canonical.__file__).resolve() == Path("src/harness/project_model/target_state.py").resolve()
assert engineering_graph.CoreError is core.CoreError
assert target_state.CoreError is core.CoreError
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
