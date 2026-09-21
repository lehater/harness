# Research — Engineering Coverage Map

Status: research candidate.

## Problem

A project may contain many accepted engineering artifacts while still being hard to understand as a whole.

A reader needs to answer quickly:

- which engineering concerns were considered;
- which concerns apply to this project;
- which do not apply and why;
- which accepted artifact(s) cover each concern;
- which concerns are missing or blocked;
- which coverage has become stale;
- which upstream requirement/policy/decision caused an artifact to exist;
- how two otherwise very different projects compare against the same engineering lens.

This is not the same problem as Design Profile / target-state evaluation.

A Design Profile answers:

> What accepted engineering knowledge must exist for one selected Consumer?

The requested map answers:

> Across a stable catalogue of engineering concerns, what is this project's coverage state, evidence and rationale?

The map is therefore a cross-project **coverage/navigation projection**, not another semantic policy owner.

## External concepts

### ISO/IEC/IEEE 42010

ISO/IEC/IEEE 42010 distinguishes:

- stakeholders;
- concerns;
- viewpoints;
- views;
- architecture decisions and rationale.

Its useful lesson for Harness is not to force every engineering concern into one architecture document. It is to make explicit which concerns are addressed by which views/artifacts and for whom.

### arc42

arc42 uses explicit architecture sections, quality requirements, quality scenarios and checklists as recall/communication aids.

Its useful lesson is that a stable concern taxonomy can improve completeness reviews while still allowing each project to decide which concerns actually matter.

### NIST SSDF and similar frameworks

NIST SSDF demonstrates another useful pattern: a common reusable catalogue of practices can be applied across different software-development contexts, while project-specific implementation/evidence differs.

Harness should adopt that shape, not copy SSDF as a universal software checklist.

## Terminology decision

Use **Engineering Coverage Map** as the primary name.

Avoid calling the artifact simply a "Viewpoint Matrix" because ISO 42010 uses Viewpoint in a narrower architecture-description sense.

The map may expose human-facing "viewpoints", but the reusable row identity should be an **Engineering Concern**.

Conceptual hierarchy:

```
Engineering Concern Catalog
        ↓ project applicability/coverage projection
Engineering Coverage Map
        ↓ links
CanonicalArtifacts / Capabilities / Questions / evidence
```

## Key distinction: catalog vs project truth

### Concern Catalog

Harness may own a reusable catalogue of concern definitions.

Examples:

- product intent;
- domain semantics;
- application/use-case behavior;
- structural architecture;
- interface contracts;
- human interface;
- data/persistence;
- security architecture;
- security analysis;
- privacy/data governance;
- quality attributes;
- reliability/concurrency;
- operability;
- engineering policy;
- dependencies/supply chain;
- build/reproducibility;
- migration/change transition;
- verification;
- test design;
- accessibility;
- internationalization/localization;
- externally imposed obligations;
- safety;
- AI/ML-specific risk when applicable.

The catalog is a **recall taxonomy**, not proof that every project requires every concern.

### Project Coverage Map

The project-specific map resolves each catalog concern against accepted project policy/knowledge.

The map does not decide applicability by itself.

It projects existing evidence such as:

- Engineering Graph production/consumer topology;
- selected Consumers and Design Profiles;
- accepted Capability providers;
- project completeness/coverage policy;
- obligation applicability analysis;
- security/quality/etc analysis;
- explicit NOT_APPLICABLE evidence;
- unresolved Questions;
- lifecycle/current/stale information when available.

## Why this should be a projection, not Core

A concern such as "accessibility" can be covered by several semantic owners:

- Product requirements;
- Interface design;
- Quality;
- Obligation analysis;
- Verification.

Likewise "security" is not one artifact and "data" is not necessarily one Authority.

Therefore:

```
Concern != Authority
Concern != Capability
Concern != CanonicalArtifact
Concern != Consumer
```

A Concern is a reusable review/navigation lens that may map to several required capabilities or project-owned applicability rules.

Adding Concern to Core would incorrectly turn a reporting taxonomy into engineering truth.

## Leaf coverage states

At a leaf concern, avoid ambiguous "partial" statuses.

Use explicit states:

### COVERED

The concern is applicable and all project-declared required evidence/capabilities are current and accepted.

### MISSING

The concern is applicable but one or more required capabilities/evidence items have no accepted provider.

### BLOCKED

The concern is applicable but resolution is waiting on one or more unresolved Questions.

### STALE

Accepted coverage exists but lifecycle-aware evaluation proves it was accepted against an obsolete prerequisite/baseline.

This state is available only when lifecycle metadata can prove staleness.

### NOT_APPLICABLE

Accepted project evidence proves the concern does not apply to the selected project/scope.

Silence is never NOT_APPLICABLE.

### DEFERRED

The concern is known/applicable but intentionally excluded from the current selected scope with:
- explicit rationale;
- owner;
- reopening condition.

This differs from NOT_APPLICABLE.

### UNASSESSED

No accepted applicability decision exists yet.

This is the honest state for a catalogue concern that has never been evaluated.

## Parent/category states

Parent rows are summaries only.

Derived examples:

- all children COVERED/NOT_APPLICABLE -> COMPLETE;
- at least one STALE -> STALE;
- at least one BLOCKED -> BLOCKED;
- at least one MISSING -> INCOMPLETE;
- mixture of covered/deferred/unassessed -> PARTIAL.

Do not persist parent status as independent truth.

## Why UNASSESSED matters

Without UNASSESSED, a blank row is ambiguous:

- not applicable?
- forgotten?
- not yet researched?
- intentionally deferred?
- stale?
- artifact deleted?

The requested dashboard only works if absence is distinguishable from explicit non-applicability.

Therefore a blank cell should never mean "N/A".

## Coverage record

Conceptual project projection:

```yaml
version: 1
kind: harness-engineering-coverage-map
catalog: software-engineering-concerns/v1
scope:
  kind: project
  id: NAPMS

rows:
  - concern: security.architecture
    state: COVERED
    applicability:
      rationale: External OIDC and protected actions require explicit trust/admission design.
      evidence:
        - capability: engineering.architecture.security
    coverage:
      capabilities:
        - engineering.architecture.security
      artifacts:
        - SECURITY-ARCHITECTURE
      paths:
        - docs/architecture/mvp-security-architecture.yaml
    provenance:
      caused_by:
        - FIRST-MVP-REQUIREMENTS
    freshness:
      state: CURRENT

  - concern: messaging.async
    state: NOT_APPLICABLE
    applicability:
      rationale: Accepted architecture establishes no asynchronous message boundary.
      evidence:
        - capability: engineering.architecture.async-messaging-not-applicable

  - concern: accessibility.external-obligation
    state: UNASSESSED
```

The exact schema remains a prototype question.

## "Why does this artifact exist?"

The user-facing map should make two different provenance chains visible.

### Concern -> coverage

```
Security architecture
  -> applicable because protected actions + external identity boundary
  -> required CapabilityIds
  -> accepted provider artifact(s)
```

### Artifact -> reason

Reverse index:

```
SECURITY-ARCHITECTURE
  <- covers concerns:
       security.authentication
       security.authorization
       security.trust-boundary
  <- required by:
       Interface Design
       Quality Design
       Security Analysis
       Operability
       Implementation
  <- ultimately traces to:
       accepted product/security obligations
```

This reverse view is valuable as a "why is this file here?" navigator.

## File/dashboard form

Recommended generated package:

```
docs-generated/engineering-map/
├── README.md
├── coverage-map.yaml
├── coverage-map.md
├── artifacts.md
├── concerns/
│   ├── product.md
│   ├── domain.md
│   ├── architecture.md
│   ├── security.md
│   ├── data.md
│   ├── quality.md
│   ├── operability.md
│   ├── verification.md
│   └── ...
└── comparison/
    └── <optional generated comparison>.md
```

Only the catalog/project policy inputs may be canonical.

The generated dashboard files are disposable projections.

## Human matrix example

| Concern | Applicability | Coverage | Artifact / evidence | Freshness | Why / source |
|---|---|---|---|---|---|
| Product intent | applicable | ✓ COVERED | product requirements | current | project goal |
| Structural architecture | applicable | ✓ COVERED | workspace.dsl | current | implementation requires runtime boundaries |
| Async messaging | not applicable | — N/A | async N/A evidence | current | no async boundary |
| Accessibility obligation | unknown | ? UNASSESSED | — | — | no applicability analysis |
| Security architecture | applicable | ✓ COVERED | security architecture | current | external identity + protected actions |
| Data retention | deferred | ◷ DEFERRED | decision/rationale | current | reopen when retention policy introduced |
| Component design | applicable | ! STALE | component design | stale | upstream architecture changed |

Symbols are presentation only; machine states remain explicit strings.

## Comparison across projects

Because concern IDs come from the same reusable catalog, two projects can be compared without requiring identical artifact types or Authority names.

Example:

| Concern | ETL script | NAPMS |
|---|---|---|
| Product intent | COVERED | COVERED |
| Domain semantics | NOT_APPLICABLE or light project-specific coverage | COVERED |
| Human interface | NOT_APPLICABLE | applicable/incomplete |
| Security architecture | depends on secrets/trust boundary | COVERED |
| Persistence | maybe NOT_APPLICABLE | COVERED |
| Operability | logging/error/retry concerns may apply | COVERED |
| Accessibility | NOT_APPLICABLE | UNASSESSED/applicable depending product scope |
| Async messaging | maybe NOT_APPLICABLE | NOT_APPLICABLE |
| Verification | COVERED | COVERED |

The important point is not identical implementation depth.

The value is that the same concern was consciously classified rather than silently absent.

## Applicability model

A universal catalog must not contain rules such as:

> every project must have Security Architecture.

Instead, a concern entry may contain **applicability prompts**.

Example:

```yaml
- id: security.authentication
  category: security
  question: Does the system establish or consume an identity boundary?
  typical_owners:
    - PRODUCT-REQUIREMENTS
    - SECURITY-ARCHITECTURE
    - VERIFICATION-DESIGN
```

Prompts assist analysis but do not automatically decide applicability.

Where deterministic accepted project facts make applicability derivable, a project adapter may derive it.

Where judgment or external policy interpretation is required, applicability must be accepted project knowledge or remain UNASSESSED/QUESTION.

## Baseline catalog vs specialized profiles

One enormous flat catalog would become noisy.

Use:

1. **baseline software concern catalog** — broad concerns relevant to ordinary software;
2. optional specialization modules:
   - web/frontend;
   - data/ETL;
   - distributed systems;
   - regulated/privacy;
   - safety-relevant;
   - AI/ML;
   - offline/sync;
   - multi-tenant;
   - internationalized product.

A simple ETL project can still be evaluated against the same baseline catalog, with specialized modules activated only when evidence says they are relevant.

This preserves comparability without pretending every concern applies equally.

## Relationship to Engineering Graph

Engineering Graph remains the normative producer/consumer topology.

Coverage Map consumes it.

The map may derive:

- capability provider;
- owning Authority;
- Consumer dependencies;
- target status;
- blockers;
- terminal capabilities.

It must not duplicate these declarations.

Example:

```
Concern: operability.logging
    ↓ catalog/project mapping
Capabilities:
    project.operability.observability
    project.engineering-policy.error-handling
    ↓ Engineering Graph/Core
providers / paths / state
    ↓
Coverage row
```

## Relationship to Human Documentation Projection

The two research tracks are complementary.

Human Documentation Projection answers:

> How do we produce useful source-bounded documents from canonical knowledge?

Engineering Coverage Map answers:

> Which engineering concerns were considered and where is their accepted coverage?

The Coverage Map should become a natural first document/navigation page in a human documentation package.

Conceptually:

```
Engineering Coverage Map
    ↓ choose concern/artifact
Human Documentation Projection
    ↓ explanatory documents / diagrams / source links
Canonical project knowledge
```

## Relationship to ISO 42010 viewpoints

For architecture-only concerns, a catalog concern may link to a formal architecture Viewpoint.

Example:

```
concern: architecture.runtime-structure
viewpoint: C4/container
view: Structurizr Containers
artifact: docs/architecture/structurizr/workspace.dsl
```

But do not force security obligations, testing policy, licensing or build reproducibility into ISO architecture viewpoints merely for uniformity.

The Engineering Concern layer is broader.

## Relationship to existing applicability research

The existing OBLIGATION-ANALYSIS research already uses an obligation/applicability coverage matrix with states such as covered, not applicable, deferred and question.

The Coverage Map should reuse that discipline.

It must not create a second independent applicability truth.

Similarly, security/quality/data/etc analyses remain semantic owners of their own coverage decisions.

The project map aggregates references to them.

## Relationship to lifecycle/staleness research

Existing decision-lifecycle research proposes derived CURRENT/STALE behavior from prerequisite revisions/baselines.

When lifecycle-aware metadata exists, the map can expose STALE.

When it does not exist:

```
freshness: UNKNOWN
```

Do not infer freshness from Git mtime, file age or commit date.

A valid old decision is not stale merely because it is old.

## Concern catalog ownership

The reusable catalog can live in Harness because it is generic engineering recall knowledge.

However the catalog must be explicitly non-normative about applicability.

It should include:

- stable concern id;
- category;
- name;
- question/prompt;
- description;
- common evidence/capability kinds;
- common standards/lenses;
- optional specialization tags.

It must not say that every project MUST produce one artifact per row.

## Proposed first catalog categories

A v0 research catalog should at least cover:

1. problem/discovery;
2. product/requirements;
3. domain semantics;
4. application/use cases;
5. architecture/structure;
6. interfaces/API;
7. human interface/accessibility;
8. data/persistence/evidence;
9. security;
10. privacy/governance/obligations;
11. quality attributes;
12. reliability/concurrency/distributed behavior;
13. operability/configuration/logging/error handling;
14. external dependencies/supply chain;
15. build/reproducibility/release provenance;
16. engineering policy/code structure;
17. component design;
18. implementation design;
19. verification/test design;
20. change/migration/backward compatibility;
21. internationalization/localization/time semantics;
22. safety;
23. AI/ML/agentic concerns.

These categories should be decomposed into leaf concerns only where projects can classify them meaningfully.

## What makes this different from a checklist

A checklist says:

> Did you remember security?

The Coverage Map says:

```
security.authentication
  applicability: APPLICABLE
  evidence: accepted security analysis
  required capability: project.security.identity-boundary
  provider: SECURITY-ARCHITECTURE
  artifact: docs/security/...
  consumers: interface, implementation, verification
  freshness: CURRENT
  blockers: none
```

That is a navigable graph projection, not a yes/no checklist.

## Expected benefits

### Project comprehension

A new engineer can answer "what design exists and why?" without traversing the entire repository.

### Completeness review

UNASSESSED and MISSING rows are visible instead of disappearing into absent files.

### Cross-project comparison

Two projects can use the same concern IDs while mapping to completely different artifacts.

### Change impact

STALE or blocked coverage can be surfaced by concern rather than only by internal CapabilityId.

### Documentation navigation

The map becomes the index into human-readable documents, diagrams and canonical sources.

### Harness evaluation

The same map can expose whether a project has consciously classified relevant engineering concerns without claiming that the generic catalog itself proves project completeness.

## Main risk

A universal concern catalog can become a giant bureaucratic checklist.

Mitigations:

- catalog rows are prompts, not mandatory artifacts;
- NOT_APPLICABLE is first-class but requires rationale/evidence;
- concern modules can be activated conditionally;
- mapping may be many-to-many;
- project does not have to create one document per concern;
- the map is generated from existing truth wherever possible;
- only applicability decisions not derivable elsewhere need explicit project data.

## Prototype questions

Before canonicalization, test:

1. Can NAPMS and Nutrition both map to one baseline concern catalog without artificial artifacts?
2. Can a deliberately tiny ETL/script fixture classify the same catalog without excessive noise?
3. Can at least 80% of map rows be derived from existing Engineering Graph/Core/project policies rather than manually duplicated?
4. Can NOT_APPLICABLE always point to accepted evidence/rationale?
5. Can reverse artifact -> concerns navigation be generated?
6. Can missing/stale links be detected automatically?
7. Does the map improve detection of real omissions rather than simply produce many UNASSESSED rows?
8. Can the map be embedded as the first navigation page of Human Documentation Projection?

## Initial recommendation

Prototype the Engineering Coverage Map as a **derived Harness projection** with:

- a reusable baseline Engineering Concern Catalog;
- project-specific concern-to-capability/applicability mapping;
- explicit states COVERED / MISSING / BLOCKED / STALE / NOT_APPLICABLE / DEFERRED / UNASSESSED;
- artifact paths and reverse provenance;
- optional lifecycle freshness;
- Markdown + YAML outputs;
- no Core change.

Do not create a VIEWPOINT-DESIGN or DOCUMENTATION Authority.

Do not put the concern catalog into Engineering Graph as mandatory producer topology.

Do not canonicalize a huge universal catalog before it is tested against at least:
- NAPMS;
- Nutrition;
- one tiny/simple software project.

The likely end-state is a file/dashboard exactly matching the requested user experience, but backed by Harness graph semantics rather than manually maintained checkmarks.
