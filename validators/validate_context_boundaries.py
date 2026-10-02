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
    facades: set[str],
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

    if facades & (baseline | exceptions):
        raise SystemExit(
            "CLI compatibility must be tracked separately from implementation baseline"
        )

    classified = set(owner) | ignored
    unclassified = sorted((baseline | exceptions) - classified)
    if unclassified:
        raise SystemExit(
            f"repository-layout root modules lack context/test classification: {unclassified}"
        )

    actual = _root_python_modules()
    unexpected = sorted(actual - baseline - exceptions - facades)
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
    base = ROOT / "src" if module.startswith("harness.") else ROOT
    return base.joinpath(*module.split(".")).with_suffix(".py")


def _facade_body(target: str, kind: str) -> str:
    """Closed grammar for migration surfaces, not a semantic implementation."""
    exports = f"from {target} import *\nfrom {target} import __all__\n"
    if kind == "exports":
        return exports
    if kind == "bridge":
        return (
            'from pathlib import Path as _Path\n'
            '__path__ = [str(_Path(__file__).resolve().parents[1] / "src" / "harness")]\n'
            + exports
        )
    if kind == "cli":
        return (
            f"from {target} import main\n"
            'if __name__ == "__main__":\n'
            '    raise SystemExit(main())\n'
        )
    raise SystemExit(f"unknown compatibility surface kind: {kind}")



def _without_docstring(body: list[ast.stmt]) -> list[ast.stmt]:
    if (
        body
        and isinstance(body[0], ast.Expr)
        and isinstance(body[0].value, ast.Constant)
        and isinstance(body[0].value.value, str)
    ):
        return body[1:]
    return body


def _validate_facade_tree(tree: ast.Module, target: str, kind: str) -> None:
    body = list(tree.body)
    body = _without_docstring(body)
    actual = ast.dump(ast.Module(body=body, type_ignores=[]))
    expected = ast.dump(ast.parse(_facade_body(target, kind)))
    if actual != expected:
        raise SystemExit(f"{kind} must only delegate to {target}; implementation is forbidden")


def _validate_facade(relative: str, target: str, kind: str) -> None:
    path = ROOT / relative
    if not path.is_file():
        raise SystemExit(f"compatibility surface missing: {relative}")
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=relative)
        _validate_facade_tree(tree, target, kind)
    except (SyntaxError, SystemExit) as exc:
        raise SystemExit(f"invalid compatibility surface {relative}: {exc}") from exc


def _compatibility(layout: dict, owner: dict[str, str]) -> tuple[dict[str, str], set[str]]:
    compatibility = layout.get("compatibility", {})
    if not isinstance(compatibility, dict) or set(compatibility) - {
        "import_aliases", "cli_facades"
    }:
        raise SystemExit("invalid compatibility metadata")
    aliases: dict[str, str] = {}
    facades: set[str] = set()
    for kind in ("import_aliases", "cli_facades"):
        entries = compatibility.get(kind, {})
        if not isinstance(entries, dict):
            raise SystemExit(f"compatibility.{kind} must be a mapping")
        for legacy, entry in entries.items():
            fields = {"target", "bridge"} if kind == "import_aliases" else {"target"}
            if not isinstance(entry, dict) or set(entry) != fields:
                raise SystemExit(f"invalid compatibility entry: {legacy}")
            target = entry["target"]
            if (
                not isinstance(target, str)
                or target not in owner
                or not _module_path(target).is_file()
            ):
                raise SystemExit(f"compatibility target must be an existing canonical module: {target}")
            if not target.startswith("harness."):
                raise SystemExit(f"compatibility target must live under src/harness: {target}")
            if kind == "import_aliases":
                if not isinstance(legacy, str) or not legacy.isidentifier() or legacy in owner:
                    raise SystemExit(f"import alias cannot own semantics: {legacy}")
                bridge = f"{legacy}/__init__.py"
                if entry["bridge"] != bridge:
                    raise SystemExit(f"import bridge must match alias package: {legacy}")
                if legacy != "harness":
                    raise SystemExit("source package bridge currently supports only harness")
                _validate_facade(bridge, target, "bridge")
                _validate_facade("src/harness/__init__.py", target, "exports")
                aliases[legacy] = target
            else:
                if (
                    not isinstance(legacy, str)
                    or Path(legacy).name != legacy
                    or not legacy.endswith(".py")
                ):
                    raise SystemExit(f"CLI facade must be a root Python file: {legacy}")
                if Path(legacy).stem in owner:
                    raise SystemExit(f"CLI facade cannot own semantics: {legacy}")
                _validate_facade(legacy, target, "cli")
                facades.add(Path(legacy).stem)
    return aliases, facades


def _runtime_modules(spec: dict, facades: set[str], aliases: dict[str, str]) -> set[str]:
    result = _root_python_modules() - facades
    packages = spec.get("runtime_packages", []) or []
    if not isinstance(packages, list) or any(
        not isinstance(package, str) or not package for package in packages
    ):
        raise SystemExit("runtime_packages must be a string list")

    # src modules use import identities, never the physical src prefix.
    bases = [(ROOT / package, ROOT) for package in packages]
    if (ROOT / "src/harness").exists():
        bases.append((ROOT / "src/harness", ROOT / "src"))
    if (ROOT / "harness").exists():
        bases.append((ROOT / "harness", ROOT))
    for base, import_root in bases:
        if not base.is_dir():
            raise SystemExit(f"runtime package missing: {base.relative_to(ROOT)}")
        for path in base.rglob("*.py"):
            if path.name == "__init__.py":
                # Initializers carry package wiring only, never domain meaning.
                registered_exports = (
                    path == ROOT / "src/harness/__init__.py" and "harness" in aliases
                )
                if import_root == ROOT / "src" and not registered_exports:
                    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
                    if _without_docstring(tree.body):
                        raise SystemExit(
                            "packaged initializer cannot own implementation: "
                            f"{path.relative_to(ROOT)}"
                        )
                if base == ROOT / "harness" and (
                    path != base / "__init__.py" or "harness" not in aliases
                ):
                    raise SystemExit(
                        f"undeclared compatibility initializer: {path.relative_to(ROOT)}"
                    )
                continue
            module = ".".join(path.relative_to(import_root).with_suffix("").parts)
            if module in result:
                raise SystemExit(f"duplicate runtime module identity: {module}")
            result.add(module)
    return result


def _resolve_target(module_name: str, owner: dict[str, str], aliases: dict[str, str]) -> str | None:
    # Aliases match exactly; harness.project_model.other must not become Core.
    if module_name in aliases:
        return aliases[module_name]
    parts = module_name.split(".")
    for length in range(len(parts), 0, -1):
        candidate = ".".join(parts[:length])
        if candidate in owner:
            return candidate
    return None


def test_compatibility_guards() -> None:
    target = "harness.project_model.core"
    for kind in ("bridge", "exports", "cli"):
        valid = _facade_body(target, kind)
        _validate_facade_tree(ast.parse(valid), target, kind)
        for mutation in (
            "\nclass ShadowCore: pass\n",
            "\ndef validate_model(model): return model\n",
            "\nreplacement = lambda model: model\n",
            "\nexec('pass')\n",
            "\nimport sys\nsys.path.insert(0, 'src')\n",
        ):
            try:
                _validate_facade_tree(ast.parse(valid + mutation), target, kind)
            except SystemExit:
                pass
            else:
                raise AssertionError(f"{kind} accepted semantic/path mutation")
    owner = {target: "project-model"}
    aliases = {"harness": target}
    assert _resolve_target("harness", owner, aliases) == target
    assert _resolve_target(target, owner, aliases) == target
    assert _resolve_target("harness.project_model.other", owner, aliases) is None


def main() -> int:
    test_compatibility_guards()
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
    layout = load_layout()
    aliases, facades = _compatibility(layout, owner)
    _validate_physical_layout(layout, contexts, owner, ignored, facades)
    runtime_modules = _runtime_modules(spec, facades, aliases)
    missing = sorted(runtime_modules - set(owner) - ignored)
    stale = sorted((set(owner) | ignored) - runtime_modules)
    if missing:
        raise SystemExit(f"unclassified runtime modules: {missing}")
    if stale:
        raise SystemExit(f"context map references missing runtime modules: {stale}")

    packages = layout["runtime_target"]["packages"]
    for module, context in owner.items():
        if module.startswith("harness.") and not module.startswith(
            f"harness.{packages[context]}."
        ):
            raise SystemExit(f"canonical module {module} is outside {context}'s package")

    allowed = {
        name: set(context.get("may_depend_on", []) or [])
        for name, context in contexts.items()
    }
    published_boundaries: dict[tuple[str, str], dict[str, set[str]]] = {}
    for index, item in enumerate(spec.get("published_boundaries", []) or []):
        if not isinstance(item, dict):
            raise SystemExit(f"published boundary #{index + 1} must be a mapping")
        source_context = item.get("from_context")
        target_context = item.get("to_context")
        if source_context not in contexts or target_context not in contexts:
            raise SystemExit(
                f"published boundary #{index + 1} references unknown context"
            )
        if target_context not in allowed.get(source_context, set()):
            raise SystemExit(
                f"published boundary {source_context}->{target_context} is not "
                "an allowed context dependency"
            )
        key = (source_context, target_context)
        if key in published_boundaries:
            raise SystemExit(
                f"duplicate published boundary: {source_context}->{target_context}"
            )
        modules = item.get("modules")
        if not isinstance(modules, dict) or not modules:
            raise SystemExit(
                f"published boundary {source_context}->{target_context} requires modules"
            )
        normalized: dict[str, set[str]] = {}
        for module, symbols in modules.items():
            if owner.get(module) != target_context:
                raise SystemExit(
                    f"published boundary module {module} is not owned by {target_context}"
                )
            if not isinstance(symbols, list) or not symbols or any(
                not isinstance(symbol, str) or not symbol for symbol in symbols
            ):
                raise SystemExit(
                    f"published boundary {module} symbols must be a non-empty string list"
                )
            if len(symbols) != len(set(symbols)):
                raise SystemExit(f"published boundary {module} has duplicate symbols")
            normalized[module] = set(symbols)
        published_boundaries[key] = normalized
    shared = {
        module: set(names or [])
        for module, names in (spec.get("shared_kernel_imports", {}) or {}).items()
    }

    declared = {
        (item["from_module"], item["to_module"]): item
        for item in spec.get("known_violations", []) or []
    }
    actual_violations: set[tuple[str, str]] = set()
    published_boundary_violations: list[str] = []

    def resolve_target(module_name: str) -> str | None:
        return _resolve_target(module_name, owner, aliases)

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

        boundary = published_boundaries.get((source_context, target_context))
        if boundary is not None:
            allowed_symbols = boundary.get(target)
            if allowed_symbols is None:
                published_boundary_violations.append(
                    f"{source} ({source_context}) imports non-published module "
                    f"{target} ({target_context})"
                )
                return
            if imported_names is None:
                published_boundary_violations.append(
                    f"{source} ({source_context}) imports published module {target} "
                    "without an explicit symbol boundary"
                )
                return
            disallowed = sorted(imported_names - allowed_symbols)
            if disallowed:
                published_boundary_violations.append(
                    f"{source} ({source_context}) imports non-published symbols "
                    f"from {target}: {disallowed}"
                )
                return
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
                    prefix = package_parts[:len(package_parts) - node.level + 1]
                    module_name = ".".join(prefix + ([module_name] if module_name else []))
                names = {alias.name for alias in node.names}
                if resolve_target(module_name) is not None:
                    check_edge(source, module_name, names)
                else:
                    for alias in node.names:
                        check_edge(
                            source,
                            f"{module_name}.{alias.name}",
                            None,
                        )
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    check_edge(source, alias.name, None)

    declared_edges = set(declared)
    unknown = sorted(actual_violations - declared_edges)
    stale_exceptions = sorted(declared_edges - actual_violations)

    if published_boundary_violations:
        print("published cross-context contract violations:", file=sys.stderr)
        for violation in sorted(published_boundary_violations):
            print(f"- {violation}", file=sys.stderr)
        return 1

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
