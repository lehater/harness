# Semantic disagreement analysis v0

Status: completed; corpus/protocol ambiguity isolated and corrected in v2.

## Question

When live evaluators disagree with an expert label, determine whether the cause is
primarily evaluator quality or an under-specified semantic judgement task.

The first observed disagreement was the v1 case
`valid-subject-preservation`.

## Evidence

Historical corpus v1:

- source: `Only the owner of the current resource may edit that resource.`
- target: `Enable the current resource edit action only for its owner.`
- relation: `REALIZES`
- expert label: `ACCEPTED`

GitHub Actions run `36504064197`, attempt 1, run 1 resolved to
`gpt-6-luna` and returned `REJECTED`. Its brief rationale identified the
missing guarantee: restricting the edit action does not prohibit edits through
other execution paths.

Earlier runs resolved to `mai-code-1.1-flash` and returned `ACCEPTED`,
treating the owner-only edit action as a sufficient realization of the
owner-only edit rule.

The disagreement is therefore semantically explainable from the task text; it
is not evidence by itself that either model is generally better.

## Diagnosis

The source is an authorization invariant over edit execution. The target only
states a UI/action-availability constraint. Unless the target also states that
this action is the exclusive edit path, or that non-owner edit execution is
rejected, the target does not entail the source invariant.

Corpus v1 nevertheless labelled that target `ACCEPTED`.

Protocol v1 also said only that required meaning must be preserved without
material loss. It did not state whether an evaluator may assume unstated
mechanisms, exclusivity, enforcement paths, or surrounding context needed to
make the target sufficient.

The two live evaluators therefore applied different but defensible completion
assumptions:

- closed-world reading: judge only what is explicitly stated -> `REJECTED`;
- charitable completion: treat the edit action as the effective edit path ->
  `ACCEPTED`.

This is an oracle/task-specification defect before it is a model-quality defect.

## RED

A calibration case is not a valid discriminator when two reasonable readings of
the supplied source/target/protocol lead to opposite verdicts.

The v1 `valid-subject-preservation` case therefore cannot support a claim that
one evaluator is semantically better than another.

## Resolution

Historical v1 artifacts remain unchanged so recorded evidence keeps its original
fingerprints.

Current calibration moves to:

- `spec/semantic-derivation/calibration-corpus-v2.yaml`;
- `spec/semantic-derivation/live-calibration-protocol-v2.yaml`.

Protocol v2 requires evaluators to judge only explicitly stated semantics and
not invent unstated mechanisms, exclusivity, enforcement paths, side effects or
context. It also makes `REALIZES` sufficiency explicit: a merely contributory
mechanism is not enough.

Corpus v2 split the ambiguous v1 example into two discriminating controls:

1. `valid-subject-preservation` is now explicitly sufficient:
   owner/resource identity is preserved and non-owner edit execution is
   rejected.
2. `semantic-enforcement-gap` preserves the original UI-only target and is
   labelled `REJECTED`.

This preserves the semantic lesson discovered by the disagreement instead of
merely rewriting the case until models agree. A subsequent full audit found
additional wording/coverage weaknesses and promoted the current corpus to v3;
see `semantic-calibration-corpus-audit-v0.md`. Protocol v2 remains current.

## Consequence

For semantic calibration, the investigation order is:

1. inspect disagreement rationale;
2. test whether the current protocol uniquely determines the expert verdict;
3. repair corpus/protocol ambiguity when it does not;
4. only then treat remaining disagreement as evaluator behavior;
5. use fixed evaluator identity/repetition when measuring regression stability.

Evaluator reproducibility remains useful for regression measurement, but it is
not the primary explanation for this first semantic disagreement.

No Core, scorer, orchestration or provider abstraction change is required.
