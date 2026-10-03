#!/usr/bin/env python3
"""Validate the typed Harness skill router in source and Consumer Pack form."""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from harness.application.consumer_pack import materialize_pack  # noqa: E402
from harness.project_model.core import CoreError  # noqa: E402
from harness.application.skill_router import route_artifact, route_method, route_operation  # noqa: E402

TRUST_CONTRACT = "docs/design/agent-instruction-architecture-v0.md"


def _assert_instruction_contract(result: dict, root: Path) -> None:
    assert result.get("instruction_contracts") == [TRUST_CONTRACT], result
    assert (root / TRUST_CONTRACT).is_file(), (root, TRUST_CONTRACT)


def _expect_error(fn, fragment: str) -> None:
    try:
        fn()
    except CoreError as exc:
        assert fragment in str(exc), (fragment, str(exc))
    else:
        raise AssertionError(f"expected CoreError containing {fragment!r}")


def exercise(root: Path, *, has_maintainer: bool) -> None:
    product = route_artifact(knowledge_kind="product-requirements", root=root)
    assert product == {
        "surface": "consumer",
        "route_class": "artifact-production",
        "route_key": "product-requirements",
        "skill": "skills/artifacts/product-requirements/SKILL.md",
        "instruction_contracts": [TRUST_CONTRACT],
    }
    _assert_instruction_contract(product, root)

    reliability = route_method(
        concerns=["reliability.failure-semantics"],
        root=root,
    )
    assert [item["method"] for item in reliability["routed"]] == [
        "reliability-analysis"
    ]
    _assert_instruction_contract(reliability, root)

    status = route_operation(
        surface="consumer",
        operation="project-engineering-status",
        root=root,
    )
    assert status["skill"] == "skills/agent/project-engineering-status/SKILL.md"
    assert status["exposure"] == "public"
    _assert_instruction_contract(status, root)

    _expect_error(
        lambda: route_operation(
            surface="consumer",
            operation="bootstrap-existing-project",
            root=root,
        ),
        "requires invoked_by parent operation",
    )
    _expect_error(
        lambda: route_operation(
            surface="consumer",
            operation="bootstrap-existing-project",
            root=root,
            invoked_by="project-engineering-status",
        ),
        "not authorized",
    )
    _expect_error(
        lambda: route_operation(
            surface="consumer",
            operation="bootstrap-existing-project",
            root=root,
            invoked_by="not-a-real-operation",
        ),
        "not a registered operation",
    )

    internal = route_operation(
        surface="consumer",
        operation="bootstrap-existing-project",
        root=root,
        invoked_by="project-bootstrap-reconcile",
    )
    assert internal["exposure"] == "internal"
    assert internal["invoked_by"] == "project-bootstrap-reconcile"
    _assert_instruction_contract(internal, root)

    _expect_error(
        lambda: route_operation(
            surface="consumer",
            operation="architecture-c4-structurizr",
            root=root,
        ),
        "requires invoked_by parent operation",
    )
    _expect_error(
        lambda: route_operation(
            surface="consumer",
            operation="architecture-c4-structurizr",
            root=root,
            invoked_by="project-engineering-status",
        ),
        "not authorized",
    )
    structurizr = route_operation(
        surface="consumer",
        operation="architecture-c4-structurizr",
        root=root,
        invoked_by="human-documentation-projection",
    )
    assert structurizr["skill"] == (
        "skills/agent/architecture-c4-structurizr/SKILL.md"
    )
    assert structurizr["exposure"] == "internal"
    assert structurizr["invoked_by"] == "human-documentation-projection"
    _assert_instruction_contract(structurizr, root)

    _expect_error(
        lambda: route_operation(
            surface="consumer",
            operation="data-model-dbml",
            root=root,
        ),
        "requires invoked_by parent operation",
    )
    _expect_error(
        lambda: route_operation(
            surface="consumer",
            operation="data-model-dbml",
            root=root,
            invoked_by="project-engineering-status",
        ),
        "not authorized",
    )
    dbml = route_operation(
        surface="consumer",
        operation="data-model-dbml",
        root=root,
        invoked_by="human-documentation-projection",
    )
    assert dbml["skill"] == "skills/agent/data-model-dbml/SKILL.md"
    assert dbml["exposure"] == "internal"
    assert dbml["invoked_by"] == "human-documentation-projection"
    _assert_instruction_contract(dbml, root)

    _expect_error(
        lambda: route_operation(
            surface="consumer",
            operation="application-process-bpmn",
            root=root,
        ),
        "requires invoked_by parent operation",
    )
    _expect_error(
        lambda: route_operation(
            surface="consumer",
            operation="application-process-bpmn",
            root=root,
            invoked_by="project-engineering-status",
        ),
        "not authorized",
    )
    process_bpmn = route_operation(
        surface="consumer",
        operation="application-process-bpmn",
        root=root,
        invoked_by="human-documentation-projection",
    )
    assert process_bpmn["skill"] == (
        "skills/agent/application-process-bpmn/SKILL.md"
    )
    assert process_bpmn["exposure"] == "internal"
    assert process_bpmn["invoked_by"] == "human-documentation-projection"
    _assert_instruction_contract(process_bpmn, root)

    _expect_error(
        lambda: route_artifact(knowledge_kind="change-transition-design", root=root),
        "no artifact skill registered",
    )

    if has_maintainer:
        capture = route_operation(
            surface="maintainer",
            operation="capture-harness-observation",
            root=root,
        )
        assert capture["skill"] == (
            "skills/maintainer/capture-harness-observation/SKILL.md"
        )
        _assert_instruction_contract(capture, root)
    else:
        _expect_error(
            lambda: route_operation(
                surface="maintainer",
                operation="capture-harness-observation",
                root=root,
            ),
            "not available",
        )


def main() -> int:
    exercise(ROOT, has_maintainer=True)

    with tempfile.TemporaryDirectory(prefix="skill-router-pack-") as temp:
        pack = Path(temp) / "consumer-pack"
        materialize_pack(
            ROOT,
            pack,
            binding_revision="b" * 40,
            effective_revision="validation-source",
        )
        exercise(pack, has_maintainer=False)
        assert (pack / "src/harness/application/skill_router.py").is_file()

    print("Typed Harness skill router validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
