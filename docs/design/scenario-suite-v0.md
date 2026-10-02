# Harness Scenario Suite v0

## Purpose

The Scenario Suite is the executable behavioral specification of Harness as a
whole. It tests how Harness reacts to project states and transitions rather than
testing individual Python functions in isolation.

It is deliberately a test-orchestration protocol, not a universal engineering
semantic model and not new Harness Core state. Its role in the broader evidence
hierarchy is governed by `docs/design/harness-assurance-policy-v0.md`; Scenario
Suite coverage is an evidence provider, not the independent denominator of
Harness correctness.

## Model

```text
project/scenario fixture
        ↓
ordered scenario steps
        ↓
pluggable Harness driver
        ↓
structured observation
        ↓
invariant assertions
        ↓
coverage catalog
        ↓
suite report
```

A scenario may represent a synthetic project, a fixture copied from a real
project shape, or a mutation of a known-good state.

## Scenario contract

Each `harness-scenario` declares:

- stable scenario id;
- arbitrary catalog-defined dimensions such as project archetype, Harness stage,
  behavior class and execution type;
- behavioral requirements it claims to cover;
- reusable fixtures;
- ordered driver steps;
- invariant assertions over each step result.

The runner never executes arbitrary Python from YAML.

References use `{"ref": "fixture.NAME"}` or
`{"ref": "step.STEP_ID"}`. A JSON Pointer may follow `#`, for example
`{"ref": "step.before#/status"}`.

## Fixtures

The runner supports inline values plus reusable file/workspace fixtures:

- `value` — inline structured value;
- `yaml` / `json` / `text` — load a file relative to the scenario;
- `path` — expose a fixture path to a driver;
- `workspace` — copy a project tree into an isolated temporary directory.

This allows future scenarios to exercise whole project layouts without changing
the runner.

## Drivers

A driver is a named adapter from scenario arguments to one Harness behavior.
Drivers are registered in `scenario_drivers.py`.

Initial drivers expose:

- Core validation;
- Engineering Graph target evaluation;
- semantic acceptance;
- semantic-gap Question derivation and application;
- semantic closure;
- lifecycle currentness;
- concern activation;
- decision exploration;
- decision governance;
- test-data patch/mutation.

Adding a Harness mechanism requires a driver only when no existing driver can
observe it. The scenario runner itself should remain unchanged.

## Oracles

v0 uses deterministic invariant assertions over structured results:

- equals / not-equals;
- exists / not-exists;
- contains / contains-all;
- set equality;
- length;
- truthy / falsy;
- expected exception type/message.

Prefer invariants over full golden-output snapshots. This keeps scenarios stable
when irrelevant output fields evolve.

Agentic or heuristic decisions are tested through structured evidence rather
than a literal golden answer. Scenario drivers expose the decision/exploration
boundary; scenarios assert required constraints, material alternative diversity,
forbidden preselection, delegation limits, escalation behavior and accepted
outcome properties. Several concrete answers may remain valid while the
decision process is still testable.

## Mutation testing

`data.patch` creates variants of a known-good fixture inside the scenario.
This supports tests such as:

```text
COMPLETE fixture
→ remove one provider / fact / obligation / decision
→ run Harness
→ assert the exact expected reaction
```

The base fixture remains unchanged.

## Coverage catalog

`spec/scenario-suite/catalog-v1.yaml` is the inventory of Harness behaviors
that must have executable scenario coverage. Scenarios declare `covers`.

The catalog also owns the allowed scenario dimensions, mandatory dimension
values and required driver coverage. Therefore the suite can fail even when all
individual scenarios pass, for example when:

- a Harness behavior has no passing scenario;
- a required stage or behavior class has no scenario at all;
- a newly mandatory driver has never been exercised;
- a specific behavior is required to be proven across several dimension values.

Dimensions are data, not Python fields. Adding a future axis such as
`risk_class` or `project_maturity` requires only catalog/scenario changes.

This is not a claim of mathematical completeness. It makes missing test
coverage explicit and reviewable as Harness grows.

## Intended growth

The suite should expand across independent dimensions:

- project archetype: user-facing, backend/service, data/integration, library;
- lifecycle stage: bootstrap, discovery, design, decision, implementation,
  revalidation;
- behavior class: happy path, missing knowledge, contradiction, wrong
  Authority, invalid provenance, deferred decision, stale downstream,
  implementation feedback;
- execution type: deterministic mechanisms first, agent/evaluator-backed
  behavior separately.

Real-project fixtures such as Prep or NAPMS may be added as regression
scenarios, but reusable synthetic scenarios remain the minimal proofs of Harness
mechanics.


## Current bootstrap coverage

The first cross-layer suite intentionally spans distinct Harness mechanisms:

- structural target reaction and mutation;
- semantic completeness gap to owning-Authority Question;
- recurring Question reopening;
- lifecycle currentness propagation;
- CREATE-to-skill routing and WAIT suppression;
- selective concern activation;
- sequential decision frontier;
- blind pre-choice exploration;
- autonomy enforcement and escalation;
- Engineering Coverage;
- Graph Doctor diagnostics;
- project Authority applicability/status.

These scenarios are bootstrap proofs of the mechanism, not the final scenario
inventory. New Harness behavior should normally add or strengthen a catalog
requirement and then add scenarios until that requirement is satisfied.


## External drivers

Target repositories may extend the runner without changing Harness. The CLI
accepts repeated `--driver-module <python.module>` options. Each explicitly
loaded module may register drivers through `scenario_driver(...)`.

Driver modules are selected by the operator/CI command, never by scenario YAML.
This keeps executable-code selection outside untrusted test data while allowing
Prep, NAPMS or another repository to expose project-native validators and
integration behavior to the same scenario protocol.

## Observations

Assertions determine pass/fail. A step may additionally declare `observe` as a
mapping from stable observation names to JSON Pointer paths. Observations are
copied into the suite report without requiring a full golden snapshot.

Use observations for longitudinal analysis such as selected frontier size,
Question owner, activated concern count or decision disposition. They are
diagnostic evidence, not a second correctness oracle.


### Required versus planned coverage

A catalog requirement may set `enforcement: required` or
`enforcement: planned` (default is `required`).

- **required** — missing passing scenarios fail the suite;
- **planned** — the gap is emitted in `planned_gaps` but does not fail CI.

This permits the catalog to describe the complete known Harness functional
surface before every scenario exists. Coverage should normally move from
`planned` to `required` when a stable executable scenario is available.
New behavior must not remain uncataloged merely because its scenario has not yet
been written.
