#!/usr/bin/env python3
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from concern_activation_experiment import derive_activation, load

def main() -> int:
    result = derive_activation(
        load(str(ROOT / "spec/research/concern-activation-policy-v1.yaml")),
        load(str(ROOT / "spec/research/coverage-planner-fixture-authorities.yaml")),
        load(str(ROOT / "spec/research/concern-activation-fixture-overlay.yaml")),
        [load(str(ROOT / "spec/research/coverage-derivation-fixture-knowledge.yaml"))],
    )
    rows = {row["concern"]: row for row in result["rows"]}
    assert "intent.behavior" in rows
    assert "data.classification" in rows
    assert "data.lifecycle" in rows
    assert "governance.privacy" in rows
    assert any(p["source"] == "BASELINE" for p in rows["intent.behavior"]["provenance"])
    assert any(p["source"] == "RULE" and p["rule"] == "PERSISTENT-DATA" for p in rows["data.classification"]["provenance"])
    assert any(p["source"] == "EXPLICIT_PROJECT_FACT" for p in rows["governance.privacy"]["provenance"])
    print("concern activation experiment: ok")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
