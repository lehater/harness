# Harness repository agent map

## Purpose

This repository owns reusable methodology and generic Skills for AI-assisted engineering across multiple target repositories.

Harness owns **how work is performed**. A target project owns **what is true, what is active, and what is authorized**.

Do not move product/domain truth, project-specific architecture, active project state, project-local gates or implementation authorization into this repository.

## Task-first startup

For Harness repository work:
1. read this file;
2. read only the methodology/Skill files required by the explicit task;
3. load `docs/plans/active/README.md` only when continuing development of this Harness repository.

When a user asks to use this Harness while working on another repository, treat the two repositories independently:
- read the smallest relevant Harness method/Skill;
- read the target project's own instructions and canonical artifacts required by the task;
- load target-project active state only when current execution, lifecycle/gate state or authorization matters.

No manifest, pin, submodule or repository-to-repository binding is required.

## Task precedence

The explicit user request selects the target project, task, scope and desired output. Harness methodology and target-project truth constrain execution; they must not redirect an unrelated request into an active plan.

A Skill or protocol may broaden context, reroute work or stop execution only for a concrete target-project invariant, blocking unknown/conflict, or dependency of the requested task.

## Source map

- `docs/methodology/core/` — repository-independent working/decision/knowledge protocols.
- `docs/methodology/software-product/` — reusable software-product lifecycle methodology.
- `docs/methodology/ddd/` — reusable Strategic/Tactical DDD methodology.
- `skills/` — reusable judgement-heavy workflows.
- `validators/` and `evals/` — generic deterministic checks/evaluation machinery when implemented.
- `templates/` — optional examples/bootstrap material when useful.
- `docs/plans/active/` — execution state for development of this Harness repository itself.

## Change discipline

- do not commit directly to `main`;
- work on a branch;
- use one coherent change per PR;
- integrate through squash merge.

## Design rules

- Keep target projects independent from Harness implementation details.
- Generic methodology must not mention a specific product except as an explicit example.
- Project-specific rules, truth and durable state stay in the project repository.
- Progressive disclosure is the default: load the smallest relevant method/Skill/context.
- Shared policy has one canonical owner; Skills reference it instead of restating its state machine.
- Orchestration Skills coordinate; they do not duplicate lifecycle, decision or implementation methodologies.
- Validators enforce deterministic ownership/schema/reference invariants rather than synchronized policy prose.
- Static routing-corpus validation is not evidence that a model routed correctly; observed model-routing evaluation is separate.
- Measure context overhead before adding scaffolding.
- Do not turn methodology into a workflow engine without demonstrated need.

## Repository workflow

- Never push or commit changes directly to `main`.
- Every task is implemented on a dedicated non-main branch.
- Run validation and tests on that branch before integration.
- Integrate completed work into `main` only through a pull request using squash merge.
- Treat `main` as the reviewed, integrated baseline, not as a working branch.
