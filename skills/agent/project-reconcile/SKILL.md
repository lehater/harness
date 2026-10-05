---
name: project-reconcile
description: "Use when an existing Harness project has a usable current Project Publication and a selected Consumer target needs currentness/semantic reconciliation."
---

# Project Reconcile

## Trigger

Use for an existing project after accepted knowledge, acceptance policy or other
currentness inputs changed and the selected Consumer target must be brought as
far as possible toward Semantic Closure.

Do not use this operation to bootstrap an absent/incompatible Harness
realization. That remains `project-bootstrap-reconcile`.

## Inputs

- selected Consumer target;
- current Project Publication and its revision;
- current Project Frontier and Semantic Closure projections, or the inputs needed
  to derive them;
- current Engineering Graph;
- real candidate/source/decision evidence for affected existing providers;
- real caller/admission `acceptance_id` values for attempted admission.

## Procedure

1. Derive or read current Semantic Closure and Project Frontier.
2. Call `plan_reconciliation` against the current publication revision.
3. Reuse `unchanged` CURRENT capabilities; do not re-admit them.
4. For affected existing providers with complete supplied inputs, call bounded
   `execute_reconciliation`.
5. Continue across independent branches so one failing capability does not hide
   other independently discoverable failures.
6. Never synthesize an acceptance identity, semantic evidence, Authority
   decision, provider or Engineering Graph topology. Surface the missing input
   or external action instead.
7. Keep intermediate semantic/lifecycle changes non-current.
8. Publish only when final Semantic Closure is COMPLETE and no blockers,
   validation failures, gaps, waiting work or external actions remain. Use one
   CAS-bound Project Publication transition.
9. On retry, use a plan bound to the same current revision. If the publication
   changed, re-plan rather than applying stale continuation state.

## Output

A `harness-reconciliation-result` exposing:

- structural and semantic closure separately;
- affected, unchanged and completed capabilities;
- the aggregated blocker/failure/waiting frontier;
- the revision-bound continuation token;
- one final Project Publication only when reconciliation reaches COMPLETE.

## Stop conditions

Stop automatic execution and surface the owning next action when:

- no usable current Project Publication exists;
- a provider must be created or provider selection/topology must change;
- required candidate/source/decision evidence is absent;
- an `acceptance_id` is absent;
- Authority or semantic judgement is required;
- the current publication revision no longer matches the plan/CAS expectation.

Reconciliation automates mechanics, not authority.
