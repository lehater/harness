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
2. Enumerate the relevant source/evidence statements before drafting requirements.
3. Classify each statement as requirement-bearing, rationale/context, example, prior derived design, duplicate, out-of-scope or unresolved. Classify by semantic ownership, not by who most recently said or confirmed the statement: stakeholder confirmation of a Domain/Architecture/Interface decision does not make it a Product Requirement.
4. For requirement-bearing statements:
   - preserve all observable constraints, including scope, time, cardinality, negative conditions and NOT_REQUIRED decisions;
   - split compound statements into independently verifiable atomic requirements;
   - merge only true semantic duplicates;
   - do not discard an observable constraint merely because the same sentence also contains design vocabulary.
5. Reconcile conflicts. If two accepted sources imply incompatible product behavior, create a Product Requirements Question and stop the affected capability.
6. Normalize the accepted result into product-level observable requirements without importing Domain/Architecture/API/Data choices. When a mixed statement contains both observable intent and a downstream realization choice, preserve the observable constraint and route the realization choice to its owning downstream Authority. If nothing observable remains after removing the realization choice, do not manufacture a Product Requirement from it.
7. Define acceptance semantics/examples sufficient for downstream design to know what success means.
8. Preserve scope boundaries and non-goals.
9. Keep source/evidence semantics distinct from accepted product decisions.
10. Do not select Domain entities/aggregates, architecture, API shape, persistence, package layout or implementation strategy.
11. If a needed product choice is not determined by accepted input, create a Core Question to Product Requirements and stop the affected capability rather than inventing behavior.
12. Do not invent numeric quality targets; preserve explicit NOT_REQUIRED decisions when they exist.
13. Produce one canonical managed `product-requirements/v1` artifact.
14. Give every atomic normative requirement a stable unique `REQ-*` identifier.
15. Record non-empty `source_refs` for every requirement; preserve rationale when it materially explains derivation or intent.
16. Mark only accepted current requirements as `ACCEPTED`; keep historical superseded requirements `RETIRED` rather than silently reusing IDs.
17. Review the resulting requirement list against the enumerated source/evidence set; no requirement-bearing source statement may disappear silently.
18. Run `workspace.py validate-artifact` on the candidate.
19. When machine-addressable semantic acceptance is used, require explicit Authority ownership for candidate/source assertions and constrain admitted source Authorities to the accepted upstream production contract plus Product Requirements itself. Do not admit Domain, Architecture, Interface, Data or Implementation decisions as requirement evidence merely because they are available or stakeholder-confirmed.
20. Apply common semantic acceptance, register all capabilities actually satisfied by the artifact, then re-evaluate the target Consumer.

## Stop conditions

Create or preserve a Product Requirements Question when:

- two accepted stakeholder/product sources conflict;
- an observable behavior choice materially changes product meaning and has not
  been decided;
- a numeric/quality constraint is required but unknown;
- acceptance cannot be stated without deciding an upstream product fact;
- the proposed requirement can only be justified by an already-derived downstream design decision rather than an independent observable product need/choice.

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

- every relevant source/evidence statement has an explicit disposition during requirements production;
- every requirement-bearing source statement maps to one or more accepted requirements or to a blocking Question;
- no observable scope/time/cardinality/negative/NOT_REQUIRED constraint is silently dropped;
- true duplicates may merge, but independent semantics remain independently addressable;
- every accepted requirement is supported by evidence or explicit product decision;
- every normative requirement is atomic enough to be reviewed and verified independently;
- every requirement has one stable unique `REQ-*` ID and non-empty source provenance;
- IDs are not reused for materially different requirement meaning;
- statements describe what the product must achieve, not how it is implemented;
- acceptance semantics are concrete enough for downstream design/verification;
- non-goals prevent accidental scope expansion;
- Domain/Architecture/Interface decisions remain downstream and are not promoted upstream through wording, provenance shortcuts or stakeholder reconfirmation;
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
