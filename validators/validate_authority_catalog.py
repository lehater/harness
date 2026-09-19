#!/usr/bin/env python3
"""Validate experimental Harness Authority reference catalogs."""
from __future__ import annotations

import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def main() -> int:
    errors: list[str] = []
    catalogs = sorted((ROOT / "catalogs").glob("*authorities*.yaml"))
    if not catalogs:
        errors.append("no Authority catalog found")

    for path in catalogs:
        try:
            doc = yaml.safe_load(path.read_text(encoding="utf-8"))
            if not isinstance(doc, dict):
                raise ValueError("catalog must be a mapping")
            if doc.get("version") != 1:
                raise ValueError("catalog version must be 1")
            if doc.get("kind") != "harness-authority-catalog":
                raise ValueError("unexpected Authority catalog kind")
            if not isinstance(doc.get("id"), str) or not doc["id"]:
                raise ValueError("catalog id is required")

            principles = doc.get("principles", {})
            atomicity = principles.get("atomicity_test")
            if atomicity != [
                "semantic_cohesion",
                "independent_change",
                "public_contract",
            ]:
                raise ValueError(
                    "atomicity_test must be semantic_cohesion, "
                    "independent_change, public_contract"
                )

            seen: set[str] = set()
            for authority in doc.get("authorities", []) or []:
                if not isinstance(authority, dict):
                    raise ValueError("Authority entry must be a mapping")
                authority_id = authority.get("id")
                if not isinstance(authority_id, str) or not authority_id:
                    raise ValueError("Authority id is required")
                if authority_id in seen:
                    raise ValueError(f"duplicate Authority id: {authority_id}")
                seen.add(authority_id)

                authority_class = authority.get("class")
                if authority_class not in {"baseline", "conditional"}:
                    raise ValueError(
                        f"{authority_id}: class must be baseline or conditional"
                    )
                if authority_class == "conditional":
                    applies_when = authority.get("applies_when")
                    if not isinstance(applies_when, str) or not applies_when.strip():
                        raise ValueError(
                            f"{authority_id}: conditional Authority needs applies_when"
                        )

                responsibility = authority.get("responsibility")
                if not isinstance(responsibility, str) or not responsibility.strip():
                    raise ValueError(f"{authority_id}: responsibility is required")

                boundary = authority.get("boundary")
                if not isinstance(boundary, dict):
                    raise ValueError(f"{authority_id}: boundary is required")
                for field in (
                    "semantic_cohesion",
                    "independent_change",
                    "public_contract",
                ):
                    value = boundary.get(field)
                    if not isinstance(value, str) or not value.strip():
                        raise ValueError(
                            f"{authority_id}: boundary.{field} is required"
                        )

            baseline = {
                item["id"]
                for item in doc.get("authorities", []) or []
                if item.get("class") == "baseline"
            }
            expected_baseline = {
                "DISCOVERY",
                "PRODUCT-REQUIREMENTS",
                "SYSTEM-ARCHITECTURE",
                "IMPLEMENTATION-DESIGN",
                "VERIFICATION-DESIGN",
            }
            if baseline != expected_baseline:
                raise ValueError(
                    f"reference baseline mismatch: {sorted(baseline)} "
                    f"!= {sorted(expected_baseline)}"
                )
        except Exception as exc:
            fail(errors, f"{path.relative_to(ROOT)}: {exc}")

    if errors:
        print("Harness Authority catalog validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(
        "Harness Authority catalog validation passed "
        f"({len(catalogs)} catalog(s))"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
