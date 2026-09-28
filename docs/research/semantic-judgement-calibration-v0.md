# Semantic judgement calibration v0

Status: experimental validation protocol.

## Purpose

Measure an external semantic evaluator against expert-labelled derivation cases
without moving semantic interpretation into Harness Core.

Harness does not generate the semantic verdict. It owns:

- the labelled calibration corpus;
- prediction identity and completeness checks;
- confusion-matrix calculation;
- false-negative / false-positive reporting;
- regression scenarios around the scoring protocol.

## Corpus

Canonical bootstrap corpus:

`spec/semantic-derivation/calibration-corpus-v1.yaml`

Each case has:

- stable `id`;
- expert `expected_status`: `ACCEPTED` or `REJECTED`;
- `mutation_class`;
- source semantics;
- target semantics;
- derivation relation;
- expert rationale.

Initial semantic classes:

- semantic weakening — REJECTED;
- semantic inversion — REJECTED;
- semantic subject swap — REJECTED;
- valid paraphrase — ACCEPTED;
- valid decomposition — ACCEPTED;
- valid aggregation — ACCEPTED.

The corpus is deliberately balanced between defect cases and valid controls.
It is a bootstrap calibration set, not a claim of statistical
representativeness.

## Evaluator input

An evaluator supplies verdicts only:

```yaml
- id: semantic-weakening
  status: REJECTED
- id: valid-paraphrase
  status: ACCEPTED
```

The scorer does not accept unknown case IDs or duplicate predictions.

Missing predictions make the result `INCOMPLETE`; an evaluator cannot improve
its apparent score by omitting difficult cases.

## Scoring

`semantic_judgement_calibration.py` treats semantic defects as the positive
class:

- true positive: expert REJECTED, evaluator REJECTED;
- false negative: expert REJECTED, evaluator ACCEPTED;
- true negative: expert ACCEPTED, evaluator ACCEPTED;
- false positive: expert ACCEPTED, evaluator REJECTED.

Reported metrics:

- `detection_recall = TP / (TP + FN)`;
- `false_positive_rate = FP / (TN + FP)`;
- accuracy;
- per-mutation-class accuracy;
- explicit miss records.

A complete evaluator result is `PASS` only when all bootstrap cases match the
expert labels. Mismatches return `FAIL`; missing predictions return
`INCOMPLETE`.

## Scenario Suite integration

Driver:

`semantic.judgement_calibration`

Scenario:

`semantic-judgement-calibration-scoring`

The scenario proves:

- perfect predictions score with FN=0 and FP=0;
- a seeded false negative is exposed explicitly;
- a seeded false positive is exposed explicitly;
- incomplete prediction sets cannot pass;
- unknown case IDs are rejected.

This remains a deterministic scoring layer. A live model, human reviewer, or
external agent can produce the predictions through an external workflow without
changing Harness semantics.

## Boundary

This protocol measures agreement with the expert corpus. It does not establish
that the expert labels are universally correct, nor does it estimate production
error rates from six bootstrap cases.

The next calibration work is corpus growth:

1. near-miss pairs with small wording changes and opposite labels;
2. DDD / security / consistency / lifecycle-specific semantic cases;
3. independently reviewed labels;
4. evaluator runs recorded by model/version/configuration;
5. trend comparison across evaluator versions without weakening the Harness
   acceptance contract.
