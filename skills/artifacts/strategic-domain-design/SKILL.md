---
name: strategic-domain-design
description: "Use for actionable CREATE work that must define semantic domain ownership boundaries and relationships before tactical modeling or technical architecture."
---

# Strategic Domain Design

## Trigger

Use when actionable work has `knowledge_kind: strategic-domain-design` and the product has non-trivial semantic ownership boundaries, multiple domain capabilities or independently changing domain areas.

## Inputs

- accepted Product Requirements and acceptance semantics;
- accepted Discovery evidence needed to disambiguate domain meaning;
- existing accepted domain ownership constraints, if any;
- unresolved Questions owned by Strategic Domain Design.

## Read boundary

Use accepted product/problem knowledge as truth. Do not infer context boundaries from package names, database schemas, service topology, existing code, prior tactical aggregates or UI/API grouping.

## Procedure

1. Identify cohesive domain responsibilities required by accepted product behavior.
2. Apply the Authority atomicity test to each candidate boundary: semantic cohesion, independent change and public contract.
3. Assign one semantic owner to each accepted domain responsibility; avoid duplicate ownership.
4. Define public semantic relationships between independently modeled areas using stable concepts/facts, not private models.
5. State which upstream concepts cross boundaries and which ownership assumptions are explicitly forbidden.
6. Preserve design freedom below this layer: do not choose aggregates, tables, APIs, modules or deployment topology.
7. If a boundary depends on unresolved product meaning or two areas cannot be separated coherently, create/route a Question rather than forcing a context split.
8. Produce the smallest project-native strategic domain artifact, accept/register it and reevaluate the target.

## Stop conditions

Stop when product behavior is too ambiguous to assign semantic ownership; a proposed split is justified only by technical structure; two candidate owners both claim the same decision; or resolving a relationship would require tactical/technical choices.

## Output contract

Produce accepted semantic decomposition containing only applicable:
- domain responsibility boundaries;
- ownership statements;
- public semantic relationships/dependencies;
- cross-boundary identity/reference expectations at a conceptual level;
- explicit non-ownership/non-goals;
- unresolved Questions.

A Context Map or named Bounded Contexts may be used when useful, but no notation is mandatory.

## Acceptance checks

- every boundary is justified by the atomicity test, not repository structure;
- every material domain decision has one owner;
- relationships preserve upstream product meaning;
- tactical identities/invariants and technical architecture remain downstream;
- unresolved product/domain meaning is not silently converted into a boundary.

## Registration

Register accepted project-native artifact(s) under STRATEGIC-DOMAIN-DESIGN and provide only the capabilities actually established.

## Human projection

Prefer a concise ownership/relationship map plus rationale, not a large DDD taxonomy.
