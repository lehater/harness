#!/usr/bin/env python3
"""Ratchet validator for the Harness DDD bounded-context map."""
from __future__ import annotations

import ast
from pathlib import Path
import sys
import yaml

ROOT = Path(__file__).resolve().parents[1]
MAP = ROOT / "spec" / "architecture" / "harness-context-map-v0.yaml"
LAYOUT = ROOT / "spec" / "architecture" / "repository-layout-v0.yaml"


def load_map() -> dict:
    value = yaml.safe_load(MAP.read_text(encoding="utf-8"))
    if not isinstance(value, dict) or value.get("kind") != "harness-bounded-context-map":
        raise SystemExit("invalid Harness bounded-context map")
    return value


def load_layout() -> dict:
    value = yaml.safe_load(LAYOUT.read_text(encoding="utf-8"))
    if not isinstance(value, dict) or value.get("kind") != "harness-repository-layout":
        raise SystemExit("invalid Harness repository-layout contract")
    return value


def _root_python_modules() -> set[str]:
    return {path.stem for path in ROOT.glob("*.py") if path.is_file()}


def _validate_physical_layout(
    layout: dict,
    contexts: dict,
    owner: dict[str, str],
    ignored: set[str],
) -> None:
    design = layout.get("design")
    if not isinstance(design, str) or not design or not (ROOT / design).is_file():
        raise SystemExit("repository layout must reference an existing design contract")

    context_map = layout.get("context_map")
    if context_map != MAP.relative_to(ROOT).as_posix():
        raise SystemExit("repository layout must reference the canonical context map")

    target = layout.get("runtime_target")
    if not isinstance(target, dict) or target.get("root") != "src/harness":
        raise SystemExit("runtime_target.root must be src/harness")

    packages = target.get("packages")
    if not isinstance(packages, dict) or set(packages) != set(contexts):
        raise SystemExit(
            "runtime_target.packages must map every bounded context/application layer"
        )
    for context_name, package in packages.items():
        if not isinstance(package, str) or not package.isidentifier():
            raise SystemExit(
                f"invalid target package for {context_name}: {package!r}"
            )

    root_python = layout.get("root_python")
    if not isinstance(root_python, dict):
        raise SystemExit("root_python migration policy is required")
    if root_python.get("policy") != "migration-ratchet":
        raise SystemExit("root_python.policy must be migration-ratchet")

    baseline_values = root_python.get("migration_baseline_modules")
    exceptions_values = root_python.get("permanent_bootstrap_exceptions", [])
    for label, values in (
        ("migration_baseline_modules", baseline_values),
        ("permanent_bootstrap_exceptions", exceptions_values),
    ):
        if not isinstance(values, list) or any(
            not isinstance(value, str) or not value for value in values
        ):
            raise SystemExit(f"root_python.{label} must be a string list")
        if len(values) != len(set(values)):
            raise SystemExit(f"root_python.{label} contains duplicates")

    baseline = set(baseline_values)
    exceptions = set(exceptions_values)
    overlap = sorted(baseline & exceptions)
    if overlap:
        raise SystemExit(
            f"root Python modules cannot be both migration baseline and exception: {overlap}"
        )

    classified = set(owner) | ignored
    unclassified = sorted((baseline | exceptions) - classified)
    if unclassified:
        raise SystemExit(
            f"repository-layout root modules lack context/test classification: {unclassified}"
        )

    actual = _root_python_modules()
    unexpected = sorted(actual - baseline - exceptions)
    stale = sorted(baseline - actual)
    stale_exceptions = sorted(exceptions - actual)
    if unexpected:
        raise SystemExit(
            "new root Python modules are forbidden during package migration: "
            f"{unexpected}"
        )
    if stale:
        raise SystemExit(
            "remove migrated/deleted modules from root migration baseline: "
            f"{stale}"
        )
    if stale_exceptions:
        raise SystemExit(
            "remove missing permanent root bootstrap exceptions: "
            f"{stale_exceptions}"
        )


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
    _validate_physical_layout(load_layout(), contexts, owner, ignored)
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
        "Harness bounded-context/repository-layout boundaries: PASS "
        f"({len(actual_violations)} known violation(s) ratcheted)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
