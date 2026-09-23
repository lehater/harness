#!/usr/bin/env python3
from copy import deepcopy
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from coverage_planner import capability_realization  # noqa: E402
from frontend_screen_contracts import (  # noqa: E402
    evaluate_frontend_screen_contracts,
    semantic_evaluation,
)


PRESENTATION = {
    "version": 1,
    "kind": "presentation-system-design",
    "id": "FIXTURE-PRESENTATION",
    "external_baseline": {
        "provider": "fixture-ui",
        "artifact": "crud-dashboard",
        "version": "1.2.3",
        "feature_policy": {"default": "deny"},
    },
    "patterns": {
        "CATALOGUE": {
            "features": [
                "open-item",
                "create-item",
                "search",
                "filter",
                "sort",
                "paginate",
                "bulk-delete",
            ]
        },
        "DETAIL": {
            "features": ["show-primary", "show-history", "edit", "delete"]
        },
        "STATUS": {"features": ["loading", "empty", "error"]},
    },
}


PROVIDER = {
    "kind": "frontend-presentation-provider-contract",
    "provider": "fixture-ui",
    "version": "1.2.3",
    "feature_policy": {"default": "deny"},
    "required_patterns": ["CATALOGUE", "DETAIL", "STATUS"],
    "pattern_mappings": {
        "CATALOGUE": {
            "adapter": "FixtureCatalogue",
            "provider_primitives": ["FixtureTable", "FixtureButton"],
        },
        "DETAIL": {
            "adapter": "FixtureDetail",
            "provider_primitives": ["FixtureStack"],
        },
        "STATUS": {
            "adapter": "FixtureStatus",
            "provider_primitives": ["FixtureAlert"],
        },
    },
}

OPENAPI = {
    "openapi": "3.1.0",
    "paths": {
        "/v1/resources": {
            "get": {"operationId": "listResources", "responses": {"200": {}}},
            "post": {"operationId": "createResource", "responses": {"201": {}, "403": {}, "409": {}, "422": {}}},
        },
        "/v1/resources/{resourceRef}": {
            "get": {"operationId": "getResource", "responses": {"200": {}, "403": {}, "404": {}}},
        },
    },
}


NAVIGATION = {
    "version": 1,
    "kind": "ui-navigation-model",
    "journeys": [{"id": "RESOURCE-MANAGEMENT"}],
    "routes": [
        {
            "path": "/resources",
            "workspace": "RESOURCE-CATALOGUE",
            "parent": {
                "state": "not-applicable",
                "rationale": "top-level fixture workspace",
            },
            "direct_link": "canonical",
        },
        {
            "path": "/resources/{resourceRef}",
            "workspace": "RESOURCE-DETAIL",
            "parent": "navigation:resource-catalogue",
            "direct_link": "canonical",
        },
    ],
}

SCREENS = {
    "version": 1,
    "kind": "screen-view-design",
    "id": "FIXTURE-SCREENS",
    "screens": [
        {
            "id": "RESOURCE-CATALOGUE",
            "purpose": "Locate/select Resources and start supported creation.",
            "patterns": ["CATALOGUE", "STATUS"],
            "states": ["loading", "loaded", "empty", "validation-rejected", "error"],
            "semantic_contract": {
                "reads": [
                    {
                        "id": "catalogue",
                        "operation_id": "listResources",
                        "projection": "ResourceCatalogueView",
                    }
                ],
                "commands": [
                    {
                        "id": "create-resource",
                        "operation_id": "createResource",
                    }
                ],
                "view_model": {
                    "id": "ResourceCatalogueScreenModel",
                    "fields": [
                        {"id": "items", "source": "read:catalogue.items"},
                        {"id": "has_more", "source": "read:catalogue.hasMore"},
                    ],
                },
                "capabilities": {
                    "allowed": [
                        {"id": "open-resource", "backed_by": "navigation:resource-detail"},
                        {"id": "create-resource", "backed_by": "command:create-resource"},
                    ],
                    "excluded": ["search", "filter", "sort", "bulk-delete"],
                },
                "pattern_mapping": [
                    {
                        "pattern": "CATALOGUE",
                        "feature_bindings": {
                            "open-item": "open-resource",
                            "create-item": "create-resource",
                        },
                    },
                    {
                        "pattern": "STATUS",
                        "feature_bindings": {},
                    },
                ],
                "state_mapping": {
                    "loading": "read:catalogue.pending",
                    "loaded": "read:catalogue.200-items",
                    "empty": "read:catalogue.200-empty",
                    "validation-rejected": "command:create-resource.422",
                    "error": ["read:catalogue.failure", "command:create-resource.failure"],
                },
                "verification": {
                    "contract": ["operation:listResources", "operation:createResource"],
                    "semantic": ["resource-catalogue-state-matrix"],
                    "rendered": ["resource-catalogue-reference-render"],
                },
            },
        },
        {
            "id": "RESOURCE-DETAIL",
            "purpose": "Inspect one Resource and its history.",
            "patterns": ["DETAIL"],
            "states": ["loading", "loaded", "not-found", "error"],
            "semantic_contract": {
                "reads": [
                    {
                        "id": "resource-detail",
                        "operation_id": "getResource",
                        "projection": "ResourceView",
                    }
                ],
                "commands": [],
                "view_model": {
                    "id": "ResourceDetailScreenModel",
                    "fields": [
                        {"id": "identity", "source": "read:resource-detail.resourceRef"},
                        {"id": "current", "source": "read:resource-detail.current"},
                        {"id": "history", "source": "read:resource-detail.history"},
                    ],
                },
                "capabilities": {
                    "allowed": [
                        {"id": "show-primary", "backed_by": "read:resource-detail"},
                        {"id": "show-history", "backed_by": "read:resource-detail"},
                    ],
                    "excluded": ["delete"],
                },
                "pattern_mapping": [
                    {
                        "pattern": "DETAIL",
                        "feature_bindings": {
                            "show-primary": "show-primary",
                            "show-history": "show-history",
                        },
                    }
                ],
                "state_mapping": {
                    "loading": "read:resource-detail.pending",
                    "loaded": "read:resource-detail.200",
                    "not-found": "read:resource-detail.404",
                    "error": "read:resource-detail.failure",
                },
                "verification": {
                    "contract": ["operation:getResource"],
                    "semantic": ["resource-detail-state-matrix"],
                    "rendered": ["resource-detail-reference-render"],
                },
            },
        },
    ],
}


def codes(result):
    return {item["code"] for item in result["findings"]}


def main() -> int:
    accepted = evaluate_frontend_screen_contracts(
        PRESENTATION,
        SCREENS,
        OPENAPI,
        screen_ids={"RESOURCE-CATALOGUE", "RESOURCE-DETAIL"},
        provider_contract=PROVIDER,
    )
    assert accepted["status"] == "ACCEPTED", accepted

    missing_provider_pattern = deepcopy(PROVIDER)
    del missing_provider_pattern["pattern_mappings"]["DETAIL"]
    result = evaluate_frontend_screen_contracts(
        PRESENTATION,
        SCREENS,
        OPENAPI,
        screen_ids={"RESOURCE-CATALOGUE", "RESOURCE-DETAIL"},
        provider_contract=missing_provider_pattern,
    )
    assert "MISSING_PROVIDER_PATTERN_MAPPING" in codes(result)

    provider_invents_feature = deepcopy(PROVIDER)
    provider_invents_feature["pattern_mappings"]["CATALOGUE"]["enabled_features"] = ["search"]
    result = evaluate_frontend_screen_contracts(
        PRESENTATION,
        SCREENS,
        OPENAPI,
        provider_contract=provider_invents_feature,
    )
    assert "PROVIDER_FEATURE_ENABLEMENT_FORBIDDEN" in codes(result)

    unsafe_provider = deepcopy(PROVIDER)
    unsafe_provider["feature_policy"]["default"] = "allow"
    result = evaluate_frontend_screen_contracts(
        PRESENTATION,
        SCREENS,
        OPENAPI,
        provider_contract=unsafe_provider,
    )
    assert "UNSAFE_PROVIDER_FEATURE_DEFAULT" in codes(result)

    incomplete_provider = deepcopy(PROVIDER)
    del incomplete_provider["pattern_mappings"]["DETAIL"]
    result = evaluate_frontend_screen_contracts(
        PRESENTATION,
        SCREENS,
        OPENAPI,
        provider_contract=incomplete_provider,
    )
    assert "MISSING_PROVIDER_PATTERN_MAPPING" in codes(result)

    provider_invents_feature = deepcopy(PROVIDER)
    provider_invents_feature["pattern_mappings"]["CATALOGUE"]["enabled_features"] = ["search"]
    result = evaluate_frontend_screen_contracts(
        PRESENTATION,
        SCREENS,
        OPENAPI,
        provider_contract=provider_invents_feature,
    )
    assert "PROVIDER_FEATURE_ENABLEMENT_FORBIDDEN" in codes(result)

    unsafe = deepcopy(PRESENTATION)
    unsafe["external_baseline"]["feature_policy"]["default"] = "allow"
    result = evaluate_frontend_screen_contracts(unsafe, SCREENS, OPENAPI)
    assert "UNSAFE_PROVIDER_FEATURE_DEFAULT" in codes(result)

    invented_search = deepcopy(SCREENS)
    invented_search["screens"][0]["semantic_contract"]["pattern_mapping"][0]["feature_bindings"]["search"] = "search"
    result = evaluate_frontend_screen_contracts(PRESENTATION, invented_search, OPENAPI)
    assert "PRESENTATION_FEATURE_NOT_AUTHORIZED" in codes(result)

    absent_query = deepcopy(SCREENS)
    absent_query["screens"][0]["semantic_contract"]["reads"][0]["operation_id"] = "searchResources"
    result = evaluate_frontend_screen_contracts(PRESENTATION, absent_query, OPENAPI)
    assert "UNKNOWN_INTERFACE_OPERATION" in codes(result)

    unmapped_state = deepcopy(SCREENS)
    del unmapped_state["screens"][1]["semantic_contract"]["state_mapping"]["not-found"]
    result = evaluate_frontend_screen_contracts(PRESENTATION, unmapped_state, OPENAPI)
    assert "UNMAPPED_SCREEN_STATE" in codes(result)

    impossible_outcome = deepcopy(SCREENS)
    impossible_outcome["screens"][0]["semantic_contract"]["state_mapping"]["validation-rejected"] = "command:create-resource.404"
    result = evaluate_frontend_screen_contracts(PRESENTATION, impossible_outcome, OPENAPI)
    assert "UNSUPPORTED_OPERATION_OUTCOME" in codes(result)

    no_rendered_proof = deepcopy(SCREENS)
    no_rendered_proof["screens"][1]["semantic_contract"]["verification"]["rendered"] = []
    result = evaluate_frontend_screen_contracts(PRESENTATION, no_rendered_proof, OPENAPI)
    assert "INCOMPLETE_VERIFICATION_CONTRACT" in codes(result)

    collection_defaults = deepcopy(PRESENTATION)
    collection_defaults["entity_collection_default"] = {
        "navigation_model": "general-to-specific",
        "catalogue": {
            "default_pattern": "DATA-TABLE",
            "default_query_controls": ["search", "attribute-filter", "sort"],
            "scaling_controls": ["pagination-or-virtualization"],
        },
        "detail": {"inline_editing": "explicit-override-only"},
        "structured_list_role": "nested/secondary only",
    }
    missing_collection_defaults = evaluate_frontend_screen_contracts(
        collection_defaults,
        SCREENS,
        OPENAPI,
        screen_ids={"RESOURCE-CATALOGUE"},
    )
    assert "PRIMARY_CATALOGUE_REQUIRES_DEFAULT_PATTERN" in codes(
        missing_collection_defaults
    )
    assert "MISSING_CATALOGUE_QUERY_CONTRACT" in codes(missing_collection_defaults)

    structured_primary = deepcopy(SCREENS)
    structured_primary["screens"][0]["patterns"].append("STRUCTURED-LIST")
    result = evaluate_frontend_screen_contracts(
        collection_defaults,
        structured_primary,
        OPENAPI,
        screen_ids={"RESOURCE-CATALOGUE"},
    )
    assert "PRIMARY_CATALOGUE_STRUCTURED_LIST_WITHOUT_OVERRIDE" in codes(result)

    nested_structured_list = deepcopy(structured_primary)
    nested_structured_list["screens"][0]["regions"] = [
        {
            "id": "resources",
            "role": "collection",
            "priority": "primary",
            "pattern": "DATA-TABLE",
        },
        {
            "id": "relationships",
            "role": "nested-relationship-collection",
            "priority": "secondary",
            "pattern": "STRUCTURED-LIST",
        },
    ]
    result = evaluate_frontend_screen_contracts(
        collection_defaults,
        nested_structured_list,
        OPENAPI,
        screen_ids={"RESOURCE-CATALOGUE"},
    )
    assert "PRIMARY_CATALOGUE_STRUCTURED_LIST_WITHOUT_OVERRIDE" not in codes(result)

    wrong_drilldown = deepcopy(SCREENS)
    wrong_drilldown["screens"][0]["semantic_contract"]["capabilities"]["allowed"][0][
        "backed_by"
    ] = "navigation:resource-catalogue"
    detail_default = deepcopy(PRESENTATION)
    detail_default["entity_collection_default"] = {
        "navigation_model": "general-to-specific",
        "catalogue": {
            "default_pattern": "CATALOGUE",
            "default_query_controls": [],
            "scaling_controls": [],
        },
        "detail": {"inline_editing": "explicit-override-only"},
    }
    result = evaluate_frontend_screen_contracts(
        detail_default,
        wrong_drilldown,
        OPENAPI,
        screen_ids={"RESOURCE-CATALOGUE"},
    )
    assert "PRIMARY_CATALOGUE_MISSING_DETAIL_DRILLDOWN" in codes(result)

    query_screen = deepcopy(SCREENS)
    query_screen["screens"][0]["semantic_contract"]["reads"][0]["query"] = {
        "search": {"source": "local:query.search"}
    }
    query_screen["screens"][0]["semantic_contract"]["capabilities"]["allowed"].append(
        {"id": "search", "backed_by": "read:catalogue"}
    )
    query_screen["screens"][0]["semantic_contract"]["pattern_mapping"][0][
        "feature_bindings"
    ]["search"] = "search"
    query_default = deepcopy(detail_default)
    query_default["entity_collection_default"]["catalogue"][
        "default_query_controls"
    ] = ["search"]
    result = evaluate_frontend_screen_contracts(
        query_default,
        query_screen,
        OPENAPI,
        screen_ids={"RESOURCE-CATALOGUE"},
    )
    assert "CATALOGUE_QUERY_PARAMETER_NOT_IN_INTERFACE" in codes(result)

    inline_edit_presentation = deepcopy(detail_default)
    inline_edit_presentation["patterns"]["CATALOGUE"]["features"].append("edit-row")
    inline_edit_screen = deepcopy(SCREENS)
    inline_edit_screen["screens"][0]["semantic_contract"]["capabilities"]["allowed"].append(
        {"id": "edit-resource", "backed_by": "command:create-resource"}
    )
    inline_edit_screen["screens"][0]["semantic_contract"]["pattern_mapping"][0][
        "feature_bindings"
    ]["edit-row"] = "edit-resource"
    result = evaluate_frontend_screen_contracts(
        inline_edit_presentation,
        inline_edit_screen,
        OPENAPI,
        screen_ids={"RESOURCE-CATALOGUE"},
    )
    assert "PRIMARY_CATALOGUE_INLINE_EDIT_REQUIRES_OVERRIDE" in codes(result)



    strict = deepcopy(SCREENS)
    strict["screens"][0]["semantic_contract"]["task_refs"] = ["RESOURCE-MANAGEMENT"]
    strict["screens"][0]["semantic_contract"]["outcome_mapping"] = {
        "command:create-resource.201": "navigation:resource-detail",
        "command:create-resource.403": "state:error",
        "command:create-resource.409": "state:error",
    }
    strict["screens"][0]["semantic_contract"]["references"] = [
        {
            "id": "related-resource",
            "use": "selection",
            "identity": "resourceRef",
            "display": {
                "primary": "displayName",
                "technical_identity": "resourceRef",
            },
            "candidates": {
                "operation_id": "listResources",
                "mode": "independent",
                "search": "server-backed",
            },
            "submitted_value": "resourceRef",
            "submits_to": "command:create-resource",
        }
    ]
    strict["screens"][0]["composition"] = {
        "fixture-field": {
            "id": "related-resource",
            "selection": {"contract": "related-resource"},
        }
    }
    strict["screens"][1]["semantic_contract"]["task_refs"] = ["RESOURCE-MANAGEMENT"]
    strict["screens"][1]["semantic_contract"]["outcome_mapping"] = {
        "read:resource-detail.403": "state:error",
    }
    strict_result = evaluate_frontend_screen_contracts(
        PRESENTATION,
        strict,
        OPENAPI,
        screen_ids={"RESOURCE-CATALOGUE", "RESOURCE-DETAIL"},
        navigation_contract=NAVIGATION,
        require_interaction_closure=True,
    )
    assert strict_result["status"] == "ACCEPTED", strict_result

    missing_action = deepcopy(strict)
    missing_action["screens"][0]["semantic_contract"]["capabilities"]["allowed"] = [
        row
        for row in missing_action["screens"][0]["semantic_contract"]["capabilities"]["allowed"]
        if row["id"] != "create-resource"
    ]
    result = evaluate_frontend_screen_contracts(
        PRESENTATION,
        missing_action,
        OPENAPI,
        screen_ids={"RESOURCE-CATALOGUE", "RESOURCE-DETAIL"},
        navigation_contract=NAVIGATION,
        require_interaction_closure=True,
    )
    assert "UNEXPOSED_COMMAND_SEMANTICS" in codes(result)


    composite_reference = deepcopy(strict)
    composite_reference["screens"][0]["semantic_contract"]["references"][0]["identity"] = [
        "resourceRef",
        "relatedResourceRef",
    ]
    composite_reference["screens"][0]["semantic_contract"]["references"][0]["display"]["technical_identity"] = [
        "resourceRef",
        "relatedResourceRef",
    ]
    composite_reference["screens"][0]["semantic_contract"]["references"][0]["submitted_value"] = [
        "resourceRef",
        "relatedResourceRef",
    ]
    result = evaluate_frontend_screen_contracts(
        PRESENTATION,
        composite_reference,
        OPENAPI,
        screen_ids={"RESOURCE-CATALOGUE", "RESOURCE-DETAIL"},
        navigation_contract=NAVIGATION,
        require_interaction_closure=True,
    )
    assert result["status"] == "ACCEPTED", result

    candidate_read_source = deepcopy(strict)
    candidate_read_source["screens"][0]["semantic_contract"]["references"][0]["candidates"] = {
        "source": "read:catalogue.items",
        "mode": "independent",
        "search": "bounded-current-read",
    }
    result = evaluate_frontend_screen_contracts(
        PRESENTATION,
        candidate_read_source,
        OPENAPI,
        screen_ids={"RESOURCE-CATALOGUE", "RESOURCE-DETAIL"},
        navigation_contract=NAVIGATION,
        require_interaction_closure=True,
    )
    assert result["status"] == "ACCEPTED", result

    missing_candidates = deepcopy(strict)
    del missing_candidates["screens"][0]["semantic_contract"]["references"][0]["candidates"]
    result = evaluate_frontend_screen_contracts(
        PRESENTATION,
        missing_candidates,
        OPENAPI,
        screen_ids={"RESOURCE-CATALOGUE", "RESOURCE-DETAIL"},
        navigation_contract=NAVIGATION,
        require_interaction_closure=True,
    )
    assert "MISSING_REFERENCE_CANDIDATES" in codes(result)

    missing_dependency = deepcopy(strict)
    missing_dependency["screens"][0]["semantic_contract"]["references"][0]["candidates"]["mode"] = "dependent"
    result = evaluate_frontend_screen_contracts(
        PRESENTATION,
        missing_dependency,
        OPENAPI,
        screen_ids={"RESOURCE-CATALOGUE", "RESOURCE-DETAIL"},
        navigation_contract=NAVIGATION,
        require_interaction_closure=True,
    )
    assert "MISSING_REFERENCE_DEPENDENCY" in codes(result)

    missing_outcome = deepcopy(strict)
    del missing_outcome["screens"][0]["semantic_contract"]["outcome_mapping"]["command:create-resource.409"]
    strict_missing_outcome_result = evaluate_frontend_screen_contracts(
        PRESENTATION,
        missing_outcome,
        OPENAPI,
        screen_ids={"RESOURCE-CATALOGUE", "RESOURCE-DETAIL"},
        navigation_contract=NAVIGATION,
        require_interaction_closure=True,
    )
    assert "UNMAPPED_OPERATION_OUTCOME" in codes(strict_missing_outcome_result)

    missing_task = deepcopy(strict)
    missing_task["screens"][0]["semantic_contract"]["task_refs"] = ["UNKNOWN-TASK"]
    result = evaluate_frontend_screen_contracts(
        PRESENTATION,
        missing_task,
        OPENAPI,
        screen_ids={"RESOURCE-CATALOGUE", "RESOURCE-DETAIL"},
        navigation_contract=NAVIGATION,
        require_interaction_closure=True,
    )
    assert "UNKNOWN_TASK_REF" in codes(result)

    incomplete_navigation = deepcopy(NAVIGATION)
    incomplete_navigation["routes"][0]["mode"] = "create"
    result = evaluate_frontend_screen_contracts(
        PRESENTATION,
        strict,
        OPENAPI,
        screen_ids={"RESOURCE-CATALOGUE", "RESOURCE-DETAIL"},
        navigation_contract=incomplete_navigation,
        require_interaction_closure=True,
    )
    assert "MISSING_ROUTE_SUCCESS" in codes(result)
    assert "MISSING_ROUTE_CANCEL" in codes(result)

    evidence = semantic_evaluation(
        accepted,
        artifact="SCREENS",
        capability="frontend.screen-view",
        semantic_claims=["engineering.interface.human.screen-composition"],
    )
    assert evidence["status"] == "ACCEPTED"
    assert evidence["semantic_claims"]["accepted"] == [
        "engineering.interface.human.screen-composition"
    ]

    rejected_evidence = semantic_evaluation(
        strict_missing_outcome_result,
        artifact="SCREENS",
        capability="frontend.screen-view",
        semantic_claims=["engineering.interface.human.screen-composition"],
    )
    graph = {
        "kind": "harness-engineering-graph",
        "authorities": [
            {
                "id": "INTERFACE",
                "produces": [
                    {
                        "capability": "frontend.screen-view",
                        "requires": [],
                        "semantic_claims": [
                            "engineering.interface.human.screen-composition"
                        ],
                    }
                ],
            },
            {
                "id": "IMPLEMENTATION",
                "produces": [
                    {
                        "capability": "frontend.implementation",
                        "requires": [{"capability": "frontend.screen-view"}],
                    }
                ],
            },
        ],
        "consumers": [
            {
                "id": "FRONTEND",
                "requires": [{"capability": "frontend.implementation"}],
            }
        ],
    }
    realization = {
        "artifacts": [
            {"id": "SCREENS", "provides": ["frontend.screen-view"]},
            {"id": "IMPLEMENTATION", "provides": ["frontend.implementation"]},
        ]
    }
    coverage = capability_realization(
        [graph, realization, rejected_evidence],
        "FRONTEND",
    )
    assert "frontend.screen-view" not in coverage["usable"]
    assert "frontend.implementation" not in coverage["usable"]
    assert coverage["semantic_invalid"]["frontend.screen-view"] == [
        "frontend.screen-view"
    ]

    print(
        "frontend screen contracts: PASS "
        "(positive closure + query/action/state/provider exclusion + coverage gating)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
