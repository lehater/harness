#!/usr/bin/env python3
"""Focused acceptance for the first specialized document projection slice."""
from __future__ import annotations

import copy
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from harness.project_model.core import CoreError  # noqa: E402
from harness.workspace.structurizr_projection import (  # noqa: E402
    expected_provenance,
    validate_dsl,
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
        "sources": [
            {
                "artifact": "ARCHITECTURE",
                "authority": "ARCHITECTURE",
                "path": "docs/architecture.md",
                "sha256": "b" * 64,
            },
            {
                "artifact": "COMPONENT-DESIGN",
                "authority": "COMPONENT-DESIGN",
                "path": "docs/component-design.md",
                "sha256": "c" * 64,
            },
        ],
    }
    plan = {
        "version": 1,
        "kind": "harness-human-projection-plan",
        "projection": "architecture-review",
        "consumer": "IMPLEMENTATION",
        "manifest_digest": manifest["manifest_digest"],
        "documents": [
            {
                "id": "architecture-model",
                "title": "Architecture Model",
                "sections": [
                    {
                        "id": "c4",
                        "title": "C4",
                        "purpose": "Generate the accepted architecture model.",
                        "renderer": "architecture-c4-structurizr",
                        "sources": ["ARCHITECTURE", "COMPONENT-DESIGN"],
                    }
                ],
            }
        ],
    }
    profile = load(ROOT / "spec/projection/structurizr-c4-v1.yaml")
    dsl = """workspace "Example" "Generated from accepted canonical architecture" {
    !identifiers hierarchical
    !impliedRelationships false

    model {
        user = person "User"
        system = softwareSystem "Example" {
            api = container "API" "Backend API" "Python"
            database = container "Database" "Persistent data" "PostgreSQL" {
                repository = component "Repository" "Persistence boundary" "Python"
            }
        }

        user -> system.api "Uses"
        system.api -> system.database "Reads from and writes to"
    }

    views {
        systemContext system "system-context" {
            include *
            autoLayout lr
        }

        container system "containers" {
            include *
            autoLayout lr
        }

        component system.database "component-database" {
            include *
            autoLayout lr
        }
    }
}
"""
    return manifest, plan, profile, dsl


def main() -> int:
    manifest, plan, profile, dsl = valid_fixture()
    validate_profile(profile)
    provenance = expected_provenance(
        manifest,
        plan,
        document_id="architecture-model",
        section_id="c4",
        profile=profile,
    )
    assert provenance["sources"] == [
        {
            "artifact": "ARCHITECTURE",
            "path": "docs/architecture.md",
            "sha256": "b" * 64,
        },
        {
            "artifact": "COMPONENT-DESIGN",
            "path": "docs/component-design.md",
            "sha256": "c" * 64,
        },
    ]
    validate_generated_projection(
        manifest,
        plan,
        document_id="architecture-model",
        section_id="c4",
        profile=profile,
        dsl_text=dsl,
        provenance=provenance,
    )

    manifest_with_unrelated_generated = copy.deepcopy(manifest)
    manifest_with_unrelated_generated["sources"].append(
        {
            "artifact": "UNRELATED-GENERATED",
            "authority": "OTHER",
            "path": "docs/generated/other/disposable.md",
            "sha256": "e" * 64,
        }
    )
    unrelated_provenance = expected_provenance(
        manifest_with_unrelated_generated,
        plan,
        document_id="architecture-model",
        section_id="c4",
        profile=profile,
    )
    assert unrelated_provenance["sources"] == provenance["sources"]

    outside = copy.deepcopy(plan)
    outside["documents"][0]["sections"][0]["sources"].append("OUTSIDE")
    expect_error(
        lambda: expected_provenance(
            manifest,
            outside,
            document_id="architecture-model",
            section_id="c4",
            profile=profile,
        ),
        "outside manifest",
    )

    generated_manifest = copy.deepcopy(manifest)
    generated_manifest["sources"][0]["path"] = (
        "docs/generated/architecture/previous-workspace.dsl"
    )
    expect_error(
        lambda: expected_provenance(
            generated_manifest,
            plan,
            document_id="architecture-model",
            section_id="c4",
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
            document_id="architecture-model",
            section_id="c4",
            profile=profile,
        ),
        "renderer must be architecture-c4-structurizr",
    )

    stale = copy.deepcopy(provenance)
    stale["manifest_digest"] = "d" * 64
    expect_error(
        lambda: validate_generated_projection(
            manifest,
            plan,
            document_id="architecture-model",
            section_id="c4",
            profile=profile,
            dsl_text=dsl,
            provenance=stale,
        ),
        "provenance does not match",
    )

    expect_error(
        lambda: validate_dsl(
            dsl.replace("!impliedRelationships false", "!impliedRelationships true"),
            profile,
        ),
        "requires !impliedRelationships false",
    )
    expect_error(
        lambda: validate_dsl(
            dsl.replace(
                "!impliedRelationships false",
                "!impliedRelationships false\n    !include architecture.dsl",
            ),
            profile,
        ),
        "forbids directive !include",
    )
    expect_error(
        lambda: validate_dsl(
            dsl.replace('systemContext system "system-context"', "systemContext system"),
            profile,
        ),
        "requires explicit scope and key",
    )
    expect_error(
        lambda: validate_dsl(
            dsl.replace("            autoLayout lr\n", "", 1),
            profile,
        ),
        "requires autoLayout lr",
    )

    no_container_view = dsl.replace(
        """        container system "containers" {
            include *
            autoLayout lr
        }

""",
        "",
    )
    expect_error(
        lambda: validate_dsl(no_container_view, profile),
        "with containers requires a container view",
    )

    no_component_view = dsl.replace(
        """        component system.database "component-database" {
            include *
            autoLayout lr
        }
""",
        "",
    )
    expect_error(
        lambda: validate_dsl(no_component_view, profile),
        "with components requires a component view",
    )

    bad_profile = copy.deepcopy(profile)
    bad_profile["output"]["dsl"] = "../workspace.dsl"
    expect_error(
        lambda: validate_profile(bad_profile),
        "must be repository-relative",
    )

    print("Structurizr C4 projection acceptance PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
