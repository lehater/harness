# Reference Model CDR — label-blind provider pilot v1

Status: experimental; **no accepted project semantics, no independent Authority verdict, no graph mutation**.

## Purpose

Exercise the existing `evals.adapters.copilot_dependency_resolution_evaluator` against three reusable Reference Engineering Model templates (Interaction Design, Interface Topology, Domain Model) **without exposing their declared `requires`**.

The target obligations are deliberately operator-authored descriptions of artifact SKILL outputs. These are candidates for independent assessment, not accepted project-owner output contracts. The provider catalog includes **all other 39 templates for every case** (not only accepted or graph-linked providers), with public `Output contract` excerpts where available and research claim vocabulary. Every provider is `CONTRACT_ONLY`, never `ACCEPTED_EVIDENCE`.

A source-only snapshot fingerprint binds the Reference Model, Authority catalog, proof vocabulary, pilot profile and corresponding skill output contracts. Existing graph edges are excluded from the provider-facing Phase A payload. The opaque request and case IDs intentionally change with the full source snapshot. The adapter runs Copilot in an isolated fresh session with no tools or repository access. This is **operational blinding**, not independent Authority review or full protection against operator selection bias.

## Execution contract

From the root of the experimental `lehater/harness` checkout with Python 3.10, PyYAML 6.0.3 and an authenticated GitHub Copilot CLI version 1.0.86:

```bash
python -m evals.cdr_reference_provider_pilot prepare --output pilot/inputs.json --request pilot/request.json
python -m evals.cdr_reference_provider_pilot evaluate --request pilot/request.json --output pilot/provider.json
python -m evals.cdr_reference_provider_pilot reconcile --input pilot/inputs.json --request pilot/request.json --response pilot/provider.json --output pilot/contrast.json
```

Copilot evaluation is **explicit/manual and provider-backed**, not included in a PR gate. The existing external GitHub Actions workflow `live-calibration-copilot.yml` has accepted execution bindings and must not be modified to host this experiment: its source hash is part of assurance evidence. Creating a new experimental workflow only on a feature branch also does not make it manually dispatchable until registered on the default branch. Therefore local/isolated operator execution is the valid current run path, without weakening assurance policies or touching main.

The deterministic `tests/test_cdr_reference_provider_pilot.py` is part of `make harness-check` and of the experimental focused PR workflow. It verifies profile and provider counts, label omission, stable source-bound request identity, stale reference rejection, and that removing a reference edge changes the provenance binding but **not model-visible catalog/obligation contents**. It substitutes synthetic response rows for the agent and **does not make a semantic quality claim**.

## Post-model interpretation

`reconcile` reads actual `requires` only after the provider response is frozen. It separates:

- `both_provisional`: model proposal also declared by Reference Model v0;
- `new_candidate_not_accepted`: model proposal with no declared edge;
- `declared_not_suggested_review_only`: declared edge omitted by model, **not automatically a removal candidate**.

Every proposed provider requires a target-output obligation, a specific source public-surface index, a nontrivial rationale and `PLANNED_CONTRACT` basis. Malformed/unbound outputs fail closed.

Model proposals remain **unverified hypotheses**. A target output obligation requires separately accepted project/Authority provenance; a source claim requires actual accepted semantics; and directness requires a concrete target-output constraint, inability of intermediate public contracts to mediate the exact rule, and counterfactual source change sensitivity. These are not established by a tool-free LLM run.

No automatic modification, adoption, publication, PREP change, Harness main change or promotion of frozen Reference Engineering Model v0 is permitted.
