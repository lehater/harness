# Harness Scenario Suite v0

## Purpose

The Scenario Suite is the executable behavioral specification of Harness as a
whole. It tests how Harness reacts to project states and transitions rather than
testing individual Python functions in isolation.

It is deliberately a test-orchestration protocol, not a universal engineering
semantic model and not new Harness Core state.

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
- project archetype;
- Harness stage under observation;
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

Agentic or heuristic decisions should later be exposed through a driver that
returns structured decision evidence. The scenario should assert required
constraints, explored alternatives, forbidden behavior, escalation behavior and
accepted outcome properties rather than require one literal answer where several
answers may be valid.

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
The suite fails when a required behavior has no passing scenario.

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
