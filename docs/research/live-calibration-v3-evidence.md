# Live calibration v3 evidence

Status: in progress; first real v3 execution recorded.

## Purpose

Run the ambiguity-hardened semantic calibration corpus v3 through the existing
real GitHub Copilot evaluator path and determine whether the semantic
disagreement observed on corpus v1 remains after the oracle/task specification
was tightened.

This is runtime calibration evidence, not a deterministic PR gate.

## Binding

Execution branch: `experiment/live-calibration-v3-evidence`.

The workflow trigger is temporarily extended to pushes on this disposable
evidence branch because the connected GitHub control surface does not expose a
workflow-dispatch write action. The trigger change must be removed before any
integration PR.

Current calibration inputs:

- corpus: `semantic-derivation-calibration-v3`;
- corpus fingerprint:
  `LCCORPUS-f2fa93992fc0bacbc1a3c54eb7b2bf60fab7f4e8764b3d5abc3b8ffc779ce342`;
- protocol: `semantic-derivation-live-calibration-v2`;
- protocol fingerprint:
  `LCPROTO-8d603fe525420519d8a51c6554aa889f5a84f645b9226c845c22c593280065af`;
- evaluator fingerprint:
  `LCEVAL-0a670c5231ac40358125de00bfab1939a1a3026b66c14cbfb203785be9cc3b09`;
- requested model policy: `auto`;
- Copilot CLI: `1.0.86`.

## Execution 1

GitHub Actions run: `36511694311`, attempt 1.

### Run 1

- run id: `GH-36511694311-1-1`;
- resolved model: `gpt-6-luna`;
- provider response: valid structured envelope;
- scored cases: 14 / 14;
- TP=7, TN=7, FN=0, FP=0;
- detection recall: `1.0`;
- false-positive rate: `0.0`;
- accuracy: `1.0`;
- misses: none.

Every v3 case matched its expert label. In particular, the model distinguished
the pair introduced from the original v1 disagreement:

- `valid-subject-preservation` -> ACCEPTED;
- `semantic-enforcement-gap` -> REJECTED.

The brief rationales explicitly used the intended v2 distinction: the positive
case states non-owner rejection, while UI action availability alone does not
establish edit-execution prevention.

### Run 2

- run id: `GH-36511694311-1-2`;
- process state: `FAILED`;
- evaluation status: `INCOMPLETE`;
- error: provider response omitted/violated the required `version: 1` envelope;
- no partial semantic score accepted.

This is an operational/protocol-output failure, not a semantic disagreement.
Harness failed closed as designed.

## Execution 2

GitHub Actions run: `36511822435`, attempt 1.

Artifact: `live-calibration-evidence`, id `11009515395`, digest
`sha256:d46e2fb3e6883a0ff7a3cf6f18ad9e336da82e276d954ba0688226e87d43b3eb`.

Run 1:

- run id: `GH-36511822435-1-1`;
- resolved model: `gpt-6-luna`;
- TP=7, TN=7, FN=0, FP=0;
- detection recall: `1.0`;
- false-positive rate: `0.0`;
- accuracy: `1.0`;
- misses: none.

Run 2:

- run id: `GH-36511822435-1-2`;
- resolved model: `gpt-6-luna`;
- TP=7, TN=7, FN=0, FP=0;
- detection recall: `1.0`;
- false-positive rate: `0.0`;
- accuracy: `1.0`;
- misses: none.

The two complete request-bound runs produced the same 14 verdicts. Existing
stability evaluation returned:

```yaml
status: STABLE
unstable_cases: []
```

Across both executions there are therefore three scorable gpt-6-luna v3 runs,
all with the same 14/14 verdict vector. The remaining failed invocation from
Execution 1 was an output-envelope failure and was not scored.

## Result

The first scorable v3 execution and both repeated runs resolved to the same
model (`gpt-6-luna`) that had rejected the ambiguous v1
`valid-subject-preservation` case.

After the oracle/task wording was made explicit, gpt-6-luna:

- ACCEPTED the explicit owner-only execution enforcement case;
- REJECTED the UI-only enforcement-gap case;
- matched all other v3 expert labels;
- repeated the complete verdict vector without semantic instability.

This is direct evidence that the original v1 mismatch was caused by an
under-specified calibration case/protocol boundary, not evidence by itself that
gpt-6-luna was a worse semantic evaluator.

It does not prove universal evaluator correctness. Corpus v3 is still a small
bootstrap corpus, and provider `model: auto` remains operationally
non-reproducible at model identity. The provider also still occasionally emits
malformed structured output.

The durable conclusion is narrower: semantic disagreement should first be
treated as a possible specification/oracle defect. Only disagreement that
survives an ambiguity audit is meaningful evidence about evaluator behavior.

The temporary branch-only push trigger used to obtain this evidence was removed
before integration; the live provider workflow remains operator-triggered.
