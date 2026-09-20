---
name: concurrency-consistency-analysis
description: "Use when overlap, reordering, stale visibility, shared mutable state, asynchronous delivery or bounded-capacity pressure can change correctness or an accepted outcome before implementation."
---

# Concurrency Consistency Analysis

## Trigger

Use for implementation scope containing shared mutable state, competing writers, coherent multi-read requirements, async/event delivery, ordering-sensitive operations, cross-boundary convergence, queues, shared capacity, admission or backpressure.

## Inputs

Accepted Product, Domain, Application, System, Interface, Data and Quality knowledge for the selected scope; Security and Operability where applicable.

## Read boundary

Accepted design is authority. Production code, database isolation defaults, ORM behavior, broker delivery defaults, thread models and framework retry behavior are not proof of intended semantics.

## Procedure

1. Enumerate state-changing operations, coherent reads, shared resources, async boundaries and bounded-capacity dependencies.
2. Generate applicable overlap, duplicate, reordering, stale-read, partial-progress and saturation scenarios.
3. Identify authoritative state/invariant for each scenario.
4. Identify the Authority owning that state/invariant/outcome.
5. State required atomicity, observation, ordering, conflict and continuation semantics.
6. State capacity-pressure behavior where it can be externally meaningful.
7. Classify COVERED, NOT_APPLICABLE, DEFERRED_NONBLOCKING or QUESTION.
8. Route Questions; do not repair missing semantics in this analysis.
9. Only after closure identify implementation freedoms for locking, isolation, versioning, queueing, partitioning and admission.
10. Derive Verification/Test obligations for races, reordering, duplicates, stale visibility and overload.
11. Derive Operability evidence for conflict rate, serialization failure, lag, queue depth, saturation, shedding and recovery as applicable.

## Ownership routing

- competing business effects, merge/win/reject validity, invariant -> Domain/Application;
- transaction/use-case atomicity and continuation -> Application;
- public conflict/version/order/overload representation -> Interface;
- physical uniqueness, isolation, locking/version representation -> Data;
- partition, queue, admission, isolation and coordination topology -> System Architecture;
- staleness/latency/capacity/headroom targets -> Quality;
- externally meaningful degradation/priority/fairness -> Product/Application;
- runtime evidence -> Operability;
- race/reorder/overload proof -> Verification/Test.

## Stop conditions

Create a blocking Question if implementation would otherwise choose material:
- lost-update behavior;
- conflict winner/rejection/merge;
- atomicity boundary;
- coherent snapshot requirement;
- tolerated stale observation;
- authoritative operation/event ordering;
- duplicate/reordered delivery effect;
- convergence/reconciliation rule;
- reject/wait/queue/drop/degrade behavior;
- priority/fairness under shared capacity.

## Implementation freedoms

After semantic closure, implementation may choose mechanism details that cannot change accepted outcomes, including lock/token form, database isolation satisfying the contract, retry-loop mechanics where retry is authorized, queue/broker library, pool/semaphore implementation, partition function and telemetry names.

## Output contract

Produce the smallest project-native coverage artifact/review containing:
- scope;
- scenario/concern;
- authoritative state/invariant;
- owner;
- required semantic behavior;
- accepted source or missing decision;
- state;
- reopening condition for deferred items;
- blocking Questions;
- implementation freedoms;
- Verification/Test obligations;
- Operability obligations.

The analysis artifact is not automatically a Capability.

## Registration

This skill is evidence against creating a generic CONCURRENCY-DESIGN/CONSISTENCY-DESIGN/ORDERING-DESIGN/BACKPRESSURE-DESIGN Authority from the currently demonstrated semantics. Any future independently owned decision boundary requires a new atomicity test.


## Acceptance checks

- every material concern traces to accepted scope and an owning Authority;
- unresolved semantics are routed as Questions rather than invented;
- the analysis/design does not duplicate upstream semantic ownership;
- implementation freedoms remain explicit after closure.


## Human projection

Prefer the smallest project-native coverage/contract view that shows scope, accepted decisions, routed gaps, evidence obligations and implementation freedoms.
