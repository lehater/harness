#!/usr/bin/env python3
"""Regression: Checker source decisions must not be promoted into test requirements."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from harness.assurance.semantic_acceptance import evaluate_artifact


def check(candidate):
    contract = {
        "authority": "PRODUCT-REQUIREMENTS",
        "owned_assertion_kinds": ["product-requirement"],
        "allowed_source_authorities": ["PRODUCT-REQUIREMENTS"],
        "requires_assertion_authority": True,
        "requires_semantic_review": True,
        "required_semantic_review_checks": ["product-requirement-boundary-review"],
    }
    return evaluate_artifact(contract, {"semantic_assertions": []}, candidate)


def fixture():
    a = lambda id, value: {
        "id": id, "kind": "product-requirement", "subject": id,
        "semantic_value": value, "decision_authority": "PRODUCT-REQUIREMENTS",
    }
    return {
        "id": "CHECKER-REQUIREMENTS", "capability": "checker.requirements",
        "semantic_assertions": [
            a("REQ-FLOW", "Accept one IPv4 TCP/UDP flow with both addresses and ports."),
            a("REQ-PROVENANCE", "Expose origin, date, completeness and unknowns."),
        ],
        "semantic_review": {
            "status": "ACCEPTED", "checks": ["product-requirement-boundary-review"],
            "requirement_classifications": [
                {"assertion": "REQ-FLOW", "role": "PRODUCT_BEHAVIOR", "obligation": "flow-input-contract",
                 "rationale": "All addresses, protocol and ports form one input contract."},
                {"assertion": "REQ-PROVENANCE", "role": "PRODUCT_BEHAVIOR", "obligation": "source-credibility-contract",
                 "rationale": "Metadata and unknown values form one observable result obligation."},
            ],
            "source_dispositions": [
                {"source": "PDEC-004-flow", "disposition": "PRODUCT_REQUIREMENT",
                 "assertions": ["REQ-FLOW"], "rationale": "One supported input contract."},
                {"source": "PDEC-004-metadata", "disposition": "PRODUCT_REQUIREMENT",
                 "assertions": ["REQ-PROVENANCE"], "rationale": "One provenance result contract."},
                {"source": "PDEC-004-independent-examples", "disposition": "VERIFICATION_OBLIGATION",
                 "assertions": [], "rationale": "Test oracle obligation belongs to Verification Design."},
                {"source": "PDEC-004-no-mandatory-verdict", "disposition": "NON_GOAL",
                 "assertions": [], "rationale": "Absence of universal verdict is a scope boundary."},
            ],
        },
    }


def main():
    import copy
    valid = fixture()
    assert check(valid)["status"] == "ACCEPTED"
    bad = copy.deepcopy(valid)
    bad["semantic_review"]["requirement_classifications"].append({
        "assertion": "REQ-028", "role": "VERIFICATION_OBLIGATION",
        "obligation": "independent-oracle", "rationale": "Should not be product.",
    })
    bad["semantic_assertions"].append({
        "id": "REQ-028", "kind": "product-requirement", "subject": "REQ-028",
        "semantic_value": "Verify ACL matching with independent test examples.",
        "decision_authority": "PRODUCT-REQUIREMENTS",
    })
    result = check(bad)
    assert result["status"] == "REJECTED"
    assert any(x["code"] == "INVALID_PRODUCT_REQUIREMENT_CLASSIFICATION" for x in result["findings"])
    split = copy.deepcopy(valid)
    split["semantic_assertions"].append({
        "id": "REQ-PORT", "kind": "product-requirement", "subject": "REQ-PORT",
        "semantic_value": "Support source port.", "decision_authority": "PRODUCT-REQUIREMENTS",
    })
    split["semantic_review"]["requirement_classifications"].append({
        "assertion": "REQ-PORT", "role": "PRODUCT_BEHAVIOR",
        "obligation": "flow-input-contract", "rationale": "Port is a field of same input."})
    split["semantic_review"]["source_dispositions"][0]["assertions"].append("REQ-PORT")
    result = check(split)
    assert result["status"] == "REJECTED"
    assert any(x["code"] == "PRODUCT_REQUIREMENT_FRAGMENTED_OBLIGATION" for x in result["findings"])
    missing = copy.deepcopy(valid)
    missing["semantic_review"].pop("source_dispositions")
    assert check(missing)["status"] == "REJECTED"
    promoted = copy.deepcopy(valid)
    promoted["semantic_review"]["source_dispositions"][2]["assertions"] = ["REQ-FLOW"]
    assert any(x["code"] == "NONPRODUCT_SOURCE_PROMOTED" for x in check(promoted)["findings"])
    print("product requirement boundary review: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
