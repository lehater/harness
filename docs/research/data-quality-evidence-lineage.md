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


## Real-project validation

### Nutrition Management: BLS nutrient evidence

Evidence used: accepted canonical domain and verification design only. Production code was not inspected.

Nutrition is a strong adversarial case because "data quality" is already decomposed into semantic decisions rather than one score:

- nutrient identity is semantic and cannot be inferred from display names;
- unit and 100 g edible-portion basis are part of quantity meaning;
- source states known, zero, trace, below-quantification, below-detection, ambiguous-limit and missing remain distinct;
- only known and zero are quantitatively usable;
- provenance is retained per nutrient data point where available;
- source lexical numeric representation is preserved separately from normalized Decimal semantics;
- derived measures identify formula/version;
- unsupported target mappings remain unsupported rather than approximated;
- verification separately proves preservation of evidence states, normalization semantics and provenance.

This demonstrates that evidence quality is often **domain truth**. A generic Data Quality owner could not decide whether VITAA and VITA are equivalent, whether trace may become zero, whether a safety limit is comparable, or whether per-100-ml data can replace per-100-g data. Food Knowledge/Nutrition Targeting own those decisions.

It also demonstrates consumer-specific fitness. A Product Card may exist while being non-executable for quantitative nutrition planning because edible-gram conversion is unavailable. "Quality" is therefore not an intrinsic scalar property of the record; fitness depends on the consuming capability.

Nutrition verdict: PASS for cross-Authority ownership; FAIL for a generic DATA-QUALITY-DESIGN Authority.

### NAPMS: provenance, temporal validity and persistence

Evidence used: accepted persistence, technical-representation and quality artifacts only. Production code/tests were not used as design truth.

NAPMS uses provenance in several distinct semantic roles:
- Resource and connectivity facts retain provenance;
- InteractionContractRevision is append-only and retains provenance;
- policy submission, decision and retirement have separate provenance;
- temporal facts have valid-from/valid-to semantics;
- technical representation standardizes only an extensible provenance envelope: source + recordedAt + optional detail;
- Data Design chooses jsonb storage but does not own owner-specific provenance meaning;
- Quality Design requires complete materialization and forbids silently partial success.

This is a second counterexample to a generic Data Quality owner. Interface Design owns shared provenance representation, Data Design owns physical storage/integrity, domain owners own the meaning of the provenance-bearing fact, and Quality Design owns architecture-significant completeness/integrity requirements.

NAPMS verdict: PASS for cross-Authority ownership.

## Adversarial scenarios

### A — missing value

Missingness is not universally a quality defect.

In Nutrition, missing nutrient evidence is an explicit domain state and prevents deterministic quantitative use without becoming zero. In another consumer, an optional field may be valid.

Rule: the semantic owner defines missingness; the consumer/Quality contract defines fitness.

### B — stale/fresh data

Freshness has at least three meanings:
1. source fact has an effective/valid time;
2. consumer requires data no older than a threshold;
3. accepted engineering knowledge about the source/constraint has been superseded.

(1) is domain/application semantics, (2) is consumer/domain/Quality constraint, (3) is Capability Lifecycle. They must not share one generic stale flag.

### C — conflicting sources

Two sources can disagree while both records are structurally valid.

Source precedence, reconciliation or preservation of disagreement is a domain/application decision. Data Design may preserve both facts; it cannot choose semantic truth merely because one arrived later.

### D — transformation formula changes

If an accepted nutrient formula changes, the formula Capability receives a new acceptance identity and dependent accepted knowledge can become STALE through Capability Lifecycle.

Historical calculated rows may require recomputation/migration through Change Transition Design depending on persistence semantics.

Lineage evidence identifies which outputs used which formula; it does not itself decide the new formula.

### E — corrupted persistence with unchanged semantics

If stored bytes violate an accepted representation/integrity constraint while all accepted design remains unchanged, this is a realization/verification/operational failure. It must not mark the semantic Capability STALE.

This mirrors the supply-chain distinction between accepted design and acquired-artifact evidence.

## Semantic provenance vs realization lineage

A critical boundary emerged:

**Semantic provenance** is part of accepted application/domain truth when source identity/context changes the meaning, admissibility or auditability of a datum.

**Realization lineage** is evidence describing how a concrete stored/derived/output value was produced.

A lineage record may support verification, debugging, audit or recomputation without becoming CanonicalArtifact design truth.

Therefore Harness must not require one universal lineage graph.

## Data-quality dimensions

Completeness, accuracy, precision, timeliness, consistency, uniqueness and validity are useful analysis lenses, not automatically project requirements.

For each dimension the analysis must ask:
- quality of what semantic fact?
- for which consumer/use?
- according to which accepted rule?
- owned by which Authority?
- proved by what evidence?

A generic checklist must not invent thresholds.

## Refined verdict

P0: no DATA-QUALITY-DESIGN, PROVENANCE-DESIGN or LINEAGE-DESIGN Authority.

P0: do not add generic DataRecord, Provenance, Lineage or QualityScore entities to Core v0.

P0: do not conflate source/effective-time freshness, consumer freshness requirements and Capability Lifecycle staleness.

P1: canonicalize a reusable Data Evidence / Fitness Analysis method if contradiction review confirms it does not duplicate Verification, Data Design, Quality Design or domain ownership.

P1: semantic provenance belongs to the Authority owning the fact when provenance affects meaning/admissibility.

P1: realization lineage remains project/integration evidence unless the owning semantic model explicitly makes lineage part of accepted truth.

P1: fitness-for-use is consumer-relative and must trace to an accepted constraint; it is not an intrinsic global score.

P2: project-native lineage systems should be referenced rather than copied into Harness.
