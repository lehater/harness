# Source boundary and statement enumeration completeness v0

Status: completed proof; raw-source omission is bounded by lossless source
coverage and local semantic enumeration without changing Harness Core.

## Question

The preceding semantic-surface work assumed that every independently meaningful
source statement had already entered the source ledger.

That leaves an outer failure mode:

```text
raw source contains material statement
        |
        X  never enumerated
        |
statement ledger
```

`source_coverage.py` cannot detect this because it correctly validates only
the statements present in its input ledger.

The question is therefore:

> Can Harness prove that no raw source text disappeared before statement-level
> semantic enumeration?

## Real-project RED

Pinned source:

`lehater/napms@c403ceed`

`docs/requirements/wave1-product-requirements.md`.

The experiment uses the real contiguous source excerpt containing:

- `REQ-W1-004`;
- `REQ-W1-005`;
- `REQ-W1-006`.

A source-coverage ledger deliberately enumerates only `REQ-W1-004` and
`REQ-W1-005`, with both statements ADMITTED.

Existing deterministic result:

```text
valid = true
coverage_status = COMPLETE
statement_count = 2
```

This is expected behavior. The ledger has no independent representation of the
raw source section that was omitted.

Therefore:

```text
SOURCE COVERAGE COMPLETE
    does not imply
RAW SOURCE ENUMERATION COMPLETE
```

## Minimal source-boundary mechanism

A small assurance-only validator was added:

`source_boundary.py`.

Scenario driver:

`source.boundary`.

The mechanism does not interpret source semantics. It accepts:

- the exact source text;
- an immutable SHA-256 fingerprint;
- a set of line-range segments.

It checks only:

1. the source fingerprint matches;
2. every segment range is valid;
3. every source line is covered;
4. no source line is covered by more than one segment.

The source may be partitioned however the producer finds useful. Semantic
quality is deliberately outside this validator.

### Real excerpt result

Scenario:

`spec/scenario-suite/scenarios/source-boundary-completeness.yaml`.

The pinned excerpt has 37 lines.

Incomplete boundary:

```text
REQ-W1-004 -> lines 1..14
REQ-W1-005 -> lines 15..29
REQ-W1-006 -> absent
```

Result:

```text
status = REJECTED
covered_line_count = 29
finding = UNCOVERED_SOURCE_LINES
uncovered = 30..37
```

Complete boundary:

```text
REQ-W1-004 -> lines 1..14
REQ-W1-005 -> lines 15..29
REQ-W1-006 -> lines 30..37
```

Result:

```text
status = ACCEPTED
covered_line_count = 37
segment_count = 3
```

This closes silent byte/text loss before semantic enumeration for the selected
immutable source.

It does not prove that one covered unit was decomposed into the correct number
of meaningful statements.

## Local statement-enumeration review

The remaining semantic task is now bounded:

```text
one losslessly covered source unit
        ->
candidate statement list
        ->
does the list contain every material source statement?
```

Corpus:

`spec/semantic-derivation/source-unit-statement-enumeration-calibration-v1.yaml`.

Deterministic calibration scenario:

`spec/scenario-suite/scenarios/source-unit-statement-enumeration-calibration.yaml`.

Four real NAPMS requirement units were used:

- `REQ-W1-004`;
- `REQ-W1-008`;
- `REQ-W1-010`;
- `REQ-W1-013`.

For each source unit:

- one complete expert enumeration is ACCEPTED;
- one enumeration with one material statement removed is REJECTED.

Total:

```text
8 cases
4 complete enumerations
4 omission enumerations
```

## Live evidence with generic semantic protocol

Repository policy prefers explicit GPT-6 Luna. The current GitHub Actions
identity cannot pin it, so `auto` was used only as the documented research
fallback with resolved-model provenance retained.

Workflow:

`36522236092`.

Corpus fingerprint:

`LCCORPUS-07a66a066af64ae0ff12832f95ab19fdfa30db35acbe021be807cd795581e2eb`.

Protocol:

`semantic-derivation-live-calibration-v2`.

Artifact:

- id `11013253362`;
- digest
  `sha256:e334d446c01ed2653dd4e3178fbbff876ca2fcfe65409e89b18022a312e476fb`.

### Run 1

Resolved model:

`mai-code-1.1-flash`.

Result:

```text
TP=4
TN=4
FN=0
FP=0
accuracy=1.0
detection_recall=1.0
false_positive_rate=0.0
```

All eight verdicts matched the expert oracle.

### Run 2

Resolved model:

`gpt-6-luna`.

Result:

```text
TP=4
TN=3
FN=0
FP=1
accuracy=0.875
detection_recall=1.0
false_positive_rate=0.25
```

All four real statement-enumeration omissions were detected.

The sole false positive was:

`w1-010-enumeration-complete`.

Stability across the two runs was:

```text
UNSTABLE
unstable_cases:
  - w1-010-enumeration-complete
```

## Disagreement analysis

The `w1-010-enumeration-complete` target explicitly contains:

> Rows retain source-fact provenance/effective validity sufficient to explain
> projection.

GPT-6 Luna rejected the case with the rationale that the target omitted
source-fact provenance and effective validity.

That required meaning is visibly present in the blinded target.

Therefore this disagreement is classified as evaluator semantic error rather
than oracle ambiguity or protocol underspecification.

It is useful evidence of the remaining evaluator boundary:

```text
source omission detection
    -> 4/4 in both scorable runs

acceptance of a complete enumeration
    -> can still produce a false rejection
```

The expert-reviewed corpus remains the oracle.

## Focused enumeration protocol experiment

A narrower temporary protocol,
`source-unit-statement-enumeration-v1`, was drafted to instruct the evaluator
to check source clauses explicitly for actor/subject, scope, time, cardinality,
negative constraints, provenance and boundary statements. It was not retained
as a repository protocol because no scorable execution was obtained.

Workflow:

`36522375985`.

Three execution attempts were made without changing the corpus or protocol.

All three failed before semantic scoring because the provider response omitted
or violated the required `version: 1` envelope.

Evidence artifacts:

- `11013293368`,
  `sha256:d3ad1b45ead9166e88b176d2b73730fbbac0a8a74e25af528fbce92c3d432c97`;
- `11013093905`,
  `sha256:0af210666271e3081841842c6ed2732213c790608fe8ba0173e91bf45cd12edc`;
- `11012999104`,
  `sha256:5412fc4fa7bca573ad074936ab329773dc61c22bff01ace4202d8fd276e8e46f`.

No claim about semantic quality of that focused protocol is made.

## Resulting assurance chain

The source-to-downstream path can now be decomposed as:

```text
selected immutable raw source
        |
        v
lossless source boundary                          deterministic
        |
        v
covered source unit -> meaningful statements     semantic review
        |
        v
statement disposition coverage                   deterministic
        |
        v
statement -> semantic atoms                      semantic review
        |
        v
accepted semantic surface
        |
        v
consumed-atom accounting                         deterministic
        |
        v
declared atom -> atom link truth                 narrow semantic review
        |
        v
downstream derivation coverage                   deterministic
```

The important property is that semantic review is local.

No evaluator is asked to discover arbitrary missing meaning across the entire
source and downstream artifact simultaneously.

## What this proves

For a selected immutable source artifact:

- raw text cannot silently disappear before review;
- source-unit omission is deterministic;
- statement enumeration can be reviewed one source unit at a time;
- current live evidence detected every tested enumeration omission;
- evaluator false positives remain possible and are measured rather than made
  authoritative.

## Remaining outer boundary

The mechanism assumes that the correct source artifacts were selected in the
first place.

It cannot detect:

```text
relevant source file / interview / external evidence
        |
        X  never enters selected source baseline
        |
lossless source-boundary validation
```

That next boundary was investigated in
`docs/research/source-set-evidence-boundary-v0.md`.

The follow-up establishes that open-world evidence completeness cannot be
proven generically. Harness can instead prove deterministic source-set closure
relative to an accepted acquisition contract over arbitrary project-owned
evidence channel ids. Missing, unresolved or undersatisfied required channels
fail closed before per-artifact source-boundary review.

This remains distinct from statement enumeration and downstream Capability
derivation.

## Architecture consequence

The new mechanism is assurance above Core.

No Authority, CanonicalArtifact, CapabilityId, Question, workflow state,
universal ontology or semantic DSL is added to Core.

The lossless boundary is intentionally syntactic; semantic meaning remains owned
by canonical project knowledge and expert-reviewed admission.
