"""Compare a proposed target contract revision to its original unaccepted draft.

This is a conservation/provenance check, NOT a semantic review, output
contract adoption mechanism or permission to edit project graph topology.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from evals.project_discovery_snapshot import DiscoveryError, _required_yaml

ACTIONS = {"REFINE_OUTPUT", "RECAST_AS_GOVERNING_CONSTRAINT"}
FORBIDDEN_MUTATION_KEYS = {"requires", "depends_on", "accepted_requires", "graph_updates"}


def validate_revision(v1: dict[str, Any], v2: dict[str, Any]) -> dict[str, Any]:
    if (v1.get("kind") != "harness-cdr-target-output-contract-candidates"
        or v1.get("status") != "OPERATOR_DRAFT_NOT_ACCEPTED"
        or v1.get("no_automatic_writeback") is not True):
        raise DiscoveryError("source proposal is not an unaccepted target draft")
    if (v2.get("kind") != "harness-cdr-tactical-target-revision-proposal"
        or v2.get("version") != 2
        or v2.get("status") != "OPERATOR_DRAFT_NOT_ACCEPTED"
        or v2.get("independent_review_performed") is not False
        or v2.get("semantic_completeness_established") is not False
        or v2.get("automatic_writeback_allowed") is not False):
        raise DiscoveryError("revision cannot assert Authority acceptance or semantic completeness")
    if (v1.get("source_commit") != v2.get("source_commit")
        or v1.get("source_project") != v2.get("source_project")
        or v1.get("owning_authority") != v2.get("authority_for_future_review")):
        raise DiscoveryError("revision must preserve project source and reviewing Authority")

    def no_graph_mutations(o: Any) -> None:
        if isinstance(o, dict):
            if set(o) & FORBIDDEN_MUTATION_KEYS:
                raise DiscoveryError("revision cannot contain graph dependency edits")
            for child in o.values():
                no_graph_mutations(child)
        elif isinstance(o, list):
            for child in o:
                no_graph_mutations(child)
    no_graph_mutations(v2)

    old_targets = v1.get("target_contracts")
    new_targets = v2.get("targets")
    if not isinstance(old_targets, list) or not isinstance(new_targets, list):
        raise DiscoveryError("target records required")
    olds: dict[str, dict[str, Any]] = {}
    for old in old_targets:
        cid = old.get("target_capability")
        if (not isinstance(cid, str) or cid in olds
            or old.get("target_contract_status") != "NEEDS_INDEPENDENT_AUTHORITY_REVIEW"):
            raise DiscoveryError("duplicate or accepted source target")
        ob_by_id: dict[str, dict[str, Any]] = {}
        for ob in old.get("candidate_obligations", []):
            oid = ob.get("id")
            if (not isinstance(oid, str) or oid in ob_by_id
                or ob.get("status") != "CANDIDATE_NOT_ACCEPTED"):
                raise DiscoveryError("invalid source draft obligation")
            ob_by_id[oid] = ob
        if not ob_by_id:
            raise DiscoveryError("empty original target obligations")
        olds[cid] = ob_by_id
    seen_targets = set()
    results = []
    for target in new_targets:
        cid = target.get("target_capability")
        if not isinstance(cid, str) or cid in seen_targets or cid not in olds:
            raise DiscoveryError("revision has unknown or duplicate target")
        seen_targets.add(cid)
        if target.get("status") != "NEEDS_INDEPENDENT_AUTHORITY_REVIEW":
            raise DiscoveryError("revision has prematurely accepted target")
        outputs = target.get("candidate_outputs")
        constraints = target.get("candidate_constraints")
        if not isinstance(outputs, list) or not outputs or not isinstance(constraints, list):
            raise DiscoveryError("outputs and governing constraints must be explicit")
        if not isinstance(target.get("additional_review_questions"), list) or not target["additional_review_questions"]:
            raise DiscoveryError("unresolved target ownership questions missing")
        ids = set()
        lineage = set()
        count_by_action = {"REFINE_OUTPUT": 0, "RECAST_AS_GOVERNING_CONSTRAINT": 0}
        output_ids = {x.get("id") for x in outputs}
        if len(output_ids) != len(outputs) or not all(isinstance(x, str) and x for x in output_ids):
            raise DiscoveryError("duplicate/invalid revised output ID")
        for kind, items, expected_action in (
            ("OUTPUT", outputs, "REFINE_OUTPUT"),
            ("GOVERNING_CONSTRAINT", constraints, "RECAST_AS_GOVERNING_CONSTRAINT"),
        ):
            for item in items:
                iid, old_id = item.get("id"), item.get("supersedes_v1")
                if (not isinstance(iid, str) or iid in ids
                    or old_id not in olds[cid] or old_id in lineage):
                    raise DiscoveryError("obligation lineage is incomplete, duplicated or unknown")
                ids.add(iid)
                lineage.add(old_id)
                if iid != old_id:
                    raise DiscoveryError("draft revisions preserve stable obligation identifiers")
                if (item.get("status") != "CANDIDATE_NOT_ACCEPTED"
                    or item.get("proposal") != expected_action
                    or item["proposal"] not in ACTIONS):
                    raise DiscoveryError("proposed action or status is invalid")
                text = item.get("text")
                if (not isinstance(text, str) or len(text.strip()) < 80
                    or text.strip() == olds[cid][old_id].get("description", "").strip()):
                    raise DiscoveryError("revised formulation missing or unchanged")
                for field in ("review_rationale", "unresolved_question"):
                    val = item.get(field)
                    if not isinstance(val, str) or len(val.strip()) < 40:
                        raise DiscoveryError("substantive review rationale and open question required")
                old_sources = {
                    (x.get("path"), x.get("heading"))
                    for x in olds[cid][old_id].get("upstream_scope", [])
                }
                source_refs = item.get("source_sections")
                if not isinstance(source_refs, list) or not source_refs:
                    raise DiscoveryError("revised source provenance omitted")
                new_sources = set()
                for ref in source_refs:
                    if not isinstance(ref, dict) or not all(
                        isinstance(ref.get(p), str) and ref[p] for p in ("path", "heading")
                    ):
                        raise DiscoveryError("invalid revisited source section")
                    new_sources.add((ref["path"], ref["heading"]))
                if not old_sources.issubset(new_sources):
                    raise DiscoveryError("revision discards v1 source section evidence")
                if kind == "GOVERNING_CONSTRAINT":
                    applies = item.get("applies_to_outputs")
                    if (not isinstance(applies, list) or not applies
                        or len(applies) != len(set(applies))
                        or not set(applies).issubset(output_ids)):
                        raise DiscoveryError("governing constraint must name existing local outputs")
                elif "applies_to_outputs" in item:
                    raise DiscoveryError("positive output cannot masquerade as governing constraint")
                count_by_action[expected_action] += 1
        if lineage != set(olds[cid]):
            raise DiscoveryError("revision silently drops a prior draft obligation")
        results.append({
            "target_capability": cid,
            "preserved_v1_obligation_ids": sorted(lineage),
            "candidate_output_ids": sorted(output_ids),
            "governing_constraint_ids": sorted(set(ids) - output_ids),
            "action_counts": count_by_action,
            "independent_authority_review_performed": False,
            "target_contract_accepted": False,
        })
    if seen_targets != set(olds):
        raise DiscoveryError("revision omits an entire original target")
    return {
        "kind": "harness-cdr-target-revision-conservation-review",
        "version": 1,
        "source_snapshot": v1["source_commit"],
        "status": "REVISION_PROPOSAL_REQUIRES_AUTHORITY_REVIEW",
        "targets": results,
        "original_obligation_count": sum(len(x) for x in olds.values()),
        "candidate_output_count": sum(len(x["candidate_output_ids"]) for x in results),
        "candidate_constraint_count": sum(len(x["governing_constraint_ids"]) for x in results),
        "original_meaning_independently_verified": False,
        "revised_meaning_independently_verified": False,
        "independent_authority_review_performed": False,
        "semantic_completeness_established": False,
        "graph_mutation_authorized": False,
        "automatic_writeback_allowed": False,
    }


def main() -> int:
    p=argparse.ArgumentParser(description="Non-authorizing comparison of PREP target draft obligations")
    p.add_argument("--source-draft",type=Path,required=True)
    p.add_argument("--revision",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    try:
        report=validate_revision(_required_yaml(args.source_draft),_required_yaml(args.revision))
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        print(json.dumps({
            "status":report["status"],
            "original":report["original_obligation_count"],
            "revised_outputs":report["candidate_output_count"],
            "governing_constraints":report["candidate_constraint_count"],
            "independent_authority_review_performed":False,
        },ensure_ascii=False))
        return 0
    except (DiscoveryError,KeyError,TypeError,OSError,ValueError) as exc:
        print(json.dumps({"status":"INVALID","error":str(exc)},ensure_ascii=False))
        return 2


if __name__=="__main__":
    raise SystemExit(main())
