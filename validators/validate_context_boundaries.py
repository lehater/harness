#!/usr/bin/env python3
"""Ratchet validator for the Harness DDD bounded-context map."""
from __future__ import annotations

import ast
from pathlib import Path
import sys
import yaml

ROOT = Path(__file__).resolve().parents[1]
MAP = ROOT / "spec" / "architecture" / "harness-context-map-v0.yaml"


def load_map() -> dict:
    value = yaml.safe_load(MAP.read_text(encoding="utf-8"))
    if not isinstance(value, dict) or value.get("kind") != "harness-bounded-context-map":
        raise SystemExit("invalid Harness bounded-context map")
    return value


def _module_path(module: str) -> Path:
    return ROOT.joinpath(*module.split(".")).with_suffix(".py")


def _runtime_modules(spec: dict) -> set[str]:
    result = {
        path.stem
        for path in ROOT.glob("*.py")
        if path.is_file()
    }
    packages = spec.get("runtime_packages", []) or []
    if not isinstance(packages, list) or any(
        not isinstance(package, str) or not package for package in packages
    ):
        raise SystemExit("runtime_packages must be a string list")

    for package in packages:
        base = ROOT / package
        if not base.is_dir():
            raise SystemExit(f"runtime package missing: {package}")
        for path in base.rglob("*.py"):
            if path.name == "__init__.py":
                continue
            relative = path.relative_to(ROOT).with_suffix("")
            result.add(".".join(relative.parts))
    return result


def main() -> int:
    spec = load_map()
    contexts = spec.get("contexts", {}) or {}

    owner: dict[str, str] = {}
    for context_name, context in contexts.items():
        for module in context.get("modules", []) or []:
            previous = owner.setdefault(module, context_name)
            if previous != context_name:
                raise SystemExit(
                    f"module {module} belongs to multiple contexts: "
                    f"{previous}, {context_name}"
                )

    ignored = set(spec.get("ignored_modules", []) or [])
    runtime_modules = _runtime_modules(spec)
    missing = sorted(runtime_modules - set(owner) - ignored)
    stale = sorted((set(owner) | ignored) - runtime_modules)
    if missing:
        raise SystemExit(f"unclassified runtime modules: {missing}")
    if stale:
        raise SystemExit(f"context map references missing runtime modules: {stale}")

    allowed = {
        name: set(context.get("may_depend_on", []) or [])
        for name, context in contexts.items()
    }
    shared = {
        module: set(names or [])
        for module, names in (spec.get("shared_kernel_imports", {}) or {}).items()
    }

    declared = {
        (item["from_module"], item["to_module"]): item
        for item in spec.get("known_violations", []) or []
    }
    actual_violations: set[tuple[str, str]] = set()

    def resolve_target(module_name: str) -> str | None:
        parts = module_name.split(".")
        for length in range(len(parts), 0, -1):
            candidate = ".".join(parts[:length])
            if candidate in owner:
                return candidate
        return None

    def check_edge(
        source: str,
        target_name: str,
        imported_names: set[str] | None,
    ) -> None:
        target = resolve_target(target_name)
        if target is None:
            return
        if (
            imported_names is not None
            and target in shared
            and imported_names
            and imported_names <= shared[target]
        ):
            return
        source_context = owner[source]
        target_context = owner[target]
        if source_context == target_context:
            return
        if target_context in allowed.get(source_context, set()):
            return
        actual_violations.add((source, target))

    for source in sorted(owner):
        path = _module_path(source)
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                names = {alias.name for alias in node.names}
                if resolve_target(node.module) is not None:
                    check_edge(source, node.module, names)
                else:
                    for alias in node.names:
                        check_edge(
                            source,
                            f"{node.module}.{alias.name}",
                            None,
                        )
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    check_edge(source, alias.name, None)

    declared_edges = set(declared)
    unknown = sorted(actual_violations - declared_edges)
    stale_exceptions = sorted(declared_edges - actual_violations)

    if unknown:
        print("undeclared bounded-context violations:", file=sys.stderr)
        for source, target in unknown:
            print(
                f"- {source} ({owner[source]}) -> {target} ({owner[target]})",
                file=sys.stderr,
            )
        return 1

    if stale_exceptions:
        print("remove resolved known_violations from context map:", file=sys.stderr)
        for source, target in stale_exceptions:
            print(f"- {source} -> {target}", file=sys.stderr)
        return 1

    print(
        "Harness bounded-context boundaries: PASS "
        f"({len(actual_violations)} known violation(s) ratcheted)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
