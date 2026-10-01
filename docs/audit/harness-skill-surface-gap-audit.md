# Harness Skill Surface Gap Audit

Date: 2026-10-01  
Run: AUD-006  
Status: current-state audit against
`docs/design/agent-skill-surfaces-and-consumer-distribution-v0.md`.

## Question

Given the accepted separation of Harness Maintainer and Consumer skill surfaces,
what exists in the repository today, what is still ambiguous, and what must
change before a fresh agent can rely on the model without conversation history?

## Current inventory

The repository currently contains **56** `SKILL.md` files:

| Current location | Count | Current effective role |
|---|---:|---|
| `skills/agent/**` | 6 | active consumer/application procedures |
| `skills/artifacts/**` | 45 | 34 deterministic artifact producers + 11 `judgement_only` procedures |
| `skills/core/**` | 3 | retained pre-Core / inactive |
| `skills/ddd/**` | 1 | retained pre-Core / inactive |
| `skills/software-product/**` | 1 | retained pre-Core / inactive |

There is currently no explicit Maintainer skill namespace or Maintainer
registry.

### Active consumer/application procedures

The six current `skills/agent/**` procedures are:

- `bootstrap-existing-project`;
- `decision-pipeline`;
- `design-profile`;
- `human-documentation-projection`;
- `project-bootstrap-reconcile`;
- `project-engineering-status`.

They are validated for frontmatter/sections, but there is no registry that
declares their surface, route class, precedence, exclusions or composition.

### Deterministic artifact-production routes

`skills/artifact-skill-registry-v0.yaml` currently maps **34**
`knowledge_kind` values to artifact skills.

This is the strongest current routing mechanism and should be preserved:

```text
Engineering Graph CREATE
  -> production knowledge_kind
  -> artifact-skill-registry
  -> artifact-production SKILL
```

### judgement_only bucket

`skill-invariant-policy-v1.yaml` classifies **11** additional procedures as
`judgement_only`.

They are not one semantic type:

- ten are non-owning analysis/coverage procedures;
- `change-transition-design` is a conditional producer whose production
  contract is not currently registered.

Therefore `judgement_only` is a policy bucket, not a sufficient route class.

### Retained pre-Core skills

Five ordinary `SKILL.md` files remain outside the active v0 layer:

- `skills/core/agent-harness-design`;
- `skills/core/record-project-knowledge`;
- `skills/core/resolve-decision`;
- `skills/ddd/domain-model-change`;
- `skills/software-product/architecture-review`.

Some may contain reusable procedure value, but their current status is
historical/inactive. Because they remain ordinary `SKILL.md`, generic
discovery cannot distinguish them from active procedures without reading
repository prose.

## Current entry points

### Root AGENTS.md

`AGENTS.md` currently acts as several things at once:

- repository bootstrap;
- Consumer startup procedure;
- Core invariant summary;
- LLM execution policy;
- Scenario Suite change procedure;
- audit/evolution capture procedure;
- Core-extension procedure;
- source map;
- repository workflow policy.

This conflicts with the accepted target role of `AGENTS.md` as minimal
bootstrap + always-on invariants.

It also activates Consumer procedures inside the Harness source repository even
though the accepted architecture says normal Harness-repository work enters the
Maintainer Surface.

### Router implementations

Only the Capability/artifact path currently has an executable router:
`agent_router.py`.

There is no equivalent:

- Maintainer registry/router;
- Consumer operation registry/router;
- method/analysis router;
- Consumer Pack entry point.

## Current validation

### validate_agent_layer.py

The validator uses filesystem location as type information:

```text
skills/agent/**     -> agent skill shape
skills/artifacts/** -> artifact skill shape
```

It does not understand:

- Maintainer vs Consumer surface;
- operation vs method vs artifact-production route class;
- inactive/quarantined procedure status;
- routing overlap;
- distribution/export membership.

It requires every `skills/artifacts/**` procedure to contain artifact-oriented
sections such as Registration and Human Projection, including non-owning
analyses.

### skill_invariant_policy.py

This validator ensures every artifact-directory skill is classified as either
routed/enforced or `judgement_only`. It does not prove that a
`judgement_only` procedure is reachable.

### agent_router.py

This router is intentionally narrow and correct in scope: it routes actionable
Engineering Graph CREATE work by `knowledge_kind`.

It should not become the universal skill router.

## Physical distribution state

The accepted design now requires a pinned, locally materialized Consumer Pack.

No implementation exists yet for:

- a Consumer Pack manifest/export boundary;
- `consumer_api` compatibility identity;
- target-project Harness distribution binding;
- lock/pin schema;
- materialization/sync command;
- local checkout override resolution;
- validation that Maintainer skills are excluded from Consumer distribution.

Repository search finds no implemented `harness.lock`, `consumer_api`,
Maintainer registry or Consumer registry.

This is an implementation gap against the newly accepted architecture, not an
additional historical defect by itself; it is already explicit follow-up work
in the active migration plan.

## Current vs target

| Concern | Current | Target |
|---|---|---|
| Repository entry | large hybrid `AGENTS.md` | minimal environment bootstrap |
| Harness source default | mixed maintainer + consumer guidance | Maintainer Surface |
| Target project default | ad hoc access to Harness procedures | Consumer Surface |
| Active membership | inferred from folders/docs | machine-readable surface registry |
| Consumer operations | six files, no route registry | typed Consumer operation routes |
| Artifact production | deterministic 34-route registry | preserve deterministic route |
| Analysis methods | `judgement_only`, manual discovery | explicit method/analysis routes |
| Conditional producer | mixed into `judgement_only` | explicit producer applicability/route |
| Legacy skills | active-looking files | quarantined/promoted explicitly |
| Skill type | inferred from directory | declared surface + route class |
| Consumer distribution | source repository only | pinned local Consumer Pack |
| Skill public identity | mostly path-based | stable ID resolved by installed registry |
| Routing validation | shape + artifact registry | membership + overlap + reachability + type |
| Fresh-context operation | depends on prose synthesis | deterministic bootstrap and routing |

## Defects confirmed by this audit

### HARN-017 — agent operation routing

No machine-readable route/precedence contract exists for active
`skills/agent/**`; bootstrap procedures overlap.

### HARN-018 — inactive skill discovery

Inactive pre-Core skills remain exposed as ordinary `SKILL.md` files.

### HARN-019 — non-capability routing

The `judgement_only` bucket contains procedures with no explicit executable
routing contract.

### HARN-020 — skill role/type conflation

The repository derives procedure type from physical directory and validates all
artifact-directory procedures as if they were artifact producers.

## Not additional defects

The following are expected implementation work after the newly accepted design
and should not receive separate HARN IDs unless implementation later contradicts
the contract:

- no Consumer Pack yet;
- no lock/binding schema yet;
- no local cache/materializer yet;
- no Maintainer registry yet;
- no Consumer registry yet.

They are tracked by
`docs/plans/active/agent-instruction-skill-routing-scalability.md`.

## Target skill model

Every executable procedure should eventually have two independent
classifications:

```text
surface:
  maintainer | consumer

route_class:
  operation | method | artifact-production
```

A possible third lifecycle dimension is separate:

```text
status:
  active | deprecated | archived
```

These dimensions must not be inferred solely from directory names.

Examples:

```text
capture-harness-observation
  surface: maintainer
  route_class: operation

project-bootstrap-reconcile
  surface: consumer
  route_class: operation

reliability-analysis
  surface: consumer
  route_class: method

product-requirements
  surface: consumer
  route_class: artifact-production
  knowledge_kind: product-requirements
```

`change-transition-design` needs an explicit decision during migration:
either establish its production contract and route it as artifact-production,
or keep it non-routed until the contract is justified. It must not be treated as
the same kind of procedure merely because it currently shares the
`judgement_only` bucket.

## Recommended migration boundary

Do not begin by moving directories.

First make the model machine-readable:

1. declare surface + route class + active lifecycle for every executable skill;
2. validate exactly-one active surface membership;
3. validate route reachability and overlap;
4. collapse bootstrap overlap;
5. create actual Maintainer procedures for Harness maintenance;
6. create the Consumer Pack export boundary;
7. only then reorganize physical paths.

Once those invariants are enforced, directory moves become mechanical rather
than architectural.
