#!/usr/bin/env python3
"""Validate one source-bounded BPMN application-process generated projection."""
from __future__ import annotations

import argparse
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

import yaml

from harness.project_model.core import CoreError
from harness.workspace.projection_boundary import (
    bind_projection_sources,
    repository_relative_path,
)

PROJECTION_ID = "application-process-bpmn"
PROFILE_KIND = "harness-bpmn-process-profile"
PROVENANCE_KIND = "harness-generated-projection-provenance"
EXPECTED_FLOW_NODES = {
    "startEvent",
    "endEvent",
    "task",
    "userTask",
    "exclusiveGateway",
    "parallelGateway",
}
EXPECTED_GATEWAY_DIRECTIONS = {"Diverging", "Converging"}


def load_yaml(path: str | Path) -> dict[str, Any]:
    path = Path(path)
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise CoreError(f"cannot load {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise CoreError(f"{path} must contain a mapping")
    return value


def _local(tag: str) -> str:
    return tag.split("}", 1)[1] if tag.startswith("{") else tag


def validate_profile(profile: dict[str, Any]) -> dict[str, Any]:
    if profile.get("version") != 1:
        raise CoreError("BPMN process profile version must be 1")
    if profile.get("kind") != PROFILE_KIND:
        raise CoreError("unexpected BPMN process profile kind")
    if profile.get("projection") != PROJECTION_ID:
        raise CoreError("BPMN process profile projection id mismatch")
    if not isinstance(profile.get("id"), str) or not profile["id"]:
        raise CoreError("BPMN process profile id is required")

    scope = profile.get("scope")
    if not isinstance(scope, dict):
        raise CoreError("BPMN process profile scope must be a mapping")
    try:
        re.compile(scope.get("id_pattern", ""))
    except re.error as exc:
        raise CoreError(f"BPMN process scope id_pattern is invalid: {exc}") from exc

    output = profile.get("output")
    if not isinstance(output, dict):
        raise CoreError("BPMN process profile output must be a mapping")
    for key in ("bpmn", "provenance"):
        value = output.get(key)
        if not isinstance(value, str) or "{scope-id}" not in value:
            raise CoreError(f"BPMN process {key} output must contain {{scope-id}}")
        normalized = repository_relative_path(value, f"BPMN process {key} output")
        if not normalized.startswith("docs/generated/"):
            raise CoreError(f"BPMN process {key} output must remain under docs/generated/")

    bpmn = profile.get("bpmn")
    if not isinstance(bpmn, dict):
        raise CoreError("BPMN process profile bpmn must be a mapping")
    if bpmn.get("namespace") != "http://www.omg.org/spec/BPMN/20100524/MODEL":
        raise CoreError("BPMN process profile namespace is invalid")
    if not isinstance(bpmn.get("target_namespace"), str) or not bpmn["target_namespace"]:
        raise CoreError("BPMN process target_namespace is required")
    if bpmn.get("process_is_executable") is not False:
        raise CoreError("BPMN process v1 must remain non-executable")
    if set(bpmn.get("supported_flow_nodes", []) or []) != EXPECTED_FLOW_NODES:
        raise CoreError("BPMN process supported_flow_nodes do not match v1 contract")
    if set(bpmn.get("supported_gateway_directions", []) or []) != EXPECTED_GATEWAY_DIRECTIONS:
        raise CoreError("BPMN process gateway directions do not match v1 contract")
    if bpmn.get("allow_cycles") is not False:
        raise CoreError("BPMN process v1 must reject cycles")
    if bpmn.get("allow_event_definitions") is not False:
        raise CoreError("BPMN process v1 must reject event definitions")
    if bpmn.get("allow_extensions") is not False:
        raise CoreError("BPMN process v1 must reject extensions")
    if bpmn.get("require_explicit_exclusive_branch_labels") is not True:
        raise CoreError("BPMN process v1 requires exclusive branch labels")
    markers = bpmn.get("require_markers")
    if not isinstance(markers, list) or set(markers) != {
        "GENERATED PROJECTION",
        "NOT A SOURCE OF TRUTH",
    }:
        raise CoreError("BPMN process generated markers are invalid")
    return profile


def _scope_id(profile: dict[str, Any], scope_id: str) -> str:
    validate_profile(profile)
    pattern = profile["scope"]["id_pattern"]
    if not isinstance(scope_id, str) or not re.fullmatch(pattern, scope_id):
        raise CoreError(f"BPMN process scope-id is invalid: {scope_id}")
    return scope_id


def expected_output_paths(profile: dict[str, Any], scope_id: str) -> dict[str, str]:
    scope_id = _scope_id(profile, scope_id)
    result = {
        key: repository_relative_path(
            value.replace("{scope-id}", scope_id),
            f"BPMN process {key} output",
        )
        for key, value in profile["output"].items()
    }
    if result["bpmn"] == result["provenance"]:
        raise CoreError("BPMN process output and provenance paths must differ")
    return result


def expected_provenance(
    manifest: dict[str, Any],
    plan: dict[str, Any],
    *,
    document_id: str,
    section_id: str,
    scope_id: str,
    profile: dict[str, Any],
) -> dict[str, Any]:
    scope_id = _scope_id(profile, scope_id)
    section, sources = bind_projection_sources(
        manifest,
        plan,
        document_id=document_id,
        section_id=section_id,
        renderer=PROJECTION_ID,
        projection_label="BPMN process projection",
    )
    if section.get("scope") != scope_id:
        raise CoreError("BPMN process scope does not match plan scope")
    paths = expected_output_paths(profile, scope_id)
    return {
        "version": 1,
        "kind": PROVENANCE_KIND,
        "projection": PROJECTION_ID,
        "profile": profile["id"],
        "profile_version": profile["version"],
        "manifest_digest": manifest["manifest_digest"],
        "document": document_id,
        "section": section_id,
        "scope": scope_id,
        "sources": sources,
        "outputs": [paths["bpmn"], paths["provenance"]],
    }


def _require_attrs(element: ET.Element, required: set[str], allowed: set[str]) -> None:
    actual = set(element.attrib)
    missing = sorted(required - actual)
    if missing:
        raise CoreError(f"BPMN {_local(element.tag)} requires attributes: {', '.join(missing)}")
    unexpected = sorted(actual - allowed)
    if unexpected:
        raise CoreError(
            f"BPMN {_local(element.tag)} has unsupported attributes: {', '.join(unexpected)}"
        )
    for name in required:
        if not element.attrib.get(name, "").strip():
            raise CoreError(f"BPMN {_local(element.tag)} attribute {name} must be non-empty")


def _ensure_no_children(element: ET.Element) -> None:
    if list(element):
        raise CoreError(f"BPMN {_local(element.tag)} child constructs are unsupported in v1")


def _reachable(start: str, adjacency: dict[str, list[str]]) -> set[str]:
    seen: set[str] = set()
    stack = [start]
    while stack:
        node = stack.pop()
        if node in seen:
            continue
        seen.add(node)
        stack.extend(adjacency.get(node, []))
    return seen


def _has_cycle(nodes: set[str], adjacency: dict[str, list[str]]) -> bool:
    state: dict[str, int] = {node: 0 for node in nodes}

    def visit(node: str) -> bool:
        state[node] = 1
        for nxt in adjacency.get(node, []):
            if state[nxt] == 1:
                return True
            if state[nxt] == 0 and visit(nxt):
                return True
        state[node] = 2
        return False

    return any(state[node] == 0 and visit(node) for node in sorted(nodes))


def validate_bpmn(text: str, profile: dict[str, Any]) -> None:
    validate_profile(profile)
    if not isinstance(text, str) or not text.strip():
        raise CoreError("BPMN process content is required")
    for marker in profile["bpmn"]["require_markers"]:
        if marker not in text:
            raise CoreError(f"BPMN process requires generated marker: {marker}")
    if "<!DOCTYPE" in text.upper() or "<!ENTITY" in text.upper():
        raise CoreError("BPMN process forbids DOCTYPE/entity declarations")

    try:
        root = ET.fromstring(text)
    except ET.ParseError as exc:
        raise CoreError(f"invalid BPMN XML: {exc}") from exc

    ns = profile["bpmn"]["namespace"]
    if root.tag != f"{{{ns}}}definitions":
        raise CoreError("BPMN process root must be BPMN definitions")
    _require_attrs(root, {"id", "targetNamespace"}, {"id", "targetNamespace"})
    if root.attrib["targetNamespace"] != profile["bpmn"]["target_namespace"]:
        raise CoreError("BPMN process targetNamespace does not match profile")

    root_children = list(root)
    if any(_local(item.tag) != "process" for item in root_children):
        raise CoreError("BPMN process v1 definitions may contain only process")
    if len(root_children) != 1:
        raise CoreError("BPMN process v1 requires exactly one process")
    process = root_children[0]
    _require_attrs(process, {"id", "name", "isExecutable"}, {"id", "name", "isExecutable"})
    if process.attrib["isExecutable"].lower() != "false":
        raise CoreError("BPMN process must be non-executable")

    allowed_children = EXPECTED_FLOW_NODES | {"sequenceFlow", "documentation"}
    ids: set[str] = set()
    nodes: dict[str, ET.Element] = {}
    flows: list[ET.Element] = []
    starts: list[str] = []
    ends: set[str] = set()

    for item in list(process):
        kind = _local(item.tag)
        if item.tag != f"{{{ns}}}{kind}":
            raise CoreError("BPMN process contains non-BPMN namespace content")
        if kind not in allowed_children:
            raise CoreError(f"unsupported BPMN process construct: {kind}")
        if kind == "documentation":
            if item.attrib:
                raise CoreError("BPMN documentation attributes are unsupported")
            continue
        if kind == "sequenceFlow":
            _require_attrs(
                item,
                {"id", "sourceRef", "targetRef"},
                {"id", "sourceRef", "targetRef", "name"},
            )
            _ensure_no_children(item)
            flows.append(item)
            element_id = item.attrib["id"]
        else:
            allowed_attrs = {"id", "name"}
            required = {"id", "name"}
            if kind in {"exclusiveGateway", "parallelGateway"}:
                allowed_attrs.add("gatewayDirection")
                required.add("gatewayDirection")
            _require_attrs(item, required, allowed_attrs)
            _ensure_no_children(item)
            element_id = item.attrib["id"]
            nodes[element_id] = item
            if kind == "startEvent":
                starts.append(element_id)
            elif kind == "endEvent":
                ends.add(element_id)

        if element_id in ids:
            raise CoreError(f"duplicate BPMN id: {element_id}")
        ids.add(element_id)

    if len(starts) != 1:
        raise CoreError("BPMN process v1 requires exactly one startEvent")
    if not ends:
        raise CoreError("BPMN process v1 requires at least one endEvent")
    if not flows:
        raise CoreError("BPMN process requires sequenceFlow")

    incoming = {node: [] for node in nodes}
    outgoing = {node: [] for node in nodes}
    adjacency = {node: [] for node in nodes}
    reverse = {node: [] for node in nodes}

    for flow in flows:
        source = flow.attrib["sourceRef"]
        target = flow.attrib["targetRef"]
        if source not in nodes:
            raise CoreError(f"BPMN sequenceFlow sourceRef does not exist: {source}")
        if target not in nodes:
            raise CoreError(f"BPMN sequenceFlow targetRef does not exist: {target}")
        outgoing[source].append(flow)
        incoming[target].append(flow)
        adjacency[source].append(target)
        reverse[target].append(source)

    start = starts[0]
    if incoming[start]:
        raise CoreError("BPMN startEvent must not have incoming flow")
    if len(outgoing[start]) != 1:
        raise CoreError("BPMN startEvent must have exactly one outgoing flow")

    for node_id, node in nodes.items():
        kind = _local(node.tag)
        in_count = len(incoming[node_id])
        out_count = len(outgoing[node_id])
        if kind == "endEvent":
            if out_count:
                raise CoreError("BPMN endEvent must not have outgoing flow")
            if in_count != 1:
                raise CoreError("BPMN endEvent must have exactly one incoming flow")
            continue
        if kind == "startEvent":
            continue
        if kind in {"task", "userTask"}:
            if in_count != 1 or out_count != 1:
                raise CoreError(
                    f"BPMN {kind} must have exactly one incoming and one outgoing flow; "
                    "use explicit gateways for branching/merging"
                )
            continue
        if kind in {"exclusiveGateway", "parallelGateway"}:
            direction = node.attrib["gatewayDirection"]
            if direction not in EXPECTED_GATEWAY_DIRECTIONS:
                raise CoreError(f"BPMN gateway direction is unsupported: {direction}")
            if direction == "Diverging":
                if in_count != 1 or out_count < 2:
                    raise CoreError("BPMN divergent gateway requires one incoming and at least two outgoing flows")
                if kind == "exclusiveGateway":
                    missing_labels = [
                        flow.attrib["id"]
                        for flow in outgoing[node_id]
                        if not flow.attrib.get("name", "").strip()
                    ]
                    if missing_labels:
                        raise CoreError(
                            "BPMN divergent exclusiveGateway requires explicit branch labels: "
                            + ", ".join(missing_labels)
                        )
            else:
                if in_count < 2 or out_count != 1:
                    raise CoreError("BPMN converging gateway requires at least two incoming and one outgoing flow")

    reachable = _reachable(start, adjacency)
    missing_from_start = sorted(set(nodes) - reachable)
    if missing_from_start:
        raise CoreError(
            "BPMN flow nodes are unreachable from start: " + ", ".join(missing_from_start)
        )

    can_reach_end: set[str] = set()
    stack = list(ends)
    while stack:
        node = stack.pop()
        if node in can_reach_end:
            continue
        can_reach_end.add(node)
        stack.extend(reverse.get(node, []))
    incomplete = sorted(set(nodes) - can_reach_end)
    if incomplete:
        raise CoreError(
            "BPMN flow nodes cannot reach completion: " + ", ".join(incomplete)
        )

    if _has_cycle(set(nodes), adjacency):
        raise CoreError("BPMN process v1 does not support cycles/repetition")


def validate_generated_projection(
    manifest: dict[str, Any],
    plan: dict[str, Any],
    *,
    document_id: str,
    section_id: str,
    scope_id: str,
    profile: dict[str, Any],
    bpmn_text: str,
    provenance: dict[str, Any],
    bpmn_path: str | None = None,
    provenance_path: str | None = None,
) -> None:
    expected = expected_provenance(
        manifest,
        plan,
        document_id=document_id,
        section_id=section_id,
        scope_id=scope_id,
        profile=profile,
    )
    if provenance != expected:
        raise CoreError("BPMN process projection provenance does not match current manifest/plan/scope")
    paths = expected_output_paths(profile, scope_id)
    if bpmn_path is not None and repository_relative_path(bpmn_path, "BPMN path") != paths["bpmn"]:
        raise CoreError("BPMN process path does not match profile/scope")
    if (
        provenance_path is not None
        and repository_relative_path(provenance_path, "BPMN provenance path")
        != paths["provenance"]
    ):
        raise CoreError("BPMN provenance path does not match profile/scope")
    validate_bpmn(bpmn_text, profile)


def _write_yaml(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(value, sort_keys=False), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate one Harness BPMN application-process generated projection"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    for name in ("provenance", "validate"):
        command = sub.add_parser(name)
        command.add_argument("--manifest", required=True)
        command.add_argument("--plan", required=True)
        command.add_argument("--document", required=True)
        command.add_argument("--section", required=True)
        command.add_argument("--scope", required=True)
        command.add_argument("--profile", required=True)
        if name == "provenance":
            command.add_argument("--output")
        else:
            command.add_argument("--bpmn", required=True)
            command.add_argument("--provenance", required=True)

    args = parser.parse_args()
    manifest = load_yaml(args.manifest)
    plan = load_yaml(args.plan)
    profile = load_yaml(args.profile)

    if args.command == "provenance":
        provenance = expected_provenance(
            manifest,
            plan,
            document_id=args.document,
            section_id=args.section,
            scope_id=args.scope,
            profile=profile,
        )
        if args.output:
            expected_path = expected_output_paths(profile, args.scope)["provenance"]
            if repository_relative_path(args.output, "BPMN provenance output") != expected_path:
                raise CoreError("BPMN provenance output path does not match profile/scope")
            _write_yaml(Path(args.output), provenance)
        else:
            print(yaml.safe_dump(provenance, sort_keys=False), end="")
        return 0

    expected_paths = expected_output_paths(profile, args.scope)
    if repository_relative_path(args.bpmn, "BPMN path") != expected_paths["bpmn"]:
        raise CoreError("BPMN process path does not match profile/scope")
    if (
        repository_relative_path(args.provenance, "BPMN provenance path")
        != expected_paths["provenance"]
    ):
        raise CoreError("BPMN provenance path does not match profile/scope")

    provenance = load_yaml(args.provenance)
    bpmn_text = Path(args.bpmn).read_text(encoding="utf-8")
    validate_generated_projection(
        manifest,
        plan,
        document_id=args.document,
        section_id=args.section,
        scope_id=args.scope,
        profile=profile,
        bpmn_text=bpmn_text,
        provenance=provenance,
        bpmn_path=args.bpmn,
        provenance_path=args.provenance,
    )
    print("BPMN application-process projection valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
