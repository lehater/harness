#!/usr/bin/env python3
"""Read-only end-to-end assurance traceability projection."""
from __future__ import annotations
from typing import Any

EDGE_INTERACTION_TO_SCREEN = "INTERACTION_TO_SCREEN"
EDGE_SCREEN_TO_TEST_DESIGN = "SCREEN_TO_TEST_DESIGN"
STAGE_TEST_DESIGN_CONTRACT = "TEST_DESIGN_CONTRACT"
EDGE_TEST_DESIGN_TO_EXECUTABLE = "TEST_DESIGN_TO_EXECUTABLE"
BLOCKED = "BLOCKED_BY_UPSTREAM"
NOT_EVALUABLE = "NOT_EVALUABLE"
_CORRESPONDENCE = ("JUDGEMENT", "SEMANTIC_REVIEW", "CORRESPONDENCE", "QUESTION")


def _map(value: Any, where: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{where} must be a mapping")
    return value


def _str(value: Any, where: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{where} must be a non-empty string")
    return value


def _strings(value: Any, where: str) -> list[str]:
    if not isinstance(value, list) or not value or any(
        not isinstance(item, str) or not item for item in value
    ):
        raise ValueError(f"{where} must be a non-empty string list")
    return list(value)


def _derivations(rows: list[dict[str, Any]]) -> dict[tuple[str, str], dict[str, Any]]:
    result: dict[tuple[str, str], dict[str, Any]] = {}
    for row in rows:
        if row.get("kind") != "harness-semantic-derivation-evaluation":
            raise ValueError("unexpected derivation evaluation kind")
        key = (
            _str(row.get("source_capability"), "derivation source_capability"),
            _str(row.get("target_capability"), "derivation target_capability"),
        )
        if key in result:
            raise ValueError(f"duplicate derivation evaluation: {key}")
        result[key] = row
    return result


def _realizations(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for row in rows:
        if row.get("kind") != "harness-test-realization-evaluation":
            raise ValueError("unexpected test realization evaluation kind")
        contract = _str(row.get("test_contract"), "test realization contract")
        if contract in result:
            raise ValueError(f"duplicate test realization evaluation: {contract}")
        result[contract] = row
    return result


def _ref(source: str, target: str) -> str:
    return f"semantic-derivation:{source}->{target}"


def _finding_codes(row: dict[str, Any]) -> list[str]:
    return [
        item["code"]
        for item in row.get("findings", []) or []
        if isinstance(item, dict) and isinstance(item.get("code"), str)
    ]


def _edge_failure_status(row: dict[str, Any]) -> str:
    judgement = row.get("semantic_judgement")
    if isinstance(judgement, dict) and judgement.get("status") in {
        "MISSING", "QUESTION", "REJECTED", "INVALID"
    }:
        return "QUESTION"
    if any(any(marker in code for marker in _CORRESPONDENCE) for code in _finding_codes(row)):
        return "QUESTION"
    return "MISSING"


def _disposition(row: dict[str, Any], source: str) -> dict[str, Any] | None:
    for item in row.get("dispositions", []) or []:
        if (
            isinstance(item, dict)
            and item.get("source") == source
            and item.get("status") == "NOT_APPLICABLE"
        ):
            return item
    return None


def _targets(
    row: dict[str, Any],
    sources: list[str],
    allowed_targets: list[str],
) -> list[str]:
    if row.get("status") != "ACCEPTED":
        return []
    covered = set(row.get("covered_sources", []) or [])
    allowed = set(allowed_targets)
    found: set[str] = set()
    for source in sources:
        if source not in covered:
            continue
        for link in row.get("links", []) or []:
            if not isinstance(link, dict) or source not in set(link.get("sources", []) or []):
                continue
            found.update(set(link.get("targets", []) or []) & allowed)
    return sorted(found)


def _contract(test_design: dict[str, Any], contract_id: str) -> dict[str, Any] | None:
    if test_design.get("schema") != "test-design/v1":
        return None
    content = test_design.get("content")
    tests = content.get("tests") if isinstance(content, dict) else None
    matches = [
        item for item in tests or []
        if isinstance(item, dict) and item.get("id") == contract_id
    ]
    return matches[0] if len(matches) == 1 else None


def _obligation_ids(contract: dict[str, Any], kind: str) -> set[str]:
    field = "operation_obligations" if kind == "operation" else "oracle_obligations"
    return {
        item["id"]
        for item in contract.get(field, []) or []
        if isinstance(item, dict) and isinstance(item.get("id"), str) and item["id"]
    }


def _blocked() -> dict[str, Any]:
    return {"status": BLOCKED, "semantic_ids": [], "evidence_refs": []}


def _result(
    request: dict[str, Any],
    stages: dict[str, dict[str, Any]],
    status: str,
    first: str | None,
    missing: str | None = None,
) -> dict[str, Any]:
    root = _map(request.get("root"), "request.root")
    result: dict[str, Any] = {
        "version": 1,
        "kind": "harness-traceability-projection",
        "trace_id": _str(request.get("trace_id"), "request.trace_id"),
        "root": {
            "artifact": _str(root.get("artifact"), "request.root.artifact"),
            "assertion": _str(root.get("assertion"), "request.root.assertion"),
            "category": _str(root.get("category"), "request.root.category"),
        },
        "stages": stages,
        "overall_status": status,
        "first_missing_link": first,
    }
    if missing is not None:
        result["missing_obligation"] = missing
    return result


def _currentness(currentness: dict[str, Any] | None, code: str) -> str | None:
    if not isinstance(currentness, dict):
        return None
    value = currentness.get(code)
    if isinstance(value, str):
        return value
    return value.get("status") if isinstance(value, dict) else None


def build_traceability_projection(
    request: dict[str, Any],
    *,
    derivation_evaluations: list[dict[str, Any]],
    test_design: dict[str, Any],
    test_realization_evaluations: list[dict[str, Any]],
    currentness: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Project existing assurance truth without creating new semantic validity."""
    request = _map(request, "request")
    if request.get("version") != 1 or request.get("kind") != "harness-traceability-projection-request":
        raise ValueError("invalid traceability projection request")

    root = _map(request.get("root"), "request.root")
    root_id = _str(root.get("assertion"), "request.root.assertion")
    stages = {
        "interaction": {"status": "ACCEPTED", "semantic_ids": [root_id], "evidence_refs": []},
        "screen": _blocked(),
        "test_design": _blocked(),
        "executable": _blocked(),
    }
    derivations = _derivations(derivation_evaluations)
    realizations = _realizations(test_realization_evaluations)

    i2s = _map(request.get("interaction_to_screen"), "request.interaction_to_screen")
    i_source_cap = _str(i2s.get("source_capability"), "interaction_to_screen.source_capability")
    i_target_cap = _str(i2s.get("target_capability"), "interaction_to_screen.target_capability")
    i_source = _str(i2s.get("source_assertion"), "interaction_to_screen.source_assertion")
    i_targets = _strings(i2s.get("target_assertions"), "interaction_to_screen.target_assertions")
    if i_source != root_id:
        raise ValueError("interaction_to_screen source must equal root assertion")
    i_eval = derivations.get((i_source_cap, i_target_cap))
    i_ref = _ref(i_source_cap, i_target_cap)
    if i_eval is None:
        stages["screen"] = {"status": "MISSING", "semantic_ids": [], "evidence_refs": []}
        return _result(request, stages, "INCOMPLETE", EDGE_INTERACTION_TO_SCREEN)
    if _currentness(currentness, EDGE_INTERACTION_TO_SCREEN) == "STALE":
        stages["screen"] = {"status": "STALE", "semantic_ids": i_targets, "evidence_refs": [i_ref]}
        return _result(request, stages, "STALE", EDGE_INTERACTION_TO_SCREEN)
    if _disposition(i_eval, i_source):
        stages["screen"] = {
            "status": "DISPOSITIONED", "semantic_ids": [], "evidence_refs": [i_ref],
            "disposition": "NOT_APPLICABLE",
        }
        stages["test_design"] = {"status": NOT_EVALUABLE, "semantic_ids": [], "evidence_refs": []}
        stages["executable"] = {"status": NOT_EVALUABLE, "semantic_ids": [], "evidence_refs": []}
        return _result(request, stages, "DISPOSITIONED", None)

    screen_ids = _targets(i_eval, [i_source], i_targets)
    if not screen_ids:
        edge_status = _edge_failure_status(i_eval)
        stages["screen"] = {
            "status": edge_status,
            "semantic_ids": [],
            "evidence_refs": [i_ref],
            "finding_refs": _finding_codes(i_eval),
        }
        return _result(
            request, stages,
            "QUESTION" if edge_status == "QUESTION" else "INCOMPLETE",
            EDGE_INTERACTION_TO_SCREEN,
        )
    stages["screen"] = {"status": "ACCEPTED", "semantic_ids": screen_ids, "evidence_refs": [i_ref]}

    s2t = _map(request.get("screen_to_test_design"), "request.screen_to_test_design")
    s_source_cap = _str(s2t.get("source_capability"), "screen_to_test_design.source_capability")
    s_target_cap = _str(s2t.get("target_capability"), "screen_to_test_design.target_capability")
    s_sources = _strings(s2t.get("source_assertions"), "screen_to_test_design.source_assertions")
    s_targets = _strings(s2t.get("target_assertions"), "screen_to_test_design.target_assertions")
    selected_sources = sorted(set(screen_ids) & set(s_sources))
    if not selected_sources:
        stages["test_design"] = {"status": "MISSING", "semantic_ids": [], "evidence_refs": []}
        return _result(request, stages, "INCOMPLETE", EDGE_SCREEN_TO_TEST_DESIGN)
    s_eval = derivations.get((s_source_cap, s_target_cap))
    s_ref = _ref(s_source_cap, s_target_cap)
    if s_eval is None:
        stages["test_design"] = {"status": "MISSING", "semantic_ids": [], "evidence_refs": []}
        return _result(request, stages, "INCOMPLETE", EDGE_SCREEN_TO_TEST_DESIGN)
    if _currentness(currentness, EDGE_SCREEN_TO_TEST_DESIGN) == "STALE":
        stages["test_design"] = {"status": "STALE", "semantic_ids": s_targets, "evidence_refs": [s_ref]}
        return _result(request, stages, "STALE", EDGE_SCREEN_TO_TEST_DESIGN)
    if all(_disposition(s_eval, source) for source in selected_sources):
        stages["test_design"] = {
            "status": "DISPOSITIONED", "semantic_ids": [], "evidence_refs": [s_ref],
            "disposition": "NOT_APPLICABLE",
        }
        stages["executable"] = {"status": NOT_EVALUABLE, "semantic_ids": [], "evidence_refs": []}
        return _result(request, stages, "DISPOSITIONED", None)

    test_semantic_ids = _targets(s_eval, selected_sources, s_targets)
    if not test_semantic_ids:
        edge_status = _edge_failure_status(s_eval)
        stages["test_design"] = {
            "status": edge_status,
            "semantic_ids": [],
            "evidence_refs": [s_ref],
            "finding_refs": _finding_codes(s_eval),
        }
        return _result(
            request, stages,
            "QUESTION" if edge_status == "QUESTION" else "INCOMPLETE",
            EDGE_SCREEN_TO_TEST_DESIGN,
        )

    td = _map(request.get("test_design"), "request.test_design")
    contract_id = _str(td.get("contract"), "test_design.contract")
    obligations = td.get("obligations")
    if not isinstance(obligations, list) or not obligations:
        raise ValueError("test_design.obligations must be a non-empty list")
    selected: list[tuple[str, str]] = []
    for index, raw in enumerate(obligations):
        item = _map(raw, f"test_design.obligations[{index}]")
        obligation_id = _str(item.get("id"), f"test_design.obligations[{index}].id")
        kind = item.get("kind")
        if kind not in {"operation", "oracle"}:
            raise ValueError("test obligation kind must be operation or oracle")
        selected.append((obligation_id, kind))

    contract = _contract(test_design, contract_id)
    if contract is None:
        stages["test_design"] = {
            "status": "MISSING", "semantic_ids": test_semantic_ids, "evidence_refs": [s_ref]
        }
        return _result(request, stages, "INCOMPLETE", STAGE_TEST_DESIGN_CONTRACT, contract_id)
    for obligation_id, kind in selected:
        if obligation_id not in _obligation_ids(contract, kind):
            stages["test_design"] = {
                "status": "MISSING",
                "semantic_ids": test_semantic_ids,
                "evidence_refs": sorted([s_ref, f"test-design:{contract_id}"]),
            }
            return _result(
                request, stages, "INCOMPLETE", STAGE_TEST_DESIGN_CONTRACT, obligation_id
            )
    stages["test_design"] = {
        "status": "ACCEPTED",
        "semantic_ids": sorted(set(test_semantic_ids + [item[0] for item in selected])),
        "evidence_refs": sorted([s_ref, f"test-design:{contract_id}"]),
    }

    if _currentness(currentness, EDGE_TEST_DESIGN_TO_EXECUTABLE) == "STALE":
        stages["executable"] = {
            "status": "STALE",
            "semantic_ids": sorted(item[0] for item in selected),
            "evidence_refs": [f"test-realization:{contract_id}"],
        }
        return _result(request, stages, "STALE", EDGE_TEST_DESIGN_TO_EXECUTABLE)

    realization = realizations.get(contract_id)
    if realization is None:
        stages["executable"] = {"status": "MISSING", "semantic_ids": [], "evidence_refs": []}
        return _result(
            request, stages, "INCOMPLETE", EDGE_TEST_DESIGN_TO_EXECUTABLE, selected[0][0]
        )
    if realization.get("status") != "ACCEPTED":
        requested = {item[0] for item in selected}
        missing = sorted({
            item.get("obligation")
            for item in realization.get("findings", []) or []
            if isinstance(item, dict)
            and item.get("obligation") in requested
            and item.get("code") in {
                "TEST_REALIZATION_OPERATION_MISSING",
                "TEST_REALIZATION_ORACLE_MISSING",
            }
        })
        codes = _finding_codes(realization)
        question = any(any(marker in code for marker in _CORRESPONDENCE) for code in codes)
        stages["executable"] = {
            "status": "QUESTION" if question else "MISSING",
            "semantic_ids": sorted(requested),
            "evidence_refs": [f"test-realization:{contract_id}"],
            "finding_refs": codes,
        }
        return _result(
            request, stages,
            "QUESTION" if question else "INCOMPLETE",
            EDGE_TEST_DESIGN_TO_EXECUTABLE,
            missing[0] if missing else None,
        )

    stages["executable"] = {
        "status": "ACCEPTED",
        "semantic_ids": sorted(item[0] for item in selected),
        "evidence_refs": [f"test-realization:{contract_id}"],
    }
    return _result(request, stages, "COMPLETE", None)


__all__ = [
    "BLOCKED",
    "EDGE_INTERACTION_TO_SCREEN",
    "EDGE_SCREEN_TO_TEST_DESIGN",
    "EDGE_TEST_DESIGN_TO_EXECUTABLE",
    "NOT_EVALUABLE",
    "STAGE_TEST_DESIGN_CONTRACT",
    "build_traceability_projection",
]
