# Canonical artifact schema boundary — pilot research

Status: experimental. No canonical Harness model or main-branch change is proposed.

## Research question

Where can a reusable schema/format contract be attached without contradicting the
existing Harness model?

Candidates tested:

1. Authority;
2. CapabilityId;
3. knowledge_kind / Artifact Skill;
4. CanonicalArtifact;
5. reusable canonical-artifact schema/type selected by an Artifact Skill.

## Existing Harness invariants

- Authority is the atomic semantic decision-ownership boundary.
- CapabilityId names project-specific accepted knowledge exposed to consumers.
- CanonicalArtifact is an addressable accepted source owned by one Authority.
- knowledge_kind is repository-independent agent-routing metadata.
- one CanonicalArtifact may provide several CapabilityIds;
- one CapabilityId may have several providers inside one Authority;
- Core intentionally does not interpret arbitrary artifact contents.

Therefore storage/schema must not redefine Authority or Capability identity.

## Falsification 1 — schema per Authority

Rejected.

NAPMS SYSTEM-ARCHITECTURE owns at least:

- C4 structural architecture in Structurizr DSL;
- application architecture rules in YAML;
- module contracts in YAML.

These are one coherent Authority but materially different canonical shapes and
validators. Authority is therefore too coarse to select one storage schema.

## Falsification 2 — schema per CapabilityId

Rejected as a 1:1 rule.

NAPMS currently exposes the broad capability
`engineering.domain.tactical-model` from six CanonicalArtifacts. Five are
`tactical-domain-model`; one is `domain-language`.

The same CapabilityId is therefore not a reliable physical representation key.
This broad capability is also consistent with the existing Harness warning that
broad capabilities cannot prove independently scoped coverage.

A future refinement may make capabilities more precise, but current evidence does
not justify making CapabilityId the schema registry key.

## Falsification 3 — schema per knowledge_kind / Skill

Rejected.

The active System Architecture skill explicitly permits project-native architecture
artifacts and can materialize topology, dependency rules, consistency rules,
orchestration responsibilities and non-goals. NAPMS realizes those concerns in
several artifacts/notations, while Nutrition and the greenfield pilot use combined
Markdown architecture documents.

Likewise Interface Contract may naturally produce OpenAPI, CLI contract, UI
interaction contract or another project-native representation.

A Skill is a production procedure, not a single storage type.

## Candidate that survives the cardinality tests

The first stable attachment point is the concrete CanonicalArtifact, but a contract
defined separately for every individual artifact would not be reusable.

The surviving hypothesis is therefore a reusable **Artifact Schema/Profile** chosen
for each CanonicalArtifact materialization.

```text
Authority
  -> production contract(s)
      -> CapabilityId(s)
          -> Artifact Skill / semantic acceptance
              -> one or more CanonicalArtifacts
                   -> Artifact Schema/Profile
                       -> representation + structural validator
```

The schema/profile does not own the engineering decision. It specifies how one
canonical artifact shape carries a class of accepted semantics.

A CanonicalArtifact may provide several capabilities. A Skill may emit several
artifacts with different schemas. Several schemas may be available to one Skill.

## Product Requirements cross-project schema experiment

Product Requirements was selected because the same reusable Harness skill is
supported by three independent projects.

### Nutrition Management

Current representation: Markdown.

Observed shape:

- five material sections;
- 52 bullet requirements/scope statements;
- no separately claimed acceptance CapabilityId in the IMPLEMENTATION contract.

The material maps naturally to:

- purpose/goal;
- grouped requirements;
- constraints;
- non-goals.

A universal requirement that every Product Requirements artifact contain separate
acceptance examples would incorrectly strengthen Nutrition's current capability
contract.

### NAPMS

Current representation: typed project YAML.

Top-level semantic fields include:

- purpose;
- goal;
- journey;
- output row minimum;
- non-goals;
- acceptance examples;
- evidence.

This maps naturally to the same semantic family while retaining explicit acceptance
content because NAPMS's one artifact provides both product-intent and acceptance
capabilities.

### Greenfield CSV Deduplicator

Current representation: Markdown.

Observed shape:

- Product intent;
- Required behavior;
- Failure behavior;
- Acceptance expectations;
- Out of scope;
- ten numbered behavior requirements plus supporting lists.

It also maps naturally to the same semantic family.

### Result

A common **semantic Product Requirements schema family** appears plausible across
all three projects, but one mandatory physical encoding is not yet justified.

A candidate semantic shape is:

```yaml
purpose: string
goals: [string]
requirement_groups:
  - id: string
    title: string
    requirements: [string]
constraints: [string]          # optional
acceptance_examples: [string]  # optional unless the artifact claims acceptance knowledge
non_goals: [string]
```

Evidence/provenance references remain project/Core dependencies rather than copied
truth unless the artifact itself owns evidence semantics.

This is an experimental schema shape, not a canonical `product-requirements/v1`.

## Architecture counterexample

The Product Requirements result must not be generalized to one schema per Skill.

NAPMS architecture is deliberately split across standard C4 structure, architecture
rules and module contracts. Nutrition and the greenfield project combine several
of those concerns in narrative architecture documents.

Attempting one `system-architecture/v1` schema would either:

- become a weak generic bag of optional fields; or
- force unrelated architecture concerns into one artifact; or
- duplicate standard Structurizr semantics.

Therefore the likely reusable schema boundary is narrower than Artifact Skill and
closer to artifact concern, for example:

- structural-architecture;
- architecture-rules;
- module-contract-design;
- product-requirements;
- verification-plan;
- component-design;
- implementation-plan;
- etc.

These names remain hypotheses until repeated pilot evidence validates each one.

## Semantic contract versus representation

The experiments require two separate layers:

1. **Artifact semantic schema/profile** — what semantic fields/relationships this
   artifact shape can carry.
2. **Representation profile** — how that schema is encoded and validated.

Examples:

- product-requirements semantic profile -> Harness YAML or deterministic adapter
  from a project-native representation;
- structural-architecture -> Structurizr DSL may itself be the native representation
  profile;
- HTTP contract -> OpenAPI is both a standard semantic/representation contract;
- verification-plan -> current Harness `verification-plan/v1` YAML.

The distinction prevents “Markdown/YAML/DSL” from becoming the semantic taxonomy.

## What should be canonical

Current evidence supports the existing Harness rule rather than a mandatory
document catalogue:

- store a CanonicalArtifact when accepted engineering truth needs an addressable
  durable owner;
- expose a CapabilityId only when downstream engineering work/terminal consumers
  rely on that accepted knowledge;
- internal Authority refinements may remain canonical without a public Capability
  when they are necessary to own durable truth;
- projections, generated documentation and diagrams are non-canonical unless the
  represented model itself is the owned semantic truth;
- implementation/test evidence does not become design truth merely because it is
  machine-readable.

Thus “what is canonical” is decided by semantic ownership and downstream knowledge
contracts, not by the schema registry.

## Current hypothesis

Do not add Representation Contract or Artifact Type to Core.

Test an **Artifact Schema Registry** in the agent/workspace layer:

- schema/profile ids are repository-independent where repeated evidence exists;
- each schema defines semantic structure and structural validation;
- a schema may have a Harness-native representation or a standard/native adapter;
- Artifact Skills declare which schemas/profiles they can produce;
- one Skill may support several schemas;
- one artifact may provide several CapabilityIds;
- semantic acceptance remains separate from schema validation;
- legacy project-native artifacts require explicit deterministic adapters only when
  automated consumers need structured access.

## Promotion gate

Do not canonicalize this hypothesis until all of the following are demonstrated:

1. at least Product Requirements plus two materially different artifact concerns
   work across Nutrition, NAPMS and greenfield;
2. no semantic truth must be duplicated merely to satisfy Harness;
3. a standard-native artifact such as OpenAPI/Structurizr remains first-class;
4. a compound legacy artifact can be migrated/split without changing Authority
   ownership or capability semantics;
5. invalid structured artifacts are rejected deterministically;
6. generated projections remain disposable;
7. Core behavior remains unchanged.


## Verification-family cross-check

Verification provides a stronger counterexample than architecture.

Nutrition currently has two distinct accepted canonical verification artifacts:

- `docs/redesign/verification-design.md` — pre-code, design-derived evidence classes; explicitly independent of current tests;
- `.harness/knowledge/verification-strategy.yaml` — `verification-plan/v1`, with concrete checks and evidence paths/commands against the current baseline.

NAPMS uses `test-intent` YAML centered on required scenarios and traceability, while
greenfield uses a narrative strategy organized by evidence level.

Therefore `verification-plan/v1` is a valid reusable schema for one materialization
profile, but it is not the schema of the entire VERIFICATION Authority or of every
`verification-strategy` routed work item.

This strongly supports treating the **schema/profile id itself as the reusable artifact
contract** rather than introducing a second redundant ArtifactType object.

## Simplified candidate model

The experiments now favor this minimal model:

```text
Authority
  -> Production Contract
      -> CapabilityId
          -> knowledge_kind (optional routing hint)
              -> Artifact Skill
                  -> chooses one or more Artifact Schemas / native standard profiles
                      -> CanonicalArtifact instance(s)
                          -> provides CapabilityId(s)
```

An Artifact Schema/Profile defines:

- semantic shape owned by that artifact instance;
- required/optional fields or grammar;
- structural validator;
- renderer/projection support where deterministic;
- version.

Examples of the same concept:

- `domain-model/v1` — Harness schema;
- `verification-plan/v1` — Harness schema;
- Product Requirements candidate schema — reusable semantic schema still under test;
- OpenAPI version/profile — external standard used as the artifact schema/profile;
- Structurizr DSL + project invariants — external/native structural architecture profile.

No separate `RepresentationContract` or `ArtifactType` entity is currently justified.
If a schema/profile id can carry the reusable contract, introducing both would duplicate
identity.

## Remaining question

The unresolved question is no longer “what format for every Capability?” It is:

> Which recurring canonical artifact semantic shapes deserve a reusable schema/profile,
> and which should remain project-native until repeated consumer evidence exists?

The schema catalog must therefore be empirical and sparse. Skills may support several
schemas; projects instantiate only the schemas their actual production contracts need.


## Cross-project schema-family inventory

The current canonical artifacts and greenfield evidence produce the following
non-normative inventory. “Strong” means repeated independent project evidence, not
that a schema has been designed or accepted.

| Semantic artifact family | Nutrition | NAPMS | Greenfield | Evidence result |
| --- | --- | --- | --- | --- |
| Problem evidence | Markdown Problem | YAML discovery | Markdown Problem | strong recurring family; schema candidate |
| Product requirements | Markdown requirements | YAML product-requirements | Markdown requirements | strong recurring family; schema candidate |
| Strategic domain structure | Markdown strategic model + context map | typed capabilities/contexts/relationships | absent | recurring concern, but split shape differs |
| Tactical domain model | per-context Markdown | typed tactical-domain-model/domain-language | absent | strong two-project need; `domain-model/v1` is too small for full tactical semantics |
| Application/use-case design | application-design Markdown | typed use-case/journey | absent | related but not yet proven to be one schema family |
| Structural architecture | embedded narrative topology | Structurizr DSL | embedded narrative topology | standard-native structural profile proven; migration from prose requires reviewed semantic extraction |
| Architecture rules | embedded in target architecture | typed application-architecture-rules | embedded in system architecture | recurring facet; likely separate profile from structure |
| Module/component contracts | Component Design + application contracts | typed module-contract-design | architecture/implementation boundaries | recurring concern; ownership differs by project, so schema must not encode Authority |
| Data/persistence | Data Design Markdown | typed physical-persistence-model | not applicable | recurring but detail level differs; likely more than one profile |
| CLI interface contract | Markdown CLI | not applicable | Markdown CLI | repeated direct profile candidate |
| HTTP interface contract | absent | OpenAPI | absent | standard-native profile; no Harness duplicate schema needed |
| UI contract | absent | typed UI navigation/screen contracts | absent | single-project evidence only |
| Engineering policy | Markdown | no equivalent separate owner | absent | insufficient cross-project evidence |
| Security architecture/analysis | merged/not separately applicable | typed security artifacts | absent | insufficient cross-project evidence for generic schema |
| Operability | merged/not separately applicable | typed observability requirements | absent | insufficient cross-project evidence |
| Implementation design/plan | Markdown implementation design | typed implementation readiness | Markdown plan + completion artifact | strong recurring family; combination/splitting differs |
| Verification design/strategy | Markdown redesign verification + typed verification-plan | typed test-intent | Markdown strategy + scenarios | strong recurring concern but clearly several artifact profiles |

### Existing schema audit

The two existing Harness schemas are valid evidence but must not be overgeneralized.

**`domain-model/v1`** carries purpose, terms, concepts, responsibilities and
invariants. Real NAPMS tactical domain models additionally own aggregates, entities,
value objects, domain services, command semantics and explicit non-decisions.
Nutrition tactical documents also own operations, cross-context relationships,
special evidence semantics and precision rules. Therefore `domain-model/v1` is a
compact domain-knowledge profile, not a universal tactical-domain schema.

**`verification-plan/v1`** carries purpose, scope and concrete checks with evidence.
Nutrition's pre-code redesign Verification Design intentionally has no current-test
evidence. NAPMS test-intent is scenario/trace oriented, and greenfield verification is
organized by evidence level. Therefore `verification-plan/v1` is one verification
artifact profile, not the universal Verification schema.

### Data/Persistence check

Nutrition Data Design owns representation rules, logical context ownership,
scalar encodings, transaction/read behavior and migration constraints but does not
enumerate the complete physical schema.

NAPMS `physical-persistence-model` owns concrete schemas, tables, columns, keys,
indexes, checks and owner-enforced invariants.

Collapsing both into one mandatory physical-persistence schema would either force
Nutrition to decide unnecessary physical details early or make most fields optional.
The evidence favors at least a conceptual Data Design profile and a more concrete
Physical Persistence profile.

## What the inventory says about “final artifacts”

Harness should not define a mandatory final-document list.

The stable axis is:

1. the Engineering Graph determines which public knowledge capabilities a selected
   consumer requires;
2. Authorities decide and own the accepted semantics;
3. CanonicalArtifacts persist the smallest useful owner-local units of that truth;
4. each concrete CanonicalArtifact selects a reusable schema/profile only when a
   validated profile exists for its semantic shape;
5. Artifact Skills may create one or several such artifacts;
6. generated human/visual views remain projections.

This means a “final artifact catalogue” can exist only as a **schema/profile
catalogue of reusable materialization shapes**, not as a mandatory lifecycle
checklist.


## Migration consequence

The Product Requirements experiment also rejects a generic automatic
Markdown-to-schema migration.

Nutrition and greenfield carry accepted requirements in prose sections and lists.
Mapping those statements into semantic schema fields such as requirement,
constraint, acceptance example or non-goal requires classification judgement.
That judgement can change meaning and therefore cannot be hidden inside a renderer
or deterministic projection adapter.

Consequences:

- new artifacts may be authored directly in an accepted reusable schema/profile;
- standard-native artifacts may remain in their native standard;
- existing project-native prose can remain canonical until there is a justified
  migration/re-materialization;
- migration of accepted prose into a typed schema is Authority-owned semantic work,
  followed by ordinary semantic acceptance;
- a generated typed copy of prose must not silently become a second canonical owner.

This means schema standardization can be prospective and incremental. It does not
require a repository-wide rewrite merely to adopt Harness.
