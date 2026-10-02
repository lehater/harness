#!/usr/bin/env python3
"""Canonical v1 clean-target wrapper acceptance."""
from __future__ import annotations
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WRAPPER_PATH = ROOT / "distribution" / "harnessw.py"
REVISION = subprocess.run(
    ["git", "-C", str(ROOT), "rev-parse", "HEAD"],
    check=True, capture_output=True, text=True,
).stdout.strip()

spec = importlib.util.spec_from_file_location("harnessw_under_test", WRAPPER_PATH)
assert spec and spec.loader
harnessw = importlib.util.module_from_spec(spec)
spec.loader.exec_module(harnessw)

def clean_env() -> dict[str, str]:
    env = dict(os.environ)
    env.pop("PYTHONPATH", None)
    env["PYTHONNOUSERSITE"] = "1"
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    return env

def main() -> int:
    assert len(REVISION) == 40
    valid = {
        "version": 1,
        "kind": "harness-consumer-binding",
        "consumer_api": "v1",
        "source": {"repository": str(ROOT), "revision": REVISION},
    }
    with tempfile.TemporaryDirectory(prefix="harness-wrapper-v1-") as tmp:
        root = Path(tmp); binding = root / "binding.json"
        binding.write_text(json.dumps(valid), encoding="utf-8")
        assert harnessw.load_binding(binding)["consumer_api"] == "v1"

        bad = dict(valid); bad["consumer_api"] = "v0"
        binding.write_text(json.dumps(bad), encoding="utf-8")
        try:
            harnessw.load_binding(binding)
        except harnessw.WrapperError as exc:
            assert "expected v1" in str(exc)
        else:
            raise AssertionError("legacy v0 binding accepted")

        binding.write_text(json.dumps(valid), encoding="utf-8")
        cache = root / "cache"
        pack = harnessw.sync(binding_path=binding, cache_root=cache, dev_source=ROOT)
        assert pack.is_dir()
        assert not list(pack.glob("*.py"))
        assert (pack / "src/harness/application/consumer_pack.py").is_file()
        assert (pack / "src/harness/application/scenario_suite.py").is_file()
        assert harnessw.sync(binding_path=binding, cache_root=cache, dev_source=ROOT) == pack

        probe = subprocess.run(
            [sys.executable, "-m", "harness.application.skill_router",
             "operation", "--surface", "consumer", "--operation", "project-engineering-status",
             "--root", str(pack)],
            cwd=pack, env=clean_env(), capture_output=True, text=True, check=True,
        )
        assert json.loads(probe.stdout)["skill"]
    print("Harness canonical v1 clean-target wrapper: PASS")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
