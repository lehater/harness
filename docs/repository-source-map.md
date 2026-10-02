# Repository Source Map

Status: navigation only; not an instruction or semantic owner.

Purpose: retain the detailed repository inventory outside the automatically loaded root `AGENTS.md`. Load this map on demand when locating implementation, design, assurance, fixture, or validator surfaces. Active procedure discovery still goes through `skill_router.py` and the registered skill surfaces.

## Inventory

- `skills/maintainer-operation-registry-v0.yaml` — active Harness-maintainer operation routes.
- `skills/consumer-operation-registry-v0.yaml` — active Harness-consumer operation routes.
- `skills/consumer-method-registry-v0.yaml` — canonical-concern to non-owning consumer method routes.
- `skills/skill-surface-registry-v0.yaml` — explicit skill surface/type/lifecycle inventory.
- `harness.application.skill_router` — canonical typed skill discovery implementation;
  root `skill_router.py` retains the Consumer v0 CLI entrypoint over Maintainer/Consumer operation, method and artifact registries.
- `docs/audit/README.md` — canonical routing policy for defects, evolution ideas and accepted decisions.
- `docs/audit/audit-framework.md` — reusable Harness audit perspectives, coverage and AUD run history.
- `docs/audit/harness-audit-backlog.md` — cumulative `HARN-*` defect/design-gap ledger.
- `docs/audit/harness-evolution-radar.md` — cumulative `EVO-*` non-defect recommendation/research/idea ledger.
- `docs/design/agent-instruction-architecture-v0.md` — canonical instruction ownership/scoping contract.
- `docs/design/operation-orchestration-v0.md` — canonical coordinator/router/operation composition contract.
- `docs/design/context-published-contracts-v0.md` — canonical published module/symbol contracts for selected cross-context dependencies.
- `docs/design/repository-layout-v0.md` — canonical physical-layout migration target and responsibility boundaries.
- `spec/architecture/repository-layout-v0.yaml` — machine-readable root-module migration ratchet and context-to-package target mapping.
- `docs/design/core-v0.md` — current Core boundary and model.
- `docs/design/harness-consumer-pack-v0.md` — pinned Consumer Pack binding, materialization and validation contract.
- `docs/design/harness-consumer-wrapper-v0.md` — clean-target wrapper/bootstrap contract.
- `spec/distribution/consumer-pack-v0.yaml` — machine-readable Consumer Pack export definition.
- `spec/assurance/llm-execution-policy-v1.yaml` — conditional provider-backed assurance execution policy.
- `evals/behavioral_eval.py` — provider-neutral clean-context behavioral-evaluation runner, semantic normalizer and scorer.
- `spec/behavioral-evals/first-wave/manifest-v0.yaml` — reviewed first-wave Capability/Authority/task-intent behavioural case inventory.
- `adapters/copilot_behavioral_eval_agent.py` — provider adapter for clean-context judgement runs; oracle/pass criteria are not provider inputs.
- `validators/validate_behavioral_eval_cases.py` — deterministic first-wave case/adapter boundary validation; not judgement evidence.
- `.github/workflows/behavioral-eval-copilot.yml` — operator-triggered external provider execution for first-wave behavioural evidence.
- `validators/validate_behavioral_eval.py` — deterministic substrate contract/self-test; it is not agent-quality evidence.
- `docs/design/harness-assurance-policy-v0.md` — canonical evidence-selection, test-level and oracle policy for Harness changes/release claims.
- `docs/design/harness-ability-to-evidence-v0.md` — canonical Harness ability/failure-mode/evidence blueprint used to design assurance before implementation.
- `docs/design/harness-test-design-catalog-v0.md` — reviewed framework-neutral test designs and implementation dispositions for Harness assurance gaps.
- `docs/design/harness-agent-behavioral-evaluation-v0.md` — clean-context behavioural-eval protocol for judgement-dependent agent responsibilities.
- `docs/design/harness-assurance-registry-v0.md` — canonical design for the machine-readable Ability -> requirement -> evidence assurance denominator/self-test.
- `spec/assurance/harness-assurance-registry-v0.yaml` — initial machine-readable assurance denominator/evidence seed.
- `validators/validate_assurance_registry.py` — assurance registry structural/admissibility validator and AR-M01..AR-M08 self-tests.
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
- `src/harness/project_model/core.py` — canonical Core v0 structural operations and CLI implementation.
- `harness/__init__.py` — temporary source-tree Core import bridge.
- `harness.py` — legacy Core CLI compatibility facade.
- `src/harness/project_model/target_state.py` — canonical target-state evaluator above Core;
  `target_state.py` is its temporary import/CLI facade.
- `src/harness/project_model/engineering_graph.py` — canonical Engineering Graph implementation;
  `engineering_graph.py` is its temporary import/CLI facade.
- `src/harness/reference_model/project_status.py` — canonical Authority applicability/status implementation;
  `project_status.py` is its temporary import/CLI facade.
- `src/harness/reference_model/reference_materializer.py` — canonical Reference Engineering Model validator/materializer;
  `reference_materializer.py` is its temporary import/CLI facade.
- `src/harness/reference_model/reference_model_evolution.py` — canonical Reference Model evolution analysis;
  `reference_model_evolution.py` is its temporary import-only facade.
- `src/harness/coverage/` — the five canonical `harness.coverage.*` modules for
  applicability, subject obligations, proof planning and completeness evaluation;
  the five root Coverage modules are temporary import/CLI compatibility facades.
- `src/harness/decision/` — the four canonical `harness.decision.*` modules for
  exploration, Explorer request contracts, governance and execution assurance;
  the four corresponding root files are temporary import-only facades.
- `src/harness/application/project_frontier.py` — canonical derived cross-layer next-action frontier; it owns precedence only, never project truth.
- `src/harness/application/project_publication.py` — validates/prepares one coherent project-state publication revision and provides crash-safe direct-file publication.
- `src/harness/application/graph_doctor.py` — canonical non-destructive aggregate diagnostics over Engineering Graph/Core/project integration.
- `src/harness/workspace/` — the four canonical `harness.workspace.*` modules for
  frontend contracts, managed knowledge and disposable human projections;
  root frontend modules are import-only facades, while `human_projection.py`
  and `workspace.py` retain import/CLI compatibility.
- `src/harness/evidence/source_boundary.py` — canonical assurance-only lossless line-range coverage;
  `source_boundary.py` is its temporary import/CLI facade.
- `src/harness/evidence/source_coverage.py` — canonical statement-level admitted/excluded/question coverage;
  `source_coverage.py` is its temporary import/CLI facade.
- `src/harness/evidence/source_set.py` — canonical acquisition-contract source-set completeness;
  `source_set.py` is its temporary import/CLI facade.
- `src/harness/integration/` — canonical alignment, repository realization and
  canonical-graph adapter implementations; root `integration_alignment.py`,
  `repository_realization.py` and `adapters/canonical_graph.py` retain legacy
  Consumer v0 import/CLI entrypoints.
- `src/harness/assurance/` — canonical semantic acceptance/derivation/fingerprint,
  acceptance policy, lifecycle, derivation coverage and calibration implementations;
  the eight corresponding root files and
  `adapters/copilot_live_calibration_evaluator.py` retain legacy Consumer v0 facades.
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
- `validators/validate_context_boundaries.py` — bounded-context import ratchet plus repository-layout/root-module migration ratchet.
- `docs/methodology/**` — retained pre-Core material; not part of Core v0 consumer semantics.

- `src/harness/application/` — fifteen canonical Application runtime modules;
  same-layer imports are relative, and fifteen root facades preserve Consumer v0.
  Root `consumer_pack.py` remains the wrapper entrypoint; root `skill_router.py`
  remains the Pack CLI. No Consumer API bump or installed-package requirement.
- `distribution/harnessw.py` — deliberately standalone stdlib-only bootstrap
  transport, copied to target `.harness/harnessw.py`; excluded from the Pack and
  independent of `harness.application.*` imports.

Runtime physical migration is closed: `src/harness/**` owns production runtime,
`experiments/**` contains research, and `evals/**` contains the moved evaluation
runner/process driver. Root Scenario modules remain Consumer v0 tooling; other
root runtime surfaces are compatibility facades. See the closure ADR in
`docs/design/repository-layout-v0.md`.


## Consumer API v1 distribution

- `docs/design/harness-consumer-pack-v1.md` — versioned distribution decision
  and wrapper v1 protocol;
- `spec/distribution/consumer-pack-v1.yaml` — explicit canonical runtime inventory;
- `spec/distribution/target-agents-fragment-v1.md` — canonical module router bootstrap.

Consumer v0 definitions and source compatibility facades remain supported.
