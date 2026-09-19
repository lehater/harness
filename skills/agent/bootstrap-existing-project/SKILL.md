---
name: bootstrap-existing-project
description: "Use when introducing Harness into an existing repository that has project knowledge but no Harness Core graph. Build the smallest scope-driven graph and reuse existing canonical artifacts instead of copying the repository."
---

# Bootstrap Existing Project

## Trigger

Use when a selected task or Design Profile needs Harness navigation but the target repository has no usable Core model.

## Inputs

- selected task/scope;
- target repository instructions;
- Design Profile or the expectations currently being evaluated;
- existing accepted project documentation and explicit source-of-truth maps.

## Procedure

1. Read target-repository instructions before project artifacts.
2. Start from the selected expectations, not from a full repository inventory.
3. For each required capability, locate the smallest accepted source that actually owns that knowledge.
4. Reuse that artifact path as a Core `CanonicalArtifact`; do not copy its prose into `.harness/knowledge`.
5. Create only the Authorities needed by the selected artifacts and expectations.
6. Declare artifact dependencies only where one artifact semantically relies on another.
7. Treat draft plans, generated views, historical snapshots and implementation code as canonical only when the target repository explicitly assigns them that role.
8. Leave missing capabilities without providers so target-state evaluation returns `CREATE`.
9. If ownership or accepted truth is genuinely unresolved, represent the semantic gap as a Core `Question` rather than guessing.
10. Validate the smallest model and re-evaluate the selected Design Profile.

## Stop conditions

Do not continue by inference when:

- two accepted artifacts make conflicting claims;
- no Authority can be identified for a required decision;
- a candidate source is clearly draft/WIP while the expectation requires accepted knowledge;
- satisfying the expectation would require interpreting arbitrary implementation details as an undocumented product/domain decision.

## Output

A minimal Core model, normally `.harness/graph.yaml`, that references existing canonical project artifacts and leaves genuinely missing knowledge visible.

## Anti-goals

- no repository-wide prose mining;
- no migration of all documentation into Harness;
- no duplicate source of truth;
- no automatic claim that code is canonical design;
- no graph entries created merely for completeness.
