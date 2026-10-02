#!/usr/bin/env python3
"""Deterministic source-set coverage relative to an explicit acquisition contract."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml

from harness.project_model.core import CoreError


CHANNEL_STATES = {"COMPLETE", "QUESTION"}


__all__ = [
    "annotations",
    "argparse",
    "json",
    "Path",
    "Any",
    "yaml",
    "CoreError",
    "CHANNEL_STATES",
    "evaluate_source_set",
    "load_yaml",
    "main",
]


def _text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise CoreError(f"{label} must be a non-empty string")
    return value.strip()


def _non_negative_int(value: Any, label: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise CoreError(f"{label} must be a non-negative integer")
    return value


def evaluate_source_set(
    *,
    contract: dict[str, Any],
    inventory: dict[str, Any],
) -> dict[str, Any]:
    """Evaluate source-set closure relative to a declared acquisition scope.

    This validator deliberately does not prove that the acquisition contract is
    globally sufficient. It proves only that every contract-declared evidence
    channel was explicitly reviewed and satisfies its minimum item count.
    """
    if contract.get("version") != 1:
        raise CoreError("source-set contract version must be 1")
    if contract.get("kind") != "harness-source-set-contract":
        raise CoreError("unexpected source-set contract kind")
    contract_id = _text(contract.get("id"), "source-set contract id")
    _text(contract.get("scope"), "source-set contract scope")

    requirements = contract.get("requirements")
    if not isinstance(requirements, list) or not requirements:
        raise CoreError("source-set contract requirements must be a non-empty list")

    required: dict[str, int] = {}
    for item in requirements:
        if not isinstance(item, dict):
            raise CoreError("source-set requirement must be a mapping")
        channel_id = _text(item.get("id"), "requirement.id")
        if channel_id in required:
            raise CoreError(f"duplicate source-set requirement id: {channel_id}")
        required[channel_id] = _non_negative_int(
            item.get("min_items", 1),
            f"{channel_id}.min_items",
        )

    if inventory.get("version") != 1:
        raise CoreError("source-set inventory version must be 1")
    if inventory.get("kind") != "harness-source-set":
        raise CoreError("unexpected source-set inventory kind")
    inventory_id = _text(inventory.get("id"), "source-set inventory id")
    inventory_contract = _text(inventory.get("contract_id"), "contract_id")

    findings: list[dict[str, Any]] = []
    if inventory_contract != contract_id:
        findings.append(
            {
                "code": "SOURCE_SET_CONTRACT_MISMATCH",
                "expected": contract_id,
                "actual": inventory_contract,
            }
        )

    channels = inventory.get("channels")
    if not isinstance(channels, list):
        raise CoreError("source-set inventory channels must be a list")

    seen_channels: dict[str, dict[str, Any]] = {}
    seen_refs: set[str] = set()
    duplicate_refs: list[str] = []

    for channel in channels:
        if not isinstance(channel, dict):
            raise CoreError("source-set channel must be a mapping")
        channel_id = _text(channel.get("id"), "channel.id")
        if channel_id in seen_channels:
            raise CoreError(f"duplicate source-set channel id: {channel_id}")

        state = _text(channel.get("state"), f"{channel_id}.state")
        if state not in CHANNEL_STATES:
            raise CoreError(
                f"{channel_id}.state must be one of {sorted(CHANNEL_STATES)}"
            )

        items = channel.get("items", [])
        if not isinstance(items, list):
            raise CoreError(f"{channel_id}.items must be a list")

        normalized_items: list[str] = []
        for item in items:
            if not isinstance(item, dict):
                raise CoreError(f"{channel_id}: source item must be a mapping")
            source_ref = _text(item.get("source_ref"), f"{channel_id}.source_ref")
            normalized_items.append(source_ref)
            if source_ref in seen_refs:
                duplicate_refs.append(source_ref)
            seen_refs.add(source_ref)

        seen_channels[channel_id] = {
            "state": state,
            "items": normalized_items,
        }

    if duplicate_refs:
        findings.append(
            {
                "code": "DUPLICATE_SOURCE_SET_ITEM",
                "source_refs": sorted(set(duplicate_refs)),
            }
        )

    channel_results: list[dict[str, Any]] = []
    for channel_id, min_items in required.items():
        channel = seen_channels.get(channel_id)
        if channel is None:
            findings.append(
                {
                    "code": "SOURCE_CHANNEL_MISSING",
                    "channel": channel_id,
                    "min_items": min_items,
                }
            )
            channel_results.append(
                {
                    "id": channel_id,
                    "state": "MISSING",
                    "min_items": min_items,
                    "item_count": 0,
                    "satisfied": False,
                }
            )
            continue

        state = channel["state"]
        item_count = len(channel["items"])
        satisfied = state == "COMPLETE" and item_count >= min_items

        if state == "QUESTION":
            findings.append(
                {
                    "code": "SOURCE_CHANNEL_QUESTION",
                    "channel": channel_id,
                }
            )
        if item_count < min_items:
            findings.append(
                {
                    "code": "SOURCE_CHANNEL_UNDERSATISFIED",
                    "channel": channel_id,
                    "min_items": min_items,
                    "item_count": item_count,
                }
            )

        channel_results.append(
            {
                "id": channel_id,
                "state": state,
                "min_items": min_items,
                "item_count": item_count,
                "satisfied": satisfied,
            }
        )

    accepted = not findings
    return {
        "version": 1,
        "kind": "harness-source-set-evaluation",
        "status": "ACCEPTED" if accepted else "REJECTED",
        "contract_id": contract_id,
        "inventory_id": inventory_id,
        "required_channel_count": len(required),
        "reviewed_channel_count": len(
            [item for item in channel_results if item["state"] != "MISSING"]
        ),
        "channels": channel_results,
        "extra_channels": sorted(set(seen_channels) - set(required)),
        "findings": findings,
    }


def load_yaml(path: str | Path) -> dict[str, Any]:
    value = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise CoreError(f"{path} must contain a mapping")
    return value


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate source-set coverage against an acquisition contract"
    )
    parser.add_argument("contract")
    parser.add_argument("inventory")
    args = parser.parse_args()

    result = evaluate_source_set(
        contract=load_yaml(args.contract),
        inventory=load_yaml(args.inventory),
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "ACCEPTED" else 2


if __name__ == "__main__":
    raise SystemExit(main())
