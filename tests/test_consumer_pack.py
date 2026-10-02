#!/usr/bin/env python3
"""Canonical Consumer Pack v1 acceptance and repository-layout regression."""
from __future__ import annotations
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from harness.application.consumer_pack import (
    ConsumerPackError, load_yaml, materialize_pack, sync_binding,
    validate_binding, validate_definition, validate_pack,
)

REVISION = "a" * 40

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

def main() -> int:
    assert not list(ROOT.glob("*.py")), "root Python modules must remain empty"
    assert not (ROOT / "adapters").exists(), "legacy top-level adapters tree must remain absent"

    definition = load_yaml(ROOT / "spec/distribution/consumer-pack-v1.yaml")
    validate_definition(definition, ROOT)
    assert definition["consumer_api"] == "v1"
    assert definition["root_files"] == []
    assert "src/harness/application/scenario_suite.py" in definition["exact_files"]
    assert "src/harness/application/scenario_drivers.py" in definition["exact_files"]

    valid = {
        "version": 1,
        "kind": "harness-consumer-binding",
        "consumer_api": "v1",
        "source": {"repository": "https://example.invalid/harness.git", "revision": REVISION},
    }
    validate_binding(valid)
    bad = dict(valid); bad["consumer_api"] = "v0"
    expect_error(lambda: validate_binding(bad), "expected v1")

    with tempfile.TemporaryDirectory(prefix="harness-pack-v1-") as tmp:
        root = Path(tmp); pack = root / "pack"
        manifest = materialize_pack(ROOT, pack, binding_revision=REVISION)
        assert manifest["consumer_api"] == "v1"
        validate_pack(pack, expected_revision=REVISION)
        assert not list(pack.glob("*.py"))
        assert (pack / "src/harness/application/skill_router.py").is_file()
        assert (pack / "src/harness/application/scenario_suite.py").is_file()
        assert not (pack / "adapters").exists()

        probe = (
            "from harness.application.skill_router import route_operation; "
            "from harness.application.scenario_suite import run_scenario; "
            "from pathlib import Path; "
            "r=route_operation(surface='consumer', operation='project-engineering-status', root='.'); "
            "assert r['skill']; "
            "s=run_scenario(Path('spec/scenario-suite/scenarios/create-work-routing.yaml')); "
            "assert s.status == 'PASSED', s.as_dict()"
        )
        subprocess.run([sys.executable, "-c", probe], cwd=pack, env=clean_env(), check=True)

        cli = subprocess.run(
            [sys.executable, "-m", "harness.application.skill_router",
             "operation", "--surface", "consumer", "--operation", "project-engineering-status",
             "--root", str(pack)],
            cwd=pack, env=clean_env(), capture_output=True, text=True, check=True,
        )
        assert json.loads(cli.stdout)["skill"]

        tracked = pack / "src/harness/application/skill_router.py"
        original = tracked.read_bytes()
        tracked.write_bytes(original + b"\n# tamper\n")
        expect_error(lambda: validate_pack(pack, expected_revision=REVISION), "hash mismatch")
        tracked.write_bytes(original)
        validate_pack(pack, expected_revision=REVISION)

        extra = pack / "unexpected.txt"; extra.write_text("unexpected", encoding="utf-8")
        expect_error(lambda: validate_pack(pack, expected_revision=REVISION), "manifest/file set mismatch")
        extra.unlink()

        binding = root / "binding.json"; binding.write_text(json.dumps(valid), encoding="utf-8")
        synced = sync_binding(binding, root / "cache", dev_source=ROOT)
        validate_pack(synced, expected_revision=REVISION)
        assert synced == sync_binding(binding, root / "cache", dev_source=ROOT)

    print("Harness canonical Consumer Pack v1: PASS")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
