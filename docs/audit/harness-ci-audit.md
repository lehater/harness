# Harness CI Audit

Status: correction implemented and policy-validated on the audit branch; no integration to `main`.

Date: 2026-10-01
Branch: `audit/harness-corrections`
Scope: all GitHub Actions workflows and the aggregate validation path reachable from them.

## Objective

Minimize CI work without weakening the final integration invariant:

1. run the cheapest deterministic checks first;
2. run only checks justified by the changed surface during iteration;
3. defer broad cross-layer and distribution checks until cheaper checks pass;
4. execute the exhaustive gate only for a coherent candidate;
5. keep external/nondeterministic assurance explicitly opt-in.

The final candidate remains exhaustive. "Lazy" means delaying work until it can
change the current decision, not removing acceptance evidence.

## Current CI topology

| Workflow | Trigger | Responsibility | Observed cost | Audit result |
|---|---|---|---:|---|
| `harness.yml` | `workflow_dispatch`, push to `main`, path-filtered `pull_request` | Full repository gate via `make harness-check` plus one greenfield frontier evaluation | successful run #973: 50 s job / 42 s aggregate validation | Main cost center; currently eager on every matching PR commit |
| `greenfield-engineering-graph.yml` | path-filtered `push` and `pull_request` | Targeted greenfield graph/routing integration evidence | historical runs typically 8-15 s | Useful targeted check, but push + PR can duplicate one branch commit |
| `live-calibration-copilot.yml` | `workflow_dispatch` only | Provider-backed live calibration evidence | bounded by 10 min timeout; installs Node/Copilot CLI and invokes provider | Correctly lazy already; keep outside normal PR gate |

## Cost decomposition

Reference: successful `harness core` run #973 on this audit branch.

- checkout: about 1 s;
- Python setup: about 1 s;
- dependency install: about 3 s;
- `make harness-check`: about 42 s;
- extra greenfield frontier evaluation: below 1 s.

The optimization target is therefore the validation graph, not runner setup.

The aggregate target launches 62 validator scripts sequentially. Approximate
dominant durations from the job log:

| Validator | Time | Share of aggregate |
|---|---:|---:|
| `validators/validate_scenario_suite.py` | 27.17 s | ~65% |
| `validators/validate_consumer_wrapper.py` | 3.25 s | ~8% |
| `validators/validate_consumer_pack.py` | 2.83 s | ~7% |
| all remaining 59 validators | ~8.6 s | ~20% |

The Scenario Suite currently runs all 78 scenario YAML files sequentially. Its
CLI has no scenario/requirement/execution-type selector, so a local change to one
bounded surface still pays the full suite cost when `harness-check` runs.

## Findings

### HARN-H03 — incomplete CI path coverage (P1)

The main PR workflow manually enumerates runtime Python files. The repository
currently has 53 top-level Python modules; 25 are not in the workflow allowlist,
including `decision_pipeline.py`, `consumer_pack.py`, `method_router.py`,
`project_status.py`, `repository_realization.py`, `source_boundary.py`,
`source_coverage.py`, and `skill_router.py`.

Consequence: optimization based on the current allowlist is unsafe because a
material runtime change may skip PR validation completely.

Correction principle: final-candidate CI should not depend on a manually
maintained module allowlist. Prefer an unconditional final gate after the PR is
ready, or a broad stable surface matcher rather than per-module enumeration.

### HARN-H04 — aggregate validation has no explicit inventory/tiering (P2)

There are 63 `validators/validate_*.py` scripts, while `make harness-check`
invokes 62. `validators/validate_harness.py` is omitted. The repository also
contains `tests/test_lifecycle_experiment.py`, which is outside the aggregate
gate.

The problem is not merely one missing script. The Makefile is simultaneously:

- the validator inventory;
- the execution order;
- the full-gate definition.

That makes omission easy and prevents reliable selection of affected checks.

Correction principle: make check inventory and execution tiers explicit, while
preserving `make harness-check` as the exhaustive compatibility entrypoint.

### HARN-H05 — full gate is eager during draft iteration (P2)

`harness.yml` executes the exhaustive gate on every matching
`pull_request.synchronize`, including draft PRs. This conflicts with
`AGENTS.md`, which says commits/CI are checkpoints rather than per-file
feedback and reserves the full PR gate for coherent checkpoints/final
candidates.

Snapshot during AUD-008: the current draft branch produced 27 `harness core`
runs, 26 completed, consuming about 22.2 runner-minutes. Successful runs average
roughly one minute.

The targeted greenfield workflow also subscribes to both unrestricted `push`
and `pull_request`. When its paths change on a branch with an open PR, the same
commit can be evaluated twice.

Correction principle: separate iteration feedback from final integration
assurance and make every expensive layer have one trigger owner.

## Recommended execution model

### Tier 1 — focused iteration checks

Purpose: fast feedback while a PR is draft.

Inputs: changed files / explicitly selected Harness surface.

Output: only deterministic checks whose owned contract can be affected.

Target: normally below 10-15 seconds and no full Scenario Suite.

Initial implementation should stay conservative. Do not build a complex
dependency engine first; start with a small explicit check registry and fall
back to the full gate when impact is unknown.

### Tier 2 — deferred integration checks

Purpose: validate expensive packaging/distribution or cross-surface contracts
after Tier 1 passes.

First candidates:

- `validate_consumer_pack.py`;
- `validate_consumer_wrapper.py`.

These two account for about six seconds and are especially valuable when
distribution, skill registries, wrapper/bootstrap, or pack manifests change.

Unknown impact must fail toward running the checks, not skipping them.

### Tier 3 — exhaustive Scenario Suite

Purpose: cross-layer behavioral acceptance.

Input: coherent candidate after cheap checks pass.

Output: full 78-scenario coverage and benchmark result.

Run last because it dominates the current gate (~27 s). Prefer serial
dependency ordering over parallel fan-out: parallelism can reduce wall-clock
time but spends runner capacity on expensive work even when an earlier cheap
check would have failed.

### Tier 4 — provider-backed live assurance

Purpose: nondeterministic/provider-backed calibration evidence.

Current implementation is already correct: manual `workflow_dispatch`, its own
workflow, explicit timeout and artifact retention. Do not move it into the
ordinary PR gate.

## Minimal correction sequence

### Step 1 — fix trigger ownership

1. Keep the exhaustive `harness core` gate for:
   - push to `main`;
   - manual dispatch;
   - non-draft/ready-for-review PR candidates.
2. Do not execute the exhaustive gate for every draft synchronization.
3. Restrict greenfield `push` execution to `main`; PR branches use the
   `pull_request` trigger.
4. Preserve live calibration as manual-only.

Expected value: eliminates the largest class of unnecessary runs without
changing validator semantics.

### Step 2 — remove fragile final-gate path enumeration

For the final candidate, prefer running the full gate regardless of which files
changed once the PR becomes ready. This removes the HARN-H03 false-negative
class and makes the final invariant simple:

```text
ready candidate -> exhaustive deterministic gate -> integration eligibility
```

Path selectivity belongs primarily to draft/focused feedback, where skipping a
check cannot silently authorize integration.

### Step 3 — split the aggregate target by cost/responsibility

Keep `make harness-check` as the full public target, but compose it from named
subtargets, for example:

```text
harness-check
  -> harness-check-fast
  -> harness-check-distribution
  -> harness-check-scenarios
```

The exact membership must follow ownership/evidence, not timing alone.

### Step 4 — add explicit check inventory and Scenario Suite selectors

Only after the three-tier split proves useful:

- declare validator/check id;
- owner surface / affected paths;
- cost tier;
- whether it is mandatory in the exhaustive gate;
- optional Scenario Suite filters by scenario id, requirement or behavior class.

This enables safe affected-check selection and closes the structural part of
HARN-H04. It should be introduced incrementally; a full dependency solver is
not justified yet.

## Correction outcome

Implemented after the audit under the canonical CI policy:

- `docs/design/ci-execution-policy-v0.md` defines the execution invariants;
- `spec/ci/check-registry-v0.yaml` inventories every validator/test and every workflow role;
- `validators/validate_ci_policy.py` is the first full-gate command and rejects unregistered checks/workflows, early expensive checks, path-filtered final gates, draft exhaustive execution, stage-order regressions and overlapping branch event ownership;
- `harness.yml` has no PR path allowlist and gates its exhaustive job on a non-draft PR;
- `greenfield-engineering-graph.yml` restricts `push` to `main`;
- `ci-policy.yml` gives draft CI edits a cheap automatic guard;
- `validate_harness.py` and `tests/test_lifecycle_experiment.py` are now explicit full-gate checks;
- `make harness-check` is ordered `policy -> focused -> deferred -> exhaustive`, with the ~27 s Scenario Suite in the last stage.

Initial correction commit `d486066c2b286db0a5c3538ee37a195e1f71da27` made the exhaustive Harness job skip drafts and passed CI policy. A follow-up observation showed that GitHub `pull_request.paths` uses the cumulative PR diff, so the Greenfield workflow still launched on later unrelated draft commits. The same HARN-H05 execution-policy root cause was tightened by draft-gating non-cheap focused workflows.

Final draft verification on `bd760921e96073b8f4164e5e2afd95447ab927d2`:

- `harness core` run 36868615767: job **skipped**;
- `Greenfield Engineering Graph` run 36868615957: job **skipped**;
- `CI policy` run 36868615780: **passed**.

Thus relevant draft CI edits retain one cheap automatic policy guard while non-cheap deterministic work is deferred.

The branch remains draft. Full repository validation is intentionally deferred until a coherent integration candidate; unrelated functional finding HARN-009 remains open and is not altered by this CI correction.

## What should not be optimized first

- PyYAML installation: about 3 seconds, small compared with the Scenario Suite.
- The extra greenfield `engineering_graph.py evaluate` in `harness.yml`:
  below one second in the measured run.
- Parallelizing all validators: lowers latency but increases wasted compute on
  failing candidates and works against the requested lazy-test principle.
- Adding a Python-version matrix: increases cost unless a concrete compatibility
  contract requires it.
- Removing project-specific greenfield assertions solely because generic router
  validators exist: overlap is visible, but equivalence must be proven before
  deleting integration evidence.

## Acceptance criteria for a CI correction

1. Draft commits do not automatically start the exhaustive Scenario Suite.
2. A ready/final candidate still executes every required deterministic
   validator and the complete Scenario Suite.
3. Changes to any runtime Python module cannot silently bypass the final gate.
4. No matching greenfield branch commit runs both push and PR copies of the same
   workflow.
5. `validate_harness.py` and the lifecycle unittest have an explicit
   disposition: included in a gate or deliberately retired/replaced.
6. Unknown impact routes to more validation, never less.
7. Live provider calibration remains opt-in and cannot block ordinary PRs.
8. Full validation is green before any integration to `main`.

## Decision

Do not optimize by deleting tests first.

The first correction should be execution-policy refactoring: stop running the
full gate on every draft commit, remove duplicate event ownership, and move the
dominant Scenario Suite to the latest deterministic stage. Only then use
measured evidence to decide whether individual assertions are redundant.
