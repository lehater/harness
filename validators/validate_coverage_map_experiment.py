#!/usr/bin/env python3
"""Research-only smoke validation for hierarchical coverage map prototype."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from coverage_map_experiment import aggregate, derive_tree, load, validate

CATALOG = ROOT / "spec/research/engineering-concerns-v1.yaml"
ETL = ROOT / "spec/research/engineering-coverage-map-etl-v1.yaml"


def main() -> int:
    catalog = load(str(CATALOG))
    etl = load(str(ETL))

    errors = validate(catalog, etl)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    assert aggregate(["COVERED", "NOT_APPLICABLE"]) == "COVERED"
    assert aggregate(["COVERED", "UNASSESSED"]) == "PARTIAL"
    assert aggregate(["NOT_APPLICABLE", "NOT_APPLICABLE"]) == "NOT_APPLICABLE"

    states = derive_tree(catalog, etl)
    assert states["interface.human"] == "NOT_APPLICABLE"
    assert states["interface"] == "PARTIAL"
    assert states["data"] == "PARTIAL"
    assert states["security"] == "PARTIAL"
    assert states["verification"] == "COVERED"

    print("hierarchical coverage experiment: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
