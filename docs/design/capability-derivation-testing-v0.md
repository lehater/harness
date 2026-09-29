# Capability derivation testing v0

Status: implemented experimental design; research task closed in
`docs/research/capability-derivation-testing-closure-v1.md`.

## Purpose

Test whether one Authority produces downstream engineering knowledge from
accepted upstream knowledge without silent semantic loss or cross-Authority
guessing.

The existing Scenario Suite remains the orchestration layer.

## Test subjects

Two subjects are intentionally separate:

1. **Production test** — one Authority realizes one ProductionContract and
   produces a Capability.
2. **Derivation-edge test** — one direct upstream Capability supplies semantic
   input to one downstream ProductionContract.

Downstream sufficiency is therefore relative to a concrete downstream
production, not an absolute property of a Capability.

## Derivation model

```text
accepted upstream semantic surface
        |
        v
Semantic Input Contract
        |
        +-- missing input -> Question to source Authority
        |
        v
downstream Authority work
        |
        v
candidate semantic surface
        |
        v
Derivation Evidence
        |
        v
Derivation Evaluation
```

Every applicable accepted upstream semantic atom must be accounted for by a
derivation link or an explicit disposition.

Supported deterministic relations in v0:

- `PRESERVES`
- `TRANSFORMS`
- `CONSTRAINS`
- `REALIZES`

The relation does not require one-to-one mapping. One source may map to several
targets and several sources may combine into one target.

## Failure classification

- **MISSING_REQUIRED_INPUT** — the downstream production contract requires
  semantic input absent from the upstream Capability. The Question belongs to
  the source Capability Authority.
- **UNDISPOSITIONED_SOURCE** — upstream knowledge exists but the downstream
  candidate did not account for it. This is a downstream production defect and
  does not manufacture an upstream Question.
- invalid/unknown trace references are process/evidence defects.
- `QUESTION` disposition represents unresolved downstream-owned derivation
  work and blocks the target Capability.

This preserves the Harness rule that unknown upstream knowledge is not invented
downstream.

## Oracles

- deterministic oracle: ids, ownership, dependency edge, trace coverage,
  dispositions and Question routing;
- invariant/property oracle: mutations, alternative-valid designs and
  irrelevant-input stability;
- semantic/evaluator oracle: request-bound EVALUATOR/HUMAN judgement when a
  declared transformation cannot be validated structurally;
- human/expert oracle: benchmark/test-pack authoring and calibration.

Literal full-artifact snapshots are not the primary oracle.

## First experiment

The first executable slice is `task-model -> interaction-design`.

It proves:

- complete derivation is accepted;
- removing recovery derivation is rejected;
- removing required upstream recovery creates a Question for
  `APPLICATION-DESIGN`;
- the dependent interaction production waits rather than guessing;
- two materially different Interaction Design shapes can both be accepted;
- irrelevant source noise does not change the result.

The scenario also records that the older frontend structural closure can be
complete while semantic derivation coverage is still unknown. The two checks
serve different purposes.

## Integration

`semantic.derivation` is a Scenario Suite driver backed by
`semantic_derivation.py`. No second test runner or CapabilityTestSuite is
introduced.

A higher-level capability-test-pack DSL should be added only if repeated
scenario data demonstrates real duplication.


## Mutation classes

Reusable packs should classify semantic mutations rather than expose only raw
JSON-patch operations:

- omission: fact, requirement, relation, information, outcome or recovery;
- ambiguity or contradiction;
- constraint change;
- provenance/owner drift;
- stale prerequisite;
- irrelevant noise;
- alternative collapse or preselected solution.

`data.patch` remains the execution primitive. The classification belongs to
scenario/test data, not to a second mutation engine.

## Metrics

Do not collapse quality into one score. Useful independent measures are:

- gap-detection recall and false-positive rate;
- Question owner-routing accuracy;
- root-cause localization accuracy;
- blocking precision;
- derivation mutation kill rate by mutation class;
- alternative-valid acceptance;
- irrelevant-input stability;
- cross-Authority invention findings when a semantic/evaluator oracle is used.

The deterministic evaluator exposes required/covered/disposed/unresolved
counts. Scenario steps may additionally opt into benchmark labels. The Scenario
Suite aggregates independent corpus metrics such as mutation detection,
false-positive control, ambiguity handling, Question-owner routing,
root-cause localization, blocking behavior, alternative-valid acceptance,
selective revalidation and semantic-truth detection, including rates by
mutation class.

These are regression-corpus rates, not estimates of universal recall/precision.
Harness deliberately does not collapse them into one quality score.

## Semantic judgement

A derivation contract may require semantic judgement. Harness creates a
deterministic request bound to the exact required source assertions, referenced
target assertions, link set and required checks. EVALUATOR or HUMAN evidence is
accepted only for that request. A changed target/source/link therefore rejects
stale judgement evidence.

This proves request binding and fail-closed behavior. It does not prove reviewer
independence or that an evaluator is infallible. Stronger execution/trust
attestation remains a separate concern.

## Selective lifecycle revalidation

Accepted semantic admission publishes fingerprints for its semantic assertions.
An ACCEPTED derivation evaluation publishes fingerprints only for source atoms
actually consumed by derivation links. Downstream admission may persist these
under `accepted_prerequisite_semantics`.

Lifecycle then uses two modes:

- no authoritative semantic baseline -> conservative prerequisite
  acceptance-id comparison;
- exhaustive consumed semantic baseline -> stale only when a consumed atom
  changes, disappears, or its upstream Capability is itself non-current.

Selective currentness is fail-closed. A derivation contract must explicitly
declare `lifecycle_dependency.exhaustive: true`, and every upstream semantic
assertion must be either linked as consumed or explicitly dispositioned. A
partial derivation evaluation cannot silently narrow lifecycle invalidation.

This keeps backward compatibility while preventing unnecessary cascade only
when the dependency surface is proven complete.

## Derivation test coverage

`derivation_test_coverage.py` evaluates direct Engineering Graph production
dependencies against two reusable proof forms:

- a tested knowledge-kind edge, which allows one generic scenario to cover the
  same semantic transfer class across projects;
- an exact capability-edge test for project-specific behavior.

An edge may alternatively be explicitly `NOT_APPLICABLE` with rationale.
Anything else remains a coverage gap. Coverage is auto-discovered from the
actual executable `semantic.derivation` steps in scenario files; optional
`derivation_edges` metadata must match those executable graph/contract edges
exactly. A scenario name or declaration alone cannot satisfy coverage.

The evaluator is exposed through the Scenario Suite as
`semantic.derivation_test_coverage`; it does not introduce a second test
runner. The three current repository example Engineering Graphs are guarded by
full direct-edge coverage scenarios.

## Closure boundary

The capability-derivation testing research task is complete. The reusable
mechanisms are present for deterministic derivation coverage, request-bound
semantic judgement, fail-closed selective lifecycle invalidation,
executable-proof-derived edge coverage and benchmark corpus metrics.

Further live evaluation of a concrete semantic evaluator is a separate research
stage: Live Calibration Validator. See
`docs/research/capability-derivation-testing-closure-v1.md`.
