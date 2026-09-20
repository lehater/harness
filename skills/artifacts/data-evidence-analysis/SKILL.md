---
name: data-evidence-analysis
description: "Use to analyze application/domain data evidence, provenance, transformation lineage and consumer-relative fitness, routing gaps without creating a generic data-quality owner or score."
---

# Data Evidence / Fitness Analysis

## Trigger

Use when material application data must be checked for semantic provenance, missingness, freshness, transformation lineage, conflicting sources, precision/completeness or fitness for an accepted consumer/use.

## Inputs

- accepted semantic capabilities and owning Authorities;
- relevant Interface, Data and Quality design;
- accepted consumer/use requirements;
- project-native source/provenance/lineage evidence where available;
- applicable Verification obligations.

## Read boundary

Accepted canonical design is authority. Production data, database contents, ETL lineage, profiler output and monitoring are evidence unless their semantic meaning has been explicitly accepted by the owning Authority. Generic data-quality dimensions are recall lenses, not automatic requirements.

## Procedure

1. Identify the concrete semantic fact/data flow and its owning Authority.
2. Identify the consumer/use whose fitness is being evaluated.
3. State accepted meaning, admissible evidence states, units/basis/identity and source semantics where applicable.
4. Distinguish semantic provenance from realization lineage.
5. Identify accepted transformation/reconciliation/precedence semantics; do not invent them.
6. Evaluate applicable completeness, validity, precision, freshness, consistency, uniqueness or accuracy concerns only against accepted rules.
7. Distinguish source/effective time, consumer freshness requirement and Capability Lifecycle currentness.
8. Trace representation/persistence constraints to Interface/Data Design.
9. Trace architecture-significant measurable targets to Quality Design.
10. Trace proof/evidence strategy to Verification.
11. Route acquisition/integrity concerns for external sources through External Dependency Analysis when applicable.
12. Record COVERED, NOT_APPLICABLE, DEFERRED_NONBLOCKING with reopening condition, or QUESTION.

## Stop conditions

Stop and route a QUESTION when the analysis would otherwise decide semantic equivalence, source authority/precedence, missing-value meaning, admissibility, transformation formula, reconciliation policy, consumer fitness threshold or another upstream semantic constraint.

## Output contract

Produce data-evidence coverage containing semantic fact/flow, owner, consumer/use, accepted evidence/provenance/transformation constraints, applicable fitness concerns, evidence references, routed gaps and explicit coverage state.

## Acceptance checks

- every quality concern is attached to a concrete fact/flow and consumer/use;
- no generic quality score substitutes for accepted constraints;
- missing/unknown is not silently converted to zero/default;
- semantic provenance and realization lineage remain distinct;
- freshness meanings remain distinct;
- conflicting sources are not resolved by arrival time unless accepted semantics say so;
- persistence/interface representation does not become semantic ownership;
- verification strategy is not invented by the analysis;
- project-native provenance/lineage history is referenced rather than duplicated;
- Capability Lifecycle is used only for accepted engineering knowledge currentness.

## Registration

Register as a reusable cross-Authority analysis skill. Do not create DATA-QUALITY-DESIGN, PROVENANCE-DESIGN, LINEAGE-DESIGN or DATA-EVIDENCE-ANALYSIS Authority solely to host this analysis.

## Human projection

Prefer a compact coverage view by semantic fact/data flow and consumer, showing provenance/transformation/fitness constraints, evidence and routed gaps. Avoid generic dashboard scores without accepted thresholds.
