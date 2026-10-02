#!/usr/bin/env python3
"""Validate Harness Core v0 and its acceptance fixtures."""
from __future__ import annotations

import copy
import json
import os
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from harness.project_model.core import (  # noqa: E402
    CoreError,
    affected,
    artifact_blockers,
    blocked,
    capability_owner,
    next_action,
    capability_resolve,
    completeness,
    design_frontier,
    question_frontier,
    resolve_question,
    unresolved_questions,
    validate_model,
)

def test_multiple_provider_alternative() -> None:
    model = {
        "authorities": [{"id": "SOURCE"}],
        "artifacts": [
            {
                "id": "SOURCE-CURRENT",
                "authority": "SOURCE",
                "path": "docs/source-current.md",
                "provides": ["application.source"],
                "depends_on": [],
            },
            {
                "id": "SOURCE-OLD",
                "authority": "SOURCE",
                "path": "docs/source-old.md",
                "provides": ["application.source"],
                "depends_on": [],
            },
        ],
        "questions": [
            {
                "id": "Q-OLD",
                "authority": "SOURCE",
                "text": "Historical provider remains unresolved.",
                "blocks": ["SOURCE-OLD"],
            }
        ],
    }
    action = next_action(model, "application.source")
    assert action["action"] == "DESIGN", action
    assert action["providers"] == ["SOURCE-CURRENT", "SOURCE-OLD"], action

def test_capability_question_granularity() -> None:
    model = {
        "authorities": [{"id": "PRODUCT"}],
        "artifacts": [
            {
                "id": "REQUIREMENTS",
                "authority": "PRODUCT",
                "path": "docs/requirements.md",
                "provides": ["product.intent", "product.acceptance"],
                "depends_on": [],
            }
        ],
        "questions": [
            {
                "id": "Q-ACCEPTANCE",
                "authority": "PRODUCT",
                "text": "Which acceptance behavior is required?",
                "blocks_capabilities": ["product.acceptance"],
            }
        ],
    }

    acceptance = next_action(model, "product.acceptance")
    intent = next_action(model, "product.intent")
    assert acceptance["action"] == "WAIT", acceptance
    assert acceptance["questions"] == ["Q-ACCEPTANCE"], acceptance
    assert intent["action"] == "DESIGN", intent
    assert artifact_blockers(model, "REQUIREMENTS") == []
    assert blocked(model, "REQUIREMENTS") == ["Q-ACCEPTANCE"]

    whole_artifact = copy.deepcopy(model)
    whole_artifact["questions"].append(
        {
            "id": "Q-ARTIFACT",
            "authority": "PRODUCT",
            "text": "The requirements artifact as a whole is unusable.",
            "blocks": ["REQUIREMENTS"],
        }
    )
    intent = next_action(whole_artifact, "product.intent")
    assert intent["action"] == "WAIT", intent
    assert intent["questions"] == ["Q-ARTIFACT"], intent


def test_structural_validation_mutations() -> None:
    base = {
        "authorities": [{"id": "A"}, {"id": "B"}],
        "artifacts": [
            {
                "id": "A-DOC",
                "authority": "A",
                "path": "docs/a.yaml",
                "provides": ["demo.a"],
                "depends_on": [],
            },
            {
                "id": "B-DOC",
                "authority": "B",
                "path": "docs/b.yaml",
                "provides": ["demo.b"],
                "depends_on": ["A-DOC"],
            },
        ],
        "questions": [
            {
                "id": "Q-B",
                "authority": "B",
                "text": "Which B semantics are accepted?",
                "blocks_capabilities": ["demo.b"],
                "answer_from": ["B-DOC"],
            }
        ],
    }
    validate_model(base)

    cases: list[tuple[str, dict, str]] = []

    model = copy.deepcopy(base)
    model["artifacts"][0]["authority"] = "MISSING"
    cases.append(("artifact unknown authority", model, "references unknown authority"))

    model = copy.deepcopy(base)
    model["artifacts"][1]["provides"] = ["demo.a"]
    cases.append(("cross-authority provider", model, "providers in multiple authorities"))

    model = copy.deepcopy(base)
    model["artifacts"][1]["depends_on"] = ["MISSING"]
    cases.append(("dangling dependency", model, "depends on unknown artifact"))

    model = copy.deepcopy(base)
    model["artifacts"][1]["depends_on"] = ["B-DOC"]
    cases.append(("self dependency", model, "cannot depend on itself"))

    model = copy.deepcopy(base)
    model["artifacts"][0]["depends_on"] = ["B-DOC"]
    cases.append(("dependency cycle", model, "artifact dependency cycle"))

    model = copy.deepcopy(base)
    model["artifacts"][1]["path"] = "docs/a.yaml"
    cases.append(("duplicate canonical path", model, "duplicate canonical artifact path"))

    model = copy.deepcopy(base)
    model["questions"][0]["authority"] = "MISSING"
    cases.append(("question unknown authority", model, "references unknown authority"))

    model = copy.deepcopy(base)
    model["questions"][0]["blocks"] = ["MISSING"]
    cases.append(("question dangling block", model, "blocks unknown artifact"))

    model = copy.deepcopy(base)
    model["questions"][0]["answer_from"] = ["MISSING"]
    cases.append(("question dangling answer source", model, "answers from unknown artifact"))

    model = copy.deepcopy(base)
    model["questions"][0]["answer_from"] = ["A-DOC"]
    cases.append(("question wrong-authority answer source", model, "answer source must belong"))

    model = copy.deepcopy(base)
    model["questions"][0]["resolution"] = {
        "artifact": "MISSING",
        "acceptance_id": "B-2",
        "supersedes_acceptance_id": "B-1",
    }
    cases.append(("question dangling resolution", model, "resolves to unknown artifact"))

    model = copy.deepcopy(base)
    model["questions"][0]["resolution"] = {
        "artifact": "A-DOC",
        "acceptance_id": "B-2",
        "supersedes_acceptance_id": "B-1",
    }
    cases.append(("question wrong-authority resolution", model, "must belong to addressed authority"))

    for label, model, fragment in cases:
        try:
            validate_model(model)
        except CoreError as exc:
            assert fragment in str(exc), (label, fragment, str(exc))
        else:
            raise AssertionError(f"{label}: invalid Core model was accepted")


def test_package_execution() -> None:
    env = dict(os.environ)
    env.pop("PYTHONPATH", None)
    env["PYTHONNOUSERSITE"] = "1"
    probe = """
from pathlib import Path
import harness
from harness.project_model import core
assert Path(harness.__file__).resolve() == Path('harness/__init__.py').resolve()
assert Path(core.__file__).resolve() == Path('src/harness/project_model/core.py').resolve()
assert not hasattr(harness, 'CoreError')
assert not hasattr(harness, 'validate_model')
"""
    result = subprocess.run(
        [sys.executable, "-c", probe], cwd=ROOT, env=env,
        capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr

    fixture = yaml.safe_load(
        (ROOT / "spec/research/consumer-activation-fixture-core.yaml").read_text()
    )
    validate_model(fixture)
    command = [
        sys.executable, "-m", "harness.project_model.core",
        "validate", "spec/research/consumer-activation-fixture-core.yaml",
    ]
    result = subprocess.run(command, cwd=ROOT, env=env, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout) == {"valid": True}, result.stdout


def main() -> int:
    errors: list[str] = []
    try:
        test_package_execution()
        test_multiple_provider_alternative()
        test_capability_question_granularity()
        test_structural_validation_mutations()
    except Exception as exc:
        errors.append(f"Core focused regression: {exc}")
    required = [
        ROOT / "src/harness/project_model/core.py",
        ROOT / "harness/__init__.py",
        ROOT / "docs/design/core-v0.md",
    ]
    for path in required:
        if not path.is_file():
            errors.append(f"missing Core v0 file: {path.relative_to(ROOT)}")

    fixtures = sorted((ROOT / "spec/acceptance").glob("*.yaml"))
    if not fixtures:
        errors.append("no Core v0 acceptance fixtures found")

    for path in fixtures:
        try:
            doc = yaml.safe_load(path.read_text(encoding="utf-8"))
            if doc.get("kind") != "harness-core-acceptance":
                raise CoreError("unexpected acceptance fixture kind")
            model = doc["model"]
            expect = doc["expect"]
            validate_model(model)

            affected_expect = expect["affected"]
            actual = affected(model, affected_expect["artifact"])
            missing = sorted(set(affected_expect.get("contains", [])) - set(actual))
            if missing:
                raise CoreError(f"affected missing expected artifacts: {missing}")

            cap = expect["capability"]
            if capability_resolve(model, cap["id"]) != sorted(cap["providers"]):
                raise CoreError("capability resolve mismatch")
            if capability_owner(model, cap["id"]) != cap["owner"]:
                raise CoreError("capability owner mismatch")

            completeness_expect = expect.get("completeness")
            if completeness_expect:
                expectations = completeness_expect["expectations"]
                coverage = completeness_expect["coverage"]
                actual_missing = completeness(expectations, coverage)
                if actual_missing != completeness_expect["missing"]:
                    raise CoreError(
                        f"completeness mismatch: {actual_missing!r} != {completeness_expect['missing']!r}"
                    )
                frontier_expect = completeness_expect.get("frontier")
                if frontier_expect is not None:
                    actual_frontier = design_frontier(model, expectations, coverage)
                    if actual_frontier != frontier_expect:
                        raise CoreError(
                            f"design frontier mismatch: {actual_frontier!r} != {frontier_expect!r}"
                        )
                    question_expect = completeness_expect.get("question_frontier")
                    if question_expect is not None:
                        blocker_ids = [
                            question
                            for item in actual_frontier["wait"]
                            for question in item.get("questions", [])
                        ]
                        actual_questions = question_frontier(model, blocker_ids)
                        if actual_questions != question_expect:
                            raise CoreError(
                                f"question frontier mismatch: {actual_questions!r} != {question_expect!r}"
                            )

                complete_coverage = completeness_expect.get("complete_coverage")
                if complete_coverage is not None:
                    actual_complete = design_frontier(model, expectations, complete_coverage)
                    expected_complete = {"status": "COMPLETE", "design": [], "wait": []}
                    if actual_complete != expected_complete:
                        raise CoreError(
                            f"complete frontier mismatch: {actual_complete!r} != {expected_complete!r}"
                        )

            action = expect.get("next_action")
            if action:
                actual_action = next_action(model, action["capability"])
                for key, value in action.items():
                    if key == "capability":
                        continue
                    if actual_action.get(key) != value:
                        raise CoreError(
                            f"next-action {key} mismatch: {actual_action.get(key)!r} != {value!r}"
                        )

            if unresolved_questions(model) != sorted(expect["questions"]["unresolved"]):
                raise CoreError("questions mismatch")

            block = expect["blocked"]
            if blocked(model, block["artifact"]) != sorted(block["by"]):
                raise CoreError("blocked mismatch")

            resolution = expect["resolution"]
            try:
                resolve_question(
                    copy.deepcopy(model),
                    resolution["question"],
                    resolution["artifact"],
                    resolution["acceptance_id"],
                    resolution["acceptance_id"],
                )
            except CoreError:
                pass
            else:
                raise CoreError(
                    "resolve-question accepted an unchanged semantic acceptance identity"
                )

            resolved = resolve_question(
                copy.deepcopy(model),
                resolution["question"],
                resolution["artifact"],
                resolution["acceptance_id"],
                resolution["supersedes_acceptance_id"],
            )
            after_action = resolution.get("next_action")
            if after_action:
                actual_after = next_action(resolved, after_action["capability"])
                for key, value in after_action.items():
                    if key == "capability":
                        continue
                    if actual_after.get(key) != value:
                        raise CoreError(
                            f"resolved next-action {key} mismatch: {actual_after.get(key)!r} != {value!r}"
                        )
            if unresolved_questions(resolved) != sorted(resolution["unresolved_after"]):
                raise CoreError("resolve-question did not clear unresolved question")
            if blocked(resolved, block["artifact"]) != sorted(resolution["blocked_after"]):
                raise CoreError("resolve-question did not clear blocking")

            external_resolution = expect.get("external_resolution")
            if external_resolution:
                externally_resolved = resolve_question(
                    copy.deepcopy(model),
                    external_resolution["question"],
                    external_resolution["artifact"],
                    external_resolution["acceptance_id"],
                    external_resolution["supersedes_acceptance_id"],
                )
                if unresolved_questions(externally_resolved) != sorted(
                    external_resolution["unresolved_after"]
                ):
                    raise CoreError("external resolution did not clear expected question")
                actual_frontier = design_frontier(
                    externally_resolved,
                    completeness_expect["expectations"],
                    completeness_expect["coverage"],
                )
                if actual_frontier != external_resolution["frontier_after"]:
                    raise CoreError(
                        f"external resolution frontier mismatch: {actual_frontier!r} != "
                        f"{external_resolution['frontier_after']!r}"
                    )
        except Exception as exc:
            errors.append(f"{path.relative_to(ROOT)}: {exc}")

    if errors:
        print("Harness Core validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(f"Harness Core validation passed ({len(fixtures)} acceptance fixture(s))")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
