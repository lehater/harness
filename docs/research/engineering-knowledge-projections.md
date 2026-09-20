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


## NAPMS validation

NAPMS provides the structurally different second case requested by the Nutrition experiment.

Unlike Nutrition, NAPMS already owns canonical structural architecture in `docs/architecture/structurizr/workspace.dsl`. The project artifact specification explicitly assigns system/container/component/deployment structure to Structurizr DSL, while non-C4 rules, HTTP contracts, persistence and domain semantics remain in their own canonical formats.

The canonical graph registers that artifact as `C4-STRUCTURE` with kind `structural-architecture`; the Harness projection binds it to `SYSTEM-ARCHITECTURE` and capability `engineering.architecture.c4-model`. The IMPLEMENTATION consumer explicitly requires that capability.

NAPMS also has deterministic projections from other typed canonical artifacts into PlantUML views, and embeds those disposable views into the Structurizr workspace. This demonstrates that Structurizr may be either:

1. a canonical artifact when the project deliberately chooses Structurizr DSL as the natural notation for structural architecture; or
2. a disposable projection target when structural truth is owned elsewhere in a typed/adaptable form.

The distinction is ownership, not file format.

### Revised Structurizr conclusion

The Nutrition-only conclusion that Structurizr should not be a canonical store was too strong.

The validated rule is:

> Harness does not prescribe whether Structurizr is canonical or generated. A project may make Structurizr DSL the canonical owner of structural C4 semantics, or generate it from another canonical structural model. What is forbidden is two competing owners or semantic inference hidden in a renderer.

NAPMS proves that no universal `system-architecture/v1` schema is required for Harness integration. Its project-native Structurizr model already provides a deterministic machine-readable structural contract and is directly addressable through the canonical graph.

### Human projection evidence

NAPMS also has `generate_human_context_package.py`, which resolves the exact IMPLEMENTATION consumer capability closure, writes a manifest, groups artifacts for humans and copies canonical sources into a disposable package. This independently validates assembly projection.

Its current rendering of arbitrary canonical files inside fenced YAML/text is intentionally low-semantic: useful for bounded context packaging, but not evidence that Harness should parse every project-native notation into a universal document model.

## Cross-pilot conclusion

Nutrition and NAPMS together establish:

- capability closure, not a fixed document catalogue, selects documentation input;
- human-document grouping is projection policy;
- canonical format is concern-specific and project-native;
- standard machine-readable notations such as Structurizr/OpenAPI are valid canonical owners when they naturally express the concern;
- generated diagrams/documents remain disposable when their semantics are owned by another canonical artifact;
- Harness needs a renderer-neutral **projection contract**, not a universal canonical knowledge schema;
- no Core primitive or new DOCUMENTATION consumer is justified.

### Projection contract candidate

A generic projection declaration needs only:

- projection id;
- selected source artifact IDs or selected Consumer closure;
- renderer/adapter identity;
- output paths;
- deterministic regeneration command;
- optional view metadata;
- traceability back to canonical sources.

This is orchestration metadata, not semantic knowledge. NAPMS already carries an equivalent project-native form in `canonical-graph.yaml.projections`.

## Decision

The research question is sufficiently validated across two materially different projects.

Recommended canonicalization: generalize the existing project-native Human Projection contract into an **Engineering Knowledge Projection v0** contract covering assembly, semantic and visual projections, while preserving project-native projection declarations/adapters. Do not change Core v0.
