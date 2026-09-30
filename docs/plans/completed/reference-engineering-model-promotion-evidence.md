# Reference Engineering Model promotion evidence

Status: completed

Closure: R1/R2/R3 completed. Canonical promotion is deferred; see `docs/research/reference-engineering-model-promotion-decision-v0.md`.

## Goal

Collect the minimum independent evidence needed to decide whether Reference Engineering Model v0 should remain an optional research mechanism or become a candidate for canonical Harness status.

The current default is **non-canonical**. Promotion is an outcome to be earned by evidence, not the objective of the research.

## Accepted baseline

PR #114 established:

- a frozen Reference Engineering Model v0;
- deterministic materialization into the existing `harness-engineering-graph`;
- 39 Reference Capability Templates;
- 46 normalized Project Predicates;
- routing of all 118 current canonical semantic proof claims;
- fail-closed structural and materialization mutations;
- PREP/NAPMS compatibility regressions;
- known `REFERENCE_MODEL_GAP` results for safety-critical and AI/agentic specializations.

Harness Core remains unchanged.

## R1 — independent external hold-outs

### Question

Does the frozen v0 model survive projects and system shapes that did not participate in its construction?

### Responsibility

Test transferability without changing the model to fit the test set.

### Input

- immutable Reference Engineering Model v0;
- a new frozen external hold-out batch;
- accepted project-truth snapshots for those hold-outs.

### Output

For every hold-out:

- `STABLE`, `BLOCKED`, `UNRESOLVED`, `REFERENCE_MODEL_GAP`, or conflict;
- required/forbidden template evidence;
- any falsification of current reference assumptions.

### Gate

Do not modify v0 while evaluating the batch. Any required model change is recorded as a falsification result and belongs to a later version.

## R2 — version evolution and migration

Start only after R1 has produced evidence worth preserving.

Research at minimum:

- template rename;
- template split;
- template merge;
- predicate evolution;
- obsolete generated capability detection;
- reproducibility of historical materializations;
- migration of existing project graphs between reference-model versions.

Output: an explicit versioning/migration contract or evidence that canonical promotion is premature.

## R3 — safety and AI specialization semantics

Keep current fail-closed `REFERENCE_MODEL_GAP` behavior until semantics are justified.

Research whether safety-critical and AI/agentic concerns produce independently consumed engineering knowledge contracts with stable:

- Authority ownership;
- semantic claim surfaces;
- applicability evidence;
- verification/proof expectations.

Do not introduce new Capability Types merely to remove the gap.

## Promotion decision

A later promotion decision requires all of:

1. independent hold-out evidence;
2. defined evolution/migration behavior;
3. explicit handling of known specialization gaps;
4. deterministic materialization;
5. fail-closed invalid/conflicting evidence handling;
6. unchanged Harness Core boundary unless separately justified;
7. preservation of project-owned truth;
8. successful validation of every generated Engineering Graph.

Until then, Reference Engineering Model remains an optional research layer.
