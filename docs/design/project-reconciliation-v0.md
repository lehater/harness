# Project Reconciliation v0

Status: experimental.

## Purpose

Define one bounded Application operation for bringing a selected Consumer target
from the current Project Publication toward semantic closure while preserving
the existing semantic owners.

Reconciliation owns **mechanics**, not engineering meaning.

## Ownership

Reconciliation may coordinate:

- target dependency ordering;
- lifecycle/currentness and acceptance-policy comparison;
- cheap deterministic Decision Preflight;
- reuse of unaffected CURRENT capabilities;
- aggregation of independent blockers;
- semantic-admission invocation when complete evidence and a real acceptance
  identity are supplied;
- assembly of one coherent next Project Publication;
- final Semantic Closure evaluation.

It does not own:

- Authority decisions;
- candidate semantics;
- semantic evidence or acceptance rationale;
- acceptance identity generation;
- lifecycle truth separate from accepted admission;
- another current-publication store.

Project Publication remains the only atomic/CAS current-state boundary.

## Planning

`harness.application.reconciliation.plan_reconciliation` is the first bounded
read model. It consumes the current publication revision plus existing Project
Frontier and Semantic Closure projections and returns:

- structural and semantic closure status separately;
- CURRENT capabilities that can be reused unchanged;
- the whole currently known affected/stale target set in dependency order;
- all currently known independent blockers/failures/gaps;
- a deterministic continuation token bound to the current publication and plan.

The planner uses `Semantic Closure.currentness_gaps`, not only the first
lifecycle READY item. This is deliberate: a policy or upstream acceptance
change can make a whole downstream closure stale even when only its first item
is immediately executable.

The plan is disposable. Recomputing it from the same publication and inputs
produces the same continuation token.

## Continuation contract

The continuation token is not an acceptance identity and is not persisted as
semantic truth. A resume attempt must recompute the plan against the current
publication. If publication revision or relevant plan inputs changed, the token
changes and the caller must use the new plan instead of applying stale work.

This provides bounded restartability without a workflow engine or second source
of truth.

## Execution direction

A later execution slice may process deterministic work in plan order, stopping
only where candidate/evidence/Authority input is required. Intermediate results
remain non-current. Publication occurs once after a coherent final state has
been assembled and validated against the original current revision.

No executor may synthesize `acceptance_id`; successful re-admission must carry
a real caller/admission identity.

## Completion UX

Consumer-facing reconciliation output must keep these independent facts visible:

- `closure.structural`;
- `closure.semantic`;
- affected/stale work;
- decision/semantic blockers;
- final publication revision when complete.

Structural COMPLETE therefore remains structural completeness and cannot be
mistaken for semantic closure.
