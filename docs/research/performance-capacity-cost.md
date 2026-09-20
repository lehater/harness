# Performance / capacity / scalability / resource efficiency / cost ownership research

Status: research conclusion.

## Research question

Do performance, capacity planning, scalability, resource efficiency and operational cost form a new engineering Authority, or are they already coherently owned by QUALITY-DESIGN plus Product, System Architecture, Implementation and Operability?

Separate:
- **product expectation** — externally meaningful responsiveness/volume/availability/economic constraint;
- **quality constraint** — measurable latency, throughput, concurrency, capacity, scale, utilization or cost envelope;
- **workload model** — load shape against which the constraint is meaningful;
- **architecture response** — topology, partitioning, caching, admission, horizontal/vertical scale;
- **implementation efficiency** — algorithms, queries, memory/CPU/I/O behavior;
- **operational evidence** — measurements showing headroom/saturation/cost;
- **capacity action** — scale/provision/admit/degrade choices.

## Decision ownership map

| Decision | Owner |
| --- | --- |
| User/business-visible responsiveness or volume need | Product |
| Economic/business cost constraint | Product; Engineering Policy/Obligation Analysis when externally imposed |
| Latency/throughput/concurrency/scale target | Quality Design |
| Workload envelope and measurement conditions | Quality Design derived from Product/System scope |
| Resource/cost budget needed as realization constraint | Quality Design |
| Topology/partitioning/cache/admission/scaling strategy | System Architecture |
| Semantic behavior under overload | Product/Application + Quality; System realizes |
| Algorithm/query/data-layout efficiency | Implementation/Data within accepted constraints |
| Solver/time-budget semantics affecting outcome | Product/Application/Quality; implementation mechanism downstream |
| Runtime saturation/headroom/latency/cost evidence | Operability |
| Load/performance/capacity proof | Verification/Test |
| Provisioning commands/autoscaler implementation | Implementation/operations |

## Key distinctions

### Performance without workload is underspecified

A latency number is not a useful engineering contract without operation, percentile/statistic, workload/concurrency/data size, environment/scope and measurement boundary.

### Capacity is not architecture topology

"Support N requests" is a quality constraint. "Use three replicas" is one architecture/implementation response. Capacity planning connects evidence to constraints but does not own a new product semantic.

### Scalability is not current capacity

Current capacity says what load is supported now. Scalability describes behavior/constraints as load or resources change. Both are quality properties; architecture owns mechanisms enabling them.

### Cost is a quality/business constraint, not automatically FinOps design

A maximum infrastructure cost per tenant/request/month can constrain realization independently and belongs in Product/Quality. Cloud billing tags, dashboards and purchasing mechanics do not create a semantic Authority.

### Optimization is not allowed to trade correctness silently

Performance/cost pressure cannot silently relax accepted correctness, determinism, consistency, security or product outcomes. Such trade-offs require upstream accepted semantics.

## Atomicity test — candidate PERFORMANCE-CAPACITY-DESIGN

### Semantic cohesion — FAIL as a new Authority

The coherent portion—measurable performance/capacity/scale/resource/cost constraints—is already exactly QUALITY-DESIGN's responsibility: explicit realization quality constraints derived from accepted product/design truth.

The remaining decisions belong to architecture, implementation, operability and verification. Creating a second Authority would overlap Quality Design.

### Independent change — already represented

Quality constraints can change independently of architecture mechanisms; this is the existing QUALITY-DESIGN boundary.

### Public contract — already represented

Quality Design already provides measurable or explicitly unresolved quality constraints to architecture, implementation and verification.

## Verdict

**Do not create PERFORMANCE-DESIGN, CAPACITY-DESIGN, SCALABILITY-DESIGN, RESOURCE-EFFICIENCY-DESIGN or COST-DESIGN Authorities.**

Instead, strengthen QUALITY-DESIGN interpretation and add a reusable performance/capacity closure analysis for cases where implementation would otherwise invent workload, target or economic trade-offs.

## Required quality contract

A material performance/capacity requirement should identify, as applicable:
- operation/journey;
- metric;
- target/statistic;
- workload/concurrency;
- data size/cardinality;
- environment/deployment scope;
- measurement boundary;
- duration/burst assumptions;
- degradation/overload semantics;
- resource/cost envelope;
- evidence method.

Missing material fields are Questions, not permission to choose convenient benchmarks.

## Validation — Nutrition Management

Accepted Nutrition architecture has a synchronous in-process optimizer. It explicitly leaves realistic synchronous solve time as non-blocking S4 verification and treats timeout/unknown as technical failure, never as a valid partial domain result.

This demonstrates the boundary:
- Purchase Planning owns outcome semantics;
- a future acceptable solve-time target belongs to Product/Quality;
- solver/library/model strategy belongs to Architecture/Implementation;
- measurement belongs to Verification/Operability.

The accepted artifacts do not provide numeric latency, throughput, dataset-size or cost targets. Harness must not infer them from local SQLite or SCIP choices.

If a future product requirement says, for example, planning must complete under a specified workload/data size, QUALITY-DESIGN can own the measurable constraint without a new Performance Authority.

## Validation — NAPMS

NAPMS Quality Design explicitly states numeric latency, throughput, availability and scale targets are absent from accepted upstream truth and remain unspecified rather than invented by Architecture.

This is direct evidence that QUALITY-DESIGN is already the correct owner.

The current architecture is a modular monolith and explicitly forbids inventing distributed-service extraction without future quality/runtime need. Therefore "scalability" cannot be used as an excuse to introduce services, queues, replicas or caches absent an accepted quality constraint.

Observability also correctly refuses to introduce production metrics/SLO tooling without upstream requirement. Once targets exist, Operability should expose evidence rather than own the targets.

No residual Performance/Capacity Authority appears.

## Synthetic high-scale SaaS case

Assume accepted needs:
- p95 API latency <= target under stated concurrency;
- sustained and burst throughput envelopes;
- tenant data cardinality;
- maximum infrastructure cost envelope;
- no correctness degradation under ordinary load;
- explicit overload rejection above protected capacity.

Routing:
1. Product defines externally meaningful experience/economic constraint.
2. Quality Design defines measurable workload/latency/throughput/cost envelope.
3. System Architecture chooses partition/cache/admission/scaling topology.
4. Data/Implementation optimize query/index/algorithm/resource use.
5. Operability measures latency, saturation, headroom and cost signals.
6. Verification performs load/capacity tests.
7. If overload changes observable outcomes, Product/Application owns those semantics.

Changing Kubernetes/autoscaler/cache technology need not change the quality contract. Changing p95 target or cost envelope can invalidate architecture while product semantics remain otherwise stable. This is precisely the existing Quality boundary.

## Capacity closure algorithm

For each performance-sensitive journey/dependency/resource:

1. identify externally meaningful consequence of delay/saturation/cost;
2. locate accepted Product/Domain basis;
3. identify metric and measurement boundary;
4. establish workload/data-size/concurrency envelope;
5. establish target/statistic and resource/cost budget if material;
6. define ordinary-load vs overload boundary;
7. route observable overload/degradation behavior to Product/Application;
8. route topology/scaling/admission choices to System;
9. route data/algorithm/query efficiency to Data/Implementation;
10. classify COVERED, NOT_APPLICABLE, DEFERRED_NONBLOCKING or QUESTION;
11. derive Verification/Test load/capacity evidence;
12. derive Operability latency/saturation/headroom/cost evidence;
13. prevent implementation defaults from weakening accepted correctness/security/reliability semantics.

## Pre-code blocking Questions

Create a Question when implementation would otherwise invent material:
- latency/throughput/concurrency target;
- dataset/cardinality envelope;
- workload/burst shape;
- capacity/headroom expectation;
- acceptable queueing/rejection/degradation;
- resource budget;
- operational cost ceiling;
- scale-up/scale-out trigger semantics that affect product outcome;
- timeout used as a product-quality boundary;
- benchmark environment/measurement boundary used as acceptance truth.

## Implementation freedoms

After closure:
- profiling tooling;
- algorithm/query/index optimization preserving semantics;
- cache implementation within accepted consistency rules;
- worker/pool sizing inside accepted constraints;
- replica/autoscaler mechanics after architecture decision;
- benchmark harness mechanics;
- telemetry names;
- cloud instance types within accepted architecture/quality envelope.

## Priority findings

### P0
1. Architecture/implementation must not invent numeric performance, scale or cost requirements.
2. Performance optimizations must not silently change correctness/security/domain semantics.
3. Latency/capacity claims without workload and measurement boundary are insufficient acceptance contracts.
4. Overload behavior is semantic when observable.

### P1
1. Existing QUALITY-DESIGN already owns the atomic quality-constraint boundary.
2. Capacity planning is analysis connecting Quality constraints, architecture and runtime evidence, not a new Authority.
3. Cost/resource efficiency fit Quality when they constrain realization; billing/optimization mechanics remain downstream.
4. No Core change is justified.

## Canonicalization recommendation

Add performance-capacity analysis skill and catalog principles clarifying QUALITY-DESIGN ownership. Do not add a new Authority.
