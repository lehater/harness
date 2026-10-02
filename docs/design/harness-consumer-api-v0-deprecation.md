# ADR-CONSUMER-API-V0-DEPRECATION — v1-first Consumer adoption

Status: accepted distribution decision.

## Decision

Consumer API v0 transitions from SUPPORTED to DEPRECATED. Consumer API v1
remains SUPPORTED and is the required path for every new Consumer integration.
This decision is referenced by `apis.v0.decision` in the lifecycle contract.
It changes distribution policy, not Core/domain semantics or runtime dispatch.

## Operational obligations

Latest source still accepts and materializes `consumer_api: v0`. The wrapper
still supports v0, v0 Pack compatibility remains tested, and bugs breaking
its documented compatibility remain defects. Existing v0 consumers should
migrate to v1. New Consumer integrations MUST use v1.

Deprecation does not mean removal, best-effort support, silent fallback or
automatic EOL. No calendar EOL date is assigned. EOL and removal each require
separate explicit distribution decisions. All root/dotted facades, both Core
export sets, the non-installed execution bridge and provider tooling remain.

## Adoption and compatibility

Canonical new onboarding uses the v1 binding example, target AGENTS fragment,
`python .harness/harnessw.py sync` and, from the printed Pack directory,
`python -m harness.application.skill_router ...`. The lifecycle contract owns
a bounded onboarding surface list and labels v0-specific compatibility surfaces
separately. Its validator rejects legacy command recommendations in owned
onboarding code blocks and validates the canonical v1 binding and bootstrap.
Extend that list when adding a first-party onboarding surface.

The implicit Consumer Pack CLI/programmatic default remains v0. Published v1
Pack documentation explicitly records that behavior; changing an omitted
argument would break existing callers. Recommended selection for new callers
is explicit v1, independently of that compatibility default.

First-party CI frontier checks, README/current command examples and active
Consumer skill commands use canonical modules. Pack/wrapper validator harness
imports use canonical implementation identities; their v0 invocation/import
probes remain compatibility subjects. Registry-driven facade probes and old
wrapper execution remain required evidence, not incidental dependencies.
Historical evidence is preserved.

## Core alias semantics

`physically_present_in` records distribution presence, while
`public_consumer_apis` records public identity membership. The source-tree
execution bridge is physically required by v1 non-installed execution but is
not itself a public Core identity. Its Core re-exports and the canonical package
initializer exports are physically present in both APIs; `from harness import
...` is public compatibility only for v0. V1 Core access is
`harness.project_model.core`. No exports are removed.

## Evidence and follow-up

Reuse HA-A18 (A18-F03/F05/F06), TD-DIST-001/002, TL0/TL1 policy/mutation checks
and existing TL2 Pack/wrapper acceptance with O1 oracles. No new workflow, Core
entity, scenario DSL, package model or provider behavior is introduced.

EOL readiness is not claimed. Existing external v0 consumers need migration
assessment; intentional first-party v0 compatibility users need a coordinated
EOL test/registry/wrapper change under a separate decision. Core export policy,
execution bridge/package model and provider distribution remain separate
questions and are not authorized for redesign by this decision.
