# Concurrency / consistency / ordering / backpressure ownership research

Status: research conclusion. This document does not by itself change Harness Core or the canonical Authority catalogue.

## Research question

Do concurrency, distributed consistency, ordering and backpressure form an independently owned engineering decision boundary, or are they cross-Authority concerns whose semantics remain with existing owners?

The analysis deliberately separates:

- **semantic concurrency** — which simultaneous intents are valid and how conflicts affect business state;
- **consistency model** — which observations/effects must agree, atomically or eventually;
- **ordering** — whether operation/event order is semantically relevant and which order is authoritative;
- **coordination mechanism** — transaction, lock, version token, compare-and-swap, queue, partition, leader, deduplication;
- **flow control/backpressure** — what happens when demand exceeds bounded processing capacity;
- **evidence** — how violations, conflicts, queue growth and saturation are observed.

## External coverage lenses

Database isolation demonstrates an important separation: a mechanism such as Serializable can reject executions that would produce a serialization anomaly, but the application still has to retry aborted work and must know whether retry is semantically valid. Database isolation therefore cannot invent application continuation semantics.

Queue/backlog guidance demonstrates a second separation: backpressure, throttling, prioritization and queue isolation protect bounded capacity, but choosing reject/delay/drop/prioritize/degrade behavior can alter externally meaningful outcomes.

Distributed/event processing demonstrates a third: consistency can be achieved with different coordination models. The mechanism is not the business invariant.

These references are coverage lenses, not Harness ontology.

## Decision ownership map

| Decision | Owner |
| --- | --- |
| Which concurrent intents may both succeed | Domain/Application |
| Invariant that must hold under concurrency | Domain |
| Conflict outcome visible to caller | Application/Product; Interface represents externally |
| Stable mutation/command identity | Application/Domain; Interface when external |
| Atomicity boundary for one use case | Application + Data/System according to scope |
| Required read consistency/coherent snapshot | Application/Domain + Quality when measurable |
| Physical isolation/locking/version mechanism | Data/System/Implementation within accepted semantics |
| Whether operation order changes business meaning | Domain/Application |
| Authoritative ordering/version relation | Domain/Application; Interface represents metadata |
| Message delivery/order guarantee required | Application/System; Interface/event contract represents it |
| Partitioning/leader/queue topology | System Architecture |
| Cross-boundary consistency/deferred convergence semantics | Domain/Application/System according to authoritative state |
| Compensation/reconciliation | Domain/Application |
| Capacity/latency/headroom target | Quality Design |
| Reject/block/queue/drop/degrade behavior under saturation | Product/Application; System realizes |
| Admission/throttling/backpressure placement | System Architecture |
| Queue/thread/pool implementation | Implementation within accepted constraints |
| Conflict/saturation/lag evidence | Operability |
| Proof under races/reordering/overload | Verification/Test |

## Core distinctions

### Concurrency control is not concurrency semantics

A lock, serializable transaction or optimistic token is a mechanism. Before selecting it, accepted design must say which competing effects may coexist and what outcome is valid when they cannot.

### Consistency is scoped

"Strong consistency" is underspecified without:
- authoritative state;
- participants;
- observation boundary;
- invariant;
- time/order relation;
- tolerated intermediate states.

A local aggregate transaction and cross-service convergence are different problems and need not share an Authority.

### Ordering is semantic only when order changes validity

FIFO is not universally desirable. If operations commute, imposing total order may be unnecessary. If order changes state meaning, the owning Domain/Application contract must define the relation before broker/database implementation.

### Backpressure is not only performance

When saturation causes externally visible reject, delay, drop, priority or degradation, Product/Application/Quality semantics are involved. System Architecture owns placement/topology of admission and isolation; implementation owns mechanics only inside that contract.

## Atomicity test — candidate CONCURRENCY-CONSISTENCY-DESIGN

### Semantic cohesion — FAIL

The candidate combines several decision classes with different authoritative subjects:
- domain conflict validity;
- application transaction/continuation;
- data isolation;
- distributed topology;
- quality capacity;
- product degradation;
- runtime evidence.

The common trigger is simultaneous activity, not one semantic owner.

### Independent change — FAIL

Concurrency mechanism can change without semantic conflict policy changing. Backpressure topology can change without domain ordering changing. A consistency mechanism can change from lock to serializable retry while the application invariant remains fixed.

Conversely, business conflict semantics can change without changing deployment topology.

### Public producer/consumer contract — FAIL as one boundary

There is no single residual contract after existing Authorities keep their native decisions. Consumers require specific capabilities: conflict semantics, atomicity, consistency observation, ordering, capacity/admission, or evidence. Aggregating them as one "Concurrency Design" artifact would hide ownership.

## Verdict

**Do not create CONCURRENCY-DESIGN, CONSISTENCY-DESIGN, ORDERING-DESIGN or BACKPRESSURE-DESIGN Authorities from current evidence.**

Treat the subject as a cross-Authority closure analysis, analogous to Reliability but with a different question:

> For every operation whose correctness can change under overlap, reordering, delayed visibility or saturation, is the required semantic outcome owned and accepted before implementation chooses coordination and flow-control mechanisms?

## Pre-code blocking Questions

Route a Question when code/framework/database/broker would otherwise decide:
- whether two competing mutations may both succeed;
- which state wins or whether conflict must be surfaced;
- whether lost update is acceptable;
- required atomicity across multiple state changes;
- required read snapshot/coherence;
- whether stale observation is acceptable and for how long;
- whether operation/event order is material;
- authoritative version/order relation;
- duplicate/reordered event effect;
- convergence/reconciliation after partial cross-boundary progress;
- reject vs wait vs queue vs drop vs degrade under capacity pressure;
- priority/fairness semantics when capacity is shared;
- maximum accepted lag/backlog where product/quality behavior depends on it.

## Implementation freedoms

When upstream semantics are accepted, implementation may choose:
- lock/version-token representation;
- database isolation level that demonstrably satisfies the contract;
- retry loop mechanics where retry is already authorized;
- queue/broker library;
- worker/thread/pool implementation;
- partition/hash mechanism;
- semaphore/rate-limiter implementation;
- internal queue capacity inside accepted budgets;
- telemetry names.

A default is safe only when changing it cannot alter accepted state validity, observable conflict outcome, ordering, consistency, capacity/degradation or evidence obligations.

## Validation — Nutrition Management

Accepted design gives a deliberately narrow concurrency surface:
- state-changing imports/commands are context-local transactions;
- planning captures one coherent relational read scope and closes it before pure solver computation;
- no provider reads occur during solver execution;
- first slice is one local process and one SQLite file.

This already assigns the meaningful decisions:
- coherent planning observation -> Application Design;
- persistence snapshot realization -> Data/System/Implementation;
- mutation atomicity -> Application/Data;
- solver execution has no durable concurrent mutation semantics.

No independent Concurrency Authority remains. If later multi-writer imports introduce lost-update/conflict semantics, those questions first belong to the owning domain/application use case rather than to a generic concurrency owner.

Result: negative validation for a new Authority, positive validation for closure analysis.

## Validation — NAPMS

Accepted Resource Catalogue architecture is stronger evidence:
- Resource is one application-owned consistency boundary;
- mutation persistence is atomic for that Resource;
- conflicting concurrent update must not silently overwrite newer accepted state;
- stable command identity may resolve equivalent retry to a known outcome;
- incompatible identity reuse is conflict;
- without stable identity, duplicate submission is rejected/prevented;
- exact token/header/storage representation remains downstream.

The physical persistence model separately realizes local uniqueness, temporal constraints and application-enforced overlap rules.

This is exactly the desired separation:
- Domain/Application own conflict and duplicate semantics;
- Data owns enforceable representation/integrity;
- Interface can expose the conflict/token contract;
- implementation chooses token/locking/storage details;
- Verification proves races do not violate the accepted semantics.

NAPMS therefore provides direct evidence **against** a generic concurrency owner.

## Synthetic distributed case

Assume two writers update the same logical entity through separate service instances while an event consumer receives changes asynchronously.

Experiments:

1. **Lost update** — deciding last-write-wins vs reject vs merge is domain/application semantics; lock/CAS/serializable is mechanism.
2. **Concurrent invariant** — two individually valid reservations exceed shared capacity. Domain owns capacity invariant; System/Data select coordination capable of preserving it.
3. **Reordered events** — if state is version-monotonic, Domain/Application must define stale-event behavior; broker FIFO alone cannot establish business authority.
4. **Partition** — accepting writes on both sides may create conflicting authoritative states. Product/Domain/System must define availability/consistency tradeoff for this concrete boundary.
5. **Consumer lag** — acceptable staleness is Application/Product/Quality; queue scaling is System/Implementation.
6. **Overload** — reject, queue, shed or degrade can change product outcome; System cannot invent the semantic choice from CPU/thread limits.

Again there is no residual atomic "Concurrency" contract.

## Closure algorithm

For each selected implementation scope:

1. enumerate state-changing operations, coherent reads, shared resources, async boundaries and bounded-capacity dependencies;
2. identify overlap/reordering/staleness/saturation scenarios that can alter correctness or accepted outcome;
3. identify authoritative state/invariant and owner;
4. determine required observation/order/atomicity/conflict behavior;
5. determine allowed continuation under conflict or capacity pressure;
6. classify each concern as COVERED, NOT_APPLICABLE, DEFERRED_NONBLOCKING or QUESTION;
7. route Questions to owning Authorities;
8. only after semantic closure select coordination/isolation/admission mechanisms;
9. derive Verification/Test race/reorder/overload obligations;
10. derive Operability conflict/lag/saturation evidence.

This procedure is analysis, not a new workflow stage or Core entity.

## Priority findings

### P0

1. Database/broker/framework defaults must not invent material concurrency semantics.
2. Isolation level does not define business conflict outcome.
3. FIFO/ordering guarantees are not substitutes for authoritative business ordering.
4. Backpressure becomes semantic when it changes observable reject/delay/drop/degrade behavior.

### P1

1. Concurrency/Consistency/Ordering/Backpressure fail the Authority atomicity test as one boundary.
2. Existing Harness Authorities can own all demonstrated decisions.
3. A reusable cross-Authority analysis skill is justified.
4. No Harness Core change is justified.

## Canonicalization recommendation

Add a reusable `concurrency-consistency-analysis` skill and catalog principles that preserve ownership routing. Do not add a new Authority or Capability by default. The analysis artifact becomes a Capability only if a concrete consumer independently requires accepted coverage evidence.
