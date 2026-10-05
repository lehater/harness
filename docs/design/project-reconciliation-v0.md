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

## Bounded execution

`harness.application.reconciliation.execute_reconciliation` processes the
planned affected set in dependency order while continuing across independent
branches. It reuses the current Project Publication as the immutable base and
keeps all intermediate evaluation/lifecycle updates non-current.

The v0 executor is deliberately narrow:

- it may re/admit only providers already present in the Core model;
- callers must supply real `sources`, `candidate` and `acceptance_id` inputs;
- it does not create canonical artifacts or change Engineering Graph topology;
- it does not invent Authority decisions, semantic evidence or acceptance ids;
- independent validation failures are aggregated in one result;
- dependent work waits when an affected prerequisite did not complete;
- no durable workflow/continuation state is created.

`prepare_reconciliation_publication` is the batch publication primitive. The
executor invokes it only after final Semantic Closure is COMPLETE and no
blockers, failures, gaps or external actions remain. It validates all completed
Capability outcomes against one final snapshot and creates at most one child
revision of the original current publication. It never chains hidden
per-Capability publications.

A retry recomputes/uses a plan bound to the same publication revision. The
optional supplied resume token must match that plan. If the current publication
changed, CAS/plan validation rejects the stale continuation and the caller must
re-plan.

## Completion UX

Consumer-facing reconciliation output must keep these independent facts visible:

- `closure.structural`;
- `closure.semantic`;
- affected/stale work;
- decision/semantic blockers;
- final publication revision when complete.

Structural COMPLETE therefore remains structural completeness and cannot be
mistaken for semantic closure.


## Consumer operation

The public routed operation is `project-reconcile`. It applies to an existing,
usable Project Publication and a selected Consumer target. Startup,
compatibility/bootstrap repair remains owned by `project-bootstrap-reconcile`;
provider creation or topology changes remain in their existing production and
decision procedures rather than being absorbed into reconciliation.
