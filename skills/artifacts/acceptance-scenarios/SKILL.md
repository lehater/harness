---
name: acceptance-scenarios
description: "Use for actionable CREATE work requiring concrete verification/acceptance scenarios from an accepted verification strategy and canonical design. Produce traceable expected evidence without inventing new product/domain/architecture semantics."
---

# Acceptance Scenarios

## Trigger

Use when actionable grouped work has `knowledge_kind: acceptance-scenarios` and
Verification Design must materialize concrete scenarios/evidence cases after a
verification strategy exists.

## Inputs

- actionable work and Verification Design Authority;
- accepted Verification Strategy;
- canonical Requirements/Domain/Architecture/Interface contracts being proved;
- Implementation Design when scenario boundaries depend on supported realization.

## Read boundary

Read only contracts needed to state:

- setup/preconditions;
- action/event;
- expected observable/domain outcome;
- evidence level (module/integration/API/E2E/etc.);
- traceability to accepted design.

## Procedure

1. Confirm Verification Strategy is accepted.
2. Enumerate material success, rejection, unresolved/unknown and failure paths
   required by accepted contracts.
3. Write scenarios with concrete preconditions/actions/expected outcomes.
4. Cover boundary and historical/provenance cases where canonical semantics make
   them material.
5. Map each scenario to the accepted source contract(s) it verifies.
6. Ensure scenarios prove behavior rather than current implementation quirks.
7. Route any missing expected semantic result upstream as a Question; tests do
   not create design truth.
8. Remove redundant scenarios that add no distinct correctness evidence.
9. Produce project-native scenario/test-intent artifact, accept/register and
   reevaluate.

## Stop conditions

Stop when:

- expected behavior is not decided by accepted upstream knowledge;
- a scenario would introduce a new requirement;
- only diagnostic/performance evidence exists for a correctness claim;
- the selected evidence level cannot observe the required outcome.

## Output contract

Prefer project-native scenario/test-intent format.

Each material scenario should identify:

- stable scenario id/name;
- setup/preconditions;
- action;
- expected result;
- canonical trace/evidence target.

## Acceptance checks

- every expected result traces to accepted design;
- important negative/unresolved paths are represented;
- implementation details are not mistaken for product truth;
- scenarios collectively satisfy the accepted Verification Strategy;
- diagnostic checks are not mislabeled as acceptance evidence.

## Registration

Register accepted scenario artifact(s) under Verification Design and provide the
grouped acceptance-scenario capabilities they genuinely satisfy.

## Human projection

Normally none beyond the project-native test-intent/scenario artifact.
