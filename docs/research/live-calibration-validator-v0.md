# Live Calibration Validator v0

Status: active research; RED proven, minimal GREEN implemented.

## Scope

Measure a concrete live semantic evaluator against the existing expert-labelled
semantic calibration corpus without turning Harness into a semantic oracle.

The completed Capability Derivation Testing result is an upstream dependency,
not part of this task.

## Existing mechanisms reused

- Scenario Suite is the orchestration surface.
- Operator-selected external driver modules are the extension point for live
  evaluator execution; scenario YAML never selects executable Python.
- `semantic_judgement_calibration.py` remains the only calibration scorer.
- Semantic derivation already demonstrates deterministic request binding.
- Decision Execution Assurance already establishes the trust rule that a
  workload cannot self-attest stronger isolation/provenance.

No Core extension is justified.

## Architectural boundary

```text
expert-labelled corpus
        |
        | Harness-only oracle data
        v
Live Calibration Validator
  - validate corpus/protocol/evaluator descriptor
  - build blinded request
  - bind corpus + protocol + evaluator config + run
        |
        | label-free semantic cases
        v
external evaluator driver
        |
        | request-bound verdicts
        v
Live Calibration Validator
  - validate response identity/completeness
  - map opaque case request ids back to corpus ids
        |
        v
semantic_judgement_calibration.py
        |
        v
FN / FP / recall / FPR / accuracy / per-class / misses
```

The validator is deterministic generated-evidence machinery above Core.
A concrete external driver is runtime integration, not canonical project truth.

## First RED

The current scorer accepts only `case id + verdict`. The same predictions can
therefore be scored without proving which evaluator/model/configuration/protocol
produced them.

A more fundamental live-execution defect is also present: the canonical corpus
is unsafe as direct evaluator input. Its `id`, `mutation_class`,
`expected_status` and expert `rationale` reveal calibration labels. Several
case ids are themselves label-bearing (for example `valid-paraphrase` and
`semantic-weakening`).

Therefore a live evaluator must never receive the canonical corpus verbatim.
Harness must derive a blinded request containing only the semantic material
needed for judgement plus opaque per-case request identities.

RED scenario:
`spec/scenario-suite/scenarios/live-semantic-evaluator-calibration.yaml`.

At this commit the required `semantic.live_calibration.validate` driver does
not exist, so the Scenario Suite cannot establish the required live-run binding.

## Minimal GREEN target

Add one deterministic validator that:

1. derives a blinded request from corpus + protocol + evaluator descriptor +
   caller-supplied run identity;
2. fingerprints every material binding input;
3. requires every returned verdict to bind to an opaque per-case request id;
4. rejects stale/wrong/malformed/duplicate responses and non-completed runs;
5. maps validated verdicts to the existing scorer without reimplementing score
   semantics;
6. emits evaluator/protocol/corpus/run provenance alongside the scorer result.

Actual model/service invocation stays in an explicitly loaded Scenario Suite
external driver. Without trusted external attestation Harness must report
evaluator independence as unverified; binding and label withholding are the
guarantees Harness itself can establish.

## RED evidence

PR #94 at commit `da4daeb202b5de459ca94a2c5cce1f5bfda54088`
failed the repository Scenario Suite exactly because
`semantic.live_calibration.validate` did not exist. Existing checks before the
Scenario Suite passed. This isolates the missing capability rather than a
pre-existing repository failure.

## Minimal GREEN

The first GREEN adds:

- canonical live evaluator protocol v1;
- label-blind request construction;
- corpus/protocol/evaluator/run fingerprints;
- opaque per-case request binding;
- deterministic live-run validation;
- unchanged delegation to `semantic_judgement_calibration.py`;
- Scenario Suite request/validator drivers.

The GREEN deliberately does not add provider SDKs or a new executor. A real
provider is integrated through the existing externally loaded Scenario Suite
driver module.

## Mutation result

The live layer now fails closed for:

- changed evaluator configuration;
- changed corpus;
- changed protocol;
- stale run identity/request;
- wrong case binding;
- missing prediction;
- duplicate prediction;
- malformed/missing verdict;
- interrupted run;
- unavailable evaluator/run.

A complete bound run is scored only by the existing
`semantic_judgement_calibration.py` scorer.

## Unstable evaluator decision

The explicit unstable-evaluator RED justifies one small additional check:
repeated whole-corpus runs for the same corpus/protocol/evaluator binding remain
independent runs, and their case verdicts may be compared for stability.

No consensus, majority vote or averaged quality score is introduced. If two
scorable runs disagree on any case, the stability result is `UNSTABLE` and
lists the affected canonical case ids. This is a separate quality dimension from
FN/FP/recall/FPR/accuracy.

## Evaluator comparison

Evaluator A vs B, or model/configuration version N vs N+1, is represented by
separate live evaluations. Each retains its own descriptor fingerprint and full
existing scorer result. Comparison is side-by-side over false negatives, false
positives, recall, false-positive rate, accuracy, per-class accuracy and misses;
Harness does not select a winner or collapse those dimensions.
