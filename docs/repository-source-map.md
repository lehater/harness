# Repository source map

## Runtime

- `src/harness/project_model/**` — Core, Engineering Graph and Target State.
- `src/harness/reference_model/**` — reference materialization and project status.
- `src/harness/coverage/**` — concern activation, obligations, planning and coverage.
- `src/harness/assurance/**` — acceptance, derivation, lifecycle and calibration.
- `src/harness/decision/**` — exploration, governance and execution assurance.
- `src/harness/evidence/**` — source boundary/set/coverage.
- `src/harness/integration/**` — project adapters and repository realization.
- `src/harness/workspace/**` — managed workspace and human/frontend projections.
- `src/harness/application/**` — orchestration, routing, publication, Consumer Pack,
  Scenario Suite and Scenario Drivers.

`harness/__init__.py` is the source-tree package bridge into `src/harness`;
it is not a second implementation tree.

## Validation and evaluation

- `checks/**` — repository, architecture and CI policy checks.
- `tests/**` — behavioral, regression, integration and acceptance tests.
- `evals/behavioral_eval.py` — provider-neutral behavioral-evaluation runner.
- `evals/live_calibration_process_driver.py` — external live-calibration process driver.
- `evals/adapters/copilot_behavioral_eval_agent.py` — Copilot behavioral provider adapter.
- `experiments/**` — research implementations.

## Distribution

- `distribution/harnessw.py` — standalone bootstrap transport.
- `spec/distribution/consumer-pack-v1.yaml` — canonical Consumer Pack inventory.
- `spec/distribution/consumer-binding-example-v1.json` — canonical pinned binding example.
- `spec/distribution/target-agents-fragment-v1.md` — target-agent bootstrap instructions.
- `docs/design/harness-consumer-pack-v1.md` — Consumer Pack contract.
- `docs/design/harness-consumer-wrapper-v1.md` — wrapper/bootstrap contract.

## Architecture contracts

- `spec/architecture/harness-context-map-v0.yaml` — bounded-context ownership/dependencies.
- `spec/architecture/repository-layout-v0.yaml` — physical layout/closed-root contract.
- `docs/design/context-published-contracts-v0.md` — explicit published cross-context symbols.
- `docs/design/repository-layout-v0.md` — canonical physical layout.
- `docs/design/document-projection-operations-v0.md` — reusable mechanism for specialized source-bounded generated document/diagram projection operations.

## Agent surfaces

- `skills/maintainer-operation-registry-v0.yaml` — Maintainer operations.
- `skills/consumer-operation-registry-v0.yaml` — Consumer operations.
- `skills/consumer-method-registry-v0.yaml` — Consumer methods.
- `skills/artifact-skill-registry-v0.yaml` — artifact production routes.
- `skills/skill-surface-registry-v0.yaml` — skill surface/type/lifecycle inventory.

Historical audit material under `docs/audit/**` may mention retired paths as
historical evidence; it is not a description of the current executable layout.
