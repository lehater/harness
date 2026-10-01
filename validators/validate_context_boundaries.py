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
    root_modules = {
        path.stem
        for path in ROOT.glob("*.py")
        if path.is_file()
    }
    missing = sorted(root_modules - set(owner) - ignored)
    stale = sorted((set(owner) | ignored) - root_modules)
    if missing:
        raise SystemExit(f"unclassified root runtime modules: {missing}")
    if stale:
        raise SystemExit(f"context map references missing root modules: {stale}")

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

    def check_edge(source: str, target: str, imported_names: set[str] | None) -> None:
        if target not in owner:
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
        path = ROOT / f"{source}.py"
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                target = node.module.split(".", 1)[0]
                names = {alias.name for alias in node.names}
                check_edge(source, target, names)
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    target = alias.name.split(".", 1)[0]
                    check_edge(source, target, None)

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
