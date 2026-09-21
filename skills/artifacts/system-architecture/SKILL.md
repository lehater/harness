---
name: system-architecture
description: "Use for actionable CREATE work requiring accepted system/application architecture. Define structural/runtime boundaries, dependency and consistency rules from accepted upstream semantics without inventing product/domain behavior or prematurely owning interface/persistence details."
---

# System Architecture

## Trigger

Use when grouped actionable CREATE work has `knowledge_kind:
system-architecture` or otherwise requires structural/runtime architecture owned
by the System Architecture Authority.

## Inputs

- actionable grouped artifact work and System Architecture Authority;
- accepted Product Requirements;
- accepted Domain/Application semantics when applicable;
- accepted quality/security constraints that already exist.

## Read boundary

Read only canonical upstream knowledge needed to decide:

- system/runtime structure;
- application/module boundaries;
- dependency and interaction rules;
- consistency/transaction boundaries;
- cross-owner resolution/orchestration constraints.

Do not mine implementation code as a substitute for accepted architecture.

## Procedure

1. Confirm the work is CREATE and upstream semantic requirements are satisfied.
2. Preserve product/domain ownership rather than restating it as architecture.
3. Select the smallest structural/runtime model capable of realizing accepted
   behavior.
4. Define component/module/application boundaries and allowed dependency
   directions.
5. Define interaction and consistency rules where cross-boundary behavior matters.
6. Define explicit architectural non-goals to prevent accidental complexity.
7. Keep transport, UI and physical persistence details downstream unless they are
   architecture-significant constraints.
8. If a required product/domain/quality fact is unknown, create/route a Question
   upstream rather than inventing it.
9. Produce the target repository's canonical architecture artifact(s).
10. Apply semantic acceptance, register the provided capabilities and reevaluate.

## Stop conditions

Stop when:

- Architecture Driver Closure is incomplete or contains an unresolved material Question;\n- architecture depends on an unresolved product/domain decision;
- a numeric quality target is required but not accepted;
- two accepted upstream contracts demand incompatible structural guarantees;
- the proposed architecture would silently change accepted observable behavior.

## Output contract

Prefer project-native architecture artifacts. No universal architecture schema is
required in v0.

Useful knowledge may include:

- structural/runtime topology;
- module/application boundaries;
- dependency rules;
- consistency/transaction rules;
- orchestration responsibilities;
- explicit non-goals/evolution constraints.

## Acceptance checks

- Architecture Driver Closure is complete for the selected scope;\n- every structural choice traces to accepted upstream needs;\n- every material complexity increase has explicit upstream justification;
- no downstream interface/storage detail is promoted without architectural need;
- no product/domain truth is re-owned;
- dependency/consistency rules are explicit where implementation could otherwise
  invent them;
- unresolved upstream semantics remain Questions.

## Registration

Register accepted project-native architecture artifact(s) under the System
Architecture Authority and provide all grouped capabilities actually satisfied.

Dependencies include only canonical upstream artifacts relied upon.

## Human projection

Project-native architecture documentation is normally sufficient; generated views
may remain disposable projections.
