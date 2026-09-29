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

## Interim result

The first scorable v3 execution resolved to the same model
(`gpt-6-luna`) that had rejected the ambiguous v1
`valid-subject-preservation` case. With the ambiguity removed, it scored all
14 v3 cases correctly.

This is direct evidence supporting the diagnosis that the original mismatch was
caused by the calibration task/oracle wording rather than by that mismatch alone
demonstrating inferior model quality.

One complete run is not stability evidence. A further independent live
execution is required before recording v3 repeat stability.
