"""Source-anchored candidate provider public surfaces for blinded CDR research.

Selection is deliberately operator-authored and explicitly incomplete. It
does not infer ownership, acceptance, directness or provider sufficiency.
Never consult an Engineering Graph or declared requires in Phase A.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from evals.project_discovery_snapshot import DiscoveryError, _required_yaml, _resolve, _sha256

KIND = "harness-cdr-research-owned-surface-selectors"
MODELS = {"markdown-sections", "accepted-product-requirements", "yaml-fields"}


def load_selectors(path: Path, *, pin: str, target: str,
                   expected: tuple[str, ...]) -> tuple[dict[str, dict[str, Any]], str]:
    raw = path.read_bytes()
    doc = _required_yaml(path)
    if (doc.get("version") != 1 or doc.get("kind") != KIND
            or doc.get("status") != "UNACCEPTED_OPERATOR_RESEARCH_SELECTION"
            or doc.get("source_commit") != pin
            or doc.get("target_capability") != target):
        raise DiscoveryError("unbound or incorrectly accepted surface selector manifest")
    entries = doc.get("providers")
    if not isinstance(entries, list) or len(entries) != len(expected):
        raise DiscoveryError("selector manifest missing or duplicating providers")
    found = {}
    for row in entries:
        if not isinstance(row, dict) or row.get("mode") not in MODELS:
            raise DiscoveryError("invalid source selection")
        cid = row.get("capability")
        if cid in found or cid not in expected:
            raise DiscoveryError("unknown/duplicated source selector capability")
        mode = row["mode"]
        allowed = {"capability", "mode"}
        if mode == "markdown-sections":
            allowed.add("headings")
        elif mode == "yaml-fields":
            allowed.add("fields")
        if set(row) != allowed:
            raise DiscoveryError("source selector has unsupported fields")
        if mode in {"markdown-sections", "yaml-fields"}:
            key = "headings" if mode == "markdown-sections" else "fields"
            vals = row[key]
            if (not isinstance(vals, list) or not 1 <= len(vals) <= 12
                    or any(not isinstance(x, str) or not x.strip() for x in vals)
                    or len(vals) != len(set(vals))):
                raise DiscoveryError("source selectors must be unique explicit labels")
        found[cid] = row
    if set(found) != set(expected):
        raise DiscoveryError("selector catalog differs from expected provider set")
    return found, _sha256(raw)


def _markdown_section(doc: str, label: str) -> str:
    lines = doc.splitlines()
    headings = []
    for i, line in enumerate(lines):
        m = re.fullmatch(r"(#{2,4})[ \t]+(.+?)[ \t]*", line)
        if m and m.group(2).strip() == label:
            headings.append((i, len(m.group(1))))
    if len(headings) != 1:
        raise DiscoveryError(f"missing/ambiguous selected Markdown heading {label!r}")
    pos, level = headings[0]
    end = len(lines)
    fenced = False
    for j in range(pos + 1, len(lines)):
        stripped = lines[j].strip()
        if stripped.startswith((chr(96) * 3, "~~~")):
            fenced = not fenced
        if not fenced:
            m = re.match(r"^(#{1,6})[ \t]+", lines[j])
            if m and len(m.group(1)) <= level:
                end = j
                break
    section = "\n".join(lines[pos + 1:end]).strip()
    if len(section) < 55 or len(section) > 2600:
        raise DiscoveryError(f"selected section is empty or too large: {label!r}")
    return section


def selected_surface(root: Path, artifact: dict[str, Any],
                     selector: dict[str, Any]) -> tuple[list[str], dict[str, Any]]:
    source = artifact["path"]
    path = _resolve(root, source)
    raw = path.read_bytes()
    mode = selector["mode"]
    if mode == "markdown-sections":
        if path.suffix != ".md":
            raise DiscoveryError("section selector requires a Markdown source")
        doc = raw.decode("utf-8")
        chunks = [f"RESEARCH-SELECTED SECTION [{heading}]: "
                  + _markdown_section(doc, heading)
                  for heading in selector["headings"]]
    else:
        if path.suffix not in (".yaml", ".yml"):
            raise DiscoveryError("structured selectors require YAML source")
        doc = _required_yaml(path)
        if mode == "accepted-product-requirements":
            content = doc.get("content")
            values = content.get("requirements") if isinstance(content, dict) else None
            if not isinstance(values, list) or not values:
                raise DiscoveryError("no structured product requirements")
            seen = set()
            chunks = []
            for entry in values:
                if not isinstance(entry, dict) or entry.get("status") != "ACCEPTED":
                    raise DiscoveryError("research selector cannot silently omit draft requirements")
                cid, statement = entry.get("id"), entry.get("statement")
                if (not isinstance(cid, str) or cid in seen or not cid
                        or not isinstance(statement, str) or len(statement.strip()) < 30):
                    raise DiscoveryError("invalid/duplicated accepted product statement")
                seen.add(cid)
                chunks.append(f"ACCEPTED PRODUCT REQUIREMENT [{cid}]: {statement.strip()}")
        else:
            chunks = []
            for field in selector["fields"]:
                value = doc.get(field)
                if isinstance(value, str) and len(value.strip()) > 35:
                    chunks.append(f"YAML SOURCE FIELD [{field}]: {value.strip()}")
                elif (isinstance(value, list) and value
                      and all(isinstance(v, str) and len(v.strip()) > 20
                              for v in value)):
                    chunks.extend(f"YAML SOURCE FIELD [{field}/{i}]: {v.strip()}"
                                  for i, v in enumerate(value))
                else:
                    raise DiscoveryError("selected YAML field is missing or non-substantive")
    if not chunks or any(len(c.strip()) < 40 for c in chunks):
        raise DiscoveryError("empty/non-substantive provider contract selection")
    if len(chunks) > 50:
        raise DiscoveryError("selected provider corpus requires explicit review")
    return chunks, {
        "path": source, "sha256": _sha256(raw),
        "claim_count_in_source": "NOT_EXHAUSTIVELY_INVENTORIED",
        "claim_count_supplied": len(chunks),
        "public_surface_truncated": False,
        "selection_scope_partial": True,
        "selection_mode": mode,
        "claim_role": "RESEARCH_CANDIDATE_NOT_AUTHORITY_APPROVED",
        "independent_ownership_review_verified": False,
        "all_source_contracts_included": False,
    }
