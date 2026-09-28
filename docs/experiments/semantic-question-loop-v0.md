# Semantic Question Loop experiment v0

## Hypothesis

A capability is not semantically complete merely because a canonical artifact
provides it. Machine-addressable obligations define the minimum accepted
semantic surface of selected knowledge kinds. Open obligations become Core
Questions rather than downstream assumptions.

## Contract

```text
knowledge-kind contract
  -> semantic assertions
  -> per-obligation disposition when needed
  -> semantic admission
  -> semantic gap
  -> deterministic Question proposal
  -> owning Authority
  -> capability block
  -> canonical revision
  -> new acceptance identity
  -> downstream lifecycle revalidation
```

The mechanism stays above Core. Core still owns only Authority,
CanonicalArtifact, CapabilityId, Question and dependencies.

## Obligation semantics

Reusable knowledge-kind contracts may define:

- `kind` and `min_count`;
- static `subjects`;
- `subjects_from_kind`, which requires coverage for every assertion identity
  of another kind;
- `required_values`.

A candidate may explicitly disposition an obligation or one subject as:

- `NOT_APPLICABLE` — closes it with rationale;
- `DEFERRED` — remains open and creates a Question;
- `QUESTION` — remains open and creates a Question.

Silence is not `NOT_APPLICABLE`.

## Project overlay

Project-specific completeness is expressed by
`harness-knowledge-kind-semantic-overlay`. It extends the reusable contract
without moving target-project truth into Harness.

## Failure classification

Only semantic absence/unresolved knowledge generates Questions. Missing review
checks, invalid provenance, wrong Authority, contradictions and other producer
validation defects stay ordinary admission failures.

## Acceptance proof

`validators/validate_semantic_question_loop.py` verifies:

1. subject-scoped missing Task Model semantics are detected;
2. the gap becomes a deterministic Question for the owning Authority;
3. the Question blocks an already-present capability;
4. `NOT_APPLICABLE` closes a justified obligation;
5. `DEFERRED` remains blocking;
6. process errors do not become Questions;
7. a project overlay adds target-specific completeness requirements;
8. semantic closure cannot report COMPLETE while generated Questions exist;
9. resolving the upstream gap with a new acceptance identity makes downstream
   knowledge STALE until revalidated.
