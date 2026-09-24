# Research — Frontend UI/UX design closure v1

Status: validated research candidate for canonicalization after CI.

## Question

What is the minimum complete set of independent UI/UX design knowledge that lets a frontend implementer realize an accepted user interface without inventing material UX/UI decisions, while preserving implementation freedom?

## Evidence synthesis

Across ISO 9241 human-centred design/interaction guidance, W3C/WAI/WCAG, Nielsen Norman heuristics and mature design systems (Apple HIG, Fluent, Material, GOV.UK, USWDS, Carbon, Atlassian, Shopify Polaris, Adobe Spectrum), the recurring separation is:

1. user goals/tasks/context;
2. interaction/information semantics;
3. shared presentation foundations/patterns;
4. concrete page/view composition;
5. reusable implementation components and technical realization;
6. evaluation/verification.

Mature systems consistently separate foundations/tokens/styles, components and task patterns. Accessibility and usability cut across all of them rather than forming a single visual layer. Design tokens encode reusable design decisions but are not themselves a design system or component library.

## Taxonomy decision

Harness should model four independently meaningful frontend design knowledge families:

### A. User Journey Design

Already canonical under APPLICATION-DESIGN.

Owns actor/goal/task flow, alternatives and completion without deciding screens.

### B. Human Interface Design

Already canonical under HUMAN-INTERFACE-DESIGN.

Owns information architecture, navigation, view boundaries, visible states, actions, transitions, validation/recovery, authorization-sensitive interaction, accessibility interaction semantics and adaptive semantics.

It answers **what the human interaction means**.

### C. Presentation System Design

New knowledge kind under HUMAN-INTERFACE-DESIGN.

Owns reusable application-level presentation choices inherited by screens:
- hierarchy/density/layout principles;
- typography/color/spacing/iconography roles when material;
- action/navigation/feedback conventions;
- reusable task patterns;
- responsive/accessibility defaults;
- semantic design tokens when useful;
- deviation rules.

It answers **what common presentation language all screens share**.

This is broader than Visual Style and smaller than a vendor-style Design System.

### D. Screen / View Design

New knowledge kind under HUMAN-INTERFACE-DESIGN.

Owns local composition:
- regions/sections/tabs/disclosures;
- content/action hierarchy;
- selected reusable patterns;
- table/form/list/detail composition;
- state variants;
- responsive transformations;
- explicit justified overrides.

It answers **how one accepted interaction context is composed**.

## Not separate mandatory capabilities

Typography, spacing, density, color, forms, tables, search/filter/sort, dialogs, feedback, loading/empty states, progressive disclosure, iconography, content, motion, data visualization and personalization are facets. They become independently activated only when project evidence requires independent lifecycle/consumers.

Accessibility and usability remain cross-cutting concern lenses with routed ownership and verification.

Internationalization/localization remains conditional cross-cutting interface concern.

## Terminology

- **Visual Style**: visual subset of presentation knowledge (color, type, spacing, imagery, shape, etc.).
- **Presentation System**: project-level reusable presentation contract including visual foundations plus interaction/layout/feedback/responsive conventions.
- **Design System**: broader governed ecosystem of foundations, patterns, components, guidance and lifecycle. Conditional capability, not required name for every project.
- **Pattern Library**: reusable design solutions for recurring tasks/interactions; design knowledge.
- **Design Tokens**: named machine-readable design decisions/values; part of a Presentation System when useful.
- **UI Component Library**: reusable implementation asset realizing design contracts; usually Component Design/implementation, not Interface Design authority.
- **Figma/Storybook**: projections/review/implementation surfaces unless explicitly assigned canonical status.

## Decision boundary

Canonicalize decisions that affect user meaning, discoverability, hierarchy, consistency, interaction, accessibility, responsive preservation or reusable visual/presentation invariants.

Leave realization mechanics free when multiple implementations preserve the contract.

Examples:

- canonical: primary action role and region;
- free: CSS Grid vs Flexbox;
- canonical: semantic heading/action hierarchy;
- free: exact DOM helper decomposition;
- canonical when required: tokenized spacing scale;
- free: generated CSS variable naming;
- usually free: exact pixel coordinates;
- canonical when justified: measurable target/focus size or fixed brand dimension.

## Upstream dependency rule

Create a Question rather than guess when missing inputs materially affect a design decision, especially:
- users/goals/tasks;
- domain vocabulary/state;
- action/business rules;
- permission/security semantics;
- data displayed/edited and expected scale;
- platform/device/channel;
- accessibility obligation;
- branding/content;
- localization/directionality;
- measurable quality target.

## Dependency graph

The graph is not a stage machine.

Typical frontend closure:

Product/Domain/Security/Machine Interface/Quality
          ↓
      User Journey
          ↓
   ┌───────────────┬────────────────────┐
   ↓               ↓                    │
Human Interface   Presentation System   │
   └───────┬───────┘                    │
           ↓                            │
      Screen/View Design                │
           ↓                            │
   Frontend Architecture ←──────────────┘
           ↓
 Component Design + Verification
           ↓
        Test Design
           ↓
 Implementation Design

Presentation System may be developed in parallel with Human Interface once its own prerequisites are known. Screen/View Design requires both because local composition must reference shared presentation defaults.

Feedback edges are Questions/revisions, not hidden inference.

## Completeness

Universal for a frontend implementation consumer:
- journeys required for selected UI scope;
- human-interface semantics required;
- one applicable Presentation System required;
- every required view has Screen/View Design;
- each screen inherits a Presentation System;
- required states/actions/data are represented;
- local overrides are explicit;
- downstream verification covers accepted UI invariants.

Conditional facets:
- tables, forms, search, visualization, motion, personalization, i18n, mobile-specific adaptation, formal WCAG target, branding, etc.

Backend/CLI consumers do not inherit these requirements unless they consume the same UI capabilities.

Coverage Map remains a generated projection. Concern taxonomy can expose:
- interface.human.semantics;
- interface.human.presentation-system;
- interface.human.screen-composition;
with deeper leaves activated only when independently decidable.

## Canonical machine-readable shape

Presentation System example:

```yaml
kind: presentation-system-design
id: APP-PRESENTATION
principles:
  action_hierarchy: one clear primary action per task context
patterns:
  DETAIL:
    regions: [context, primary-content, actions, secondary-content]
tokens:
  density: {default: comfortable}
responsive:
  preserve: [information, actions, semantic-order]
deviation_policy:
  require_rationale: true
```

Screen example:

```yaml
kind: screen-view-design
id: APPLICATION-DETAIL
inherits: APP-PRESENTATION
purpose: Author one application and its communication structure.
regions:
  - {id: context, role: heading-context, priority: primary}
  - {id: components, pattern: EDITABLE-LIST, priority: primary}
  - {id: interactions, pattern: EDITABLE-TABLE, priority: primary}
states: [loading, loaded, empty, validation-rejected, conflict, error]
responsive:
  - when: narrow
    transform: editable-table-to-labeled-records
overrides: []
```

This contract can generate a wireframe skeleton, screen inventory, state matrix, navigation map, responsive review views or Figma/Storybook scaffolding. Those outputs remain projections by default.

## Pilot — NAPMS

Existing NAPMS Human Interface Design covers nine canonical workspaces and strong state/transition semantics. Resource Detail additionally defines current/history priority and a few composition constraints.

Missing material decisions across the full frontend:
- one shared application Presentation System;
- common shell/layout/density/action hierarchy;
- reusable catalogue/detail/editor/table/form/feedback patterns;
- consistent placement and visual hierarchy rules;
- explicit per-screen composition for most of the nine workspaces;
- inherited responsive composition rules;
- explicit local deviations.

Therefore current NAPMS frontend is semantically designed but not presentation-closed. A developer can still make substantial UI decisions.

The model fits NAPMS without making its table-heavy patterns universal: table/detail patterns are project-local Presentation System entries.

## Pilot — Nutrition Management

Existing design has Overview, Household, Food Knowledge, Market, Plan and Result, including detailed semantic sections and accessibility/responsive baselines.

It still deliberately leaves typography/colors/spacing, table-vs-card realization and modal-vs-page realization free. Some of those are legitimate implementation freedom; others become material if consistency across the application is a goal.

A small Presentation System can define shell, hierarchy, form/status patterns, density and responsive default, while Screen/View contracts choose composition for each workspace. Nutrition needs different patterns from NAPMS, proving the abstraction is not enterprise/table-specific.

## Gap analysis

P0:
- frontend consumer completeness can currently pass without shared Presentation System and per-screen composition;
- Human Interface skill conflates semantic interaction with optional spatial composition.

P1:
- design-system terminology is too coarse to distinguish design knowledge from component implementation assets;
- reusable inheritance/deviation policy is not first-class;
- verification does not explicitly require presentation/screen invariants.

P2:
- generated wireframe/prototype/Figma projections are not described as derivable from structured contracts;
- concern taxonomy can expose presentation/screen leaves when Coverage prototype becomes canonical.

P3:
- naming/documentation consistency.

## Rejected alternatives

- **One monolithic DESIGN-SYSTEM capability**: mixes visual foundations, interaction patterns, components and governance; poor applicability.
- **New UI/UX Authority**: no independent semantic ownership/lifecycle beyond HUMAN-INTERFACE-DESIGN.
- **Put all composition in Human Interface Design**: preserves current blind spot because shared vs local presentation knowledge is not separately complete.
- **Pixel-perfect canonical screens/Figma**: overconstrains implementation and makes a tool/file format the authority.
- **One capability per UI facet**: excessive graph/checklist complexity; facets should activate only when independently consumed/decidable.
- **Component library as design authority**: implementation assets cannot substitute for accepted UX/UI semantics.

## Minimal Harness change-set

1. add `presentation-system-design` and `screen-view-design` knowledge kinds, both owned by HUMAN-INTERFACE-DESIGN;
2. register skills for each;
3. make frontend example graph require Presentation System + Screen/View closure before architecture;
4. extend verification/test dependencies to accepted screen/presentation contracts;
5. regression-test that missing presentation or screen design prevents frontend completion;
6. update canonical frontend-design model and Human Interface skill boundary;
7. keep Coverage Map and visual artifacts as generated projections.
