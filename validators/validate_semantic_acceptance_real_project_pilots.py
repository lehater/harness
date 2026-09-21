from copy import deepcopy
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from semantic_acceptance_experiment import evaluate, coverage_proof_available


def codes(result):
    return {item["code"] for item in result["findings"]}


def nutrition_pilot():
    contract = {
        "authority": "TEST-DESIGN",
        "owned_assertion_kinds": ["test-contract", "precondition", "operation", "oracle"],
        # Current Nutrition semantic-claim bindings intentionally do not bind
        # broad Test Design capabilities to Coverage concerns.
        "semantic_claims": [],
        "obligations": [
            {"id": "nt", "kind": "test-contract", "subject": "TD-NT-01"},
            {"id": "fk", "kind": "test-contract", "subject": "TD-FK-01"},
            {"id": "mc", "kind": "test-contract", "subject": "TD-MC-01"},
            {"id": "pp", "kind": "test-contract", "subject": "TD-PP-03"},
            {"id": "arch", "kind": "test-contract", "subject": "TD-ARCH-01"},
            {"id": "persist", "kind": "test-contract", "subject": "TD-PERSIST-01"},
            {"id": "cli", "kind": "test-contract", "subject": "TD-CLI-03"},
        ],
    }
    sources = {
        "semantic_assertions": [
            {"id": "VER-NT", "kind": "oracle", "subject": "TD-NT-01", "semantic_value": "deterministic-derivation"},
            {"id": "VER-FK", "kind": "oracle", "subject": "TD-FK-01", "semantic_value": "evidence-state-preserved"},
            {"id": "VER-MC", "kind": "oracle", "subject": "TD-MC-01", "semantic_value": "explicit-as-of"},
            {"id": "VER-PP", "kind": "oracle", "subject": "TD-PP-03", "semantic_value": "infeasible-vs-technical"},
            {"id": "VER-ARCH", "kind": "oracle", "subject": "TD-ARCH-01", "semantic_value": "dependency-boundary"},
            {"id": "VER-PERSIST", "kind": "oracle", "subject": "TD-PERSIST-01", "semantic_value": "semantic-roundtrip"},
            {"id": "VER-CLI", "kind": "oracle", "subject": "TD-CLI-03", "semantic_value": "technical-vs-domain"},
        ]
    }
    candidate = {
        "id": "REDESIGN-TEST-DESIGN",
        "capability": "nutrition-management.redesign.test-design",
        "semantic_assertions": [
            {"id": "TD-NT-01", "kind": "test-contract", "subject": "TD-NT-01", "semantic_value": "deterministic-derivation", "decision_authority": "TEST-DESIGN"},
            {"id": "TD-FK-01", "kind": "test-contract", "subject": "TD-FK-01", "semantic_value": "evidence-state-preserved", "decision_authority": "TEST-DESIGN"},
            {"id": "TD-MC-01", "kind": "test-contract", "subject": "TD-MC-01", "semantic_value": "explicit-as-of", "decision_authority": "TEST-DESIGN"},
            {"id": "TD-PP-03", "kind": "test-contract", "subject": "TD-PP-03", "semantic_value": "infeasible-vs-technical", "decision_authority": "TEST-DESIGN"},
            {"id": "TD-ARCH-01", "kind": "test-contract", "subject": "TD-ARCH-01", "semantic_value": "dependency-boundary", "decision_authority": "TEST-DESIGN"},
            {"id": "TD-PERSIST-01", "kind": "test-contract", "subject": "TD-PERSIST-01", "semantic_value": "semantic-roundtrip", "decision_authority": "TEST-DESIGN"},
            {"id": "TD-CLI-03", "kind": "test-contract", "subject": "TD-CLI-03", "semantic_value": "technical-vs-domain", "decision_authority": "TEST-DESIGN"},
        ],
    }

    baseline = evaluate(contract, sources, candidate)
    assert baseline["status"] == "ACCEPTED", baseline
    assert baseline["semantic_claims"]["accepted"] == []

    missing = deepcopy(candidate)
    missing["semantic_assertions"] = missing["semantic_assertions"][:-1]
    rejected = evaluate(contract, sources, missing)
    assert rejected["status"] == "REJECTED", rejected
    assert "MISSING_OBLIGATION" in codes(rejected)

    # No current semantic claim binding means acceptance does not manufacture
    # Coverage proof.
    assert not coverage_proof_available([], baseline, "engineering.verification.functional")
    return 4


def napms_pilot():
    claims = [
        "engineering.interface.machine.contract",
        "engineering.interface.machine.errors",
        "engineering.interface.machine.compatibility",
    ]
    contract = {
        "authority": "INTERFACE-DESIGN",
        "owned_assertion_kinds": ["operation", "input", "output", "error", "compatibility"],
        "semantic_claims": claims,
        "obligations": [
            {"id": "materialize-op", "kind": "operation", "subject": "materializeCurrentPolicy"},
            {"id": "materialize-input", "kind": "input", "subject": "materializeCurrentPolicy"},
            {"id": "materialize-output", "kind": "output", "subject": "materializeCurrentPolicy"},
            {"id": "materialize-error", "kind": "error", "subject": "materializeCurrentPolicy"},
            {"id": "access-op", "kind": "operation", "subject": "submitAccessRequest"},
            {"id": "access-error", "kind": "error", "subject": "submitAccessRequest"},
        ],
    }
    sources = {
        "semantic_assertions": [
            {"id": "HTTP-REQ-MAT", "kind": "operation", "subject": "materializeCurrentPolicy", "semantic_value": "supported"},
            {"id": "HTTP-REQ-ACCESS", "kind": "operation", "subject": "submitAccessRequest", "semantic_value": "supported"},
        ]
    }
    candidate = {
        "id": "OPENAPI",
        "capability": "engineering.interface.http-contract",
        "semantic_assertions": [
            {"id": "N1", "kind": "operation", "subject": "materializeCurrentPolicy", "semantic_value": "supported", "derived_from": ["HTTP-REQ-MAT"]},
            {"id": "N2", "kind": "input", "subject": "materializeCurrentPolicy", "semantic_value": "PolicyMaterializationRequest", "decision_authority": "INTERFACE-DESIGN"},
            {"id": "N3", "kind": "output", "subject": "materializeCurrentPolicy", "semantic_value": "PolicyMaterializationResult COMPLETE|UNRESOLVED", "decision_authority": "INTERFACE-DESIGN"},
            {"id": "N4", "kind": "error", "subject": "materializeCurrentPolicy", "semantic_value": "401|403|422|503", "decision_authority": "INTERFACE-DESIGN"},
            {"id": "N5", "kind": "operation", "subject": "submitAccessRequest", "semantic_value": "supported", "derived_from": ["HTTP-REQ-ACCESS"]},
            {"id": "N6", "kind": "error", "subject": "submitAccessRequest", "semantic_value": "401|403|409|422|503", "decision_authority": "INTERFACE-DESIGN"},
        ],
    }

    baseline = evaluate(contract, sources, candidate)
    assert baseline["status"] == "ACCEPTED", baseline
    for claim in claims:
        assert coverage_proof_available(claims, baseline, claim)

    contradiction = deepcopy(candidate)
    contradiction["semantic_assertions"][0]["semantic_value"] = "unsupported"
    rejected = evaluate(contract, sources, contradiction)
    assert rejected["status"] == "REJECTED", rejected
    assert "SOURCE_FIDELITY_VIOLATION" in codes(rejected)
    for claim in claims:
        assert not coverage_proof_available(claims, rejected, claim)
    return 8


def main():
    total = nutrition_pilot() + napms_pilot()
    print(f"PASS {total} real-project pilot assertions across Nutrition and NAPMS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
