---
name: domain-use-case
description: "Use for actionable CREATE work that defines stable domain-focused behavior contracts before tactical modeling, without choosing aggregates, transport or persistence."
---

# Domain Use-Case Design

## Trigger

Use when actionable work has `knowledge_kind: domain-use-case` and observable domain behavior needs an independently valuable contract before tactical modeling.

## Inputs

- accepted Product Requirements/acceptance semantics;
- accepted Strategic Domain ownership for the selected scope;
- relevant accepted problem evidence;
- unresolved Questions owned by Domain Use-Case Design.

## Read boundary

Read only accepted behavior and strategic ownership needed for the selected domain slice. Do not use tactical models, APIs, schemas or existing implementation as truth.

## Procedure

1. Select one coherent domain responsibility owned by the target Authority/scope.
2. Derive actors/initiators only where they affect domain behavior; do not invent authentication roles.
3. State preconditions and accepted inputs in domain language.
4. Define success outcomes, domain rejections and meaningful state/effect changes.
5. Preserve unknown, temporal, identity and provenance semantics already accepted upstream.
6. Separate independent use cases instead of encoding workflow/transport sequencing into one contract.
7. Do not choose aggregates, entities/value objects, transaction technology, endpoint shapes or storage.
8. Route missing product meaning upstream and tactical questions downstream; create a blocking Question when the behavior itself is undecidable.
9. Produce/register the smallest project-native use-case artifact and reevaluate.

## Stop conditions

Stop when an observable outcome is not accepted upstream; ownership is unclear; behavior can only be described by assuming a tactical identity/invariant; or the use case would invent interface/security/persistence semantics.

## Output contract

For each selected use case capture only useful:
- purpose;
- trigger/initiator;
- preconditions;
- domain inputs/references;
- success/effect;
- domain rejection/alternative outcomes;
- semantic postconditions;
- explicit non-goals;
- Questions.

## Acceptance checks

- behavior traces to accepted product semantics;
- strategic ownership is preserved;
- no tactical model is smuggled in as a precondition;
- transport/storage/security representation is absent unless already semantic upstream;
- downstream tactical/application design can proceed without guessing domain behavior.

## Registration

Register under DOMAIN-USE-CASE-DESIGN and provide the exact domain-use-case capability or grouped capabilities genuinely covered.

## Human projection

Prefer compact behavior contracts organized by domain responsibility, not UI journeys or endpoint lists.
