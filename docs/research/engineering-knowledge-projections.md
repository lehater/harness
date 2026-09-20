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


## Representation-contract correction

Follow-up inspection of the active artifact skills shows that Harness already has the beginning of a representation model, but it is split across prose contracts.

The agent-layer validator requires every artifact skill to declare either an `Output schema` or an `Output contract`. Managed artifacts such as `domain-model/v1` and `verification-plan/v1` have executable schema validators/renderers. Other skills deliberately target standard or project-native representations such as OpenAPI and Structurizr DSL and rely on deterministic native/project validators.

Therefore “canonical artifacts may use arbitrary formats” is rejected.

### Representation Contract v0

For every reusable `knowledge_kind`, the producing artifact skill MUST define an explicit Representation Contract. It determines which representations are admissible for that knowledge and how structural validity is established.

A Representation Contract has these logical fields:

- `knowledge_kind`;
- accepted representation family/families;
- schema/grammar/specification identifier when applicable;
- deterministic validator;
- canonicalization/normalization rules when needed;
- optional renderer/projection adapters;
- artifact-skill owner.

A representation family may be:

1. **Harness typed schema** — e.g. `domain-model/v1`, `verification-plan/v1`;
2. **standard/domain notation** — e.g. OpenAPI or Structurizr DSL, validated by its native specification/tooling plus project invariants;
3. **project-native typed contract** — allowed only when the project supplies a deterministic validator/adapter sufficient for the declared knowledge contract.

Free-form prose with no deterministic representation contract is not sufficient merely because it is registered as a CanonicalArtifact. It may still be canonical rationale/evidence where machine extraction is not a downstream requirement, but it cannot satisfy a capability whose consumers require structured semantics unless its Representation Contract explicitly permits that form.

### Relationship to Core

Representation Contract does not belong in Core v0. Core remains concerned with ownership, capabilities, dependencies and Questions.

The agent/skill layer owns production semantics:

```text
Engineering Graph production
        ↓ knowledge_kind
Artifact Skill
        ↓
Representation Contract
        ↓
Canonical Artifact
        ↓
validator
        ↓
semantic acceptance
        ↓
provides Capability
```

This also means schema validation must not be confused with semantic acceptance. A structurally valid artifact can still be semantically wrong or unsupported; `provides` is registered only after both representation validation and semantic acceptance.

### Relationship to Projection

Projection is downstream of Representation Contract:

```text
Canonical Artifact
        + Representation Contract
        ↓
Projection Adapter / Renderer
        ↓
human / visual / machine view
```

A projection must consume only semantics admitted by the Representation Contract. It must not recover missing structure by interpreting arbitrary prose.

### Cross-pilot validation

Nutrition demonstrates Harness-managed typed schemas and project-native artifacts. NAPMS demonstrates standard typed notations: Structurizr DSL canonically owns C4 structure and OpenAPI canonically owns HTTP representation. Both fit one model without forcing either project into a universal Harness DSL.

### Priority findings

- **P0:** none.
- **P1:** current skill contracts encode representation requirements mostly in prose; the relationship `knowledge_kind -> admissible representation -> validator` is not yet machine-addressable as one registry.
- **P1:** project-native free-form artifacts must not be treated as equivalent to typed knowledge when downstream consumers need deterministic semantic access.
- **P2:** managed schema registry in `workspace.py` is implementation-local and covers only two schemas; it is not yet the general representation registry.
- **P2:** projection contracts should reference representation contracts rather than independently deciding how to parse canonical artifacts.

## Revised promotion sequence

Before promoting Engineering Knowledge Projection v0:

1. canonicalize Representation Contract v0 at the agent/skill layer;
2. make artifact-skill representation declarations machine-checkable without moving semantic ownership into Core;
3. retain Harness schemas, standard notations and validated project-native typed formats as first-class representation families;
4. make Projection v0 consume those contracts;
5. validate against Nutrition and NAPMS;
6. only then merge the research into main.

No universal engineering-document schema is proposed.


## Experiment status: not canonical

The Representation Contract hypothesis is explicitly **not accepted or canonicalized** by this research branch.

Two isolated pilot branches were created for falsification:

- Nutrition Management: `research/representation-contract-v0`
- NAPMS: `research/representation-contract-v0`

No pilot change was written to `main`.

### First falsification result

NAPMS contains an independently developed artifact-type registry that already models canonical representation rules, format families, validator requirements, canonical uniqueness and projection non-canonicity. This is strong convergent evidence for the Representation Contract hypothesis, but it is not yet proof that the proposed Harness abstraction is correctly shaped.

Nutrition is materially weaker: several `knowledge_kind` values currently resolve to Markdown/project-native artifacts whose integration validator proves graph/integration properties, not necessarily the internal semantic structure of the artifact. The experiment therefore exposes an important distinction:

- **artifact validity**: file/graph/ownership/integration is valid;
- **representation validity**: the artifact conforms to a machine-checkable representation contract for its knowledge kind;
- **semantic acceptance**: the represented decisions are accepted and supported.

These three must not be collapsed.

The Nutrition experiment is therefore intentionally incomplete until each selected knowledge kind can demonstrate what its representation validator actually proves. A generic “project validator” label is insufficient evidence.

### Acceptance gate for the hypothesis

Do not promote Representation Contract v0 or Projection v0 to Harness main until the experiments demonstrate, on both pilots:

1. every sampled `knowledge_kind` resolves deterministically to an admissible representation;
2. invalid representation is rejected independently of semantic judgement;
3. valid representation does not automatically imply semantic acceptance;
4. canonical ownership remains unique;
5. projections can be regenerated without changing canonical state;
6. project-native standard formats need no duplicated Harness schema;
7. the contract can be consumed by an agent/validator without project-specific inference hidden in Harness.

Failure of any item requires revising or rejecting the abstraction rather than canonicalizing it.
