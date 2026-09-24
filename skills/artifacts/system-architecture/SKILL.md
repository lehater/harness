---
name: system-architecture
description: "Use for actionable CREATE work requiring accepted system/application architecture. Define structural/runtime boundaries and dependency topology from accepted upstream semantics without inventing product/domain behavior or prematurely owning interface/persistence details."
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
- accepted quality/security/operability constraints that already exist;
- Architecture Driver Closure for the selected scope, derived from accepted upstream knowledge.

## Read boundary

Read only canonical upstream knowledge needed to decide:

- system/runtime structure;
- application/module boundaries;
- dependency and interaction rules;
- cross-owner resolution/orchestration constraints;
- architecture-driving scale/runtime facts whose plausible alternatives could change topology.

Do not mine implementation code as a substitute for accepted architecture.

## Architecture-driver closure

Before choosing topology, classify the architecture-driving input concerns defined by
`architecture-driver-closure/v1`. Derive answers from accepted upstream knowledge.
Do not interpret silence as `NOT_APPLICABLE`.

If a plausible answer to an unknown could materially change execution mode, runtime
topology, deployment, persistence, integration or trust boundaries,
route a Question to the owning upstream Authority and stop. Ask only unresolved
material questions; do not force a universal NFR questionnaire.

## Procedure

1. Confirm the work is CREATE and upstream semantic requirements are satisfied.
2. Establish Architecture Driver Closure for the selected scope.
3. Preserve product/domain ownership rather than restating it as architecture.
4. Derive material architectural drivers and risks from accepted upstream truth.
5. Select the smallest structural/runtime model capable of satisfying all accepted drivers.
6. Justify every material increase in runtime, deployment, coordination or operational complexity with an accepted driver, constraint or material risk.
7. Compare materially different candidates only when uncertainty/risk makes the choice consequential; do not perform heavyweight trade-off analysis for a trivially sufficient topology.
8. Define component/module/application boundaries and allowed dependency directions.
9. Define technical interaction topology where cross-boundary behavior matters. Route material ordering, isolation, atomicity, conflict, retry/idempotency or consistency semantics to CONCURRENCY-CONSISTENCY-DESIGN.
10. Define explicit architectural non-goals and reopening conditions.
11. Keep transport, UI and physical persistence details downstream unless they are architecture-significant constraints.
12. Produce the target repository's canonical architecture artifact(s).
13. Apply semantic acceptance, register the provided capabilities and reevaluate.

## Stop conditions

Stop when:

- Architecture Driver Closure is incomplete or contains an unresolved material Question;
- architecture depends on an unresolved product/domain/quality/security/operability decision;
- a numeric quality target is required but not accepted;
- two accepted upstream contracts demand incompatible structural guarantees;
- the proposed architecture would silently change accepted observable behavior.

## Output contract

Prefer project-native architecture artifacts. No universal architecture schema is
required in v0.

Useful knowledge may include:

- structural/runtime topology;
- architecture drivers and their canonical sources;
- material candidate/trade-off rationale where needed;
- module/application boundaries;
- dependency rules;
- orchestration responsibilities;
- explicit non-goals/evolution/reopening constraints.

## Acceptance checks

- Architecture Driver Closure is complete for the selected scope;
- every structural choice traces to accepted upstream needs;
- every material complexity increase has explicit upstream justification;
- a materially simpler satisfying topology is not rejected without an explicit trade-off;
- no downstream interface/storage detail is promoted without architectural need;
- no product/domain truth is re-owned;
- dependency topology is explicit where implementation could otherwise invent it;
- material concurrent-state correctness semantics are routed to CONCURRENCY-CONSISTENCY-DESIGN rather than owned here;
- unresolved upstream semantics remain Questions.

## Registration

Register accepted project-native architecture artifact(s) under the System
Architecture Authority and provide all grouped capabilities actually satisfied.

Dependencies include only canonical upstream artifacts relied upon.

## Human projection

Project-native architecture documentation is normally sufficient; generated views
may remain disposable projections.
