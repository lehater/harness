#!/usr/bin/env python3
"""Pre-choice decision-space exploration evidence for Harness semantic admission."""
from __future__ import annotations

import json
from typing import Any

from decision_explorer_request import validate_explorer_request_binding
from harness import CoreError

EXPLORATION = {"LOCAL": 0, "EXPLORE": 1, "RESEARCH": 2, "DEEP_RESEARCH": 3}
APPLICABILITY = {"APPLICABLE", "NOT_APPLICABLE", "UNRESOLVED"}
AUTHORITATIVE_SOURCES = {"official", "standard", "primary", "maintainer"}


def _level(value: Any, where: str) -> str:
    if not isinstance(value, str) or value not in EXPLORATION:
        raise CoreError(f"{where} must be one of {sorted(EXPLORATION)}")
    return value


def _finding(code: str, axis: str | None = None, decision: str | None = None, **extra: Any) -> dict[str, Any]:
    value: dict[str, Any] = {"code": code}
    if axis is not None:
        value["axis"] = axis
    if decision is not None:
        value["decision"] = decision
    value.update(extra)
    return value


def _canonical_artifact_ids(model: dict[str, Any]) -> set[str]:
    return {
        item["id"]
        for item in model.get("artifacts", []) or []
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }


def _normalized_effects(value: Any) -> str | None:
    if not isinstance(value, dict) or not value:
        return None
    normalized: dict[str, Any] = {}
    for key, effect in value.items():
        if not isinstance(key, str) or not key:
            return None
        if not isinstance(effect, (str, int, float, bool)) or effect == "":
            return None
        normalized[key] = effect
    return json.dumps(normalized, sort_keys=True, ensure_ascii=True)


def evaluate_decision_exploration(
    *,
    contract: dict[str, Any] | None,
    axis_policies: dict[str, dict[str, str]] | None,
    capability: str,
    knowledge_kind: str,
    evidence: dict[str, Any] | None,
    explorer_request: dict[str, Any] | None,
    model: dict[str, Any],
) -> dict[str, Any]:
    base = {
        "version": 1,
        "kind": "harness-decision-exploration-evaluation",
        "capability": capability,
        "knowledge_kind": knowledge_kind,
    }
    if contract is None or not contract.get("required") or axis_policies is None:
        return {**base, "status": "NOT_REQUIRED", "findings": [], "axes": []}
    if not isinstance(evidence, dict):
        return {
            **base,
            "status": "REJECTED",
            "findings": [_finding("DECISION_EXPLORATION_REQUIRED")],
            "axes": [],
        }
    if evidence.get("version") != 1 or evidence.get("kind") != "harness-decision-exploration":
        return {
            **base,
            "status": "REJECTED",
            "findings": [_finding("DECISION_EXPLORATION_DOCUMENT_INVALID")],
            "axes": [],
        }
    if evidence.get("capability") != capability or evidence.get("knowledge_kind") != knowledge_kind:
        return {
            **base,
            "status": "REJECTED",
            "findings": [_finding("DECISION_EXPLORATION_TARGET_MISMATCH")],
            "axes": [],
        }

    binding_findings = validate_explorer_request_binding(
        expected_request=explorer_request,
        evidence=evidence,
    )
    if binding_findings:
        return {
            **base,
            "status": "REJECTED",
            "findings": binding_findings,
            "axes": [],
            "explorer_request_id": (
                explorer_request.get("request_id")
                if isinstance(explorer_request, dict)
                else None
            ),
        }
    # Exploration is intentionally pre-choice. Selection/disposition fields are
    # forbidden anywhere in this evidence document.
    forbidden = {"selected", "selection", "disposition", "preferred", "chosen"}

    def scan_forbidden(value: Any, path: str = "") -> list[str]:
        hits: list[str] = []
        if isinstance(value, dict):
            for key, child in value.items():
                child_path = f"{path}.{key}" if path else key
                if key in forbidden:
                    hits.append(child_path)
                hits.extend(scan_forbidden(child, child_path))
        elif isinstance(value, list):
            for index, child in enumerate(value):
                hits.extend(scan_forbidden(child, f"{path}[{index}]"))
        return hits

    forbidden_hits = scan_forbidden(evidence)
    if forbidden_hits:
        return {
            **base,
            "status": "REJECTED",
            "findings": [
                _finding(
                    "DECISION_EXPLORATION_NOT_BLIND",
                    paths=forbidden_hits,
                )
            ],
            "axes": [],
        }

    sources = {
        item.get("id"): item
        for item in evidence.get("research_sources", []) or []
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }
    axis_items = {
        item.get("axis"): item
        for item in evidence.get("axes", []) or []
        if isinstance(item, dict) and isinstance(item.get("axis"), str)
    }
    artifact_ids = _canonical_artifact_ids(model)
    findings: list[dict[str, Any]] = []
    evaluated_axes: list[dict[str, Any]] = []

    for axis, axis_contract in contract["axes"].items():
        item = axis_items.get(axis)
        if item is None:
            findings.append(_finding("DECISION_EXPLORATION_AXIS_MISSING", axis))
            continue
        applicability = item.get("applicability")
        if applicability not in APPLICABILITY:
            findings.append(_finding("DECISION_APPLICABILITY_INVALID", axis))
            continue

        effective = axis_policies.get(axis)
        if effective is None:
            findings.append(_finding("DECISION_EXPLORATION_POLICY_MISSING", axis))
            continue
        required = effective["exploration"]
        performed = item.get("exploration_level")
        if performed not in EXPLORATION:
            findings.append(_finding("DECISION_EXPLORATION_LEVEL_MISSING", axis))
        elif EXPLORATION[performed] < EXPLORATION[required]:
            findings.append(
                _finding(
                    "DECISION_EXPLORATION_TOO_SHALLOW",
                    axis,
                    required=required,
                    performed=performed,
                )
            )

        if applicability == "NOT_APPLICABLE":
            refs = item.get("applicability_evidence", []) or []
            if (
                not isinstance(refs, list)
                or not refs
                or any(ref not in artifact_ids for ref in refs)
            ):
                findings.append(
                    _finding("DECISION_NOT_APPLICABLE_EVIDENCE_REQUIRED", axis)
                )
            evaluated_axes.append(
                {
                    "axis": axis,
                    "applicability": applicability,
                    "exploration": required,
                    "decision_points": [],
                }
            )
            continue

        if applicability == "UNRESOLVED":
            findings.append(_finding("DECISION_APPLICABILITY_UNRESOLVED", axis))
            evaluated_axes.append(
                {
                    "axis": axis,
                    "applicability": applicability,
                    "exploration": required,
                    "decision_points": [],
                }
            )
            continue

        source_items = [
            sources[source_id]
            for source_id in item.get("research_sources", []) or []
            if source_id in sources
        ]
        if EXPLORATION[required] >= EXPLORATION["RESEARCH"] and not any(
            source.get("kind") in AUTHORITATIVE_SOURCES for source in source_items
        ):
            findings.append(_finding("DECISION_RESEARCH_EVIDENCE_MISSING", axis))
        if EXPLORATION[required] >= EXPLORATION["DEEP_RESEARCH"] and (
            len(source_items) < 2
            or len({source.get("kind") for source in source_items}) < 2
        ):
            findings.append(
                _finding("DECISION_DEEP_RESEARCH_DIVERSITY_MISSING", axis)
            )

        probes = item.get("probes", []) or []
        if not isinstance(probes, list):
            findings.append(_finding("DECISION_PROBES_INVALID", axis))
            probes = []
        strategies: set[str] = set()
        for probe in probes:
            strategy = probe.get("strategy") if isinstance(probe, dict) else None
            if not isinstance(strategy, str) or strategy not in axis_contract["challenge_strategies"]:
                findings.append(_finding("DECISION_PROBE_STRATEGY_INVALID", axis))
                continue
            strategies.add(strategy)
            if not isinstance(probe.get("challenge"), str) or not probe["challenge"].strip():
                findings.append(_finding("DECISION_PROBE_CHALLENGE_REQUIRED", axis))

        min_probes = 1 if EXPLORATION[required] == EXPLORATION["LOCAL"] else axis_contract["minimum_probes"]
        if len(strategies) < min_probes:
            findings.append(
                _finding(
                    "DECISION_PROBE_DIVERSITY_INSUFFICIENT",
                    axis,
                    required=min_probes,
                    performed=len(strategies),
                )
            )

        decision_points = item.get("decision_points", []) or []
        if not isinstance(decision_points, list) or not decision_points:
            findings.append(_finding("DECISION_POINT_DISCOVERY_REQUIRED", axis))
            decision_points = []
        evaluated_points: list[dict[str, Any]] = []
        seen_decisions: set[str] = set()
        for decision in decision_points:
            decision_id = decision.get("id") if isinstance(decision, dict) else None
            if not isinstance(decision_id, str) or not decision_id or decision_id in seen_decisions:
                findings.append(_finding("DECISION_POINT_INVALID", axis))
                continue
            seen_decisions.add(decision_id)
            alternatives = decision.get("alternatives", []) or []
            if not isinstance(alternatives, list) or not alternatives:
                findings.append(_finding("DECISION_ALTERNATIVE_REQUIRED", axis, decision_id))
                alternatives = []

            alt_ids: list[str] = []
            effect_signatures: set[str] = set()
            for alt in alternatives:
                alt_id = alt.get("id") if isinstance(alt, dict) else None
                if not isinstance(alt_id, str) or not alt_id or alt_id in alt_ids:
                    findings.append(_finding("DECISION_ALTERNATIVE_INVALID", axis, decision_id))
                    continue
                alt_ids.append(alt_id)
                if not isinstance(alt.get("difference"), str) or not alt["difference"].strip():
                    findings.append(
                        _finding(
                            "DECISION_ALTERNATIVE_DIFFERENCE_REQUIRED",
                            axis,
                            decision_id,
                            alternative=alt_id,
                        )
                    )
                effects = _normalized_effects(alt.get("material_effects"))
                if effects is None:
                    findings.append(
                        _finding(
                            "DECISION_ALTERNATIVE_MATERIAL_EFFECTS_REQUIRED",
                            axis,
                            decision_id,
                            alternative=alt_id,
                        )
                    )
                    continue
                effect_keys = set(alt["material_effects"])
                unknown_dimensions = sorted(
                    effect_keys - set(axis_contract["material_dimensions"])
                )
                if unknown_dimensions:
                    findings.append(
                        _finding(
                            "DECISION_ALTERNATIVE_UNKNOWN_DIMENSION",
                            axis,
                            decision_id,
                            alternative=alt_id,
                            dimensions=unknown_dimensions,
                        )
                    )
                effect_signatures.add(effects)

            minimum_alternatives = (
                1 if EXPLORATION[required] == EXPLORATION["LOCAL"] else 2
            )
            if len(alt_ids) < minimum_alternatives:
                findings.append(
                    _finding(
                        "DECISION_ALTERNATIVE_SEARCH_INSUFFICIENT",
                        axis,
                        decision_id,
                        required=minimum_alternatives,
                        performed=len(alt_ids),
                    )
                )
            if len(alt_ids) >= 2 and len(effect_signatures) < 2:
                findings.append(
                    _finding(
                        "DECISION_ALTERNATIVES_NOT_MATERIALLY_DISTINCT",
                        axis,
                        decision_id,
                    )
                )

            covered = {
                alternative
                for probe in probes
                if isinstance(probe, dict)
                for alternative in (probe.get("alternatives", []) or [])
                if isinstance(alternative, str)
            }
            missing_probe_coverage = sorted(set(alt_ids) - covered)
            if missing_probe_coverage:
                findings.append(
                    _finding(
                        "DECISION_ALTERNATIVE_NOT_PROBE_DISCOVERED",
                        axis,
                        decision_id,
                        alternatives=missing_probe_coverage,
                    )
                )
            evaluated_points.append(
                {"id": decision_id, "alternatives": alt_ids}
            )

        evaluated_axes.append(
            {
                "axis": axis,
                "applicability": applicability,
                "exploration": required,
                "probe_strategies": sorted(strategies),
                "decision_points": evaluated_points,
            }
        )

    return {
        **base,
        "status": "ACCEPTED" if not findings else "REJECTED",
        "findings": findings,
        "axes": evaluated_axes,
        "explorer_request_id": (
            explorer_request.get("request_id")
            if isinstance(explorer_request, dict)
            else None
        ),
    }
