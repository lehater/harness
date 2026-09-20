# Engineering Knowledge Projection Research

Status: experimental research validated against Nutrition Management.

## Question

Can Harness derive useful human and visual documentation from accepted engineering knowledge without creating a second semantic source of truth?

## Evidence from Nutrition Management

Nutrition already has two projection modes in one repository:

- managed typed knowledge: `.harness/knowledge/verification-strategy.yaml` is rendered deterministically by `workspace.py`;
- project-native knowledge: the IMPLEMENTATION closure is assembled into `docs/generated/{README,overview,domain-and-data,implementation-guide,verification-and-readiness}.md`.

The project-native projection demonstrates that document count and grouping are presentation policy. The IMPLEMENTATION closure is the semantic input; generated documents are not capability providers.

## Artifact inventory conclusion

The IMPLEMENTATION closure spans accepted requirements, domain/context knowledge, architecture, application/data/interface design, implementation stack, engineering policy, component design, verification design/strategy and implementation design.

These do not map 1:1 to generated documents. One canonical artifact may feed several human topics and one human topic may assemble several canonical artifacts.

Therefore Harness must not define a universal fixed document set.

## Projection classes

Three projection classes are justified:

1. **Assembly projection** — index, navigation, readiness, source traceability and grouping of existing project-native artifacts.
2. **Semantic projection** — deterministic rendering of typed canonical knowledge into narrative/tables.
3. **Visual projection** — deterministic rendering of typed structural knowledge into diagrams or external visualization formats.

All three are disposable views. Deleting them must not change Core/Consumer state.

## Structurizr experiment

Nutrition contains enough accepted architecture prose for a human to draw useful C4 views: one local modular-monolith process, four context-aligned modules, provider/consumer directions, one relational store, CLI boundary and solver/infrastructure boundaries.

It does **not** contain a canonical typed representation that deterministically identifies C4 System/Container/Component elements, relationships and view membership.

A generic Harness renderer would therefore have to interpret prose and make modeling choices. That violates the existing projection boundary: projection may faithfully reorganize accepted knowledge but must not create architecture semantics.

### Consequence

Do not restore Structurizr as a canonical store and do not add a prose-to-C4 inference renderer.

Structurizr is a valid **projection target** only when its required structural semantics are already available in a typed canonical artifact or in a project-owned deterministic adapter.

## Minimal future contract

A visual renderer should consume an explicit structural projection input such as:

```text
accepted architecture artifact
        ↓
project-owned adapter OR typed architecture schema
        ↓
structural projection model
        ↓
Structurizr / Mermaid / other renderer
```

The intermediate structural model must contain only accepted facts required by renderers: stable element identity/type, containment, relationships, optional deployment placement and source traceability. It must not become a new Authority or duplicate richer project semantics.

## Schema decision

Do not introduce `system-architecture/v1` merely to support diagrams.

A typed architecture schema is justified only when at least two structurally different consumers need the same machine-readable semantics for purposes beyond one renderer. Otherwise a project-owned adapter is the smaller solution.

This follows the existing managed-knowledge rule: add typed schemas one at a time from demonstrated consumer need, not from a desire for a universal DSL.

## Documentation consumer decision

Do not add a DOCUMENTATION Authority/Capability/Consumer.

Documentation is a view over a selected semantic closure. Generating or deleting documentation must not affect IMPLEMENTATION completeness. A separate Consumer is justified only if a future external consumer genuinely requires an independently owned engineering capability rather than a presentation.

## Findings

- **P0:** none.
- **P1:** visual projection is not deterministic from current project-native architecture prose; semantic inference must not be hidden in a renderer.
- **P2:** project-native Human Projection has a validated contract but no generic renderer/configuration implementation yet.
- **P2:** managed projection supports only `domain-model/v1` and `verification-plan/v1`; this is intentionally narrow, not a completeness defect.
- **P3:** generated document taxonomy should remain project presentation policy.

## Recommended next experiment

Validate the same three projection classes against NAPMS. Specifically test whether its existing canonical graph can deterministically supply structural identities/relationships through an adapter. If Nutrition requires a typed schema while NAPMS can adapt existing structure, that is evidence for a renderer-neutral structural projection contract, not evidence for a universal canonical architecture format.

Do not change Core or Integration Contract v0 from the Nutrition result alone.
