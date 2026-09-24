#!/usr/bin/env python3
"""Validate Authority knowledge-flow research fixtures."""
from __future__ import annotations

import sys
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "spec/research/authority-boundary-knowledge-flow-v1.yaml"

def evaluate(case: dict) -> list[str]:
    errors: list[str] = []
    authorities = case.get("authorities") or []
    ids = {a.get("id") for a in authorities}
    produced: dict[str, str] = {}
    outputs_by_authority: dict[str, set[str]] = {}

    for a in authorities:
        aid = a.get("id")
        decisions = a.get("decisions") or []
        if not aid or not decisions:
            errors.append(f"{aid or '<missing>'}: decision identity missing")
        outputs = a.get("outputs") or []
        if not outputs:
            errors.append(f"{aid}: no accepted knowledge output")
        outputs_by_authority[aid] = set()
        for out in outputs:
            cap = out.get("capability")
            if not cap:
                errors.append(f"{aid}: output capability missing")
                continue
            if cap in produced:
                errors.append(f"{cap}: multiple producers")
            produced[cap] = aid
            outputs_by_authority[aid].add(cap)
            consumers = out.get("consumers") or []
            terminal = out.get("terminal_reason")
            if not consumers and not terminal:
                errors.append(f"{aid}/{cap}: public output is not live")
            for c in consumers:
                target = c.get("authority")
                target_output = c.get("output")
                necessity = (c.get("necessity") or "").strip()
                encapsulation = (c.get("encapsulation") or "").strip()
                if target not in ids:
                    errors.append(f"{aid}/{cap}: unknown consumer {target}")
                if not target_output:
                    errors.append(f"{aid}/{cap}: consumer output missing")
                elif target_output not in outputs_by_authority.get(target, set()):
                    # target may appear later; checked again after collection
                    pass
                if not necessity:
                    errors.append(f"{aid}/{cap}: dependency necessity missing")
                if not encapsulation:
                    errors.append(f"{aid}/{cap}: encapsulation evidence missing")

    # second pass after all outputs are known
    invalid_edge_markers = [x.lower() for x in case.get("invalid_edge_markers", [])]
    forbidden_encapsulation = [x.lower() for x in case.get("forbidden_encapsulation_markers", [])]
    for a in authorities:
        aid = a.get("id")
        for out in a.get("outputs") or []:
            cap = out.get("capability")
            for c in out.get("consumers") or []:
                target = c.get("authority")
                target_output = c.get("output")
                if target_output and target_output not in outputs_by_authority.get(target, set()):
                    errors.append(f"{aid}/{cap}: consumer output {target_output} not produced by {target}")
                necessity = (c.get("necessity") or "").lower()
                encapsulation = (c.get("encapsulation") or "").lower()
                if any(marker in necessity for marker in invalid_edge_markers):
                    errors.append(f"{aid}/{cap}: dependency justified only by conceptual/order language")
                if any(marker in encapsulation for marker in forbidden_encapsulation):
                    errors.append(f"{aid}/{cap}: consumer leaks into producer decision ownership")

    return errors

def main() -> int:
    doc = yaml.safe_load(FIXTURE.read_text(encoding="utf-8"))
    failures: list[str] = []
    passed = 0
    for case in doc.get("cases", []):
        errors = evaluate(case)
        actual = "PASS" if not errors else "FAIL"
        expected = case.get("expect")
        if actual != expected:
            failures.append(f"{case.get('id')}: expected {expected}, got {actual}: {errors}")
        else:
            passed += 1

    if failures:
        print("Authority knowledge-flow research validation failed:", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1
    print(f"Authority knowledge-flow research validation passed ({passed} cases)")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
