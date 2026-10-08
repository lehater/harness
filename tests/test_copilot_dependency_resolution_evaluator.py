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
# Model and adapter own different envelopes: missing or inconsistent model
# version metadata must not discard complete, correctly bound semantic results.
normalized, envelope = adapter._validate_model_results(
    {"version": "2", "kind": "model-supplied-envelope", "results": example["results"]},
    request,
)
assert len(normalized) == 6 and envelope["adapter_envelope_normalized"]
clean, envelope = adapter._validate_model_results(
    {"results": example["results"]},
    request,
)
assert len(clean) == 6 and envelope["model_supplied_version"] == "OMITTED"

missing = copy.deepcopy(example)
missing["results"].pop()
try:
    adapter._validate_model_results(missing, request)
except ValueError as exc:
    assert "count mismatch" in str(exc)
else:
    raise AssertionError("missing model predictions may not be repaired")

duplicate = copy.deepcopy(example)
duplicate["results"][1]["case_request_id"] = duplicate["results"][0]["case_request_id"]
try:
    adapter._validate_model_results(duplicate, request)
except ValueError as exc:
    assert "duplicate case binding" in str(exc)
else:
    raise AssertionError("duplicate model bindings must be rejected")

# Source-derived real-project pilots can elicit omitted empty list fields.
# Retry is a NEW blinded model request, not silent completion of its output.
seen_prompts = []
incomplete = copy.deepcopy(example)
del incomplete["results"][0]["unresolved_obligations"]
counter = [0]

def simulated_provider(executable, prompt):
    seen_prompts.append(prompt)
    counter[0] += 1
    return (
        incomplete if counter[0] == 1 else example,
        {
            "client_session_id": f"fake-session-{counter[0]}",
            "requested_model": "auto",
            "resolved_model": "fixture-model",
            "observed_cli_version": adapter.CLI_VERSION,
        },
    )

with patch.object(adapter, "_invoke_copilot_once", side_effect=simulated_provider):
    output, provenance = adapter._invoke_model(request)
assert output["results"] == example["results"]
assert provenance["invocation_attempts"] == 2
assert provenance["attempt_session_ids"] == ["fake-session-1", "fake-session-2"]
assert "missing unresolved_obligations list" in provenance["schema_retry_errors"][0]
assert len(seen_prompts) == 2
assert "SCHEMA RETRY" not in seen_prompts[0]
assert "SCHEMA RETRY" in seen_prompts[1]
assert "expected_requires" not in repr(seen_prompts)
assert "baseline_requires" not in repr(seen_prompts)
assert "NEVER_SEND_TO_EVALUATED_AGENT" not in repr(seen_prompts)
assert all(
    c["case_request_id"] in seen_prompts[0]
    and c["case_request_id"] in seen_prompts[1]
    for c in request["cases"]
)
assert "unresolved_obligations" in seen_prompts[0]

with patch.object(
    adapter, "_invoke_copilot_once",
    return_value=(
        incomplete,
        {
            "client_session_id": "always-incomplete",
            "requested_model": "auto",
            "resolved_model": "fixture-model",
            "observed_cli_version": adapter.CLI_VERSION,
        },
    ),
):
    try:
        adapter._invoke_model(request)
    except ValueError as exc:
        assert "after 2 fresh attempts" in str(exc)
        assert "missing unresolved_obligations list" in str(exc)
    else:
        raise AssertionError("two invalid responses must fail closed")

# Source-traceability-v1 requires exhaustive per-product statement
# applicability review; silently missing a candidate is a protocol failure.
coverage_request = copy.deepcopy(request)
coverage_request["coverage_contract"] = "source-traceability-v1"
coverage_request["cases"] = [coverage_request["cases"][0]]
coverage_request["cases"][0]["target"]["upstream_constraint_candidates"] = [
    {"requirement_id": "REQ-CANDIDATE-1", "provider": "fixture.product",
     "claim_index": 0, "statement": "A test accepted product rule.",
     "traceability": "EXPLICIT_STRATEGIC_DERIVATION",
     "applicability": "REQUIRES_SEMANTIC_REVIEW"},
    {"requirement_id": "REQ-CANDIDATE-2", "provider": "fixture.product",
     "claim_index": 1, "statement": "Unrelated accepted product rule.",
     "traceability": "UNADJUDICATED_ACCEPTED_PRODUCT_REQUIREMENT",
     "applicability": "REQUIRES_SEMANTIC_REVIEW"},
]
coverage_result = copy.deepcopy(example["results"][0])
coverage_result["coverage_assessments"] = [
    {"requirement_id": "REQ-CANDIDATE-1", "disposition": "DIRECT_CONSTRAINT",
     "rationale": "The accepted normative claim constrains this exact target meaning."},
    {"requirement_id": "REQ-CANDIDATE-2", "disposition": "UNDECIDED",
     "rationale": "The accepted statement needs further scope applicability review."},
]
response = {"results": [coverage_result]}
valid_rows, _ = adapter._validate_model_results(response, coverage_request)
assert len(valid_rows[0]["coverage_assessments"]) == 2
assert "coverage_assessments" in adapter._prompt(coverage_request)
assert "expected_requires" not in adapter._prompt(coverage_request)

for change in ("missing", "duplicate", "short-rationale"):
    bad_response = copy.deepcopy(response)
    rows = bad_response["results"][0]["coverage_assessments"]
    if change == "missing":
        rows.pop()
    elif change == "duplicate":
        rows[1]["requirement_id"] = rows[0]["requirement_id"]
    else:
        rows[0]["rationale"] = "no"
    try:
        adapter._validate_model_results(bad_response, coverage_request)
    except ValueError:
        pass
    else:
        raise AssertionError(f"source coverage validation must reject {change}")

assert oracle["privacy"] == "NEVER_SEND_TO_EVALUATED_AGENT"
print("Copilot Dependency Resolution adapter: PASS")
