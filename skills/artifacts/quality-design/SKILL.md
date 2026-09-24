---
name: quality-design
description: "Use for actionable CREATE work that makes architecture-significant quality constraints explicit without inventing numeric targets or turning generic non-functional checklists into requirements."
---

# Quality Design

## Trigger

Use when actionable work has `knowledge_kind: quality-design` and performance, availability, scale, staleness tolerance, reliability or another realization quality constraint needs independent pre-code ownership.

## Inputs

- accepted Product Requirements and acceptance semantics;
- accepted Domain/Application behavior;
- accepted external/deployment constraints where applicable;
- relevant analysis evidence (performance, reliability, concurrency, obligations) when already available.

## Read boundary

Start from accepted consumer/product/design needs. Existing benchmarks, infrastructure limits, framework defaults and generic NFR checklists are evidence only unless explicitly accepted.

## Procedure

1. Enumerate quality dimensions that can materially constrain realization for the selected scope.
2. Trace each applicable constraint to an accepted upstream need or external constraint.
3. Express measurable target/boundary only when evidence supplies one; never invent latency, throughput, availability, RPO/RTO or dataset scale.
4. For correctness-adjacent concerns (staleness tolerance, boundedness, degradation, recovery), own only measurable/qualitative quality targets. Route interacting-execution correctness semantics to CONCURRENCY-CONSISTENCY-DESIGN and separate every target from its implementation mechanism.
5. Classify non-applicable or currently unquantified concerns explicitly; use DEFERRED_NONBLOCKING only with a reopening condition and when current implementation does not need the missing value.
6. Route product-visible policy upstream, runtime evidence to Operability, structural response to System, concurrent-state correctness to CONCURRENCY-CONSISTENCY-DESIGN, physical realization to Data/Implementation and proof to Verification.
7. State implementation freedoms.
8. Produce/register the project-native quality contract and reevaluate.

## Stop conditions

Stop and create/route a Question when implementation needs a numeric or qualitative target that has no accepted owner; two accepted quality constraints conflict; or a supposedly deferred concern is actually needed to choose current correctness semantics.

## Output contract

Useful content may include:
- applicable quality constraints;
- measurable targets/boundaries when accepted;
- staleness/reliability/capacity and other quality constraints;
- NOT_APPLICABLE/DEFERRED_NONBLOCKING decisions with reopening conditions;
- downstream architecture/operability/verification obligations;
- implementation freedoms;
- Questions.

## Acceptance checks

- no numeric target is invented;
- deferred items do not hide current coding decisions;
- quality constraints do not re-own product/domain behavior;
- architecture/implementation consumers can tell which qualities constrain them;
- verification can derive evidence from the accepted contract.

## Registration

Register under QUALITY-DESIGN when the constraints have independent lifecycle/public consumers; otherwise keep simple expectations with their existing owner.

## Human projection

Prefer a compact constraint/applicability table plus rationale over a generic NFR catalog.
