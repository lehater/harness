#!/usr/bin/env python3
"""Focused acceptance for the BPMN application-process projection slice."""
from __future__ import annotations

import copy
import sys
import tempfile
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from harness.project_model.core import CoreError  # noqa: E402
from harness.application.consumer_pack import materialize_pack  # noqa: E402
from harness.application.skill_router import route_operation  # noqa: E402
from harness.workspace.human_projection import validate_recipe  # noqa: E402
from harness.workspace.application_process_bpmn_projection import (  # noqa: E402
    expected_output_paths,
    expected_provenance,
    validate_bpmn,
    validate_generated_projection,
    validate_profile,
)


def load(path: Path) -> dict:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def expect_error(fn, fragment: str) -> None:
    try:
        fn()
    except CoreError as exc:
        assert fragment in str(exc), (fragment, str(exc))
    else:
        raise AssertionError(f"expected CoreError containing {fragment!r}")


def valid_fixture() -> tuple[dict, dict, dict, str]:
    manifest = {
        "version": 1,
        "kind": "harness-human-projection-manifest",
        "manifest_digest": "a" * 64,
        "consumer": "IMPLEMENTATION",
        "capabilities": [
            {
                "capability": "demo.application-process.policy-export",
                "providers": ["APPLICATION-PROCESS"],
            },
            {
                "capability": "demo.application",
                "providers": ["APPLICATION"],
            },
        ],
        "sources": [
            {
                "artifact": "APPLICATION-PROCESS",
                "authority": "APPLICATION-DESIGN",
                "path": "docs/application-process.yaml",
                "sha256": "b" * 64,
            },
            {
                "artifact": "APPLICATION",
                "authority": "APPLICATION-DESIGN",
                "path": "docs/application.yaml",
                "sha256": "c" * 64,
            },
        ],
    }
    recipe = {
        "version": 1,
        "kind": "harness-human-projection",
        "id": "process-review",
        "consumer": "IMPLEMENTATION",
        "documents": [
            {
                "id": "policy-export-process",
                "title": "Policy Export Process",
                "sections": [
                    {
                        "id": "bpmn",
                        "title": "BPMN",
                        "purpose": "Project accepted policy export process semantics.",
                        "renderer": "application-process-bpmn",
                        "scope": "policy-export",
                        "select": {
                            "capabilities": [
                                "demo.application-process.policy-export",
                                "demo.application",
                            ]
                        },
                    }
                ],
            }
        ],
    }
    plan = validate_recipe(recipe, manifest)
    profile = load(ROOT / "spec/projection/application-process-bpmn-v1.yaml")
    bpmn = """<?xml version="1.0" encoding="UTF-8"?>
<!-- GENERATED PROJECTION -->
<!-- NOT A SOURCE OF TRUTH -->
<definitions xmlns="http://www.omg.org/spec/BPMN/20100524/MODEL"
             id="Definitions_policy_export"
             targetNamespace="urn:harness:generated:application-process">
  <process id="Process_policy_export" name="Policy export" isExecutable="false">
    <startEvent id="Start_requested" name="Export requested" />
    <userTask id="Task_review" name="Review export" />
    <exclusiveGateway id="Gateway_decision" name="Review outcome" gatewayDirection="Diverging" />
    <task id="Task_publish" name="Publish export" />
    <task id="Task_reject" name="Record rejection" />
    <endEvent id="End_published" name="Export published" />
    <endEvent id="End_rejected" name="Export rejected" />
    <sequenceFlow id="Flow_1" sourceRef="Start_requested" targetRef="Task_review" />
    <sequenceFlow id="Flow_2" sourceRef="Task_review" targetRef="Gateway_decision" />
    <sequenceFlow id="Flow_approved" name="approved" sourceRef="Gateway_decision" targetRef="Task_publish" />
    <sequenceFlow id="Flow_rejected" name="rejected" sourceRef="Gateway_decision" targetRef="Task_reject" />
    <sequenceFlow id="Flow_5" sourceRef="Task_publish" targetRef="End_published" />
    <sequenceFlow id="Flow_6" sourceRef="Task_reject" targetRef="End_rejected" />
  </process>
</definitions>
"""
    return manifest, plan, profile, bpmn


def test_route_and_distribution() -> None:
    route = route_operation(
        surface="consumer",
        operation="application-process-bpmn",
        root=ROOT,
        invoked_by="human-documentation-projection",
    )
    assert route["skill"] == "skills/agent/application-process-bpmn/SKILL.md"
    assert route["exposure"] == "internal"
    assert route["invoked_by"] == "human-documentation-projection"

    expect_error(
        lambda: route_operation(
            surface="consumer",
            operation="application-process-bpmn",
            root=ROOT,
        ),
        "requires invoked_by parent operation",
    )

    with tempfile.TemporaryDirectory(prefix="bpmn-process-pack-") as tmp:
        pack = Path(tmp) / "pack"
        materialize_pack(
            ROOT,
            pack,
            binding_revision="1" * 40,
        )
        assert (
            pack / "src/harness/workspace/application_process_bpmn_projection.py"
        ).is_file()
        assert (
            pack / "skills/agent/application-process-bpmn/SKILL.md"
        ).is_file()
        assert (
            pack / "spec/projection/application-process-bpmn-v1.yaml"
        ).is_file()
        packed_route = route_operation(
            surface="consumer",
            operation="application-process-bpmn",
            root=pack,
            invoked_by="human-documentation-projection",
        )
        assert packed_route["skill"] == (
            "skills/agent/application-process-bpmn/SKILL.md"
        )


def main() -> int:
    test_route_and_distribution()
    manifest, plan, profile, bpmn = valid_fixture()
    validate_profile(profile)
    validate_bpmn(bpmn, profile)

    paths = expected_output_paths(profile, "policy-export")
    assert paths == {
        "bpmn": "docs/generated/process/policy-export/process.bpmn",
        "provenance": "docs/generated/process/policy-export/process.bpmn.provenance.yaml",
    }

    provenance = expected_provenance(
        manifest,
        plan,
        document_id="policy-export-process",
        section_id="bpmn",
        scope_id="policy-export",
        profile=profile,
    )
    assert provenance["projection"] == "application-process-bpmn"
    assert provenance["profile"] == "BPMN-PROCESS-V1"
    assert provenance["scope"] == "policy-export"
    assert provenance["sources"] == [
        {
            "artifact": "APPLICATION",
            "path": "docs/application.yaml",
            "sha256": "c" * 64,
        },
        {
            "artifact": "APPLICATION-PROCESS",
            "path": "docs/application-process.yaml",
            "sha256": "b" * 64,
        },
    ]

    validate_generated_projection(
        manifest,
        plan,
        document_id="policy-export-process",
        section_id="bpmn",
        scope_id="policy-export",
        profile=profile,
        bpmn_text=bpmn,
        provenance=provenance,
        bpmn_path=paths["bpmn"],
        provenance_path=paths["provenance"],
    )

    expect_error(
        lambda: expected_output_paths(profile, "../policy-export"),
        "scope-id is invalid",
    )

    wrong_scope = copy.deepcopy(plan)
    wrong_scope["documents"][0]["sections"][0]["scope"] = "other"
    expect_error(
        lambda: expected_provenance(
            manifest,
            wrong_scope,
            document_id="policy-export-process",
            section_id="bpmn",
            scope_id="policy-export",
            profile=profile,
        ),
        "scope does not match plan scope",
    )

    outside = copy.deepcopy(plan)
    outside["documents"][0]["sections"][0]["sources"].append("OUTSIDE")
    expect_error(
        lambda: expected_provenance(
            manifest,
            outside,
            document_id="policy-export-process",
            section_id="bpmn",
            scope_id="policy-export",
            profile=profile,
        ),
        "outside manifest",
    )

    generated_manifest = copy.deepcopy(manifest)
    generated_manifest["sources"][0]["path"] = "docs/generated/process/old/process.bpmn"
    expect_error(
        lambda: expected_provenance(
            generated_manifest,
            plan,
            document_id="policy-export-process",
            section_id="bpmn",
            scope_id="policy-export",
            profile=profile,
        ),
        "forbids generated source artifact",
    )

    wrong_renderer = copy.deepcopy(plan)
    wrong_renderer["documents"][0]["sections"][0]["renderer"] = "narrative"
    expect_error(
        lambda: expected_provenance(
            manifest,
            wrong_renderer,
            document_id="policy-export-process",
            section_id="bpmn",
            scope_id="policy-export",
            profile=profile,
        ),
        "renderer must be application-process-bpmn",
    )

    service_task = bpmn.replace(
        '<task id="Task_publish" name="Publish export" />',
        '<serviceTask id="Task_publish" name="Publish export" />',
    )
    expect_error(
        lambda: validate_bpmn(service_task, profile),
        "unsupported BPMN process construct: serviceTask",
    )

    implicit_branch = bpmn.replace(
        '<sequenceFlow id="Flow_2" sourceRef="Task_review" targetRef="Gateway_decision" />',
        '<sequenceFlow id="Flow_2" sourceRef="Task_review" targetRef="Gateway_decision" />\n'
        '    <sequenceFlow id="Flow_implicit" sourceRef="Task_review" targetRef="Task_reject" />',
    )
    expect_error(
        lambda: validate_bpmn(implicit_branch, profile),
        "use explicit gateways for branching/merging",
    )

    missing_branch_label = bpmn.replace(
        'id="Flow_rejected" name="rejected"',
        'id="Flow_rejected"',
    )
    expect_error(
        lambda: validate_bpmn(missing_branch_label, profile),
        "requires explicit branch labels",
    )

    executable = bpmn.replace('isExecutable="false"', 'isExecutable="true"')
    expect_error(
        lambda: validate_bpmn(executable, profile),
        "must be non-executable",
    )

    message_event = bpmn.replace(
        '<startEvent id="Start_requested" name="Export requested" />',
        '<startEvent id="Start_requested" name="Export requested"><messageEventDefinition /></startEvent>',
    )
    expect_error(
        lambda: validate_bpmn(message_event, profile),
        "child constructs are unsupported",
    )

    cycle = """<?xml version="1.0" encoding="UTF-8"?>
<!-- GENERATED PROJECTION -->
<!-- NOT A SOURCE OF TRUTH -->
<definitions xmlns="http://www.omg.org/spec/BPMN/20100524/MODEL"
             id="Definitions_cycle"
             targetNamespace="urn:harness:generated:application-process">
  <process id="Process_cycle" name="Cycle" isExecutable="false">
    <startEvent id="Start" name="Start" />
    <parallelGateway id="Merge" name="Loop merge" gatewayDirection="Converging" />
    <task id="Work" name="Work" />
    <exclusiveGateway id="Choice" name="Continue?" gatewayDirection="Diverging" />
    <task id="Again" name="Again" />
    <endEvent id="End" name="Completed" />
    <sequenceFlow id="F1" sourceRef="Start" targetRef="Merge" />
    <sequenceFlow id="F2" sourceRef="Merge" targetRef="Work" />
    <sequenceFlow id="F3" sourceRef="Work" targetRef="Choice" />
    <sequenceFlow id="F4" name="finish" sourceRef="Choice" targetRef="End" />
    <sequenceFlow id="F5" name="repeat" sourceRef="Choice" targetRef="Again" />
    <sequenceFlow id="F6" sourceRef="Again" targetRef="Merge" />
  </process>
</definitions>
"""
    expect_error(
        lambda: validate_bpmn(cycle, profile),
        "does not support cycles/repetition",
    )

    stale = copy.deepcopy(provenance)
    stale["manifest_digest"] = "d" * 64
    expect_error(
        lambda: validate_generated_projection(
            manifest,
            plan,
            document_id="policy-export-process",
            section_id="bpmn",
            scope_id="policy-export",
            profile=profile,
            bpmn_text=bpmn,
            provenance=stale,
        ),
        "provenance does not match",
    )

    bad_profile = copy.deepcopy(profile)
    bad_profile["output"]["bpmn"] = "../process-{scope-id}.bpmn"
    expect_error(
        lambda: validate_profile(bad_profile),
        "must be repository-relative",
    )

    print("BPMN application-process projection acceptance PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
