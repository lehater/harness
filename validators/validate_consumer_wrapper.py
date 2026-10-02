#!/usr/bin/env python3
"""Validate clean-target bootstrap through the standalone Harness wrapper."""
from __future__ import annotations

import ast
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from consumer_pack import validate_pack  # noqa: E402

WRAPPER = ROOT / "distribution/harnessw.py"


def _git_head() -> str:
    result = subprocess.run(
        ["git", "-C", str(ROOT), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def _run_wrapper(
    wrapper: Path,
    binding: Path,
    cache: Path,
    *extra: str,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(wrapper),
            "sync",
            "--binding",
            str(binding),
            "--cache",
            str(cache),
            *extra,
        ],
        check=check,
        capture_output=True,
        text=True,
    )


def _assert_stdlib_only() -> None:
    tree = ast.parse(WRAPPER.read_text(encoding="utf-8"), filename=str(WRAPPER))
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name.split(".", 1)[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".", 1)[0])
    nonstdlib = sorted(
        module
        for module in imported
        if module not in sys.stdlib_module_names and module != "__future__"
    )
    assert nonstdlib == [], f"wrapper imports non-stdlib modules: {nonstdlib}"


def main() -> int:
    _assert_stdlib_only()
    revision = _git_head()

    with tempfile.TemporaryDirectory(prefix="harness-wrapper-validation-") as temp:
        target = Path(temp) / "target"
        harness_dir = target / ".harness"
        harness_dir.mkdir(parents=True)
        wrapper = harness_dir / "harnessw.py"
        shutil.copy2(WRAPPER, wrapper)

        binding = harness_dir / "harness-binding.json"
        binding.write_text(
            json.dumps(
                {
                    "version": 1,
                    "kind": "harness-consumer-binding",
                    "consumer_api": "v0",
                    "source": {
                        "repository": str(ROOT),
                        "revision": revision,
                    },
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )

        cache = Path(temp) / "cache"
        first = _run_wrapper(wrapper, binding, cache)
        pack = Path(first.stdout.strip().splitlines()[-1]).resolve()
        assert pack.is_dir()
        manifest = validate_pack(pack, expected_revision=revision)
        assert manifest["binding_revision"] == revision

        # The clean target has no copied Harness skill tree.
        assert not (target / "skills").exists()
        assert not (harness_dir / "skills").exists()

        # The materialized distribution contains Consumer routing but no
        # Maintainer registry/skills.
        assert (pack / "skill_router.py").is_file()
        assert (pack / "skills/consumer-operation-registry-v0.yaml").is_file()
        assert not (pack / "skills/maintainer-operation-registry-v0.yaml").exists()
        assert not (pack / "skills/maintainer").exists()

        routed = subprocess.run(
            [
                sys.executable,
                str(pack / "skill_router.py"),
                "operation",
                "--surface",
                "consumer",
                "--operation",
                "project-engineering-status",
                "--root",
                str(pack),
            ],
            cwd=str(pack),
            check=True,
            capture_output=True,
            text=True,
        )
        value = json.loads(routed.stdout)
        assert value["skill"] == "skills/agent/project-engineering-status/SKILL.md"

        # A second clean sync reuses the validated immutable pack.
        second = _run_wrapper(wrapper, binding, cache)
        assert Path(second.stdout.strip().splitlines()[-1]).resolve() == pack

        # Development override is explicit and does not mutate the pinned
        # binding identity.
        dev = _run_wrapper(
            wrapper,
            binding,
            cache,
            "--dev-source",
            str(ROOT),
        )
        dev_pack = Path(dev.stdout.strip().splitlines()[-1]).resolve()
        dev_manifest = validate_pack(dev_pack, expected_revision=revision)
        assert dev_manifest["binding_revision"] == revision
        assert binding.read_text(encoding="utf-8").find(revision) >= 0

        invalid = harness_dir / "invalid-binding.json"
        invalid.write_text(
            json.dumps(
                {
                    "version": 1,
                    "kind": "harness-consumer-binding",
                    "consumer_api": "v0",
                    "source": {
                        "repository": str(ROOT),
                        "revision": "main",
                    },
                }
            ),
            encoding="utf-8",
        )
        rejected = _run_wrapper(
            wrapper,
            invalid,
            cache,
            check=False,
        )
        assert rejected.returncode == 2
        assert "40-hex" in rejected.stderr

    print("Harness clean-target wrapper validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
