#!/usr/bin/env python3
"""No-provider contract tests for blinded Copilot Dependency Resolution adapter."""
from __future__ import annotations

import copy
from pathlib import Path
import sys
from unittest.mock import patch

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from evals.dependency_resolution_process_driver import build_blinded_request
import evals.adapters.copilot_dependency_resolution_evaluator as adapter

data = yaml.safe_load(
    (ROOT / "spec/dependency-resolution/calibration-inputs-v1.yaml").read_text(encoding="utf-8")
)
oracle = yaml.safe_load(
    (ROOT / "spec/dependency-resolution/calibration-oracle-v1.yaml").read_text(encoding="utf-8")
)
request = build_blinded_request(data, run_id="ADAPTER-SMOKE", adapter_binding={"id": "fixture"})
payload = adapter._blinded_model_payload(request)
assert len(payload["cases"]) == 6
assert "expected_requires" not in adapter._prompt(request)
assert "baseline_requires" not in adapter._prompt(request)
assert "review_status" not in adapter._prompt(request)
assert "CDR-01" not in adapter._prompt(request)
assert "PREP-REVALIDATION" not in adapter._prompt(request)
assert "declare" not in set(payload["cases"][0])

invalid = copy.deepcopy(request)
invalid["cases"][0]["target"]["requires"] = ["demo.product-edit-policy"]
try:
    adapter._blinded_model_payload(invalid)
except ValueError:
    pass
else:
    raise AssertionError("target requires must not be passed to Copilot")

invalid = copy.deepcopy(request)
invalid["cases"][0]["expected_requires"] = ["demo.product-edit-policy"]
try:
    adapter._blinded_model_payload(invalid)
except ValueError:
    pass
else:
    raise AssertionError("expert answer must never reach model prompt")

example = {
    "version": 1,
    "kind": adapter.RESPONSE_KIND,
    "results": [
        {
            "case_request_id": c["case_request_id"],
            "status": "UNRESOLVED",
            "proposed_requires": [],
            "input_needs": [],
            "unresolved_obligations": [],
        }
        for c in request["cases"]
    ],
}
with patch.object(adapter, "_invoke_model", return_value=(
    example,
    {"provider": "github-copilot", "resolved_model": "synthetic"}
)):
    result = adapter.evaluate_request(request)
assert result["request_id"] == request["request_id"]
assert result["results"] == example["results"]
assert result["provenance"]["provider"] == "github-copilot"

# The oracle must never be passed to the adapter, even if it is present in the
# repository for scoring. These fixtures check process boundaries, not semantic
# validity or actual provider independence.
assert oracle["privacy"] == "NEVER_SEND_TO_EVALUATED_AGENT"
print("Copilot Dependency Resolution adapter: PASS")
