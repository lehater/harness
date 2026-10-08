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
    current = {"A": ["a"], "B": ["b"], "C": ["c"]}
    assert compose_derivations([a, b], current_assertion_ids=current)["status"] == "ACCEPTED"
    assert compose_derivations([a, b], current_assertion_ids={"A": ["new-a"], "B": ["b"], "C": ["c"]})["findings"][0]["code"] == "STALE_LINK_IDS"
    assert compose_derivations([a, b], current_assertion_ids={"A": ["a"], "B": ["b"]})["findings"][0]["code"] == "CURRENT_SCOPE_MISSING"
    from harness.assurance.semantic_fingerprint import semantic_assertion_fingerprints
    sem_a = {"semantic_assertions": [{"id": "a", "kind": "requirement", "semantic_value": "old"}]}
    sem_b = {"semantic_assertions": [{"id": "b", "kind": "task", "semantic_value": "execute"}]}
    sem_c = {"semantic_assertions": [{"id": "c", "kind": "operation", "semantic_value": "show"}]}
    scopes = {"A": sem_a, "B": sem_b, "C": sem_c}
    fa, fb, fc = (semantic_assertion_fingerprints(scopes[k]) for k in ("A", "B", "C"))
    accepted_a = {**a, "assertion_fingerprints": {"source": fa, "target": fb}}
    accepted_b = {**b, "assertion_fingerprints": {"source": fb, "target": fc}}
    assert compose_derivations([accepted_a, accepted_b], current_semantics=scopes)["status"] == "ACCEPTED"
    mutated = {"A": {"semantic_assertions": [{"id": "a", "kind": "requirement", "semantic_value": "changed"}]}, "B": sem_b, "C": sem_c}
    assert compose_derivations([accepted_a, accepted_b], current_semantics=mutated)["findings"][0]["code"] == "SEMANTIC_FINGERPRINT_MISMATCH"
    assert compose_derivations([a, b], current_semantics=scopes)["findings"][0]["code"] == "ACCEPTED_FINGERPRINTS_MISSING"
    assert compose_derivations([accepted_a, accepted_b], current_semantics={"A": sem_a, "B": sem_b})["findings"][0]["code"] == "CURRENT_SEMANTICS_MISSING"
    print("Composition tests passed (12)")


if __name__ == "__main__":
    main()
