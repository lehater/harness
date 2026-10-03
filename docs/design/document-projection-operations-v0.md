# Document Projection Operations v0

Status: canonical v0.

## Purpose

Define the reusable Harness mechanism for producing specialized generated
project documents and diagrams from accepted canonical engineering knowledge.

This contract covers projections whose target representation needs its own
procedure or format expertise, for example an architecture model, data model,
process model or diagram source. It does not define the semantics of any
particular target format.

The mechanism extends Human Documentation Projection without creating a second
source of engineering truth, a parallel skill router, or a new Core concept.

## Relationship to existing contracts

This contract composes existing Harness owners:

- `docs/design/human-documentation-projection-v1.md` owns Consumer-scoped
  source closure, projection manifest/plan, provenance, freshness and packaging;
- `docs/design/operation-orchestration-v0.md` owns composition of public and
  internal operations;
- `docs/design/agent-skill-surfaces-and-consumer-distribution-v0.md` owns
  skill identity, routing surfaces and Consumer Pack distribution;
- `docs/design/agent-instruction-architecture-v0.md` owns instruction
  discovery and the instruction/data trust boundary;
- the target repository's CanonicalArtifacts remain the only owners of project
  product/domain/architecture/implementation semantics.

This document owns only the common mechanism by which a source-bounded
projection operation turns accepted canonical knowledge into a generated view.

## Core invariants

1. A generated projection is not a `CanonicalArtifact` merely because it is
   useful, versioned or checked into Git.
2. A generated projection provides no `CapabilityId` and cannot change target
   state.
3. Deleting all generated projection output must not lose accepted engineering
   knowledge.
4. Generated output must never be used as semantic input to regenerate itself or
   another canonical/project decision.
5. Projection operations consume only sources already admitted by the compiled
   Human Projection manifest/plan for the selected scope.
6. A projection operation must not scan unrelated repository content to make an
   output appear complete.
7. Missing or conflicting source semantics remain missing/conflicting; a
   projection must not repair, select or invent engineering decisions.
8. Projection routing reuses `harness.application.skill_router`; no projection-
   specific router or duplicate skill registry is permitted.
9. Projection-specific procedure knowledge belongs in a routed skill; durable
   reusable format policy belongs in a canonical Harness contract/profile, not
   copied independently into multiple skills.
10. Workspace/domain code must not depend on the Application routing layer.
    Routing and sequencing remain Application/coordinator responsibilities.

## Execution model

The default execution path is:

```text
Engineering Graph + Core/project realization + Consumer
        ↓
Human Projection manifest
        ↓
source-bounded projection plan
        ↓
Application coordinator
        ↓
skill_router operation
        ↓
registered internal projection operation
        ↓
projection-specific skill + format profile
        ↓
generated output under docs/generated/**
```

The Human Projection manifest/plan is the source-selection boundary. A
projection operation does not independently rediscover CanonicalArtifacts by
walking the repository, searching by filename, or reconstructing a second
artifact index.

## Projection operation identity

A reusable specialized projection is modeled initially as an **internal
Consumer operation**.

Example identities are semantic projection responsibilities rather than generic
tool names:

```text
architecture-c4-structurizr
data-model-dbml
sequence-diagram-plantuml
state-machine-plantuml
```

A generic identity such as `plantuml` is normally too broad because different
diagram types have different source semantics, completeness rules and
acceptance criteria.

The operation is registered through the existing Consumer Operation Registry
and Skill Surface Registry. It is invoked through the normal typed
`skill_router` with an authorized parent operation, normally
`human-documentation-projection`.

Renderer identity is not projection-instance identity. A plan section may carry
an explicit `scope` owned by the projection responsibility, and the same
renderer operation may be invoked multiple times for independent scopes. For
example, separate persistence ownership boundaries may each invoke
`data-model-dbml` and produce distinct generated outputs. Scope metadata is
carried by the existing Human Projection recipe/plan; it does not create a new
router, source registry or Core concept.

Do not introduce a new route class for projections until multiple implemented
consumers demonstrate that internal operations cannot express the required
contract without distortion.

## Operation contract

Each specialized projection skill must make at least these boundaries explicit:

- **Trigger** — which planned projection responsibility activates it;
- **Inputs** — compiled manifest/plan data, target output and format/profile
  contract;
- **Read boundary** — exact CanonicalArtifact IDs/paths permitted by the plan;
- **Procedure** — how accepted source meaning is mapped into the target
  representation;
- **Stop conditions** — missing/conflicting semantics or unsupported source
  shape that prevents faithful projection;
- **Output contract** — generated format, repository-relative destination and
  required provenance;
- **Acceptance checks** — source-bounding, syntax/shape validation where
  available, and representation-specific invariants.

The skill is procedural knowledge. It is not a second owner of format policy or
project engineering truth.

## Format profiles and reusable static policy

When a target representation needs stable syntax/style/layout conventions,
those rules should be stored once in a versioned Harness-owned profile or
specification and consumed by the projection skill.

Conceptually:

```text
projection SKILL.md
    owns procedure and semantic mapping discipline

spec/projection/<format-or-projection>-vN.*
    owns reusable syntax/style/default conventions

project CanonicalArtifacts
    own project semantics
```

A format profile may define stable identifiers, naming conventions, supported
language subset, layout defaults, output conventions or validator expectations.
It must not encode project-specific architecture/domain/product decisions.

Files required by Consumer projection skills must be distributed through the
existing Consumer Pack rules rather than copied into target-project skill trees.

## Source boundary and fail-closed behavior

For one planned projection, the coordinator supplies the source set already
resolved by Human Projection.

The projection skill may read only those sources. Deterministic source-boundary
validation applies generated-input rejection to the sources selected for that
planned section; unrelated manifest members do not widen or block that section.

It must not:

- use generated documentation as authority;
- search implementation/code as substitute architecture/domain truth unless
  that code is itself an explicitly selected CanonicalArtifact;
- add another Capability merely because the chosen document would conventionally
  contain it;
- widen scope implicitly to another Authority or artifact;
- silently omit a material contradiction and then present the projection as
  complete.

If required target content cannot be supported by the allowed canonical source
set, the projection is incomplete/blocked for that output. The generator does
not manufacture the missing semantics.

## Output location and canonical boundary

Generated project views should live under the configured generated-document
root; the default convention remains:

```text
docs/generated/**
```

Canonical project documents and generated projections should not be mixed in
the same storage role.

Generated files may be checked into Git for review, history and diffability.
Version control does not make them canonical. A project may instead regenerate
them in CI; that repository policy does not alter their semantic role.

Every generated output should make its derived status explicit in a
human-readable or machine-readable form equivalent to:

```text
GENERATED PROJECTION
NOT A SOURCE OF TRUTH
```

## Provenance and freshness

A specialized projection must preserve enough identity to explain and reproduce
its result.

At minimum the projection result or its package metadata should bind to:

- projection/renderer operation identity;
- current Human Projection manifest digest;
- selected CanonicalArtifact IDs;
- source paths and source digests/baseline when the manifest records them;
- generated output path(s).

Existing Human Projection freshness validation remains authoritative for
canonical source changes. A generated output must not be accepted as current
when its bound source baseline is stale.

Existing visual-asset/package mechanisms should be reused when they satisfy the
needed result/provenance shape; do not create a parallel packaging model merely
for one format.

## Layering constraint

The Workspace bounded context owns validation/materialization of optional
managed knowledge and disposable projections. The Application layer owns
routing/orchestration.

Therefore this dependency is forbidden:

```text
harness.workspace.* → harness.application.skill_router
```

The coordinator instead composes the mechanisms:

```text
Application coordinator
    ├── Workspace: compile/validate manifest and plan
    └── Application skill_router: resolve projection operation
```

This preserves the canonical bounded-context dependency direction.

## Vertical-slice adoption rule

Add specialized projection capabilities one complete slice at a time.

A slice is not complete merely because a `SKILL.md` exists. It should prove the
whole relevant path:

```text
recipe/plan
  → existing routing
  → projection skill
  → reusable format/profile contract
  → generated output
  → validation
  → Consumer Pack availability
  → assurance for source/routing/distribution boundaries
```

The first implementation should remain specific. Extract a generic renderer
dispatcher, shared result type, new route class or other common abstraction only
after more than one implemented projection demonstrates the same invariant and
the existing mechanism is insufficient.

## Assurance boundary

Projection slices primarily exercise:

- **HA-A16 Agent/method/artifact routing** — internal operation authorization and
  deterministic route identity;
- **HA-A17 Repository realization and projections** — derivation from accepted
  truth, source bounding, freshness and non-canonical output;
- **HA-A18 Consumer distribution and compatibility** — required projection
  skills/contracts are present in the pinned Consumer Pack without leaking
  Maintainer surfaces.

Use the Harness Assurance Policy: prove deterministic routing/source invariants
at the smallest falsifiable level first, then promote to project-shaped or agent
evidence only when the transformation itself requires judgement.

## Non-goals

This contract does not define:

- a mandatory project document taxonomy;
- one universal renderer framework;
- one universal projection IR;
- a new Core entity, Authority or Capability type;
- a new skill route class;
- a new skill router;
- a second CanonicalArtifact/source registry;
- semantic inference from arbitrary repository prose;
- canonical status for generated files;
- the syntax or semantics of Structurizr, PlantUML, DBML, BPMN, OpenAPI,
  AsyncAPI or any other specific output representation.
