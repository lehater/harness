# Harness repository agent map

## Purpose

Harness Core manages engineering-knowledge ownership boundaries for target repositories.

Harness Core v0 owns only the structural model and derived operations described in `docs/design/core-v0.md`. Target repositories own all product/domain/architecture semantics, canonical artifact contents, implementation constraints and durable project state.

The Design Profile layer in `docs/design/target-state-v0.md` declares what engineering knowledge a selected scope must contain before it is structurally design-complete. It does not add workflow semantics to Core.

The optional managed workspace in `docs/design/managed-knowledge-v0.md` lets a target project keep Harness-owned canonical machine-readable knowledge under `.harness/` and derive human-readable documentation from it.

## Consumer startup

When Harness is used with another repository:

1. read `docs/design/core-v0.md`;
2. read the target repository's own instructions;
3. locate only the target canonical artifacts required by the task;
4. use the target's declared Core model, when present, to navigate ownership, capabilities, dependencies and unresolved Questions;
5. when a Design Profile is present, use it to evaluate the target state without inventing missing knowledge;
6. when the project opts into a managed `.harness/` workspace, validate managed knowledge before treating its generated documentation as current.

No manifest, pin, submodule or repository-to-repository runtime binding is required. The managed workspace is a target-project-local opt-in format.

## Core rules

- One `CanonicalArtifact` belongs to exactly one `Authority`.
- A `CapabilityId` may have several providers only when every canonical provider belongs to the same `Authority`.
- `depends_on` expresses declared canonical-artifact dependency.
- A `Question` is addressed to the `Authority` that may decide the missing semantics.
- A Question never stores the final semantic answer. Resolution references the canonical artifact changed by the addressed Authority.
- Harness validates declared structure, ownership, references, dependencies and capability ownership. It does not infer arbitrary engineering semantics.

## Change discipline

Do not add Stage/Phase, Role/Person/Team, Task/Change, Workflow/Status machine, Gate/Approval, Readiness, Handoff, maturity/scoring, task capsules or a universal semantic DSL without a concrete consumer failure.

A Core extension requires a failure case that states:
- what the consumer attempted;
- which canonical truth was available;
- what was missing;
- why Authority / CanonicalArtifact / CapabilityId / Question / dependency were insufficient;
- what incorrect workaround would otherwise be required.

Add an acceptance fixture reproducing that failure before changing Core behavior.

## Source map

- `docs/design/core-v0.md` — current Core boundary and model.
- `docs/design/target-state-v0.md` — Design Profile target-state contract.
- `docs/design/managed-knowledge-v0.md` — optional managed canonical knowledge and generated-document contract.
- `harness.py` — Core v0 structural operations.
- `target_state.py` — target-state evaluator above Core.
- `workspace.py` — managed knowledge validation and rendering.
- `adapters/canonical_graph.py` — optional projection of existing canonical graph routing into Core without copying paths/dependencies.
- `spec/acceptance/**` — executable Core acceptance cases.
- `spec/adapter-acceptance/**` — executable adapter integration cases.
- `spec/target-state-acceptance/**` — executable Design Profile target-state cases.
- `spec/workspace-acceptance/**` — executable managed-workspace scenarios.
- `validators/validate_core.py` — Core validator/acceptance runner.
- `validators/validate_adapters.py` — adapter acceptance runner.
- `validators/validate_target_state.py` — target-state acceptance runner.
- `validators/validate_workspace.py` — managed-workspace acceptance runner.
- `docs/methodology/**` and `skills/**` — retained pre-Core material; not part of Core v0 consumer semantics.

## Repository workflow

- Never push or commit changes directly to `main`.
- Every task is implemented on a dedicated non-main branch.
- Run validation and tests on that branch before integration.
- Integrate completed work into `main` only through a pull request using squash merge.
- Treat `main` as the reviewed, integrated baseline, not as a working branch.
