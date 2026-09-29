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

`spec/semantic-derivation/calibration-corpus-v3.yaml`

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
- valid aggregation — ACCEPTED;
- valid strengthening — ACCEPTED;
- semantic partial loss — REJECTED;
- valid subject preservation — ACCEPTED;
- semantic outcome substitution — REJECTED;\n- semantic enforcement gap — REJECTED.

The 10-case corpus is deliberately balanced between defect cases and valid
controls, including near-miss cases whose wording is related but whose semantic
verdict differs. It is a bootstrap calibration set, not a claim of statistical
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
error rates from the 10 bootstrap cases.

A live disagreement on v1 exposed an ambiguity in `valid-subject-preservation`:\nthe target restricted a UI action but did not explicitly state edit-execution\nenforcement. Corpus/protocol v2 remove that ambiguity and preserve the original\nwording as the negative `semantic-enforcement-gap` control. See\n`docs/research/semantic-disagreement-analysis-v0.md`.\n\nThe next calibration work is:

1. DDD / security / consistency / lifecycle-specific semantic cases;
2. independently reviewed labels;
3. evaluator runs recorded by model/version/configuration;
4. trend comparison across evaluator versions without weakening the Harness
   acceptance contract.

The separate Live Calibration Validator research is now implemented in
`docs/design/live-calibration-validator-v0.md`. It adds blinded request
construction and reproducible corpus/protocol/evaluator/run binding while
retaining this scorer unchanged. Concrete provider results remain runtime
evidence and require an independently controlled external evaluator driver.
