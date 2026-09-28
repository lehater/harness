#!/usr/bin/env python3
"""Semantic derivation coverage between accepted upstream and downstream knowledge."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml

from engineering_graph import producer_index, production_index
from harness import CoreError

RELATIONS = {"PRESERVES", "TRANSFORMS", "CONSTRAINS", "REALIZES"}
DISPOSITIONS = {"NOT_APPLICABLE", "QUESTION"}


def _index_assertions(document: dict[str, Any], where: str) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for item in document.get("semantic_assertions", []) or []:
        if not isinstance(item, dict):
            raise CoreError(f"{where} semantic assertion must be a mapping")
        assertion_id = item.get("id")
        if not isinstance(assertion_id, str) or not assertion_id:
            raise CoreError(f"{where} semantic assertion requires id")
        if assertion_id in result:
            raise CoreError(f"duplicate {where} semantic assertion: {assertion_id}")
        result[assertion_id] = item
    return result


def _require_string(value: Any, where: str) -> str:
    if not isinstance(value, str) or not value:
        raise CoreError(f"{where} must be a non-empty string")
    return value


def _required_capabilities(production: dict[str, Any]) -> set[str]:
    result: set[str] = set()
    for item in production.get("requires", []) or []:
        if isinstance(item, str):
            result.add(item)
        elif isinstance(item, dict) and isinstance(item.get("capability"), str):
            result.add(item["capability"])
    return result


def evaluate_derivation(
    *,
    graph: dict[str, Any],
    contract: dict[str, Any],
    source: dict[str, Any],
    candidate: dict[str, Any],
    evidence: dict[str, Any] | None,
) -> dict[str, Any]:
    """Evaluate one direct Capability derivation edge.

    The evaluator answers two separate questions:
    1. Is the declared upstream semantic surface sufficient for this edge?
    2. Did the downstream candidate account for every applicable upstream atom?

    It deliberately does not judge whether an arbitrary natural-language
    transformation is semantically correct; that remains evaluator/human evidence
    when deterministic traceability is insufficient.
    """
    if contract.get("version") != 1:
        raise CoreError("semantic derivation contract version must be 1")
    if contract.get("kind") != "harness-semantic-derivation-contract":
        raise CoreError("unexpected semantic derivation contract kind")

    source_capability = _require_string(
        contract.get("source_capability"),
        "semantic derivation source_capability",
    )
    target_capability = _require_string(
        contract.get("target_capability"),
        "semantic derivation target_capability",
    )

    producers = producer_index(graph)
    productions = production_index(graph)
    if source_capability not in productions:
        raise CoreError(f"unknown derivation source capability: {source_capability}")
    if target_capability not in productions:
        raise CoreError(f"unknown derivation target capability: {target_capability}")
    if source_capability not in _required_capabilities(productions[target_capability]):
        raise CoreError(
            f"semantic derivation edge is not a direct production dependency: "
            f"{source_capability} -> {target_capability}"
        )

    source_authority = producers[source_capability]
    target_authority = producers[target_capability]
    source_assertions = _index_assertions(source, "source")
    target_assertions = _index_assertions(candidate, "candidate")

    findings: list[dict[str, Any]] = []
    required_sources: set[str] = set()
    source_obligation: dict[str, str] = {}

    obligations = contract.get("obligations", []) or []
    if not isinstance(obligations, list) or not obligations:
        raise CoreError("semantic derivation contract requires obligations")

    seen_obligations: set[str] = set()
    for item in obligations:
        if not isinstance(item, dict):
            raise CoreError("semantic derivation obligation must be a mapping")
        obligation_id = _require_string(
            item.get("id"),
            "semantic derivation obligation id",
        )
        if obligation_id in seen_obligations:
            raise CoreError(f"duplicate semantic derivation obligation: {obligation_id}")
        seen_obligations.add(obligation_id)
        source_kind = _require_string(
            item.get("source_kind"),
            f"semantic derivation obligation {obligation_id} source_kind",
        )
        minimum = item.get("min_count", 1)
        if not isinstance(minimum, int) or minimum < 0:
            raise CoreError(
                f"semantic derivation obligation {obligation_id} min_count "
                "must be a non-negative integer"
            )

        matches = [
            assertion
            for assertion in source_assertions.values()
            if assertion.get("kind") == source_kind
        ]
        subject = item.get("subject")
        if subject is not None:
            matches = [assertion for assertion in matches if assertion.get("subject") == subject]

        if len(matches) < minimum:
            findings.append(
                {
                    "code": "MISSING_REQUIRED_INPUT",
                    "obligation": obligation_id,
                    "source_kind": source_kind,
                    "required": minimum,
                    "actual": len(matches),
                    "source_capability": source_capability,
                    "required_by": target_capability,
                    "owner_authority": source_authority,
                }
            )

        for assertion in matches:
            assertion_id = assertion["id"]
            required_sources.add(assertion_id)
            source_obligation[assertion_id] = obligation_id

    evidence_valid = (
        isinstance(evidence, dict)
        and evidence.get("version") == 1
        and evidence.get("kind") == "harness-semantic-derivation-evidence"
        and evidence.get("source_capability") == source_capability
        and evidence.get("target_capability") == target_capability
    )
    if not evidence_valid:
        findings.append({"code": "DERIVATION_EVIDENCE_REQUIRED"})
        evidence = {}

    allowed_relations = set(contract.get("allowed_relations", []) or RELATIONS)
    unknown_relations = sorted(allowed_relations - RELATIONS)
    if unknown_relations:
        raise CoreError(
            f"semantic derivation contract has unknown relations: {unknown_relations}"
        )

    covered_sources: set[str] = set()
    evaluated_links: list[dict[str, Any]] = []
    links = evidence.get("links", []) or []
    if not isinstance(links, list):
        findings.append({"code": "INVALID_DERIVATION_LINKS"})
        links = []

    for index, link in enumerate(links):
        if not isinstance(link, dict):
            findings.append({"code": "INVALID_DERIVATION_LINK", "index": index})
            continue
        relation = link.get("relation")
        sources = link.get("sources", []) or []
        targets = link.get("targets", []) or []
        if relation not in allowed_relations:
            findings.append(
                {
                    "code": "INVALID_DERIVATION_RELATION",
                    "index": index,
                    "relation": relation,
                }
            )
            continue
        if (
            not isinstance(sources, list)
            or not sources
            or any(not isinstance(value, str) or not value for value in sources)
            or not isinstance(targets, list)
            or not targets
            or any(not isinstance(value, str) or not value for value in targets)
        ):
            findings.append({"code": "INVALID_DERIVATION_LINK", "index": index})
            continue

        unknown_sources = sorted(set(sources) - set(source_assertions))
        unknown_targets = sorted(set(targets) - set(target_assertions))
        if unknown_sources:
            findings.append(
                {
                    "code": "UNKNOWN_DERIVATION_SOURCE",
                    "index": index,
                    "sources": unknown_sources,
                }
            )
        if unknown_targets:
            findings.append(
                {
                    "code": "UNKNOWN_DERIVATION_TARGET",
                    "index": index,
                    "targets": unknown_targets,
                }
            )
        valid_sources = sorted(set(sources) & set(source_assertions))
        valid_targets = sorted(set(targets) & set(target_assertions))
        if unknown_sources or unknown_targets:
            continue

        covered_sources.update(valid_sources)
        evaluated_links.append(
            {
                "relation": relation,
                "sources": valid_sources,
                "targets": valid_targets,
            }
        )

    disposition_by_source: dict[str, dict[str, Any]] = {}
    dispositions = evidence.get("dispositions", []) or []
    if not isinstance(dispositions, list):
        findings.append({"code": "INVALID_DERIVATION_DISPOSITIONS"})
        dispositions = []
    for item in dispositions:
        if not isinstance(item, dict):
            findings.append({"code": "INVALID_DERIVATION_DISPOSITION"})
            continue
        source_id = item.get("source")
        status = item.get("status")
        rationale = item.get("rationale")
        if (
            not isinstance(source_id, str)
            or source_id not in source_assertions
            or status not in DISPOSITIONS
            or not isinstance(rationale, str)
            or not rationale.strip()
        ):
            findings.append(
                {
                    "code": "INVALID_DERIVATION_DISPOSITION",
                    **({"source": source_id} if isinstance(source_id, str) else {}),
                }
            )
            continue
        if source_id in disposition_by_source:
            findings.append(
                {
                    "code": "DUPLICATE_DERIVATION_DISPOSITION",
                    "source": source_id,
                }
            )
            continue
        disposition_by_source[source_id] = item
        if status == "QUESTION":
            findings.append(
                {
                    "code": "DERIVATION_QUESTION",
                    "source": source_id,
                    "obligation": source_obligation.get(source_id),
                    "source_capability": source_capability,
                    "target_capability": target_capability,
                    "owner_authority": target_authority,
                    "rationale": rationale,
                }
            )

    for source_id in sorted(covered_sources & set(disposition_by_source)):
        findings.append(
            {
                "code": "DERIVATION_DISPOSITION_CONFLICT",
                "source": source_id,
            }
        )

    for source_id in sorted(required_sources):
        if source_id in covered_sources or source_id in disposition_by_source:
            continue
        assertion = source_assertions[source_id]
        findings.append(
            {
                "code": "UNDISPOSITIONED_SOURCE",
                "source": source_id,
                "source_kind": assertion.get("kind"),
                "subject": assertion.get("subject"),
                "obligation": source_obligation[source_id],
                "source_capability": source_capability,
                "target_capability": target_capability,
                "owner_authority": target_authority,
            }
        )

    status = "ACCEPTED" if not findings else "REJECTED"
    return {
        "version": 1,
        "kind": "harness-semantic-derivation-evaluation",
        "source_capability": source_capability,
        "target_capability": target_capability,
        "source_authority": source_authority,
        "target_authority": target_authority,
        "status": status,
        "required_sources": sorted(required_sources),
        "covered_sources": sorted(required_sources & covered_sources),
        "dispositions": [
            {
                "source": source_id,
                "status": item["status"],
                "rationale": item["rationale"],
            }
            for source_id, item in sorted(disposition_by_source.items())
            if source_id in required_sources
        ],
        "links": evaluated_links,
        "findings": findings,
    }


def _load(path: str | Path) -> dict[str, Any]:
    value = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise CoreError(f"{path} must contain a mapping")
    return value


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate semantic derivation coverage")
    parser.add_argument("graph")
    parser.add_argument("contract")
    parser.add_argument("source")
    parser.add_argument("candidate")
    parser.add_argument("evidence")
    args = parser.parse_args()
    result = evaluate_derivation(
        graph=_load(args.graph),
        contract=_load(args.contract),
        source=_load(args.source),
        candidate=_load(args.candidate),
        evidence=_load(args.evidence),
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "ACCEPTED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
