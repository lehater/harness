---
name: product-requirements
description: "Use for actionable CREATE work requiring accepted product intent, observable behavior or acceptance semantics. Derive requirements from accepted problem evidence and explicit product decisions without inventing domain ownership or technical realization."
---

# Product Requirements

## Trigger

Use when actionable grouped artifact work has `knowledge_kind:
product-requirements`, including product-intent and acceptance capabilities that
may be materialized by one coherent requirements artifact.

## Inputs

- actionable grouped artifact work and Product Requirements Authority;
- accepted Problem Evidence when required by the production contract;
- explicit user/stakeholder product decisions;
- accepted scope constraints and existing product policy relevant to the selected
  target.

## Read boundary

Read the smallest canonical sources needed to establish:

- product goal/intent;
- externally observable behavior;
- product-level constraints and scope boundaries;
- acceptance expectations/examples;
- explicit non-goals.

Domain models, architecture, interfaces, persistence and implementation are read
only when checking for conflicts. They do not become evidence that a product
decision was accepted merely because current code behaves that way.

## Procedure

1. Confirm all grouped capabilities are actionable CREATE under one Product
   Requirements Authority and subject.
2. Trace each requirement to accepted problem evidence or an explicit
   user/stakeholder product decision.
3. Define required observable behavior and product-level constraints.
4. Define acceptance semantics/examples sufficient for downstream design to know
   what success means.
5. Preserve scope boundaries and non-goals.
6. Keep source/evidence semantics distinct from accepted product decisions.
7. Do not select Domain entities/aggregates, architecture, API shape, persistence,
   package layout or implementation strategy.
8. If a needed product choice is not determined by accepted input, create a Core
   Question to Product Requirements and stop the affected capability rather than
   inventing a convenient behavior.
9. Do not invent numeric quality targets. Record an explicit unknown or route a
   Question when downstream design requires one.
10. Produce one canonical managed `product-requirements/v1` artifact.
11. Give every atomic normative requirement a stable unique `REQ-*` identifier.
12. Record non-empty `source_refs` for every requirement; preserve rationale when it materially explains derivation or intent.
13. Mark only accepted current requirements as `ACCEPTED`; keep historical superseded requirements `RETIRED` rather than silently reusing their IDs for different meaning.
14. Run `workspace.py validate-artifact` on the candidate.
15. Apply common semantic acceptance, register all capabilities actually satisfied by the artifact, then re-evaluate the target Consumer.

## Stop conditions

Create or preserve a Product Requirements Question when:

- two accepted stakeholder/product sources conflict;
- an observable behavior choice materially changes product meaning and has not
  been decided;
- a numeric/quality constraint is required but unknown;
- acceptance cannot be stated without deciding an upstream product fact.

Route downstream instead of deciding here when the unresolved issue is semantic
domain ownership, architecture, interface representation, persistence or
implementation detail.

## Output schema

`product-requirements/v1`.

The canonical artifact contains:

- `purpose`;
- non-empty `requirements`;
- for each requirement:
  - stable unique `id` beginning with `REQ-`;
  - one atomic normative `statement`;
  - `status: ACCEPTED|RETIRED`;
  - non-empty `source_refs`;
  - optional `rationale`;
- optional `non_goals`.

Requirement IDs identify the accepted requirement, not its document position or technical implementation. Reasonable wording refinement does not require a new ID when the same normative requirement remains intact; materially different semantics must not silently reuse an old ID. Git history remains the revision mechanism.

## Acceptance checks

- every accepted requirement is supported by evidence or explicit product decision;
- every normative requirement is atomic enough to be reviewed and verified independently;
- every requirement has one stable unique `REQ-*` ID and non-empty source provenance;
- IDs are not reused for materially different requirement meaning;
- statements describe what the product must achieve, not how it is implemented;
- acceptance semantics are concrete enough for downstream design/verification;
- non-goals prevent accidental scope expansion;
- Domain/Architecture/Interface decisions remain downstream;
- unknown quality targets are not fabricated;
- the artifact genuinely provides every grouped CapabilityId being registered.

## Registration

Register the accepted project-native requirements artifact as one Core
`CanonicalArtifact` owned by Product Requirements.

Its `provides` may contain several capabilities from the grouped artifact work
when one accepted requirements artifact genuinely materializes them together.

Its dependencies identify the accepted Problem Evidence / product-policy
artifacts actually used.

## Human projection

Render the managed canonical artifact into a disposable human-readable Requirements document. The projection is for review; `.harness/knowledge/**` remains the source of truth.
