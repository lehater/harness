# Engineering coverage gap analysis

Status: research inventory. No new Authority or Core entity is proposed by this document.

## Question

Which application-development decision areas are still missing, weakly represented, or not yet experimentally validated in Harness after the operability and security studies?

The goal is not to import every software-engineering topic into Harness. A topic matters only when it can create pre-code decisions that an implementation agent must not invent, or when it exposes a reusable analysis/verification responsibility with independent lifecycle and public consumers.

## Method

1. Inventory the current Harness Authority catalog.
2. Compare it with broad software-product quality, SDLC, architecture and operations concern families.
3. Classify each concern as:
   - COVERED: current Authority boundaries already own it coherently;
   - PARTIAL: represented indirectly but not researched enough to prove closure;
   - UNEXPLORED: no demonstrated Harness treatment;
   - OUTSIDE: organizational/process concern unless a project-specific contract makes it relevant.
4. Do not equate a named discipline with a new Authority.
5. Prioritize topics by risk that a coding/deployment agent would otherwise invent material decisions.

Reference lenses include ISO/IEC 25010 product-quality characteristics, NIST SSDF lifecycle practice coverage, accessibility standards, architecture/operations practice, and cost/sustainability disciplines. They are coverage lenses, not ontology.

## Current coverage

Strong or recently validated:
- problem discovery and product requirements;
- strategic/tactical domain semantics and use cases;
- application orchestration;
- system architecture;
- interface and persistence design;
- explicit quality constraints;
- security architecture and threat/control analysis;
- runtime evidence/diagnosability;
- engineering policy;
- component design;
- verification and executable test design;
- terminal implementation design.

This is broad, but it does not prove that all important cross-cutting application concerns are closed.

## Gap map

| Topic | State | Why it may matter before implementation | Preliminary Harness location |
| --- | --- | --- | --- |
| Reliability / resilience / fault tolerance | PARTIAL | Retry, timeout, idempotency, circuit breaking, degradation, recovery and failure containment can change externally observable semantics and state safety. Operability explicitly does not own them. | Product/Quality/Application/System Architecture; possible dedicated conditional boundary only if atomicity survives research. |
| Concurrency / consistency / distributed correctness | PARTIAL | Ordering, races, duplicate delivery, isolation, idempotency, consensus/ownership and consistency models can be semantic, architectural or data decisions. | Domain/Application/System/Data/Quality; needs ownership study. |
| Performance / capacity / scalability engineering | PARTIAL | Quality Design can state constraints, but workload model, budgets, capacity assumptions and performance architecture have not been independently validated. | Product/Quality/System Architecture/Verification. |
| Deployment / environment / infrastructure architecture | PARTIAL | Runtime placement, topology, environment parity, rollout constraints, external dependencies, certificates and infrastructure boundaries can be pre-code inputs. | System Architecture + Implementation Design; boundary not studied. |
| Release / delivery / migration / rollback | PARTIAL | Safe rollout, compatibility windows, DB/data migration, rollback/roll-forward and feature transition can require design before code. | Implementation Design/System/Data/Interface; not validated as a coherent boundary. |
| Backward compatibility / API & data evolution | PARTIAL | Versioning, compatibility windows, schema evolution and consumer migration can constrain both interface and data implementation. | Interface/Data/Product/Implementation; needs change/evolution research. |
| Data lifecycle / privacy / governance | PARTIAL | Retention, deletion, residency, minimization, purpose, export and lineage may be product/legal/security/data decisions rather than generic security. | Product/Data/Security/Policy; privacy ownership not studied. |
| Accessibility / inclusive interaction | UNEXPLORED | Human interfaces can have externally observable accessibility obligations that implementation must not invent or omit. | Product/Interface/Quality/Verification; likely conditional, not automatically separate Authority. |
| Internationalization / localization | UNEXPLORED | Locale, language, time zone, calendars, collation, formatting and translation ownership can affect domain/interface semantics. | Product/Domain/Interface/Data; needs boundary study. |
| Time / temporal semantics | PARTIAL | Clock source, business dates, time zones, ordering and expiry have appeared in pilots but no general ownership model has been studied. | Domain/Application/System/Interface/Data/Security depending semantics. |
| Resource management / limits / backpressure | UNEXPLORED | Memory/disk/connection/queue limits and overload behavior can affect availability and correctness. | Quality/System/Application/Operability; needs applicability study. |
| Disaster recovery / backup / restore / continuity | UNEXPLORED | RPO/RTO, restore semantics and authoritative-state recovery can be product/quality/data/system decisions. | Product/Quality/Data/System/Verification. |
| External dependency / third-party service governance | PARTIAL | Provider contracts, failure assumptions, quotas, versioning, data trust, exit/substitution and licensing can constrain architecture. | System/Interface/Application/Engineering Policy; not studied as a lifecycle. |
| Supply-chain / provenance / SBOM / dependency policy | PARTIAL | Security study routed generic discipline to Engineering Policy, but acquisition/provenance/update obligations remain unvalidated. | Engineering Policy/Security Analysis/Implementation/Verification. |
| Compliance / regulatory / audit obligations | UNEXPLORED | Regulations may create traceable product, data, security, retention and evidence constraints; a generic COMPLIANCE Authority may be wrong. | Likely source/policy feeding existing owners; needs routing study. |
| Cost / resource economics / FinOps | UNEXPLORED | Cost ceilings/unit economics/workload placement can constrain architecture and quality, especially cloud systems. | Product/Quality/System Architecture; maybe analysis capability rather than Authority. |
| Sustainability / energy/carbon constraints | UNEXPLORED | Can become an accepted quality/business constraint affecting workload placement and resource use. | Product/Quality/System Architecture; likely conditional. |
| Licensing / IP / open-source constraints | UNEXPLORED | Dependency/license constraints can forbid implementation choices and affect distribution. | Product/Engineering Policy/Implementation; organizational policy often upstream. |
| Safety / hazard analysis | UNEXPLORED | In safety-relevant software, hazardous outcomes and mitigations require stronger analysis than ordinary functional verification. | Product/Domain/Quality + conditional safety analysis; domain-dependent. |
| Human factors / usability | PARTIAL | Product/interface cover observable behavior, but explicit usability quality and validation have not been researched. | Product/Interface/Quality/Verification. |
| Data quality / provenance / lineage | PARTIAL | Pilots use provenance heavily, but no generic model distinguishes semantic evidence quality from physical data design. | Domain/Data/Quality/Verification; needs study. |
| AI/ML-specific lifecycle | UNEXPLORED | Model/data provenance, evaluation, nondeterminism, drift, prompt/tool trust and model updates create decision classes absent in ordinary deterministic apps. | Conditional extension across Product/Data/Quality/Security/Verification/Operability; separate research needed if Harness targets AI systems. |
| Multi-tenancy / isolation | UNEXPLORED | Tenant identity, isolation, quotas, noisy-neighbor behavior and data partitioning cross security/domain/data/quality boundaries. | Product/Domain/Security/System/Data/Quality; useful stress case. |
| Offline/sync/eventual connectivity | UNEXPLORED | Conflict resolution, local authority, reconciliation and stale data are semantic/architecture concerns. | Product/Domain/Application/Data/System; useful stress case. |
| Deprecation / retirement / data exit | UNEXPLORED | End-of-life, export, deletion and consumer transition are lifecycle decisions not represented by implementation completion alone. | Product/Interface/Data/Implementation/Policy. |

## Highest-value research themes

### P0 — Reliability and failure-semantics closure

Operability research intentionally routed retry/timeout/degradation elsewhere, but Harness has not yet established a general owner model for those decisions.

Questions:
- who owns retryability and idempotency;
- who owns timeout/cancellation semantics;
- where failure containment and bulkheads live;
- when degraded service is a Product outcome versus Quality/System Architecture;
- recovery/reconciliation after uncertain state change;
- whether a conditional RELIABILITY-DESIGN boundary is atomic or merely fragments existing owners.

This is the largest known hole because coding agents and frameworks routinely introduce retries/timeouts/default recovery behavior.

### P0 — Deployment, release and evolution

Implementation Design currently owns sequencing/migration concerns, but this may be too broad for systems with independent deployment lifecycle.

Research together:
- environment/deployment topology;
- rollout/rollback/roll-forward;
- database/data migrations;
- API compatibility/versioning;
- feature transitions;
- zero/low-downtime constraints;
- configuration/secret changes across releases;
- retirement/decommissioning.

Atomicity question: one DEPLOYMENT/EVOLUTION boundary, multiple existing owners, or project-specific Authorities?

### P1 — Data governance and privacy lifecycle

Security does not fully own privacy. Research:
- classification/minimization;
- retention/deletion;
- subject/export requirements;
- residency;
- provenance/lineage;
- derived-data lifecycle;
- backup copies and deletion;
- audit evidence versus business history.

Test whether these are Product/Data/Security/Compliance inputs or justify a conditional DATA-GOVERNANCE boundary.

### P1 — Concurrency, distributed consistency and resource pressure

Stress the current Domain/Application/System/Data/Quality split with:
- duplicate messages/requests;
- ordering;
- optimistic concurrency;
- transaction boundaries;
- eventual consistency;
- reconciliation;
- queues/backpressure;
- quotas and overload;
- split-brain/partial dependency failure.

This is likely best researched using a deliberately distributed/event-driven validation case rather than current simple pilots.

### P1 — Performance/capacity and economic constraints

Quality Design already exists, but it has not been tested against explicit workload/capacity/cost decisions.

Research:
- workload model and growth assumptions;
- latency/throughput/resource budgets;
- capacity and headroom;
- scale-up/out triggers;
- cost ceilings/unit economics;
- workload placement;
- performance evidence and regression budgets.

Do not create FinOps concepts in Core unless project decision semantics require them.

### P2 — Human-interface quality

Jointly investigate:
- accessibility;
- usability;
- localization/internationalization;
- locale/time-zone presentation;
- assistive technology and keyboard/focus semantics.

Likely outcome: Product/Interface/Quality/Test coverage plus reusable skills rather than new Core.

### P2 — Compliance, licensing and organizational constraints

Research these primarily as **sources of normative constraints** that must be routed to existing semantic owners. Avoid a catch-all COMPLIANCE Authority unless it passes atomicity.

### P2 — Recovery and continuity

Backup/restore, RPO/RTO, disaster recovery, state reconstruction and operational continuity deserve an explicit validation case with durable business state.

### P3 — Specialized system classes

Only if Harness intends to support them:
- safety-critical systems;
- AI/ML/agentic systems;
- multi-tenant SaaS;
- offline-first/synchronizing systems;
- real-time/embedded systems.

These are excellent adversarial cases for testing whether the generic Core remains sufficient.

## Cross-cutting meta-gap: lifecycle/change design

A repeated pattern across deployment, migration, compatibility, key rotation, schema evolution, data retention and retirement is that Harness is strongest at designing a target state, but less explicitly studied for **safe transition between accepted states**.

This may be more fundamental than any individual missing topic.

Research question:

> Does Harness need an explicit reusable model for Change/Transition Design, or are transition contracts already coherently owned by each semantic Authority plus Implementation Design?

A transition is material when both old and new states/contracts coexist, ordering matters, rollback is constrained, or irreversible effects exist. This should be investigated before inventing a CHANGE-DESIGN Authority.

## Cross-cutting meta-gap: policy provenance

Security, privacy, compliance, accessibility, licensing, cost and organizational engineering rules may originate outside the project. Harness currently has Engineering Policy, but it has not been studied as a general mechanism for:
- external normative source provenance;
- applicability;
- precedence/conflict;
- project adoption/waiver;
- expiry/review;
- routing a policy constraint to the Authority that owns the affected semantics.

This may justify a policy-ingestion/routing skill without changing Core.

## Cross-cutting meta-gap: decision lifecycle after implementation

Current graph strongly addresses pre-code closure. Less studied:
- what invalidates an accepted artifact after production evidence;
- how incidents/telemetry/user evidence reopen Questions;
- how architecture decisions are superseded;
- how compatibility/deprecation windows are represented;
- how design knowledge follows system evolution.

This is not necessarily a new Authority. It may be missing Harness lifecycle mechanics.

## Recommended research program

1. **Reliability/failure semantics** — highest immediate risk and direct continuation of Operability.
2. **Deployment/release/evolution/change transitions** — tests whether Implementation Design is overloaded.
3. **Data governance/privacy lifecycle** — deliberately separate privacy from generic Security.
4. **Concurrency/distributed consistency/resource pressure** — use a new adversarial distributed case.
5. **Performance/capacity/cost** — validate Quality Design under measurable operational/economic constraints.
6. **Policy provenance/compliance routing** — determine how external norms enter the graph.
7. **Human-interface quality** — accessibility/usability/i18n when a UI project is available.
8. Specialized stress cases only after the general boundaries above stabilize.

## Current conclusion

Harness has good coverage of **what a system means, how it is structured, how it is secured, how runtime evidence is exposed, how it is verified, and how implementation is planned**.

The largest unvalidated territory is **how systems survive failure and change over time**: resilience, concurrency, deployment, migration, compatibility, recovery, data lifecycle and retirement.

Therefore the next research should not be another broad catch-all Authority. The best next experiment is a combined **Reliability + Change/Evolution boundary study**, with atomicity tests determining whether these remain distributed responsibilities or reveal one or more missing conditional Authorities.
