#!/usr/bin/env python3
"""Canonical v1 clean-target wrapper acceptance."""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WRAPPER = ROOT / "distribution" / "harnessw.py"


def clean_env() -> dict[str, str]:
    env = dict(os.environ)
    env.pop("PYTHONPATH", None)
    env["PYTHONNOUSERSITE"] = "1"
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    return env


def run(
    args: list[str],
    *,
    cwd: Path,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        cwd=cwd,
        env=clean_env(),
        capture_output=True,
        text=True,
        check=check,
    )


def create_source_snapshot(destination: Path) -> str:
    shutil.copytree(
        ROOT,
        destination,
        ignore=shutil.ignore_patterns(
            ".git",
            "__pycache__",
            ".pytest_cache",
            ".venv",
            ".mypy_cache",
            ".ruff_cache",
        ),
    )
    run(["git", "init", "-q"], cwd=destination)
    run(["git", "add", "."], cwd=destination)
    run(
        [
            "git",
            "-c",
            "user.name=Harness Test",
            "-c",
            "user.email=harness@example.invalid",
            "commit",
            "-q",
            "-m",
            "test source snapshot",
        ],
        cwd=destination,
    )
    revision = run(["git", "rev-parse", "HEAD"], cwd=destination).stdout.strip()
    assert len(revision) == 40
    return revision


def run_wrapper(
    wrapper: Path,
    binding: Path,
    cache: Path,
    *,
    dev_source: Path | None = None,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    command = [
        sys.executable,
        str(wrapper),
        "sync",
        "--binding",
        str(binding),
        "--cache",
        str(cache),
    ]
    if dev_source is not None:
        command.extend(["--dev-source", str(dev_source)])
    return run(command, cwd=wrapper.parents[1], check=check)


def route_from_pack(pack: Path) -> dict:
    result = run(
        [
            sys.executable,
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
    )
    return json.loads(result.stdout)


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="harness-wrapper-v1-") as tmp:
        root = Path(tmp)
        source = root / "source"
        revision = create_source_snapshot(source)

        target = root / "target"
        harness_dir = target / ".harness"
        harness_dir.mkdir(parents=True)
        wrapper = harness_dir / "harnessw.py"
        shutil.copy2(WRAPPER, wrapper)
        wrapper_bytes = wrapper.read_bytes()

        binding = harness_dir / "harness-binding.json"
        valid = {
            "version": 1,
            "kind": "harness-consumer-binding",
            "consumer_api": "v1",
            "source": {"repository": str(source), "revision": revision},
        }
        binding.write_text(json.dumps(valid), encoding="utf-8")
        cache = root / "cache"

        first = run_wrapper(wrapper, binding, cache)
        pack = Path(first.stdout.strip().splitlines()[-1]).resolve()
        assert pack.is_dir()
        assert not list(pack.glob("*.py"))
        assert (pack / "src/harness/application/consumer_pack.py").is_file()
        assert (pack / "src/harness/application/scenario_suite.py").is_file()
        assert route_from_pack(pack)["skill"] == (
            "skills/agent/project-engineering-status/SKILL.md"
        )
        assert not (target / "skills").exists()
        assert not (harness_dir / "skills").exists()

        offline = json.loads(binding.read_text(encoding="utf-8"))
        offline["source"]["repository"] = str(root / "unavailable-source")
        binding.write_text(json.dumps(offline), encoding="utf-8")
        second = run_wrapper(wrapper, binding, cache)
        assert Path(second.stdout.strip().splitlines()[-1]).resolve() == pack

        binding.write_text(json.dumps(valid), encoding="utf-8")
        tracked = pack / "src/harness/application/skill_router.py"
        tracked.write_bytes(tracked.read_bytes() + b"\n# tampered\n")
        rebuilt = run_wrapper(wrapper, binding, cache)
        assert Path(rebuilt.stdout.strip().splitlines()[-1]).resolve() == pack
        assert b"# tampered" not in tracked.read_bytes()
        assert route_from_pack(pack)["skill"]

        invalid_revision = dict(valid)
        invalid_revision["source"] = dict(valid["source"])
        invalid_revision["source"]["revision"] = "main"
        binding.write_text(json.dumps(invalid_revision), encoding="utf-8")
        rejected = run_wrapper(wrapper, binding, cache, check=False)
        assert rejected.returncode == 2
        assert "40-hex" in rejected.stderr

        legacy = dict(valid)
        legacy["consumer_api"] = "v0"
        binding.write_text(json.dumps(legacy), encoding="utf-8")
        rejected = run_wrapper(wrapper, binding, cache, check=False)
        assert rejected.returncode == 2
        assert "expected v1" in rejected.stderr

        binding.write_text(json.dumps(valid), encoding="utf-8")
        dev_cache = root / "dev-cache"
        dev = run_wrapper(
            wrapper,
            binding,
            dev_cache,
            dev_source=source,
        )
        dev_pack = Path(dev.stdout.strip().splitlines()[-1]).resolve()
        assert dev_pack.is_dir()
        assert route_from_pack(dev_pack)["skill"]

        assert wrapper.read_bytes() == wrapper_bytes
        assert binding.read_text(encoding="utf-8").find(revision) >= 0

    print(
        "Harness canonical v1 clean-target wrapper: PASS "
        "(pinned fetch + offline reuse + tamper rebuild + dev source)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
