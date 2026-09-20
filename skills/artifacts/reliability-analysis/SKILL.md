---
name: reliability-analysis
description: "Use before implementation when failure paths can make retry, timeout, cancellation, duplicate execution, degradation, overload or recovery semantics material. Analyze coverage and route gaps to their semantic owners without becoming a Reliability design authority."
---

# Reliability Analysis

## Trigger

Use when the selected implementation scope contains state-changing operations, external dependencies, asynchronous delivery, partial-failure boundaries, cancellation/deadline behavior, overload/resource pressure, degradation or recovery whose semantics must be closed before coding.

Do not instantiate a RELIABILITY-DESIGN Authority merely because this skill is used.

## Inputs

- selected implementation scope;
- accepted Product/Domain/Application/System Architecture/Interface/Data/Quality knowledge applicable to that scope;
- Security and Operability constraints when applicable;
- accepted dependency and delivery guarantees;
- Verification/Test knowledge when already available.

## Read boundary

Accepted design is authority. Production code, framework defaults, SDK retry behavior, broker defaults and infrastructure settings do not prove accepted reliability semantics.

External reliability guidance and patterns are coverage lenses, not project requirements.

## Procedure

1. Enumerate every state-changing operation, external dependency and asynchronous boundary in scope.
2. Identify the authoritative state/effect for each.
3. Enumerate material interruption points: before effect, during effect, after effect before acknowledgement, duplicate attempt/delivery, cancellation, dependency failure, partial failure and overload.
4. For each interruption point identify what the caller/consumer can actually know. Do not equate timeout or lost acknowledgement with confirmed failure.
5. Determine the permitted continuation from accepted knowledge: stop, retry, reconcile, compensate, degrade, reject or wait.
6. Route ownership to the Authority that owns the affected outcome, state or runtime boundary. Reliability terminology does not transfer semantic ownership.
7. Record one coverage state per material concern:
   - COVERED;
   - NOT_APPLICABLE;
   - DEFERRED_NONBLOCKING with an explicit reopening condition;
   - QUESTION.
8. Route every QUESTION to its semantic owner. Never select missing retryability, idempotency, fallback, ordering, cancellation, recovery or overload semantics inside this analysis.
9. Derive Verification/Test obligations from accepted failure/recovery outcomes.
10. Derive Operability evidence requirements from accepted failure/recovery states without redefining them.
11. Reevaluate implementation closure. Applicable material Questions block dependent implementation.

## Ownership routing

Typical routing, subject to project semantics:

- duplicate business effect, state-transition validity, compensation meaning -> Product/Domain;
- orchestration continuation, command identity, reconciliation workflow -> Application;
- timeout/deadline budgets, availability/recovery/capacity targets -> Quality/Product;
- dependency topology, retry-responsibility placement, circuit breaking, bulkheads, load shedding, queue/admission structure -> System Architecture;
- public idempotency keys, retryable status, overload/degraded representation, event metadata -> Interface;
- durable uniqueness, atomic persistence, deduplication representation -> Data;
- runtime evidence for retries/timeouts/stuck recovery -> Operability;
- executable proof -> Verification/Test.

If the actual accepted semantics place a decision elsewhere, route to that owner instead of following this list mechanically.

## Stop conditions

Create/route a blocking Question when implementation would otherwise have to decide any material case such as:

- whether a state-changing operation may be repeated after uncertain completion;
- whether duplicate attempts may produce duplicate semantic effects;
- what timeout/cancellation means for already-started or committed work;
- how an ambiguous commit/delivery is reconciled;
- whether stale/partial/fallback output is an accepted result;
- whether failure is fail-open/fail-closed when not already decided upstream;
- ordering/reordering semantics;
- poison-work/replay semantics;
- overload behavior where reject/queue/drop/degrade changes accepted behavior;
- recovery needed to preserve authoritative state/invariants.

## Implementation freedoms

Leave mechanics to implementation when changing them cannot alter accepted semantics, state safety, architecture boundaries, quality constraints or evidence obligations.

Typical freedoms include:

- concrete resilience library;
- private exception/helper structure;
- backoff/jitter algorithm and retry count inside accepted retry/capacity/deadline constraints;
- circuit-breaker internal state representation after placement/admission semantics are accepted;
- cancellation primitive after cancellation semantics are accepted;
- internal metric/log names after Operability requirements are accepted.

## Output contract

Produce the smallest project-native reliability coverage artifact or review result containing:

- scope and analyzed boundaries;
- failure-path concern;
- applicability;
- semantic owner;
- accepted source or missing decision;
- coverage state;
- reopening condition for deferred concerns;
- blocking Questions;
- implementation freedoms;
- Verification/Test obligations;
- Operability evidence obligations.

The analysis artifact is not required to become a Capability merely because the skill ran. Register it only when a concrete project consumer needs independently accepted reliability-coverage knowledge.

## Acceptance checks

- every material state-changing/external/asynchronous boundary was considered;
- timeout/lost acknowledgement is not silently treated as confirmed failure;
- retryability is derived from accepted semantics rather than framework defaults;
- transport delivery guarantee is distinguished from semantic effect guarantee;
- fallback/degradation is accepted upstream when externally observable;
- retry/load mechanisms cannot create unbounded amplification against accepted capacity constraints;
- analysis does not become a second owner of Product/Domain/Application/System/Interface/Data/Quality semantics;
- every material gap is routed as a Question;
- implementation freedoms are explicit enough that coding agents can proceed without inventing reliability semantics.

## Registration

This is an analysis skill, not evidence for a RELIABILITY-DESIGN Authority.

If a project later demonstrates an independently valuable reliability-analysis Capability with a stable public consumer contract, evaluate that proposal separately with the Authority atomicity test. Do not infer it from this skill alone.


## Human projection

Prefer the smallest project-native coverage/contract view that shows scope, accepted decisions, routed gaps, evidence obligations and implementation freedoms.
