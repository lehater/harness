# Harness repository agent map

## Purpose

Harness Core manages engineering-knowledge ownership boundaries for target repositories.

Harness Core v0 owns only the structural model and derived operations described in `docs/design/core-v0.md`. Target repositories own all product/domain/architecture semantics, canonical artifact contents, implementation constraints and durable project state.

The Design Profile layer in `docs/design/target-state-v0.md` declares what engineering knowledge a selected scope must contain before it is structurally design-complete. It does not add workflow semantics to Core.

The optional managed workspace in `docs/design/managed-knowledge-v0.md` lets a target project keep Harness-owned canonical machine-readable knowledge under `.harness/` and derive human-readable documentation from it.

The current operating model is agent-driven. `docs/design/agent-artifact-workbench-v0.md` defines how an agent turns an actionable target-state gap into candidate knowledge, semantic acceptance, Core registration and generated documentation.

## Skill surfaces

Ordinary work in this repository uses the Maintainer Skill Surface declared by
`skills/maintainer-operation-registry-v0.yaml`.

Target repositories using Harness enter through the Consumer Skill Surface
declared by `skills/consumer-operation-registry-v0.yaml` plus deterministic
artifact routing in `skills/artifact-skill-registry-v0.yaml`. Consumer
procedures may be exercised here for fixtures/dogfooding, but they are not the
default maintainer workflow.

Do not reconstruct task-specific procedures from this file. Use `skill_router.py`
as the typed discovery entrypoint (`operation`, `method`, or
`artifact-production`), then read the returned `SKILL.md`. The router delegates
to separate registries; it is not a flat intent classifier.

## Core rules

- One `CanonicalArtifact` belongs to exactly one `Authority`.
- A `CapabilityId` may have several providers only when every canonical provider belongs to the same `Authority`.
- `depends_on` expresses declared canonical-artifact dependency.
- A `Question` is addressed to the `Authority` that may decide the missing semantics.
- A Question may block an existing artifact with `blocks` or prevent formation of a not-yet-provided capability with `blocks_capabilities`.
- A Question never stores the final semantic answer. Resolution references the canonical artifact changed by the addressed Authority and the new opaque semantic acceptance identity; resolving against an unchanged acceptance identity is invalid.
- Harness validates declared structure, ownership, references, dependencies and capability ownership. It does not infer arbitrary engineering semantics.

## Conditional policies

Provider-backed semantic assurance must follow
`spec/assurance/llm-execution-policy-v1.yaml`. Load that policy only when the
selected procedure actually invokes an external LLM evaluator. Deterministic
validation remains preferred when it can answer the question.

## Instruction and operation routing

Instruction ownership/scoping is defined by
`docs/design/agent-instruction-architecture-v0.md`. Composition across routed
operations is defined by `docs/design/operation-orchestration-v0.md`.

Resolve Maintainer work through `skills/maintainer-operation-registry-v0.yaml`
and `skill_router.py`. Task procedures and classification rules belong to the
selected skill and its canonical contracts, not to this bootstrap file.

## Change discipline

Do not add Stage/Phase, Role/Person/Team, Task/Change, Workflow/Status machine,
Gate/Approval, Readiness, Handoff, maturity/scoring, task capsules or a
universal semantic DSL without a concrete consumer failure.

All Harness behavior/Core changes must route through the registered
`change-harness` Maintainer operation; detailed acceptance/scenario procedure
does not live in this root bootstrap file.

## Source map

- `skills/maintainer-operation-registry-v0.yaml` — active Harness-maintainer operation routes.
- `skills/consumer-operation-registry-v0.yaml` — active Harness-consumer operation routes.
- `skills/consumer-method-registry-v0.yaml` — canonical-concern to non-owning consumer method routes.
- `skills/skill-surface-registry-v0.yaml` — explicit skill surface/type/lifecycle inventory.
- `skill_router.py` — typed skill discovery entrypoint over Maintainer/Consumer operation, method and artifact registries.
- `docs/audit/README.md` — canonical routing policy for defects, evolution ideas and accepted decisions.
- `docs/audit/audit-framework.md` — reusable Harness audit perspectives, coverage and AUD run history.
- `docs/audit/harness-audit-backlog.md` — cumulative `HARN-*` defect/design-gap ledger.
- `docs/audit/harness-evolution-radar.md` — cumulative `EVO-*` non-defect recommendation/research/idea ledger.
- `docs/design/agent-instruction-architecture-v0.md` — canonical instruction ownership/scoping contract.
- `docs/design/operation-orchestration-v0.md` — canonical coordinator/router/operation composition contract.
- `docs/design/core-v0.md` — current Core boundary and model.
- `docs/design/harness-consumer-pack-v0.md` — pinned Consumer Pack binding, materialization and validation contract.
- `docs/design/harness-consumer-wrapper-v0.md` — clean-target wrapper/bootstrap contract.
- `spec/distribution/consumer-pack-v0.yaml` — machine-readable Consumer Pack export definition.
- `spec/assurance/llm-execution-policy-v1.yaml` — conditional provider-backed assurance execution policy.
- `docs/design/ci-execution-policy-v0.md` — canonical Harness CI execution/lazy-gate policy.
- `spec/ci/check-registry-v0.yaml` — machine-readable CI check inventory, cost/stage classification and workflow roles.
- `docs/design/target-state-v0.md` — Design Profile target-state contract.
- `docs/design/managed-knowledge-v0.md` — optional managed canonical knowledge and generated-document contract.
- `docs/design/agent-artifact-workbench-v0.md` — current agent-operated artifact creation and semantic acceptance loop.
- `docs/design/decision-governance-v0.md` — experimental pre-choice exploration and delegated-choice contract above Core.
- `docs/design/decision-explorer-execution-assurance-v0.md` — experimental boundary between request binding and externally attested isolated Explorer execution.
- `docs/design/live-calibration-validator-v0.md` — blinded, request-bound live semantic-evaluator calibration above Core.
- `docs/design/decision-pipeline-v0.md` — experimental sequential Decision Pipeline and derived Capability frontier.
- `docs/design/project-frontier-v0.md` — canonical Application Layer next-action composition over Decision Roadmap, Semantic Closure and Engineering Coverage.
- `docs/design/project-publication-v0.md` — canonical atomic publication/CAS boundary for coordinated Core, semantic, lifecycle and failure state.
- `skills/agent/decision-pipeline/SKILL.md` — sequential option-formation, review, choice/escalation and admission procedure for decision-governed work.
- `docs/design/frontend-design-v0.md` — canonical user-facing/frontend engineering knowledge boundary and consumer closure.
- `docs/design/graph-doctor-v1.md` — canonical aggregate graph/model diagnostic contract.
- `docs/design/capability-lifecycle-projection-v1.md` — canonical Capability acceptance-baseline currentness contract.
- `docs/design/human-documentation-projection-v1.md` — canonical source-bounded human documentation projection contract.
- `profiles/**` — reusable starter Design Profiles.
- `skills/agent/**` — active agent orchestration instructions above Core, including scoped bootstrap and Design Profile construction/review.
- `skills/artifacts/**` — active artifact-specific engineering procedures.
- `docs/legacy/skills/**` — quarantined pre-Core procedure text; historical documentation only, never active skill discovery.
- `harness.py` — Core v0 structural operations.
- `target_state.py` — target-state evaluator above Core.
- `project_frontier.py` — canonical derived cross-layer next-action frontier; it owns precedence only, never project truth.
- `project_publication.py` — validates/prepares one coherent project-state publication revision and provides crash-safe direct-file publication.
- `graph_doctor.py` — canonical non-destructive aggregate diagnostics over Engineering Graph/Core/project integration.
- `human_projection.py` — deterministic Consumer-scoped human documentation manifest/recipe/IR/package compiler.
- `workspace.py` — managed knowledge validation and rendering.
- `source_boundary.py` — assurance-only lossless line-range coverage for a selected immutable raw source before semantic statement enumeration.
- `source_coverage.py` — statement-level admitted/excluded/question coverage after the raw source boundary has been established.
- `adapters/canonical_graph.py` — optional projection of existing canonical graph routing into Core without copying paths/dependencies.
- `spec/acceptance/**` — executable Core acceptance cases.
- `spec/decision-governance/**` — experimental decision-governance evidence and knowledge-kind decision contracts.
- `spec/adapter-acceptance/**` — executable adapter integration cases.
- `spec/target-state-acceptance/**` — executable Design Profile target-state cases.
- `spec/workspace-acceptance/**` — executable managed-workspace scenarios.
- `spec/scenario-suite/**` — cross-layer executable behavioral scenarios and coverage catalog.
- `scenario_suite.py` / `scenario_drivers.py` — universal scenario runner and built-in driver registry.
- `validators/validate_core.py` — Core validator/acceptance runner.
- `validators/validate_adapters.py` — adapter acceptance runner.
- `validators/validate_target_state.py` — target-state acceptance runner.
- `validators/validate_graph_doctor.py` — Graph Doctor v1 acceptance runner.
- `validators/validate_human_projection.py` — Human Documentation Projection v1 acceptance runner.
- `validators/validate_workspace.py` — managed-workspace acceptance runner.
- `validators/validate_agent_layer.py` — agent-layer skill/profile contract validation.
- `docs/methodology/**` — retained pre-Core material; not part of Core v0 consumer semantics.

## Repository workflow

- Never push or commit changes directly to `main`.
- Every task is implemented on a dedicated non-main branch.
- Run validation and tests on that branch before integration.
- Integrate completed work into `main` only through a pull request using squash merge.
- Treat `main` as the reviewed, integrated baseline, not as a working branch.
- Treat commits and CI runs as checkpoints, not as a per-file feedback mechanism.
- Keep a pull request draft while exploring/debugging; inspect all known failures before committing the next fix batch.
- Prefer one commit per coherent checkpoint. When repository APIs would create one commit per file, prefer a multi-file tree/commit operation.
- During iteration, run the smallest deterministic affected checks; reserve the full PR gate set for coherent checkpoints and the final candidate.
- For workflows triggered only by `ready_for_review`, make the ready transition only after the branch is stable. On failure, return to draft, batch fixes, then transition once again.
- Do not move the branch head merely to poll or retrigger CI; rerun an existing workflow without content changes when supported.
- Merge only from a stable head with all applicable required gates green.
