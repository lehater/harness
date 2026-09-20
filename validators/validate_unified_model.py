#!/usr/bin/env python3
"""Acceptance validation for the unified Harness model."""
from __future__ import annotations

import copy
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from authority_context import (  # noqa: E402
    build_authority_context,
    validate_extracted_references,
    validate_write_set,
)
from engineering_graph import validate_engineering_graph  # noqa: E402
from harness import CoreError  # noqa: E402
from integration_alignment import validate_project_alignment  # noqa: E402


def expect_error(fn, contains: str) -> None:
    try:
        fn()
    except CoreError as exc:
        if contains not in str(exc):
            raise AssertionError((contains, str(exc))) from exc
    else:
        raise AssertionError(f"expected CoreError containing {contains!r}")


def main() -> int:
    errors: list[str] = []
    fixtures = sorted((ROOT / "spec/unified-model-acceptance").glob("*.yaml"))
    if not fixtures:
        errors.append("no unified-model acceptance fixtures found")

    for path in fixtures:
        try:
            doc = yaml.safe_load(path.read_text(encoding="utf-8"))
            graph = doc["engineering_graph"]
            source = doc["source_graph"]
            projection = doc["projection"]

            baseline = validate_project_alignment(source, projection, graph)
            model = baseline["model"]

            assert baseline["authority_dependencies"]["APPLICATION"] == ["PRODUCT"]
            assert baseline["authority_dependencies"]["ARCHITECTURE"] == ["APPLICATION"]
            assert baseline["authority_dependencies"]["INTERFACE"] == ["ARCHITECTURE"]
            assert baseline["authority_dependencies"]["IMPLEMENTATION-DESIGN"] == [
                "ARCHITECTURE",
                "INTERFACE",
            ]

            context = build_authority_context(
                graph, model, "IMPLEMENTATION-DESIGN"
            )
            assert context["status"] == "READY"
            assert {item["authority"] for item in context["input_artifacts"]} == {
                "ARCHITECTURE",
                "INTERFACE",
            }
            assert set(context["access"]["write"]) == {
                "docs/implementation-design.yaml"
            }
            assert validate_write_set(
                context, ["docs/implementation-design.yaml"]
            ) == ["docs/implementation-design.yaml"]
            expect_error(
                lambda: validate_write_set(context, ["docs/interface.yaml"]),
                "may not write outside owned canonical artifacts",
            )

            validate_extracted_references(
                context,
                [
                    {
                        "artifact": "IMPLEMENTATION-DESIGN",
                        "referenced_path": "docs/interface.yaml",
                    }
                ],
            )
            expect_error(
                lambda: validate_extracted_references(
                    context,
                    [
                        {
                            "artifact": "IMPLEMENTATION-DESIGN",
                            "referenced_path": "docs/requirements.yaml",
                        }
                    ],
                ),
                "canonical references outside",
            )

            hidden = copy.deepcopy(source)
            interface = next(
                item for item in hidden["nodes"] if item["id"] == "INTERFACE"
            )
            interface["depends_on"].append("JOURNEY")
            expect_error(
                lambda: validate_project_alignment(hidden, projection, graph),
                "hidden project-graph upstream Authorities",
            )

            phantom = copy.deepcopy(source)
            interface = next(
                item for item in phantom["nodes"] if item["id"] == "INTERFACE"
            )
            interface["depends_on"] = []
            expect_error(
                lambda: validate_project_alignment(phantom, projection, graph),
                "phantom capability prerequisites",
            )

            incomplete_projection = copy.deepcopy(projection)
            incomplete_projection["bindings"] = [
                item
                for item in incomplete_projection["bindings"]
                if item["artifact"] != "INTERFACE"
            ]
            expect_error(
                lambda: validate_project_alignment(
                    source, incomplete_projection, graph
                ),
                "without Authority binding",
            )

            dead = copy.deepcopy(graph)
            arch = next(
                item for item in dead["authorities"]
                if item["id"] == "ARCHITECTURE"
            )
            arch["produces"].append(
                {
                    "capability": "example.dead-public-output",
                    "requires": ["example.architecture"],
                }
            )
            expect_error(
                lambda: validate_engineering_graph(dead),
                "unconsumed public capabilities",
            )

            terminal = copy.deepcopy(dead)
            terminal["terminal_capabilities"] = [
                {
                    "capability": "example.dead-public-output",
                    "authority": "ARCHITECTURE",
                    "reason": "Acceptance fixture for an intentionally terminal result.",
                }
            ]
            validate_engineering_graph(terminal)

            redundant = copy.deepcopy(graph)
            redundant["terminal_capabilities"] = [
                {
                    "capability": "example.interface",
                    "authority": "INTERFACE",
                    "reason": "Invalid because this capability is consumed.",
                }
            ]
            expect_error(
                lambda: validate_engineering_graph(redundant),
                "already consumed downstream",
            )

            blocked_projection = copy.deepcopy(projection)
            blocked_projection["questions"] = [
                {
                    "id": "Q-INTERFACE",
                    "authority": "INTERFACE",
                    "text": "Resolve interface semantics before implementation design.",
                    "blocks_capabilities": ["example.interface"],
                }
            ]
            blocked_model = validate_project_alignment(
                source, blocked_projection, graph
            )["model"]
            blocked = build_authority_context(
                graph, blocked_model, "IMPLEMENTATION-DESIGN"
            )
            assert blocked["status"] == "BLOCKED"
            interface_req = next(
                item
                for item in blocked["requirements"]
                if item["capability"] == "example.interface"
            )
            assert interface_req["status"] == "WAIT"
            assert interface_req["blocked_by"] == ["Q-INTERFACE"]
            expect_error(
                lambda: validate_write_set(
                    blocked, ["docs/implementation-design.yaml"]
                ),
                "is BLOCKED",
            )

        except Exception as exc:
            errors.append(f"{path.relative_to(ROOT)}: {exc}")

    if errors:
        print("Unified Harness model validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(
        "Unified Harness model validation passed "
        f"({len(fixtures)} acceptance fixture(s))"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
