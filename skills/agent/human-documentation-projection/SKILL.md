---
name: human-documentation-projection
description: "Produce source-bounded human narrative projections from a compiled Harness projection manifest and presentation plan without creating or repairing engineering semantics."
---

# Human Documentation Projection

Status: canonical v1.

## Trigger

Use only after a deterministic Human Projection manifest and plan have been compiled for an explicit Consumer/capability scope.

## Inputs

- projection manifest;
- presentation plan;
- selected canonical source artifacts allowed for each section;
- target audience/purpose already declared by the presentation recipe;
- unresolved Questions and target-state gaps from the manifest.

## Read boundary

For each section, read only the canonical artifacts listed in that section's plan.

Do not read:
- generated human documentation being replaced or benchmarked during generation;
- downstream implementation/code as semantic authority;
- canonical artifacts outside the section scope;
- unrelated repository prose to make the section more complete.

A missing fact is omitted or reported as unresolved. It is never recovered from an out-of-scope source.

## Procedure

1. Read the section purpose and exact allowed source list.
2. Extract the smallest set of substantive statements needed for the human audience.
3. Preserve accepted distinctions, negative constraints, scope limits and failure semantics.
4. Prefer one claim per independently traceable assertion; combine claims only when the same source set supports them.
5. Attach every substantive claim to one or more allowed CanonicalArtifact IDs.
6. If sources disagree materially, create a conflict/incomplete note; do not select a winner.
7. If a Question/gap affects the section, state the gap explicitly and avoid completing the missing semantics.
8. Keep implementation detail out unless the section's allowed sources own it.
9. Produce projection IR first.
10. Validate the IR against the compiled plan.
11. Render Markdown from validated IR.

## Output contract

Output is generated harness-human-projection-ir, never a CanonicalArtifact.

Each planned section contains one or more claims with human-readable text and non-empty source CanonicalArtifact IDs.

Generated Markdown is derived from this IR.

## Acceptance checks

- every substantive claim has non-empty source refs;
- every referenced artifact is allowed for the section;
- no claim silently answers an unresolved Question;
- no claim strengthens a MUST/guarantee beyond its source;
- no project/domain/architecture decision is introduced by wording;
- important negative constraints are not dropped merely for readability;
- conflicting sources remain visible;
- generated files do not provide CapabilityIds;
- deletion of the generated package cannot change Harness target state.

## Quality guidance

Good projection prose:
- explains concepts in project/domain language;
- removes storage-format noise;
- groups related facts by reader task;
- preserves precise semantic distinctions;
- highlights coding/operational boundaries relevant to the selected audience;
- points the reader to canonical sources rather than reproducing entire source files.

Avoid:
- copying YAML mechanically;
- generic architecture boilerplate;
- replacing precise domain terms with vague synonyms;
- inventing causal explanations or rationale not present in sources;
- claiming completeness merely because the section rendered.

## Important limit

Structural traceability proves where prose came from; it does not prove paraphrase correctness.

Semantic review remains required before treating a generated narrative package as acceptable review/handoff material.
