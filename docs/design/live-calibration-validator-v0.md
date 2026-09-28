# Live Calibration Validator v0

Status: implemented experimental design; research closed in `docs/research/live-calibration-validator-v0.md`.

## Purpose

Measure a concrete semantic evaluator against the expert-labelled calibration
corpus while preserving three separate responsibilities:

- expert corpus supplies expected labels;
- external evaluator supplies only semantic predictions;
- Harness deterministically validates binding/completeness and delegates scoring
  to `semantic_judgement_calibration.py`.

The validator is generated evidence above Core. No Core entity is added.

## Runtime chain

```text
Calibration Corpus
        |
        v
build_live_calibration_request
        |
        | blinded cases + opaque case_request_id
        v
Scenario Suite external driver
        |
        | concrete evaluator/model/session/service
        v
Live Calibration Run
        |
        v
evaluate_live_calibration_run
        |
        v
semantic_judgement_calibration.py
```

Scenario Suite remains the orchestration surface. A concrete evaluator adapter
is loaded through the existing operator-controlled `--driver-module` extension.
Scenario YAML does not select executable modules or arbitrary commands.

## Artifact classification

- calibration corpus: canonical Harness test artifact;
- live evaluator protocol: canonical Harness test artifact;
- evaluator descriptor: runtime configuration/provenance input;
- live calibration request: generated runtime evidence;
- live calibration run: runtime evidence returned by an adapter;
- live calibration evaluation: generated evidence;
- scorer result: existing deterministic calibration evaluation nested unchanged
  inside the live evaluation.

None of these require a new Core concept.

## Evaluator descriptor

Minimum bound descriptor:

```yaml
version: 1
kind: harness-semantic-evaluator-descriptor
id: evaluator-a
provider: provider-name
model: model-name
model_version: immutable-or-provider-reported-version
configuration:
  temperature: 0
adapter:
  id: provider-adapter
  version: "1"
```

The complete descriptor is fingerprinted. Any configuration or adapter change
therefore changes the request binding.

## Blinding

The canonical corpus must never be sent directly to a live evaluator. Corpus
case ids and mutation classes are label-bearing, and expected_status/rationale
are explicit oracle data.

The request contains only:

- opaque `case_request_id`;
- source;
- target;
- relation.

The opaque id is derived from the bound run request and corpus position. Harness
keeps the mapping back to canonical case ids for scoring.

## Binding

The request identity binds:

- full corpus fingerprint;
- full protocol fingerprint;
- full evaluator descriptor fingerprint;
- explicit run identity.

Each `case_request_id` is derived from that request identity. A response from a
different corpus, protocol, evaluator configuration or run therefore cannot be
silently reused.

## Trust boundary

Harness guarantees only properties it can establish deterministically:

- the generated evaluator request withholds expert labels;
- the accepted response is bound to the generated request;
- duplicate/unknown/malformed predictions cannot score;
- incomplete or interrupted runs cannot become PASS;
- scoring semantics are exactly the existing scorer.

Harness reports evaluator independence as `UNVERIFIED`. A descriptor or
workload-authored claim does not prove that a model/session/service was actually
independent. Stronger independence requires the external driver/control plane to
establish and, if needed, attest it.

## External execution

A concrete live driver should:

1. receive corpus, protocol, evaluator descriptor and a fresh run id from
   operator/CI configuration;
2. call `build_live_calibration_request`;
3. send only the returned blinded semantic cases/protocol instruction to a fresh
   external evaluator context;
4. capture structured results;
5. form `harness-live-semantic-calibration-run`;
6. call `evaluate_live_calibration_run`;
7. return the evaluation as the Scenario Suite step observation.

This reuses the existing external-driver mechanism instead of creating a second
orchestration framework.

## Non-goals

- proving expert labels universally correct;
- extracting or storing private chain-of-thought;
- self-attested model/session independence;
- replacing the calibration scorer;
- aggregating evaluator quality into one score.

## Stability

A single live run measures agreement for that run only. When repeatability is a
requirement, run the same bound evaluator configuration more than once with
distinct run ids and pass the resulting evaluations to
`evaluate_live_calibration_stability`.

The stability evaluator requires identical corpus, protocol and evaluator
fingerprints. It reports `STABLE` or `UNSTABLE` and the disagreeing cases.
It deliberately does not perform consensus voting or alter scorer metrics.


## Reference external-process adapter

Harness includes an optional Scenario Suite external driver module
`live_calibration_process_driver`. It is not loaded by scenario YAML. The
operator/CI explicitly loads it and supplies the evaluator executable through
`HARNESS_LIVE_CALIBRATION_EXECUTABLE`.

The driver executes exactly one program without a shell and sends a JSON request
on stdin containing only:

- the versioned semantic judgement instruction;
- the declared evaluator descriptor/configuration;
- blinded cases with opaque `case_request_id`.

Expert labels and canonical case ids are not sent.

The driver fingerprints the executable bytes and effective timeout into the
evaluator adapter descriptor before request construction. Therefore changing the
executable or timeout changes evaluator binding and invalidates old run
evidence.

An external process boundary is execution evidence only. It does not upgrade
`independence.status`; a separate process does not prove a fresh model session,
different provider-side memory, or an independent viewpoint.
