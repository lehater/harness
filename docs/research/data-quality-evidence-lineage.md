# Data Quality / Evidence / Lineage Research

Status: research candidate. No Core change.

## Question

Does Harness need a new Authority or Core concept for data quality, evidence quality, provenance/lineage and fitness-for-use of data consumed or produced by an application?

## Initial distinction

The phrase "data quality" hides several independently owned questions:

1. semantic correctness — what a datum means;
2. source/evidence identity — where it came from and what observation/assertion it represents;
3. representation validity — whether encoding/schema/unit/basis is valid;
4. fitness for a specific use — whether quality is sufficient for a consumer decision;
5. transformation lineage — which accepted inputs and rules produced a derived datum;
6. operational integrity — whether realized storage/transport preserved accepted data;
7. verification evidence — how conformance is proven.

These must not be collapsed into one generic quality score.

## Candidate DATA-QUALITY-DESIGN Authority

### Semantic cohesion — likely FAIL

A generic owner would need to decide domain meaning, source admissibility, representation constraints, consumer-specific fitness, persistence integrity and proof strategy. Those are different engineering decisions.

### Independent change — likely FAIL

A source may remain semantically valid while a consumer raises freshness/precision requirements. Storage representation can change without changing evidence semantics. A transformation can change while source identity remains fixed.

### Public producer/consumer contract — not demonstrated

Consumers rarely need "data quality" in the abstract. They need concrete accepted properties: provenance, precision, completeness rule, freshness, admissible evidence state, reconciliation rule or transformation semantics.

Initial hypothesis: no DATA-QUALITY-DESIGN Authority. Data-quality closure is cross-Authority.

## Ownership hypothesis

- Product/Domain owns meaning and business fitness rules.
- Domain/Application owns admissibility and transformation semantics when they affect decisions.
- Data Design owns persistence representation/integrity constraints.
- Interface Design owns boundary representation/validation semantics.
- Quality Design owns measurable cross-cutting quality targets when architecture-significant.
- Security/Obligation analyses constrain confidentiality, integrity, provenance or retention where applicable.
- Operability owns runtime evidence needed to diagnose data-flow failures, not data truth.
- Verification owns proof against accepted data/evidence constraints.

## Provenance vs lineage

Provenance answers where an assertion/value came from and under what source context.
Lineage answers how a value/materialization was derived through transformations and dependencies.

Neither is automatically an Authority. They may be domain truth when source identity affects semantics, or realization evidence when used only to audit processing.

The same representation must not be forced into one global meaning.

## Core hypothesis

No new Core entity is justified yet.

Capability can express accepted provenance/fitness/transformation knowledge.
CanonicalArtifact can materialize it.
Engineering Graph can express semantic prerequisites.
Capability Lifecycle can invalidate accepted derived knowledge when prerequisite acceptance changes.
Project-native provenance/lineage evidence can remain integration evidence.

## Research program

1. Test the ownership decomposition against Nutrition Management, especially BLS nutrient evidence and normalization.
2. Test against NAPMS for persistence/interface/materialization semantics.
3. Adversarially test freshness, missingness, conflicting sources, transformation changes and corrupted realization.
4. Distinguish semantic lineage from build/supply-chain provenance and from Capability Lifecycle.
5. Decide whether a reusable DATA-EVIDENCE-ANALYSIS method is warranted.
