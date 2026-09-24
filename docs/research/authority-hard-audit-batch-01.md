# Authority hard audit — batch 1

Method: `authority-boundary-knowledge-flow-v1` plus applicability atomicity. Batch size is **4 Authorities**: small enough to reconstruct decision→knowledge→consumer flow independently and falsify neighboring boundaries, while large enough to expose overlap. Twenty Authorities therefore require five passes.

Verdicts: KEEP = boundary survives; SPLIT = non-atomic; MERGE/REDEFINE = current identity is not independently justified; WATCH = evidence insufficient for canonicalization.

## DISCOVERY — KEEP

Decision identity: accept problem observations, actors, outcomes and provenance without deciding product behavior.

Accepted knowledge: problem evidence and unresolved discovery questions.

Consumers: Product Requirements consumes accepted problem evidence to form product intent/scope. Necessity is real when requirements must be traceable to observed problem evidence. Encapsulation holds because Product Requirements need not own discovery provenance/research reasoning.

Applicability atomicity: evidence domains may differ, but they remain one provenance/evidence decision class until independent consumers/lifecycles are demonstrated.

Falsification: merge with Product Requirements only when evidence has no independent provenance, lifecycle or consumer value.

Verdict: KEEP.

## PRODUCT-REQUIREMENTS — KEEP, boundary wording needs sharper policy split test

Decision identity: decide externally observable product intent, scope, constraints and acceptance expectations.

Accepted knowledge: product intent/behavior/acceptance contract.

Consumers: Domain Use Case, Application, System/Quality/Verification and other design Authorities consume this contract. They cannot correctly choose realization while inventing product intent themselves. Encapsulation is strong.

Applicability atomicity: baseline product-intent decision is atomic enough. However catalog split_when mentions product policy; policy that independently governs authorization/pricing/eligibility may become its own semantic decision family if it has independent accepted outputs/consumers/lifecycle.

Verdict: KEEP. Add falsification fixture for independent product-policy ownership before canonicalization.

## STRATEGIC-DOMAIN-DESIGN — SPLIT

Current identity combines:
1. problem-space/domain strategy: subdomain landscape, strategic classification/investment;
2. model-context strategy: where models/languages apply, context relationships and translation contracts.

Both produce accepted knowledge with different consumers. Each can be REQUIRED while the other is N/A. They can evolve independently and consumers can use one without the other.

A single applicability bit therefore loses project truth.

Verdict: SPLIT into candidate `DOMAIN-STRATEGY` and `MODEL-CONTEXT-STRATEGY`. Current Authority fails applicability atomicity.

## DOMAIN-USE-CASE-DESIGN — WATCH / likely merge unless stronger consumer evidence is produced

Decision identity claimed: stable domain-focused observable behavior before tactical modeling.

Knowledge output claimed: domain use-case behavior.

Potential consumers: Tactical Domain Design and Application Design.

Hard failure: current catalog does not yet prove when this knowledge is independently accepted rather than being either Product Requirements behavior or Application orchestration. “Needs an explicit stable contract” is circular applicability evidence. Independent lifecycle is plausible but not demonstrated by the current boundary.

To KEEP, require a fixture where:
- Product Requirements remain stable;
- application orchestration can change;
- a domain behavior/use-case contract remains independently accepted;
- Tactical/Application consumers demonstrably require that contract without co-owning it.

Verdict: WATCH. Do not canonicalize as-is without this falsification fixture.

## Batch result

- DISCOVERY: KEEP
- PRODUCT-REQUIREMENTS: KEEP + policy split falsification
- STRATEGIC-DOMAIN-DESIGN: SPLIT
- DOMAIN-USE-CASE-DESIGN: WATCH

P1: STRATEGIC-DOMAIN-DESIGN is definitely unsafe as a registry applicability unit.
P1: DOMAIN-USE-CASE-DESIGN lacks sufficient independent consumer/lifecycle proof.
