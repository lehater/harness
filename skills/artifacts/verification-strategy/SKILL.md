---
name: verification-strategy
description: "Use for an actionable CREATE expectation requiring verification/test strategy knowledge. Produce verification-plan/v1 from accepted requirements, domain/architecture constraints and real or explicitly required evidence."
---

# Verification Strategy Artifact

## Trigger

Use when target state exposes an actionable `CREATE` for verification strategy, test strategy or verification evidence planning and `verification-plan/v1` is an appropriate representation.

## Inputs

- the `CREATE` expectation;
- its Verification Authority;
- accepted Requirements, Domain and Architecture providers in prerequisite closure;
- existing tests, validators and CI commands relevant to the selected scope.

## Read boundary

Inspect:

- the canonical behavior/constraint owners that must be verified;
- existing automated tests that directly demonstrate those contracts;
- deterministic validators and CI checks;
- known exclusions that should not silently become acceptance gates.

Do not treat a performance benchmark, lint check or test count as useful evidence unless it verifies a stated objective.

## Procedure

1. Confirm the expectation is `CREATE`, not `WAIT` or `PENDING`.
2. Identify the accepted behaviors/invariants/boundaries whose regression would invalidate the selected scope.
3. Map each verification objective to concrete evidence:
   - an existing test/validator/command; or
   - an explicit evidence requirement that must be created before the stronger capability is claimed.
4. Remove redundant or diagnostic-only checks from the correctness gate.
5. Preserve important out-of-scope boundaries.
6. If verification requires semantics that are not decided upstream, create a Core `Question` for the owning Authority rather than specifying an arbitrary expected result.
7. Draft `verification-plan/v1`.
8. Run `workspace.py validate-artifact`.
9. Apply common semantic acceptance.
10. After acceptance, register, render and re-evaluate target state.

## Stop conditions

Stop and create or preserve a Core `Question` when:

- a verification objective depends on upstream behavior or semantics that are not accepted;
- available evidence cannot distinguish the required correctness claim from a diagnostic or incidental check;
- a proposed check would introduce a new product/domain requirement rather than verify an accepted one;
- the selected scope lacks an Authority-owned contract that defines what success means.

## Output schema

`verification-plan/v1`.

Required knowledge:

- purpose;
- selected scope;
- one or more named verification checks;
- concrete evidence for every check.

Optional `out_of_scope` makes non-gates explicit.

## Artifact-specific acceptance

- every check traces to accepted behavior or a structural constraint;
- every evidence item is specific enough for an agent to locate or create;
- diagnostic performance evidence is not mislabeled as correctness;
- the strategy does not introduce new product requirements;
- test implementation details do not become domain truth.

## Registration

Register the accepted managed artifact as a Core `CanonicalArtifact`.

Its dependencies should identify the accepted Requirements, Domain and Architecture providers whose behavior/constraints the strategy verifies. Its `provides` entry must be the verification capability from the actionable expectation.

## Human projection

A generated Verification Strategy Markdown document under the configured generated-docs directory.
