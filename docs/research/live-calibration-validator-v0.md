# Live Calibration Validator v0

Status: active research; first RED established.

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
