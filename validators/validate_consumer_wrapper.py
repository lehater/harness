#!/usr/bin/env python3
"""Validate clean-target bootstrap through the standalone Harness wrapper."""
from __future__ import annotations

import ast
import json
import os
import shutil
import subprocess
import sys
import tempfile
import venv

import yaml
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from harness.application.consumer_pack import validate_pack  # noqa: E402

WRAPPER = ROOT / "distribution/harnessw.py"


def _run_wrapper(
    wrapper: Path,
    binding: Path,
    cache: Path,
    *extra: str,
    check: bool = True,
    python: str = sys.executable,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            python,
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
        cwd=wrapper.parents[1],
        env=_clean_env(),
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


def _clean_env() -> dict[str, str]:
    env = dict(os.environ)
    env.pop("PYTHONPATH", None)
    env["PYTHONNOUSERSITE"] = "1"
    return env


def _source_snapshot(destination: Path) -> str:
    """Freeze the current candidate so pinned paths test edits before a checkpoint."""
    subprocess.run(["git", "clone", "--quiet", "--no-hardlinks", str(ROOT), str(destination)], check=True)
    changed = subprocess.run(
        ["git", "-C", str(ROOT), "diff", "HEAD", "--name-only"],
        check=True, capture_output=True, text=True,
    ).stdout.splitlines()
    added = subprocess.run(
        ["git", "-C", str(ROOT), "ls-files", "--others", "--exclude-standard"],
        check=True, capture_output=True, text=True,
    ).stdout.splitlines()
    for relative in changed + added:
        target = destination / relative
        if (ROOT / relative).is_file():
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / relative, target)
        elif target.is_file():
            target.unlink()
    return _commit_snapshot(destination)


def _commit_snapshot(source: Path) -> str:
    subprocess.run(["git", "-C", str(source), "add", "-A"], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(source), "-c", "user.name=Harness acceptance",
                    "-c", "user.email=acceptance@example.invalid", "commit", "--quiet",
                    "--allow-empty", "-m", "Freeze wrapper acceptance source"], check=True)
    return subprocess.run(["git", "-C", str(source), "rev-parse", "HEAD"],
                          check=True, capture_output=True, text=True).stdout.strip()


def test_matrix(temp_root: Path, source: Path, revision: str, consumer_api: str) -> None:

    target = temp_root / "target"
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
                "consumer_api": consumer_api,
                "source": {
                    "repository": str(source),
                    "revision": revision,
                },
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    cache = temp_root / "cache"
    first = _run_wrapper(wrapper, binding, cache)
    pack = Path(first.stdout.strip().splitlines()[-1]).resolve()
    assert pack.is_dir()
    manifest = validate_pack(pack, expected_revision=revision, expected_api=consumer_api)
    assert manifest["binding_revision"] == revision

    # The clean target has no copied Harness skill tree.
    assert not (target / "skills").exists()
    assert not (harness_dir / "skills").exists()

    # The materialized distribution contains Consumer routing but no
    # Maintainer registry/skills.
    assert (pack / "skill_router.py").is_file() == (consumer_api == "v0")
    assert (pack / "consumer_pack.py").is_file() == (consumer_api == "v0")
    assert (pack / "skills/consumer-operation-registry-v0.yaml").is_file()
    assert not (pack / "skills/maintainer-operation-registry-v0.yaml").exists()
    assert not (pack / "skills/maintainer").exists()

    routed = subprocess.run(
        [
            *([sys.executable, str(pack / "skill_router.py")] if consumer_api == "v0"
              else [sys.executable, "-m", "harness.application.skill_router"]),
            "operation",
            "--surface",
            "consumer",
            "--operation",
            "project-engineering-status",
            "--root",
            str(pack),
        ],
        cwd=str(pack),
        env=_clean_env(),
        check=True,
        capture_output=True,
        text=True,
    )
    value = json.loads(routed.stdout)
    assert value["skill"] == "skills/agent/project-engineering-status/SKILL.md"

    if consumer_api == "v1":
        validated = subprocess.run(
            [sys.executable, "-m", "harness.application.consumer_pack", "validate-pack",
             str(pack), "--consumer-api", "v1"],
            cwd=pack, env=_clean_env(), check=True, capture_output=True, text=True,
        )
        assert json.loads(validated.stdout) == {"status": "VALID", "consumer_api": "v1"}
        # Exercise the canonical sync_binding pinned-source and reuse paths too.
        command = [sys.executable, "-m", "harness.application.consumer_pack", "sync",
                   str(binding), str(temp_root / "native-cache")]
        native = subprocess.run(command, cwd=source, env=_clean_env(),
                                check=True, capture_output=True, text=True)
        native_pack = Path(native.stdout.strip())
        validate_pack(native_pack, expected_revision=revision, expected_api="v1")
        reused = subprocess.run(command, cwd=source, env=_clean_env(),
                                check=True, capture_output=True, text=True)
        assert Path(reused.stdout.strip()) == native_pack

    # A second clean sync reuses the validated immutable pack.
    original_binding = binding.read_text()
    offline_binding = json.loads(original_binding)
    offline_binding["source"]["repository"] = str(temp_root / "unavailable-repository")
    binding.write_text(json.dumps(offline_binding))
    second = _run_wrapper(wrapper, binding, cache)
    binding.write_text(original_binding)
    assert Path(second.stdout.strip().splitlines()[-1]).resolve() == pack

    # Development override is explicit and does not mutate the pinned
    # binding identity.
    dev = _run_wrapper(
        wrapper,
        binding,
        cache,
        "--dev-source",
        str(source),
    )
    dev_pack = Path(dev.stdout.strip().splitlines()[-1]).resolve()
    dev_manifest = validate_pack(dev_pack, expected_revision=revision, expected_api=consumer_api)
    assert dev_manifest["binding_revision"] == revision
    assert binding.read_text(encoding="utf-8").find(revision) >= 0

    invalid = harness_dir / "invalid-binding.json"
    invalid.write_text(
        json.dumps(
            {
                "version": 1,
                "kind": "harness-consumer-binding",
                "consumer_api": consumer_api,
                "source": {
                    "repository": str(source),
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
    # Unknown API fails before source transport or materialization.
    unknown = json.loads(binding.read_text())
    unknown["consumer_api"] = "v2"
    invalid.write_text(json.dumps(unknown))
    rejected = _run_wrapper(wrapper, invalid, cache, check=False)
    assert rejected.returncode == 2 and "consumer_api" in rejected.stderr
    # Tampering triggers rebuild from the exact source, for both APIs.
    tracked = pack / "src/harness/application/skill_router.py"
    tracked.write_bytes(tracked.read_bytes() + b"\n# tampered\n")
    rebuilt = _run_wrapper(wrapper, binding, cache)
    assert Path(rebuilt.stdout.strip()) == pack
    validate_pack(pack, expected_revision=revision, expected_api=consumer_api)



def test_v0_to_v1_migration(temp_root: Path, source: Path, revision: str) -> None:
    """One target/wrapper migrates API and pin without changing project truth."""
    from validators.validate_consumer_api_lifecycle import facade_paths

    target = temp_root / "target"
    harness_dir = target / ".harness"
    harness_dir.mkdir(parents=True)
    wrapper = harness_dir / "harnessw.py"
    shutil.copy2(WRAPPER, wrapper)
    wrapper_bytes = wrapper.read_bytes()
    # Representative target-owned source and semantic artifacts are immutable.
    (target / "src").mkdir()
    (target / "src/product.py").write_text("PRODUCT = 'target-owned'\n")
    (harness_dir / "knowledge.yaml").write_text("authority: TARGET\nacceptance: reviewed-v1\n")
    truth = {p.relative_to(target): p.read_bytes() for p in target.rglob("*") if p.is_file()}
    interpreter = temp_root / "interpreter"
    venv.EnvBuilder(with_pip=False).create(interpreter)
    python = str(interpreter / "bin/python")
    purelib = subprocess.check_output(
        [python, "-c", "import sysconfig; print(sysconfig.get_path('purelib'))"],
        cwd=target, env=_clean_env(), text=True,
    ).strip()
    shutil.copytree(Path(yaml.__file__).parent, Path(purelib) / "yaml")
    subprocess.run([python, "-c", "import importlib.util, os; "
                    "assert 'PYTHONPATH' not in os.environ; "
                    "assert importlib.util.find_spec('harness') is None"],
                   cwd=target, env=_clean_env(), check=True)
    binding = harness_dir / "harness-binding.json"
    value = {"version": 1, "kind": "harness-consumer-binding", "consumer_api": "v0",
             "source": {"repository": str(source), "revision": revision}}
    binding.write_text(json.dumps(value))
    cache = temp_root / "cache"
    old_pack = Path(_run_wrapper(wrapper, binding, cache, python=python).stdout.strip())
    validate_pack(old_pack, expected_revision=revision, expected_api="v0")

    def semantics(pack: Path, api: str) -> dict:
        routes = {}
        for name, args, expected in (
            ("operation", ["operation", "--surface", "consumer", "--operation", "project-engineering-status"],
             "skills/agent/project-engineering-status/SKILL.md"),
            ("artifact", ["artifact", "--knowledge-kind", "verification-strategy"],
             "skills/artifacts/verification-strategy/SKILL.md"),
        ):
            command = ([python, str(pack / "skill_router.py")] if api == "v0" else
                       [python, "-m", "harness.application.skill_router"])
            result = subprocess.run([*command, *args, "--root", str(pack)], cwd=pack,
                                    env=_clean_env(), capture_output=True, text=True, check=True)
            route = json.loads(result.stdout)
            assert route["skill"] == expected
            assert route["instruction_contracts"] == ["docs/design/agent-instruction-architecture-v0.md"]
            routes[name] = route
        probe = """
import json
from pathlib import Path
from scenario_suite import run_scenario
results = []
for name in ('create-work-routing', 'structural-provider-removal', 'semantic-gap-question'):
    result = run_scenario(Path('spec/scenario-suite/scenarios/' + name + '.yaml')).as_dict()
    assert result['status'] == 'PASSED', result
    result.pop('path')
    results.append(result)
print(json.dumps(results))
"""
        result = subprocess.run([python, "-c", probe], cwd=pack, env=_clean_env(),
                                capture_output=True, text=True, check=True)
        return {"routes": routes, "scenarios": json.loads(result.stdout)}

    before = semantics(old_pack, "v0")
    # A second immutable pin physically lacks every v0 facade. This is test-only
    # removal, not permission to delete any surface from the repository.
    stripped = temp_root / "v1-source"
    subprocess.run(["git", "clone", "--quiet", "--no-hardlinks", str(source), str(stripped)], check=True)
    layout = yaml.safe_load((stripped / "spec/architecture/repository-layout-v0.yaml").read_text())
    retired = facade_paths(layout)
    for relative in retired:
        (stripped / relative).unlink()
    v1_revision = _commit_snapshot(stripped)
    assert revision != v1_revision
    value["consumer_api"] = "v1"
    value["source"] = {"repository": str(stripped), "revision": v1_revision}
    binding.write_text(json.dumps(value))
    new_pack = Path(_run_wrapper(wrapper, binding, cache, python=python).stdout.strip())
    validate_pack(new_pack, expected_revision=v1_revision, expected_api="v1")
    assert new_pack != old_pack
    assert all(not (new_pack / relative).exists() for relative in retired)
    assert semantics(new_pack, "v1") == before, "Consumer migration changed semantic observations"
    assert wrapper.read_bytes() == wrapper_bytes
    assert {p.relative_to(target): p.read_bytes() for p in target.rglob("*")
            if p.is_file() and p != binding} == truth
    print("v0 -> v1 migration PASS: same wrapper; isolated interpreter; immutable pins; "
          "routes and three authored scenario traces equivalent; v1 facades absent")


def main() -> int:
    _assert_stdlib_only()
    with tempfile.TemporaryDirectory(prefix="harness-wrapper-validation-") as temp:
        root = Path(temp)
        source = root / "source"
        revision = _source_snapshot(source)
        test_matrix(root / "v0", source, revision, "v0")
        test_v0_to_v1_migration(root / "migration", source, revision)
        # Regression: every v1 source execution path must work without this facade.
        (source / "consumer_pack.py").unlink()
        revision = _commit_snapshot(source)
        test_matrix(root / "v1", source, revision, "v1")
    print("Harness v0 and v1 clean-target wrapper validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
