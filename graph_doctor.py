#!/usr/bin/env python3
"""Research prototype: aggregate structural diagnostics for Harness project graphs."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml

from adapters.canonical_graph import project_model
from engineering_graph import (
    derive_profile,
    evaluate_engineering_target,
    validate_engineering_graph,
)
from harness import CoreError, validate_model
from integration_alignment import validate_project_alignment


SEVERITY_ORDER = {"ERROR": 0, "WARN": 1, "INFO": 2}


def finding(
    code: str,
    severity: str,
    message: str,
    *,
    owner: str | None = None,
    evidence: dict[str, Any] | None = None,
    suggestions: list[str] | None = None,
) -> dict[str, Any]:
    row: dict[str, Any] = {
        "code": code,
        "severity": severity,
        "message": message,
    }
    if owner:
        row["owner"] = owner
    if evidence:
        row["evidence"] = evidence
    if suggestions:
        row["suggestions"] = suggestions
    return row


def _productions(graph: dict[str, Any]) -> tuple[dict[str, str], dict[str, dict[str, Any]]]:
    producers: dict[str, str] = {}
    productions: dict[str, dict[str, Any]] = {}
    for authority in graph.get("authorities", []) or []:
        if not isinstance(authority, dict):
            continue
        authority_id = authority.get("id")
        for production in authority.get("produces", []) or []:
            if isinstance(production, str):
                capability = production
                production = {"capability": capability, "requires": []}
            elif isinstance(production, dict):
                capability = production.get("capability")
            else:
                continue
            if isinstance(capability, str) and capability:
                producers.setdefault(capability, authority_id)
                productions.setdefault(capability, production)
    return producers, productions


def _requirements(graph: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for authority in graph.get("authorities", []) or []:
        if not isinstance(authority, dict):
            continue
        authority_id = authority.get("id")
        for production in authority.get("produces", []) or []:
            if isinstance(production, str):
                continue
            if not isinstance(production, dict):
                continue
            capability = production.get("capability")
            for raw in production.get("requires", []) or []:
                req = raw if isinstance(raw, dict) else {"capability": raw}
                rows.append(
                    {
                        "kind": "production",
                        "consumer": capability,
                        "owner": authority_id,
                        "capability": req.get("capability"),
                    }
                )
    for consumer in graph.get("consumers", []) or []:
        if not isinstance(consumer, dict):
            continue
        consumer_id = consumer.get("id")
        for raw in consumer.get("requires", []) or []:
            req = raw if isinstance(raw, dict) else {"capability": raw}
            rows.append(
                {
                    "kind": "consumer",
                    "consumer": consumer_id,
                    "capability": req.get("capability"),
                }
            )
    return rows


def diagnose_engineering_graph(graph: dict[str, Any]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    producers, productions = _productions(graph)
    requirements = _requirements(graph)

    for authority in graph.get("authorities", []) or []:
        if not isinstance(authority, dict):
            continue
        authority_id = authority.get("id")
        if not (authority.get("produces", []) or []):
            findings.append(
                finding(
                    "AUTHORITY_NO_OUTPUTS",
                    "WARN",
                    f"Authority {authority_id} declares no public production contracts.",
                    owner=authority_id,
                    suggestions=[
                        "Remove the Authority if it is stale.",
                        "Add the public capability it actually owns if the omission is accidental.",
                    ],
                )
            )

    seen_producers: dict[str, str] = {}
    for authority in graph.get("authorities", []) or []:
        if not isinstance(authority, dict):
            continue
        authority_id = authority.get("id")
        for production in authority.get("produces", []) or []:
            capability = production if isinstance(production, str) else (
                production.get("capability") if isinstance(production, dict) else None
            )
            if not isinstance(capability, str) or not capability:
                continue
            previous = seen_producers.setdefault(capability, authority_id)
            if previous != authority_id:
                findings.append(
                    finding(
                        "CAPABILITY_MULTIPLE_PRODUCERS",
                        "ERROR",
                        f"Capability {capability} is produced by multiple Authorities: {previous}, {authority_id}.",
                        owner=authority_id,
                        evidence={"capability": capability, "producers": [previous, authority_id]},
                        suggestions=[
                            "Keep one semantic producer Authority for the CapabilityId.",
                            "Split the CapabilityId if the outputs are independently owned.",
                        ],
                    )
                )

    for req in requirements:
        capability = req.get("capability")
        if isinstance(capability, str) and capability and capability not in producers:
            findings.append(
                finding(
                    "CAPABILITY_NO_PRODUCER",
                    "ERROR",
                    f"{req['kind'].title()} {req['consumer']} requires {capability}, but no Authority produces it.",
                    owner=req.get("owner"),
                    evidence=req,
                    suggestions=[
                        "Declare the missing producer if this is accepted public knowledge.",
                        "Remove or replace the requirement if it is stale.",
                    ],
                )
            )

    consumed = {
        req["capability"]
        for req in requirements
        if isinstance(req.get("capability"), str)
    }
    terminal_rows = graph.get("terminal_capabilities", []) or []
    terminals = {
        row.get("capability"): row
        for row in terminal_rows
        if isinstance(row, dict) and isinstance(row.get("capability"), str)
    }
    for capability, authority in sorted(producers.items()):
        if capability not in consumed and capability not in terminals:
            findings.append(
                finding(
                    "CAPABILITY_DEAD_PUBLIC",
                    "ERROR",
                    f"Public capability {capability} is produced by {authority} but is neither consumed nor explicitly terminal.",
                    owner=authority,
                    evidence={"capability": capability},
                    suggestions=[
                        "Remove it from the public Engineering Graph if it is only an internal artifact fact.",
                        "Add a real downstream requirement if one is missing.",
                        "Declare it terminal with a reason only if it is intentionally terminal.",
                    ],
                )
            )

    for capability, terminal in terminals.items():
        producer = producers.get(capability)
        if producer is None:
            findings.append(
                finding(
                    "TERMINAL_NO_PRODUCER",
                    "ERROR",
                    f"Terminal capability {capability} has no producer.",
                    owner=terminal.get("authority"),
                    evidence=terminal,
                    suggestions=["Remove the stale terminal declaration or restore its producer."],
                )
            )
        elif capability in consumed:
            findings.append(
                finding(
                    "TERMINAL_ALREADY_CONSUMED",
                    "WARN",
                    f"Capability {capability} is declared terminal but is also consumed downstream.",
                    owner=producer,
                    evidence=terminal,
                    suggestions=["Remove the terminal declaration; consumed capabilities are not terminal."],
                )
            )
        elif terminal.get("authority") != producer:
            findings.append(
                finding(
                    "TERMINAL_OWNER_MISMATCH",
                    "ERROR",
                    f"Terminal declaration for {capability} names {terminal.get('authority')}, but producer is {producer}.",
                    owner=producer,
                    evidence=terminal,
                    suggestions=["Make terminal ownership match the capability producer."],
                )
            )

    # Preserve the canonical validator as a final backstop for cycles, malformed
    # boundaries and schema rules that are not duplicated here.
    try:
        validate_engineering_graph(graph)
    except CoreError as exc:
        message = str(exc)
        already_explained = False
        if "unconsumed public capabilities require explicit terminal declaration" in message:
            already_explained = any(
                row["code"] == "CAPABILITY_DEAD_PUBLIC"
                for row in findings
            )
        if not already_explained:
            code = "ENGINEERING_GRAPH_INVALID"
            if "production cycle" in message:
                code = "CAPABILITY_CYCLE"
            elif "multiple subjects" in message:
                code = "CAPABILITY_SUBJECT_COLLISION"
            elif "duplicate" in message:
                code = "ENGINEERING_GRAPH_DUPLICATE"
            findings.append(
                finding(
                    code,
                    "ERROR",
                    message,
                    suggestions=["Repair the Engineering Graph before relying on target-state evaluation."],
                )
            )

    return findings


def diagnose_model(
    model: dict[str, Any],
    *,
    source_root: str | Path | None = None,
    engineering_graph: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    artifacts = model.get("artifacts", []) or []
    questions = model.get("questions", []) or []

    by_id: dict[str, dict[str, Any]] = {}
    path_owners: dict[str, list[dict[str, Any]]] = {}
    for artifact in artifacts:
        if not isinstance(artifact, dict):
            continue
        artifact_id = artifact.get("id")
        path = artifact.get("path")
        if isinstance(artifact_id, str) and artifact_id:
            if artifact_id in by_id:
                findings.append(
                    finding(
                        "ARTIFACT_DUPLICATE_ID",
                        "ERROR",
                        f"Canonical artifact id {artifact_id} is registered more than once.",
                        evidence={"artifact": artifact_id},
                        suggestions=["Keep exactly one registration for each CanonicalArtifact id."],
                    )
                )
            else:
                by_id[artifact_id] = artifact
        if isinstance(path, str) and path:
            path_owners.setdefault(path, []).append(artifact)

    declared_authorities = {
        item.get("id")
        for item in model.get("authorities", []) or []
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }
    engineering_authorities = {
        item.get("id")
        for item in (engineering_graph or {}).get("authorities", []) or []
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }
    known_authorities = declared_authorities | engineering_authorities

    depended_on = {
        dep
        for artifact in artifacts
        if isinstance(artifact, dict)
        for dep in (artifact.get("depends_on", []) or [])
        if isinstance(dep, str)
    }
    for artifact_id, artifact in sorted(by_id.items()):
        owner = artifact.get("authority")
        if known_authorities and owner not in known_authorities:
            findings.append(
                finding(
                    "ARTIFACT_UNKNOWN_AUTHORITY",
                    "ERROR",
                    f"Artifact {artifact_id} is owned by unknown Authority {owner}.",
                    owner=owner if isinstance(owner, str) else None,
                    evidence={"artifact": artifact_id, "authority": owner},
                    suggestions=["Correct the artifact owner or restore the Authority declaration."],
                )
            )
        if not (artifact.get("provides", []) or []) and artifact_id not in depended_on:
            findings.append(
                finding(
                    "ARTIFACT_ORPHAN",
                    "WARN",
                    f"Artifact {artifact_id} provides no public capability and is not a dependency of another canonical artifact.",
                    owner=owner if isinstance(owner, str) else None,
                    evidence={"artifact": artifact_id, "path": artifact.get("path")},
                    suggestions=[
                        "Remove the stale artifact registration if it is obsolete.",
                        "Add the missing dependency edge if it is accepted supporting knowledge.",
                        "Expose a CapabilityId only if there is a real downstream consumer.",
                    ],
                )
            )

    for path, rows in sorted(path_owners.items()):
        if len(rows) > 1:
            findings.append(
                finding(
                    "ARTIFACT_DUPLICATE_PATH",
                    "ERROR",
                    f"Canonical path {path} is registered by multiple artifacts.",
                    evidence={
                        "path": path,
                        "artifacts": [row.get("id") for row in rows],
                        "authorities": [row.get("authority") for row in rows],
                    },
                    suggestions=[
                        "Keep one canonical owner/registration for the file.",
                        "If the file contains multiple independent concerns, split the artifact/file deliberately.",
                    ],
                )
            )

    for artifact_id, artifact in sorted(by_id.items()):
        owner = artifact.get("authority")
        path = artifact.get("path")
        for dep in artifact.get("depends_on", []) or []:
            if dep not in by_id:
                findings.append(
                    finding(
                        "ARTIFACT_DEPENDENCY_MISSING",
                        "ERROR",
                        f"Artifact {artifact_id} depends on unknown artifact {dep}.",
                        owner=owner,
                        evidence={"artifact": artifact_id, "dependency": dep},
                        suggestions=[
                            "Restore the missing artifact registration.",
                            "Remove the stale dependency if the relationship no longer exists.",
                        ],
                    )
                )

        if source_root is not None and isinstance(path, str) and path:
            actual = Path(source_root) / path
            if not actual.is_file():
                findings.append(
                    finding(
                        "ARTIFACT_FILE_MISSING",
                        "ERROR",
                        f"Canonical artifact {artifact_id} points to missing file {path}.",
                        owner=owner,
                        evidence={"artifact": artifact_id, "path": path},
                        suggestions=[
                            "Update the canonical path if the artifact moved.",
                            "Restore the file if it is still the accepted canonical artifact.",
                            "Delete the registration if the artifact is obsolete.",
                        ],
                    )
                )

        if isinstance(path, str) and (
            path.startswith("docs-generated/")
            or "/generated/" in path
            or path.startswith("generated/")
        ):
            findings.append(
                finding(
                    "CANONICAL_POINTS_TO_GENERATED",
                    "WARN",
                    f"Canonical artifact {artifact_id} points into generated output: {path}.",
                    owner=owner,
                    evidence={"artifact": artifact_id, "path": path},
                    suggestions=[
                        "Confirm this is intentionally canonical; generated projections should normally be disposable and non-canonical."
                    ],
                )
            )

    if engineering_graph is not None:
        producers, _ = _productions(engineering_graph)
        for artifact_id, artifact in sorted(by_id.items()):
            for capability in artifact.get("provides", []) or []:
                expected = producers.get(capability)
                if expected is None:
                    findings.append(
                        finding(
                            "ARTIFACT_PROVIDES_UNKNOWN_CAPABILITY",
                            "WARN",
                            f"Artifact {artifact_id} provides {capability}, which has no Engineering Graph producer.",
                            owner=artifact.get("authority"),
                            evidence={"artifact": artifact_id, "capability": capability},
                            suggestions=[
                                "Add the capability to the Engineering Graph if it is public engineering knowledge.",
                                "Remove it from artifact.provides if it is not a public CapabilityId.",
                            ],
                        )
                    )
                elif artifact.get("authority") != expected:
                    findings.append(
                        finding(
                            "PROVIDER_OWNER_MISMATCH",
                            "ERROR",
                            f"Artifact {artifact_id} provides {capability} under {artifact.get('authority')}, but producer is {expected}.",
                            owner=expected,
                            evidence={
                                "artifact": artifact_id,
                                "capability": capability,
                                "artifact_authority": artifact.get("authority"),
                                "producer_authority": expected,
                            },
                            suggestions=["Move the provider to the owning Authority or correct the Engineering Graph ownership."],
                        )
                    )

    known_caps: set[str] = set()
    if engineering_graph is not None:
        known_caps = set(_productions(engineering_graph)[0])

    for question in questions:
        if not isinstance(question, dict):
            continue
        qid = question.get("id")
        owner = question.get("authority")
        if known_authorities and owner not in known_authorities:
            findings.append(
                finding(
                    "QUESTION_UNKNOWN_AUTHORITY",
                    "ERROR",
                    f"Question {qid} is addressed to unknown Authority {owner}.",
                    owner=owner if isinstance(owner, str) else None,
                    evidence={"question": qid, "authority": owner},
                    suggestions=["Route the Question to an existing semantic owner or restore the missing Authority."],
                )
            )
        for artifact_id in question.get("blocks", []) or []:
            if artifact_id not in by_id:
                findings.append(
                    finding(
                        "QUESTION_BLOCKS_UNKNOWN_ARTIFACT",
                        "WARN",
                        f"Question {qid} blocks unknown artifact {artifact_id}.",
                        owner=owner,
                        evidence={"question": qid, "artifact": artifact_id},
                        suggestions=[
                            "Remove the stale block reference or restore the intended artifact registration."
                        ],
                    )
                )
        for capability in question.get("blocks_capabilities", []) or []:
            if engineering_graph is not None and capability not in known_caps:
                findings.append(
                    finding(
                        "QUESTION_BLOCKS_UNKNOWN_CAPABILITY",
                        "WARN",
                        f"Question {qid} blocks unknown capability {capability}.",
                        owner=owner,
                        evidence={"question": qid, "capability": capability},
                        suggestions=[
                            "Remove the stale capability block or restore the intended production contract."
                        ],
                    )
                )

    try:
        validate_model(model)
    except CoreError as exc:
        findings.append(
            finding(
                "CORE_MODEL_INVALID",
                "ERROR",
                str(exc),
                suggestions=["Repair the Core realization before target-state evaluation."],
            )
        )
    return findings


def _alignment_findings(
    source_graph: dict[str, Any],
    projection: dict[str, Any],
    engineering_graph: dict[str, Any],
    target: str | None,
) -> list[dict[str, Any]]:
    try:
        validate_project_alignment(
            source_graph,
            projection,
            engineering_graph,
            target_consumer=target,
        )
        return []
    except CoreError as exc:
        message = str(exc)
        code = "PROJECT_ALIGNMENT_INVALID"
        if "hidden project-graph upstream Authorities" in message:
            code = "ALIGNMENT_HIDDEN_DEPENDENCY"
        elif "phantom capability prerequisites" in message:
            code = "ALIGNMENT_PHANTOM_DEPENDENCY"
        elif "without Authority binding" in message:
            code = "ALIGNMENT_UNBOUND_ARTIFACT"
        elif "producer is" in message and "bound to" in message:
            code = "ALIGNMENT_OWNER_MISMATCH"
        return [
            finding(
                code,
                "ERROR",
                message,
                suggestions=[
                    "Make project artifact dependencies and capability prerequisites describe the same semantic frontier.",
                    "Do not silence the mismatch by broadening Authority-wide prerequisites.",
                ],
            )
        ]


def diagnose_project(
    engineering_graph: dict[str, Any],
    *,
    model: dict[str, Any] | None = None,
    source_graph: dict[str, Any] | None = None,
    projection: dict[str, Any] | None = None,
    target: str | None = None,
    source_root: str | Path | None = None,
) -> dict[str, Any]:
    findings = diagnose_engineering_graph(engineering_graph)

    realized = model
    if source_graph is not None and projection is not None:
        try:
            realized = project_model(source_graph, projection)
        except CoreError as exc:
            findings.append(
                finding(
                    "PROJECT_PROJECTION_INVALID",
                    "ERROR",
                    str(exc),
                    suggestions=["Repair the project projection before running deeper graph diagnostics."],
                )
            )
        findings.extend(
            _alignment_findings(source_graph, projection, engineering_graph, target)
        )

    if realized is not None:
        findings.extend(
            diagnose_model(
                realized,
                source_root=source_root,
                engineering_graph=engineering_graph,
            )
        )

    structural_errors = any(row["severity"] == "ERROR" for row in findings)
    if target is not None and realized is not None and not structural_errors:
        try:
            result = evaluate_engineering_target(engineering_graph, target, realized)
            if result["status"] != "COMPLETE":
                findings.append(
                    finding(
                        "TARGET_INCOMPLETE",
                        "INFO",
                        f"Consumer {target} target state is {result['status']}.",
                        evidence={
                            "consumer": target,
                            "status": result["status"],
                            "create": [item["capability"] for item in result.get("create", []) or []],
                            "wait": [item["capability"] for item in result.get("wait", []) or []],
                            "pending": [item["capability"] for item in result.get("pending", []) or []],
                        },
                        suggestions=["Treat this as design frontier information, not as a graph defect by itself."],
                    )
                )
        except CoreError as exc:
            findings.append(
                finding(
                    "TARGET_EVALUATION_FAILED",
                    "ERROR",
                    str(exc),
                    suggestions=["Repair structural graph/model errors before interpreting target state."],
                )
            )

    # Deduplicate identical findings caused by both focused checks and canonical validators.
    unique: dict[tuple[str, str, str], dict[str, Any]] = {}
    for row in findings:
        unique.setdefault((row["code"], row["severity"], row["message"]), row)
    rows = sorted(
        unique.values(),
        key=lambda row: (
            SEVERITY_ORDER.get(row["severity"], 99),
            row["code"],
            row["message"],
        ),
    )
    summary = {
        severity: sum(1 for row in rows if row["severity"] == severity)
        for severity in ("ERROR", "WARN", "INFO")
    }
    return {
        "version": 1,
        "kind": "harness-graph-doctor-report",
        "target": target,
        "summary": summary,
        "findings": rows,
        "healthy": summary["ERROR"] == 0,
    }


def _load(path: str | Path) -> dict[str, Any]:
    value = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise SystemExit(f"{path} must contain a mapping")
    return value


def _print_human(report: dict[str, Any]) -> None:
    summary = report["summary"]
    print(
        f"Graph Doctor: {summary['ERROR']} error(s), "
        f"{summary['WARN']} warning(s), {summary['INFO']} info"
    )
    if not report["findings"]:
        print("PASS")
        return
    for row in report["findings"]:
        owner = f" owner={row['owner']}" if row.get("owner") else ""
        print(f"{row['severity']:5} {row['code']}{owner}")
        print(f"      {row['message']}")
        for suggestion in row.get("suggestions", []) or []:
            print(f"      -> {suggestion}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Harness Graph Doctor research prototype")
    parser.add_argument("engineering_graph")
    parser.add_argument("--core-model")
    parser.add_argument("--source-graph")
    parser.add_argument("--projection")
    parser.add_argument("--target")
    parser.add_argument("--source-root")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if (args.source_graph is None) != (args.projection is None):
        raise SystemExit("--source-graph and --projection must be supplied together")
    if args.core_model and args.source_graph:
        raise SystemExit("use either --core-model or --source-graph/--projection")

    report = diagnose_project(
        _load(args.engineering_graph),
        model=_load(args.core_model) if args.core_model else None,
        source_graph=_load(args.source_graph) if args.source_graph else None,
        projection=_load(args.projection) if args.projection else None,
        target=args.target,
        source_root=args.source_root,
    )
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        _print_human(report)
    return 1 if report["summary"]["ERROR"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
