#!/usr/bin/env python3
"""Export two Authority-grouped Capability dependency diagrams from Engineering Graph.

The full diagram retains every direct production `requires`; the optional
reachability-only diagram is NOT a substitute for those direct requirements.
Only four reproducible DOT/SVG files are emitted, never a new source of truth.
"""
from __future__ import annotations

import argparse
from collections import deque
import json
from pathlib import Path
import subprocess
import sys
from typing import Any

import yaml

FILENAMES = (
    "capability-requires.dot",
    "capability-requires.svg",
    "capability-requires-reachability-only.dot",
    "capability-requires-reachability-only.svg",
)


class GraphExportError(ValueError):
    """The requested projection cannot be exported faithfully."""


def topology(graph: dict[str, Any]) -> tuple[dict[str, str], tuple[tuple[str, str], ...]]:
    """Read only explicitly declared direct production requirements."""
    owners: dict[str, str] = {}
    links: list[tuple[str, str]] = []
    authorities = graph.get("authorities")
    if not isinstance(authorities, list):
        raise GraphExportError("engineering graph authorities must be a list")
    seen_authorities: set[str] = set()
    for authority in authorities:
        if not isinstance(authority, dict):
            raise GraphExportError("authority must be a mapping")
        name = authority.get("id")
        if not isinstance(name, str) or not name or name in seen_authorities:
            raise GraphExportError(f"missing or duplicated authority: {name!r}")
        seen_authorities.add(name)
        productions = authority.get("produces", []) or []
        if not isinstance(productions, list):
            raise GraphExportError(f"authority {name} produces must be a list")
        for item in productions:
            production = {"capability": item, "requires": []} if isinstance(item, str) else item
            if not isinstance(production, dict):
                raise GraphExportError(f"invalid production in authority {name}")
            capability = production.get("capability")
            if not isinstance(capability, str) or not capability or capability in owners:
                raise GraphExportError(f"missing or duplicated capability: {capability!r}")
            owners[capability] = name
            requires = production.get("requires", []) or []
            if not isinstance(requires, list):
                raise GraphExportError(f"invalid requires for {capability}")
            for requirement in requires:
                source = (requirement if isinstance(requirement, str) else
                          requirement.get("capability") if isinstance(requirement, dict) else None)
                if not isinstance(source, str) or not source:
                    raise GraphExportError(f"invalid upstream capability in {capability}")
                links.append((source, capability))
    if not owners:
        raise GraphExportError("engineering graph has no produced Capabilities")
    if len(links) != len(set(links)):
        raise GraphExportError("duplicate direct production requires")
    for source, target in links:
        if source not in owners:
            raise GraphExportError(f"unknown required capability {source} for {target}")
        if source == target:
            raise GraphExportError(f"self dependency: {source}")
    return owners, tuple(sorted(links))


def _alternate_path(adjacency: dict[str, tuple[str, ...]], source: str,
                    target: str, forbidden: tuple[str, str]) -> bool:
    queue = deque([source])
    seen = {source}
    while queue:
        current = queue.popleft()
        for next_node in adjacency[current]:
            if (current, next_node) == forbidden:
                continue
            if next_node == target:
                return True
            if next_node not in seen:
                seen.add(next_node)
                queue.append(next_node)
    return False


def reduced_edges(owners: dict[str, str],
                  links: tuple[tuple[str, str], ...]) -> tuple[tuple[str, str], ...]:
    """Transitive reduction for a DAG; no claim about semantic dispensability."""
    successors: dict[str, set[str]] = {cap: set() for cap in owners}
    indegree = {cap: 0 for cap in owners}
    for source, target in links:
        successors[source].add(target)
        indegree[target] += 1
    # Refuse cycles: reachability reduction of a cyclic graph is not unique.
    pending = deque(sorted(cap for cap, d in indegree.items() if d == 0))
    visited = 0
    while pending:
        current = pending.popleft()
        visited += 1
        for target in sorted(successors[current]):
            indegree[target] -= 1
            if indegree[target] == 0:
                pending.append(target)
    if visited != len(owners):
        raise GraphExportError("production requirements contain a cycle")
    adjacency = {cap: tuple(sorted(targets)) for cap, targets in successors.items()}
    return tuple((source, target) for source, target in links
                 if not _alternate_path(adjacency, source, target, (source, target)))


def dot_source(owners: dict[str, str], links: tuple[tuple[str, str], ...],
               *, overview: bool = False) -> str:
    """Stable DOT, with one Graphviz cluster per Authority."""
    q = lambda s: json.dumps(s, ensure_ascii=False)
    lines = ["// Generated read-only; not a source of truth.",
             "digraph HarnessProjection {", "  rankdir=TB;",
             "  graph [compound=true, newrank=true, nodesep=0.3, ranksep=0.65];",
             "  node [shape=box, style=rounded];"]
    if overview:
        lines.extend(['  label="Reachability only: some direct requires deliberately hidden";',
                      "  labelloc=t;"])
    prefixes = {cap.split(".", 1)[0] for cap in owners if "." in cap}
    prefix = (next(iter(prefixes)) + "." if len(prefixes) == 1 and
              all(cap.startswith(next(iter(prefixes)) + ".") for cap in owners) else "")
    for index, authority in enumerate(sorted(set(owners.values()))):
        lines.extend([f"  subgraph cluster_{index} {{", f"    label={q(authority)};",
                      '    style="rounded";', '    color="#9aa8b7";'])
        for cap in sorted(cap for cap, owner in owners.items() if owner == authority):
            label = cap.removeprefix(prefix)
            lines.append(f"    {q(cap)} [label={q(label)}];")
        lines.append("  }")
    for source, target in links:
        lines.append(f"  {q(source)} -> {q(target)};")
    return "\n".join(lines + ["}", ""])


def render_svg(dot: str) -> bytes:
    try:
        completed = subprocess.run(
            ["dot", "-Tsvg"], input=dot.encode("utf-8"), capture_output=True,
            check=True,
        )
    except FileNotFoundError as exc:
        raise GraphExportError("Graphviz `dot` is not installed") from exc
    except subprocess.CalledProcessError as exc:
        raise GraphExportError(f"Graphviz rendering failed: {exc.stderr.decode(errors='replace')}") from exc
    return completed.stdout


def generate(graph: dict[str, Any]) -> tuple[dict[str, bytes], int, int]:
    owners, links = topology(graph)
    overview = reduced_edges(owners, links)
    dot_full = dot_source(owners, links)
    dot_overview = dot_source(owners, overview, overview=True)
    files = {
        "capability-requires.dot": dot_full.encode("utf-8"),
        "capability-requires.svg": render_svg(dot_full),
        "capability-requires-reachability-only.dot": dot_overview.encode("utf-8"),
        "capability-requires-reachability-only.svg": render_svg(dot_overview),
    }
    return files, len(links), len(overview)


def export(project: Path, *, check: bool = False) -> tuple[int, int, int]:
    from harness.project_model.engineering_graph import validate_engineering_graph

    project = project.resolve()
    path = project / ".harness" / "engineering-graph.yaml"
    try:
        graph = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise GraphExportError(f"cannot read engineering graph {path}: {exc}") from exc
    if not isinstance(graph, dict):
        raise GraphExportError("engineering graph must be a YAML mapping")
    validate_engineering_graph(graph)
    files, direct, overview = generate(graph)
    output_dir = project / "docs" / "generated" / "harness-graphs"
    if check:
        stale = [name for name, contents in files.items()
                 if not (output_dir / name).exists() or (output_dir / name).read_bytes() != contents]
        if stale:
            raise GraphExportError(f"stale or absent graph outputs: {', '.join(stale)}")
        return direct, overview, 0
    output_dir.mkdir(parents=True, exist_ok=True)
    changed = 0
    for name in FILENAMES:
        target = output_dir / name
        if not target.exists() or target.read_bytes() != files[name]:
            target.write_bytes(files[name])
            changed += 1
    return direct, overview, changed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, default=Path("."),
                        help="Project root containing .harness/engineering-graph.yaml")
    parser.add_argument("--check", action="store_true",
                        help="Check tracked DOT/SVG freshness without writing files")
    args = parser.parse_args(argv)
    try:
        direct, overview, changed = export(args.project, check=args.check)
    except (GraphExportError, ValueError) as exc:
        parser.error(str(exc))
    print(f"Capabilities graph: {direct} direct requires; {overview} overview edges; "
          f"{changed} files updated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
