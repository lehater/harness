"""Read-only CDR corpus preparation and dependency inventory for Reference Model v0.

Reference templates are research proposals, NOT project-accepted capability
contracts. No asserted edge is an oracle of semantic directness.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import deque
from pathlib import Path
from typing import Any

from harness.reference_model.reference_materializer import (
    load_yaml, validate_reference_model,
)
from harness.project_model.core import CoreError

DEFAULT_MODEL = "spec/research/reference-engineering-model-v0.yaml"
DEFAULT_AUTHORITIES = "catalogs/software-authorities-v0.yaml"
DEFAULT_PROOF = "spec/engineering-coverage/semantic-proof-contract-v1.yaml"


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _corpus(model: dict[str, Any], authorities: dict[str, Any],
            proof: dict[str, Any]) -> list[dict[str, Any]]:
    problems = validate_reference_model(model, authorities, proof)
    if problems:
        raise CoreError("invalid reference model: " +
                        ", ".join(str(x.get("code")) for x in problems[:12]))
    templates = model["templates"]
    if len(templates) > 5000:
        raise CoreError("reference corpus exceeds explicit 5000-template bound")
    return templates


def _blind_template(t: dict[str, Any]) -> dict[str, Any]:
    # Only the public output description and context. Crucially NO "requires",
    # other template dependencies, existing edges, or independent oracle labels.
    return {
        "id": t["id"],
        "authority_type": t["authority_type"],
        "knowledge_kind": t.get("knowledge_kind"),
        "primary_claims": list(t.get("primary_claims", []) or []),
        "claim_surface": list(t.get("claim_surface", []) or []),
        "applicability": t.get("applicability", {}),
        "scope": t.get("scope", {}),
        "own_output_contract_complete": False,
        "research_template_not_accepted_project_contract": True,
    }


def _path_from(
    edges: dict[str, list[dict[str, Any]]],
    source: str, destination: str,
) -> list[dict[str, Any]] | None:
    """One shortest possible path, ignoring predicate satisfiability."""
    queue = deque([(source, [source], [])])
    seen = {source}
    while queue:
        node, nodes, conditions = queue.popleft()
        if node == destination:
            return [{
                "templates": nodes,
                "conditional_hops": conditions,
                "all_conditions_satisfiable_proven": False,
            }]
        for relation in edges.get(node, []):
            nxt = relation["template"]
            if nxt in seen:
                continue
            seen.add(nxt)
            condition = relation.get("when")
            queue.append((
                nxt, nodes + [nxt],
                conditions + ([{"from": node, "to": nxt, "when": condition}]
                              if condition is not None else []),
            ))
    return None


def prepare(model: dict[str, Any], authorities: dict[str, Any],
            proof: dict[str, Any], fingerprints: dict[str, str]) -> dict[str, Any]:
    templates = _corpus(model, authorities, proof)
    return {
        "kind": "harness-cdr-reference-blind-corpus-v1",
        "status": "EXPERIMENTAL_SOURCE_ONLY_NOT_ACCEPTED",
        "source_fingerprints": fingerprints,
        "templates": [_blind_template(t) for t in templates],
        "target_output_obligation_completeness_proven": False,
        "semantic_directness_verified": False,
        "automatic_writeback_allowed": False,
    }


def audit(model: dict[str, Any], authorities: dict[str, Any],
          proof: dict[str, Any], fingerprints: dict[str, str]) -> dict[str, Any]:
    templates = _corpus(model, authorities, proof)
    by_id = {t["id"]: t for t in templates}
    edges = {t["id"]: t.get("requires", []) or [] for t in templates}
    rows: list[dict[str, Any]] = []
    for target in templates:
        deps = edges[target["id"]]
        for direct in deps:
            supplier = direct["template"]
            paths = []
            for intermediary in deps:
                mid = intermediary["template"]
                if mid == supplier:
                    continue
                segment = _path_from(edges, mid, supplier)
                if segment is None:
                    continue
                path = segment[0]
                first_condition = intermediary.get("when")
                hops = ([{"from": target["id"], "to": mid, "when": first_condition}]
                        if first_condition is not None else [])
                paths.append({
                    "templates": [target["id"]] + path["templates"],
                    "conditional_hops": hops + path["conditional_hops"],
                    "all_conditions_satisfiable_proven": False,
                    "semantic_mediation_proven": False,
                })
            rows.append({
                "target": target["id"],
                "provider": supplier,
                "direct_condition": direct.get("when"),
                "target_output_claims": list(target.get("primary_claims", []) or []),
                "target_claim_surface": list(target.get("claim_surface", []) or []),
                "provider_claim_surface": list(by_id[supplier].get("claim_surface", []) or []),
                "alternative_structural_paths": paths,
                "structural_transitive_flag": bool(paths),
                "independent_directness": "UNDETERMINED",
                "authority_decision": "NOT_ACCEPTED",
                "review_questions": [
                    "Which independently accepted target output consumes this supplier?",
                    "Which accepted supplier rule is materially consumed?",
                    "Do existing immediate contracts fully mediate that rule?",
                    "Can supplier semantics change while intermediates stay unchanged and still force target reconsideration?",
                    "Which target Authority has accepted the decision at which revisions?",
                ],
            })
    missing_primary = sorted(t["id"] for t in templates
                             if not t.get("primary_claims"))
    return {
        "kind": "harness-cdr-reference-dependency-audit-v1",
        "status": "STRUCTURAL_CANDIDATES_AWAIT_SEMANTIC_REVIEW",
        "source_fingerprints": fingerprints,
        "template_count": len(templates),
        "direct_edge_count": len(rows),
        "conditional_edge_count": sum(row["direct_condition"] is not None for row in rows),
        "structural_transitive_flag_count": sum(row["structural_transitive_flag"] for row in rows),
        "targets_without_explicit_primary_claims": missing_primary,
        "edge_review_packets": rows,
        "missing_direct_edges_exhaustively_found": False,
        "structural_transitive_flag_proves_redundancy": False,
        "target_output_obligation_completeness_proven": False,
        "independent_directness_verified": False,
        "graph_edit_authorized": False,
        "automatic_writeback_allowed": False,
    }


def run(*, phase: str, model_path: Path, authorities_path: Path,
        proof_path: Path) -> dict[str, Any]:
    sources = {"model": model_path, "authorities": authorities_path,
               "proof": proof_path}
    fingerprints = {name: _digest(path) for name, path in sources.items()}
    docs = {name: load_yaml(path) for name, path in sources.items()}
    if phase == "prepare":
        return prepare(docs["model"], docs["authorities"], docs["proof"], fingerprints)
    if phase == "audit":
        return audit(docs["model"], docs["authorities"], docs["proof"], fingerprints)
    raise CoreError("unknown reference audit phase")


def main() -> int:
    parser = argparse.ArgumentParser(description="Noncanonical read-only CDR reference-template audit")
    parser.add_argument("phase", choices=("prepare", "audit"))
    parser.add_argument("--model", type=Path, default=Path(DEFAULT_MODEL))
    parser.add_argument("--authorities", type=Path, default=Path(DEFAULT_AUTHORITIES))
    parser.add_argument("--proof", type=Path, default=Path(DEFAULT_PROOF))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        result = run(phase=args.phase, model_path=args.model,
                     authorities_path=args.authorities, proof_path=args.proof)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        print(json.dumps({
            "status": result["status"],
            "templates": result.get("template_count", len(result.get("templates", []))),
            "flagged_edges": result.get("structural_transitive_flag_count", 0),
            "automatic_writeback_allowed": False,
        }))
        return 0
    except (CoreError, ValueError, TypeError, KeyError, OSError) as exc:
        print(json.dumps({"status": "INVALID", "error": str(exc)}, ensure_ascii=False))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
