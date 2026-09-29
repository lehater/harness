# Capability derivation testing — closure

Status: completed research task.

## Problem

Determine whether Harness can test the quality of its own design process, not
only code conformance.

The subject is one Authority producing a Capability from accepted upstream
engineering knowledge. The test must distinguish:

- missing upstream knowledge;
- downstream semantic loss;
- cross-Authority invention;
- structurally complete but semantically false derivation;
- legitimate alternative designs;
- irrelevant upstream changes;
- stale downstream knowledge after relevant upstream changes.

The test must work at individual Authority/Capability stages and across an
Engineering Graph without relying on literal golden artifacts.

## Result

The research question is answered positively.

Harness now has an executable design-testing model based on:

1. Production tests for one Authority / ProductionContract.
2. Semantic derivation tests for one direct Capability dependency.
3. Deterministic checks for coverage, ownership, provenance, dispositions,
   Question routing and lifecycle state.
4. Optional request-bound HUMAN/EVALUATOR semantic judgement where structural
   evidence cannot establish meaning preservation.
5. Mutation scenarios instead of exact-output snapshots.
6. Benchmark metrics that remain separate rather than collapsing into one
   quality score.
7. Executable graph-wide derivation-test coverage derived from real
   `semantic.derivation` scenario steps.
8. Fail-closed selective lifecycle revalidation based only on exhaustive
   consumed-semantic baselines.

Scenario Suite remains the single orchestration layer. No parallel test
framework and no new Core entity were introduced.

## Proven failure classes

The executable scenarios prove at least the following behavior:

- absent required upstream knowledge -> `MISSING_REQUIRED_INPUT` and Question
  routed to the source Authority;
- present upstream knowledge silently lost downstream ->
  `UNDISPOSITIONED_SOURCE` owned by the downstream producer;
- downstream waits rather than inventing blocked upstream knowledge;
- false semantic mapping can be rejected even with structurally complete
  trace coverage;
- materially different but semantically valid downstream designs can both pass;
- irrelevant upstream semantic noise does not create false derivation failure;
- a changed consumed semantic atom makes downstream knowledge stale;
- an unconsumed upstream change does not force revalidation when the dependency
  surface is proven exhaustive;
- partial lifecycle dependency evidence cannot narrow invalidation;
- fake or invalid test registration cannot make graph coverage `COMPLETE`.

## Coverage evidence

Harness-owned example Engineering Graphs have complete direct-edge reusable test
coverage.

Pinned external validation also passes through the normal
`semantic.derivation_test_coverage` evaluator:

- Prep snapshot: 100 / 100 direct dependency edges covered.
- NAPMS snapshot: 222 / 222 direct dependency edges covered.

This means that every direct knowledge-kind transition in those pinned graphs
has a reusable executable derivation test class. It does not mean that every
concrete project artifact has been semantically proven correct.

## Benchmark evidence

Scenario Suite records independent benchmark dimensions including:

- mutation detection;
- false-positive control;
- ambiguity handling;
- Question-owner routing;
- root-cause localization;
- blocking behavior;
- alternative-valid acceptance;
- selective lifecycle revalidation;
- semantic-truth detection.

The current bootstrap semantic-judgement calibration corpus contains 14
expert-labelled cases, including valid near-miss controls and semantic defects. The deterministic
calibration scorer can compute false negatives, false positives, detection
recall, false-positive rate, accuracy and per-class accuracy from external
verdicts.

## Architectural decisions retained

- `Capability` remains accepted engineering knowledge identity.
- Semantic derivation evidence remains generated evidence above Core.
- Downstream sufficiency is relative to a concrete downstream
  ProductionContract.
- Missing upstream knowledge and downstream derivation loss are different defect
  classes.
- Semantic judgement is external to deterministic Harness semantics.
- Request binding prevents stale semantic verdict reuse.
- Selective lifecycle currentness is allowed only from an explicitly exhaustive
  dependency surface; otherwise Harness falls back to conservative
  Capability-level invalidation.
- Knowledge-kind edge coverage is reusable test-class coverage, not project
  semantic proof.

## Boundaries intentionally left open

The completed task does not solve:

- universal natural-language semantic entailment;
- universal ontology of engineering meaning;
- statistical estimates of production evaluator accuracy;
- evaluator independence or trust attestation;
- live execution of a particular model/evaluator;
- proof that expert calibration labels are universally correct.

These are not blockers for the completed design-testing mechanism.

## Next separate research task

Live Calibration Validator is a separate follow-up.

Its purpose is to run a specifically identified independent evaluator against
the labelled semantic corpus and record reproducible verdict evidence together
with evaluator identity/version/configuration.

That work should start in a new context and must not be treated as unfinished
scope of capability-derivation testing.
