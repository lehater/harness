from copy import deepcopy
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from semantic_acceptance_experiment import evaluate, coverage_proof_available


CASES = {
    "domain-model": {
        "contract": {
            "authority": "DOMAIN",
            "owned_assertion_kinds": ["concept", "responsibility", "invariant"],
            "semantic_claims": ["engineering.domain.model"],
            "obligations": [
                {"id": "concept-order", "kind": "concept", "subject": "Order"},
                {
                    "id": "responsibility-order",
                    "kind": "responsibility",
                    "subject": "Order",
                },
                {"id": "invariant-order", "kind": "invariant", "subject": "Order"},
            ],
        },
        "sources": {
            "semantic_assertions": [
                {
                    "id": "REQ-ORDER-1",
                    "kind": "invariant",
                    "subject": "Order",
                    "semantic_value": "number-unique",
                }
            ]
        },
        "candidate": {
            "id": "DOMAIN-MODEL",
            "capability": "domain.model",
            "semantic_assertions": [
                {
                    "id": "DM-1",
                    "kind": "concept",
                    "subject": "Order",
                    "semantic_value": "order",
                    "decision_authority": "DOMAIN",
                },
                {
                    "id": "DM-2",
                    "kind": "responsibility",
                    "subject": "Order",
                    "semantic_value": "owns-order-lifecycle",
                    "decision_authority": "DOMAIN",
                },
                {
                    "id": "DM-3",
                    "kind": "invariant",
                    "subject": "Order",
                    "semantic_value": "number-unique",
                    "derived_from": ["REQ-ORDER-1"],
                },
            ],
        },
        "claim": "engineering.domain.model",
    },
    "interface-contract": {
        "contract": {
            "authority": "INTERFACE",
            "owned_assertion_kinds": [
                "operation",
                "input",
                "output",
                "error",
                "compatibility",
            ],
            "semantic_claims": ["engineering.interface.machine.contract"],
            "obligations": [
                {
                    "id": "op-create",
                    "kind": "operation",
                    "subject": "CreateOrder",
                },
                {"id": "input-create", "kind": "input", "subject": "CreateOrder"},
                {
                    "id": "output-create",
                    "kind": "output",
                    "subject": "CreateOrder",
                },
                {"id": "error-create", "kind": "error", "subject": "CreateOrder"},
            ],
        },
        "sources": {
            "semantic_assertions": [
                {
                    "id": "APP-CREATE",
                    "kind": "operation",
                    "subject": "CreateOrder",
                    "semantic_value": "supported",
                },
                {
                    "id": "APP-ERR",
                    "kind": "error",
                    "subject": "CreateOrder",
                    "semantic_value": "duplicate-number-rejected",
                },
            ]
        },
        "candidate": {
            "id": "API",
            "capability": "interface.http",
            "semantic_assertions": [
                {
                    "id": "I-1",
                    "kind": "operation",
                    "subject": "CreateOrder",
                    "semantic_value": "supported",
                    "derived_from": ["APP-CREATE"],
                },
                {
                    "id": "I-2",
                    "kind": "input",
                    "subject": "CreateOrder",
                    "semantic_value": "order-number",
                    "decision_authority": "INTERFACE",
                },
                {
                    "id": "I-3",
                    "kind": "output",
                    "subject": "CreateOrder",
                    "semantic_value": "created-order",
                    "decision_authority": "INTERFACE",
                },
                {
                    "id": "I-4",
                    "kind": "error",
                    "subject": "CreateOrder",
                    "semantic_value": "duplicate-number-rejected",
                    "derived_from": ["APP-ERR"],
                },
            ],
        },
        "claim": "engineering.interface.machine.contract",
    },
    "test-design": {
        "contract": {
            "authority": "TEST-DESIGN",
            "owned_assertion_kinds": [
                "test-contract",
                "precondition",
                "operation",
                "oracle",
            ],
            "semantic_claims": ["engineering.verification.functional"],
            "obligations": [
                {
                    "id": "contract-v1",
                    "kind": "test-contract",
                    "subject": "VERIFY-CREATE",
                },
                {
                    "id": "pre-v1",
                    "kind": "precondition",
                    "subject": "VERIFY-CREATE",
                },
                {
                    "id": "op-v1",
                    "kind": "operation",
                    "subject": "VERIFY-CREATE",
                },
                {
                    "id": "oracle-v1",
                    "kind": "oracle",
                    "subject": "VERIFY-CREATE",
                },
            ],
        },
        "sources": {
            "semantic_assertions": [
                {
                    "id": "VERIFY-CREATE",
                    "kind": "oracle",
                    "subject": "VERIFY-CREATE",
                    "semantic_value": "created-order-observable",
                }
            ]
        },
        "candidate": {
            "id": "TEST-DESIGN",
            "capability": "test.design",
            "semantic_assertions": [
                {
                    "id": "T-1",
                    "kind": "test-contract",
                    "subject": "VERIFY-CREATE",
                    "semantic_value": "create-order",
                    "decision_authority": "TEST-DESIGN",
                },
                {
                    "id": "T-2",
                    "kind": "precondition",
                    "subject": "VERIFY-CREATE",
                    "semantic_value": "number-unused",
                    "decision_authority": "TEST-DESIGN",
                },
                {
                    "id": "T-3",
                    "kind": "operation",
                    "subject": "VERIFY-CREATE",
                    "semantic_value": "submit-create",
                    "decision_authority": "TEST-DESIGN",
                },
                {
                    "id": "T-4",
                    "kind": "oracle",
                    "subject": "VERIFY-CREATE",
                    "semantic_value": "created-order-observable",
                    "derived_from": ["VERIFY-CREATE"],
                },
            ],
        },
        "claim": "engineering.verification.functional",
    },
}


def codes(result):
    return {item["code"] for item in result["findings"]}


def main() -> int:
    total = 0
    for name, fixture in CASES.items():
        baseline = evaluate(
            fixture["contract"], fixture["sources"], fixture["candidate"]
        )
        total += 1
        assert baseline["status"] == "ACCEPTED", (name, baseline)

        total += 1
        assert coverage_proof_available(
            fixture["contract"]["semantic_claims"],
            baseline,
            fixture["claim"],
        )

        candidate = deepcopy(fixture["candidate"])
        candidate["semantic_assertions"] = candidate["semantic_assertions"][:-1]
        result = evaluate(fixture["contract"], fixture["sources"], candidate)
        total += 1
        assert result["status"] == "REJECTED"
        assert {
            "MISSING_OBLIGATION",
            "MISSING_SUBJECTS",
        } & codes(result)

        total += 1
        assert not coverage_proof_available(
            fixture["contract"]["semantic_claims"],
            result,
            fixture["claim"],
        )

        candidate = deepcopy(fixture["candidate"])
        target = next(
            item
            for item in candidate["semantic_assertions"]
            if item.get("derived_from")
        )
        target["semantic_value"] = "CONTRADICTED"
        result = evaluate(fixture["contract"], fixture["sources"], candidate)
        total += 1
        assert "SOURCE_FIDELITY_VIOLATION" in codes(result), (name, result)

        candidate = deepcopy(fixture["candidate"])
        candidate["semantic_assertions"].append(
            {
                "id": "INV",
                "kind": fixture["contract"]["owned_assertion_kinds"][0],
                "subject": "Extra",
                "semantic_value": "invented",
            }
        )
        result = evaluate(fixture["contract"], fixture["sources"], candidate)
        total += 1
        assert "INVENTED_ASSERTION" in codes(result), (name, result)

        candidate = deepcopy(fixture["candidate"])
        candidate["semantic_assertions"].append(
            {
                "id": "OWN",
                "kind": "foreign-rule",
                "subject": "X",
                "semantic_value": "x",
                "decision_authority": fixture["contract"]["authority"],
            }
        )
        result = evaluate(fixture["contract"], fixture["sources"], candidate)
        total += 1
        assert "WRONG_AUTHORITY_OWNERSHIP" in codes(result), (name, result)

        contract = deepcopy(fixture["contract"])
        contract["obligations"].append(
            {
                "id": "all-subjects",
                "kind": fixture["contract"]["owned_assertion_kinds"][0],
                "subjects": ["S1", "S2"],
            }
        )
        candidate = deepcopy(fixture["candidate"])
        candidate["semantic_assertions"].append(
            {
                "id": "S1",
                "kind": fixture["contract"]["owned_assertion_kinds"][0],
                "subject": "S1",
                "semantic_value": "x",
                "decision_authority": fixture["contract"]["authority"],
            }
        )
        result = evaluate(contract, fixture["sources"], candidate)
        total += 1
        assert "MISSING_SUBJECTS" in codes(result), (name, result)

        candidate = deepcopy(fixture["candidate"])
        target = next(
            item
            for item in candidate["semantic_assertions"]
            if item.get("derived_from")
        )
        target["derived_from"] = ["UNKNOWN-SOURCE"]
        result = evaluate(fixture["contract"], fixture["sources"], candidate)
        total += 1
        assert "UNKNOWN_PROVENANCE" in codes(result), (name, result)

        candidate = deepcopy(fixture["candidate"])
        first = candidate["semantic_assertions"][0]
        candidate["semantic_assertions"].append(
            {
                "id": "DUP",
                "kind": first["kind"],
                "subject": first.get("subject"),
                "semantic_value": "DIFFERENT",
                "decision_authority": fixture["contract"]["authority"],
            }
        )
        result = evaluate(fixture["contract"], fixture["sources"], candidate)
        total += 1
        assert "INTERNAL_CONTRADICTION" in codes(result), (name, result)

        source = fixture["sources"]["semantic_assertions"][0]
        candidate = deepcopy(fixture["candidate"])
        candidate["semantic_assertions"].append(
            {
                "id": "CROSS",
                "kind": source["kind"],
                "subject": source.get("subject"),
                "semantic_value": "DIFFERENT",
                "decision_authority": fixture["contract"]["authority"],
            }
        )
        result = evaluate(fixture["contract"], fixture["sources"], candidate)
        total += 1
        assert "CROSS_ARTIFACT_CONTRADICTION" in codes(result), (name, result)

    print(
        f"PASS {total} assertions across {len(CASES)} artifact kinds"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
