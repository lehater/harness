# Research — Unified Harness Model and NAPMS Migration

Status: research candidate.

## Problem

Harness and NAPMS currently contain two descendants of the same historical engineering-knowledge model.

The separate Harness repository is intended to own universal semantics, but NAPMS still owns and executes a local adaptation:

- `docs/harness-core.yaml`;
- `tools/check_harness_vertical.py`;
- `tools/prepare_authority_execution.py`;
- `tools/test_harness_vertical.py`;
- related context/package utilities.

NAPMS explicitly states that it does not import, pin, or execute `lehater/harness`.

Therefore model drift is architectural, not accidental: both repositories can independently change the same semantics.

## Root cause

Previous synchronization work copied decisions between the two repositories without establishing one implementation owner.

The result is a fork:

```
historical NAPMS Harness
        |
        +--> NAPMS local evaluator/model
        |
        +--> standalone lehater/harness
```

Manual semantic synchronization cannot make these implementations converge permanently.

The only stable correction is:

```
lehater/harness = sole owner of universal Harness semantics/runtime
consumer repo   = project-owned data/projection/policy only
consumer CI     = pinned immutable Harness version
```

## Semantic union

### Already common or effectively common

Both models support:

- Authority as engineering-decision ownership boundary;
- boundary evidence: semantic cohesion, independent change, public contract;
- project canonical artifacts assigned to Authorities;
- public CapabilityIds;
- capability producer ownership;
- consumer requirements;
- dependency DAG semantics;
- Questions addressed to semantic owner;
- blocking existing artifacts;
- project-owned canonical graph as semantic/routing truth;
- consumers as terminal knowledge requirements rather than workflow stages.

These should remain in the unified model.

### Standalone-Harness strengths to preserve

1. Minimal Core entities:
   - Authority;
   - CanonicalArtifact;
   - CapabilityId;
   - Question.

2. `Question.blocks_capabilities` for pre-provider gaps.

3. Engineering Graph with per-capability production prerequisites.

4. Recursive consumer closure and derived Design Profile.

5. Target states:
   - CREATE;
   - PENDING;
   - WAIT;
   - COMPLETE / aggregate READY/BLOCKED.

6. Generic `knowledge_kind -> artifact skill` routing.

7. Generic agent workbench and semantic acceptance loop.

8. Project-independent artifact skills:
   - Engineering Policy;
   - Component Design;
   - Test Design;
   - frontend User Journey / Human Interface;
   - Security/Quality/Operability/etc.

9. Canonical integration contract and pinned distribution model.

10. Managed workspace as optional project choice.

### NAPMS-local strengths to preserve and promote

These are general engineering-graph invariants, not NAPMS business semantics.

#### 1. Exact project graph coverage

Every selected canonical project node has exactly one Authority binding.

This prevents unowned canonical knowledge.

For partial/scoped projections, exactness must apply to the explicitly selected projection scope rather than necessarily the entire repository.

#### 2. Authority dependency consistency

NAPMS derives actual cross-Authority dependencies from canonical artifact dependency edges and requires the declared Authority input contract to match them exactly.

This gives two important errors:

- **hidden dependency**: canonical graph depends on an upstream Authority not declared in the capability contract;
- **phantom input**: capability contract declares an upstream Authority not represented by the canonical graph.

This is stronger than standalone Harness today.

The unified model should preserve this as an optional/required adapter validation when a project supplies an authoritative canonical artifact graph.

#### 3. Public capability liveness

Every public capability must be:

- consumed by another production/consumer; or
- explicitly declared terminal with a reason.

This catches accidental public outputs and stale capability declarations.

This should be part of Engineering Graph validation, with explicit terminal outputs only where a project truly needs them.

#### 4. Explicit root semantics

NAPMS validates declared root Authorities against project dependency reality.

Standalone Harness derives root CREATE from capability prerequisites and does not need a separate universal root entity.

Unified interpretation:

- root-ness should normally be derived from capability-production prerequisites;
- adapter validation may verify project-declared root metadata when the project chooses to persist it;
- do not create a new Core RootAuthority entity.

#### 5. Authority execution context

NAPMS can derive a bounded execution context for one Authority:

- exact accepted upstream provider artifacts;
- same-Authority supporting closure;
- Authority-owned current artifacts;
- allowed canonical read paths;
- allowed canonical write paths;
- public outputs;
- downstream consumers;
- blockers/design gaps.

This is a strong generic Harness capability and should be promoted to standalone Harness.

It materially prevents agents from reading arbitrary downstream design or writing across ownership boundaries.

#### 6. Write-boundary enforcement

NAPMS verifies changed canonical paths are owned by the selected Authority and prevents artifact production when the Authority is blocked.

This should become generic Harness agent-layer behavior.

#### 7. Undeclared canonical-reference detection

NAPMS checks whether an owned canonical artifact literally references canonical paths outside the Authority execution context.

The exact literal-path technique is project-format-specific and should not become Core semantics.

But the general invariant is useful:
- project adapters may provide a canonical-reference extractor;
- Harness can validate extracted references against allowed execution context.

#### 8. NOT_APPLICABLE with evidence

NAPMS consumer contracts can satisfy a requirement through explicit project-owned NOT_APPLICABLE evidence.

Standalone Harness already supports applicability as project policy in concept but does not provide one unified generic representation in Engineering Graph evaluation.

The unified model should support an applicability/evidence hook without making generic engineering concerns mandatory.

### NAPMS elements that must NOT be promoted as universal semantics

- NAPMS-specific Authority names;
- `APPLICATION-JOURNEY-DESIGN` as a universal Authority;
- specific CapabilityIds such as `engineering.interface.http-contract`;
- specific root Authorities;
- specific file layouts;
- exact NAPMS canonical graph node kinds;
- implementation-package section names;
- literal-path reference scanning as a mandatory universal algorithm;
- mandatory coverage of every repository artifact when a consumer intentionally uses a scoped projection.

## Unified model architecture

### Layer 1 — Core realization

Owned only by Harness:

```
Authority
CanonicalArtifact
CapabilityId
Question
artifact dependency
artifact/capability blocking
```

Core remains small and does not absorb project graph policy.

### Layer 2 — Engineering Graph policy

Owned only by Harness runtime/schema.

It declares:

```yaml
authorities:
  - id
    responsibility
    boundary
    produces:
      - capability
        knowledge_kind
        requires: [...]

consumers:
  - id
    purpose
    requires: [...]
```

Add generic validation for:

- unique producer Authority;
- capability DAG;
- public capability liveness / explicit terminal output;
- no duplicate/conflicting subject scope;
- Authority boundary evidence;
- consumer closure.

Do not duplicate per-Authority `contracts` as a second topology if they can be derived from `produces[*].requires`.

### Layer 3 — Project graph adapter

A consumer repository may own a canonical artifact graph.

Its adapter/projection declares only:

- artifact -> Authority binding;
- artifact -> provided CapabilityIds;
- Questions;
- project-specific applicability evidence;
- optional adapter policy for selected scope.

Harness adapter derives Core realization and verifies consistency between:

```
project artifact dependencies
        vs
Engineering Graph capability prerequisites
```

This is where hidden/phantom dependency detection belongs.

### Layer 4 — Authority execution context

New generic Harness agent-layer projection.

Input:

- Engineering Graph;
- Core realization;
- project artifact graph/projection metadata;
- selected Authority.

Output:

- status ROOT/READY/BLOCKED (or equivalent derived state);
- accepted input capability providers;
- same-Authority support closure;
- owned canonical artifacts;
- public outputs;
- downstream consumers;
- allowed canonical reads/writes;
- unresolved gaps/Questions.

This is derived runtime context, never canonical project truth.

### Layer 5 — Consumer target state

Use existing Harness recursive consumer closure:

```
Engineering Graph + Core realization + selected Consumer
    -> CREATE / PENDING / WAIT / COMPLETE
```

Backend, frontend, import, migration, verification or any future consumer are separate project declarations.

### Layer 6 — Agent routing

Use the canonical Harness registry and skills only.

Consumer repositories do not fork artifact production methodology.

## One-source-of-truth rule

After migration:

### Harness repository owns

- Core semantics;
- Engineering Graph schema/evaluator;
- project-graph adapter semantics;
- target-state evaluator;
- Authority execution-context builder;
- write-boundary checks;
- generic adapter consistency validation;
- generic skills/routing;
- acceptance tests proving all the above.

### NAPMS owns

- `docs/canonical-graph.yaml`;
- project canonical artifacts;
- project-specific Authority assignments if needed;
- project-specific capability bindings;
- project Consumers;
- project-specific applicability/coverage rules;
- project Questions;
- a tiny adapter/projection configuration;
- the pinned Harness SHA/version in CI.

NAPMS must no longer own another Harness evaluator.

## Required Harness changes before NAPMS migration

### H1 — Capability liveness

Extend Engineering Graph:

- reject produced public capability that has no production/consumer requirement;
- allow explicit terminal capability/output declaration with reason;
- acceptance tests for unconsumed/redundant terminal outputs.

### H2 — Project graph consistency validator

Extend canonical-graph adapter or add generic integration validator that can compare:

- artifact-level cross-Authority dependency topology;
- capability-production prerequisites.

Detect:
- unbound selected canonical artifact;
- hidden Authority dependency;
- phantom Authority dependency;
- capability owner mismatch;
- adapter dependency cycles.

Important nuance:
artifact dependencies can be finer-grained than capability prerequisites. Validation should compare Authority/capability frontiers, not require one artifact edge per capability edge.

### H3 — Authority execution context

Promote generic version of NAPMS `prepare_authority_execution.py` to Harness.

It should derive:
- exact input providers;
- same-Authority support closure;
- owned artifacts;
- public outputs;
- downstream consumers;
- blockers;
- read/write boundary.

It must use canonical Harness target/blocking semantics, including `blocks_capabilities`.

### H4 — Generic write-set validation

Given Authority execution context and changed canonical paths, reject cross-Authority writes.

Keep Git mechanics outside Harness semantics.

### H5 — Optional reference-leak adapter hook

Define a project adapter contract for extracting semantic/canonical references from artifacts.

Do not put prose/path scanning in Core.

NAPMS may initially retain its path-reference extractor as a project adapter helper, but the allowed-reference semantics come from Harness.

### H6 — Applicability/evidence integration

Represent explicit NOT_APPLICABLE/evidence without creating phantom capabilities.

Options to test:

A. evidence CapabilityId produced by owning Authority and required conditionally;
B. project adapter resolves a requirement as NOT_APPLICABLE with accepted evidence reference;
C. separate applicability policy projection above Engineering Graph.

Research preference:
keep Engineering Graph topology positive and stable; model NOT_APPLICABLE as project-owned applicability policy consumed when deriving a selected consumer profile. Do not encode absence as a fake producer.

### H7 — Unified integration fixture using real NAPMS shape

Add Harness acceptance fixture based on NAPMS topology (genericized names if appropriate) proving:

- exact project-graph projection;
- hidden dependency rejection;
- phantom dependency rejection;
- public capability liveness;
- Authority context;
- Question blocking;
- `blocks_capabilities`;
- consumer target state.

This fixture becomes the regression barrier preventing future drift.

## NAPMS migration plan

### N1 — Pin Harness

NAPMS CI checks out an immutable Harness commit exactly like Nutrition.

No moving branch.

### N2 — Replace local evaluator

Delete/retire semantic ownership from:

- `tools/check_harness_vertical.py`;
- local target/completeness evaluator portions;
- duplicated Question/blocking evaluation.

Project-specific wrappers may remain only if they call the pinned Harness and add NAPMS-specific assertions.

### N3 — Convert `docs/harness-core.yaml` to thin project projection

Remove duplicated universal semantics where possible.

Retain only project metadata that Harness cannot know:

- Authority assignment;
- capability bindings;
- Consumers;
- applicability;
- Questions;
- adapter scope.

Prefer Engineering Graph producer topology in one project file rather than duplicated `contracts` and `bindings` topologies.

### N4 — Normalize Authority catalog

Do not blindly rename all NAPMS Authorities.

Map semantically:

- `APPLICATION-JOURNEY-DESIGN` -> canonical reusable APPLICATION-DESIGN Authority pattern if its boundary is only journey/application orchestration;
- `SECURITY-ARCHITECTURE-DESIGN` -> canonical SECURITY-ARCHITECTURE naming if no project-specific distinction exists;
- add ENGINEERING-POLICY, COMPONENT-DESIGN, TEST-DESIGN only when NAPMS has/needs corresponding accepted capabilities;
- preserve truly project-specific Authority boundaries when they pass atomicity tests.

Names are secondary; ownership semantics are primary.

### N5 — Split backend and frontend consumers

Current NAPMS `IMPLEMENTATION` is backend-oriented.

Create at least:
- BACKEND-IMPLEMENTATION;
- FRONTEND-IMPLEMENTATION.

Frontend consumer should expose current design gaps instead of declaring whole application complete.

### N6 — Migrate Authority context command

`make authority-context` should call pinned Harness generic authority-context runtime plus NAPMS adapter configuration.

Delete the duplicate algorithm after parity is proven.

### N7 — Preserve project-only safety checks

Keep NAPMS checks that are genuinely project-specific:
- canonical graph format/invariants;
- OpenAPI consistency;
- persistence model validation;
- project-generated views;
- project-specific semantic coverage.

Do not move these into Harness unless independently reusable evidence appears.

### N8 — Differential migration test

Before deleting local evaluator, run both old and new evaluators against the same NAPMS main state and mutation fixtures.

Require parity or explicitly explain every intentional difference.

At minimum test:
- baseline COMPLETE/satisfied backend;
- missing interface capability;
- missing security capability;
- blocked architecture;
- pre-provider blocked capability;
- hidden dependency;
- phantom input;
- dead public output;
- explicit terminal output;
- Authority execution context read/write set;
- frontend blocked state.

Only after this parity suite passes may the local evaluator be removed.

### N9 — CI anti-drift invariant

After migration, NAPMS CI must:
- checkout pinned Harness;
- run Harness integration validation;
- run NAPMS project checks;
- contain no independent implementation of Harness evaluator semantics.

A lightweight repository test should fail if retired evaluator modules reappear or if CI stops pinning Harness immutably.

## Versioning and update workflow

Harness changes must follow:

1. consumer exposes a missing general capability;
2. experiment may occur on consumer branch;
3. generalized behavior is implemented and acceptance-tested in Harness;
4. Harness change merges;
5. consumer updates immutable pin in its own PR;
6. consumer integration tests prove compatibility;
7. temporary consumer experiment is removed.

Never leave generalized evaluator logic in the consumer after promotion.

This converts synchronization from semantic copying into ordinary dependency version updates.

## Migration order

Do not migrate NAPMS directly onto current Harness yet.

Correct order:

1. canonicalize H1-H7 in Harness;
2. prove them against Harness fixtures and Nutrition compatibility;
3. create NAPMS migration branch;
4. add pinned Harness;
5. run differential parity suite;
6. replace local evaluator/context runtime;
7. split backend/frontend consumer declarations;
8. delete duplicate universal logic;
9. merge only after NAPMS project CI and Harness integration are green.

## Expected final topology

```
                lehater/harness
     universal schema + evaluator + skills
                   |
          immutable version pin
                   |
                   v
                NAPMS
  canonical graph + project artifacts + projection
                   |
                   +-- backend consumer
                   +-- frontend consumer
                   +-- project checks
```

Nutrition and NAPMS then use the same evaluator semantics. They may have different project graphs and projections, but cannot fork Harness behavior.

## Decision

Build a unified Harness model by taking the semantic union, not by choosing one repository's current implementation wholesale.

Promote the proven general NAPMS invariants into standalone Harness first, then migrate NAPMS to the pinned runtime and remove its duplicate evaluator.

This is the only approach that both preserves the stronger NAPMS guarantees and eliminates future model drift.
