# Engineering coverage audit v2

Status: research inventory after the first closure program. This audit compares the original gap map with completed research and identifies the next unresolved engineering territories.

## Scope

The audit treats a concern as covered only when Harness has either:
- an atomic Authority boundary;
- an explicit cross-Authority ownership/closure rule plus reusable analysis;
- or evidence that the concern is implementation freedom after accepted upstream constraints.

A named discipline is not evidence for a new Authority.

## Closure since v1

| v1 concern | v2 state | Result |
| --- | --- | --- |
| Reliability / resilience / fault tolerance | CLOSED | Cross-Authority reliability analysis; no Reliability Authority. |
| Deployment / release / migration / compatibility | CLOSED | Conditional CHANGE-TRANSITION-DESIGN owns material transition-state validity. |
| Concurrency / consistency / ordering / backpressure | CLOSED | Cross-Authority closure; no generic Authority. |
| Data lifecycle / privacy / retention / governance | CLOSED | Cross-Authority lifecycle analysis; no Data Governance Authority. |
| Compliance / regulatory policy provenance | CLOSED | Conditional OBLIGATION-ANALYSIS for independently governed normative-source applicability/routing. |
| Disaster recovery / backup / restore / continuity | CLOSED | Cross-Authority recovery closure; no Recovery Authority. |
| Performance / capacity / scalability / cost | CLOSED | Atomic measurable constraint boundary is existing QUALITY-DESIGN; reusable analysis. |
| Resource pressure / overload | CLOSED | Covered by concurrency/backpressure + performance/capacity + reliability ownership. |

## Important branch-integration caveat

The conclusions above exist in research branches/PRs and are not yet all present in main. This audit evaluates the researched Harness model, not only current main contents. Canonical merge should happen only after cross-branch contradiction review.

## Remaining general-purpose gaps

### P0 — Decision lifecycle / production feedback / reopening

Harness is strong at pre-code closure but still lacks a researched lifecycle for accepted knowledge after implementation and production evidence.

Questions:
- What invalidates an accepted Capability?
- How does an incident, telemetry result, failed verification, vulnerability disclosure, dependency change or user evidence reopen a Question?
- How are superseded artifacts/capabilities represented without rewriting history?
- How does downstream impact propagate after accepted knowledge becomes stale?
- Is this an Authority at all, or graph/lifecycle mechanics above Core?

This is now the highest-value general gap because every other closure assumes accepted knowledge can later change.

### P0 — External dependency / acquisition / supply-chain lifecycle

Security research covered security controls, and Obligation Analysis covers normative sources, but Harness has not yet studied dependencies/providers as engineering knowledge with lifecycle:
- third-party API/service assumptions;
- package/runtime/database/solver dependencies;
- provenance and trust;
- supported versions;
- update policy;
- vulnerability/update response;
- quotas/rate limits;
- provider deprecation;
- substitution/exit;
- build provenance/SBOM;
- license constraints routed through Obligation Analysis.

This may decompose across System Architecture, Interface, Security Analysis, Engineering Policy, Change Transition, Obligation Analysis and Implementation. A generic SUPPLY-CHAIN Authority is not assumed.

### P1 — Human-interface quality: accessibility / usability

Product, Interface, Quality and Verification exist, but no explicit research has tested:
- keyboard/focus/assistive semantics;
- accessible names/relationships/status;
- contrast/reflow/input alternatives;
- cognitive/usability constraints;
- user research/evidence feeding design;
- accessibility obligations entering through OBLIGATION-ANALYSIS.

Likely result is closure across existing owners, but this should be demonstrated against a UI-heavy case.

### P1 — Internationalization / localization / temporal presentation

Still unresearched:
- locale/language;
- translation ownership;
- number/currency formatting;
- time zones/calendars;
- collation/search;
- local legal/content variants;
- domain time versus presentation time.

This area is dangerous because frameworks frequently choose defaults that can alter product/domain meaning.

### P1 — Data quality / evidence / lineage

Data-governance research covered purpose/lifecycle/provenance routing, but not the independent question of data fitness:
- source confidence;
- completeness;
- freshness;
- uncertainty;
- correction;
- lineage of derived facts;
- acceptance thresholds;
- downstream behavior when evidence is insufficient.

Nutrition already contains rich source/evidence semantics and is a strong validation project.

### P1 — Build/reproducibility/artifact provenance

Implementation Design and Engineering Policy cover parts, but Harness has not explicitly established ownership for:
- deterministic/reproducible builds;
- dependency lock/source provenance;
- generated artifacts;
- build attestations;
- artifact identity;
- environment/toolchain pinning;
- binary/container provenance;
- release artifact traceability.

This may be part of supply-chain research rather than a separate Authority.

## Specialized stress cases

These should not be promoted to baseline Authorities without project evidence.

### P2 — Multi-tenancy / isolation

Useful adversarial case for Domain + Security + Data + Quality + System boundaries: tenant identity, isolation, quotas, noisy-neighbor behavior, per-tenant lifecycle and data partitioning.

### P2 — Offline-first / synchronization

Useful adversarial case for concurrency/change/reliability: local authority, conflict resolution, stale data, merge semantics, replay and reconciliation.

### P2 — AI/ML/agentic systems

Potentially introduces model/data/prompt/tool provenance, probabilistic quality, evaluation sets, drift, safety boundaries and model-change lifecycle. Research only if Harness intends explicit support.

### P2 — Safety/hazard analysis

For safety-relevant products, hazard analysis may form an analysis Authority analogous to Security/Obligation Analysis. Requires a real safety case; ordinary business applications do not justify it.

### P3 — Real-time / embedded / hardware-constrained systems

Potential stress test for timing, resource budgets, hardware interfaces, safety and deployment topology.

## Topics now considered adequately routed

The audit no longer treats the following as independent gaps:
- logging, metrics and tracing — OPERABILITY-DESIGN;
- configuration — distributed by semantic owner/System/Implementation;
- error handling — distributed by semantic owner and interface/application boundaries;
- retry/timeout/idempotency — reliability closure;
- overload/backpressure — concurrency/performance/reliability closure;
- migration/rollback/compatibility/deprecation path — CHANGE-TRANSITION-DESIGN plus semantic owners;
- privacy/retention/deletion — data-governance closure plus OBLIGATION-ANALYSIS where externally imposed;
- RPO/RTO/backup/restore — Product/Quality/Data/System/Change Transition/Verification;
- performance/cost targets — QUALITY-DESIGN;
- compliance as a catch-all — rejected; OBLIGATION-ANALYSIS only owns normative-source applicability/routing.

## Revised coverage model

Harness now has three different kinds of cross-cutting treatment:

1. **Decision Authorities** — own atomic engineering decisions, e.g. Product, Domain, System, Quality, Security Architecture, Change Transition.
2. **Analysis Authorities** — own independently valuable coverage/applicability analysis but route semantic gaps, e.g. Security Analysis and Obligation Analysis.
3. **Reusable closure analyses without Authority** — reliability, concurrency/consistency, data governance, recovery, performance/capacity.

This distinction is important: not every cross-cutting concern needs a graph node.

## Next research program

1. **Decision lifecycle / production-feedback reopening** — highest priority; tests Harness itself rather than another software concern.
2. **External dependency / supply-chain / build provenance** — closes the largest remaining implementation/acquisition risk.
3. **Data quality / evidence / lineage** — use Nutrition as primary validation.
4. **Human-interface quality** — accessibility/usability against a UI-heavy NAPMS journey.
5. **Internationalization/localization/temporal presentation**.
6. Specialized adversarial cases only after these general gaps close.

## Current conclusion

The original broad gap inventory has changed materially. The main unresolved territory is no longer runtime resilience or operational quality. Those concerns now have explicit ownership models.

The most fundamental remaining gap is **knowledge evolution after acceptance**: Harness needs evidence for how accepted engineering truth becomes stale, is superseded, reopened and propagated after production or external change.

The next experiment should therefore study **Decision Lifecycle / Evidence Feedback / Reopening / Supersession**, explicitly testing whether this belongs in an Authority, in graph mechanics above Core, or requires a minimal Core lifecycle extension.
