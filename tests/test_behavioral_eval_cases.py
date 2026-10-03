#!/usr/bin/env python3
"""Validate first-wave behavioral cases and Copilot adapter boundary without a live call."""
from __future__ import annotations

import copy
import json
import shutil
import stat
import sys
import tempfile
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from evals.behavioral_eval import (
    build_execution_request,
    load_case,
    normalize_result,
    score_result,
)
from evals.greenfield_bootstrap_eval import (
    normalize_result as normalize_greenfield_result,
    score_result as score_greenfield_result,
)
from evals.adapters.copilot_greenfield_bootstrap_eval_agent import (
    _model_payload as _greenfield_model_payload,
    _parse_model_response as _parse_greenfield_model_response,
    _prompt as _greenfield_prompt,
)

from evals.adapters.copilot_behavioral_eval_agent import (
    _bootstrap_route_context,
    _model_payload,
    _observed_cli_version,
    _parse_copilot_jsonl,
    _parse_copilot_otel_jsonl,
    _parse_model_response,
    _prompt,
    _response_contract,
)

ADAPTER = ROOT / "evals" / "adapters" / "copilot_behavioral_eval_agent.py"
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
MANIFEST = yaml.safe_load(
    (BASE / "manifest-v0.yaml").read_text(encoding="utf-8")
)
EXPECTED = {
    "TD-CAP-001", "TD-CAP-002", "TD-CAP-003", "TD-CAP-004",
    "TD-AUTH-001", "TD-AUTH-002", "TD-AUTH-004",
    "TD-ROUTE-001", "TD-ROUTE-002", "TD-ROUTE-003",
    "TD-COMP-001",
    "TD-BOOT-E01", "TD-BOOT-E02", "TD-BOOT-E03", "TD-BOOT-E04", "TD-BOOT-E05",
}
assert MANIFEST["kind"] == "harness-agent-behavioral-eval-manifest"
entries = MANIFEST["cases"]
assert {item["design"] for item in entries} == EXPECTED
budget = MANIFEST["provider_prompt_budget"]
assert budget["metric"] == "utf8_bytes"
max_per_case = budget["max_per_case"]
max_suite = budget["max_suite"]
max_sequence_extra = budget["max_sequence_extra"]
assert isinstance(max_per_case, int) and max_per_case > 0
assert isinstance(max_suite, int) and max_suite >= max_per_case
assert isinstance(max_sequence_extra, int) and max_sequence_extra >= max_per_case
provider_prompt_bytes: dict[str, int] = {}
sequence_prompt_bytes = 0

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
            assert entry["design"] in {
                "TD-COMP-001",
                "TD-BOOT-E01", "TD-BOOT-E02", "TD-BOOT-E03",
                "TD-BOOT-E04", "TD-BOOT-E05",
            }
            contract = _response_contract("bootstrap_realization")
            assert "core_model" in contract["schema"]["output"]
            assert entry["max_prompt_bytes"] in {32000, 35000}
            if entry["design"] == "TD-BOOT-E04":
                assert binding.case["run_plan"] == {
                    "runs": 2,
                    "sequence": "bootstrap-idempotence",
                    "all_runs_must_pass": True,
                }
                reconcile_request = copy.deepcopy(request)
                reconcile_request["execution_context"] = {
                    "sequence": "bootstrap-idempotence",
                    "step": 2,
                    "phase": "reconcile-existing",
                }
                reconcile_request["repository_fixture"] = copy.deepcopy(
                    binding.fixture
                )
                reconcile_request["repository_fixture"]["existing_project"][
                    "harness_realization"
                ] = "current-and-usable"
                reconcile_request["repository_fixture"]["existing_project"][
                    "current_harness_realization"
                ] = {
                    "authorities": [{"id": "PAYMENT-DESIGN"}],
                    "artifacts": [{
                        "id": "PAYMENT-API",
                        "authority": "PAYMENT-DESIGN",
                        "path": "docs/payment-api.md",
                        "provides": ["payment.idempotency-contract"],
                        "depends_on": [],
                    }],
                    "questions": [],
                }
                reconcile_payload = _model_payload(reconcile_request)
                assert reconcile_payload["authorized_operation_chain"] == [
                    {
                        "operation": "project-bootstrap-reconcile",
                        "exposure": "public",
                    }
                ]
                reconcile_trusted = {
                    item["path"] for item in reconcile_payload["trusted_instructions"]
                }
                assert (
                    "skills/agent/bootstrap-existing-project/SKILL.md"
                    not in reconcile_trusted
                )
                reconcile_prompt_bytes = len(
                    _prompt(reconcile_request).encode("utf-8")
                )
                assert reconcile_prompt_bytes <= entry["max_prompt_bytes"], (
                    entry["design"],
                    reconcile_prompt_bytes,
                    entry["max_prompt_bytes"],
                )
                sequence_prompt_bytes += reconcile_prompt_bytes
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
    from harness.project_model.target_state import evaluate_target_state
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

e02_oracle = yaml.safe_load(
    (BASE / "cases/td-boot-e02/oracle.yaml").read_text(encoding="utf-8")
)
e05_oracle = yaml.safe_load(
    (BASE / "cases/td-boot-e05/oracle.yaml").read_text(encoding="utf-8")
)
assert e02_oracle["dimensions"]["bootstrap_realization"] == (
    e05_oracle["dimensions"]["bootstrap_realization"]
)
e05_fixture = yaml.safe_load(
    (BASE / "cases/td-boot-e05/fixture.yaml").read_text(encoding="utf-8")
)
assert len(e05_fixture["existing_project"]["unrelated_subtree"]) >= 8
assert any(
    "instruction authority" in item["summary"]
    for item in e05_fixture["existing_project"]["unrelated_subtree"]
)

E03_TEMPLATE = BASE / "cases/td-boot-e03/case.yaml.tmpl"
with tempfile.TemporaryDirectory(prefix="behavioral-e03-case-") as temp:
    temp_root = Path(temp)
    shutil.copytree(E03_TEMPLATE.parent, temp_root / "case")
    runtime = temp_root / "case" / "case.yaml"
    runtime.write_text(
        (temp_root / "case" / "case.yaml.tmpl")
        .read_text(encoding="utf-8")
        .replace("__HARNESS_REVISION__", "a" * 40),
        encoding="utf-8",
    )
    e03_binding = load_case(runtime)
    e03_model = {
        "authorities": [{"id": "REFUND-DESIGN"}],
        "artifacts": [],
        "questions": [{
            "id": "ARBITRARY-QUESTION-ID",
            "authority": "REFUND-DESIGN",
            "text": "The maximum refund window remains unresolved.",
            "blocks": [],
            "blocks_capabilities": ["refund.window-policy"],
            "answer_from": [],
        }],
    }
    from harness.project_model.target_state import evaluate_target_state
    e03_target = evaluate_target_state(
        e03_binding.fixture["reviewed_design_profile"],
        e03_model,
    )
    e03_normalized = normalize_result(
        e03_binding,
        {
            "run_status": "COMPLETED",
            "output": {
                "core_model": e03_model,
                "target_state": e03_target,
            },
        },
    )
    assert score_result(e03_binding, e03_normalized)["status"] == "PASS"

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
assert sequence_prompt_bytes <= max_sequence_extra, (
    sequence_prompt_bytes,
    max_sequence_extra,
)
execution_prompt_bound = total_prompt_bytes + sequence_prompt_bytes
assert execution_prompt_bound <= max_suite + max_sequence_extra, (
    execution_prompt_bound,
    max_suite + max_sequence_extra,
)
print(
    f"first-wave behavioral eval cases: PASS ({len(entries)} cases); "
    f"initial_provider_prompt_utf8_bytes={total_prompt_bytes} "
    f"sequence_extra_utf8_bytes={sequence_prompt_bytes} "
    f"execution_prompt_bound={execution_prompt_bound}; "
    f"max_case={max(provider_prompt_bytes.values())}; "
    f"td_comp_001_prompt_utf8_bytes={comp_prompt_bytes}"
)


TL4_BASE = ROOT / "spec" / "behavioral-evals" / "tl4-existing-project"
TL4_MANIFEST = yaml.safe_load(
    (TL4_BASE / "manifest-v0.yaml").read_text(encoding="utf-8")
)
TL4_EXPECTED = {"TD-COMP-003", "TD-BOOT-E06", "TD-QST-001"}
assert TL4_MANIFEST["kind"] == "harness-agent-behavioral-eval-manifest"
tl4_entries = TL4_MANIFEST["cases"]
assert {item["design"] for item in tl4_entries} == TL4_EXPECTED
tl4_budget = TL4_MANIFEST["provider_prompt_budget"]
assert tl4_budget["metric"] == "utf8_bytes"
tl4_max_per_call = tl4_budget["max_per_call"]
tl4_max_suite = tl4_budget["max_suite"]
assert isinstance(tl4_max_per_call, int) and tl4_max_per_call > 0
assert isinstance(tl4_max_suite, int) and tl4_max_suite >= tl4_max_per_call

TL4_WORKFLOW = ROOT / ".github" / "workflows" / "behavioral-eval-copilot-tl4.yml"
assert TL4_WORKFLOW.is_file()
tl4_workflow_text = TL4_WORKFLOW.read_text(encoding="utf-8")
assert "${{ inputs.model }}" not in tl4_workflow_text
assert 'MODEL="auto"' in tl4_workflow_text
assert 'MODEL_SELECTION="provider-auto"' in tl4_workflow_text
assert "spec/behavioral-evals/tl4-existing-project/manifest-v0.yaml" in tl4_workflow_text
assert "tl4-existing-project-behavioral-evidence" in tl4_workflow_text

tl4_execution_prompt_bytes = 0
for entry in tl4_entries:
    template = TL4_BASE / entry["template"]
    assert template.is_file(), entry
    with tempfile.TemporaryDirectory(prefix="behavioral-tl4-case-") as temp:
        temp_root = Path(temp)
        shutil.copytree(template.parent, temp_root / "case")
        runtime = temp_root / "case" / "case.yaml"
        rendered = (temp_root / "case" / "case.yaml.tmpl").read_text(
            encoding="utf-8"
        )
        runtime.write_text(
            rendered.replace("__HARNESS_REVISION__", "a" * 40),
            encoding="utf-8",
        )
        binding = load_case(runtime)
        assert binding.case["case_id"] == entry["design"]
        assert binding.case["test_level"] == "TL4"
        assert binding.case["run_plan"] == {
            "runs": 3,
            "all_runs_must_pass": True,
        }
        assert binding.case["normalization_profile"]["dimensions"] == [
            entry["dimension"]
        ]

        request = build_execution_request(
            binding,
            run_id=f"{entry['design']}-BOUNDARY",
            agent_descriptor=descriptor,
            agent_descriptor_sha256="b" * 64,
        )
        payload = _model_payload(request)
        serialized = json.dumps(payload, sort_keys=True)
        assert entry["design"] not in serialized
        prompt_bytes = len(_prompt(request).encode("utf-8"))
        assert prompt_bytes <= tl4_max_per_call, (
            entry["design"], prompt_bytes, tl4_max_per_call
        )
        tl4_execution_prompt_bytes += prompt_bytes * binding.case["run_plan"]["runs"]

        trusted_paths = {item["path"] for item in payload["trusted_instructions"]}
        assert all("harness-ability-to-evidence" not in path for path in trusted_paths)
        assert all("harness-test-design-catalog" not in path for path in trusted_paths)
        assert all("spec/behavioral-evals" not in path for path in trusted_paths)
        assert "id" not in payload["repository_fixture"]
        assert "kind" not in payload["repository_fixture"]

        if entry["design"] == "TD-COMP-003":
            assert entry["dimension"] == "selected_operation"
            expected = binding.oracle["dimensions"]["selected_operation"]
            assert expected == "project-bootstrap-reconcile"
            project_files = binding.fixture["project_context"]["project_files"]
            assert any("SYSTEM:" in item["content"] for item in project_files)
            assert any(
                "bootstrap-existing-project" in item["content"]
                for item in project_files
            )
            parsed = _parse_model_response(
                json.dumps({
                    "version": 1,
                    "kind": "harness-agent-behavioral-model-response",
                    "selected_operation": expected,
                }),
                "selected_operation",
            )
            assert parsed["selected_operation"] == expected
        elif entry["design"] == "TD-BOOT-E06":
            assert entry["dimension"] == "bootstrap_realization"
            assert payload["authorized_operation_chain"] == [
                {"operation": "project-bootstrap-reconcile", "exposure": "public"},
                {
                    "operation": "bootstrap-existing-project",
                    "exposure": "internal",
                    "invoked_by": "project-bootstrap-reconcile",
                },
            ]
            fixture = binding.fixture
            assert len(fixture["existing_project"]["unrelated_subtree"]) >= 4
            assert any(
                "Repository data only" in item["summary"]
                for item in fixture["existing_project"]["unrelated_subtree"]
            )
            e06_model = {
                "authorities": [
                    {"id": "ORDER-DESIGN"},
                    {"id": "DISPATCH-DESIGN"},
                ],
                "artifacts": [
                    {
                        "id": "ORDER-CONTRACT",
                        "authority": "ORDER-DESIGN",
                        "path": "docs/order-contract.md",
                        "provides": ["orders.lifecycle-contract"],
                        "depends_on": [],
                    },
                    {
                        "id": "DISPATCH-CONTRACT",
                        "authority": "DISPATCH-DESIGN",
                        "path": "docs/dispatch-contract.md",
                        "provides": ["orders.dispatch-contract"],
                        "depends_on": ["ORDER-CONTRACT"],
                    },
                ],
                "questions": [
                    {
                        "id": "ARBITRARY-QUESTION-ID",
                        "authority": "DISPATCH-DESIGN",
                        "text": "Retry policy remains unresolved.",
                        "blocks": [],
                        "blocks_capabilities": ["orders.retry-policy"],
                        "answer_from": [],
                    }
                ],
            }
            e06_target = evaluate_target_state(
                fixture["reviewed_design_profile"],
                e06_model,
            )
            e06_normalized = normalize_result(
                binding,
                {
                    "run_status": "COMPLETED",
                    "output": {
                        "core_model": e06_model,
                        "target_state": e06_target,
                    },
                },
            )
            assert score_result(binding, e06_normalized)["status"] == "PASS"
        else:
            assert entry["design"] == "TD-QST-001"
            assert entry["dimension"] == "bootstrap_realization"
            fixture = binding.fixture
            observations = fixture["existing_project"]["execution_observations"]
            assert len(observations) == 1
            assert observations[0]["outcome"] == "timeout"
            assert observations[0]["retryable"] is True
            qst_model = {
                "authorities": [{"id": "REFUND-DESIGN"}],
                "artifacts": [],
                "questions": [
                    {
                        "id": "ARBITRARY-QUESTION-ID",
                        "authority": "REFUND-DESIGN",
                        "text": "Refund-window policy remains unresolved.",
                        "blocks": [],
                        "blocks_capabilities": ["refund.window-policy"],
                        "answer_from": [],
                    }
                ],
            }
            qst_target = evaluate_target_state(
                fixture["reviewed_design_profile"],
                qst_model,
            )
            qst_normalized = normalize_result(
                binding,
                {
                    "run_status": "COMPLETED",
                    "output": {
                        "core_model": qst_model,
                        "target_state": qst_target,
                    },
                },
            )
            assert score_result(binding, qst_normalized)["status"] == "PASS"

assert tl4_execution_prompt_bytes <= tl4_max_suite, (
    tl4_execution_prompt_bytes,
    tl4_max_suite,
)
print(
    f"TL4 existing-project behavioral eval cases: PASS ({len(tl4_entries)} cases); "
    f"provider_calls={len(tl4_entries) * 3}; "
    f"execution_prompt_bound={tl4_execution_prompt_bytes}; "
    f"max_per_call={tl4_max_per_call}"
)

TL5_BASE = ROOT / "spec" / "behavioral-evals" / "tl5-known-project"
TL5_MANIFEST = yaml.safe_load(
    (TL5_BASE / "manifest-v0.yaml").read_text(encoding="utf-8")
)
TL5_EXPECTED = {"TD-BOOT-E07"}
assert TL5_MANIFEST["kind"] == "harness-agent-behavioral-eval-manifest"
tl5_entries = TL5_MANIFEST["cases"]
assert {item["design"] for item in tl5_entries} == TL5_EXPECTED
tl5_budget = TL5_MANIFEST["provider_prompt_budget"]
assert tl5_budget["metric"] == "utf8_bytes"
tl5_max_per_call = tl5_budget["max_per_call"]
tl5_max_suite = tl5_budget["max_suite"]
assert isinstance(tl5_max_per_call, int) and tl5_max_per_call > 0
assert isinstance(tl5_max_suite, int) and tl5_max_suite >= 2 * tl5_max_per_call

tl5_execution_prompt_bytes = 0
for entry in tl5_entries:
    template = TL5_BASE / entry["template"]
    assert template.is_file(), entry
    with tempfile.TemporaryDirectory(prefix="behavioral-tl5-case-") as temp:
        temp_root = Path(temp)
        shutil.copytree(template.parent, temp_root / "case")
        runtime = temp_root / "case" / "case.yaml"
        rendered = (temp_root / "case" / "case.yaml.tmpl").read_text(
            encoding="utf-8"
        )
        runtime.write_text(
            rendered.replace("__HARNESS_REVISION__", "a" * 40),
            encoding="utf-8",
        )
        binding = load_case(runtime)
        assert binding.case["case_id"] == entry["design"]
        assert binding.case["test_level"] == "TL5"
        assert binding.case["run_plan"] == {
            "runs": 2,
            "sequence": "bootstrap-idempotence",
            "all_runs_must_pass": True,
        }
        assert binding.case["normalization_profile"]["dimensions"] == [
            "bootstrap_realization"
        ]

        fixture = binding.fixture
        known = fixture["known_project"]
        assert known["repository"] == "lehater/napms"
        assert known["commit"] == "42481577fab7f795cf3a2118b7b6f1c3c075d066"
        assert known["classification"] == "known-project"
        assert known["source_artifacts"]["canonical_graph"]["git_blob_sha"] == (
            "a1c8c5d98c2b4cb927e9b424f3ea70fc0f89d2de"
        )
        assert known["source_artifacts"]["harness_projection"]["git_blob_sha"] == (
            "3e4d074e8ac4e67d259c4d0c721da62c0dff3b91"
        )
        assert binding.case["fixture_revision"] == "TD-BOOT-E07-FIXTURE-V2"
        expected_capabilities = {
            item["capability"]
            for item in fixture["reviewed_design_profile"]["expectations"]
        }
        projected_capabilities = {
            capability
            for item in fixture["existing_project"]["harness_projection"]["bindings"]
            for capability in item["provides"]
        }
        assert expected_capabilities == projected_capabilities

        request = build_execution_request(
            binding,
            run_id="TD-BOOT-E07-BOUNDARY",
            agent_descriptor=descriptor,
            agent_descriptor_sha256="b" * 64,
        )
        payload = _model_payload(request)
        serialized = json.dumps(payload, sort_keys=True)
        assert entry["design"] not in serialized
        trusted_paths = {item["path"] for item in payload["trusted_instructions"]}
        assert all("harness-ability-to-evidence" not in path for path in trusted_paths)
        assert all("harness-test-design-catalog" not in path for path in trusted_paths)
        assert all("spec/behavioral-evals" not in path for path in trusted_paths)
        assert "id" not in payload["repository_fixture"]
        assert "kind" not in payload["repository_fixture"]

        prompt_bytes = len(_prompt(request).encode("utf-8"))
        assert prompt_bytes <= tl5_max_per_call, (
            entry["design"], prompt_bytes, tl5_max_per_call
        )
        tl5_execution_prompt_bytes += prompt_bytes * 2

        model = {
            "authorities": [
                {"id": "DISCOVERY"},
                {"id": "PRODUCT-REQUIREMENTS"},
            ],
            "artifacts": [
                {
                    "id": "FIRST-MVP-HCD-PROBLEM-EVIDENCE",
                    "authority": "DISCOVERY",
                    "path": "docs/discovery/first-mvp-hcd-problem-evidence.yaml",
                    "provides": ["engineering.hcd.first-mvp.problem-evidence"],
                    "depends_on": [],
                },
                {
                    "id": "FIRST-MVP-HCD-USER-NEEDS",
                    "authority": "DISCOVERY",
                    "path": "docs/discovery/first-mvp-hcd-user-needs.yaml",
                    "provides": [
                        "engineering.hcd.application-components.user-needs",
                        "engineering.hcd.access-request.user-needs",
                        "engineering.hcd.policy-export.user-needs",
                    ],
                    "depends_on": ["FIRST-MVP-HCD-PROBLEM-EVIDENCE"],
                },
                {
                    "id": "FIRST-MVP-REQUIREMENTS",
                    "authority": "PRODUCT-REQUIREMENTS",
                    "path": "docs/requirements/first-mvp-product-requirements.yaml",
                    "provides": [
                        "engineering.requirements.product-intent",
                        "engineering.requirements.acceptance",
                        "engineering.hcd.application-components.requirements",
                        "engineering.hcd.access-request.requirements",
                        "engineering.hcd.policy-export.requirements",
                    ],
                    "depends_on": ["FIRST-MVP-HCD-USER-NEEDS"],
                },
            ],
            "questions": [],
        }
        target = evaluate_target_state(
            fixture["reviewed_design_profile"],
            model,
        )
        normalized = normalize_result(
            binding,
            {
                "run_status": "COMPLETED",
                "output": {
                    "core_model": model,
                    "target_state": target,
                },
            },
        )
        assert score_result(binding, normalized)["status"] == "PASS"

assert tl5_execution_prompt_bytes <= tl5_max_suite, (
    tl5_execution_prompt_bytes,
    tl5_max_suite,
)
print(
    f"TL5 known-project behavioral eval cases: PASS ({len(tl5_entries)} cases); "
    "provider_calls=2; "
    f"execution_prompt_bound={tl5_execution_prompt_bytes}; "
    f"max_per_call={tl5_max_per_call}"
)



FORMATION_BASE = ROOT / "spec" / "behavioral-evals" / "release-critical-formation"
FORMATION_MANIFEST = yaml.safe_load(
    (FORMATION_BASE / "manifest-v0.yaml").read_text(encoding="utf-8")
)
FORMATION_EXPECTED = {
    "TD-AUTH-003": ("TL1", "authority_partition", 1, {"A04-F03"}),
    "TD-AUTH-006": ("TL1", "authority_partition", 1, {"A04-F05"}),
    "TD-CAP-008": ("TL3", "capability_partition", 1, {"A05-F06", "A05-F07"}),
    "TD-CAP-007": ("TL4", "capability_partition", 3, {"A05-F08"}),
    "TD-AUTH-007": ("TL4", "authority_partition", 3, {"A04-F06"}),
}
assert FORMATION_MANIFEST["kind"] == "harness-agent-behavioral-eval-manifest"
formation_entries = FORMATION_MANIFEST["cases"]
assert {item["design"] for item in formation_entries} == set(FORMATION_EXPECTED)
formation_budget = FORMATION_MANIFEST["provider_prompt_budget"]
assert formation_budget["metric"] == "utf8_bytes"
formation_max_per_call = formation_budget["max_per_call"]
formation_max_suite = formation_budget["max_suite"]
assert isinstance(formation_max_per_call, int) and formation_max_per_call > 0
assert isinstance(formation_max_suite, int) and formation_max_suite >= 9 * formation_max_per_call

formation_prompt_bound = 0
formation_provider_calls = 0
for entry in formation_entries:
    template = FORMATION_BASE / entry["template"]
    assert template.is_file(), entry
    with tempfile.TemporaryDirectory(prefix="behavioral-formation-case-") as temp:
        temp_root = Path(temp)
        shutil.copytree(template.parent, temp_root / "case")
        runtime = temp_root / "case" / "case.yaml"
        rendered = (temp_root / "case" / "case.yaml.tmpl").read_text(
            encoding="utf-8"
        )
        runtime.write_text(
            rendered.replace("__HARNESS_REVISION__", "a" * 40),
            encoding="utf-8",
        )
        binding = load_case(runtime)
        expected_level, dimension, runs, failures = FORMATION_EXPECTED[entry["design"]]
        assert binding.case["case_id"] == entry["design"]
        assert binding.case["test_level"] == expected_level
        assert binding.case["normalization_profile"]["dimensions"] == [dimension]
        assert binding.case["pass_criteria"]["require_dimensions"] == [dimension]
        assert binding.case["run_plan"]["runs"] == runs
        assert binding.case["run_plan"]["all_runs_must_pass"] is True
        assert set(binding.case["failure_modes"]) == failures
        if entry["design"] == "TD-AUTH-003":
            assert binding.case["fixture_revision"] == "TD-AUTH-003-FIXTURE-V2"
            assert binding.oracle["dimensions"]["authority_partition"]["groups"] == [
                ["P1", "P2"], ["W2"]
            ]
            assert any(
                item["id"] == "C1"
                and "consumes" in item["statement"]
                and "does not define or version" in item["statement"]
                for item in binding.fixture["atoms"]
            )
        assert entry["runs"] == runs
        assert entry["dimension"] == dimension

        request = build_execution_request(
            binding,
            run_id=entry["design"] + "-BOUNDARY",
            agent_descriptor=descriptor,
            agent_descriptor_sha256="b" * 64,
        )
        payload = _model_payload(request)
        serialized = json.dumps(payload, sort_keys=True)
        assert entry["design"] not in serialized
        assert "id" not in payload["repository_fixture"]
        assert "kind" not in payload["repository_fixture"]
        trusted_paths = {item["path"] for item in payload["trusted_instructions"]}
        assert all("harness-ability-to-evidence" not in path for path in trusted_paths)
        assert all("harness-test-design-catalog" not in path for path in trusted_paths)

        prompt_bytes = len(_prompt(request).encode("utf-8"))
        assert prompt_bytes <= formation_max_per_call, (
            entry["design"], prompt_bytes, formation_max_per_call
        )
        formation_prompt_bound += prompt_bytes * runs
        formation_provider_calls += runs

        groups = binding.oracle["dimensions"][dimension]["groups"]
        field = "capabilities" if dimension == "capability_partition" else "authorities"
        response = {
            "run_status": "COMPLETED",
            "output": {
                field: [{"support_atoms": group} for group in groups],
            },
        }
        normalized = normalize_result(binding, response)
        scored = score_result(binding, normalized)
        assert scored["status"] == "PASS"
        assert scored["dimensions"][dimension]["status"] == "PASS"

assert formation_provider_calls == 9
assert formation_prompt_bound <= formation_max_suite, (
    formation_prompt_bound,
    formation_max_suite,
)
print(
    "Release-critical formation campaign: PASS "
    f"({len(formation_entries)} cases); provider_calls={formation_provider_calls}; "
    f"execution_prompt_bound={formation_prompt_bound}; "
    f"max_per_call={formation_max_per_call}"
)

TARGET_BASE = ROOT / "spec" / "behavioral-evals" / "design-target-selection"
TARGET_MANIFEST = yaml.safe_load(
    (TARGET_BASE / "manifest-v0.yaml").read_text(encoding="utf-8")
)
TARGET_EXPECTED = {
    "TD-CAP-005": ("TL1", 1, {"A05-F06", "A05-F02", "A08-F04"}),
    "TD-TARGET-001": ("TL1", 1, {"A08-F01", "A08-F02", "A08-F03"}),
    "TD-TARGET-002": ("TL3", 1, {"A08-F01", "A08-F02", "A08-F04"}),
    "TD-TARGET-003": ("TL4", 3, {"A08-F05"}),
}
assert TARGET_MANIFEST["kind"] == "harness-agent-behavioral-eval-manifest"
target_entries = TARGET_MANIFEST["cases"]
assert {item["design"] for item in target_entries} == set(TARGET_EXPECTED)
target_budget = TARGET_MANIFEST["provider_prompt_budget"]
assert target_budget["metric"] == "utf8_bytes"
target_max_per_call = target_budget["max_per_call"]
target_max_suite = target_budget["max_suite"]
assert isinstance(target_max_per_call, int) and target_max_per_call > 0
assert isinstance(target_max_suite, int) and target_max_suite >= 6 * target_max_per_call

target_prompt_bound = 0
target_provider_calls = 0
for entry in target_entries:
    template = TARGET_BASE / entry["template"]
    assert template.is_file(), entry
    with tempfile.TemporaryDirectory(prefix="behavioral-target-case-") as temp:
        temp_root = Path(temp)
        shutil.copytree(template.parent, temp_root / "case")
        runtime = temp_root / "case" / "case.yaml"
        rendered = (temp_root / "case" / "case.yaml.tmpl").read_text(
            encoding="utf-8"
        )
        runtime.write_text(
            rendered.replace("__HARNESS_REVISION__", "a" * 40),
            encoding="utf-8",
        )
        binding = load_case(runtime)
        expected_level, runs, failures = TARGET_EXPECTED[entry["design"]]
        assert binding.case["case_id"] == entry["design"]
        assert binding.case["test_level"] == expected_level
        assert binding.case["normalization_profile"]["dimensions"] == [
            "capability_partition"
        ]
        assert binding.case["pass_criteria"]["require_dimensions"] == [
            "capability_partition"
        ]
        assert binding.case["run_plan"] == {
            "runs": runs,
            "all_runs_must_pass": True,
        }
        assert set(binding.case["failure_modes"]) == failures
        assert entry["dimension"] == "capability_partition"
        assert entry["runs"] == runs

        request = build_execution_request(
            binding,
            run_id=entry["design"] + "-BOUNDARY",
            agent_descriptor=descriptor,
            agent_descriptor_sha256="b" * 64,
        )
        payload = _model_payload(request)
        serialized = json.dumps(payload, sort_keys=True)
        assert entry["design"] not in serialized
        assert "id" not in payload["repository_fixture"]
        assert "kind" not in payload["repository_fixture"]
        trusted_paths = {item["path"] for item in payload["trusted_instructions"]}
        assert all("harness-ability-to-evidence" not in path for path in trusted_paths)
        assert all("harness-test-design-catalog" not in path for path in trusted_paths)
        assert all("spec/behavioral-evals" not in path for path in trusted_paths)

        prompt_bytes = len(_prompt(request).encode("utf-8"))
        assert prompt_bytes <= target_max_per_call, (
            entry["design"], prompt_bytes, target_max_per_call
        )
        target_prompt_bound += prompt_bytes * runs
        target_provider_calls += runs

        groups = binding.oracle["dimensions"]["capability_partition"]["groups"]
        response = {
            "run_status": "COMPLETED",
            "output": {
                "capabilities": [{"support_atoms": group} for group in groups],
            },
        }
        normalized = normalize_result(binding, response)
        assert score_result(binding, normalized)["status"] == "PASS"

        selected_atoms = {atom for group in groups for atom in group}
        all_atoms = {atom["id"] for atom in binding.fixture["atoms"]}
        assert selected_atoms <= all_atoms
        if entry["design"] == "TD-TARGET-001":
            assert {"T1", "W1", "D1"}.isdisjoint(selected_atoms)
        elif entry["design"] == "TD-TARGET-002":
            assert {"D1", "D2", "D3"}.isdisjoint(selected_atoms)
            assert len(binding.fixture["repository_shape"]["selected_paths"]) >= 4
        elif entry["design"] == "TD-TARGET-003":
            assert {"T1", "W1", "D1"}.isdisjoint(selected_atoms)
        elif entry["design"] == "TD-CAP-005":
            assert {"D1", "D2"}.isdisjoint(selected_atoms)
            assert binding.fixture["reference_pressure"]

assert target_provider_calls == 6
assert target_prompt_bound <= target_max_suite, (
    target_prompt_bound,
    target_max_suite,
)
print(
    "Design-target selection campaign: PASS "
    f"({len(target_entries)} cases); provider_calls={target_provider_calls}; "
    f"execution_prompt_bound={target_prompt_bound}; "
    f"max_per_call={target_max_per_call}"
)


GREENFIELD_BASE = ROOT / "spec" / "behavioral-evals" / "greenfield-bootstrap"
GREENFIELD_MANIFEST = yaml.safe_load(
    (GREENFIELD_BASE / "manifest-v0.yaml").read_text(encoding="utf-8")
)
GREENFIELD_EXPECTED = {
    "TD-BOOT-G01": ("TL3", 1, {"A10-F01", "A10-F02", "A10-F03", "A10-F04"}),
    "TD-BOOT-G05": ("TL4", 3, {"A10-F05"}),
}
assert GREENFIELD_MANIFEST["kind"] == "harness-agent-behavioral-eval-manifest"
greenfield_entries = GREENFIELD_MANIFEST["cases"]
assert {item["design"] for item in greenfield_entries} == set(GREENFIELD_EXPECTED)
greenfield_budget = GREENFIELD_MANIFEST["provider_prompt_budget"]
assert greenfield_budget["metric"] == "utf8_bytes"
greenfield_max_per_call = greenfield_budget["max_per_call"]
greenfield_max_suite = greenfield_budget["max_suite"]
assert isinstance(greenfield_max_per_call, int) and greenfield_max_per_call > 0
assert isinstance(greenfield_max_suite, int) and greenfield_max_suite >= 4 * greenfield_max_per_call

greenfield_prompt_bound = 0
greenfield_provider_calls = 0
for entry in greenfield_entries:
    template = GREENFIELD_BASE / entry["template"]
    assert template.is_file(), entry
    with tempfile.TemporaryDirectory(prefix="behavioral-greenfield-case-") as temp:
        temp_root = Path(temp)
        shutil.copytree(template.parent, temp_root / "case")
        runtime = temp_root / "case" / "case.yaml"
        rendered = (temp_root / "case" / "case.yaml.tmpl").read_text(
            encoding="utf-8"
        )
        runtime.write_text(
            rendered.replace("__HARNESS_REVISION__", "a" * 40),
            encoding="utf-8",
        )
        binding = load_case(runtime)
        expected_level, runs, failures = GREENFIELD_EXPECTED[entry["design"]]
        assert binding.case["case_id"] == entry["design"]
        assert binding.case["abilities"] == ["HA-A10"]
        assert binding.case["test_level"] == expected_level
        assert binding.case["normalization_profile"]["dimensions"] == [
            "greenfield_bootstrap"
        ]
        assert binding.case["pass_criteria"]["require_dimensions"] == [
            "greenfield_bootstrap"
        ]
        assert binding.case["run_plan"] == {
            "runs": runs,
            "all_runs_must_pass": True,
        }
        assert set(binding.case["failure_modes"]) == failures
        assert entry["runs"] == runs
        assert entry["dimension"] == "greenfield_bootstrap"

        request = build_execution_request(
            binding,
            run_id=entry["design"] + "-BOUNDARY",
            agent_descriptor=descriptor,
            agent_descriptor_sha256="b" * 64,
        )
        payload = _greenfield_model_payload(request)
        serialized = json.dumps(payload, sort_keys=True)
        assert entry["design"] not in serialized
        assert "id" not in payload["repository_fixture"]
        assert "kind" not in payload["repository_fixture"]
        trusted_paths = {item["path"] for item in payload["trusted_instructions"]}
        assert all("harness-ability-to-evidence" not in path for path in trusted_paths)
        assert all("harness-test-design-catalog" not in path for path in trusted_paths)
        assert all("spec/behavioral-evals" not in path for path in trusted_paths)

        prompt_bytes = len(_greenfield_prompt(request).encode("utf-8"))
        assert prompt_bytes <= greenfield_max_per_call, (
            entry["design"], prompt_bytes, greenfield_max_per_call
        )
        greenfield_prompt_bound += prompt_bytes * runs
        greenfield_provider_calls += runs

        expected = binding.oracle["dimensions"]["greenfield_bootstrap"]
        provider_output = {
            "capabilities": copy.deepcopy(expected["capabilities"]),
            "questions": copy.deepcopy(expected["questions"]),
        }
        raw_response = json.dumps({
            "version": 1,
            "kind": "harness-agent-behavioral-model-response",
            "output": {"greenfield_bootstrap": provider_output},
        })
        parsed = _parse_greenfield_model_response(raw_response)
        normalized = normalize_greenfield_result(
            binding,
            {"run_status": "COMPLETED", **parsed},
        )
        scored = score_greenfield_result(binding, normalized)
        assert scored["status"] == "PASS"
        assert scored["dimensions"]["greenfield_bootstrap"]["status"] == "PASS"

        atom_ids = {atom["id"] for atom in binding.fixture["atoms"]}
        capability_atoms = {
            atom
            for capability in expected["capabilities"]
            for atom in capability["support_atoms"]
        }
        question_atoms = {
            atom
            for question in expected["questions"]
            for atom in question["support_atoms"]
        }
        assert capability_atoms | question_atoms <= atom_ids
        assert {"D1", "D2"}.isdisjoint(capability_atoms | question_atoms)
        assert expected["questions"] == [{
            "support_atoms": ["U1"],
            "blocks_atoms": ["K5"],
        }]
        frontier = {
            tuple(item["support_atoms"]): item["disposition"]
            for item in expected["frontier"]
        }
        assert frontier == {
            ("K1",): "CREATE",
            ("K2", "K3"): "CREATE",
            ("K4",): "PENDING",
            ("K5",): "PENDING",
        }
        assert "COMPLETE" not in frontier.values()

        compatible = copy.deepcopy(provider_output)
        compatible["questions"][0]["support_atoms"] = ["U1", "K5"]
        compatible_normalized = normalize_greenfield_result(
            binding,
            {
                "run_status": "COMPLETED",
                "output": {"greenfield_bootstrap": compatible},
            },
        )
        assert score_greenfield_result(
            binding,
            compatible_normalized,
        )["status"] == "PASS"

        missing_unresolved = copy.deepcopy(provider_output)
        missing_unresolved["questions"][0]["support_atoms"] = ["K5"]
        missing_normalized = normalize_greenfield_result(
            binding,
            {
                "run_status": "COMPLETED",
                "output": {"greenfield_bootstrap": missing_unresolved},
            },
        )
        assert score_greenfield_result(
            binding,
            missing_normalized,
        )["status"] == "FAIL"

        unrelated_support = copy.deepcopy(provider_output)
        unrelated_support["questions"][0]["support_atoms"] = ["U1", "D1"]
        unrelated_normalized = normalize_greenfield_result(
            binding,
            {
                "run_status": "COMPLETED",
                "output": {"greenfield_bootstrap": unrelated_support},
            },
        )
        assert score_greenfield_result(
            binding,
            unrelated_normalized,
        )["status"] == "FAIL"

        missing_prerequisite = copy.deepcopy(provider_output)
        for capability in missing_prerequisite["capabilities"]:
            if capability["support_atoms"] == ["K4"]:
                capability["prerequisite_atoms"] = []
        prerequisite_normalized = normalize_greenfield_result(
            binding,
            {
                "run_status": "COMPLETED",
                "output": {"greenfield_bootstrap": missing_prerequisite},
            },
        )
        assert any(
            item["support_atoms"] == ["K4"]
            and item["disposition"] == "CREATE"
            for item in prerequisite_normalized["greenfield_bootstrap"]["frontier"]
        )
        assert score_greenfield_result(
            binding,
            prerequisite_normalized,
        )["status"] == "FAIL"

assert greenfield_provider_calls == 4
assert greenfield_prompt_bound <= greenfield_max_suite, (
    greenfield_prompt_bound,
    greenfield_max_suite,
)
print(
    "Greenfield bootstrap campaign: PASS "
    f"({len(greenfield_entries)} cases); provider_calls={greenfield_provider_calls}; "
    f"execution_prompt_bound={greenfield_prompt_bound}; "
    f"max_per_call={greenfield_max_per_call}"
)

GREENFIELD_WORKFLOW = (
    ROOT / ".github" / "workflows" / "greenfield-bootstrap-assurance.yml"
)
greenfield_workflow_text = GREENFIELD_WORKFLOW.read_text(encoding="utf-8")
assert "ready_for_review" in greenfield_workflow_text
assert "workflow_dispatch" in greenfield_workflow_text
assert "spec/behavioral-evals/greenfield-bootstrap/**" in greenfield_workflow_text
assert 'MODEL="auto"' in greenfield_workflow_text
assert 'MODEL_SELECTION="provider-auto"' in greenfield_workflow_text

CAMPAIGN_WORKFLOW = ROOT / ".github" / "workflows" / "assurance-campaign-copilot.yml"
campaign_workflow_text = CAMPAIGN_WORKFLOW.read_text(encoding="utf-8")
assert 'default: all' in campaign_workflow_text
assert 'release-critical-formation' in campaign_workflow_text
assert 'design-target-selection' in campaign_workflow_text
assert 'tl5-known-project' in campaign_workflow_text
assert 'tl4-existing-project' in campaign_workflow_text
assert 'first-wave' in campaign_workflow_text
assert 'MODEL="auto"' in campaign_workflow_text
assert 'MODEL_SELECTION="provider-auto"' in campaign_workflow_text
assert "inputs.model" not in campaign_workflow_text
print("Assurance campaign workflow structure: PASS")
