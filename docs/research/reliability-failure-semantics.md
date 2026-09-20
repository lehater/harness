# Reliability / failure-semantics boundary research

Status: research hypothesis after two-project validation. No Harness Core or canonical Authority change is made by this document.

## Research question

Which reliability decisions must be accepted before IMPLEMENTATION, who owns them, and how does Harness prevent coding agents, frameworks and infrastructure libraries from inventing failure semantics?

This study does **not** assume a RELIABILITY-DESIGN Authority. Reliability terminology is used as a coverage lens over decisions whose semantic owners may already exist.

## External reference model

The study uses established distributed-systems/reliability guidance as lenses rather than ontology.

Recurring facts across the references:

- a timeout or lost response does not prove that a state-changing operation did not take effect;
- automatic retry is safe only when the operation semantics make repetition safe or the caller can establish that the first attempt did not take effect;
- idempotency is an operation/effect property, not merely a retry-library setting;
- retries consume capacity and can amplify overload/cascading failure, especially when independently layered;
- backoff/jitter, retry budgets, circuit breakers, bulkheads, throttling/load shedding and degradation are different mechanisms with different semantic consequences;
- cancellation/deadline propagation is not equivalent to transactional rollback;
- reconciliation is required when authoritative completion may be uncertain and repeating the mutation is unsafe.

Primary lenses:
- RFC 9110 HTTP Semantics, especially idempotent-method/retry semantics;
- Amazon Builders' Library, "Timeouts, retries, and backoff with jitter" and "Making retries safe with idempotent APIs";
- Google SRE, "Addressing Cascading Failures" and overload handling;
- Microsoft Azure Architecture Center reliability patterns for Retry, Circuit Breaker and Bulkhead.

The important Harness implication is that "use retry/circuit breaker/timeout" is too low-level to be an engineering decision owner. The pre-code question is what externally meaningful outcome, state safety and resource/failure-containment contract must hold.

## Failure-semantics decision map

| Decision | Semantic owner | Why |
| --- | --- | --- |
| Whether an operation may have a business effect more than once | Product/Domain | Duplicate effect changes accepted business semantics/invariants. |
| Stable command/request identity and equivalent-repeat semantics | Domain/Application; Interface represents it when externally visible | Identity may be business/application semantics; header/token encoding is representation. |
| Whether an unknown completion may be repeated, rejected, queried or reconciled | Domain/Application | This defines safe continuation of a use case after ambiguous execution. |
| Transaction/atomicity boundary | Application + Data/System Architecture according to scope | Orchestration owns use-case atomic intent; persistence/system design owns realization boundary. |
| Retryable outcome classification exposed by an interface | Interface, derived from upstream semantics | Transport representation must not invent retryability. |
| Dependency timeout/deadline budget | Quality + Application/System Architecture | Required user/service budget is a quality constraint; allocation/propagation is orchestration/architecture. |
| Cancellation semantics and propagation | Application/System Architecture, constrained by Domain | Defines which work may stop and what already-committed effects remain authoritative. |
| Failure containment / blast-radius partition | System Architecture | Bulkheads/resource isolation are structural runtime decisions. |
| Circuit-breaking / admission / load shedding placement | System Architecture; Product/Quality constrain degraded outcome | It changes dependency admission and runtime topology, while user-visible degradation is upstream product/quality truth. |
| Graceful degradation / fallback result | Product/Application/Domain depending meaning | A fallback is acceptable only if its externally meaningful semantics are accepted. |
| Backpressure / quota / overload contract | Quality + System/Application; Interface when externally represented | Capacity limits constrain behavior; mechanisms are structural/orchestration choices. |
| Consistency after partial failure | Domain/Application/Data/System according to state boundary | Recovery must preserve the owner of the affected state/invariant. |
| Reconciliation rule | Domain/Application; Data/System supplies authoritative observation mechanism | Reconciliation decides how uncertain effects become known and safe to continue. |
| Recovery target / eventual recovery expectation | Product/Quality | Required availability/recovery outcome is a quality/product constraint. |
| Recovery mechanism | System/Data/Application according to failed state | Mechanism belongs to the state/runtime owner, not a generic reliability owner. |
| Retry count/backoff/jitter numeric mechanics | Implementation freedom only inside accepted budgets/constraints | These are tunable realization details unless a higher-level contract makes them observable. |
| Retry/timeout/circuit-breaker metrics and diagnostic evidence | Operability Design | Evidence projects accepted failure semantics; it does not define them. |
| Failure/recovery verification scenarios | Verification/Test Design | They prove accepted semantics without selecting them. |

## Key semantic distinctions

### Timeout is not failure

A caller-side timeout establishes that the caller stopped waiting. It does not establish whether the callee committed a state change.

For a state-changing operation, the post-timeout state can therefore be:

1. confirmed not applied;
2. confirmed applied;
3. unknown.

Case 3 is a distinct semantic outcome. An implementation agent must not collapse it into "failed" and retry unless upstream knowledge makes repetition safe.

### Retryability is derived, not defaulted

Retryability requires accepted answers to:

- is the operation read-only or state-changing;
- if state-changing, is repeating the intended effect idempotent;
- if execution status is unknown, can the result be reconciled;
- which failure classes are transient;
- what total latency/load budget is available;
- at which single layer is retry responsibility placed;
- what happens when the retry budget is exhausted.

A framework default that answers these questions implicitly is an unowned design decision.

### Cancellation is not rollback

Cancellation can stop future work or signal cooperative termination. It cannot be assumed to reverse already committed external or durable effects. The owner of each state transition defines what remains authoritative and whether compensation/reconciliation exists.

### Fallback is product semantics when observable

Returning stale data, partial data, cached data, a default value, "accepted for later", or reduced functionality is not merely a resilience mechanism when the caller can observe a different result. The accepted product/application contract must authorize the degraded outcome.

## Atomicity test for a candidate RELIABILITY-DESIGN Authority

### 1. Semantic cohesion — fails

The candidate set does not form one semantic decision class.

- duplicate/idempotency semantics belong to Domain/Application;
- timeout budgets originate in Quality and are allocated by Application/System;
- containment/bulkheads/circuit-breaker placement are System Architecture;
- degraded outcomes are Product/Application semantics;
- state recovery/reconciliation follows the owner of the affected state;
- evidence is Operability;
- proof is Verification/Test.

The common label is "behavior under failure", but the decisions preserve different invariants and public contracts.

### 2. Independent change — fails as one boundary

These decisions can change independently. A system can change retry policy without changing degradation semantics; change a bulkhead without changing idempotency; change reconciliation without changing observability evidence requirements.

### 3. Public producer/consumer contract — fails as one boundary

There is no single coherent reliability artifact that downstream consumers need without either duplicating accepted upstream semantics or becoming a collection of references to decisions owned elsewhere.

### Verdict

**Do not create RELIABILITY-DESIGN.**

Reliability is a required **cross-Authority closure analysis**, analogous to a coverage lens, not an atomic semantic owner.

A reusable RELIABILITY-ANALYSIS skill is justified if it only:
- enumerates material failure paths against accepted design;
- checks ownership/coverage;
- derives implementation-blocking Questions;
- routes each gap to its semantic owner;
- never selects retry/degradation/recovery semantics itself.

This is closer to SECURITY-ANALYSIS than to OPERABILITY-DESIGN, but it does not require a new Authority unless future pilots demonstrate independently accepted reliability-analysis knowledge as a stable consumer contract. Current evidence supports the skill first, not the Authority.

## Pre-code closure

IMPLEMENTATION must be blocked when an applicable path leaves coding/framework defaults to decide any of these:

- whether a state-changing operation may be repeated after uncertain completion;
- duplicate-effect semantics or command identity needed for safe repetition;
- whether timeout means confirmed failure or unknown completion;
- required reconciliation after an ambiguous commit;
- cancellation behavior where partial durable/external effects are possible;
- atomicity/consistency boundary for a state-changing use case;
- externally observable fallback/degradation behavior;
- fail-open/fail-closed behavior when it is not already security-owned;
- dependency failure behavior that can violate accepted domain/application outcomes;
- overload behavior when dropping/rejecting/queuing work changes accepted semantics;
- recovery behavior needed to preserve authoritative state/invariants;
- timeout/deadline requirement where an implementation choice can violate an accepted latency/availability contract.

Implementation freedom remains for:

- library/framework choice;
- private exception types and helper structure;
- exact backoff algorithm, jitter distribution and retry count when upstream contracts only require bounded safe retry and Quality/System budgets leave those values free;
- circuit-breaker library and internal state representation after placement/admission semantics are accepted;
- thread/task cancellation mechanism after cancellation semantics are accepted;
- connection-pool implementation after isolation/capacity constraints are accepted;
- internal logging/metric names after Operability evidence requirements are accepted.

A default is allowed only when changing it cannot alter accepted externally meaningful behavior, state safety, architecture boundary, quality constraint or diagnostic obligation.

## Validation case 1 — Nutrition Management

Accepted design describes a local CLI, file-backed SQLite, context-local state-changing transactions, one coherent read transaction for planning snapshot capture, and pure solver computation after the read closes.

Observed pressure:

- solver timeout/cancellation/unknown numeric status is already explicitly a technical failure and must not become a domain `partial` result;
- state-changing imports/commands are context-local transactions;
- no remote service/message boundary exists in the MVP;
- plan generation reads a coherent snapshot then performs pure computation, so retrying the pure computation does not duplicate persisted business effects;
- SQLite migration/transaction rules preserve provider semantics.

Result:

- a dedicated Reliability Authority would add little value here;
- most distributed retry/circuit-breaker/bulkhead concerns are NOT_APPLICABLE for the current local boundary;
- the case validates negative applicability and demonstrates that failure semantics already live in Application/Data/Interface owners;
- one generic closure question remains useful for every state-changing import/command: after an infrastructure/commit acknowledgement failure, can completion become uncertain, and if so what accepted reconciliation/repetition rule applies? Existing design establishes transaction scope but does not universally state this post-commit-ambiguity contract.

This gap must be routed to the owner of each mutation/use case; it is not evidence for a Reliability owner.

## Validation case 2 — NAPMS

Accepted design describes a long-running HTTP modular monolith with PostgreSQL, protected mutations and explicit application/module contracts.

Observed pressure:

- Resource Catalogue design already requires safe duplicate-submission handling, stable command identity where available, conflict on incompatible identity reuse and prevention of duplicate application where identity is absent;
- local aggregate invariants are transactional;
- cross-module validation is synchronous and must not manufacture distributed-service semantics;
- export composition is either complete Success or explicit Unresolved; silent partial success is forbidden.

This is strong positive evidence that reliability semantics are real pre-code design knowledge **and are already naturally owned by existing semantic Authorities**.

However, the broader MVP graph does not yet establish a uniform failure-semantics closure for:
- client disconnect/timeout after a protected mutation reaches commit;
- which HTTP mutations expose/require stable idempotency identity;
- reconciliation/readback after uncertain mutation completion;
- server/request cancellation propagation and its relationship to database work;
- dependency/admission timeout budgets;
- overload/backpressure behavior for the long-running HTTP service.

These are implementation-blocking only for implementation slices where the path is applicable. They should be Questions routed to Product/Application/System/Interface/Data/Quality owners as appropriate, not filled by framework defaults.

## Need for a third validation case

The two current pilots are sufficient for the atomicity verdict but **not sufficient to validate distributed failure closure**.

Nutrition is deliberately local. NAPMS deliberately avoids asynchronous messaging and distributed-service semantics in the first MVP. Neither exercises:
- at-least-once delivery;
- duplicate messages across process boundaries;
- ordering/reordering;
- consumer crash after effect but before acknowledgement;
- distributed partial failure;
- eventual consistency and reconciliation;
- retry storms across service layers;
- backpressure across queues.

Therefore a third synthetic distributed/event-driven case is required before claiming the reliability closure model is complete. It must be a research fixture, not a distortion of either pilot.


## Validation case 3 — synthetic distributed/event-driven fixture

This fixture exists only to pressure-test ownership and closure. It is not a new product repository and does not prescribe Kafka, a cloud provider, or a particular implementation.

### Accepted baseline

Consider an Order service that accepts a state-changing `PlaceOrder` command and publishes `OrderPlaced` to an at-least-once broker. A Fulfilment consumer reserves stock in its own durable store.

The accepted success path is:

```text
client -> Order application -> Order state commit
                           -> outbox/event
broker -> Fulfilment consumer -> inventory reservation
```

Assume:
- Order and Fulfilment own different durable state;
- no distributed transaction spans them;
- broker delivery is at least once;
- acknowledgement can be lost;
- consumers can crash after committing their local effect but before acknowledging;
- messages can be delayed and, unless an ordering contract says otherwise, observed out of order;
- the broker and dependencies have finite capacity.

### Failure experiments

#### F1 — producer commit succeeds, client response is lost

The client cannot infer that `PlaceOrder` failed. Repeating the command can create a second order unless accepted Product/Domain/Application semantics define command identity/equivalent-repeat behavior or a reconciliation/readback path.

Ownership result:
- duplicate business effect: Domain/Product;
- command identity and continuation after unknown completion: Application/Domain;
- external representation of identity/status/readback: Interface;
- durable uniqueness/transaction realization: Data;
- timeout mechanics: implementation only after the semantic contract exists.

A generic retry library cannot own this decision.

#### F2 — consumer effect commits, acknowledgement is lost

The broker redelivers `OrderPlaced`. At-least-once delivery therefore creates duplicate **attempts**, while the required semantic effect may still be exactly once per accepted event identity.

Ownership result:
- whether repeated event application may duplicate inventory reservation: Fulfilment Domain/Application;
- event identity and deduplication contract: producer/consumer application contract, represented by Interface/event contract;
- durable deduplication/atomic effect+receipt representation: Data/Application realization;
- broker redelivery policy: System Architecture within accepted capacity/latency constraints.

This demonstrates that transport delivery guarantee and business-effect guarantee are different knowledge.

#### F3 — messages arrive out of order

Suppose `OrderCancelled` can arrive before a delayed `OrderPlaced`.

No generic reliability rule can decide the result. The owner of the state transition must define whether:
- ordering is required and enforced;
- versions/sequence numbers make stale events rejectable;
- transitions commute;
- later reconciliation repairs the state;
- the event model itself is invalid for this use case.

Ownership result: Domain/Application first; Interface represents ordering/version metadata; System Architecture selects delivery mechanisms capable of satisfying the accepted contract.

#### F4 — downstream unavailable; producer retries

Retrying delivery or dependency calls increases load. Independent retry layers can amplify one logical request into many attempts and worsen overload.

Ownership result:
- acceptable end-user delay/failure/degraded outcome: Product/Quality;
- one retry-responsibility boundary, queue/buffer placement, circuit breaking, load shedding and isolation: System Architecture/Application;
- retry budget/backoff/jitter: implementation freedom only inside accepted architecture/capacity constraints;
- retry/load evidence: Operability.

This confirms that "retry" spans several owners but does not create a coherent owner of its own.

#### F5 — queue reaches capacity

The system must choose among reject, block/backpressure, shed, spill, delay, or degrade. Each can change externally meaningful behavior and recovery time.

Ownership result:
- accepted rejection/degradation semantics and priority: Product/Application;
- throughput/latency/headroom constraints: Quality;
- queue limits, admission, partition/isolation and pressure propagation: System Architecture;
- public overload response: Interface;
- evidence: Operability.

A queue/framework default is unsafe when it silently chooses one of these outcomes.

#### F6 — poison message repeatedly fails

Infinite retry prevents progress and can consume capacity. Moving the message aside permits progress but creates an unresolved business effect.

Ownership result:
- whether later messages may proceed and what unresolved state means: Domain/Application;
- quarantine/dead-letter topology: System Architecture;
- operator-visible evidence: Operability;
- replay/reconciliation semantics: Domain/Application;
- proof that replay cannot duplicate effects: Verification/Test.

"Dead-letter queue" is therefore a mechanism, not the semantic answer.

#### F7 — reconciliation after partial distributed success

Order is accepted but inventory reservation remains unknown/unavailable.

Possible policies—cancel order, keep pending, compensate, retry later, require operator action—are observably different product/domain outcomes. Architecture may provide saga/workflow/reconciliation machinery only after those outcomes are accepted.

Ownership result: Product/Domain/Application own the transition policy; System/Data own durable coordination realization; Interface owns exposed state; Operability owns stuck/recovery evidence.

### Fixture verdict

The distributed case strengthens, rather than weakens, the two-project verdict.

1. Failure semantics remain attached to the owner of the affected state, outcome or runtime boundary.
2. No residual coherent decision set remains for RELIABILITY-DESIGN.
3. A cross-Authority analysis step is valuable because the dangerous gaps occur **between** otherwise valid success-path contracts.
4. Existing Core primitives can represent every discovered gap as a Question routed to its semantic owner.
5. Reliability analysis itself need not become a canonical project Capability unless a concrete consumer requires an accepted coverage artifact. For implementation readiness, its useful effect is closure: all material concerns resolve to accepted capabilities or blocking Questions.

## Reliability closure algorithm

For a selected IMPLEMENTATION scope, an agent can perform this analysis without adding Core concepts.

For every state-changing operation, external dependency and asynchronous boundary:

1. identify the authoritative state/effect;
2. enumerate material interruption points: before effect, during effect, after effect before acknowledgement, duplicate attempt, cancellation, dependency failure and overload;
3. for each point ask what the caller/consumer can actually know;
4. derive the allowed continuation: stop, retry, reconcile, compensate, degrade, reject or wait;
5. locate the Authority that owns that outcome/state/continuation;
6. classify the concern:
   - `COVERED` — accepted knowledge answers it;
   - `NOT_APPLICABLE` — accepted design removes the failure path;
   - `DEFERRED_NONBLOCKING` — outside current implementation scope with an explicit reopening condition;
   - `QUESTION` — coding would otherwise invent a material decision;
7. route every `QUESTION` to the semantic owner;
8. derive Verification/Test obligations from the accepted outcome;
9. derive Operability evidence from the accepted failure/recovery states;
10. permit implementation only when applicable blocking Questions are closed.

This algorithm is a reusable analysis procedure, not a workflow stage and not a new graph entity.

## Distributed validation conclusion

The additional fixture provides the evidence previously missing from the two pilots.

The no-RELIABILITY-DESIGN verdict now survives:
- local transactional computation;
- synchronous HTTP/modular-monolith mutation;
- at-least-once asynchronous delivery;
- ambiguous acknowledgement;
- duplicate attempts;
- reordering;
- overload/backpressure;
- poison work;
- eventual reconciliation.

This is enough to canonicalize the **ownership rule and analysis procedure** in Harness, subject to repository CI/contract checks. It is not evidence to add a Reliability Authority or any Core entity.

Recommended canonicalization:
- add a reusable `reliability-analysis` skill;
- add a concise canonical rule that failure-path semantics follow the Authority owning the affected outcome/state/runtime boundary;
- require the skill to route gaps as Questions and never repair them itself;
- keep concurrency/distributed-consistency details for the later dedicated study;
- keep numeric capacity/performance budgets for the later Performance/Capacity study.


## Harness consequences

### Core

No Core change is justified.

Authority, Capability, CanonicalArtifact, Question and prerequisite closure can already represent:
- accepted failure semantics;
- their semantic owners;
- unresolved reliability gaps;
- propagation to IMPLEMENTATION.

### Catalog

Do not add RELIABILITY-DESIGN.

Potential future catalog refinement: explicitly state in existing Authority contracts that failure-path semantics are owned wherever the corresponding success-path semantics/state/runtime boundary is owned. This should wait until the distributed validation case.

### Reusable skill

The distributed validation fixture confirms the routing rules; a `reliability-analysis` skill is now justified.

Proposed responsibility:

> Analyze applicable failure paths against accepted product/domain/application/architecture/interface/data/quality truth, identify unowned retry/timeout/cancellation/duplicate/degradation/recovery semantics, and route each material gap to its semantic owner without selecting the missing semantics.

Inputs:
- selected implementation scope;
- accepted upstream capabilities/artifacts;
- external dependency/state-change boundaries;
- quality constraints;
- operability and verification knowledge when available.

Output:
- concern -> applicability -> owner -> coverage state;
- blocking Questions;
- implementation freedoms;
- required verification/evidence obligations.

The skill should use the same useful state vocabulary demonstrated by Security Analysis:
`COVERED`, `NOT_APPLICABLE`, `DEFERRED_NONBLOCKING` with reopening condition, `QUESTION`.

This is a skill-level convention; it does not require Core states.

## Priority findings

### P0

1. Harness must explicitly prohibit coding/framework defaults from inventing retryability, uncertain-completion handling, duplicate-effect semantics, fallback/degradation and cancellation semantics.
2. Timeout must be modeled in analysis as an observation boundary, not automatically as operation failure.
3. The distributed/event-driven validation case confirms that reusable reliability-analysis guidance can be canonicalized without a new Authority.

### P1

1. Existing Authority descriptions should eventually make failure-path ownership symmetric with success-path ownership.
2. Quality Design needs later pressure-testing for deadline/capacity/recovery budgets; this overlaps the planned Performance/Capacity study.
3. Concurrency/backpressure belongs in the later dedicated distributed-consistency study rather than being prematurely absorbed here.

## Current conclusion

Reliability is not one missing design Authority. It is a cross-cutting **closure property of accepted semantics under failure**.

The pre-code invariant is:

> For every material failure path in the selected implementation scope, the resulting externally meaningful outcome, authoritative state and permitted continuation must be derivable from accepted upstream knowledge; otherwise IMPLEMENTATION is blocked by a Question routed to the Authority that owns that semantic boundary.

The current Core is sufficient. Two real pilots plus the synthetic distributed/event-driven fixture support the no-RELIABILITY-DESIGN verdict and provide enough evidence to canonicalize the ownership rule and reusable analysis procedure.

## Next research step

Canonicalize the validated reliability-analysis procedure and ownership rule in a separate change, run repository checks, then begin the P0 Deployment / Release / Migration / Compatibility / Change research. Do not add a Reliability Authority or Core entity.
