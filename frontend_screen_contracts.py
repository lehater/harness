#!/usr/bin/env python3
"""Provider-neutral semantic closure checks for frontend Screen/View contracts."""
from __future__ import annotations

from typing import Any, Iterable
import re

HTTP_METHODS = {"get", "post", "put", "patch", "delete", "options", "head"}


def operation_ids(interface_contract: dict[str, Any] | None) -> set[str]:
    """Extract stable operation ids from OpenAPI or a small generic operation catalogue."""
    if not interface_contract:
        return set()
    result: set[str] = set()
    for path_item in (interface_contract.get("paths", {}) or {}).values():
        if not isinstance(path_item, dict):
            continue
        for method, operation in path_item.items():
            if method.lower() not in HTTP_METHODS or not isinstance(operation, dict):
                continue
            operation_id = operation.get("operationId")
            if isinstance(operation_id, str) and operation_id:
                result.add(operation_id)
    for item in interface_contract.get("operations", []) or []:
        if isinstance(item, str) and item:
            result.add(item)
        elif isinstance(item, dict):
            operation_id = item.get("operation_id") or item.get("operationId") or item.get("id")
            if isinstance(operation_id, str) and operation_id:
                result.add(operation_id)
    for item in interface_contract.get("operation_ids", []) or []:
        if isinstance(item, str) and item:
            result.add(item)
    return result


def operation_response_codes(interface_contract: dict[str, Any] | None) -> dict[str, set[str]]:
    result: dict[str, set[str]] = {}
    if not interface_contract:
        return result
    for path_item in (interface_contract.get("paths", {}) or {}).values():
        if not isinstance(path_item, dict):
            continue
        for method, operation in path_item.items():
            if method.lower() not in HTTP_METHODS or not isinstance(operation, dict):
                continue
            operation_id = operation.get("operationId")
            if isinstance(operation_id, str) and operation_id:
                result[operation_id] = {
                    str(code) for code in (operation.get("responses", {}) or {}).keys()
                }
    return result


def operation_query_parameters(interface_contract: dict[str, Any] | None) -> dict[str, set[str]]:
    """Extract accepted query parameter names for each OpenAPI operation."""
    result: dict[str, set[str]] = {}
    if not interface_contract:
        return result
    component_parameters = (
        ((interface_contract.get("components") or {}).get("parameters") or {})
        if isinstance(interface_contract.get("components"), dict)
        else {}
    )

    def parameter_row(value: Any) -> dict[str, Any] | None:
        if not isinstance(value, dict):
            return None
        ref = value.get("$ref")
        if isinstance(ref, str) and ref.startswith("#/components/parameters/"):
            resolved = component_parameters.get(ref.rsplit("/", 1)[-1])
            return resolved if isinstance(resolved, dict) else None
        return value

    for path_item in (interface_contract.get("paths", {}) or {}).values():
        if not isinstance(path_item, dict):
            continue
        inherited = path_item.get("parameters", []) or []
        for method, operation in path_item.items():
            if method.lower() not in HTTP_METHODS or not isinstance(operation, dict):
                continue
            operation_id = operation.get("operationId")
            if not isinstance(operation_id, str) or not operation_id:
                continue
            names: set[str] = set()
            for raw in [*inherited, *((operation.get("parameters", []) or []))]:
                parameter = parameter_row(raw)
                if not parameter or parameter.get("in") != "query":
                    continue
                name = parameter.get("name")
                if isinstance(name, str) and name:
                    names.add(name)
            result[operation_id] = names
    return result


def _has_override_rationale(screen_row: dict[str, Any]) -> bool:
    candidates: list[Any] = []
    override = screen_row.get("override")
    if override is not None:
        candidates.append(override)
    overrides = screen_row.get("overrides", []) or []
    if isinstance(overrides, list):
        candidates.extend(overrides)
    elif overrides is not None:
        candidates.append(overrides)
    return any(
        isinstance(item, dict)
        and isinstance(item.get("rationale"), str)
        and bool(item["rationale"].strip())
        for item in candidates
    )


def _validate_entity_collection_default(
    *,
    presentation: dict[str, Any],
    screen_row: dict[str, Any],
    screen: str,
    contract: dict[str, Any],
    reads: dict[str, dict[str, Any]],
    allowed: dict[str, dict[str, Any]],
    mappings: list[Any],
    binding_operations: dict[tuple[str, str], str],
    query_parameters_by_operation: dict[str, set[str]],
    findings: list[dict[str, Any]],
) -> None:
    default = presentation.get("entity_collection_default")
    declared_patterns = {
        item
        for item in (screen_row.get("patterns", []) or [])
        if isinstance(item, str) and item
    }
    declared_patterns.update(
        mapping.get("pattern")
        for mapping in mappings
        if isinstance(mapping, dict)
        and isinstance(mapping.get("pattern"), str)
        and mapping.get("pattern")
    )
    primary_collection_patterns = {
        region.get("pattern")
        for region in (screen_row.get("regions", []) or [])
        if isinstance(region, dict)
        and region.get("role") == "collection"
        and region.get("priority") == "primary"
        and isinstance(region.get("pattern"), str)
        and region.get("pattern")
    }
    collection_patterns = primary_collection_patterns or declared_patterns
    if not isinstance(default, dict) or "CATALOGUE" not in declared_patterns:
        return

    override = _has_override_rationale(screen_row)
    catalogue = default.get("catalogue") or {}
    detail = default.get("detail") or {}
    default_pattern = catalogue.get("default_pattern")
    if (
        isinstance(default_pattern, str)
        and default_pattern
        and default_pattern not in collection_patterns
        and not override
    ):
        _finding(
            findings,
            "PRIMARY_CATALOGUE_REQUIRES_DEFAULT_PATTERN",
            f"primary entity catalogue requires {default_pattern} or an explicit override with rationale",
            screen=screen,
        )

    structured_role = default.get("structured_list_role")
    if (
        structured_role
        and "STRUCTURED-LIST" in collection_patterns
        and default_pattern != "STRUCTURED-LIST"
        and not override
    ):
        _finding(
            findings,
            "PRIMARY_CATALOGUE_STRUCTURED_LIST_WITHOUT_OVERRIDE",
            "STRUCTURED-LIST is not the accepted primary entity catalogue pattern without an explicit override with rationale",
            screen=screen,
        )

    expected_controls = catalogue.get("default_query_controls", []) or []
    expected_capabilities = {
        "search": "search",
        "attribute-filter": "filter",
        "sort": "sort",
    }
    for control in expected_controls:
        capability = expected_capabilities.get(control)
        if capability and capability not in allowed and not override:
            _finding(
                findings,
                "MISSING_DEFAULT_CATALOGUE_CAPABILITY",
                f"primary entity catalogue is missing accepted default capability {capability}",
                screen=screen,
            )

    scaling = catalogue.get("scaling_controls", []) or []
    if (
        "pagination-or-virtualization" in scaling
        and not ({"pagination", "virtualization"} & set(allowed))
        and not override
    ):
        _finding(
            findings,
            "MISSING_CATALOGUE_SCALING_CAPABILITY",
            "primary entity catalogue requires pagination or virtualization",
            screen=screen,
        )

    open_capability: str | None = None
    inline_edit_capability: str | None = None
    for mapping in mappings:
        if not isinstance(mapping, dict):
            continue
        feature_bindings = mapping.get("feature_bindings", {}) or {}
        if not isinstance(feature_bindings, dict):
            continue
        for feature, capability in feature_bindings.items():
            if feature in {"open-item", "open-row"} and isinstance(capability, str):
                open_capability = capability
            if (
                isinstance(feature, str)
                and "edit" in feature
                and isinstance(capability, str)
                and mapping.get("pattern") == default_pattern
            ):
                inline_edit_capability = capability

    navigation = allowed.get(open_capability or "", {}).get("backed_by")
    general_to_specific = default.get("navigation_model") == "general-to-specific"
    if (
        general_to_specific
        and (
            not isinstance(navigation, str)
            or not navigation.startswith("navigation:")
            or "detail" not in navigation.lower()
        )
        and not override
    ):
        _finding(
            findings,
            "PRIMARY_CATALOGUE_MISSING_DETAIL_DRILLDOWN",
            "primary entity catalogue row opening must transition to a dedicated detail navigation target",
            screen=screen,
        )

    if inline_edit_capability is not None:
        backing = allowed.get(inline_edit_capability, {}).get("backed_by")
        if not isinstance(backing, str) or not backing.startswith("command:"):
            _finding(
                findings,
                "PRIMARY_CATALOGUE_INLINE_EDIT_NOT_COMMAND_BACKED",
                "primary catalogue inline edit must be backed by an accepted command capability",
                screen=screen,
            )
        if detail.get("inline_editing") == "explicit-override-only" and not override:
            _finding(
                findings,
                "PRIMARY_CATALOGUE_INLINE_EDIT_REQUIRES_OVERRIDE",
                "primary catalogue inline edit requires an explicit Screen/View override with rationale",
                screen=screen,
            )

    query_reads = [
        binding
        for binding in reads.values()
        if isinstance(binding.get("query"), dict) and binding.get("query")
    ]
    query_expected = bool(expected_controls or scaling)
    if query_expected and not query_reads and not override:
        _finding(
            findings,
            "MISSING_CATALOGUE_QUERY_CONTRACT",
            "primary entity catalogue query controls require an accepted read query contract",
            screen=screen,
        )
        return

    for binding in query_reads:
        query = binding.get("query") or {}
        operation_id = binding.get("operation_id")
        if isinstance(operation_id, str) and operation_id in query_parameters_by_operation:
            missing = sorted(set(query) - query_parameters_by_operation[operation_id])
            for parameter in missing:
                _finding(
                    findings,
                    "CATALOGUE_QUERY_PARAMETER_NOT_IN_INTERFACE",
                    f"accepted catalogue query field {parameter} is absent from operation {operation_id}",
                    screen=screen,
                )

        if "search" in allowed and "search" not in query:
            _finding(
                findings,
                "CATALOGUE_SEARCH_NOT_IN_QUERY_CONTRACT",
                "allowed catalogue search capability is missing query.search semantics",
                screen=screen,
            )
        if "sort" in allowed and not {"sortBy", "sortDirection"} <= set(query):
            _finding(
                findings,
                "CATALOGUE_SORT_NOT_IN_QUERY_CONTRACT",
                "allowed catalogue sort capability requires sortBy and sortDirection semantics",
                screen=screen,
            )
        if "pagination" in allowed and not {"page", "pageSize"} <= set(query):
            _finding(
                findings,
                "CATALOGUE_PAGING_NOT_IN_QUERY_CONTRACT",
                "allowed catalogue pagination capability requires page and pageSize semantics",
                screen=screen,
            )
        if "filter" in allowed:
            reserved = {"search", "sortBy", "sortDirection", "page", "pageSize"}
            if not (set(query) - reserved):
                _finding(
                    findings,
                    "CATALOGUE_FILTER_NOT_IN_QUERY_CONTRACT",
                    "allowed catalogue filter capability requires at least one accepted attribute query field",
                    screen=screen,
                )


def _finding(findings: list[dict[str, Any]], code: str, detail: str, *, screen: str | None = None) -> None:
    row = {"code": code, "detail": detail}
    if screen:
        row["screen"] = screen
    findings.append(row)


def _ids(rows: Iterable[Any], *, screen: str, kind: str, findings: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for row in rows:
        if not isinstance(row, dict):
            _finding(findings, "INVALID_BINDING", f"{kind} binding must be a mapping", screen=screen)
            continue
        item_id = row.get("id")
        if not isinstance(item_id, str) or not item_id:
            _finding(findings, "MISSING_BINDING_ID", f"{kind} binding id is required", screen=screen)
            continue
        if item_id in result:
            _finding(findings, "DUPLICATE_BINDING_ID", f"duplicate {kind} binding {item_id}", screen=screen)
            continue
        result[item_id] = row
    return result


def _source_root(source: str) -> tuple[str, str] | None:
    if ":" not in source:
        return None
    kind, rest = source.split(":", 1)
    root = rest.split(".", 1)[0]
    return kind, root


def _validate_source(
    source: Any,
    *,
    screen: str,
    reads: set[str],
    commands: set[str],
    findings: list[dict[str, Any]],
    context: str,
    binding_operations: dict[tuple[str, str], str] | None = None,
    response_codes: dict[str, set[str]] | None = None,
) -> None:
    values = source if isinstance(source, list) else [source]
    for value in values:
        if not isinstance(value, str) or not value:
            _finding(findings, "INVALID_SOURCE_REF", f"{context} requires a non-empty source reference", screen=screen)
            continue
        parsed = _source_root(value)
        if parsed is None:
            _finding(findings, "INVALID_SOURCE_REF", f"{context} source must use kind:id form: {value}", screen=screen)
            continue
        kind, root = parsed
        if kind == "read" and root not in reads:
            _finding(findings, "UNKNOWN_READ_REF", f"{context} references unknown read {root}", screen=screen)
        elif kind == "command" and root not in commands:
            _finding(findings, "UNKNOWN_COMMAND_REF", f"{context} references unknown command {root}", screen=screen)
        elif kind not in {"read", "command", "local", "navigation", "semantic"}:
            _finding(findings, "UNSUPPORTED_SOURCE_REF", f"{context} uses unsupported source kind {kind}", screen=screen)
        elif kind in {"read", "command"} and root in (reads if kind == "read" else commands):
            tail = value.split(":", 1)[1].split(".", 1)
            if len(tail) == 2:
                match = re.match(r"^(\d{3})(?:-|$)", tail[1])
                if match and binding_operations is not None and response_codes is not None:
                    operation_id = binding_operations.get((kind, root))
                    if operation_id in response_codes and match.group(1) not in response_codes[operation_id]:
                        _finding(
                            findings,
                            "UNSUPPORTED_OPERATION_OUTCOME",
                            f"{context} references HTTP {match.group(1)} absent from {operation_id}",
                            screen=screen,
                        )


def evaluate_presentation_provider_contract(
    presentation: dict[str, Any],
    screen_design: dict[str, Any],
    provider_contract: dict[str, Any],
    *,
    screen_ids: set[str] | None = None,
) -> list[dict[str, Any]]:
    """Check that provider realization covers accepted patterns without owning semantics."""
    findings: list[dict[str, Any]] = []
    patterns = presentation.get("patterns", {}) or {}
    if not isinstance(patterns, dict):
        patterns = {}

    provider = provider_contract.get("provider")
    if not isinstance(provider, str) or not provider:
        _finding(findings, "MISSING_PRESENTATION_PROVIDER", "presentation provider id is required")
    if not (provider_contract.get("version") or provider_contract.get("ref")):
        _finding(findings, "UNPINNED_PRESENTATION_PROVIDER", "presentation provider requires immutable version or ref")

    default = (provider_contract.get("feature_policy") or {}).get("default")
    if default != "deny":
        _finding(
            findings,
            "UNSAFE_PROVIDER_FEATURE_DEFAULT",
            "presentation provider feature_policy.default must be deny",
        )

    mappings = provider_contract.get("pattern_mappings", {}) or {}
    if not isinstance(mappings, dict):
        _finding(findings, "INVALID_PROVIDER_PATTERN_MAPPINGS", "provider pattern_mappings must be a mapping")
        mappings = {}

    required_patterns = {
        item for item in (provider_contract.get("required_patterns", []) or [])
        if isinstance(item, str) and item
    }
    for row in screen_design.get("screens", []) or []:
        if not isinstance(row, dict):
            continue
        screen = row.get("id")
        if screen_ids is not None and screen not in screen_ids:
            continue
        required_patterns.update(
            item for item in (row.get("patterns", []) or [])
            if isinstance(item, str) and item
        )

    for pattern_id, mapping in mappings.items():
        if pattern_id not in patterns:
            _finding(
                findings,
                "UNKNOWN_PROVIDER_PATTERN",
                f"provider maps unknown presentation pattern {pattern_id}",
            )
        if not isinstance(mapping, dict):
            _finding(
                findings,
                "INVALID_PROVIDER_PATTERN_MAPPING",
                f"provider mapping for {pattern_id} must be a mapping",
            )
            continue
        adapter = mapping.get("adapter")
        if not isinstance(adapter, str) or not adapter:
            _finding(
                findings,
                "MISSING_PROVIDER_ADAPTER",
                f"provider mapping for {pattern_id} requires adapter",
            )
        primitives = mapping.get("provider_primitives")
        if not isinstance(primitives, list) or not primitives or not all(
            isinstance(item, str) and item for item in primitives
        ):
            _finding(
                findings,
                "MISSING_PROVIDER_PRIMITIVES",
                f"provider mapping for {pattern_id} requires provider_primitives",
            )
        if mapping.get("enabled_features"):
            _finding(
                findings,
                "PROVIDER_FEATURE_ENABLEMENT_FORBIDDEN",
                f"provider mapping for {pattern_id} cannot enable product features; bind them in Screen/View semantics",
            )

    for pattern_id in sorted(required_patterns - set(mappings)):
        _finding(
            findings,
            "MISSING_PROVIDER_PATTERN_MAPPING",
            f"required presentation pattern {pattern_id} has no provider mapping",
        )

    return findings


def evaluate_frontend_screen_contracts(
    presentation: dict[str, Any],
    screen_design: dict[str, Any],
    interface_contract: dict[str, Any] | None = None,
    *,
    screen_ids: set[str] | None = None,
    provider_contract: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Evaluate semantic closure while keeping provider realization subordinate to it."""
    findings: list[dict[str, Any]] = []
    if provider_contract is not None:
        findings.extend(
            evaluate_presentation_provider_contract(
                presentation,
                screen_design,
                provider_contract,
                screen_ids=screen_ids,
            )
        )
    operations = operation_ids(interface_contract)
    responses_by_operation = operation_response_codes(interface_contract)
    query_parameters_by_operation = operation_query_parameters(interface_contract)
    patterns = presentation.get("patterns", {}) or {}
    if not isinstance(patterns, dict):
        _finding(findings, "INVALID_PATTERN_CATALOGUE", "presentation patterns must be a mapping")
        patterns = {}

    baseline = presentation.get("external_baseline")
    if baseline is not None:
        if not isinstance(baseline, dict):
            _finding(findings, "INVALID_EXTERNAL_BASELINE", "external_baseline must be a mapping")
        else:
            if not baseline.get("provider") or not baseline.get("artifact"):
                _finding(findings, "UNPINNED_EXTERNAL_BASELINE", "external baseline requires provider and artifact")
            if not (baseline.get("version") or baseline.get("ref")):
                _finding(findings, "UNPINNED_EXTERNAL_BASELINE", "external baseline requires immutable version or ref")
            default = (baseline.get("feature_policy") or {}).get("default")
            if default != "deny":
                _finding(
                    findings,
                    "UNSAFE_PROVIDER_FEATURE_DEFAULT",
                    "external baseline feature_policy.default must be deny",
                )

    screens = screen_design.get("screens", []) or []
    evaluated: list[str] = []
    for row in screens:
        if not isinstance(row, dict):
            _finding(findings, "INVALID_SCREEN", "screen entry must be a mapping")
            continue
        screen = row.get("id")
        if not isinstance(screen, str) or not screen:
            _finding(findings, "MISSING_SCREEN_ID", "screen id is required")
            continue
        if screen_ids is not None and screen not in screen_ids:
            continue
        evaluated.append(screen)

        contract = row.get("semantic_contract")
        if not isinstance(contract, dict):
            _finding(findings, "MISSING_SEMANTIC_CONTRACT", "screen semantic_contract is required", screen=screen)
            continue

        reads = _ids(contract.get("reads", []) or [], screen=screen, kind="read", findings=findings)
        commands = _ids(contract.get("commands", []) or [], screen=screen, kind="command", findings=findings)

        binding_operations: dict[tuple[str, str], str] = {}
        for kind, bindings in (("read", reads), ("command", commands)):
            for binding_id, binding in bindings.items():
                operation_id = binding.get("operation_id")
                if not isinstance(operation_id, str) or not operation_id:
                    _finding(findings, "MISSING_OPERATION_ID", f"{kind} {binding_id} requires operation_id", screen=screen)
                else:
                    binding_operations[(kind, binding_id)] = operation_id
                if isinstance(operation_id, str) and operation_id and interface_contract is not None and operation_id not in operations:
                    _finding(
                        findings,
                        "UNKNOWN_INTERFACE_OPERATION",
                        f"{kind} {binding_id} references absent operationId {operation_id}",
                        screen=screen,
                    )

        view_model = contract.get("view_model")
        if not isinstance(view_model, dict) or not view_model.get("id"):
            _finding(findings, "MISSING_VIEW_MODEL", "semantic view_model with id is required", screen=screen)
        else:
            fields = view_model.get("fields", []) or []
            if not isinstance(fields, list) or not fields:
                _finding(findings, "EMPTY_VIEW_MODEL", "view_model fields are required", screen=screen)
            else:
                field_ids: set[str] = set()
                for field in fields:
                    if not isinstance(field, dict) or not field.get("id"):
                        _finding(findings, "INVALID_VIEW_MODEL_FIELD", "view_model field requires id", screen=screen)
                        continue
                    field_id = field["id"]
                    if field_id in field_ids:
                        _finding(findings, "DUPLICATE_VIEW_MODEL_FIELD", f"duplicate view_model field {field_id}", screen=screen)
                    field_ids.add(field_id)
                    _validate_source(
                        field.get("source"),
                        screen=screen,
                        reads=set(reads),
                        commands=set(commands),
                        findings=findings,
                        context=f"view_model.{field_id}",
                        binding_operations=binding_operations,
                        response_codes=responses_by_operation,
                    )

        capability_block = contract.get("capabilities")
        if not isinstance(capability_block, dict):
            _finding(findings, "MISSING_CAPABILITY_POLICY", "semantic capabilities allow/exclude policy is required", screen=screen)
            allowed_rows = []
            excluded_rows = []
        else:
            allowed_rows = capability_block.get("allowed", []) or []
            excluded_rows = capability_block.get("excluded", []) or []

        allowed: dict[str, dict[str, Any]] = {}
        for capability in allowed_rows:
            if not isinstance(capability, dict) or not capability.get("id"):
                _finding(findings, "INVALID_ALLOWED_CAPABILITY", "allowed capability requires id and backed_by", screen=screen)
                continue
            capability_id = capability["id"]
            if capability_id in allowed:
                _finding(findings, "DUPLICATE_ALLOWED_CAPABILITY", f"duplicate allowed capability {capability_id}", screen=screen)
                continue
            allowed[capability_id] = capability
            _validate_source(
                capability.get("backed_by"),
                screen=screen,
                reads=set(reads),
                commands=set(commands),
                findings=findings,
                context=f"capability.{capability_id}",
                binding_operations=binding_operations,
                response_codes=responses_by_operation,
            )

        excluded = {item for item in excluded_rows if isinstance(item, str) and item}
        overlap = set(allowed) & excluded
        for capability_id in sorted(overlap):
            _finding(findings, "CAPABILITY_ALLOW_EXCLUDE_CONFLICT", f"{capability_id} is both allowed and excluded", screen=screen)

        mappings = contract.get("pattern_mapping", []) or []
        if not isinstance(mappings, list) or not mappings:
            _finding(findings, "MISSING_PATTERN_MAPPING", "at least one presentation pattern mapping is required", screen=screen)
            mappings = []
        mapped_patterns = {
            mapping.get("pattern")
            for mapping in mappings
            if isinstance(mapping, dict) and mapping.get("pattern")
        }
        declared_patterns = {
            pattern
            for pattern in (row.get("patterns", []) or [])
            if isinstance(pattern, str) and pattern
        }
        for pattern in sorted(declared_patterns - mapped_patterns):
            _finding(
                findings,
                "UNMAPPED_PRESENTATION_PATTERN",
                f"declared pattern {pattern} has no semantic pattern mapping",
                screen=screen,
            )

        declared_actions: set[str] = set()
        primary_action = row.get("primary_action_role")
        if isinstance(primary_action, str) and primary_action:
            declared_actions.add(primary_action)
        action_hierarchy = row.get("action_hierarchy") or {}
        if isinstance(action_hierarchy, dict):
            declared_actions.update(
                value for value in action_hierarchy.values()
                if isinstance(value, str) and value
            )
        for action in sorted(declared_actions - set(allowed)):
            _finding(
                findings,
                "SCREEN_ACTION_NOT_AUTHORIZED",
                f"declared screen action {action} has no allowed semantic capability",
                screen=screen,
            )

        for mapping in mappings:
            if not isinstance(mapping, dict):
                _finding(findings, "INVALID_PATTERN_MAPPING", "pattern mapping must be a mapping", screen=screen)
                continue
            pattern_id = mapping.get("pattern")
            if pattern_id not in patterns:
                _finding(findings, "UNKNOWN_PRESENTATION_PATTERN", f"unknown pattern {pattern_id}", screen=screen)
                continue
            offered = {
                item
                for item in (patterns.get(pattern_id, {}) or {}).get("features", []) or []
                if isinstance(item, str) and item
            }
            feature_bindings = mapping.get("feature_bindings", {}) or {}
            if not isinstance(feature_bindings, dict):
                _finding(findings, "INVALID_FEATURE_BINDINGS", f"{pattern_id} feature_bindings must be a mapping", screen=screen)
                continue
            for feature, capability_id in feature_bindings.items():
                if offered and feature not in offered:
                    _finding(findings, "UNKNOWN_PATTERN_FEATURE", f"{pattern_id} does not offer feature {feature}", screen=screen)
                if capability_id not in allowed:
                    _finding(
                        findings,
                        "PRESENTATION_FEATURE_NOT_AUTHORIZED",
                        f"{pattern_id}.{feature} maps to non-allowed capability {capability_id}",
                        screen=screen,
                    )

        _validate_entity_collection_default(
            presentation=presentation,
            screen_row=row,
            screen=screen,
            contract=contract,
            reads=reads,
            allowed=allowed,
            mappings=mappings,
            binding_operations=binding_operations,
            query_parameters_by_operation=query_parameters_by_operation,
            findings=findings,
        )

        states = row.get("states", []) or []
        state_mapping = contract.get("state_mapping")
        if states and not isinstance(state_mapping, dict):
            _finding(findings, "MISSING_STATE_MAPPING", "state_mapping is required for declared screen states", screen=screen)
        elif isinstance(state_mapping, dict):
            missing_states = [state for state in states if state not in state_mapping]
            for state in missing_states:
                _finding(findings, "UNMAPPED_SCREEN_STATE", f"state {state} has no semantic source", screen=screen)
            for state, source in state_mapping.items():
                _validate_source(
                    source,
                    screen=screen,
                    reads=set(reads),
                    commands=set(commands),
                    findings=findings,
                    context=f"state.{state}",
                    binding_operations=binding_operations,
                    response_codes=responses_by_operation,
                )

        verification = contract.get("verification")
        if not isinstance(verification, dict):
            _finding(findings, "MISSING_VERIFICATION_CONTRACT", "verification contract is required", screen=screen)
        else:
            for key in ("contract", "semantic", "rendered"):
                value = verification.get(key)
                if not isinstance(value, list) or not value:
                    _finding(findings, "INCOMPLETE_VERIFICATION_CONTRACT", f"verification.{key} requires at least one proof obligation", screen=screen)

    if screen_ids is not None:
        missing = sorted(screen_ids - set(evaluated))
        for screen in missing:
            _finding(findings, "MISSING_REQUIRED_SCREEN", "required screen not found in screen design", screen=screen)

    return {
        "version": 1,
        "kind": "harness-frontend-screen-contract-evaluation",
        "status": "ACCEPTED" if not findings else "REJECTED",
        "screens_evaluated": sorted(evaluated),
        "operation_ids": sorted(operations),
        "findings": findings,
    }


def semantic_evaluation(
    result: dict[str, Any],
    *,
    artifact: str,
    capability: str,
    semantic_claims: list[str],
) -> dict[str, Any]:
    """Adapt a screen-contract evaluation to Harness semantic-acceptance evidence."""
    accepted = semantic_claims if result.get("status") == "ACCEPTED" else []
    return {
        "version": 1,
        "kind": "harness-artifact-semantic-evaluation",
        "artifact": artifact,
        "capability": capability,
        "status": result.get("status"),
        "obligations": {
            "expected": ["screen-semantic-closure"],
            "satisfied": ["screen-semantic-closure"] if accepted else [],
        },
        "findings": list(result.get("findings", [])),
        "semantic_claims": {"accepted": accepted},
    }
