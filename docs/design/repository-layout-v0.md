# Repository Layout v0

Status: canonical; physical migration closed.

## Purpose

Harness runtime implementations live under `src/harness/**`. Repository-level
validation, tests, evaluation infrastructure and research are physically separated
from production runtime. Legacy root/dotted Python facades are removed.

The machine-readable contract is
`spec/architecture/repository-layout-v0.yaml`; bounded-context ownership is
`spec/architecture/harness-context-map-v0.yaml`.

## Canonical layout

```text
src/harness/       production runtime and application orchestration
checks/            repository, architecture and CI policy checks
tests/             behavioral, regression, integration and acceptance tests
evals/             evaluation runners and provider adapters
experiments/       research implementations
distribution/      standalone bootstrap transport
spec/              machine-readable contracts
docs/              design/research/audit documentation
skills/            agent procedures and routing registries
```

Root Python modules are forbidden. `root_python.migration_baseline_modules`,
`permanent_bootstrap_exceptions` and `permanent_consumer_tooling_modules`
must remain empty.

## Source-tree package bridge

The repository is intentionally executable without installing Harness as a
package. `harness/__init__.py` supplies the package search path into
`src/harness`; `src/harness/**` remains the only runtime implementation owner.
The bridge is package wiring, not a second runtime implementation.

## Runtime ownership

Each owned runtime module belongs to exactly one bounded context or the
Application layer. Cross-context dependencies follow
`spec/architecture/harness-context-map-v0.yaml`; selected published symbol
boundaries are documented in
`docs/design/context-published-contracts-v0.md`.

`checks/validate_context_boundaries.py` enforces:

- complete context ownership;
- canonical package placement;
- dependency direction and published boundaries;
- a closed root Python namespace;
- absence of undeclared runtime packages.

## Distribution

Consumer distribution is canonical-only:

- `consumer_api: v1`;
- `spec/distribution/consumer-pack-v1.yaml`;
- `spec/distribution/consumer-binding-example-v1.json`;
- `spec/distribution/target-agents-fragment-v1.md`;
- `distribution/harnessw.py`.

The Consumer Pack contains canonical `harness.*` modules. It does not contain
root module facades or a top-level `adapters/` tree.

Scenario execution is owned by
`harness.application.scenario_suite` and
`harness.application.scenario_drivers`.

Provider-backed behavioral evaluation is infrastructure under
`evals/adapters/copilot_behavioral_eval_agent.py` and is not part of the
Consumer Pack.

## Closure invariant

A repository change that reintroduces a root `*.py` runtime module, an
undeclared runtime module, a retired Consumer API identity, or a top-level
legacy adapter implementation is a layout regression rather than a compatibility
extension.
