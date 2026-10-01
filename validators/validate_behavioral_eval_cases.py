#!/usr/bin/env python3
"""Validate first-wave behavioral cases and Copilot adapter boundary without a live call."""
from __future__ import annotations

import json
import shutil
import stat
import sys
import tempfile
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from behavioral_eval import (
    build_execution_request,
    load_case,
    normalize_result,
    score_result,
)
from adapters.copilot_behavioral_eval_agent import (
    _bootstrap_route_context,
    _model_payload,
    _observed_cli_version,
    _parse_copilot_jsonl,
    _parse_copilot_otel_jsonl,
    _parse_model_response,
    _prompt,
    _response_contract,
)

ADAPTER = ROOT / "adapters" / "copilot_behavioral_eval_agent.py"
WORKFLOW = ROOT / ".github" / "workflows" / "behavioral-eval-copilot.yml"
assert ADAPTER.is_file()
workflow_text = WORKFLOW.read_text(encoding="utf-8")
assert "${{ inputs.model }}" not in workflow_text
assert 'MODEL="auto"' in workflow_text
assert 'MODEL_SELECTION="provider-auto"' in workflow_text
assert 'MODEL="gpt-6-luna"' not in workflow_text

sample_jsonl = "\n".join([
    json.dumps({
        "type": "assistant.usage",
        "data": {
            "model": "gpt-5.4",
            "inputTokens": 1200,
            "outputTokens": 80,
            "reasoningTokens": 20,
            "cacheReadTokens": 300,
            "cacheWriteTokens": 40,
        },
    }),
    json.dumps({
        "type": "assistant.message",
        "data": {"content": '{"version":1}'},
    }),
    json.dumps({
        "type": "session.shutdown",
        "data": {"currentModel": "auto"},
    }),
])
message, resolved_model, usage = _parse_copilot_jsonl(sample_jsonl)
assert message == '{"version":1}'
assert resolved_model == "gpt-5.4"
assert usage["turn_count"] == 1
assert usage["totals"] == {
    "input_tokens": 1200,
    "output_tokens": 80,
    "reasoning_tokens": 20,
    "cache_read_tokens": 300,
    "cache_write_tokens": 40,
}

sample_otel = "\n".join([
    json.dumps({
        "name": "chat auto",
        "attributes": {
            "gen_ai.operation.name": "chat",
            "gen_ai.conversation.id": "session-1",
            "gen_ai.request.model": "auto",
            "gen_ai.response.model": "gpt-5.4",
            "gen_ai.usage.input_tokens": 2345,
            "gen_ai.usage.output_tokens": 91,
            "gen_ai.usage.cache_read.input_tokens": 512,
            "gen_ai.usage.cache_creation.input_tokens": 128,
            "github.copilot.nano_aiu": 750000000,
            "github.copilot.cost": 1,
        },
    }),
    json.dumps({
        "resourceSpans": [{
            "scopeSpans": [{
                "spans": [{
                    "name": "chat auto",
                    "attributes": [
                        {"key": "gen_ai.operation.name", "value": {"stringValue": "chat"}},
                        {"key": "gen_ai.conversation.id", "value": {"stringValue": "other-session"}},
                        {"key": "gen_ai.response.model", "value": {"stringValue": "ignored-model"}},
                        {"key": "gen_ai.usage.input_tokens", "value": {"intValue": "999999"}},
                    ],
                }],
            }],
        }],
    }),
])
otel_model, otel_usage = _parse_copilot_otel_jsonl(
    sample_otel,
    session_id="session-1",
)
assert otel_model == "gpt-5.4"
assert otel_usage["source"] == "copilot-otel-file"
assert otel_usage["turn_count"] == 1
assert otel_usage["totals"] == {
    "input_tokens": 2345,
    "output_tokens": 91,
    "cache_read_tokens": 512,
    "cache_write_tokens": 128,
    "nano_aiu": 750000000,
    "cost_multiplier": 1,
}
assert ADAPTER.stat().st_mode & stat.S_IXUSR, "Copilot behavioral adapter must be executable"

with tempfile.TemporaryDirectory(prefix="behavioral-cli-version-") as temp:
    fake_cli = Path(temp) / "copilot"
    fake_cli.write_text(
        "#!/bin/sh\nprintf '%s\\n' 'GitHub Copilot CLI 1.0.91.'\n",
        encoding="utf-8",
    )
    fake_cli.chmod(fake_cli.stat().st_mode | stat.S_IXUSR)
    assert _observed_cli_version(str(fake_cli), {}) == "1.0.91"

BASE = ROOT / "spec" / "behavioral-evals" / "first-wave"
MANIFEST = yaml.safe_load((BASE / "manifest-v0.yaml").read_text(encoding="utf-8"))
EXPECTED = {
    "TD-CAP-001", "TD-CAP-002", "TD-CAP-003", "TD-CAP-004",
    "TD-AUTH-001", "TD-AUTH-002", "TD-AUTH-004",
    "TD-ROUTE-001", "TD-ROUTE-002", "TD-ROUTE-003",
    "TD-COMP-001",
}
assert MANIFEST["kind"] == "harness-agent-behavioral-eval-manifest"
entries = MANIFEST["cases"]
assert {item["design"] for item in entries} == EXPECTED
budget = MANIFEST["provider_prompt_budget"]
assert budget["metric"] == "utf8_bytes"
max_per_case = budget["max_per_case"]
max_suite = budget["max_suite"]
assert isinstance(max_per_case, int) and max_per_case > 0
assert isinstance(max_suite, int) and max_suite >= max_per_case
provider_prompt_bytes: dict[str, int] = {}

descriptor = {
    "version": 1,
    "kind": "harness-agent-descriptor",
    "id": "boundary-test",
    "provider": "github-copilot",
    "model": "auto",
    "model_version": "UNREPORTED",
    "configuration": {
        "requested_model": "auto",
        "model_selection": "provider-auto",
        "copilot_cli_version": "1.0.91",
        "provider_timeout_seconds": 150,
    },
}

for entry in entries:
    template = BASE / entry["template"]
    assert template.is_file(), entry
    with tempfile.TemporaryDirectory(prefix="behavioral-case-") as temp:
        temp_root = Path(temp)
        shutil.copytree(template.parent, temp_root / "case")
        runtime = temp_root / "case" / "case.yaml"
        rendered = (temp_root / "case" / "case.yaml.tmpl").read_text(encoding="utf-8")
        assert "__HARNESS_REVISION__" in rendered
        runtime.write_text(
            rendered.replace("__HARNESS_REVISION__", "a" * 40),
            encoding="utf-8",
        )
        binding = load_case(runtime)
        assert binding.case["case_id"] == entry["design"]
        assert binding.case["normalization_profile"]["dimensions"] == [entry["dimension"]]

        request = build_execution_request(
            binding,
            run_id=f"{entry['design']}-BOUNDARY",
            agent_descriptor=descriptor,
            agent_descriptor_sha256="b" * 64,
        )
        assert "oracle_ref" not in request
        assert "pass_criteria" not in request
        payload = _model_payload(request)
        serialized = json.dumps(payload, sort_keys=True)
        assert entry["design"] not in serialized
        prompt_bytes = len(_prompt(request).encode("utf-8"))
        provider_prompt_bytes[entry["design"]] = prompt_bytes
        case_limit = entry.get("max_prompt_bytes", max_per_case)
        assert isinstance(case_limit, int) and case_limit >= max_per_case
        assert prompt_bytes <= case_limit, (
            entry["design"], prompt_bytes, case_limit
        )
        trusted_paths = {
            item["path"] for item in payload["trusted_instructions"]
        }
        assert all("harness-ability-to-evidence" not in path for path in trusted_paths)
        assert all("harness-test-design-catalog" not in path for path in trusted_paths)
        assert all("spec/behavioral-evals" not in path for path in trusted_paths)
        assert "id" not in payload["repository_fixture"]
        assert "kind" not in payload["repository_fixture"]

        fixture = binding.fixture
        if entry["dimension"] in {"capability_partition", "authority_partition"}:
            atoms = fixture.get("atoms")
            assert isinstance(atoms, list)
            atom_ids = {atom["id"] for atom in atoms}
            oracle_groups = binding.oracle["dimensions"][entry["dimension"]]["groups"]
            assert all(set(group) <= atom_ids for group in oracle_groups)
            if entry["design"] == "TD-CAP-001":
                assert atom_ids == {"E1"}
                assert oracle_groups == [["E1"]]
            if entry["design"] == "TD-CAP-003":
                assert atom_ids == {"P1", "P2", "A1"}
                assert sorted(oracle_groups) == sorted([["P1", "P2"], ["A1"]])
            field = "capabilities" if entry["dimension"] == "capability_partition" else "authorities"
            sample = {
                "version": 1,
                "kind": "harness-agent-behavioral-model-response",
                "output": {field: [{"support_atoms": group} for group in oracle_groups]},
            }
            parsed = _parse_model_response(json.dumps(sample), entry["dimension"])
            assert parsed["output"][field] == sample["output"][field]
        elif entry["dimension"] == "bootstrap_realization":
            assert entry["design"] == "TD-COMP-001"
            contract = _response_contract("bootstrap_realization")
            assert "core_model" in contract["schema"]["output"]
            assert entry["max_prompt_bytes"] == 32000
        else:
            contract = _response_contract("selected_operation")
            assert contract["schema"]["selected_operation"] == (
                "<one string from allowed_selected_operations>"
            )
            allowed = contract["allowed_selected_operations"]
            assert isinstance(allowed, list) and allowed
            assert all(isinstance(item, str) and item for item in allowed)
            expected = binding.oracle["dimensions"]["selected_operation"]
            registry = yaml.safe_load(
                (ROOT / "skills/consumer-operation-registry-v0.yaml").read_text(
                    encoding="utf-8"
                )
            )
            public = {
                item["operation"]
                for item in registry["routes"]
                if item.get("exposure") == "public"
            }
            assert expected in public
            parsed = _parse_model_response(
                json.dumps({
                    "version": 1,
                    "kind": "harness-agent-behavioral-model-response",
                    "selected_operation": expected,
                }),
                "selected_operation",
            )
            assert parsed["selected_operation"] == expected

COMP_TEMPLATE = BASE / "cases" / "td-comp-001" / "case.yaml.tmpl"
assert COMP_TEMPLATE.is_file()
with tempfile.TemporaryDirectory(prefix="behavioral-comp-case-") as temp:
    temp_root = Path(temp)
    shutil.copytree(COMP_TEMPLATE.parent, temp_root / "case")
    comp_runtime = temp_root / "case" / "case.yaml"
    comp_rendered = (temp_root / "case" / "case.yaml.tmpl").read_text(encoding="utf-8")
    comp_runtime.write_text(
        comp_rendered.replace("__HARNESS_REVISION__", "a" * 40),
        encoding="utf-8",
    )
    comp_binding = load_case(comp_runtime)
    assert comp_binding.case["case_id"] == "TD-COMP-001"
    assert comp_binding.case["test_level"] == "TL2"
    assert comp_binding.case["normalization_profile"]["dimensions"] == [
        "bootstrap_realization"
    ]

    comp_request = build_execution_request(
        comp_binding,
        run_id="TD-COMP-001-BOUNDARY",
        agent_descriptor=descriptor,
        agent_descriptor_sha256="b" * 64,
    )
    comp_payload = _model_payload(comp_request)
    assert comp_payload["authorized_operation_chain"] == [
        {"operation": "project-bootstrap-reconcile", "exposure": "public"},
        {
            "operation": "bootstrap-existing-project",
            "exposure": "internal",
            "invoked_by": "project-bootstrap-reconcile",
        },
    ]
    comp_routes = _bootstrap_route_context()
    assert comp_routes["entry"]["exposure"] == "public"
    assert comp_routes["internal"]["exposure"] == "internal"
    assert comp_routes["internal"]["invoked_by"] == "project-bootstrap-reconcile"

    comp_model = {
        "authorities": [{"id": "PAYMENT-DESIGN"}],
        "artifacts": [{
            "id": "LOCAL-ARTIFACT-ID",
            "authority": "PAYMENT-DESIGN",
            "path": "docs/payment-api.md",
            "provides": ["payment.idempotency-contract"],
            "depends_on": [],
        }],
        "questions": [],
    }
    from target_state import evaluate_target_state
    comp_target = evaluate_target_state(
        comp_binding.fixture["reviewed_design_profile"],
        comp_model,
    )
    comp_parsed = _parse_model_response(
        json.dumps({
            "version": 1,
            "kind": "harness-agent-behavioral-model-response",
            "output": {"core_model": comp_model},
        }),
        "bootstrap_realization",
    )
    comp_response = {
        "run_status": "COMPLETED",
        "output": {
            **comp_parsed["output"],
            "target_state": comp_target,
        },
    }
    comp_normalized = normalize_result(comp_binding, comp_response)
    assert score_result(comp_binding, comp_normalized)["status"] == "PASS"

    mutated_model = json.loads(json.dumps(comp_model))
    mutated_model["artifacts"].append({
        "id": "DUPLICATE-PROVIDER",
        "authority": "PAYMENT-DESIGN",
        "path": "docs/duplicate-payment-api.md",
        "provides": ["payment.idempotency-contract"],
        "depends_on": [],
    })
    mutated_normalized = normalize_result(
        comp_binding,
        {
            "run_status": "COMPLETED",
            "output": {
                "core_model": mutated_model,
                "target_state": evaluate_target_state(
                    comp_binding.fixture["reviewed_design_profile"],
                    mutated_model,
                ),
            },
        },
    )
    mutated_score = score_result(comp_binding, mutated_normalized)
    assert mutated_score["status"] == "FAIL"
    assert mutated_score["findings"] == [{
        "code": "WRONG_BOOTSTRAP_REALIZATION",
        "dimension": "bootstrap_realization",
    }]
    comp_prompt_bytes = len(_prompt(comp_request).encode("utf-8"))
    assert comp_prompt_bytes > 0

contaminated = dict(request)
contaminated["trusted_instruction_entrypoint"] = [
    "docs/design/harness-ability-to-evidence-v0.md"
]
try:
    _model_payload(contaminated)
except ValueError as exc:
    assert "evaluation/test artifact cannot be a trusted instruction" in str(exc)
else:
    raise AssertionError("assurance blueprint must be rejected as provider instruction")

total_prompt_bytes = sum(provider_prompt_bytes.values())
assert total_prompt_bytes <= max_suite, (total_prompt_bytes, max_suite)
print(
    f"first-wave behavioral eval cases: PASS ({len(entries)} cases); "
    f"provider_prompt_utf8_bytes total={total_prompt_bytes} "
    f"max_case={max(provider_prompt_bytes.values())}; "
    f"td_comp_001_prompt_utf8_bytes={comp_prompt_bytes}"
)
