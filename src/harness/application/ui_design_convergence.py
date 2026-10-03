#!/usr/bin/env python3
"""Deterministic UI design convergence assurance above Harness Core."""
from __future__ import annotations

from typing import Any

from harness.project_model.core import CoreError

EVIDENCE_CLASSES = {"STANDARD", "EMPIRICAL", "MODEL", "CONVENTION", "HEURISTIC", "EXPERT"}
EVIDENCE_STRENGTH = {"STRONG", "MODERATE", "WEAK"}
COVERAGE_STATUS = {"COVERED", "NOT_APPLICABLE", "UNRESOLVED"}
DECISION_DISPOSITIONS = {"DETERMINED", "DELEGATED", "EMPIRICAL_VALIDATION_REQUIRED"}
MATERIALITY = {"CRITICAL", "MATERIAL"}
EVALUATION_LEVELS = {"E0", "E1", "E2", "E3", "E4"}
REQUIRED_COVERAGE = {
    "critical-task-disposition",
    "semantic-traceability",
    "accessibility-obligations",
    "critical-executable-paths",
    "prototype-contract-consistency",
}

__all__ = [
    "ui_decision_rule_index",
    "evaluate_ui_design_convergence",
]


def _strings(value: Any, *, required: bool = False) -> list[str] | None:
    if not isinstance(value, list) or (required and not value):
        return None
    if any(not isinstance(item, str) or not item.strip() for item in value):
        return None
    return list(dict.fromkeys(value))


def _require_strings(value: Any, where: str, *, required: bool = False) -> list[str]:
    result = _strings(value, required=required)
    if result is None:
        qualifier = "non-empty " if required else ""
        raise CoreError(f"{where} must be a {qualifier}list of non-empty strings")
    return result


def ui_decision_rule_index(document: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Validate and index the reusable conditional UI decision-rule catalog."""
    if (
        not isinstance(document, dict)
        or document.get("version") != 1
        or document.get("kind") != "harness-ui-decision-rule-catalog"
    ):
        raise CoreError("invalid UI decision rule catalog")
    rules = document.get("rules")
    if not isinstance(rules, list) or not rules:
        raise CoreError("UI decision rule catalog requires rules")

    result: dict[str, dict[str, Any]] = {}
    for raw in rules:
        if not isinstance(raw, dict):
            raise CoreError("UI decision rule must be a mapping")
        rule_id = raw.get("id")
        if not isinstance(rule_id, str) or not rule_id.strip() or rule_id in result:
            raise CoreError("UI decision rules require unique non-empty ids")
        question = raw.get("question")
        if not isinstance(question, str) or not question.strip():
            raise CoreError(f"{rule_id}.question must be a non-empty string")

        predicates = _require_strings(
            raw.get("observable_predicates"),
            f"{rule_id}.observable_predicates",
            required=True,
        )
        consequence = raw.get("consequence")
        if not isinstance(consequence, dict):
            raise CoreError(f"{rule_id}.consequence must be a mapping")
        unknown_keys = sorted(set(consequence) - {"preferred", "allowed", "disallowed"})
        if unknown_keys:
            raise CoreError(f"{rule_id}.consequence has unknown keys: {unknown_keys}")
        normalized_consequence = {
            key: _require_strings(
                consequence.get(key, []),
                f"{rule_id}.consequence.{key}",
            )
            for key in ("preferred", "allowed", "disallowed")
        }
        if not any(normalized_consequence.values()):
            raise CoreError(f"{rule_id}.consequence must contain at least one item")

        exceptions = raw.get("exceptions", []) or []
        if not isinstance(exceptions, list):
            raise CoreError(f"{rule_id}.exceptions must be a list")
        normalized_exceptions: list[dict[str, str]] = []
        for exception in exceptions:
            if not isinstance(exception, dict):
                raise CoreError(f"{rule_id}.exceptions must contain mappings")
            condition = exception.get("condition")
            consequence_text = exception.get("consequence")
            if (
                not isinstance(condition, str)
                or not condition.strip()
                or not isinstance(consequence_text, str)
                or not consequence_text.strip()
            ):
                raise CoreError(
                    f"{rule_id}.exceptions require condition and consequence"
                )
            normalized_exceptions.append(
                {"condition": condition, "consequence": consequence_text}
            )

        evidence = raw.get("evidence")
        if not isinstance(evidence, dict):
            raise CoreError(f"{rule_id}.evidence must be a mapping")
        if evidence.get("class") not in EVIDENCE_CLASSES:
            raise CoreError(f"{rule_id}.evidence.class is invalid")
        if evidence.get("strength") not in EVIDENCE_STRENGTH:
            raise CoreError(f"{rule_id}.evidence.strength is invalid")
        sources = _require_strings(
            evidence.get("sources"),
            f"{rule_id}.evidence.sources",
            required=True,
        )

        applicability = raw.get("applicability", {}) or {}
        validation = raw.get("project_validation", {}) or {}
        if not isinstance(applicability, dict) or not isinstance(validation, dict):
            raise CoreError(f"{rule_id} applicability/validation must be mappings")
        suggested_method = validation.get("suggested_method")
        if suggested_method is not None and (
            not isinstance(suggested_method, str) or not suggested_method.strip()
        ):
            raise CoreError(f"{rule_id}.project_validation.suggested_method is invalid")

        result[rule_id] = {
            "id": rule_id,
            "question": question,
            "observable_predicates": predicates,
            "consequence": normalized_consequence,
            "applicability": {
                "requires": _require_strings(
                    applicability.get("requires", []),
                    f"{rule_id}.applicability.requires",
                ),
                "excludes": _require_strings(
                    applicability.get("excludes", []),
                    f"{rule_id}.applicability.excludes",
                ),
            },
            "exceptions": normalized_exceptions,
            "evidence": {
                "class": evidence["class"],
                "strength": evidence["strength"],
                "sources": sources,
            },
            "project_validation": {
                "required_when": _require_strings(
                    validation.get("required_when", []),
                    f"{rule_id}.project_validation.required_when",
                ),
                "suggested_method": suggested_method,
            },
            "freedom_remaining": _require_strings(
                raw.get("freedom_remaining", []),
                f"{rule_id}.freedom_remaining",
            ),
        }
    return result


def _finding(code: str, **details: Any) -> dict[str, Any]:
    return {"code": code, **details}


def evaluate_ui_design_convergence(
    *,
    rule_catalog: dict[str, Any],
    evidence: dict[str, Any] | None,
) -> dict[str, Any]:
    """Derive UI DESIGN READY from explicit coverage and material-decision evidence."""
    rules = ui_decision_rule_index(rule_catalog)
    base = {
        "version": 1,
        "kind": "harness-ui-design-convergence-evaluation",
        "subject": evidence.get("subject") if isinstance(evidence, dict) else None,
    }
    if not isinstance(evidence, dict):
        findings = [_finding("UI_CONVERGENCE_EVIDENCE_REQUIRED")]
        return {**base, "status": "NOT_READY", "ui_design_ready": False, "findings": findings}
    if (
        evidence.get("version") != 1
        or evidence.get("kind") != "harness-ui-design-convergence-evidence"
    ):
        findings = [_finding("UI_CONVERGENCE_EVIDENCE_DOCUMENT_INVALID")]
        return {**base, "status": "NOT_READY", "ui_design_ready": False, "findings": findings}

    findings: list[dict[str, Any]] = []
    subject = evidence.get("subject")
    if not isinstance(subject, str) or not subject.strip():
        findings.append(_finding("UI_CONVERGENCE_SUBJECT_REQUIRED"))

    coverage = evidence.get("coverage")
    if not isinstance(coverage, list):
        findings.append(_finding("UI_COVERAGE_INVALID"))
        coverage = []
    indexed_coverage: dict[str, dict[str, Any]] = {}
    for row in coverage:
        item_id = row.get("id") if isinstance(row, dict) else None
        if not isinstance(item_id, str) or not item_id or item_id in indexed_coverage:
            findings.append(_finding("UI_COVERAGE_ITEM_INVALID"))
            continue
        indexed_coverage[item_id] = row

    for item_id in sorted(REQUIRED_COVERAGE):
        row = indexed_coverage.get(item_id)
        if row is None:
            findings.append(_finding("UI_COVERAGE_ITEM_MISSING", coverage=item_id))
            continue
        status = row.get("status")
        refs = _strings(row.get("evidence_refs", []))
        if status not in COVERAGE_STATUS:
            findings.append(_finding("UI_COVERAGE_STATUS_INVALID", coverage=item_id))
        elif refs is None:
            findings.append(_finding("UI_COVERAGE_EVIDENCE_REFS_INVALID", coverage=item_id))
        elif status == "COVERED" and not refs:
            findings.append(_finding("UI_COVERAGE_EVIDENCE_REQUIRED", coverage=item_id))
        elif status == "NOT_APPLICABLE" and (
            not isinstance(row.get("rationale"), str) or not row["rationale"].strip()
        ):
            findings.append(
                _finding("UI_COVERAGE_NOT_APPLICABLE_RATIONALE_REQUIRED", coverage=item_id)
            )
        elif status == "UNRESOLVED":
            findings.append(_finding("UI_COVERAGE_UNRESOLVED", coverage=item_id))

    decisions = evidence.get("material_decisions", [])
    if not isinstance(decisions, list):
        findings.append(_finding("UI_MATERIAL_DECISIONS_INVALID"))
        decisions = []
    seen: set[str] = set()
    for row in decisions:
        decision_id = row.get("id") if isinstance(row, dict) else None
        if not isinstance(decision_id, str) or not decision_id or decision_id in seen:
            findings.append(_finding("UI_MATERIAL_DECISION_INVALID"))
            continue
        seen.add(decision_id)

        if not isinstance(row.get("axis"), str) or not row["axis"].strip():
            findings.append(_finding("UI_DECISION_AXIS_REQUIRED", decision=decision_id))
        if not isinstance(row.get("question"), str) or not row["question"].strip():
            findings.append(_finding("UI_DECISION_QUESTION_REQUIRED", decision=decision_id))
        if row.get("materiality") not in MATERIALITY:
            findings.append(_finding("UI_DECISION_MATERIALITY_INVALID", decision=decision_id))

        disposition = row.get("disposition")
        if disposition not in DECISION_DISPOSITIONS:
            findings.append(_finding("UI_DECISION_DISPOSITION_INVALID", decision=decision_id))

        if _strings(row.get("basis_refs", []), required=True) is None:
            findings.append(_finding("UI_DECISION_BASIS_REQUIRED", decision=decision_id))

        applied_rules = _strings(row.get("applied_rules", []))
        if applied_rules is None:
            findings.append(_finding("UI_DECISION_RULE_REFS_INVALID", decision=decision_id))
            applied_rules = []
        unknown_rules = sorted(set(applied_rules) - set(rules))
        if unknown_rules:
            findings.append(
                _finding("UI_UNKNOWN_DECISION_RULE", decision=decision_id, rules=unknown_rules)
            )

        if disposition in {"DETERMINED", "DELEGATED"} and (
            not isinstance(row.get("selected"), str) or not row["selected"].strip()
        ):
            findings.append(_finding("UI_DECISION_SELECTION_REQUIRED", decision=decision_id))
        if disposition == "DELEGATED" and (
            not isinstance(row.get("governance_ref"), str)
            or not row["governance_ref"].strip()
        ):
            findings.append(
                _finding("UI_DELEGATED_DECISION_GOVERNANCE_REF_REQUIRED", decision=decision_id)
            )
        if disposition == "EMPIRICAL_VALIDATION_REQUIRED":
            findings.append(_finding("UI_EMPIRICAL_VALIDATION_REQUIRED", decision=decision_id))

        residual = _strings(row.get("residual_uncertainty", []))
        if residual is None:
            findings.append(_finding("UI_RESIDUAL_UNCERTAINTY_INVALID", decision=decision_id))
        elif residual:
            findings.append(
                _finding(
                    "UI_RESIDUAL_MATERIAL_UNCERTAINTY",
                    decision=decision_id,
                    uncertainty=residual,
                )
            )
        if _strings(row.get("controlled_freedom", [])) is None:
            findings.append(_finding("UI_CONTROLLED_FREEDOM_INVALID", decision=decision_id))

        levels = _strings(row.get("required_evidence_levels", []))
        if levels is None:
            findings.append(
                _finding("UI_REQUIRED_EVALUATION_LEVELS_INVALID", decision=decision_id)
            )
            levels = []
        unknown_levels = sorted(set(levels) - EVALUATION_LEVELS)
        if unknown_levels:
            findings.append(
                _finding(
                    "UI_UNKNOWN_EVALUATION_LEVEL",
                    decision=decision_id,
                    levels=unknown_levels,
                )
            )
        if (
            disposition == "EMPIRICAL_VALIDATION_REQUIRED"
            and not ({"E3", "E4"} & set(levels))
        ):
            findings.append(
                _finding("UI_EMPIRICAL_VALIDATION_LEVEL_REQUIRED", decision=decision_id)
            )

        evaluations = row.get("evaluation_evidence", {}) or {}
        if not isinstance(evaluations, dict):
            findings.append(_finding("UI_EVALUATION_EVIDENCE_INVALID", decision=decision_id))
            evaluations = {}
        for level in levels:
            if level in EVALUATION_LEVELS and _strings(
                evaluations.get(level, []), required=True
            ) is None:
                findings.append(
                    _finding(
                        "UI_REQUIRED_EVALUATION_EVIDENCE_MISSING",
                        decision=decision_id,
                        level=level,
                    )
                )

    ready = not findings
    return {
        **base,
        "status": "READY" if ready else "NOT_READY",
        "ui_design_ready": ready,
        "findings": findings,
        "coverage": sorted(indexed_coverage),
        "material_decisions": sorted(seen),
    }
