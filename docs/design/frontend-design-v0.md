# Frontend design v0

Status: canonical active design

Harness supports user-facing/frontend engineering through the existing engineering-knowledge model. Frontend work does not introduce a separate workflow or Core entity family.

## Boundary

Frontend completeness is consumer-specific.

A frontend implementation consumer may require this knowledge closure:

```
Product Requirements
      ↓
Domain / Use-case Design
      ↓
User Journey Design
      ↓
Human Interface Design ─────┐
      ↓                    │
Presentation System Design │
      ↓                    │
Screen / View Design ◀─────┘
      ↓
Frontend System Architecture
      ↓
Component Design + Verification Design
      ↓
Test Design
      ↓
Implementation Design
      ↓
Frontend Implementation
```

Security, Quality, machine-interface and Engineering Policy capabilities attach as prerequisites where required by the project.

This is a dependency graph, not a stage machine.

## Ownership

Existing Authorities remain sufficient:

- PRODUCT-REQUIREMENTS owns users, outcomes, scope and externally observable product behavior.
- DOMAIN / DOMAIN-USE-CASE-DESIGN owns domain language, states, invariants and business outcomes.
- APPLICATION-DESIGN owns user-goal/application journeys and orchestration before screen decisions.
- INTERFACE-DESIGN owns information architecture, navigation, user-visible interaction semantics, reusable presentation-system decisions and concrete screen/view composition.
- SYSTEM-ARCHITECTURE owns frontend runtime boundaries, client/server responsibility, state/cache ownership when architectural, and dependency topology.
- SECURITY-ARCHITECTURE owns authentication/session trust boundaries and credential lifecycle.
- QUALITY-DESIGN owns measurable architecture-significant frontend quality constraints.
- COMPONENT-DESIGN owns code-facing frontend component/port/dependency boundaries.
- VERIFICATION-DESIGN and TEST-DESIGN own evidence and executable behavioral contracts.
- IMPLEMENTATION-DESIGN owns bounded realization slicing.

Do not create FRONTEND-DESIGN, UI-DESIGN, UX-DESIGN or ACCESSIBILITY-DESIGN Authorities merely to group frontend work.

## Active reusable knowledge kinds

### user-journey-design

Owner: APPLICATION-DESIGN.

Purpose: materialize task-oriented application interaction before view/screen decisions.

Canonical procedure:
`skills/artifacts/user-journey-design/SKILL.md`.

A journey establishes actor, goal, entry conditions, meaningful interactions, alternate/failure/recovery paths, completion and externally visible effects.

A journey is not a screen flow.

### human-interface-design

Owner: INTERFACE-DESIGN.

Purpose: materialize implementation-independent human-interface semantics from accepted journeys and upstream product/domain/security knowledge.

Canonical procedure:
`skills/artifacts/human-interface-design/SKILL.md`.

The result may establish:

- information architecture;
- navigation;
- view/screen boundaries;
- user-visible state model;
- state transitions;
- actions;
- validation/error/recovery semantics;
- authorization-sensitive presentation;
- focus/keyboard/input semantics where applicable;
- responsive/adaptive semantics where accepted constraints require them.

It must preserve implementation freedom for framework, CSS mechanics, private component decomposition, state libraries and equivalent local realization choices.

### presentation-system-design

Owner: INTERFACE-DESIGN.

Purpose: define reusable application-level presentation knowledge once so every screen inherits a consistent visual/interaction language instead of re-deciding it locally.

Typical facets include hierarchy, density, typography/color/spacing roles, layout principles, action/navigation/feedback patterns, responsive/accessibility defaults, reusable task patterns and design tokens where they carry stable design meaning.

This is design knowledge. A UI component library remains a downstream reusable implementation asset unless explicitly granted canonical contract status.

### screen-view-design

Owner: INTERFACE-DESIGN.

Purpose: define implementation-independent composition for each required screen/view after interaction semantics and a Presentation System are known.

A screen contract identifies inherited presentation system, regions/sections/tabs/disclosures, content/action hierarchy, reusable pattern references, state variants, responsive transformations and justified local overrides. CSS/framework mechanics and exact coordinates remain free unless an accepted invariant requires them.

Structured YAML/JSON is preferred when sufficient. Wireframes, prototypes, Figma frames and Storybook stories may be generated projections.

## Screen semantic closure

Screen/View Design is also the canonical closure point between machine-interface operations and presentation realization. A user-facing screen is not complete merely because a Screen/View artifact and Presentation System exist.

For server-backed screens, the contract records accepted read/query and command operation ids, a semantic Screen/View Model, state/error outcome mapping, allowed capabilities, presentation feature bindings and verification obligations. The executable frontend adapter maps transport/query representations into the Screen/View Model; private component props remain Component Design/implementation concerns.

External presentation templates are reusable providers, not semantic authority. A version-pinned baseline may replace hand-authored low-level visual rules, but optional provider features are deny-by-default and must be explicitly bound to accepted screen capabilities. This prevents demo routes, entities, search/filter/sort/pagination/bulk/edit/delete behavior or other template affordances from entering product semantics implicitly.

This refinement adds no Authority or frontend-specific Core entity family. See `docs/research/frontend-screen-contract-layer-v1.md` and `frontend_screen_contracts.py`.

## Human-interface quality analysis

Accessibility/usability coverage remains a cross-Authority analysis, not a new Authority.

For user-facing surfaces, Human Interface Design applies:
`skills/artifacts/human-interface-quality-analysis/SKILL.md`
before semantic acceptance.

Discovered gaps are routed to their semantic owners:

- Product for user/scope requirements;
- Interface for interaction/presentation semantics;
- Quality for measurable targets;
- Obligation for external conformance duties;
- Verification/Test for evidence.

A persistent quality/conformance CapabilityId is added only when the target project has an independently consumed durable contract.

## Frontend architecture

Use ordinary SYSTEM-ARCHITECTURE production for frontend-scoped architecture.

Typical decisions include:

- browser/mobile/desktop runtime boundary;
- client/server responsibility;
- rendering/deployment topology when material;
- frontend module topology;
- state ownership and lifetime;
- cache/invalidation policy when architectural;
- API adapter boundary;
- authentication/session integration;
- dependency direction.

Do not introduce a new `frontend-architecture` knowledge kind unless repeated consumer evidence shows the generic system-architecture procedure is insufficient.

Security-critical browser/session decisions are not frontend implementation conventions. If authentication acquisition, credential storage, refresh, logout or invalidation semantics are missing, create a Question to SECURITY-ARCHITECTURE and block downstream frontend architecture.

## Frontend component and test design

Reuse existing `component-design`, `verification-strategy`, `test-design` and `implementation-design` knowledge kinds with frontend-scoped capabilities.

Component Design should prevent:

- raw transport DTOs becoming UI semantic models;
- pages/views owning business truth;
- shared components becoming cross-feature dependency hubs;
- global state becoming the default owner;
- framework-specific stores/routes becoming hidden cross-feature integration contracts.

Frontend Test Design derives observable oracles from accepted human-interface semantics. It may cover journeys, view-state transitions, navigation, validation/recovery, keyboard/focus behavior, permission-sensitive behavior and backend-outcome-to-UI-state mapping.

Snapshot or visual-regression tests do not become semantic authority unless the corresponding visual invariant is intentionally canonical.

## Design system

A monolithic design-system capability is conditional.

Reusable project presentation decisions are represented by `presentation-system-design`. A broader governed Design System may exist when foundations, patterns, reusable components and governance have independent lifecycle/consumers; do not use the term to collapse those distinct concerns.

Figma, Storybook, token files, diagrams or prototypes may materialize canonical knowledge only when the target project explicitly assigns them Authority ownership and versioned contract meaning. Otherwise they are projections/review surfaces.

## Consumer completeness

Do not make every software application require human-interface knowledge.

A user-facing implementation consumer explicitly requires the frontend closure. Backend or non-interactive consumers may require different closures from the same Engineering Graph.

The acceptance fixture in `examples/user-facing-application/**` verifies that:

1. missing journey knowledge routes to APPLICATION-DESIGN;
2. missing human-interface knowledge routes to INTERFACE-DESIGN;
3. reusable Presentation System knowledge and concrete Screen/View Design are required before frontend architecture;
4. every required screen inherits the shared Presentation System and local deviations are explicit;
5. frontend architecture follows accepted interface/security/quality inputs;
6. Component Design and Verification may become parallel frontiers;
7. Test Design and Implementation Design follow;
8. the consumer reaches COMPLETE only when its declared closure is realized;
9. an unresolved Security Architecture Question blocks the frontend consumer and suppresses downstream CREATE work.

## Evidence for this boundary

The model was validated against NAPMS in two blind design slices:

- a cross-context first-MVP policy journey;
- Resource detail/history.

The blind reconstruction recovered material user-visible semantics from accepted upstream product/domain/security/machine-interface knowledge without using existing frontend source as authority.

It also exposed a real missing browser authentication/session decision and successfully routed that gap back to SECURITY-ARCHITECTURE through the existing Question mechanism.

Therefore no Core, Engineering Graph, target-state or agent-router semantic change is required for frontend design.
