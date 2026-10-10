#!/usr/bin/env python3
"""Contract tests for the four-file, read-only Capability graph exporter."""
from __future__ import annotations

import copy
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from harness.workspace.capability_graph_export import (
    FILENAMES, GraphExportError, dot_source, export, generate, reduced_edges, topology,
)


def fixture() -> dict:
    def authority(name, produced):
        return {
            "id": name, "responsibility": f"Produce {name} knowledge.",
            "boundary": {"semantic_cohesion": "Cohesive knowledge.",
                         "independent_change": "May change independently.",
                         "public_contract": "Expose accepted knowledge."},
            "produces": produced,
        }
    return {
        "version": 1, "kind": "harness-engineering-graph", "id": "GRAPH-EXPORT-TEST",
        "authorities": [
            authority("FIRST", [
                {"capability": "a", "requires": []},
                {"capability": "b", "requires": [{"capability": "a"}]},
            ]),
            authority("SECOND", [
                {"capability": "c", "requires": ["a", {"capability": "b"}]},
            ]),
        ],
        "consumers": [
            {"id": "READ", "purpose": "Show graph.",
             "requires": [{"capability": "c"}]},
        ],
    }


class CapabilityGraphExportTests(unittest.TestCase):
    def test_exact_direct_edges_and_authorities(self):
        owners, links = topology(fixture())
        self.assertEqual(owners, {"a": "FIRST", "b": "FIRST", "c": "SECOND"})
        self.assertEqual(links, (("a", "b"), ("a", "c"), ("b", "c")))
        self.assertEqual(reduced_edges(owners, links), (("a", "b"), ("b", "c")))

    def test_grouped_dot_and_warning_are_honest(self):
        owners, links = topology(fixture())
        full = dot_source(owners, links)
        overview = dot_source(owners, reduced_edges(owners, links), overview=True)
        self.assertIn("rankdir=TB;", full)
        self.assertEqual(full.count("subgraph cluster_"), 2)
        self.assertIn('label="FIRST";', full)
        self.assertIn('label="SECOND";', full)
        self.assertIn('"a" -> "c";', full)
        self.assertNotIn('"a" -> "c";', overview)
        self.assertIn("Reachability only", overview)

    def test_reordering_is_byte_identical(self):
        base = fixture()
        reversed_input = copy.deepcopy(base)
        reversed_input["authorities"].reverse()
        for authority in reversed_input["authorities"]:
            authority["produces"].reverse()
            for item in authority["produces"]:
                item["requires"].reverse()
        a, direct_a, reduced_a = generate(base)
        b, direct_b, reduced_b = generate(reversed_input)
        self.assertEqual((direct_a, reduced_a), (3, 2))
        self.assertEqual((direct_a, reduced_a), (direct_b, reduced_b))
        self.assertEqual(a, b)
        self.assertEqual(set(a), set(FILENAMES))
        self.assertTrue(all(a[name].startswith(b"<?xml") for name in FILENAMES if name.endswith(".svg")))

    def test_unknown_requirement_fails_closed(self):
        graph = fixture()
        graph["authorities"][1]["produces"][0]["requires"].append("missing")
        with self.assertRaisesRegex(GraphExportError, "unknown required capability"):
            topology(graph)

    def test_duplicate_requirement_and_cycle_rejected(self):
        graph = fixture()
        graph["authorities"][1]["produces"][0]["requires"].append("a")
        with self.assertRaisesRegex(GraphExportError, "duplicate direct"):
            topology(graph)
        graph = fixture()
        graph["authorities"][0]["produces"][0]["requires"] = ["c"]
        owners, links = topology(graph)
        with self.assertRaisesRegex(GraphExportError, "cycle"):
            reduced_edges(owners, links)

    def test_export_default_location_idempotent_and_check(self):
        with TemporaryDirectory() as temp:
            project = Path(temp)
            path = project / ".harness" / "engineering-graph.yaml"
            path.parent.mkdir()
            path.write_text(yaml.safe_dump(fixture()), encoding="utf-8")
            self.assertEqual(export(project), (3, 2, 4))
            directory = project / "docs" / "generated" / "harness-graphs"
            self.assertEqual(set(p.name for p in directory.iterdir()), set(FILENAMES))
            self.assertEqual(export(project), (3, 2, 0))
            self.assertEqual(export(project, check=True), (3, 2, 0))
            (directory / "capability-requires.dot").write_text("stale", encoding="utf-8")
            with self.assertRaisesRegex(GraphExportError, "stale or absent"):
                export(project, check=True)
            self.assertEqual(export(project), (3, 2, 1))


if __name__ == "__main__":
    unittest.main()
