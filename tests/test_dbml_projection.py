#!/usr/bin/env python3
"""Focused acceptance for the DBML data-model projection slice."""
from __future__ import annotations

import copy
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from harness.project_model.core import CoreError  # noqa: E402
from harness.workspace.dbml_projection import (  # noqa: E402
    expected_output_paths,
    expected_provenance,
    validate_dbml,
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
                "artifact": "DATA-DESIGN",
                "authority": "DATA-DESIGN",
                "path": "docs/data-design.md",
                "sha256": "b" * 64,
            },
            {
                "artifact": "DOMAIN-MODEL",
                "authority": "DOMAIN",
                "path": "docs/domain-model.md",
                "sha256": "c" * 64,
            },
        ],
    }
    plan = {
        "version": 1,
        "kind": "harness-human-projection-plan",
        "projection": "data-model-review",
        "consumer": "IMPLEMENTATION",
        "manifest_digest": manifest["manifest_digest"],
        "documents": [
            {
                "id": "orders-data-model",
                "title": "Orders Data Model",
                "sections": [
                    {
                        "id": "dbml",
                        "title": "DBML",
                        "purpose": "Project the accepted orders persistence model.",
                        "renderer": "data-model-dbml",
                        "scope": "orders",
                        "sources": ["DATA-DESIGN", "DOMAIN-MODEL"],
                    }
                ],
            },
            {
                "id": "billing-data-model",
                "title": "Billing Data Model",
                "sections": [
                    {
                        "id": "dbml",
                        "title": "DBML",
                        "purpose": "Project the accepted billing persistence model.",
                        "renderer": "data-model-dbml",
                        "scope": "billing",
                        "sources": ["DATA-DESIGN"],
                    }
                ],
            },
        ],
    }
    profile = load(ROOT / "spec/projection/dbml-data-model-v1.yaml")
    dbml = """// GENERATED PROJECTION
// NOT A SOURCE OF TRUTH

Enum order_status {
  pending
  paid
}

Table customers {
  id uuid [pk, not null]
  email varchar [not null, unique]
}

Table orders {
  id uuid [pk, not null]
  customer_id uuid [not null]
  status order_status [not null]
  external_id varchar

  indexes {
    (customer_id, external_id) [unique]
  }
}

Ref: orders.customer_id > customers.id
"""
    return manifest, plan, profile, dbml


def main() -> int:
    manifest, plan, profile, dbml = valid_fixture()
    validate_profile(profile)
    validate_dbml(dbml, profile)

    orders_paths = expected_output_paths(profile, "orders")
    billing_paths = expected_output_paths(profile, "billing")
    assert orders_paths == {
        "dbml": "docs/generated/data/orders/model.dbml",
        "provenance": "docs/generated/data/orders/model.dbml.provenance.yaml",
    }
    assert billing_paths == {
        "dbml": "docs/generated/data/billing/model.dbml",
        "provenance": "docs/generated/data/billing/model.dbml.provenance.yaml",
    }
    assert orders_paths != billing_paths

    provenance = expected_provenance(
        manifest,
        plan,
        document_id="orders-data-model",
        section_id="dbml",
        scope_id="orders",
        profile=profile,
    )
    assert provenance["projection"] == "data-model-dbml"
    assert provenance["profile"] == "DBML-DATA-MODEL-V1"
    assert provenance["profile_version"] == 1
    assert provenance["scope"] == "orders"
    assert provenance["sources"] == [
        {
            "artifact": "DATA-DESIGN",
            "path": "docs/data-design.md",
            "sha256": "b" * 64,
        },
        {
            "artifact": "DOMAIN-MODEL",
            "path": "docs/domain-model.md",
            "sha256": "c" * 64,
        },
    ]
    assert provenance["outputs"] == [
        orders_paths["dbml"],
        orders_paths["provenance"],
    ]

    validate_generated_projection(
        manifest,
        plan,
        document_id="orders-data-model",
        section_id="dbml",
        scope_id="orders",
        profile=profile,
        dbml_text=dbml,
        provenance=provenance,
        dbml_path=orders_paths["dbml"],
        provenance_path=orders_paths["provenance"],
    )

    expect_error(
        lambda: expected_provenance(
            manifest,
            plan,
            document_id="orders-data-model",
            section_id="dbml",
            scope_id="billing",
            profile=profile,
        ),
        "does not match plan scope",
    )
    expect_error(
        lambda: expected_output_paths(profile, "../orders"),
        "scope-id is invalid",
    )

    stale_plan = copy.deepcopy(plan)
    stale_plan["manifest_digest"] = "d" * 64
    expect_error(
        lambda: expected_provenance(
            manifest,
            stale_plan,
            document_id="orders-data-model",
            section_id="dbml",
            scope_id="orders",
            profile=profile,
        ),
        "manifest digest does not match",
    )

    outside_plan = copy.deepcopy(plan)
    outside_plan["documents"][0]["sections"][0]["sources"].append("NOT-IN-MANIFEST")
    expect_error(
        lambda: expected_provenance(
            manifest,
            outside_plan,
            document_id="orders-data-model",
            section_id="dbml",
            scope_id="orders",
            profile=profile,
        ),
        "outside manifest",
    )

    generated_manifest = copy.deepcopy(manifest)
    generated_manifest["sources"][0]["path"] = "docs/generated/data/orders/old.dbml"
    expect_error(
        lambda: expected_provenance(
            generated_manifest,
            plan,
            document_id="orders-data-model",
            section_id="dbml",
            scope_id="orders",
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
            document_id="orders-data-model",
            section_id="dbml",
            scope_id="orders",
            profile=profile,
        ),
        "renderer must be data-model-dbml",
    )

    duplicate_table = dbml + "\nTable orders {\n  another_id uuid [pk]\n}\n"
    expect_error(
        lambda: validate_dbml(duplicate_table, profile),
        "duplicate DBML table",
    )

    duplicate_column = dbml.replace(
        "  customer_id uuid [not null]\n",
        "  customer_id uuid [not null]\n  customer_id uuid\n",
    )
    expect_error(
        lambda: validate_dbml(duplicate_column, profile),
        "duplicate DBML column",
    )

    unknown_table_ref = dbml.replace(
        "Ref: orders.customer_id > customers.id",
        "Ref: orders.customer_id > accounts.id",
    )
    expect_error(
        lambda: validate_dbml(unknown_table_ref, profile),
        "target table does not exist",
    )

    unknown_column_ref = dbml.replace(
        "Ref: orders.customer_id > customers.id",
        "Ref: orders.customer_id > customers.missing",
    )
    expect_error(
        lambda: validate_dbml(unknown_column_ref, profile),
        "target column does not exist",
    )

    non_key_target = dbml.replace(
        "Ref: orders.customer_id > customers.id",
        "Ref: orders.customer_id > customers.email",
    ).replace(
        "  email varchar [not null, unique]",
        "  email varchar [not null]",
    )
    expect_error(
        lambda: validate_dbml(non_key_target, profile),
        "target must be a single-column pk/unique key",
    )

    unsupported_default = dbml.replace(
        "  external_id varchar",
        "  external_id varchar [default: generated]",
    )
    expect_error(
        lambda: validate_dbml(unsupported_default, profile),
        "unsupported settings",
    )

    unsupported_length = dbml.replace(
        "  external_id varchar",
        "  external_id varchar(255)",
    )
    expect_error(
        lambda: validate_dbml(unsupported_length, profile),
        "unsupported DBML table construct",
    )

    unsupported_index = dbml.replace(
        "    (customer_id, external_id) [unique]",
        "    (customer_id, external_id)",
    )
    expect_error(
        lambda: validate_dbml(unsupported_index, profile),
        "unsupported DBML indexes construct",
    )

    unsupported_construct = dbml + "\nProject projection_metadata {\n}\n"
    expect_error(
        lambda: validate_dbml(unsupported_construct, profile),
        "unsupported DBML construct",
    )

    bad_profile = copy.deepcopy(profile)
    bad_profile["output"]["dbml"] = "model-{scope-id}.dbml"
    expect_error(
        lambda: validate_profile(bad_profile),
        "must remain under docs/generated/",
    )

    bad_provenance = copy.deepcopy(provenance)
    bad_provenance["outputs"][0] = "docs/generated/data/other/model.dbml"
    expect_error(
        lambda: validate_generated_projection(
            manifest,
            plan,
            document_id="orders-data-model",
            section_id="dbml",
            scope_id="orders",
            profile=profile,
            dbml_text=dbml,
            provenance=bad_provenance,
            dbml_path=orders_paths["dbml"],
            provenance_path=orders_paths["provenance"],
        ),
        "provenance does not match",
    )

    expect_error(
        lambda: validate_generated_projection(
            manifest,
            plan,
            document_id="orders-data-model",
            section_id="dbml",
            scope_id="orders",
            profile=profile,
            dbml_text=dbml,
            provenance=provenance,
            dbml_path="docs/generated/data/billing/model.dbml",
            provenance_path=orders_paths["provenance"],
        ),
        "path does not match profile/scope",
    )

    print("DBML data-model projection acceptance passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
