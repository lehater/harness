# Harness repository agent map

## Purpose

This repository owns reusable methodology and execution support for AI-assisted engineering across multiple target repositories.

Harness owns **how work is performed**. Each target project owns **what is true, what is active, and what is authorized**.

Do not move product/domain truth, project-specific architecture, active project state, project-local gates, or implementation authorization into this repository.

## Task-first startup

For non-trivial work:
1. read this file;
2. read the nearest scoped `AGENTS.md` if one exists;
3. load only the methodology/Skill/contract files required by the explicit task;
4. load `docs/plans/active/README.md` only when continuing Harness repository work.

When working **through Harness on a target project**, recover target-project state from that target repository only when the requested task depends on current execution, gate or authorization state. Do not inherit a target project's active workstream merely because one exists, and do not treat Harness conversation history as project state.

## Task precedence

The explicit user request selects the target project, task, scope and desired output. Harness methodology and target-project truth constrain how that task is performed; they must not redirect an unrelated request into an active plan.

A Skill or protocol may broaden context, reroute work or stop execution only for a concrete target-project invariant, blocking unknown/conflict, or dependency of the requested task. Make that reason explicit rather than following workflow prose mechanically.

## Source map

- `docs/methodology/` — reusable operating model and protocols.
- `skills/` — reusable judgement-heavy workflows.
- `contracts/` — target-project integration contracts and schemas.
- `validators/` — deterministic Harness/project-contract checks.
- `evals/` — routing and methodology evaluation corpora/tools.
- `runtime/` — project resolution, loading and switching mechanics when implemented.
- `templates/` — bootstrap material for target repositories.
- `docs/plans/active/` — execution state for development of this Harness repository itself.

## Change discipline

The bootstrap commit is the only intentional direct initialization of `main`.

From now on:
- do not commit directly to `main`;
- work on a branch;
- use one coherent change per PR;
- keep accumulating PRs draft until ready for the final gate;
- integrate through squash merge.

## Design rules

- Prefer a thin project-local binding over copied generic methodology.
- A target project must remain the durable source of its own truth and execution state.
- Generic methodology must not mention a specific product unless used as an explicit example.
- Project-specific extensions may refine Harness behavior but must not silently fork generic rules.
- Progressive disclosure is the default: load the smallest relevant method/Skill/context; do not preload lifecycle or active-plan state for unrelated work.
- Shared policy has one canonical owner. Routing maps and Skills reference it instead of restating its state machine.
- Orchestration Skills coordinate; they do not become duplicate lifecycle, decision or implementation methodologies.
- Validators enforce deterministic ownership/schema/reference invariants, not synchronized copies of policy prose.
- Static routing-corpus validation is not evidence that a model routed correctly; observed model-routing evaluation is separate.
- Measure context overhead before adding scaffolding. Useful signals include files read, Skills loaded, tool calls before first useful action and premature stops.
- Keep runtime orchestration small; do not turn methodology into a workflow engine without demonstrated need.
- Validators enforce deterministic invariants; Skills carry judgement-heavy reusable guidance.

## Current compatibility principle

A project should be reproducible from:

```text
target repository state + pinned Harness revision
```

The exact loading mechanism (launcher, sibling checkout, submodule, or another binding) is an architecture decision to settle before migrating NAPMS off its repository-local Harness.
