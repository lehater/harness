# Capability derivation testing v0

Status: experimental

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
- semantic/evaluator oracle: whether a declared transformation preserves the
  intended meaning when deterministic structure is insufficient;
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

The deterministic evaluator already exposes required/covered/disposed/unresolved
counts. Corpus-level rates require benchmark packs with expert-labelled expected
results and are intentionally not fabricated from the small bootstrap suite.

## Remaining boundary

v0 proves deterministic trace/disposition coverage. It does not independently
prove that the meaning claimed by a `TRANSFORMS` or `REALIZES` link is true.
That is the semantic/evaluator oracle boundary.

Likewise, lifecycle currentness is still Capability-acceptance-granular. A later
experiment may use consumed semantic fingerprints to avoid revalidating a
downstream Capability when only irrelevant upstream atoms changed. That change
should be justified by its own RED scenario rather than folded into v0.
