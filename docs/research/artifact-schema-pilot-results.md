# Artifact schema pilot results

Status: research conclusion after Harness, Nutrition Management, NAPMS and greenfield
experiments. Nothing in this document is canonical and nothing is proposed for main
without a separate promotion decision.

## What was tested

The experiment asked four separate questions:

1. What is the correct unit for a reusable canonical-knowledge storage schema?
2. Can Harness reuse its existing managed-knowledge envelope rather than inventing
   another storage format?
3. Can schema validation remain outside Core while existing Consumer evaluation is
   unchanged?
4. Does every recurring artifact family actually deserve a reusable schema?

Pilot branches:

- Harness: `research/engineering-knowledge-projections`;
- Nutrition Management: `research/representation-contract-v0`;
- NAPMS: `research/representation-contract-v0`.

Research PRs remain Draft.

## Falsified attachment points

### Authority -> schema

Rejected.

One Authority can own several artifact shapes. NAPMS SYSTEM-ARCHITECTURE owns
Structurizr structural topology, YAML architecture rules and YAML module contracts.

### CapabilityId -> schema

Rejected as a 1:1 rule.

CapabilityId identifies public accepted knowledge. One artifact can provide several
capabilities, and one broad capability can have several providers inside one
Authority. Representation identity is therefore not Capability identity.

### knowledge_kind / Artifact Skill -> schema

Rejected as a 1:1 rule.

`interface-contract` can naturally produce a CLI contract or a standard-native
OpenAPI artifact. `system-architecture` can produce different structural/rule
artifacts. A Skill is a production procedure, not a storage type.

### one universal engineering schema

Rejected.

Architecture, requirements, domain, verification and implementation knowledge have
materially different semantic structures. A generic bag of sections/claims would
only move prose into YAML.

## Surviving unit

The reusable formalization unit is an **Artifact Schema/Profile**: one stable
semantic materialization shape that a concrete CanonicalArtifact may instantiate.

It is below Skill and independent of Authority/Capability identity:

```text
Authority
  -> Production Contract
      -> CapabilityId
          -> knowledge_kind
              -> Artifact Skill
                  -> Artifact Schema/Profile (when justified)
                      -> CanonicalArtifact
                          -> provides CapabilityId(s)
```

One Skill may support several profiles. One profile may be instantiated by many
projects. One artifact may provide several capabilities.

A project-native canonical artifact does not need to be migrated merely so a
reusable profile exists.

## Storage-format result

For Harness-native typed profiles, the existing envelope is sufficient:

```yaml
version: 1
kind: harness-knowledge-artifact
artifact: <core-artifact-id>
schema: <artifact-profile-id/version>
title: <human title>
content:
  ...
```

Research-only candidate metadata was added outside the semantic content, but the
actual storage envelope was unchanged.

The experiment plugged three additional schema validators into the existing
`workspace.py` schema registry and validated real candidates through the normal
`workspace.py validate-artifact` command.

No Core or Engineering Graph change was needed.

### Native-standard exception

When an established standard naturally owns the contract, the native file remains
canonical:

- OpenAPI for an HTTP contract;
- Structurizr DSL when the C4 structural model itself is canonical.

Do not copy those semantics into `.harness/knowledge/**`. The profile association
belongs to the agent/project adapter layer.

### Project-native exception

Narrative or project-specific canonical artifacts may remain project-native when no
reusable machine profile has demonstrated consumer value. Their semantic acceptance
still follows the Artifact Skill/output contract.

Therefore Harness has one reusable **managed envelope**, not one mandatory physical
format for every canonical artifact.

## Real materializations

### Product Requirements

A common candidate profile was losslessly materialized from:

- Nutrition `docs/requirements/product-requirements.md`;
- NAPMS `docs/requirements/first-mvp-policy-export.yaml`.

A first version lost NAPMS stakeholder/evidence semantics. The schema was revised to
carry structured evidence/provenance. This demonstrates why source comparison is
still semantic acceptance rather than structural validation.

Result: cross-project structural fit **PASS**.

Promotion result: **HOLD**.

Reason: current consumers do not demonstrate a need for field-level deterministic
processing of generic Product Requirements. The candidate still consists largely of
classified narrative statements. Replacing accepted project-native requirements only
for uniformity would add migration cost without a proven consumer failure.

### Implementation Design

A common candidate profile was losslessly materialized from:

- Nutrition `docs/redesign/implementation-design.md`;
- NAPMS `docs/plans/first-mvp-implementation-readiness.yaml`.

Authorization semantics had to be made explicit after source comparison.

Result: cross-project structural fit **PASS**.

Promotion result: **REJECT AS CURRENT GENERIC SCHEMA**.

Reason: the candidate's `design_sections[].decisions[]` is effectively a typed
document outline containing arbitrary prose. It does not provide enough stable
machine semantics to justify replacing project-native artifacts. More specific
implementation profiles may become justified by future deterministic consumers.

### CLI Contract

A profile was materialized from:

- Nutrition `docs/interface/cli-contract.md`;
- greenfield CSV Deduplicator `artifacts/cli-contract.md`.

It captures command syntax, argument contracts, success semantics, failure classes,
exit status when defined, representation rules and adapter boundaries.

Result: repeated structural fit **PASS**.

Promotion result: **HOLD / strongest new candidate**.

Reason: semantic fields are substantially more stable than Implementation Design,
but no current consumer has yet failed because the CLI contract is Markdown. Promote
only when deterministic implementation/verification/documentation consumption
benefits from this structure.

### Standard-native HTTP contract

NAPMS already uses OpenAPI 3.1 plus a project validator.

Result: **PASS as native profile; no Harness schema should duplicate it**.

## Managed-workspace compatibility test

The research branch extended only the workspace schema registry. Pilot CI then used
the ordinary command:

```text
workspace.py validate-artifact <candidate>
```

Observed:

- Nutrition Product Requirements candidate -> PASS;
- Nutrition Implementation Design candidate -> PASS;
- Nutrition CLI Contract candidate -> PASS;
- NAPMS Product Requirements candidate -> PASS;
- NAPMS Implementation Design candidate -> PASS;
- greenfield CLI Contract candidate -> PASS;
- deliberately invalid Product Requirements candidate -> REJECTED;
- Nutrition Engineering Graph/Core/Consumer evaluation remained green;
- NAPMS canonical graph/responsibility/design checks remained green;
- Harness Core/workspace/greenfield checks remained green.

This proves structural schemas can be added at the managed-workspace/agent layer
without extending Core.

## Compound artifact finding

NAPMS `docs/discovery/resource-catalogue.yaml` contains problem evidence, a
problem-space journey and capability-discovery evidence in one Discovery-owned
canonical file.

This means Harness must not assume that every existing project-native file maps to a
small reusable schema. A project can have a coherent compound artifact inside one
Authority.

Possible future options are:

- leave it project-native;
- define a reusable compound profile if repeated evidence appears;
- semantically split it only if independent-change/ownership analysis justifies the
  split.

Do not split files merely to satisfy a schema catalogue.

## Schema promotion gate

A new reusable Artifact Schema/Profile should be promoted only when all are true:

1. **Repeated shape** — independent projects or a recognized standard show the same
   semantic materialization shape.
2. **Stable semantics** — fields mean the same engineering thing across projects.
3. **Machine value** — a real consumer benefits from deterministic field-level
   access, validation or rendering.
4. **No semantic inflation** — required fields do not force decisions absent from
   the owning Authority's current contract.
5. **No native-standard duplication** — OpenAPI/Structurizr/etc. remain native where
   they already own the contract.
6. **Lossless pilots** — source comparison finds neither missing nor invented
   semantics.
7. **Independent validation** — malformed representation is rejected before
   semantic acceptance.
8. **Core independence** — schema support does not change ownership, Capability
   resolution or Consumer topology.

“Can be represented as YAML” is explicitly not sufficient.

## Current model

The evidence supports keeping the existing Core model unchanged and clarifying the
agent/materialization layer as:

```text
Engineering Graph
  CapabilityId + optional knowledge_kind
            |
            v
       Artifact Skill
            |
            +--> Harness-managed profile
            |      harness-knowledge-artifact + schema
            |
            +--> standard-native profile
            |      OpenAPI / Structurizr / ...
            |
            +--> project-native artifact
                   skill/project output contract
            |
            v
      semantic acceptance
            |
            v
      Core CanonicalArtifact.provides
```

Generated human/visual material remains downstream projection and never repairs
missing semantics.

## Priority findings

- **P0:** none.
- **P1:** do not introduce `RepresentationContract`, `ArtifactType`, or schema
  identity into Core; pilots do not require them.
- **P1:** do not require one schema for every Capability, Authority, Skill or
  canonical file.
- **P1:** schema promotion needs demonstrated machine-consumer value, not merely
  cross-project encodability.
- **P2:** the existing workspace registry is currently hard-coded and supports only
  two canonical schemas in main. If more profiles are eventually promoted, registry
  modularization becomes an agent/workspace implementation concern.
- **P2:** standard-native profile association needs a small adapter/skill convention
  if deterministic generic projection starts consuming those artifacts.
- **P3:** legacy project-native prose may remain canonical indefinitely when humans/
  agents are its legitimate consumers and no deterministic parser is claimed.

## Research conclusion

The original question “what format do we store canonical knowledge in?” does not
have one file-format answer.

The tested answer is:

> Canonicality is defined by Authority ownership and semantic acceptance.
> Reusable storage structure is standardized per proven Artifact Schema/Profile.
> Harness-managed profiles reuse the existing knowledge-artifact envelope; recognized
> standards stay native; unproven/project-specific shapes stay project-native.

No new schema from this research is ready for canonical promotion yet.
