---
name: domain-use-case
description: "Use for actionable CREATE work that defines independently valuable domain-focused behavior contracts before tactical modeling, without choosing aggregates, transport or persistence."
---

# Domain Use-Case Design

## Trigger

Use when actionable work has `knowledge_kind: domain-use-case` and observable domain behavior needs an independently valuable contract for the selected Consumer/scope. The existence of this skill or of a reference Authority does not establish applicability.

## Inputs

- accepted Product Requirements/acceptance semantics for the selected scope;
- relevant accepted problem evidence;
- accepted strategic-domain or model-context knowledge **only when its specific decisions materially constrain the selected use case** and its Capability is a direct production prerequisite;
- unresolved Questions owned by Domain Use-Case Design.

Strategic Domain ownership is **not a universal prerequisite**. A project can own a coherent domain behavior contract directly under DOMAIN-USE-CASE-DESIGN without producing subdomain classification/investment knowledge. A previously accepted strategic decision that materially constrains this behavior must be respected and exposed as a direct `requires` dependency; do not silently bypass it.

## Read boundary

Read accepted product behavior, relevant domain semantics and only the directly necessary upstream ownership decisions. Do not use tactical models, APIs, schemas or existing implementation as truth.

## Procedure

1. Check applicability for the actual Consumer/scope: identify the behavior requiring independent refinement, the accepted source obligations, and a concrete downstream consumer or explicit terminal reason. If this knowledge is already complete within a coherent Product Requirements or other accepted owner and has no independent consumption/change boundary, do not produce an artificial use-case Capability; route any assessment through the project-owned applicability process.
2. Confirm that every material upstream semantic dependency is represented in the selected production's `requires`. Do not add DOMAIN-STRATEGY or MODEL-CONTEXT-STRATEGY merely because a reference skill or methodology mentions them. If an accepted strategic/context decision materially constrains this use case, require that accepted knowledge before production.
3. Select one coherent domain responsibility from accepted product evidence or applicable accepted domain decisions. Do not infer strategic investment/subdomain ownership from a technical component, ACL context, or use-case title.
4. Derive actors/initiators only where they affect domain behavior; do not invent authentication roles.
5. State preconditions and accepted inputs in domain language.
6. Define success outcomes, domain rejections and meaningful state/effect changes.
7. Preserve unknown, temporal, identity and provenance semantics already accepted upstream.
8. Separate independent use cases instead of encoding workflow/transport sequencing into one contract.
9. Do not choose aggregates, entities/value objects, transaction technology, endpoint shapes or storage.
10. Route missing product meaning upstream and tactical questions downstream. When the behavior itself is undecidable, preserve/create a blocking Question addressed to the semantic decision owner instead of accepting a guessed contract.
11. Produce/register the smallest project-native use-case artifact and apply semantic acceptance.

## Stop conditions

Stop when an observable outcome is not accepted upstream; an applicable material upstream prerequisite is missing; the domain behavior/ownership is undecidable; behavior can only be described by assuming a tactical identity/invariant; or the use case would invent interface/security/persistence semantics.

An unassessed strategic Authority is **not by itself** a blocker for this use case. Assess its relevance from accepted evidence and consumers. Never infer `NOT_APPLICABLE` merely from an absent graph node; when evidence is insufficient, retain an explicit applicability Question/obligation under the project assessment contract.

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

- independently valuable behavior and its concrete consumer/terminal reason are established;
- behavior traces to accepted product semantics;
- applicable accepted strategic/context constraints are preserved, with direct `requires` and lifecycle provenance when materially consumed;
- no strategic classification or ownership is fabricated to satisfy a skill;
- no tactical model is smuggled in as a precondition;
- transport/storage/security representation is absent unless already semantic upstream;
- missing domain behavior is blocked by a real Question, not waived by a semantic review PASS;
- downstream design/verification can proceed without guessing domain behavior.

## Registration

Register under DOMAIN-USE-CASE-DESIGN and provide the exact domain-use-case capability or grouped capabilities genuinely covered. Reevaluate the selected Consumer and its Engineering Coverage after admission.

## Human projection

Prefer compact behavior contracts organized by domain responsibility, not UI journeys or endpoint lists.
