#!/usr/bin/env python3
"""Provider-neutral substrate for clean-context Harness agent behavioral evaluations."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import tempfile
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

import yaml

ROOT = Path(__file__).resolve().parent

CASE_REQUIRED_FIELDS = {
    "case_id",
    "abilities",
    "failure_modes",
    "test_level",
    "fixture_revision",
    "harness_revision",
    "user_task",
    "selected_scope",
    "repository_fixture",
    "trusted_instruction_entrypoint",
    "allowed_tools",
    "write_policy",
    "oracle_ref",
    "normalization_profile",
    "pass_criteria",
    "run_plan",
}
VALID_WRITE_POLICIES = {"read-only", "ephemeral-workspace", "captured-output"}
VALID_RUN_STATUSES = {"COMPLETED", "INCOMPLETE", "INVALID", "EXECUTION_ERROR"}
FORBIDDEN_RESPONSE_KEYS = {"chain_of_thought", "reasoning", "thoughts", "private_reasoning"}
ALLOWED_ENV = (
    "PATH",
    "GITHUB_TOKEN",
    "COPILOT_GITHUB_TOKEN",
    "GH_TOKEN",
    "HTTPS_PROXY",
    "HTTP_PROXY",
    "NO_PROXY",
    "SSL_CERT_FILE",
    "NODE_EXTRA_CA_CERTS",
)


class BehavioralEvalError(ValueError):
    """Invalid behavioral-evaluation contract or result."""


@dataclass(frozen=True)
class FrozenBinding:
    case: dict[str, Any]
    fixture: Any
    oracle: dict[str, Any]
    case_path: Path
    fixture_path: Path
    oracle_path: Path
    case_sha256: str
    fixture_sha256: str
    oracle_sha256: str


class ExecutionAdapter(Protocol):
    def execute(
        self,
        request: dict[str, Any],
        *,
        agent_descriptor: dict[str, Any],
    ) -> dict[str, Any]:
        """Execute one clean-context run and return an observable response."""


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _load_structured_bytes(path: Path, raw: bytes) -> Any:
    suffix = path.suffix.lower()
    text = raw.decode("utf-8")
    if suffix in {".yaml", ".yml"}:
        return yaml.safe_load(text)
    if suffix == ".json":
        return json.loads(text)
    return text


def _resolve_case_ref(case_path: Path, ref: Any, label: str) -> Path:
    if not isinstance(ref, dict) or not isinstance(ref.get("path"), str):
        raise BehavioralEvalError(f"{label} must contain path")
    resolved = (case_path.parent / ref["path"]).resolve()
    case_root = case_path.parent.resolve()
    try:
        resolved.relative_to(case_root)
    except ValueError as exc:
        raise BehavioralEvalError(f"{label} escapes case directory") from exc
    if not resolved.is_file():
        raise BehavioralEvalError(f"{label} does not exist: {ref['path']}")
    return resolved


def _require_string_list(value: Any, label: str, *, nonempty: bool = True) -> list[str]:
    if not isinstance(value, list):
        raise BehavioralEvalError(f"{label} must be a list")
    if nonempty and not value:
        raise BehavioralEvalError(f"{label} must be non-empty")
    if not all(isinstance(item, str) and item for item in value):
        raise BehavioralEvalError(f"{label} must contain non-empty strings")
    return value


def load_case(path: str | Path) -> FrozenBinding:
    case_path = Path(path).resolve()
    raw_case = case_path.read_bytes()
    case = _load_structured_bytes(case_path, raw_case)
    if not isinstance(case, dict):
        raise BehavioralEvalError("behavioral case must contain a mapping")
    if case.get("version") != 1 or case.get("kind") != "harness-agent-behavioral-eval-case":
        raise BehavioralEvalError("unexpected behavioral case kind/version")

    missing = CASE_REQUIRED_FIELDS - set(case)
    if missing:
        raise BehavioralEvalError("behavioral case missing fields: " + ", ".join(sorted(missing)))

    if not isinstance(case["case_id"], str) or not case["case_id"]:
        raise BehavioralEvalError("case_id must be a non-empty string")
    _require_string_list(case["abilities"], "abilities")
    _require_string_list(case["failure_modes"], "failure_modes")
    if case["test_level"] not in {f"TL{i}" for i in range(7)}:
        raise BehavioralEvalError("invalid test_level")
    for field in ("fixture_revision", "harness_revision", "user_task", "selected_scope"):
        if not isinstance(case[field], str) or not case[field]:
            raise BehavioralEvalError(f"{field} must be a non-empty string")
    _require_string_list(case["trusted_instruction_entrypoint"], "trusted_instruction_entrypoint")
    _require_string_list(case["allowed_tools"], "allowed_tools", nonempty=False)
    if case["write_policy"] not in VALID_WRITE_POLICIES:
        raise BehavioralEvalError("invalid write_policy")
    if not isinstance(case["normalization_profile"], dict):
        raise BehavioralEvalError("normalization_profile must be a mapping")
    dimensions = case["normalization_profile"].get("dimensions")
    _require_string_list(dimensions, "normalization_profile.dimensions")
    if not isinstance(case["pass_criteria"], dict):
        raise BehavioralEvalError("pass_criteria must be a mapping")
    if not isinstance(case["run_plan"], dict):
        raise BehavioralEvalError("run_plan must be a mapping")
    runs = case["run_plan"].get("runs")
    if not isinstance(runs, int) or runs < 1:
        raise BehavioralEvalError("run_plan.runs must be a positive integer")

    fixture_path = _resolve_case_ref(case_path, case["repository_fixture"], "repository_fixture")
    oracle_path = _resolve_case_ref(case_path, case["oracle_ref"], "oracle_ref")
    raw_fixture = fixture_path.read_bytes()
    raw_oracle = oracle_path.read_bytes()
    fixture = _load_structured_bytes(fixture_path, raw_fixture)
    oracle = _load_structured_bytes(oracle_path, raw_oracle)
    if not isinstance(oracle, dict):
        raise BehavioralEvalError("oracle must contain a mapping")
    if oracle.get("version") != 1 or oracle.get("kind") != "harness-agent-behavioral-eval-oracle":
        raise BehavioralEvalError("unexpected oracle kind/version")
    if not isinstance(oracle.get("dimensions"), dict):
        raise BehavioralEvalError("oracle dimensions must be a mapping")

    return FrozenBinding(
        case=case,
        fixture=fixture,
        oracle=oracle,
        case_path=case_path,
        fixture_path=fixture_path,
        oracle_path=oracle_path,
        case_sha256=_sha256(raw_case),
        fixture_sha256=_sha256(raw_fixture),
        oracle_sha256=_sha256(raw_oracle),
    )


def load_agent_descriptor(path: str | Path) -> tuple[dict[str, Any], str]:
    path = Path(path)
    raw = path.read_bytes()
    value = _load_structured_bytes(path, raw)
    if not isinstance(value, dict):
        raise BehavioralEvalError("agent descriptor must contain a mapping")
    for field in ("id", "provider", "model", "model_version", "configuration"):
        if field not in value:
            raise BehavioralEvalError(f"agent descriptor missing {field}")
    if not isinstance(value["configuration"], dict):
        raise BehavioralEvalError("agent descriptor configuration must be a mapping")
    return value, _sha256(raw)


def build_execution_request(
    binding: FrozenBinding,
    *,
    run_id: str,
    agent_descriptor: dict[str, Any],
    agent_descriptor_sha256: str,
) -> dict[str, Any]:
    case = binding.case
    return {
        "version": 1,
        "kind": "harness-agent-behavioral-eval-request",
        "run_id": run_id,
        "case_id": case["case_id"],
        "bindings": {
            "harness_revision": case["harness_revision"],
            "fixture_revision": case["fixture_revision"],
            "consumer_pack_revision": case.get("consumer_pack_revision"),
            "case_sha256": binding.case_sha256,
            "fixture_sha256": binding.fixture_sha256,
            "agent_descriptor_sha256": agent_descriptor_sha256,
        },
        "user_task": case["user_task"],
        "selected_scope": case["selected_scope"],
        "repository_fixture": binding.fixture,
        "trusted_instruction_entrypoint": case["trusted_instruction_entrypoint"],
        "allowed_tools": case["allowed_tools"],
        "write_policy": case["write_policy"],
        "normalization_profile": case["normalization_profile"],
        "agent_descriptor": agent_descriptor,
        "response_contract": {
            "version": 1,
            "kind": "harness-agent-behavioral-eval-response",
            "run_status": sorted(VALID_RUN_STATUSES),
            "private_reasoning_forbidden": True,
            "observable_fields": [
                "selected_operation",
                "resolved_routes",
                "output",
                "validator_results",
                "execution_findings",
                "trace",
                "provenance",
            ],
        },
    }


def _sanitized_env(home: Path) -> dict[str, str]:
    env = {key: os.environ[key] for key in ALLOWED_ENV if key in os.environ}
    env.update(
        {
            "HOME": str(home),
            "XDG_CONFIG_HOME": str(home / ".config"),
            "XDG_CACHE_HOME": str(home / ".cache"),
        }
    )
    return env


def _invalid_response(message: str, *, provenance: dict[str, Any]) -> dict[str, Any]:
    return {
        "version": 1,
        "kind": "harness-agent-behavioral-eval-response",
        "run_status": "INVALID",
        "execution_findings": [{"code": "INVALID_RESPONSE", "message": message}],
        "provenance": provenance,
    }


class ProcessExecutionAdapter:
    """JSON stdin/stdout adapter; every call receives fresh HOME and cwd."""

    def __init__(
        self,
        executable: str,
        args: list[str] | None = None,
        *,
        timeout_seconds: float = 120.0,
    ) -> None:
        self.executable = executable
        self.args = list(args or [])
        self.timeout_seconds = timeout_seconds

    def execute(
        self,
        request: dict[str, Any],
        *,
        agent_descriptor: dict[str, Any],
    ) -> dict[str, Any]:
        del agent_descriptor
        with tempfile.TemporaryDirectory(prefix="harness-behavioral-eval-") as temp:
            root = Path(temp)
            home = root / "home"
            work = root / "work"
            home.mkdir()
            work.mkdir()
            provenance = {
                "adapter": "process-json-v1",
                "fresh_home": True,
                "isolated_working_directory": True,
                "executable": self.executable,
                "args": self.args,
            }
            try:
                completed = subprocess.run(
                    [self.executable, *self.args],
                    input=json.dumps(request, ensure_ascii=False),
                    text=True,
                    capture_output=True,
                    cwd=work,
                    env=_sanitized_env(home),
                    check=False,
                    timeout=self.timeout_seconds,
                )
            except (OSError, subprocess.TimeoutExpired) as exc:
                return {
                    "version": 1,
                    "kind": "harness-agent-behavioral-eval-response",
                    "run_status": "EXECUTION_ERROR",
                    "execution_findings": [{"code": "EVAL_INFRASTRUCTURE_FAILURE", "message": f"{exc.__class__.__name__}: {exc}"}],
                    "provenance": provenance,
                }

            if completed.returncode != 0:
                return {
                    "version": 1,
                    "kind": "harness-agent-behavioral-eval-response",
                    "run_status": "EXECUTION_ERROR",
                    "execution_findings": [{"code": "EVAL_INFRASTRUCTURE_FAILURE", "message": f"adapter process exited {completed.returncode}: " + completed.stderr.strip()[:1000]}],
                    "provenance": provenance,
                }

            try:
                value = json.loads(completed.stdout)
            except json.JSONDecodeError:
                return _invalid_response("adapter stdout is not one JSON object", provenance=provenance)
            if not isinstance(value, dict):
                return _invalid_response("adapter response must be a JSON object", provenance=provenance)
            if value.get("version") != 1 or value.get("kind") != "harness-agent-behavioral-eval-response":
                return _invalid_response("unexpected response kind/version", provenance=provenance)
            if value.get("run_status") not in VALID_RUN_STATUSES:
                return _invalid_response("unknown run_status", provenance=provenance)
            forbidden = FORBIDDEN_RESPONSE_KEYS & set(value)
            if forbidden:
                return _invalid_response("private reasoning fields are forbidden: " + ", ".join(sorted(forbidden)), provenance=provenance)
            provider_provenance = value.get("provenance")
            if provider_provenance is not None and not isinstance(provider_provenance, dict):
                return _invalid_response("provider provenance must be a mapping", provenance=provenance)
            value["provenance"] = {**provenance, "provider": provider_provenance or {}}
            return value


def _canonical_groups(value: Any, *, field: str) -> list[list[str]]:
    if not isinstance(value, list):
        raise BehavioralEvalError(f"{field} must be a list")
    groups: list[list[str]] = []
    for index, item in enumerate(value):
        if not isinstance(item, dict):
            raise BehavioralEvalError(f"{field}[{index}] must be a mapping")
        atoms = item.get("atoms")
        if atoms is None:
            atoms = item.get("support_atoms")
        atoms = _require_string_list(atoms, f"{field}[{index}].atoms")
        groups.append(sorted(set(atoms)))
    return sorted(groups)


def _canonical_target_state(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise BehavioralEvalError(f"{label} must be a mapping")

    def normalize_items(name: str) -> list[dict[str, Any]]:
        raw = value.get(name)
        if not isinstance(raw, list):
            raise BehavioralEvalError(f"{label}.{name} must be a list")
        items: list[dict[str, Any]] = []
        for index, item in enumerate(raw):
            if not isinstance(item, dict):
                raise BehavioralEvalError(f"{label}.{name}[{index}] must be a mapping")
            normalized = {
                key: item[key]
                for key in ("expectation", "subject", "capability", "authority")
                if key in item
            }
            if "depends_on" in item:
                normalized["depends_on"] = sorted(
                    _require_string_list(
                        item["depends_on"],
                        f"{label}.{name}[{index}].depends_on",
                        nonempty=False,
                    )
                )
            if "questions" in item:
                normalized["questions"] = sorted(
                    _require_string_list(
                        item["questions"],
                        f"{label}.{name}[{index}].questions",
                        nonempty=False,
                    )
                )
            items.append(normalized)
        return sorted(items, key=lambda item: json.dumps(item, sort_keys=True))

    status = value.get("status")
    if status not in {"COMPLETE", "READY", "BLOCKED"}:
        raise BehavioralEvalError(f"{label}.status is invalid")
    return {
        "status": status,
        "satisfied": sorted(
            _require_string_list(value.get("satisfied"), f"{label}.satisfied", nonempty=False)
        ),
        "create": normalize_items("create"),
        "wait": normalize_items("wait"),
        "pending": normalize_items("pending"),
    }


def _canonical_bootstrap_model(model: Any) -> dict[str, Any]:
    if not isinstance(model, dict):
        raise BehavioralEvalError("bootstrap core_model must be a mapping")
    try:
        from harness import validate_model
        validate_model(model)
    except Exception as exc:
        raise BehavioralEvalError(f"bootstrap core_model is invalid: {exc}") from exc

    authorities = model.get("authorities")
    artifacts = model.get("artifacts")
    questions = model.get("questions")
    if not all(isinstance(value, list) for value in (authorities, artifacts, questions)):
        raise BehavioralEvalError("bootstrap core_model collections must be lists")

    id_to_path = {item["id"]: item["path"] for item in artifacts}
    normalized_artifacts = [
        {
            "path": item["path"],
            "authority": item["authority"],
            "provides": sorted(item.get("provides", []) or []),
            "depends_on_paths": sorted(
                id_to_path[dependency] for dependency in (item.get("depends_on", []) or [])
            ),
        }
        for item in artifacts
    ]
    return {
        "authorities": sorted(item["id"] for item in authorities),
        "artifacts": sorted(
            normalized_artifacts,
            key=lambda item: json.dumps(item, sort_keys=True),
        ),
        "question_count": len(questions),
    }


def _canonical_bootstrap_oracle(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise BehavioralEvalError("oracle bootstrap_realization must be a mapping")
    core = value.get("core_model")
    if not isinstance(core, dict):
        raise BehavioralEvalError("oracle bootstrap_realization.core_model must be a mapping")
    artifacts = core.get("artifacts")
    if not isinstance(artifacts, list):
        raise BehavioralEvalError("oracle bootstrap_realization.core_model.artifacts must be a list")
    normalized_artifacts = []
    for item in artifacts:
        if not isinstance(item, dict):
            raise BehavioralEvalError("oracle bootstrap artifact must be a mapping")
        normalized_artifacts.append({
            "path": item.get("path"),
            "authority": item.get("authority"),
            "provides": sorted(item.get("provides", []) or []),
            "depends_on_paths": sorted(item.get("depends_on_paths", []) or []),
        })
    return {
        "core_model": {
            "authorities": sorted(core.get("authorities", []) or []),
            "artifacts": sorted(
                normalized_artifacts,
                key=lambda item: json.dumps(item, sort_keys=True),
            ),
            "question_count": core.get("question_count"),
        },
        "target_state": _canonical_target_state(
            value.get("target_state"),
            "oracle bootstrap_realization.target_state",
        ),
    }


def normalize_result(binding: FrozenBinding, response: dict[str, Any]) -> dict[str, Any]:
    dimensions = binding.case["normalization_profile"]["dimensions"]
    output = response.get("output") or {}
    if not isinstance(output, dict):
        raise BehavioralEvalError("response output must be a mapping")
    normalized: dict[str, Any] = {}
    for dimension in dimensions:
        if dimension == "selected_operation":
            selected = response.get("selected_operation")
            if not isinstance(selected, str) or not selected:
                raise BehavioralEvalError("selected_operation is required")
            normalized[dimension] = selected
        elif dimension == "capability_partition":
            normalized[dimension] = _canonical_groups(output.get("capabilities"), field="capabilities")
        elif dimension == "authority_partition":
            normalized[dimension] = _canonical_groups(output.get("authorities"), field="authorities")
        elif dimension == "bootstrap_realization":
            normalized[dimension] = {
                "core_model": _canonical_bootstrap_model(output.get("core_model")),
                "target_state": _canonical_target_state(
                    output.get("target_state"),
                    "bootstrap target_state",
                ),
            }
        else:
            raise BehavioralEvalError(f"unsupported normalization dimension: {dimension}")
    return normalized


def _normalize_oracle_dimension(name: str, value: Any) -> Any:
    if name == "selected_operation":
        if not isinstance(value, str) or not value:
            raise BehavioralEvalError("oracle selected_operation must be a string")
        return value
    if name in {"capability_partition", "authority_partition"}:
        if not isinstance(value, dict):
            raise BehavioralEvalError(f"oracle {name} must be a mapping")
        groups = value.get("groups")
        if not isinstance(groups, list):
            raise BehavioralEvalError(f"oracle {name}.groups must be a list")
        normalized: list[list[str]] = []
        for index, group in enumerate(groups):
            atoms = _require_string_list(group, f"oracle {name}.groups[{index}]")
            normalized.append(sorted(set(atoms)))
        return sorted(normalized)
    if name == "bootstrap_realization":
        return _canonical_bootstrap_oracle(value)
    raise BehavioralEvalError(f"unsupported oracle dimension: {name}")


def score_result(binding: FrozenBinding, normalized: dict[str, Any]) -> dict[str, Any]:
    required = _require_string_list(
        binding.case["pass_criteria"].get("require_dimensions"),
        "pass_criteria.require_dimensions",
    )
    findings: list[dict[str, Any]] = []
    dimensions: dict[str, Any] = {}
    for name in required:
        if name not in normalized:
            raise BehavioralEvalError(f"normalized result lacks required dimension {name}")
        if name not in binding.oracle["dimensions"]:
            raise BehavioralEvalError(f"oracle lacks required dimension {name}")
        expected = _normalize_oracle_dimension(name, binding.oracle["dimensions"][name])
        actual = normalized[name]
        passed = actual == expected
        dimensions[name] = {"status": "PASS" if passed else "FAIL", "expected": expected, "actual": actual}
        if not passed:
            findings.append({
                "code": {
                    "selected_operation": "WRONG_OPERATION",
                    "capability_partition": "WRONG_GRANULARITY",
                    "authority_partition": "WRONG_AUTHORITY_PARTITION",
                    "bootstrap_realization": "WRONG_BOOTSTRAP_REALIZATION",
                }[name],
                "dimension": name,
            })
    return {"status": "PASS" if not findings else "FAIL", "dimensions": dimensions, "findings": findings}


def build_run_record(
    binding: FrozenBinding,
    *,
    run_id: str,
    agent_descriptor: dict[str, Any],
    agent_descriptor_sha256: str,
    response: dict[str, Any],
) -> dict[str, Any]:
    run_status = response["run_status"]
    normalized: dict[str, Any] | None = None
    correctness: dict[str, Any] = {"status": "NOT_SCORED", "dimensions": {}, "findings": []}
    if run_status == "COMPLETED":
        try:
            normalized = normalize_result(binding, response)
            correctness = score_result(binding, normalized)
        except BehavioralEvalError as exc:
            run_status = "INCOMPLETE"
            correctness = {"status": "NOT_SCORED", "dimensions": {}, "findings": [{"code": "STRUCTURALLY_INVALID_OUTPUT", "message": str(exc)}]}

    record = {
        "version": 1,
        "kind": "harness-agent-behavioral-eval-run",
        "run_id": run_id,
        "case_id": binding.case["case_id"],
        "harness_revision": binding.case["harness_revision"],
        "fixture_revision": binding.case["fixture_revision"],
        "consumer_pack_revision": binding.case.get("consumer_pack_revision"),
        "agent_descriptor": agent_descriptor,
        "bindings": {
            "case_sha256": binding.case_sha256,
            "fixture_sha256": binding.fixture_sha256,
            "oracle_sha256": binding.oracle_sha256,
            "agent_descriptor_sha256": agent_descriptor_sha256,
        },
        "started_from_clean_context": bool(response.get("provenance", {}).get("fresh_home") and response.get("provenance", {}).get("isolated_working_directory")),
        "selected_operation": response.get("selected_operation"),
        "resolved_routes": response.get("resolved_routes", []),
        "output_refs": response.get("output_refs", []),
        "normalization_result": normalized,
        "validator_results": response.get("validator_results", []),
        "execution_findings": response.get("execution_findings", []),
        "trace": response.get("trace", []),
        "run_status": run_status,
        "correctness": correctness,
        "provenance": response.get("provenance", {}),
    }
    canonical = json.dumps(record, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    record["record_sha256"] = _sha256(canonical.encode("utf-8"))
    return record


def write_run_record(path: str | Path, record: dict[str, Any]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("x", encoding="utf-8") as handle:
        json.dump(record, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")


def execute_case(
    binding: FrozenBinding,
    *,
    adapter: ExecutionAdapter,
    agent_descriptor: dict[str, Any],
    agent_descriptor_sha256: str,
    output_dir: str | Path,
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for index in range(1, binding.case["run_plan"]["runs"] + 1):
        run_id = f"{binding.case['case_id']}-R{index:02d}-{uuid.uuid4().hex[:12]}"
        request = build_execution_request(binding, run_id=run_id, agent_descriptor=agent_descriptor, agent_descriptor_sha256=agent_descriptor_sha256)
        response = adapter.execute(request, agent_descriptor=agent_descriptor)
        record = build_run_record(binding, run_id=run_id, agent_descriptor=agent_descriptor, agent_descriptor_sha256=agent_descriptor_sha256, response=response)
        write_run_record(Path(output_dir) / f"{run_id}.json", record)
        records.append(record)
    return records


def main() -> int:
    parser = argparse.ArgumentParser(description="Run one Harness behavioral eval case")
    parser.add_argument("case")
    parser.add_argument("--agent-descriptor", required=True)
    parser.add_argument("--adapter-executable", required=True)
    parser.add_argument("--adapter-arg", action="append", default=[])
    parser.add_argument("--timeout-seconds", type=float, default=120.0)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--json-summary")
    args = parser.parse_args()
    try:
        binding = load_case(args.case)
        descriptor, descriptor_sha = load_agent_descriptor(args.agent_descriptor)
        records = execute_case(
            binding,
            adapter=ProcessExecutionAdapter(args.adapter_executable, args.adapter_arg, timeout_seconds=args.timeout_seconds),
            agent_descriptor=descriptor,
            agent_descriptor_sha256=descriptor_sha,
            output_dir=args.output_dir,
        )
    except (BehavioralEvalError, OSError, yaml.YAMLError, json.JSONDecodeError) as exc:
        print(f"Behavioral eval failed: {exc}", file=os.sys.stderr)
        return 2

    summary = {
        "case_id": binding.case["case_id"],
        "runs": len(records),
        "run_statuses": [record["run_status"] for record in records],
        "correctness": [record["correctness"]["status"] for record in records],
        "all_completed": all(record["run_status"] == "COMPLETED" for record in records),
        "all_passed": all(record["correctness"]["status"] == "PASS" for record in records),
    }
    if args.json_summary:
        Path(args.json_summary).write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, sort_keys=True))
    return 0 if summary["all_completed"] and summary["all_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
