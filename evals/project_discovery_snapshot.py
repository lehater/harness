"""Build label-blinded discovery inputs from a pinned, reviewed project snapshot.

Experimental, read-only, generic Core + Engineering Graph + semantic baseline
adapter. It does not produce expert answers, canonical project data or accepted
semantic judgements. Source acceptance is conservatively bounded by a recorded
baseline review and a canonical Core provider registration.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
from typing import Any

import yaml


class DiscoveryError(ValueError):
    pass


def _required_yaml(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise DiscoveryError(f"missing source: {path}")
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise DiscoveryError(f"invalid project YAML: {path}")
    return value


def _resolve(root: Path, relative: str) -> Path:
    if not isinstance(relative, str) or not relative or "\\" in relative:
        raise DiscoveryError(f"invalid artifact path: {relative!r}")
    parts = PurePosixPath(relative)
    if parts.is_absolute() or ".." in parts.parts:
        raise DiscoveryError("path escapes project snapshot")
    target = (root / relative).resolve()
    if not target.is_relative_to(root.resolve()):
        raise DiscoveryError("resolved path escapes project snapshot")
    return target


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _commit(root: Path, expected: str) -> str:
    if not re.fullmatch(r"[a-f0-9]{40}", expected or ""):
        raise DiscoveryError("pin must be a full 40-character Git commit SHA")
    try:
        actual = subprocess.check_output(
            ["git", "-C", str(root), "rev-parse", "HEAD"], text=True,
            stderr=subprocess.DEVNULL, timeout=10,
        ).strip()
        dirty = subprocess.check_output(
            ["git", "-C", str(root), "status", "--porcelain", "--untracked-files=no"],
            text=True, stderr=subprocess.DEVNULL, timeout=10,
        ).strip()
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
        raise DiscoveryError("cannot confirm immutable Git snapshot") from exc
    if actual != expected or dirty:
        raise DiscoveryError("project commit mismatch or tracked source modifications")
    return actual


def _markdown_claims(text: str) -> list[str]:
    output: list[str] = []
    current_heading = "(document)"
    lines = text.splitlines()
    chunk: list[str] = []

    def flush() -> None:
        if chunk:
            phrase = " ".join(chunk).strip()
            if phrase:
                output.append(f"{current_heading}: {phrase}")
            chunk.clear()

    for line in lines:
        s = line.strip()
        if s.startswith("#"):
            m = re.match(r"^#{1,6}\s+(.+)$", s)
            if m:
                flush()
                current_heading = m.group(1)
                continue
        if not s:
            flush()
        elif s.startswith(("- ", "* ")) or re.match(r"^\d+\. ", s):
            flush()
            output.append(f"{current_heading}: {s}")
        elif s.startswith("**Derived from:**"):
            flush()
            output.append(f"{current_heading}: {s}")
        else:
            chunk.append(s)
    flush()
    return output


def _yaml_claims(value: dict[str, Any]) -> list[str]:
    # Product requirements must come from accepted requirement statements, not
    # all potentially stale YAML metadata or unchecked source references.
    content = value.get("content")
    if isinstance(content, dict) and isinstance(content.get("requirements"), list):
        claims = []
        for item in content["requirements"]:
            if not isinstance(item, dict):
                continue
            if item.get("status") == "ACCEPTED" and isinstance(item.get("statement"), str):
                claims.append(f"{item['id']}: {item['statement'].strip()}")
        for item in content.get("non_goals", []):
            if isinstance(item, str):
                claims.append(f"non_goal: {item.strip()}")
        return claims

    # For non-product YAML artifacts, traverse only descriptive fields, not
    # routing/control metadata, record IDs as context, and bound the output.
    collected: list[str] = []
    def scan(node: Any, prefix: str, depth: int) -> None:
        if depth > 12:
            return
        if isinstance(node, dict):
            ident = node.get("id")
            if isinstance(ident, str):
                prefix = f"{prefix}.{ident}" if prefix else ident
            for key, child in node.items():
                if key in {"id", "path", "depends_on", "provides", "evidence", "source_refs", "status", "revision"}:
                    continue
                scan(child, f"{prefix}.{key}" if prefix else key, depth + 1)
        elif isinstance(node, list):
            for n, child in enumerate(node):
                scan(child, f"{prefix}[{n}]", depth + 1)
        elif isinstance(node, str) and len(node.strip()) >= 18:
            collected.append(f"{prefix}: {node.strip()}")
    scan(value, "", 0)
    return collected


def _heading_scope(text: str, heading: str) -> str:
    lines = text.splitlines()
    needle = re.compile(r"^(#{1,6})\s+" + re.escape(heading) + r"\s*$")
    start = None
    level = 7
    for i, line in enumerate(lines):
        match = needle.match(line.strip())
        if match:
            if start is not None:
                raise DiscoveryError(f"ambiguous heading: {heading}")
            start, level = i, len(match.group(1))
    if start is None:
        raise DiscoveryError(f"scope heading missing: {heading}")
    end = len(lines)
    for j in range(start + 1, len(lines)):
        m = re.match(r"^(#{1,6})\s+", lines[j].strip())
        if m and len(m.group(1)) <= level:
            end = j
            break
    result = "\n".join(lines[start:end]).strip()
    if len(result) < 60:
        raise DiscoveryError(f"scope section too short: {heading}")
    return result



_TRACE_LINE = re.compile(r"\\*\\*Derived from:\\*\\*([^\\n]*)")
_CLAIM_ID = re.compile(r"`(REQ-[A-Z0-9-]+)`")


def _accepted_requirement_inventory(source: dict[str, Any]) -> dict[str, str]:
    """Extract only individually ACCEPTED product statements, with unique IDs."""
    content = source.get("content")
    entries = content.get("requirements") if isinstance(content, dict) else None
    if not isinstance(entries, list) or not entries:
        raise DiscoveryError("product requirements source has no requirements")
    accepted: dict[str, str] = {}
    for entry in entries:
        if not isinstance(entry, dict):
            raise DiscoveryError("malformed product requirement")
        req_id = entry.get("id")
        if not isinstance(req_id, str) or not req_id:
            raise DiscoveryError("product requirement id is invalid")
        if req_id in accepted:
            raise DiscoveryError(f"duplicate accepted product requirement: {req_id}")
        if entry.get("status") != "ACCEPTED":
            continue
        statement = entry.get("statement")
        if not isinstance(statement, str) or not statement.strip():
            raise DiscoveryError(f"empty accepted product statement: {req_id}")
        accepted[req_id] = statement.strip()
    if not accepted:
        raise DiscoveryError("no accepted product requirements")
    return accepted


def _strategic_requirement_refs(section: str) -> list[str]:
    """Only explicit DS section Derived-from links, not lexical similarity."""
    lines = _TRACE_LINE.findall(section)
    if len(lines) != 1:
        raise DiscoveryError("strategic scope needs exactly one explicit Derived from line")
    refs = _CLAIM_ID.findall(lines[0])
    if not refs or len(refs) != len(set(refs)):
        raise DiscoveryError("missing or duplicated strategic requirement references")
    return refs


def generate(
    root: Path, *, sha: str, targets: list[dict[str, Any]],
    max_surface_claims: int = 500,
    formulation: str = "SOURCE_BOUND",
) -> dict[str, Any]:
    if formulation not in {"SOURCE_BOUND", "NEUTRAL_CONTRAST"}:
        raise DiscoveryError("unknown target obligation formulation")
    root = root.resolve()
    _commit(root, sha)
    core = _required_yaml(root / ".harness/core.yaml")
    graph = _required_yaml(root / ".harness/engineering-graph.yaml")
    baseline = _required_yaml(root / ".harness/semantic-baseline.yaml")
    if core.get("questions"):
        raise DiscoveryError("project has open Core Questions: accepted scope may be blocked")
    reviews = {x["capability"]: x for x in baseline.get("reviews", []) if isinstance(x, dict) and isinstance(x.get("capability"), str)}
    authorities = graph.get("authorities")
    if not isinstance(authorities, list):
        raise DiscoveryError("Engineering Graph authorities missing")
    authority_production: dict[str, tuple[dict[str, Any], dict[str, Any]]] = {}
    for authority in authorities:
        for item in authority.get("produces", []):
            cid = item.get("capability")
            if cid in authority_production:
                raise DiscoveryError(f"duplicate Engineering Graph producer {cid}")
            authority_production[cid] = (authority, item)

    artifacts = core.get("artifacts")
    if not isinstance(artifacts, list):
        raise DiscoveryError("missing Core artifacts")
    providers = []
    seen = set()
    for a in artifacts:
        for cid in a.get("provides", []):
            if cid in seen:
                raise DiscoveryError(f"ambiguous Core provider {cid}")
            seen.add(cid)
            if cid not in reviews:
                continue  # Registered is not enough: a review revision is required.
            if cid not in authority_production:
                raise DiscoveryError(f"reviewed Core provider without production contract: {cid}")
            authority, production = authority_production[cid]
            path = a["path"]
            file_path = _resolve(root, path)
            raw = file_path.read_bytes()
            text = raw.decode("utf-8")
            claims = (_markdown_claims(text) if path.endswith(".md")
                      else _yaml_claims(_required_yaml(file_path)))
            if not claims:
                raise DiscoveryError(f"no public semantic claims in {path}")
            if len(claims) > max_surface_claims:
                raise DiscoveryError(f"too many claims in {path}; increase explicit bound")
            providers.append({
                "capability": cid,
                "authority": authority["id"],
                "evidence_status": "ACCEPTED_EVIDENCE",
                "source": path,
                "source_sha256": _sha256(raw),
                "review_revision": reviews[cid]["revision"],
                "semantic_surface": claims,
            })
    if not providers:
        raise DiscoveryError("no accepted, reviewed Core providers")
    cases = []
    for i, item in enumerate(targets):
        cid = item["capability"]
        if cid not in authority_production:
            raise DiscoveryError(f"unknown target: {cid}")
        authority, production = authority_production[cid]
        if cid in seen:
            raise DiscoveryError(f"target {cid} is already in accepted Core; pilot expects planned production")
        scope_source = item["scope_source"]
        source_file = _resolve(root, scope_source)
        accepted_sources = {x["source"] for x in providers}
        if scope_source not in accepted_sources:
            raise DiscoveryError("target scope source is not a reviewed, Core-registered artifact")
        scope_text = source_file.read_text(encoding="utf-8")
        headings = item["scope_headings"]
        if not isinstance(headings, list) or not headings:
            raise DiscoveryError("target scope heading selectors are missing")
        obligations = [{
            "id": f"source-section-{n+1}",
            "description": (
                f"Produce {production.get('knowledge_kind')} under Authority "
                f"{authority['id']} ({authority.get('responsibility', '').strip()}). "
                f"Preserve this accepted source scope without inventing technical "
                f"details or narrowing its meaning: {_heading_scope(scope_text, heading)}"
            ),
            "source": {
                "capability": next(p["capability"] for p in providers if p["source"] == scope_source),
                "path": scope_source, "heading": heading,
            },
        } for n, heading in enumerate(headings)]
        strategic_source = item.get("strategic_scope_source")
        strategic_headings = item.get("strategic_scope_headings")
        product_source = item.get("product_requirements_source")
        if (
            not isinstance(strategic_source, str)
            or not isinstance(strategic_headings, list) or not strategic_headings
            or not isinstance(product_source, str)
        ):
            raise DiscoveryError("scope coverage requires strategic sections and product requirements")
        if strategic_source not in accepted_sources or product_source not in accepted_sources:
            raise DiscoveryError("strategic/product coverage source is not accepted and reviewed in Core")
        strategic_path = _resolve(root, strategic_source)
        strategy_text = strategic_path.read_text(encoding="utf-8")
        strategic_refs: list[str] = []
        for n, heading in enumerate(strategic_headings):
            if not isinstance(heading, str) or not heading:
                raise DiscoveryError("invalid strategic scope heading")
            section = _heading_scope(strategy_text, heading)
            strategic_refs.extend(_strategic_requirement_refs(section))
            obligations.append({
                "id": f"strategic-section-{n+1}",
                "description": (
                    "Preserve this accepted strategic responsibility in the "
                    f"tactical {production.get('knowledge_kind')} without "
                    "re-owning application behavior or implementation: "
                    + section
                ),
                "source": {
                    "capability": next(p["capability"] for p in providers if p["source"] == strategic_source),
                    "path": strategic_source, "heading": heading,
                },
            })
        if len(strategic_refs) != len(set(strategic_refs)):
            raise DiscoveryError("duplicate traced requirement across strategic sections")
        accepted_requirements = _accepted_requirement_inventory(_required_yaml(_resolve(root, product_source)))
        missing_refs = sorted(set(strategic_refs) - set(accepted_requirements))
        if missing_refs:
            raise DiscoveryError("strategic section references missing accepted requirements: " + ", ".join(missing_refs))
        product_provider = next(p for p in providers if p["source"] == product_source)
        product_claim_index: dict[str, int] = {}
        for req_id in accepted_requirements:
            matches = [
                index for index, claim in enumerate(product_provider["semantic_surface"])
                if claim.startswith(req_id + ": ")
            ]
            if len(matches) != 1:
                raise DiscoveryError(f"missing/ambiguous public product semantic claim: {req_id}")
            product_claim_index[req_id] = matches[0]
        # These candidates are accepted source statements, NOT assumed tactical
        # requirements or model-produced direct edges. The target must assess
        # whether each is materially applicable before completeness is claimed.
        upstream_constraint_candidates = [
            {
                "requirement_id": req_id,
                "provider": product_provider["capability"],
                "claim_index": product_claim_index[req_id],
                "statement": statement,
                "traceability": (
                    "EXPLICIT_STRATEGIC_DERIVATION"
                    if req_id in strategic_refs else "UNADJUDICATED_ACCEPTED_PRODUCT_REQUIREMENT"
                ),
                "applicability": "REQUIRES_SEMANTIC_REVIEW",
            }
            for req_id, statement in accepted_requirements.items()
        ]
        if formulation == "NEUTRAL_CONTRAST":
            # Deliberate controlled ablation: replace upstream-authored target
            # obligation text with a short operator-authored target-output
            # paraphrase. This avoids rewarding the model for re-citing an
            # upstream statement duplicated in its own target, but the
            # paraphrase is NOT an accepted project decision or ground truth.
            neutral = item.get("neutral_output_obligations")
            if not isinstance(neutral, list) or not neutral:
                raise DiscoveryError("neutral contrast needs operator-authored target obligations")
            clean = []
            observed_ids: set[str] = set()
            for ob in neutral:
                if not isinstance(ob, dict):
                    raise DiscoveryError("invalid contrast obligation")
                ob_id, description = ob.get("id"), ob.get("description")
                if (not isinstance(ob_id, str) or not ob_id or ob_id in observed_ids
                    or not isinstance(description, str) or len(description.strip()) < 45):
                    raise DiscoveryError("missing, duplicate, or overly short neutral contrast obligation")
                observed_ids.add(ob_id)
                if any(p["capability"] in description for p in providers):
                    raise DiscoveryError("contrast obligation may not include provider CapabilityId")
                if any(
                    description.strip() in source_ob["description"]
                    or source_ob["description"] in description.strip()
                    for source_ob in obligations
                ):
                    raise DiscoveryError("neutral contrast duplicates source-bound obligation")
                clean.append({"id": ob_id, "description": description.strip()})
            obligations = clean
        candidates = [dict(p) for p in providers if p["capability"] != cid]
        # No existing target requires, lifecycle prerequisites, or oracle are
        # passed. Every accepted reviewed provider is visible, even when the
        # canonical Engineering Graph omits a direct target edge.
        cases.append({
            "id": f"SNAP-{i+1:02d}",
            "archetype": "actual-project-git-snapshot",
            "source_snapshot": f"{item.get('repository', 'local-project')}@{sha}",
            "target": {
                "capability": cid, "authority": authority["id"],
                "knowledge_kind": production.get("knowledge_kind"),
                "output_obligations": obligations,
                "upstream_constraint_candidates": upstream_constraint_candidates,
            },
            "provider_catalog": candidates,
        })
    return {
        "version": 1,
        "kind": "harness-dependency-resolution-calibration-inputs",
        "status": "real-project-discovery-readonly",
        "evidence_contract": "source-grounded-v1",
        "source_snapshot": sha,
        "discovery_method": "reviewed-core-artifacts-and-explicit-strategic-product-traceability",
        "target_formulation": formulation,
        "target_formulation_authority": (
            "ACCEPTED_SOURCE_EXCERPTS" if formulation == "SOURCE_BOUND"
            else "EXPERIMENTAL_OPERATOR_PARAPHRASE_NOT_ACCEPTED"
        ),
        "coverage_contract": "source-traceability-v1",
        # All accepted Product Capability statements are inventoried, including
        # those not traced from DS-01 / DS-02. This is an applicability inventory,
        # not independently reviewed target-output obligation completeness.
        # The operator selected Model Context and traced Domain Strategy
        # headings, and all accepted Product Capability statements are supplied
        # as applicability candidates, not guaranteed target obligations.
        # Their semantic applicability is still unadjudicated, so completeness
        # remains false. Existing requires are not exposed to the model.
        "target_obligation_coverage": {
            "status": "PARTIAL_BY_CONSTRUCTION",
            "reason": "PENDING_CROSS_AUTHORITY_SEMANTIC_APPLICABILITY_ADJUDICATION",
            "complete_upstream_obligation_coverage_established": False,
        },
        "cases": cases,
    }


def main() -> int:
    p = argparse.ArgumentParser(description="Build blind Discovery Context from pinned project snapshot")
    p.add_argument("--project-root", type=Path, required=True)
    p.add_argument("--commit", required=True)
    p.add_argument("--config", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--formulation", choices=("SOURCE_BOUND", "NEUTRAL_CONTRAST"),
                   default="SOURCE_BOUND")
    args = p.parse_args()
    try:
        config = _required_yaml(args.config)
        targets = config.get("targets")
        if not isinstance(targets, list) or not targets:
            raise DiscoveryError("configuration lacks targets")
        result = generate(args.project_root, sha=args.commit, targets=targets,
                          formulation=args.formulation)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(yaml.safe_dump(result, sort_keys=False, allow_unicode=True), encoding="utf-8")
        print(json.dumps({
            "status": "GENERATED", "source_snapshot": result["source_snapshot"],
            "cases": len(result["cases"]),
            "provider_counts": [len(x["provider_catalog"]) for x in result["cases"]],
            "obligation_counts": [len(x["target"]["output_obligations"]) for x in result["cases"]],
            "inputs_sha256": _sha256(args.output.read_bytes()),
        }))
        return 0
    except (DiscoveryError, KeyError, ValueError, OSError) as exc:
        print(json.dumps({"status": "INVALID", "error": str(exc)}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
