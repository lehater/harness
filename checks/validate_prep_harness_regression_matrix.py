#!/usr/bin/env python3
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / "spec" / "assurance" / "prep-harness-remediation-regression-matrix-v0.yaml"
CI_REGISTRY = ROOT / "spec" / "ci" / "check-registry-v0.yaml"
EXPECTED = {f"HARNESS-{index:03d}" for index in range(1, 9)}
FORBIDDEN = {"status", "priority", "description", "defect", "defect_description"}


def _load(path: Path) -> dict:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise AssertionError(f"{path} must contain a mapping")
    return value


def _walk_forbidden(value, path="matrix") -> None:
    if isinstance(value, dict):
        overlap = set(value) & FORBIDDEN
        assert not overlap, f"{path} contains mutable register fields: {sorted(overlap)}"
        for key, item in value.items():
            _walk_forbidden(item, f"{path}.{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _walk_forbidden(item, f"{path}[{index}]")


def _validate_ref(item: dict, where: str) -> None:
    assert isinstance(item, dict), f"{where} must be a mapping"
    path = item.get("path")
    anchor = item.get("anchor")
    assert isinstance(path, str) and path, f"{where}.path required"
    assert isinstance(anchor, str) and anchor, f"{where}.anchor required"
    target = ROOT / path
    assert target.is_file(), f"{where} references missing test/scenario: {path}"
    text = target.read_text(encoding="utf-8")
    assert anchor in text, f"{where} lost executable anchor {anchor!r} in {path}"


def main() -> int:
    matrix = _load(MATRIX)
    assert matrix.get("version") == 1
    assert matrix.get("kind") == "harness-program-regression-matrix"
    _walk_forbidden(matrix)

    entries = matrix.get("entries")
    assert isinstance(entries, list), "matrix.entries must be a list"
    ids = [entry.get("harness_id") for entry in entries if isinstance(entry, dict)]
    assert set(ids) == EXPECTED, f"expected HARNESS-001..008, got {sorted(set(ids))}"
    assert len(ids) == len(set(ids)) == 8, "matrix Harness ids must be unique"

    ci = _load(CI_REGISTRY)
    checks = {
        item.get("id")
        for item in ci.get("checks", [])
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }

    for entry in entries:
        harness_id = entry["harness_id"]
        owner = entry.get("owner_check")
        assert owner in checks, f"{harness_id} owner check is not registered: {owner}"
        _validate_ref(entry.get("red"), f"{harness_id}.red")
        _validate_ref(entry.get("green"), f"{harness_id}.green")
        controls = entry.get("positive_controls")
        assert isinstance(controls, list) and controls, (
            f"{harness_id} must retain at least one positive/freedom control"
        )
        for index, control in enumerate(controls):
            _validate_ref(control, f"{harness_id}.positive_controls[{index}]")

    h7 = next(item for item in entries if item["harness_id"] == "HARNESS-007")
    h7_anchors = {
        h7["red"]["anchor"],
        h7["green"]["anchor"],
        *(item["anchor"] for item in h7["positive_controls"]),
    }
    assert "test_t1_interaction_to_screen_missing_is_first" in h7_anchors
    assert "test_complete_chain_is_complete" in h7_anchors
    assert "test_composed_vertical_chain_complete_then_exact_middle_mutation" in h7_anchors

    print("Prep/Harness remediation regression matrix: PASS (HARNESS-001..008)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
