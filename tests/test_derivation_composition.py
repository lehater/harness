#!/usr/bin/env python3
"""Focused regression tests for compositional traceability."""
from harness.assurance.derivation_composition import compose_derivations


def main() -> None:
    a = {"status": "ACCEPTED", "source_capability": "A", "target_capability": "B",
         "links": [{"sources": ["a"], "targets": ["b"]}]}
    b = {"status": "ACCEPTED", "source_capability": "B", "target_capability": "C",
         "links": [{"sources": ["b"], "targets": ["c"]}]}
    assert compose_derivations([a, b])["links"] == [{"source": "a", "targets": ["c"]}]
    assert compose_derivations([a, {**b, "links": []}])["findings"][0]["code"] == "CHAIN_TRACE_LOST"
    assert compose_derivations([a, {**b, "status": "REJECTED"}])["findings"][0]["code"] == "DERIVATION_NOT_ACCEPTED"
    assert compose_derivations([a, {**b, "source_capability": "D"}])["findings"][0]["code"] == "CHAIN_DISCONNECTED"
    assert compose_derivations([{**a, "links": []}, b])["findings"][0]["code"] == "CHAIN_HAS_NO_SOURCE_LINKS"
    print("Composition tests passed (5)")


if __name__ == "__main__":
    main()
