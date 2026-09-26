# Frontend design v0

Status: canonical active design

Harness supports user-facing/frontend engineering through the existing engineering-knowledge model. Frontend work does not introduce a separate workflow or Core entity family.

## Boundary

Frontend completeness is consumer-specific.

A frontend implementation consumer may require this knowledge closure:

```text
Product Requirements
      ↓
Domain / Use-case + Application Design
      ↓
Task Model
      ↓
User Journeys
      ↓
Conceptual Interface Model
      ├───────────────┐
      ▼               ▼
Information       Interaction
Architecture      Design
      └───────┬───────┘
              ▼
      Interface Topology
          ├──────────────► early interface verification when applicable
          ▼
   Presentation System
          │
          ▼
    Screen / View Design
          │
          ▼
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
- HUMAN-INTERFACE-DESIGN owns information architecture, navigation, user-visible interaction semantics, reusable presentation-system decisions and concrete screen/view composition.
- SYSTEM-ARCHITECTURE owns frontend runtime boundaries, client/server responsibility, state/cache ownership when architectural, and dependency topology.
- SECURITY-ARCHITECTURE owns authentication/session trust boundaries and credential lifecycle.
- QUALITY-DESIGN owns measurable architecture-significant frontend quality constraints.
- COMPONENT-DESIGN owns code-facing frontend component/port/dependency boundaries.
- VERIFICATION-DESIGN and TEST-DESIGN own evidence and executable behavioral contracts.
- IMPLEMENTATION-DESIGN owns bounded realization slicing and repository/module realization derived from accepted boundaries.

Do not create FRONTEND-DESIGN, UI-DESIGN, UX-DESIGN or ACCESSIBILITY-DESIGN Authorities merely to group frontend work.

## Active reusable knowledge kinds

### task-model

Owner: APPLICATION-DESIGN.

Purpose: expose complete goal → task/subtask responsibility before concrete journeys or interface partitioning. USER work must be explicit enough that later Interaction/Topology coverage can prove no task disappeared silently.

### user-journey-design

Owner: APPLICATION-DESIGN.

Purpose: materialize task-oriented application interaction before view/screen decisions.

Canonical procedure:
`skills/artifacts/user-journey-design/SKILL.md`.

A journey establishes actor, goal, entry conditions, meaningful interactions, alternate/failure/recovery paths, completion and externally visible effects.

A journey is not a screen flow.

### conceptual-interface-model

Owner: HUMAN-INTERFACE-DESIGN.

Purpose: define the user-facing concepts, modes and shared visible state vocabulary required to make accepted product/application behavior understandable without copying the Domain Model mechanically.

### information-architecture-design

Owner: HUMAN-INTERFACE-DESIGN.

Purpose: define conceptual locations, grouping, hierarchy/cross-links, labels/taxonomy and findability independently of concrete page composition.

### interaction-design

Owner: HUMAN-INTERFACE-DESIGN.

Purpose: define USER actions, visible system responses, material states/transitions, recovery and input/focus semantics independently of final view partitioning.

Information Architecture and Interaction Design may be produced in parallel after the Conceptual Interface Model when neither needs to invent the other's decisions.

### interface-topology-design

Owner: HUMAN-INTERFACE-DESIGN.

Purpose: define the complete material view/frame inventory and navigation relationships that map accepted interaction contexts into accepted information locations.

Task views carry interaction-context coverage. Material shells/workspaces may be explicit `structural: true` topology views without claiming USER tasks. Site maps/app maps/screen maps are projections from this knowledge.

### human-interface-design — compatibility only

Owner: HUMAN-INTERFACE-DESIGN.

The broad `human-interface-design` kind remains registered for legacy/project-specific graphs that intentionally keep conceptual model, IA, interaction and topology knowledge inseparable. New/revalidated non-trivial frontend graphs should not add this capability merely as a synthesis layer on top of the granular contracts.

### presentation-system-design

Owner: HUMAN-INTERFACE-DESIGN.

Purpose: define reusable application-level presentation knowledge once so every screen inherits a consistent visual/interaction language instead of re-deciding it locally.

Typical facets include hierarchy, density, typography/color/spacing roles, layout principles, action/navigation/feedback patterns, responsive/accessibility defaults, reusable task patterns and design tokens where they carry stable design meaning.

This is design knowledge. A UI component library remains a downstream reusable implementation asset unless explicitly granted canonical contract status.

#### Default entity collection drill-down

For a primary collection of stable product entities, the Presentation System should default to an outside-in interaction model unless accepted product/interface semantics explicitly require another task shape:

1. enter through an entity catalogue rather than directly into an arbitrary instance;
2. render the primary collection as a data table with stable identity plus task-relevant distinguishing attributes;
3. provide collection query controls by default: search, attribute filtering and sorting, with pagination/virtualization when collection size requires it;
4. selecting/opening a row navigates to a dedicated detail view for that entity instance;
5. the detail view presents the full accepted instance state and is the default place for entity editing/state-changing commands;
6. inline table editing is not the default and requires explicit Screen/View authorization;
7. structured lists are for nested, secondary, relationship or otherwise non-comparative repeated records by default, not the primary entity catalogue.

If the accepted query/API contract does not yet support the required collection controls, treat that as an upstream engineering-knowledge gap to resolve. Do not silently downgrade the catalogue to an unfiltered client-only list, and do not invent client-side filtering over partial data. Any deviation from the catalogue-table-detail default requires an explicit Screen/View override with rationale.

### screen-view-design

Owner: HUMAN-INTERFACE-DESIGN.

Purpose: define implementation-independent composition for each required screen/view after interaction semantics and a Presentation System are known.

A screen contract identifies inherited presentation system, regions/sections/tabs/disclosures, content/action hierarchy, reusable pattern references, state variants, responsive transformations and justified local overrides. CSS/framework mechanics and exact coordinates remain free unless an accepted invariant requires them.

Structured YAML/JSON is preferred when sufficient. Wireframes, prototypes, Figma frames and Storybook stories may be generated projections.

## Accepted visual references and rendered conformance

A sketch, screenshot, Figma frame or executable prototype is normally a projection/evidence surface. A target project may intentionally make one a versioned **visual reference** inside its existing Presentation System or Screen/View Design when prose and structural fields alone would leave material hierarchy, composition, density or relative visual weight for implementation to reinvent.

This does **not** create a new Authority, Core entity, Stage, Gate or handoff. Ownership remains:

- HUMAN-INTERFACE-DESIGN owns which visual presentation facts are accepted and which details remain implementation freedom;
- VERIFICATION-DESIGN owns the rendered-conformance evidence obligation;
- TEST-DESIGN owns executable comparison oracles when automation is appropriate;
- INSPECTION/DEMONSTRATION may provide human perceptual evidence when an automated oracle would be weaker or more brittle.

An accepted visual reference must identify the artifact/ref, enumerate the presentation facts it constrains and enumerate material freedoms it deliberately leaves unconstrained. Downstream evidence must trace back to that reference. Pixel-perfect equality is required only when exact pixels are intentionally accepted; otherwise the oracle should target hierarchy, region weight, density, alignment, responsive transformation or other declared presentation facts.

A screenshot, diff or Figma file never authorizes product behavior, data semantics, permissions or domain truth. It can constrain presentation only to the extent explicitly admitted by HUMAN-INTERFACE-DESIGN.

## Performance-sensitive presentation surfaces

When a user-facing visualization, canvas, map, graph, dense table or other presentation surface has accepted measurable constraints for data size, frame/interaction latency, resource usage or graceful degradation, that knowledge belongs to QUALITY-DESIGN and must participate in the frontend consumer closure.

Do not leave such constraints as an unregistered architecture note or prototype-only observation. If the constraint is independently consumed by frontend architecture/component/verification/implementation work, register a project Quality capability and make the dependent frontend capabilities require it.

Screen/View Design owns the user-visible semantic consequences of degradation (for example, preserving relation type/direction access when decorative arrows or labels are reduced). Component/Implementation Design owns private renderer tactics such as instancing, batching, pixel ratio and force-engine details. Verification/Test Design owns representative workload evidence.

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

For a frontend consumer with an applicable Security Architecture, Engineering Coverage activates `security.identity`. That concern requires explicit semantic acceptance evidence rather than artifact-presence proof. A project-native evaluator should accept the identity claim only after applicable browser/client credential acquisition, storage/runtime lifetime, expiry/renewal, logout/invalidation and rejection-recovery semantics are explicit, or after identity is explicitly accepted as not applicable.

## Presentation provider realization

Presentation providers such as Material UI belong to downstream realization, not Human Interface or Screen/View semantic ownership.

The dependency is:

```
HTTP/interface contracts
        ↓
frontend query/command + semantic Screen/View Model
        ↓
Screen/View semantics
        ↓
provider-neutral Presentation System patterns
        ↓
Component Design: presentation-provider mapping/adapter
        ↓
provider theme/components/templates
        ↓
rendered UI
```

Component Design owns the provider mapping because it is an implementation-facing dependency decision. Screen/View Design remains provider-neutral and authorizes the product-visible capabilities that a provider realization may expose.

A provider contract should identify the selected provider/version, map accepted Presentation System patterns to provider adapters/primitives, and use a deny-by-default feature policy. The provider cannot authorize search, filtering, sorting, pagination, editing, deletion or any other product capability merely because a template/component supports it.

Provider abstraction should stay narrow. Do not mirror the provider component API or build a universal UI framework. Introduce seams only for project patterns or dependencies whose replacement would otherwise force product/application semantic changes.

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

## Prototype consumers

A frontend prototype is not a Stage or special Core entity. Model it as an ordinary Consumer whose dependency closure matches the decisions the experiment is allowed to make.

A disposable UX/presentation prototype may intentionally stop before production Component or Implementation Design when its code is evidence only and may be discarded. It must not silently become the canonical production structure.

When prototype code is intended for production reuse, or the experiment must choose material module boundaries, state ownership, DTO/view-model mapping, renderer/provider abstractions or cross-module dependency direction, include the corresponding System Architecture and Component Design capabilities in that Consumer. Production coding additionally uses a Consumer whose recursive closure contains `implementation-design`.

Promotion from prototype evidence to production code is therefore ordinary revalidation/adaptation against the production Consumer closure, not a workflow transition.

## Design system

A monolithic design-system capability is conditional.

Reusable project presentation decisions are represented by `presentation-system-design`. A broader governed Design System may exist when foundations, patterns, reusable components and governance have independent lifecycle/consumers; do not use the term to collapse those distinct concerns.

Figma, Storybook, token files, diagrams or prototypes may materialize canonical knowledge only when the target project explicitly assigns them Authority ownership and versioned contract meaning. Otherwise they are projections/review surfaces.

## Consumer completeness

Do not make every software application require human-interface knowledge.

A user-facing implementation consumer explicitly requires the frontend closure. Backend or non-interactive consumers may require different closures from the same Engineering Graph.

The granular full-stack acceptance fixture in `examples/user-facing-application/**` verifies that:

1. Task Model precedes User Journeys;
2. Conceptual Interface Model precedes independently addressable IA and Interaction Design;
3. Interface Topology waits for IA + Interaction and proves USER task → interaction context → material view/frame closure;
4. material structural shells/workspaces are explicit topology subjects rather than hidden in a sitemap projection;
5. expected Screen/View subjects are derived from topology;
6. missing or unexpected Screen/View subjects are rejected;
7. granular conceptual/IA/interaction/topology claims require explicit semantic acceptance evidence rather than provider existence;
8. Presentation System and Screen/View follow accepted topology/interaction knowledge;
9. early interface verification may consume IA/Interaction/Topology without creating a production-graph cycle;
10. the frontend consumer reaches COMPLETE only when its declared closure is realized.

The minimal `examples/frontend-legacy-compatibility/**` fixture exists only to verify broad-interface migration behavior. Engineering Coverage must surface missing granular concerns for that legacy graph rather than silently treating the broad provider as proof.

## Evidence for this boundary

The model was validated against NAPMS in two blind design slices:

- a cross-context first-MVP policy journey;
- Resource detail/history.

The blind reconstruction recovered material user-visible semantics from accepted upstream product/domain/security/machine-interface knowledge without using existing frontend source as authority.

It also exposed a real missing browser authentication/session decision and successfully routed that gap back to SECURITY-ARCHITECTURE through the existing Question mechanism.

The granular closure requires no new Core entity and no new frontend/UX Authority. It extends reusable knowledge kinds, concern/proof contracts and validation/coverage behavior while preserving the Engineering Graph/Core integration model.


## Granular human-interface closure

The granular production topology lives inside the existing HUMAN-INTERFACE-DESIGN Authority. It does not add workflow stages, Core entities or UI/UX Authorities.

Independently addressable knowledge:

- `conceptual-interface-model` — user-facing concepts, modes and shared visible state vocabulary;
- `information-architecture-design` — information organization, conceptual locations, taxonomy/labels and findability;
- `interaction-design` — actions, system responses, states/transitions and recovery;
- `interface-topology-design` — complete view/context inventory and navigation relationships.

A sitemap, app map, screen map, wireframe or Figma file remains a projection. The canonical completeness chain is:

```text
USER task
  -> interaction context or explicit no-ui disposition
      -> topology task view or explicit non-view disposition
          -> Screen/View contract

Material shared shells/workspace frames are explicit structural topology views (`structural: true`) so a site/app map can remain a projection without carrying extra canonical structure.
```

The same VERIFICATION-DESIGN Authority may produce early interface verification from Task/IA/Interaction/Topology before local Screen/View composition, while later presentation verification depends on Presentation System + Screen/View. Feedback remains ordinary Questions/revalidation; the production graph stays acyclic.


### Broad human-interface compatibility contract

`human-interface-design` remains registered for legacy/project-specific graphs that deliberately keep conceptual, IA, interaction and topology knowledge inseparable.

The granular frontend closure does **not** require an additional broad synthesis Capability. New graphs should depend directly on the granular capabilities they actually consume. Human-readable synthesis documents remain projections unless a project intentionally chooses the broad compatibility contract and can justify that boundary.
