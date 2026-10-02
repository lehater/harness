#!/usr/bin/env python3
"""Validate canonical repository layout and bounded-context dependency direction."""
from __future__ import annotations

import ast
from pathlib import Path
import sys
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
MAP = ROOT / "spec" / "architecture" / "harness-context-map-v0.yaml"
LAYOUT = ROOT / "spec" / "architecture" / "repository-layout-v0.yaml"
EPHEMERAL_TOP_LEVEL_DIRECTORIES = {
    ".git",
    ".venv",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "__pycache__",
}


def load_yaml(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise SystemExit(f"{path.relative_to(ROOT)} must contain a mapping")
    return value


def load_map() -> dict[str, Any]:
    value = load_yaml(MAP)
    if value.get("kind") != "harness-bounded-context-map":
        raise SystemExit("invalid Harness bounded-context map")
    return value


def load_layout() -> dict[str, Any]:
    value = load_yaml(LAYOUT)
    if value.get("kind") != "harness-repository-layout":
        raise SystemExit("invalid Harness repository-layout contract")
    return value


def _without_docstring(body: list[ast.stmt]) -> list[ast.stmt]:
    if (
        body
        and isinstance(body[0], ast.Expr)
        and isinstance(body[0].value, ast.Constant)
        and isinstance(body[0].value.value, str)
    ):
        return body[1:]
    return body


def _root_python_modules() -> set[str]:
    return {path.stem for path in ROOT.glob("*.py") if path.is_file()}


def _validate_repository_surfaces(layout: dict[str, Any]) -> None:
    surfaces = layout.get("repository_surfaces")
    if not isinstance(surfaces, dict) or surfaces.get("policy") != "closed":
        raise SystemExit("repository_surfaces.policy must be closed")

    directories = surfaces.get("directories")
    if not isinstance(directories, dict) or not directories:
        raise SystemExit("repository_surfaces.directories must be a non-empty mapping")
    for name, role in directories.items():
        if (
            not isinstance(name, str)
            or not name
            or "/" in name
            or name in {".", ".."}
        ):
            raise SystemExit(f"invalid repository surface directory: {name!r}")
        if not isinstance(role, str) or not role.strip():
            raise SystemExit(f"repository surface {name!r} requires a role")

    declared = set(directories)
    actual = {
        path.name
        for path in ROOT.iterdir()
        if path.is_dir() and path.name not in EPHEMERAL_TOP_LEVEL_DIRECTORIES
    }
    missing = sorted(declared - actual)
    undeclared = sorted(actual - declared)
    if missing:
        raise SystemExit(f"declared repository surfaces are missing: {missing}")
    if undeclared:
        raise SystemExit(f"undeclared top-level repository surfaces: {undeclared}")


def _module_path(module: str) -> Path:
    base = ROOT / "src" if module.startswith("harness.") else ROOT
    return base.joinpath(*module.split(".")).with_suffix(".py")


def _validate_bridge(layout: dict[str, Any]) -> None:
    bridge = layout.get("source_tree_bridge")
    expected = {
        "package": "harness",
        "path": "harness/__init__.py",
        "target_root": "src/harness",
    }
    if bridge != expected:
        raise SystemExit(f"source_tree_bridge must be {expected!r}")

    path = ROOT / bridge["path"]
    if not path.is_file():
        raise SystemExit("source-tree bridge is missing")
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    actual = ast.dump(ast.Module(body=_without_docstring(tree.body), type_ignores=[]))
    expected_tree = ast.parse(
        'from pathlib import Path as _Path\n'
        '__path__ = [str(_Path(__file__).resolve().parents[1] / "src" / "harness")]\n'
    )
    expected_ast = ast.dump(expected_tree)
    if actual != expected_ast:
        raise SystemExit("source-tree bridge may only bind harness.__path__ to src/harness")

    canonical_init = ROOT / "src/harness/__init__.py"
    tree = ast.parse(canonical_init.read_text(encoding="utf-8"), filename=str(canonical_init))
    if _without_docstring(tree.body):
        raise SystemExit("src/harness/__init__.py must not own exports or implementation")


def _validate_layout(layout: dict[str, Any], contexts: dict[str, Any]) -> None:
    design = layout.get("design")
    if not isinstance(design, str) or not design or not (ROOT / design).is_file():
        raise SystemExit("repository layout must reference an existing design contract")
    if layout.get("context_map") != MAP.relative_to(ROOT).as_posix():
        raise SystemExit("repository layout must reference the canonical context map")

    _validate_repository_surfaces(layout)

    target = layout.get("runtime_target")
    if not isinstance(target, dict) or target.get("root") != "src/harness":
        raise SystemExit("runtime_target.root must be src/harness")
    packages = target.get("packages")
    if not isinstance(packages, dict) or set(packages) != set(contexts):
        raise SystemExit("runtime_target.packages must map every context/application layer")
    if any(not isinstance(value, str) or not value.isidentifier() for value in packages.values()):
        raise SystemExit("runtime_target package names must be identifiers")

    root_python = layout.get("root_python")
    if root_python != {"policy": "closed"}:
        raise SystemExit("root_python must be the closed canonical policy")
    if _root_python_modules():
        raise SystemExit(f"root Python modules are forbidden: {sorted(_root_python_modules())}")
    if (ROOT / "adapters").exists():
        raise SystemExit("top-level adapters/ is retired; use canonical package/evals paths")

    if "compatibility" in layout:
        raise SystemExit("legacy compatibility registry is forbidden after migration closure")
    _validate_bridge(layout)


def _validate_initializer(path: Path) -> None:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    if _without_docstring(tree.body):
        raise SystemExit(
            f"package initializer cannot own implementation: {path.relative_to(ROOT)}"
        )


def _runtime_modules(spec: dict[str, Any]) -> set[str]:
    result: set[str] = set()

    src = ROOT / "src/harness"
    if not src.is_dir():
        raise SystemExit("canonical runtime root src/harness is missing")
    for path in src.rglob("*.py"):
        if path.name == "__init__.py":
            _validate_initializer(path)
            continue
        module = ".".join(path.relative_to(ROOT / "src").with_suffix("").parts)
        if module in result:
            raise SystemExit(f"duplicate runtime module identity: {module}")
        result.add(module)

    packages = spec.get("runtime_packages", []) or []
    if not isinstance(packages, list) or any(
        not isinstance(package, str) or not package for package in packages
    ):
        raise SystemExit("runtime_packages must be a string list")
    if len(packages) != len(set(packages)):
        raise SystemExit("runtime_packages contains duplicates")

    for package in packages:
        base = ROOT / package
        if not base.is_dir():
            raise SystemExit(f"runtime package missing: {package}")
        for path in base.rglob("*.py"):
            if path.name == "__init__.py":
                _validate_initializer(path)
                continue
            module = ".".join(path.relative_to(ROOT).with_suffix("").parts)
            if module in result:
                raise SystemExit(f"duplicate runtime module identity: {module}")
            result.add(module)
    return result


def _resolve_target(module_name: str, owner: dict[str, str]) -> str | None:
    parts = module_name.split(".")
    for length in range(len(parts), 0, -1):
        candidate = ".".join(parts[:length])
        if candidate in owner:
            return candidate
    return None


def _reject_retired_imports(path: Path, legacy_leafs: set[str]) -> None:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in ast.walk(tree):
        names: list[str] = []
        if isinstance(node, ast.Import):
            names = [alias.name for alias in node.names]
        elif isinstance(node, ast.ImportFrom) and node.level == 0:
            module = node.module or ""
            if module == "harness":
                raise SystemExit(
                    f"{path.relative_to(ROOT)}:{node.lineno} uses retired package-root Core exports"
                )
            names = [module]
        for name in names:
            if name == "adapters" or name.startswith("adapters."):
                raise SystemExit(
                    f"{path.relative_to(ROOT)}:{node.lineno} imports retired top-level adapters"
                )
            if "." not in name and name in legacy_leafs:
                raise SystemExit(
                    f"{path.relative_to(ROOT)}:{node.lineno} imports retired root module {name}"
                )


def _scan_retired_imports(owner: dict[str, str]) -> None:
    legacy_leafs = {module.rsplit(".", 1)[-1] for module in owner if module.startswith("harness.")}
    roots = ("src/harness", "checks", "tests", "evals", "experiments", "distribution")
    for relative in roots:
        base = ROOT / relative
        if not base.exists():
            continue
        for path in base.rglob("*.py"):
            if path.name == "__init__.py":
                continue
            _reject_retired_imports(path, legacy_leafs)


def main() -> int:
    spec = load_map()
    contexts = spec.get("contexts", {}) or {}
    if not isinstance(contexts, dict) or not contexts:
        raise SystemExit("context map must declare contexts")

    owner: dict[str, str] = {}
    for context_name, context in contexts.items():
        modules = context.get("modules", []) or []
        for module in modules:
            previous = owner.setdefault(module, context_name)
            if previous != context_name:
                raise SystemExit(
                    f"module {module} belongs to multiple contexts: {previous}, {context_name}"
                )

    ignored_values = spec.get("ignored_modules", []) or []
    if not isinstance(ignored_values, list) or len(ignored_values) != len(set(ignored_values)):
        raise SystemExit("ignored_modules must be a unique list")
    ignored = set(ignored_values)

    layout = load_layout()
    _validate_layout(layout, contexts)
    _scan_retired_imports(owner)

    runtime_modules = _runtime_modules(spec)
    missing = sorted(runtime_modules - set(owner) - ignored)
    stale = sorted((set(owner) | ignored) - runtime_modules)
    if missing:
        raise SystemExit(f"unclassified runtime modules: {missing}")
    if stale:
        raise SystemExit(f"context map references missing runtime modules: {stale}")

    packages = layout["runtime_target"]["packages"]
    for module, context in owner.items():
        if module == "distribution.harnessw":
            if context != "application":
                raise SystemExit("distribution.harnessw must belong to application")
            continue
        if not module.startswith("harness."):
            raise SystemExit(f"owned runtime module is not canonical: {module}")
        if not module.startswith(f"harness.{packages[context]}."):
            raise SystemExit(f"canonical module {module} is outside {context}'s package")

    allowed = {
        name: set(context.get("may_depend_on", []) or [])
        for name, context in contexts.items()
    }

    published: dict[tuple[str, str], dict[str, set[str]]] = {}
    for index, item in enumerate(spec.get("published_boundaries", []) or []):
        if not isinstance(item, dict):
            raise SystemExit(f"published boundary #{index + 1} must be a mapping")
        source_context = item.get("from_context")
        target_context = item.get("to_context")
        if source_context not in contexts or target_context not in contexts:
            raise SystemExit(f"published boundary #{index + 1} references unknown context")
        if target_context not in allowed.get(source_context, set()):
            raise SystemExit(
                f"published boundary {source_context}->{target_context} is not an allowed dependency"
            )
        key = (source_context, target_context)
        if key in published:
            raise SystemExit(f"duplicate published boundary: {source_context}->{target_context}")
        modules = item.get("modules")
        if not isinstance(modules, dict) or not modules:
            raise SystemExit(f"published boundary {source_context}->{target_context} requires modules")
        normalized: dict[str, set[str]] = {}
        for module, symbols in modules.items():
            if owner.get(module) != target_context:
                raise SystemExit(f"published boundary module {module} is not owned by {target_context}")
            if not isinstance(symbols, list) or not symbols or len(symbols) != len(set(symbols)):
                raise SystemExit(f"published boundary {module} symbols must be unique/non-empty")
            normalized[module] = set(symbols)
        published[key] = normalized

    shared = {
        module: set(names or [])
        for module, names in (spec.get("shared_kernel_imports", {}) or {}).items()
    }
    declared = {
        (item["from_module"], item["to_module"]): item
        for item in spec.get("known_violations", []) or []
    }
    actual_violations: set[tuple[str, str]] = set()
    published_violations: list[str] = []

    def check_edge(source: str, target_name: str, imported_names: set[str] | None) -> None:
        target = _resolve_target(target_name, owner)
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

        boundary = published.get((source_context, target_context))
        if boundary is not None:
            allowed_symbols = boundary.get(target)
            if allowed_symbols is None:
                published_violations.append(
                    f"{source} ({source_context}) imports non-published module {target} ({target_context})"
                )
                return
            if imported_names is None:
                published_violations.append(
                    f"{source} ({source_context}) imports published module {target} without explicit symbols"
                )
                return
            disallowed = sorted(imported_names - allowed_symbols)
            if disallowed:
                published_violations.append(
                    f"{source} ({source_context}) imports non-published symbols from {target}: {disallowed}"
                )
            return

        if target_context in allowed.get(source_context, set()):
            return
        actual_violations.add((source, target))

    for source in sorted(owner):
        path = _module_path(source)
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                module_name = node.module or ""
                if node.level:
                    package_parts = source.split(".")[:-1]
                    if node.level > len(package_parts):
                        raise SystemExit(f"invalid relative runtime import in {source}")
                    prefix = package_parts[: len(package_parts) - node.level + 1]
                    module_name = ".".join(prefix + ([module_name] if module_name else []))
                names = {alias.name for alias in node.names}
                if _resolve_target(module_name, owner) is not None:
                    check_edge(source, module_name, names)
                else:
                    for alias in node.names:
                        check_edge(source, f"{module_name}.{alias.name}", None)
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    check_edge(source, alias.name, None)

    declared_edges = set(declared)
    unknown = sorted(actual_violations - declared_edges)
    stale_exceptions = sorted(declared_edges - actual_violations)

    if published_violations:
        print("published cross-context contract violations:", file=sys.stderr)
        for violation in sorted(published_violations):
            print(f"- {violation}", file=sys.stderr)
        return 1
    if unknown:
        print("undeclared bounded-context violations:", file=sys.stderr)
        for source, target in unknown:
            print(f"- {source} ({owner[source]}) -> {target} ({owner[target]})", file=sys.stderr)
        return 1
    if stale_exceptions:
        print("remove resolved known_violations from context map:", file=sys.stderr)
        for source, target in stale_exceptions:
            print(f"- {source} -> {target}", file=sys.stderr)
        return 1

    print(
        "Harness bounded-context/repository-layout boundaries: PASS "
        f"({len(actual_violations)} known violation(s) ratcheted; root closed)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
