---
name: bootstrap-existing-project
description: "Use when introducing Harness into an existing repository that lacks a directly usable Core model. Reuse an existing canonical graph/projection when available; otherwise build the smallest scope-driven graph without copying project truth."
---

# Bootstrap Existing Project

## Trigger

Use when a selected task or Design Profile needs Harness navigation and the target repository does not already expose a directly usable Harness Core model. An existing canonical graph plus a compatible Harness projection counts as usable and should be adapted rather than replaced.

## Inputs

- selected task/scope;
- target repository instructions;
- Design Profile or the expectations currently being evaluated;
- existing accepted project documentation and explicit source-of-truth maps.

## Procedure

1. Read target-repository instructions before project artifacts.
2. Check for an explicit project-owned canonical graph, source-of-truth map or existing Harness projection before creating any new Harness graph.
3. If the repository already has a compatible canonical graph + `harness-canonical-graph-projection`, use the canonical-graph adapter in memory and preserve project-native contracts/metadata that are richer than Core. Do not create a second persistent `.harness/graph.yaml`.
4. Otherwise start from the selected expectations, not from a full repository inventory.
5. For each required capability, locate the smallest accepted source that actually owns that knowledge.
6. Reuse that artifact path as a Core `CanonicalArtifact`; do not copy its prose into `.harness/knowledge`.
7. Create only the Authorities needed by the selected artifacts and expectations.
8. Declare artifact dependencies only where one artifact semantically relies on another.
9. Treat draft plans, generated views, historical snapshots and implementation code as canonical only when the target repository explicitly assigns them that role.
10. Leave missing capabilities without providers so target-state evaluation returns `CREATE`.
11. If ownership or accepted truth is genuinely unresolved, represent the semantic gap as a Core `Question` rather than guessing.
12. Validate the smallest model and re-evaluate the selected Design Profile.

## Stop conditions

Do not continue by inference when:

- two accepted artifacts make conflicting claims;
- no Authority can be identified for a required decision;
- a candidate source is clearly draft/WIP while the expectation requires accepted knowledge;
- satisfying the expectation would require interpreting arbitrary implementation details as an undocumented product/domain decision.

## Output

Either:

- a transient Core projection derived from an existing project-owned canonical graph/projection; or
- when no compatible projection exists, a minimal Core model (normally `.harness/graph.yaml`) that references existing canonical project artifacts and leaves genuinely missing knowledge visible.

Never persist a second graph merely because Harness has a preferred workspace layout.

## Anti-goals

- no repository-wide prose mining;
- no migration of all documentation into Harness;
- no duplicate source of truth;
- no duplicate persistent graph when an existing project-owned graph/projection is already compatible;
- no automatic claim that code is canonical design;
- no graph entries created merely for completeness.
