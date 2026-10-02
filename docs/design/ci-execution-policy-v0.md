# Harness CI Execution Policy v0

Status: canonical repository CI execution policy.

## Purpose

This policy governs when Harness validation may run and how validation work is
classified. It exists to keep CI lazy, cheap during iteration, exhaustive before
integration, and resistant to gradual cost regressions.

It does not define product semantics or replace subsystem acceptance contracts.
It governs execution of evidence that already exists. Evidence sufficiency,
test-level selection, oracle strength, and the role of synthetic versus
real-project evidence are owned by
`docs/design/harness-assurance-policy-v0.md`.

## Terms

- **check** — one deterministic validation command registered in
  `spec/ci/check-registry-v0.yaml`.
- **draft iteration** — work on a draft pull request where integration is not
  currently being requested.
- **integration candidate** — a non-draft/ready pull request head being
  considered for integration.
- **full gate** — the exhaustive deterministic repository gate exposed as
  `make harness-check`.
- **external assurance** — provider-backed or otherwise nondeterministic
  evidence that is not part of the ordinary deterministic integration gate.

## Stage model

Every deterministic check belongs to exactly one execution stage.

1. `policy` — cheap structural guards that decide whether later CI execution is
   allowed to proceed.
2. `focused` — cheap deterministic checks suitable for affected-surface
   iteration.
3. `deferred` — broader or materially more expensive deterministic checks that
   should run only after focused checks pass.
4. `exhaustive` — repository-wide/cross-layer acceptance evidence that runs
   last in the deterministic full gate.
5. `external` — operator-triggered/provider-backed assurance outside the normal
   deterministic gate.

The first four stages are ordered. A full gate may not execute a later-stage
check before an earlier-stage check.

## Normative invariants

### CI-P01 — lazy draft execution

Draft pull-request synchronization must not automatically execute an
`exhaustive` full gate. Draft feedback should use affected `focused` checks.
If affected scope is unknown, escalation may run broader deterministic checks,
but the exhaustive repository gate is reserved for a coherent checkpoint or
integration candidate.

### CI-P02 — unconditional final gate

An integration candidate must be eligible for the full deterministic gate
regardless of which repository paths changed. The full-gate pull-request trigger
must therefore not use a fragile path allowlist as authorization to skip the
gate.

### CI-P03 — cheapest stage first

The deterministic full gate executes in non-decreasing stage order:

`policy -> focused -> deferred -> exhaustive`.

A failing earlier stage prevents later expensive stages from consuming runner
time.

### CI-P04 — explicit inventory

Every `validators/validate_*.py` file and every `tests/test_*.py` file must have
an explicit entry in `spec/ci/check-registry-v0.yaml`. Every
`.github/workflows/*.yml` / `.yaml` file must also have an explicit
`workflow_roles` entry declaring role, cost class, and draft behavior so a new
workflow cannot appear outside policy.

Every registered check declares an explicit disposition. A `full_gate` check
must appear in `make harness-check`; a `standalone` check must state why it is
outside the full gate; `unresolved` is intentionally invalid and blocks policy
validation until the check is included, justified as standalone, or removed.
Unregistered validation code is a policy violation rather than silently
becoming optional.

### CI-P05 — explicit cost and ownership of expensive work

Every registered check declares `cost_class` and `stage`. `medium` or `heavy`
checks must include a rationale. The early `policy` and `focused` stages admit
only `cheap` checks; costlier checks belong in `deferred` or `exhaustive`.
Measured cost growth that crosses a cost class boundary requires the registry
to be updated. A focused workflow that is allowed to execute automatically on
draft PRs must itself be `cheap`; costlier focused workflows declare
`draft_behavior: skip` and run only for an integration candidate or explicit
operator action.

Cost classes are intentionally coarse:

- `cheap`: normally below 2 seconds;
- `medium`: normally 2-10 seconds;
- `heavy`: normally above 10 seconds.

Timing is evidence for classification, not a guarantee.

### CI-P06 — unknown impact escalates

Affected-surface selection may only skip a check when its registry metadata
supports that decision. Unknown impact must route to more validation, never
less. Path-based selection can optimize draft feedback; it cannot waive the
final full gate.

### CI-P07 — one event owner per branch commit

A targeted workflow may listen to both `pull_request` and `push` only when its
`push` branch scope cannot overlap ordinary PR branches. Repository convention:
if both are used, `push` is restricted to `main`.

### CI-P08 — external assurance is opt-in

Provider-backed/nondeterministic workflows must remain explicitly
operator-triggered and must not become ordinary `push` or `pull_request`
requirements unless a separate accepted contract changes that boundary.

### CI-P09 — policy guard runs first

`validate_ci_policy.py` is the first command in `make harness-check`. A CI
topology/inventory violation must fail before subsystem, distribution, or
Scenario Suite work begins.

### CI-P10 — policy changes are ratcheted

A change that weakens an invariant, moves a check to an earlier stage, removes a
mandatory check, or broadens automatic heavy execution requires explicit
repository decision/evidence in addition to editing the policy file. A workflow
edit alone is not sufficient authority to weaken this policy.

## Machine-readable application

`spec/ci/check-registry-v0.yaml` is the machine-readable check inventory and
workflow-role declaration.

`checks/validate_ci_policy.py` verifies:

- workflow trigger invariants for `exhaustive`, `focused`, and `external`
  workflow roles;
- full-gate path independence and draft guarding;
- no branch push/PR duplicate ownership for targeted workflows;
- complete validator/test registration;
- explicit disposition of every validator/test and presence of every
  `full_gate` check in `make harness-check`;
- non-decreasing stage order;
- the policy validator itself is the first full-gate command;
- required rationale for medium/heavy checks.

The validator is deliberately conservative. If it cannot classify an execution
path safely, it reports a violation rather than assuming a skip is safe.

## Evolution

The initial policy does not yet implement affected-check routing. It establishes
the guardrail first. A later CI correction may add path/surface selectors to the
registry and use them for draft feedback, while CI-P06 keeps unknown impact
conservative.

The existing `make harness-check` entrypoint remains the compatibility definition
of the full deterministic gate until a separately accepted refactor changes it.
