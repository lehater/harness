# Semantic surface extraction admission v0

Status: completed proof; semantic-surface completeness boundary isolated without a new Core model.

## Question

After downstream derivation was reduced to explicit semantic atoms, one trust
boundary remained:

```text
canonical natural-language knowledge
        ->
accepted semantic atoms
```

If a material source meaning never becomes an accepted atom, deterministic
downstream derivation coverage cannot detect its later absence.

This experiment asks whether Harness can detect loss at that extraction/admission
boundary and how much of the check can remain deterministic.

## Existing mechanisms

Two existing mechanisms already cover different parts of the problem.

### Statement-level source coverage

`harness.evidence.source_coverage` proves that every enumerated source statement has exactly
one disposition:

- ADMITTED;
- explicit exclusion;
- duplicate;
- QUESTION.

This prevents silent disappearance of an entire enumerated statement.

It does **not** prove semantic equivalence between the original statement and an
ADMITTED `sanitized_statement`.

### Semantic acceptance

`harness.assurance.semantic_acceptance` can deterministically enforce a machine-addressable
semantic surface once the required source atoms are already known.

Relevant existing findings include:

- `MISSING_SUBJECTS`;
- `SOURCE_FIDELITY_VIOLATION`.

Therefore the missing mechanism was not another downstream derivation engine.
The unresolved question was the semantic review that establishes the source atom
baseline itself.

## Deterministic RED

Scenario:

`spec/scenario-suite/scenarios/semantic-surface-extraction-admission.yaml`.

The scenario uses canonical NAPMS requirement `REQ-RULE-004`:

> Allowed access may carry supported declarative effective conditions that
> determine contribution at evaluation time without redefining access identity
> or periodically rewriting stored Active/Inactive state.

A source-coverage ledger admits the weakened sanitized form:

> Supported declarative effective conditions determine policy contribution at
> evaluation time.

The ledger is still deterministically:

```text
valid = true
coverage_status = COMPLETE
statement_count = 1
```

This is correct behavior for `harness.evidence.source_coverage`: it proves disposition
coverage, not natural-language semantic fidelity.

The same scenario then starts from an expert-reviewed source atom baseline:

```text
REQ-RULE-004.effective-window
=
evaluation-time-effectiveness-without-periodic-state-rewrite
```

Using existing `semantic.acceptance`:

- no extracted atom -> `MISSING_SUBJECTS`;
- weakened extracted atom -> `SOURCE_FIDELITY_VIOLATION`;
- faithful extracted atom -> ACCEPTED.

So once the authoritative source atom is admitted, extraction/output fidelity is
deterministic.

## Remaining irreducible review

The irreducible step is narrower than the original problem:

```text
one canonical source statement
        ->
candidate list of semantic atoms
        ->
does the list preserve every material source clause?
```

This is not the same task as asking an evaluator to discover missing semantics
across two large engineering artifacts.

## Extraction calibration corpus

Corpus:

`spec/semantic-derivation/semantic-surface-extraction-calibration-v1.yaml`.

Scenario:

`spec/scenario-suite/scenarios/semantic-surface-extraction-calibration.yaml`.

Pinned project source:

`lehater/napms@42481577fab7f795cf3a2118b7b6f1c3c075d066`.

Four accepted NAPMS requirements were selected:

- `REQ-RULE-004`;
- `REQ-AUTH-001`;
- `REQ-RES-003`;
- `REQ-BUS-008`.

For each statement the corpus contains:

- one complete expert atomization -> ACCEPTED;
- one candidate atomization with one material clause omitted -> REJECTED.

Total:

```text
8 cases
4 complete atomizations
4 omission atomizations
```

The negative cases are extraction mutations at the boundary under test. They do
not modify downstream project design.

## Live evaluator evidence

Repository policy prefers explicit GPT-6 Luna, but the current GitHub Actions
identity cannot pin it directly. For this research-only measurement,
`model:auto` was used as the explicitly documented fallback. Runtime model
identity was retained in provenance.

Workflow run:

`36520914564`.

Corpus fingerprint:

`LCCORPUS-9c93b8402a2221c46b91fe4743060a9616fc99bb12ee2d00fc23758a6eb2ab2d`.

Protocol:

`semantic-derivation-live-calibration-v2`.

### Attempt 1

Run 1:

- resolved model: `gpt-6-luna`;
- TP=4, TN=4, FN=0, FP=0;
- accuracy=`1.0`;
- detection recall=`1.0`;
- false-positive rate=`0.0`;
- all complete atomizations accepted;
- all omission atomizations rejected.

Run 2 failed before semantic scoring because the provider returned non-strict
JSON.

Artifact:

- id `11013076388`;
- digest
  `sha256:39606b4e0065bebadc9cc8fb43cb034e0497c844c20eb3211ef4ecbf4e25851c`.

### Attempt 2

The first provider invocation failed before semantic scoring because the
response did not contain the required `version: 1` envelope.

Artifact:

- id `11013500226`;
- digest
  `sha256:74500909df148562e3074bed058ba0bb9b3e1785589f912b770c1e228ec8f6eb`.

### Attempt 3

Run 1:

- resolved model: `gpt-6-luna`;
- TP=4, TN=4, FN=0, FP=0;
- accuracy=`1.0`;
- detection recall=`1.0`;
- false-positive rate=`0.0`;
- all eight verdicts matched the expert oracle again.

Run 2 failed before scoring because the provider omitted/violated the required
versioned envelope.

Artifact:

- id `11013335989`;
- digest
  `sha256:6bc19634e47b3047551b5c4be4599997791fe4834c14ca3063e735438dbb85ed`.

There is no formal within-attempt `STABLE` result because no attempt produced
two scorable runs. The evidence nevertheless contains two independent scorable
GPT-6 Luna sessions against the same corpus/protocol/evaluator policy, both
8/8. This is repeat evidence, not a formal stability claim.

## Interpretation

The trust boundary can be decomposed more sharply.

### Layer 1 — source statement enumeration

```text
original source baseline
        ->
statement ledger
        ->
exact-one disposition
```

Oracle: deterministic `harness.evidence.source_coverage`.

Guarantee: no enumerated source statement disappears silently.

Non-guarantee: an ADMITTED rewritten statement may still weaken meaning.

### Layer 2 — source semantic-surface admission

```text
one admitted canonical statement
        ->
candidate semantic atoms
        ->
completeness/fidelity review
        ->
accepted source atom baseline
```

Oracle: expert review, optionally assisted by a calibrated semantic evaluator.

The live experiment shows that this narrow statement-to-atoms review was
handled correctly in both scorable GPT-6 Luna sessions on the current corpus.

This does not make the model the authority. Expert-reviewed canonical semantics
remain the oracle.

### Layer 3 — downstream derivation

```text
accepted source atoms
        ->
consumed atom accounting
        ->
source-atom -> target-atom links
```

Oracles:

- missing link/disposition -> deterministic;
- truth of a declared semantic link -> narrow request-bound semantic judgement.

## Resulting assurance chain

```text
canonical source
   |
   v
statement-level source coverage                 deterministic
   |
   v
statement -> semantic atoms admission           semantic review
   |
   v
accepted semantic surface
   |
   v
consumed-atom accounting                        deterministic
   |
   v
declared atom -> atom link truth                narrow semantic review
   |
   v
downstream semantic derivation coverage         deterministic
```

This localizes semantic judgement to two small boundaries instead of asking one
LLM to compare large artifacts and infer all missing meaning.

## What remains unsolved

The experiment does not automatically enumerate independently meaningful source
statements from arbitrary raw documents.

For source-loss-sensitive work, the existing Source Coverage Audit skill already
requires statement-level semantic granularity, splitting mixed sentences and an
independent reverse audit. That judgement remains the outermost source-boundary
assurance.

Therefore there are now two distinct extraction questions:

1. **statement enumeration completeness** — did the source ledger enumerate all
   independently meaningful source statements?
2. **atomization completeness** — did the admitted semantic surface preserve all
   material clauses of each admitted statement?

Neither should be collapsed into downstream Capability derivation testing.

## Architecture consequence

No new Core entity, universal ontology, semantic DSL, scorer, provider registry
or orchestration framework is justified.

The existing pieces compose sufficiently:

- Source Coverage Audit;
- semantic acceptance;
- semantic derivation;
- request-bound semantic judgement;
- calibration corpus/evidence.

The operational improvement is procedural: treat semantic-surface admission as
an explicit assurance boundary before using atoms as the authoritative
downstream derivation surface.
