#!/usr/bin/env python3
"""Portable target-repository bootstrap for a pinned Harness Consumer Pack.

This file is intentionally standard-library-only so a clean target checkout can
materialize Harness before any Harness runtime/skill code is locally available.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import venv
from pathlib import Path
from typing import Any

WRAPPER_VERSION = 1
REVISION_RE = re.compile(r"^[0-9a-fA-F]{40}$")
PY_YAML_REQUIREMENT = "PyYAML==6.0.3"


class WrapperError(RuntimeError):
    pass


def load_binding(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise WrapperError(f"cannot load Harness binding {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise WrapperError("Harness binding must contain a JSON object")
    if value.get("version") != 1:
        raise WrapperError("Harness binding version must be 1")
    if value.get("kind") != "harness-consumer-binding":
        raise WrapperError("unexpected Harness binding kind")
    if value.get("consumer_api") not in ("v0", "v1"):
        raise WrapperError("unsupported Harness consumer_api; expected v0 or v1")

    source = value.get("source")
    if not isinstance(source, dict) or set(source) != {"repository", "revision"}:
        raise WrapperError(
            "Harness binding source must contain exactly repository and revision"
        )
    repository = source["repository"]
    revision = source["revision"]
    if not isinstance(repository, str) or not repository.strip():
        raise WrapperError("Harness binding repository is required")
    if not isinstance(revision, str) or not REVISION_RE.fullmatch(revision):
        raise WrapperError(
            "Harness binding revision must be an immutable 40-hex commit"
        )
    return value


def default_cache_root() -> Path:
    explicit = os.environ.get("HARNESS_CACHE_DIR")
    if explicit:
        return Path(explicit).expanduser().resolve()
    if os.name == "nt":
        local = os.environ.get("LOCALAPPDATA")
        if local:
            return (Path(local) / "Harness" / "Cache").resolve()
    return (Path.home() / ".cache" / "harness").resolve()


def _run(
    args: list[str],
    *,
    cwd: Path | None = None,
    capture: bool = True,
) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            args,
            cwd=str(cwd) if cwd is not None else None,
            check=True,
            capture_output=capture,
            text=True,
        )
    except FileNotFoundError as exc:
        raise WrapperError(f"required executable not found: {args[0]}") from exc
    except subprocess.CalledProcessError as exc:
        detail = (exc.stderr or exc.stdout or "").strip()
        raise WrapperError(
            f"command failed ({' '.join(args)}): {detail or exc.returncode}"
        ) from exc


def _has_pyyaml(python: Path) -> bool:
    try:
        subprocess.run(
            [str(python), "-c", "import yaml"],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return True
    except (OSError, subprocess.CalledProcessError):
        return False


def _bootstrap_python(cache_root: Path) -> Path:
    current = Path(sys.executable).resolve()
    if _has_pyyaml(current):
        return current

    env_root = cache_root / "_bootstrap" / "pyyaml-6.0.3"
    if os.name == "nt":
        python = env_root / "Scripts" / "python.exe"
    else:
        python = env_root / "bin" / "python"

    if not _has_pyyaml(python):
        env_root.parent.mkdir(parents=True, exist_ok=True)
        if env_root.exists():
            shutil.rmtree(env_root)
        try:
            venv.EnvBuilder(with_pip=True, clear=True).create(env_root)
        except Exception as exc:
            raise WrapperError(f"cannot create Harness bootstrap venv: {exc}") from exc
        _run(
            [
                str(python),
                "-m",
                "pip",
                "install",
                "--disable-pip-version-check",
                PY_YAML_REQUIREMENT,
            ]
        )

    if not _has_pyyaml(python):
        raise WrapperError("Harness bootstrap Python cannot import PyYAML")
    return python


def _git_head(path: Path) -> str:
    result = _run(["git", "-C", str(path), "rev-parse", "HEAD"])
    revision = result.stdout.strip()
    if not REVISION_RE.fullmatch(revision):
        raise WrapperError(f"resolved invalid Git revision: {revision!r}")
    return revision


def _pack_command(python: Path, root: Path, consumer_api: str) -> list[str]:
    if consumer_api == "v1":
        return [str(python), "-m", "harness.application.consumer_pack"]
    tool = root / "consumer_pack.py"
    if not tool.is_file():
        raise WrapperError(f"Harness source/Pack has no consumer_pack.py: {root}")
    return [str(python), str(tool)]


def _api_selector(consumer_api: str) -> list[str]:
    return ["--consumer-api", "v1"] if consumer_api == "v1" else []


def _validate_existing_pack(
    python: Path,
    pack: Path,
    revision: str,
    consumer_api: str = "v0",
) -> bool:
    try:
        subprocess.run(
            [
                *_pack_command(python, pack, consumer_api),
                "validate-pack",
                str(pack),
                "--revision",
                revision,
                *_api_selector(consumer_api),
            ],
            cwd=str(pack),
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            text=True,
        )
        return True
    except (OSError, subprocess.CalledProcessError, WrapperError):
        return False


def _fetch_source(repository: str, revision: str, destination: Path) -> None:
    _run(["git", "init", str(destination)])
    _run(["git", "-C", str(destination), "remote", "add", "origin", repository])
    _run(
        [
            "git",
            "-C",
            str(destination),
            "fetch",
            "--depth=1",
            "origin",
            revision,
        ]
    )
    _run(
        [
            "git",
            "-C",
            str(destination),
            "checkout",
            "--detach",
            "FETCH_HEAD",
        ]
    )
    actual = _git_head(destination)
    if actual.lower() != revision.lower():
        raise WrapperError(
            f"resolved Harness revision {actual} does not match binding {revision}"
        )


def sync(
    *,
    binding_path: Path,
    cache_root: Path,
    dev_source: Path | None = None,
) -> Path:
    binding = load_binding(binding_path)
    source = binding["source"]
    revision = source["revision"].lower()
    consumer_api = binding["consumer_api"]
    python = _bootstrap_python(cache_root)

    if dev_source is not None:
        dev_source = dev_source.expanduser().resolve()
        result = _run(
            [
                *_pack_command(python, dev_source, consumer_api),
                "sync",
                str(binding_path),
                str(cache_root),
                "--dev-source",
                str(dev_source),
            ],
            cwd=dev_source,
        )
        output = Path(result.stdout.strip().splitlines()[-1]).resolve()
        if not output.is_dir():
            raise WrapperError(f"Harness dev Consumer Pack was not created: {output}")
        return output

    pack = cache_root / consumer_api / revision
    if pack.is_dir() and _validate_existing_pack(python, pack, revision, consumer_api):
        return pack
    if pack.exists():
        shutil.rmtree(pack)

    cache_root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(
        prefix="harness-wrapper-source-",
        dir=str(cache_root),
    ) as temp:
        checkout = Path(temp) / "source"
        _fetch_source(source["repository"], revision, checkout)
        _run(
            [
                *_pack_command(python, checkout, consumer_api),
                "materialize",
                str(checkout),
                str(pack),
                "--revision",
                revision,
                *_api_selector(consumer_api),
            ],
            cwd=checkout,
        )

    if not _validate_existing_pack(python, pack, revision, consumer_api):
        raise WrapperError("materialized Harness Consumer Pack failed validation")
    return pack


def main() -> int:
    parser = argparse.ArgumentParser(description="Harness target-repository wrapper")
    parser.add_argument(
        "command",
        choices=("sync",),
        help="materialize/validate the pinned Harness Consumer Pack",
    )
    parser.add_argument(
        "--binding",
        default=".harness/harness-binding.json",
    )
    parser.add_argument("--cache")
    parser.add_argument("--dev-source")
    args = parser.parse_args()

    try:
        output = sync(
            binding_path=Path(args.binding).expanduser().resolve(),
            cache_root=(
                Path(args.cache).expanduser().resolve()
                if args.cache
                else default_cache_root()
            ),
            dev_source=(
                Path(args.dev_source)
                if args.dev_source is not None
                else None
            ),
        )
    except WrapperError as exc:
        print(f"Harness wrapper error: {exc}", file=sys.stderr)
        return 2

    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
