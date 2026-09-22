# Research — Frontend presentation provider boundary v1

Status: validated research candidate; implementation acceptance is CI-backed.

## Problem

A frontend can be semantically complete through Human Interface, Presentation System and Screen/View Design yet still leave one material implementation gap: how provider-neutral presentation patterns are realized by a selected UI library/template.

Without an explicit realization boundary, either:

1. feature screens import provider APIs directly and product composition becomes coupled to one library; or
2. a project builds a second generic UI framework that mirrors the provider API.

The required boundary is smaller than either option.

## Decision

Use the existing frontend knowledge chain and add a provider realization contract under Component Design.

```text
Product / Domain / Application
        ↓
HTTP / machine-interface contract
        ↓
Frontend transport/query-command boundary
        ↓
Screen runtime model/controller
        ↓
Human Interface + Screen/View semantics
        ↓
Presentation System patterns
        ↓
Component Design: presentation-provider realization contract
        ↓
Provider adapters + provider theme/template composition
        ↓
Rendered UI
```

This is a dependency graph. Several nodes are design-time knowledge rather than runtime layers.

## Responsibility boundaries

### HTTP / machine-interface contract

Owns stable external operations, request/response schemas and outcomes. It does not own screen composition.

### Frontend transport/query-command boundary

Owns transport calls, DTO/error translation and screen-oriented query/command invocation. It may map HTTP projections into frontend semantic values.

A separate generic CQRS framework is not required. Query/command naming describes responsibility, not mandatory infrastructure.

### Screen runtime model/controller

Owns browser runtime orchestration for one screen: loading server state, mapping it to the semantic Screen Model, invoking accepted commands, refreshing authoritative state and retaining ephemeral local form/disclosure state.

It does not become product/domain authority.

### Human Interface and Screen/View semantics

Owns user-visible meaning: purpose, navigation, actions, state distinctions, capability allow/exclude policy, Screen Model meaning, and operation bindings.

This layer is provider-neutral.

### Presentation System

Owns shared presentation vocabulary and reusable task patterns such as CATALOGUE, DETAIL, DATA-TABLE, EDITOR and STATUS.

A pattern contract describes material anatomy/roles only. It is not a copy of a provider component API.

### Presentation-provider realization contract

Owner: Component Design.

Owns the replaceable realization seam:

- selected provider and version/ref;
- deny-by-default provider feature policy;
- required presentation patterns for the selected scope;
- project adapter owner for each required pattern;
- concrete provider primitives used by that adapter.

It does not own or re-declare product actions, routes, permissions, fields or screen states.

### Provider adapters

Own provider-specific composition and defaults. They translate accepted project patterns into provider primitives and explicitly suppress provider/template features that lack semantic authorization.

Adapters should be coarse enough to preserve a provider seam and small enough not to become a second UI framework.

### Provider theme/template

Owns provider-specific styling and shell composition. Theme APIs, component props and copied template internals are implementation details unless an upstream Presentation System invariant explicitly constrains the result.

## Deny-by-default rule

Provider capability is never evidence of product capability.

For each screen:

```text
allowed Screen capability
    ↓
authorized pattern feature binding
    ↓
provider adapter realization

provider/template optional feature
    ↛ no Screen capability → omitted/disabled
```

Search, filtering, sorting, pagination, destructive actions, bulk operations and routes are common examples.

Harness already validates allowed/excluded Screen capabilities and pattern feature bindings. The provider realization check added by this research verifies that the selected provider covers required patterns while keeping feature enablement upstream.

## What is not a separate layer

Do not create mandatory runtime objects for every design-time concept.

- Screen semantics is canonical design knowledge, not necessarily a runtime object.
- Presentation Pattern Contract is a small stable project vocabulary, not a component framework.
- Provider mapping is Component Design data plus adapter ownership, not another application service.
- Theme is provider-specific realization.
- A template is reference/source composition, not a product contract.

## Frontend state

Use three ownership classes:

1. server state — authoritative API projections and mutation outcomes;
2. screen/application state — derived Screen Model and request lifecycle;
3. local UI state — input drafts, disclosure/open state and other ephemeral interaction state.

Introduce a cache/query library only when repeated invalidation, deduplication, background refresh or shared server-state consumption justifies it. Do not create global client state by default.

## BFF decision

A BFF is not required merely because a frontend Screen Model exists.

Direct HTTP projection + frontend mapping is sufficient when:

- the API projection already contains the facts needed by the screen;
- one browser request or a small number of independent requests is acceptable;
- no server-side credential/policy composition is required;
- frontend mapping is deterministic presentation/application shaping.

A server-side BFF becomes justified when a screen needs one or more of:

- aggregation across multiple backend services with material latency/chattiness;
- server-side authorization/credential mediation;
- frontend-specific orchestration that must remain trusted server behavior;
- edge/server caching or shaping that materially changes operational behavior;
- a stable frontend API insulating the client from independently evolving downstream APIs.

A BFF returns network projections. A Screen Model/Presenter remains a frontend semantic/runtime model. They are not substitutes for each other.

## Verification

Use separate evidence for separate responsibilities:

- contract: OpenAPI operation ids and outcomes exist;
- semantic: Screen Model sources, states, capabilities and exclusions close;
- provider: every required presentation pattern has a deny-by-default adapter mapping;
- component: feature code depends on the provider-neutral presentation seam rather than vendor imports;
- rendered: representative states satisfy accepted hierarchy, geometry, responsive, accessibility and reference-conformance invariants;
- journey/E2E: user-visible behavior remains correct through real routing/API boundaries.

Visual snapshots are evidence only for accepted rendered invariants; they do not authorize new product behavior.

## Migration rule

Migrate by vertical slices:

1. select one semantically closed representative screen;
2. add provider/theme/shell and pattern adapter only for that slice;
3. keep legacy presentation code for non-migrated screens;
4. validate semantic/provider/rendered closure;
5. migrate remaining patterns/screens based on demonstrated reuse;
6. delete legacy design-system/tooling only when no migrated code depends on it.

This avoids both a big-bang rewrite and long-term dual-framework ownership.

## Rejected alternatives

### Provider API directly in every screen

Simple initially, but provider replacement requires changing feature composition throughout the application and makes provider defaults difficult to police.

### Generic universal UI abstraction

Mirrors the vendor API, increases surface area, hides useful provider capabilities and creates a second framework.

### Template as semantic authority

A template commonly includes optional search/filter/sort/pagination/actions. Treating those as product semantics violates upstream ownership and deny-by-default.

### BFF by default

Adds a server deployment/runtime boundary without solving a demonstrated aggregation, trust or operational problem.

## Minimal Harness implication

No new Authority, Core entity family or frontend workflow is required.

The existing Screen/View evaluator remains the semantic authority. An optional provider contract can now be supplied to verify:

- provider identity and immutable version/ref;
- default feature policy is deny;
- required presentation patterns are mapped;
- each mapping identifies an adapter and provider primitives;
- provider mappings do not independently enable product features.

This is sufficient to close the provider-neutral Screen semantics → replaceable provider realization gap without embedding MUI or any other vendor into Harness semantics.
