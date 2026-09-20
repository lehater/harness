import unittest

from lifecycle_experiment import evaluate_lifecycle_target


GRAPH = {
    "version": 1,
    "kind": "harness-engineering-graph",
    "id": "LIFECYCLE",
    "authorities": [
        {
            "id": "PRODUCT",
            "responsibility": "Own product truth.",
            "boundary": {
                "semantic_cohesion": "Product decisions.",
                "independent_change": "Product can change independently.",
                "public_contract": "Accepted requirements.",
            },
            "produces": [{"capability": "p.requirements", "requires": []}],
        },
        {
            "id": "ARCH",
            "responsibility": "Own architecture.",
            "boundary": {
                "semantic_cohesion": "Architecture decisions.",
                "independent_change": "Architecture can change independently.",
                "public_contract": "Accepted architecture.",
            },
            "produces": [{
                "capability": "p.architecture",
                "requires": ["p.requirements"],
            }],
        },
        {
            "id": "INTERFACE",
            "responsibility": "Own interface.",
            "boundary": {
                "semantic_cohesion": "Interface decisions.",
                "independent_change": "Interface can change independently.",
                "public_contract": "Accepted interface.",
            },
            "produces": [{
                "capability": "p.interface",
                "requires": ["p.architecture"],
            }],
        },
    ],
    "consumers": [{
        "id": "IMPLEMENTATION",
        "purpose": "Implement accepted design.",
        "requires": ["p.interface"],
    }],
}


def model(product_revision="R1", arch_baseline="R1", arch_revision="A1", interface_baseline="A1"):
    return {
        "artifacts": [
            {
                "id": "PRODUCT",
                "authority": "PRODUCT",
                "path": "product.md",
                "provides": ["p.requirements"],
                "depends_on": [],
                "revision": product_revision,
                "accepted_prerequisites": {},
            },
            {
                "id": "ARCH",
                "authority": "ARCH",
                "path": "architecture.md",
                "provides": ["p.architecture"],
                "depends_on": ["PRODUCT"],
                "revision": arch_revision,
                "accepted_prerequisites": {"p.requirements": arch_baseline},
            },
            {
                "id": "INTERFACE",
                "authority": "INTERFACE",
                "path": "interface.md",
                "provides": ["p.interface"],
                "depends_on": ["ARCH"],
                "revision": "I1",
                "accepted_prerequisites": {"p.architecture": interface_baseline},
            },
        ],
        "questions": [],
    }


class LifecycleExperimentTest(unittest.TestCase):
    def test_current_chain_is_complete(self):
        result = evaluate_lifecycle_target(GRAPH, "IMPLEMENTATION", model())
        self.assertEqual("COMPLETE", result["status"])
        self.assertEqual([], result["revalidate"])

    def test_upstream_supersession_makes_direct_downstream_revalidate(self):
        result = evaluate_lifecycle_target(
            GRAPH, "IMPLEMENTATION", model(product_revision="R2")
        )
        self.assertEqual("READY", result["status"])
        self.assertEqual("p.architecture", result["revalidate"][0]["capability"])
        pending = {item["capability"] for item in result["pending"]}
        self.assertIn("p.interface", pending)

    def test_explicit_revalidation_advances_frontier(self):
        result = evaluate_lifecycle_target(
            GRAPH,
            "IMPLEMENTATION",
            model(product_revision="R2", arch_baseline="R2", arch_revision="A2"),
        )
        self.assertEqual("READY", result["status"])
        self.assertEqual("p.interface", result["revalidate"][0]["capability"])

    def test_full_revalidation_restores_complete(self):
        result = evaluate_lifecycle_target(
            GRAPH,
            "IMPLEMENTATION",
            model(
                product_revision="R2",
                arch_baseline="R2",
                arch_revision="A2",
                interface_baseline="A2",
            ),
        )
        self.assertEqual("COMPLETE", result["status"])


if __name__ == "__main__":
    unittest.main()
