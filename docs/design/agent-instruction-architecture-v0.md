# Agent Instruction Architecture v0

Status: canonical.

## Purpose

Define how an agent discovers and applies repository instructions without turning
bootstrap files into duplicate procedure or architecture owners.

The instruction system uses progressive disclosure: load only the instructions
needed for the current repository scope and semantic responsibility.

## Ownership layers

### AGENTS.md

An `AGENTS.md` file is a scoped bootstrap/index for its directory subtree.

The root file contains only repository-wide information needed before task
classification: global safety/workflow invariants, instruction entrypoints and
navigation to canonical owners.

A nested `AGENTS.md` is justified only when a subtree has durable local
instructions that should apply automatically whenever work occurs there. It
narrows or supplements the parent scope; it must not copy a canonical contract
or task procedure merely to make it visible.

When several `AGENTS.md` files apply, read them from repository root toward the
working path and treat the nearest applicable file as the most specific local
instruction source.

### Registries and router

Machine-readable registries own active skill identity, surface, route class and
exposure. `skill_router.py` is the typed discovery entrypoint.

An agent does not scan the skill tree or infer a physical `SKILL.md` path from
a task name when a registered route exists.

### SKILL.md

A skill owns the executable procedure for one routed operation, method or
artifact-production responsibility.

A skill may point to canonical design/specification documents that constrain its
work. It does not restate those contracts as an independent source of truth.

### Canonical design/specification

`docs/design/**` and `spec/**` own durable normative system contracts.
Repository instructions and skills reference these owners instead of copying
their semantics.

## Agent bootstrap algorithm

1. Read the applicable `AGENTS.md` chain for the working scope.
2. Identify the current semantic responsibility and skill surface.
3. Resolve the corresponding route through `skill_router.py`.
4. Read the selected `SKILL.md`.
5. Load only the canonical contracts explicitly required by that procedure or by
   the affected system boundary.
6. Execute the operation.
7. When responsibility changes, return to route discovery as defined by
   `docs/design/operation-orchestration-v0.md`.

Do not preload all of `docs/design/**`, all skills or all repository guidance
"for context".

## Authoring rules

- Put repository-wide bootstrap/navigation in the root `AGENTS.md`.
- Add nested `AGENTS.md` only for a real subtree-specific instruction scope.
- Put task procedures in routed `SKILL.md` files.
- Put durable architecture/policy semantics in their canonical design/spec owner.
- Prefer links/references over copied rules.
- If a rule already has a canonical owner, an `AGENTS.md` or skill may summarize
  why it matters but must not become a second independently maintained contract.
- Remove obsolete executable instruction surfaces rather than leaving ambiguous
  historical procedures discoverable.

## Validation expectations

Instruction validation should be structural and incremental:

- active skill identities and paths are unique and registered;
- archived procedures are not exposed as active `SKILL.md` discovery surfaces;
- public/internal operation exposure is machine-readable;
- behavioral compliance is evaluated separately where deterministic validation
  cannot prove that an agent followed the procedure.

This document defines instruction ownership and discovery. It does not define
the semantics of any particular engineering operation.
