# Live Calibration Validator v0

Status: active research; external execution RED proven, minimal execution GREEN implemented.

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


## Independence options

The validator distinguishes evaluator identity/configuration from evaluator
independence. The practical options have different assurance strength:

- **same model, same session/context** — useful only as a functional integration
  test; it is not independent semantic calibration;
- **same model, fresh session/context** — removes declared conversation context
  when an external orchestrator actually creates that fresh context, but Harness
  still reports independence as unverified without trusted execution evidence;
- **same model, different configuration/version** — a distinct reproducible
  evaluator binding suitable for regression comparison, not proof of an
  independent viewpoint;
- **different model or provider** — provides stronger evaluator diversity when
  the external driver really invokes the declared model, while provenance still
  depends on the control plane;
- **external evaluator service** — the natural automated trust boundary; it may
  additionally provide authenticated execution provenance;
- **HUMAN evaluator** — valid external judgement when reviewer identity and the
  blinded request are recorded; automation and repeatability are lower;
- **multiple evaluators** — represented as separate runs/evaluations. Harness
  compares their independent metrics and stability evidence but does not invent
  consensus semantics.

No descriptor field named "independent" is accepted as proof. Independence is a
property of execution/control, not of evaluator-authored metadata.

## Evidence persistence

A live calibration evaluation is a runtime record, not canonical engineering
knowledge. Scenario Suite already supports a JSON report output; CI/operator
execution can persist that report as the reproducible evidence record. The
record contains the run/request identities, corpus/protocol/evaluator
fingerprints, evaluator descriptor, validated per-case verdict evidence and the
existing scorer result.

## Closure result

The research question is answered positively with an explicit trust boundary.

Harness can reproducibly measure a concrete live evaluator when an
operator-controlled Scenario Suite driver performs the external call and returns
a run bound to the generated request. Harness itself remains deterministic and
does not become the semantic oracle.

The resulting model is:

- **Calibration Corpus** — canonical Harness expert oracle.
- **Evaluation Protocol** — canonical versioned, label-blind evaluator contract.
- **Evaluator Descriptor** — runtime provenance/configuration input whose full
  contents are fingerprinted.
- **Live Calibration Request** — generated evidence binding corpus, protocol,
  evaluator descriptor and run identity; contains only blinded cases.
- **Live Calibration Run** — runtime evidence produced by the external driver.
- **Calibration Evaluation** — generated deterministic evidence containing the
  unchanged existing scorer result.
- **Stability Evaluation** — optional generated evidence comparing repeated
  runs of the exact same binding.

No new Core concept was required.

### Guarantees established by Harness

1. Expert labels, mutation classes, expert rationale and label-bearing canonical
   case ids are withheld from evaluator input.
2. Corpus, protocol, evaluator descriptor/configuration, adapter version and run
   identity are cryptographically bound into the request.
3. Each returned verdict is bound to an opaque request-specific case identity.
4. Changed corpus/protocol/evaluator configuration or run identity invalidates
   old predictions.
5. Unknown, duplicate, malformed or missing verdict evidence cannot become a
   successful calibration.
6. Interrupted, failed or unavailable runs cannot become successful
   calibration.
7. Validated predictions are scored only by
   `semantic_judgement_calibration.py`; scorer semantics are not duplicated.
8. Separate evaluator/model/configuration runs retain separate FN, FP, recall,
   false-positive rate, accuracy, per-class performance and misses.
9. Repeated identical bindings can be checked for verdict instability without
   inventing consensus or a combined quality score.
10. Private chain-of-thought is neither requested nor required; short rationale
    and structured findings are optional auditable evidence.

### Guarantees outside Harness

Harness does not prove:

- that expert labels are universally correct;
- that the declared provider/model/version actually ran unless the external
  control plane supplies independently verifiable attestation;
- that two evaluator runs are organizationally, physically or statistically
  independent;
- that a fresh process implies a fresh model session or absence of hidden
  provider-side memory;
- production error rates from the bootstrap corpus.

Accordingly evaluator independence remains `UNVERIFIED` in ordinary run
evidence. This is intentional fail-closed behavior, not a missing semantic
validator.

### Execution boundary

A real evaluator call is made by an explicitly operator-loaded Scenario Suite
driver. The driver may target a separate model, fresh model configuration,
isolated agent/session, external evaluator service, HUMAN workflow, or multiple
independent evaluators. Harness supplies the blinded request and validates the
returned run.

A provider-specific driver is infrastructure/integration code and is not
required in Core. No concrete provider calibration result is recorded by this
research change because no independently controlled evaluator/provider
configuration is part of the repository fixture. Such a result must be added as
separate runtime evidence, not synthesized by the same agent that authored the
corpus/protocol.

## CI evidence

- RED: PR #94 commit
  `da4daeb202b5de459ca94a2c5cce1f5bfda54088` failed exactly because the
  required live-calibration driver was absent.
- GREEN + mutations: commit
  `f6db868b64ac1272afa24dd038a4b61fdb5f7f25` passed the complete
  `harness core` workflow.

The Scenario Suite is therefore the executable acceptance surface for the
validator; no parallel test runner was introduced.


## External execution RED — reopened closure

The previous closure statement was too strong: the repository proved validation
of externally supplied run evidence, but did not yet contain an executable
reference driver proving that Scenario Suite can actually launch a separate
evaluator runtime.

The closure is reopened for one narrow RED/GREEN slice. Acceptance requires an
operator-selected external driver that:

- is loaded through the existing Scenario Suite `--driver-module` mechanism;
- receives corpus/protocol/evaluator/run configuration from the scenario;
- sends only blinded request material to a separate process;
- converts process failure/timeout/malformed output into non-successful run
  evidence;
- returns the normal live calibration evaluation using the unchanged scorer.

The integration fixture intentionally uses an evaluator process that ACCEPTS
every case. The expected calibration outcome is FAIL with false negatives. This
proves execution plumbing, not semantic quality, and prevents the fixture from
becoming a new semantic oracle.


## External execution GREEN

The RED was observed in CI: all existing Scenario Suite coverage passed and the
new integration validator failed only because
`live_calibration_process_driver` did not exist.

The minimal GREEN adds that one driver. It deliberately supports a single
executable path rather than arbitrary shell commands:

- executable selection remains operator/CI configuration;
- scenario data cannot choose code to execute;
- no shell is used;
- executable bytes and timeout are incorporated into the effective evaluator
  descriptor and therefore into request identity;
- only blinded request material crosses the process boundary;
- process/output failures are converted to normal fail-closed live-run states;
- the resulting predictions still flow through
  `semantic_judgement_calibration.py`.

The fixture evaluator accepts every case and therefore scores FAIL with five
false negatives. This proves the execution path cannot manufacture semantic
success.
