#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from harness.application.skill_invariant_policy import evaluate_skill_invariant_policy  # noqa: E402


def main() -> int:
    result = evaluate_skill_invariant_policy(ROOT)
    assert result["status"] == "ACCEPTED", result
    assert result["enforced_count"] == result["semantic_contract_count"], result
    assert result["active_skill_count"] == (
        result["enforced_count"] + result["judgement_only_count"]
    ), result
    print(
        "skill invariant policy: PASS "
        f"({result['enforced_count']} enforced routes, "
        f"{result['judgement_only_count']} judgement-only skills)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
