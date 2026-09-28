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
