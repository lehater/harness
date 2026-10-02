# Harness Agent Skill Surfaces and Consumer Distribution v0

Status: accepted architecture decision on the audit branch.

## Purpose

Define how Harness agent procedures are separated, discovered and physically
made available when Harness is developed in its own repository versus consumed
from another repository.

This contract is about **agent tooling distribution and procedure discovery**.
It does not change Harness Core entities, project semantic ownership, or the
project integration contract.

## Decision

Harness exposes two distinct agent-facing skill surfaces:

1. **Maintainer Skill Surface** — procedures for developing, auditing and
   evolving Harness itself.
2. **Consumer Skill Surface** — procedures used by an agent applying Harness to
   a target repository.

They may be authored in the same Harness source repository, but they are
separate discovery/routing surfaces and have independent distribution
boundaries.

```text
Harness source repository
├─ Maintainer Skill Surface
│    Harness development / audit / evolution
│
└─ Consumer Skill Surface
     project bootstrap / reconciliation
     Harness project operations
     method / analysis procedures
     artifact-production procedures
```

## Repository bootstrap

A repository-level `AGENTS.md` establishes the local execution environment
before task-specific routing.

It does not enumerate or duplicate task procedures.

### Harness source repository

The Harness repository activates the **Maintainer Skill Surface** for ordinary
repository maintenance work.

The Consumer Skill Surface may also exist in the checkout for development,
fixtures, dogfooding and integration testing, but it is not thereby part of the
default maintainer routing surface.

### Target repository using Harness

A target repository activates the **Consumer Skill Surface** through its local
Harness binding/entry contract.

Harness maintainer procedures are not part of the target repository's active
skill surface.

A target repository may also expose project-local skills. Those remain
project-owned and are not copied into Harness.

## Consumer Pack

The distributable unit is a **Harness Consumer Pack**.

It contains only what a target-project agent needs to operate Harness, such as:

- Consumer/Application operation skills;
- non-owning method/analysis skills;
- artifact-production skills;
- their registries and routing metadata;
- required validators/runtime code;
- the canonical Harness contracts needed by those procedures.

It excludes Harness-maintenance-only procedures and internal development
artifacts such as audit plans.

A target project references a Consumer Pack version/revision; it does not copy
Harness skill source into project-owned skill directories as the normal
distribution mechanism.

## Physical materialization

A consumer agent must be able to read the exact Consumer Pack locally.

The target project therefore records a **pinned Harness distribution identity**.
A conceptual binding is:

```yaml
harness:
  source: github:lehater/harness
  revision: <immutable revision>
  consumer_api: v1
```

The exact filename/schema is an implementation detail until separately
specified. The architectural invariant is the immutable identity, not the
storage syntax.

The pinned distribution is materialized locally before Harness-controlled work:

```text
target repository binding
        ↓
resolve exact Harness revision/package
        ↓
materialize locally
        ↓
validate Consumer Pack compatibility
        ↓
Consumer Registry entry point
```

An agent reads skills from that local materialization, not by following remote
GitHub links at execution time.

## Transport is not the semantic contract

How the pinned Consumer Pack is obtained is deployment policy.

Valid transports may include:

- package installation;
- pinned checkout;
- Git submodule;
- content-addressed local cache;
- CI image/artifact containing the pinned distribution.

The transport must not become part of Project Model semantics.

This is consistent with the Integration Contract: project semantic integration
does not require repository-to-repository Core ownership binding, while the
tooling used to evaluate that integration must still be obtained at an explicit
version.

## Local development override

A developer working on Harness and a consumer project simultaneously may use a
local source override:

```text
workspace/
├─ harness/
└─ napms/
```

The consumer can resolve its Consumer Pack from the local Harness checkout for
development/testing.

The override:

- must be explicit;
- must not rewrite project canonical truth;
- must not silently replace the project's pinned production/CI identity;
- should report the effective Harness revision/source in diagnostics.

This provides fast dogfooding without making `../harness` a project contract.

## Stable identities

Target repositories reference stable Consumer/API/skill identities, not source
tree paths.

For example, the public identity is conceptually:

```text
skill-id: product-requirements
```

not:

```text
../harness/skills/artifacts/product-requirements/SKILL.md
```

The installed Consumer Registry maps the stable identity to the physical file
for that Harness revision.

This permits internal repository reorganization without breaking consumers.

## Routing inside the Consumer Surface

The Consumer Surface contains different route classes; they do not share one
flat selection rule.

```text
Consumer entry
   │
   ├─ operation route
   │    project-bootstrap-reconcile
   │    project-engineering-status
   │    ...
   │
   ├─ method / analysis route
   │    reliability-analysis
   │    obligation-analysis
   │    ...
   │
   └─ capability route
        Capability + knowledge_kind
              ↓
        artifact-skill registry
              ↓
        artifact-production skill
```

Capability routing remains deterministic. Method and operation routing must not
invent fake project Capabilities merely to reuse the artifact router.

## Maintainer Surface

Maintainer procedures operate on the Harness repository as their target, for
example:

- capture a Harness audit/evolution observation;
- change externally observable Harness behavior;
- evolve architecture/specifications;
- run Harness-specific review/migration procedures.

These procedures are versioned with Harness source but are not exported in the
Consumer Pack.

They may use a separate maintainer registry/entry point.

## Non-goals

This decision does not:

- require Git submodules specifically;
- require one package manager;
- make the Harness checkout a source of target-project semantic truth;
- copy Harness skills into each target repository;
- expose maintainer skills to consumer projects;
- require one universal router for maintainer and consumer work;
- turn method/analysis procedures into project Capabilities.

## Compatibility

The Consumer Pack must eventually expose an explicit compatibility identity
(`consumer_api` or equivalent) so a target project can detect an incompatible
Harness upgrade before running procedures.

A Harness internal refactor that preserves public Consumer identities and
contracts should not require changes to target repositories.

## Consequences

### Positive

- maintainer-only procedures cannot accidentally enter target-project routing;
- consumers use one pinned methodology/runtime revision;
- no copied skill trees drift between projects;
- source tree layout is not a public API;
- local Harness development can still dogfood against real projects;
- routing responsibilities become smaller and testable.

### Costs

- Harness needs a Consumer Pack boundary and compatibility/version contract;
- target projects need a small Harness distribution binding;
- local/CI bootstrap must materialize that dependency before agent use;
- consumer routing must fail clearly when the pinned distribution is absent or
  incompatible.

## Follow-up implementation work

This decision is normative; implementation remains tracked by the active
instruction/skill-routing scalability plan.

The next concrete work is:

1. define Maintainer vs Consumer registries;
2. make active skill membership machine-readable;
3. define the smallest pinned distribution/binding schema;
4. add local materialization/bootstrap behavior;
5. test local override and pinned CI behavior;
6. ensure inactive/maintainer skills are not visible through Consumer discovery.


## Concrete distribution contract

`docs/design/harness-consumer-pack-v1.md`,
`docs/design/harness-consumer-wrapper-v1.md` and
`spec/distribution/consumer-pack-v1.yaml` define the executable distribution.
`python -m harness.application.consumer_pack` materializes and validates the pack.
The standard-library `distribution/harnessw.py` closes clean-target bootstrap by
reading the pinned JSON binding, fetching the exact revision and invoking the
canonical pack materializer. Local development override remains explicit.


## Typed discovery entrypoint

`python -m harness.application.skill_router` is the common technical entrypoint for skill discovery, but
it does not collapse the three route semantics into one classifier.

```text
operation
  -> explicit surface + operation id
  -> Maintainer or Consumer Operation Registry

method
  -> explicit method id or canonical Engineering Concern ids
  -> Consumer Method Registry

artifact-production
  -> knowledge_kind
  -> Artifact Skill Registry
```

A Consumer Pack contains the same router but not the Maintainer Operation
Registry, so maintainer operations are structurally unavailable in a target
repository.

Every successful route also exposes the canonical `instruction_contracts`
required before project/tool payloads are consumed. This keeps the repository-
wide content trust boundary identical on the Maintainer and Consumer surfaces
without copying the rule into every skill.

Internal Consumer operations (for example `bootstrap-existing-project`) are not
public route entries and require explicit composition allowance from a public
operation.


## Fresh-context verification boundary

`spec/agent-routing/fresh-context-v0.yaml` records representative new-agent
entry scenarios for Maintainer source and materialized Consumer Pack
environments.

The deterministic validator proves:

- repository context selects a physically valid surface;
- typed route inputs resolve to one declared procedure;
- internal Consumer helpers are not public entries;
- Maintainer operations are unavailable from Consumer Pack;
- unrouted research producers are not accidentally discoverable as artifact
  routes.

It deliberately does **not** claim that a language model will always classify
arbitrary natural-language prompts into the correct structured route. That is a
separate behavioral-evaluation problem tracked by the Evolution Radar.


## Consumer API v1

Consumer API v1 is the only supported distribution identity. It exposes canonical
`harness.*` runtime modules and consumer skills/registries. Root module/file
facades are not distributed and no longer exist in source.

Use `spec/distribution/consumer-binding-example-v1.json` and
`spec/distribution/target-agents-fragment-v1.md`.
