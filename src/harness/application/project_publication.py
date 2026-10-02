#!/usr/bin/env python3
"""Atomic publication boundary for coordinated Harness project state."""
from __future__ import annotations

import copy
import hashlib
import json
import os
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Any

import yaml

from harness.assurance.capability_lifecycle import lifecycle_index, validate_projection
from .decision_pipeline import decision_failure_index
from harness.project_model.engineering_graph import validate_realization
from harness.project_model.core import CoreError, artifact_blockers, capability_blockers, capability_resolve
from harness.assurance.semantic_acceptance import evaluation_index
from harness.assurance.semantic_derivation import derivation_evaluation_index

__all__ = ['Any',
 'CoreError',
 'FAILURE_SET_KIND',
 'OUTCOMES',
 'PUBLICATION_KIND',
 'PUBLICATION_VERSION',
 'Path',
 'SEMANTIC_SET_KIND',
 'STATE_KEYS',
 'annotations',
 'artifact_blockers',
 'build_project_publication',
 'capability_blockers',
 'capability_resolve',
 'contextmanager',
 'copy',
 'decision_failure_index',
 'derivation_evaluation_index',
 'evaluation_index',
 'hashlib',
 'json',
 'lifecycle_index',
 'os',
 'prepare_capability_transition',
 'publish_project_publication',
 'read_project_publication',
 'tempfile',
 'validate_project_publication',
 'validate_projection',
 'validate_realization',
 'yaml']

PUBLICATION_KIND = "harness-project-publication"
PUBLICATION_VERSION = 1
SEMANTIC_SET_KIND = "harness-semantic-evaluation-set"
FAILURE_SET_KIND = "harness-decision-failure-set"
OUTCOMES = {"CURRENT", "BLOCKED", "FAILED_VALIDATION"}
STATE_KEYS = {
    "core_model",
    "semantic_evaluations",
    "lifecycle",
    "decision_failures",
}


def _empty_failure_set() -> dict[str, Any]:
    return {
        "version": 1,
        "kind": FAILURE_SET_KIND,
        "failures": [],
    }


def _semantic_evaluation_index(
    document: dict[str, Any],
) -> dict[tuple[str, str], dict[str, Any]]:
    """Validate one current semantic-evidence snapshot for publication."""
    if (
        document.get("version") != 1
        or document.get("kind") != SEMANTIC_SET_KIND
    ):
        raise CoreError("unexpected semantic evaluation set")

    evaluations = document.get("semantic_evaluations")
    if not isinstance(evaluations, list):
        raise CoreError("semantic evaluation set semantic_evaluations must be a list")
    derivations = document.get("derivation_evaluations", [])
    if not isinstance(derivations, list):
        raise CoreError("semantic evaluation set derivation_evaluations must be a list")

    for item in evaluations:
        if not isinstance(item, dict):
            raise CoreError("semantic evaluation must be a mapping")
        if item.get("kind") != "harness-artifact-semantic-evaluation":
            raise CoreError("unexpected semantic evaluation kind")
        artifact = item.get("artifact")
        capability = item.get("capability")
        if not isinstance(artifact, str) or not artifact:
            raise CoreError("semantic evaluation artifact is required")
        if not isinstance(capability, str) or not capability:
            raise CoreError("semantic evaluation capability is required")
        if item.get("status") not in {"ACCEPTED", "REJECTED"}:
            raise CoreError(
                f"semantic evaluation {artifact}/{capability} has invalid status"
            )

    for item in derivations:
        if not isinstance(item, dict):
            raise CoreError("semantic derivation evaluation must be a mapping")
        if item.get("kind") != "harness-semantic-derivation-evaluation":
            raise CoreError("unexpected semantic derivation evaluation kind")
        if item.get("status") not in {"ACCEPTED", "REJECTED"}:
            raise CoreError("semantic derivation evaluation has invalid status")

    result = evaluation_index([document])
    derivation_evaluation_index([document])
    return {
        (artifact, capability): item
        for (artifact, capability), item in result.items()
        if isinstance(artifact, str) and isinstance(capability, str)
    }


def _state(
    *,
    core_model: dict[str, Any],
    semantic_evaluations: dict[str, Any],
    lifecycle: dict[str, Any],
    decision_failures: dict[str, Any] | None,
) -> dict[str, Any]:
    return {
        "core_model": copy.deepcopy(core_model),
        "semantic_evaluations": copy.deepcopy(semantic_evaluations),
        "lifecycle": copy.deepcopy(lifecycle),
        "decision_failures": copy.deepcopy(
            decision_failures if decision_failures is not None else _empty_failure_set()
        ),
    }


def _revision(parent_revision: str | None, state: dict[str, Any]) -> str:
    payload = {
        "parent_revision": parent_revision,
        "state": state,
    }
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def _is_revision(value: Any) -> bool:
    if not isinstance(value, str) or not value.startswith("sha256:"):
        return False
    digest = value[len("sha256:") :]
    return len(digest) == 64 and all(ch in "0123456789abcdef" for ch in digest)


def validate_project_publication(
    graph: dict[str, Any],
    publication: dict[str, Any],
) -> dict[str, Any]:
    if publication.get("version") != PUBLICATION_VERSION:
        raise CoreError("project publication version must be 1")
    if publication.get("kind") != PUBLICATION_KIND:
        raise CoreError("unexpected project publication kind")
    if set(publication) != {
        "version",
        "kind",
        "revision",
        "parent_revision",
        "state",
    }:
        raise CoreError(
            "project publication must contain exactly version, kind, revision, "
            "parent_revision and state"
        )

    revision = publication.get("revision")
    parent_revision = publication.get("parent_revision")
    if not _is_revision(revision):
        raise CoreError("project publication revision must be sha256:<64-hex>")
    if parent_revision is not None and not _is_revision(parent_revision):
        raise CoreError(
            "project publication parent_revision must be null or sha256:<64-hex>"
        )

    state = publication.get("state")
    if not isinstance(state, dict) or set(state) != STATE_KEYS:
        raise CoreError(
            "project publication state must contain exactly core_model, "
            "semantic_evaluations, lifecycle and decision_failures"
        )

    realized = validate_realization(graph, state["core_model"])
    lifecycle = validate_projection(graph, realized, state["lifecycle"])
    failures = decision_failure_index(state["decision_failures"])
    evaluations = _semantic_evaluation_index(state["semantic_evaluations"])

    for capability, lifecycle_item in lifecycle.items():
        key = (lifecycle_item["artifact"], capability)
        evaluation = evaluations.get(key)
        if evaluation is None:
            continue
        if evaluation.get("status") != "ACCEPTED":
            raise CoreError(
                f"publication lifecycle provider {lifecycle_item['artifact']}/"
                f"{capability} has non-accepted semantic evaluation"
            )
        admission = evaluation.get("admission")
        if not isinstance(admission, dict) or admission.get("status") != "ACCEPTED":
            raise CoreError(
                f"publication semantic evaluation {lifecycle_item['artifact']}/"
                f"{capability} lacks accepted admission evidence"
            )
        if admission.get("acceptance_id") != lifecycle_item.get("acceptance_id"):
            raise CoreError(
                f"publication acceptance identity mismatch for {capability}"
            )
        admission_policy = admission.get("acceptance_policy_fingerprint")
        lifecycle_policy = lifecycle_item.get("acceptance_policy_fingerprint")
        if (
            admission_policy is not None
            or lifecycle_policy is not None
        ) and admission_policy != lifecycle_policy:
            raise CoreError(
                f"publication acceptance policy mismatch for {capability}"
            )

    expected_revision = _revision(parent_revision, state)
    if revision != expected_revision:
        raise CoreError(
            f"project publication revision mismatch: expected {expected_revision}, "
            f"got {revision}"
        )

    return {
        "publication": publication,
        "realized": realized,
        "lifecycle": lifecycle,
        "failures": failures,
        "evaluations": evaluations,
    }


def build_project_publication(
    *,
    graph: dict[str, Any],
    core_model: dict[str, Any],
    semantic_evaluations: dict[str, Any],
    lifecycle: dict[str, Any],
    decision_failures: dict[str, Any] | None = None,
    parent_revision: str | None = None,
) -> dict[str, Any]:
    state = _state(
        core_model=core_model,
        semantic_evaluations=semantic_evaluations,
        lifecycle=lifecycle,
        decision_failures=decision_failures,
    )
    publication = {
        "version": PUBLICATION_VERSION,
        "kind": PUBLICATION_KIND,
        "revision": _revision(parent_revision, state),
        "parent_revision": parent_revision,
        "state": state,
    }
    validate_project_publication(graph, publication)
    return publication


def _blockers_for_capability(
    realized: dict[str, Any],
    capability: str,
    *,
    selected_artifact: str | None = None,
) -> list[str]:
    blockers = set(capability_blockers(realized, capability))
    if selected_artifact is not None:
        blockers.update(artifact_blockers(realized, selected_artifact))
        return sorted(blockers)

    try:
        providers = capability_resolve(realized, capability)
    except CoreError:
        providers = []
    if blockers:
        return sorted(blockers)

    usable = [
        artifact_id
        for artifact_id in providers
        if not artifact_blockers(realized, artifact_id)
    ]
    if usable:
        return []

    for artifact_id in providers:
        blockers.update(artifact_blockers(realized, artifact_id))
    return sorted(blockers)


def _validate_terminal_outcome(
    *,
    graph: dict[str, Any],
    publication: dict[str, Any],
    capability: str,
    outcome: str,
) -> None:
    if outcome not in OUTCOMES:
        raise CoreError(
            f"unsupported capability publication outcome: {outcome}"
        )
    checked = validate_project_publication(graph, publication)
    realized = checked["realized"]
    lifecycle = checked["lifecycle"]
    failures = checked["failures"]
    evaluations = checked["evaluations"]

    if outcome == "BLOCKED":
        lifecycle_item = lifecycle.get(capability)
        selected_artifact = (
            lifecycle_item.get("artifact")
            if isinstance(lifecycle_item, dict)
            else None
        )
        if not _blockers_for_capability(
            realized,
            capability,
            selected_artifact=selected_artifact,
        ):
            raise CoreError(
                f"BLOCKED publication for {capability} requires an unresolved Core blocker"
            )
        return

    if outcome == "FAILED_VALIDATION":
        if capability not in failures:
            raise CoreError(
                f"FAILED_VALIDATION publication for {capability} requires failure evidence"
            )
        return

    if capability in failures:
        raise CoreError(
            f"CURRENT publication for {capability} must clear persisted failure evidence"
        )
    lifecycle_item = lifecycle.get(capability)
    if lifecycle_item is None:
        raise CoreError(
            f"CURRENT publication for {capability} requires lifecycle evidence"
        )
    try:
        providers = capability_resolve(realized, capability)
    except CoreError as exc:
        raise CoreError(
            f"CURRENT publication for {capability} requires a Core provider"
        ) from exc
    if lifecycle_item["artifact"] not in providers:
        raise CoreError(
            f"CURRENT publication lifecycle provider for {capability} is not a Core provider"
        )
    blockers = _blockers_for_capability(
        realized,
        capability,
        selected_artifact=lifecycle_item["artifact"],
    )
    if blockers:
        raise CoreError(
            f"CURRENT publication for {capability} remains blocked by {blockers}"
        )
    evaluation = evaluations.get((lifecycle_item["artifact"], capability))
    if evaluation is None:
        raise CoreError(
            f"CURRENT publication for {capability} requires accepted semantic evaluation"
        )
    admission = evaluation.get("admission")
    if (
        evaluation.get("status") != "ACCEPTED"
        or not isinstance(admission, dict)
        or admission.get("status") != "ACCEPTED"
        or admission.get("acceptance_id") != lifecycle_item["acceptance_id"]
    ):
        raise CoreError(
            f"CURRENT publication for {capability} has inconsistent semantic admission"
        )


def prepare_capability_transition(
    *,
    graph: dict[str, Any],
    current_publication: dict[str, Any],
    expected_revision: str,
    capability: str,
    outcome: str,
    core_model: dict[str, Any],
    semantic_evaluations: dict[str, Any],
    lifecycle: dict[str, Any],
    decision_failures: dict[str, Any] | None = None,
) -> dict[str, Any]:
    validate_project_publication(graph, current_publication)
    current_revision = current_publication["revision"]
    if expected_revision != current_revision:
        raise CoreError(
            f"project publication compare-and-swap failed: expected "
            f"{expected_revision}, current {current_revision}"
        )

    next_state = _state(
        core_model=core_model,
        semantic_evaluations=semantic_evaluations,
        lifecycle=lifecycle,
        decision_failures=decision_failures,
    )
    if next_state == current_publication["state"]:
        _validate_terminal_outcome(
            graph=graph,
            publication=current_publication,
            capability=capability,
            outcome=outcome,
        )
        return copy.deepcopy(current_publication)

    next_publication = {
        "version": PUBLICATION_VERSION,
        "kind": PUBLICATION_KIND,
        "revision": _revision(current_revision, next_state),
        "parent_revision": current_revision,
        "state": next_state,
    }
    _validate_terminal_outcome(
        graph=graph,
        publication=next_publication,
        capability=capability,
        outcome=outcome,
    )
    return next_publication


def read_project_publication(
    path: str | Path,
    *,
    graph: dict[str, Any],
) -> dict[str, Any]:
    path = Path(path)
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise CoreError(f"cannot load project publication {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise CoreError(f"project publication {path} must contain a mapping")
    validate_project_publication(graph, value)
    return value


@contextmanager
def _exclusive_publication_lock(path: Path):
    """Serialize direct-file publishers without leaving a stale process lock."""
    path.parent.mkdir(parents=True, exist_ok=True)
    lock_path = path.with_name(f".{path.name}.lock")
    with lock_path.open("a+b") as handle:
        if os.name == "nt":
            import msvcrt

            handle.seek(0, os.SEEK_END)
            if handle.tell() == 0:
                handle.write(b"\0")
                handle.flush()
            handle.seek(0)
            msvcrt.locking(handle.fileno(), msvcrt.LK_LOCK, 1)
            try:
                yield
            finally:
                handle.seek(0)
                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
        else:
            import fcntl

            fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
            try:
                yield
            finally:
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def publish_project_publication(
    path: str | Path,
    *,
    graph: dict[str, Any],
    publication: dict[str, Any],
    expected_revision: str | None,
) -> dict[str, Any]:
    """Atomically replace one direct-declaration publication file.

    Project-native adapters must provide an equivalent atomic/CAS boundary in
    their own persistence mechanism instead of using this filesystem helper.
    """
    validate_project_publication(graph, publication)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with _exclusive_publication_lock(path):
        current: dict[str, Any] | None = None
        if path.exists():
            current = read_project_publication(path, graph=graph)
            if expected_revision is None:
                raise CoreError(
                    "existing project publication requires expected_revision"
                )
            if current["revision"] != expected_revision:
                raise CoreError(
                    f"project publication compare-and-swap failed: expected "
                    f"{expected_revision}, current {current['revision']}"
                )
            if publication["revision"] == current["revision"]:
                return copy.deepcopy(current)
            if publication["parent_revision"] != current["revision"]:
                raise CoreError(
                    "project publication parent_revision does not match current revision"
                )
        else:
            if expected_revision is not None:
                raise CoreError(
                    "initial project publication must use expected_revision=null"
                )
            if publication["parent_revision"] is not None:
                raise CoreError(
                    "initial project publication must have parent_revision=null"
                )

        fd, temp_name = tempfile.mkstemp(
            prefix=f".{path.name}.",
            suffix=".tmp",
            dir=str(path.parent),
        )
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                yaml.safe_dump(
                    publication,
                    handle,
                    sort_keys=False,
                    allow_unicode=True,
                )
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temp_name, path)
            try:
                dir_fd = os.open(path.parent, os.O_RDONLY)
            except OSError:
                dir_fd = None
            if dir_fd is not None:
                try:
                    os.fsync(dir_fd)
                finally:
                    os.close(dir_fd)
        finally:
            if os.path.exists(temp_name):
                os.unlink(temp_name)
    return copy.deepcopy(publication)
