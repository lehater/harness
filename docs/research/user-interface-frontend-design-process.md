# User Interface / Frontend Design Process Research

Status: research result, not canonicalized  
Date: 2026-09-20

## Purpose

Define a correct engineering chain for designing a user-facing frontend from accepted requirements to implementation-ready knowledge.

The goal is not to prescribe a waterfall. The goal is to make decision ownership and dependency explicit so that an agent does not invent user-visible semantics during coding.

## Main conclusion

A frontend should not be designed as:

`requirements -> pages -> components -> code`.

That chain is too weak because it jumps from product intent directly to visual structure.

The more reliable knowledge chain is:

`problem / users -> product requirements -> user tasks and journeys -> interaction model -> information architecture / navigation -> view and UI-state model -> interaction component contracts -> visual/design system -> frontend technical architecture -> frontend component design -> test design -> implementation`.

The chain is a dependency graph. Some artifacts can be developed in parallel after their prerequisites stabilize.

## 1. Problem, users and context

### Purpose

Establish who is using the product, for what outcome, in what context and under which constraints.

### Owner

Discovery / Product Requirements.

### Inputs

- stakeholder evidence;
- user/problem observations;
- business/product goals;
- environment and platform constraints;
- applicable obligations.

### Output

- user/actor definitions;
- goals/outcomes;
- problem statements;
- important usage contexts;
- accepted scope.

### Why it matters downstream

Without this knowledge UI design tends to optimize for screens rather than tasks.

## 2. Product requirements

### Purpose

Define externally observable behavior and acceptance expectations.

### Owner

Product Requirements.

### Inputs

Problem/user evidence.

### Output

For each relevant capability:

- user-visible outcome;
- supported behavior;
- constraints;
- acceptance semantics;
- authorization/policy consequences where product-visible;
- relevant quality requirements.

### Rule

A UI design must not create new product behavior simply because a common UI pattern suggests it.

## 3. User tasks and journeys

### Purpose

Transform accepted behavior into complete user goal-oriented interactions.

### Owner

Primarily Application Design, constrained by Product and Domain semantics.

### Inputs

- product requirements;
- domain/use-case semantics;
- roles/permissions;
- application orchestration.

### Output

A journey/task contract describing:

- actor;
- entry condition;
- user goal;
- sequence of meaningful user/system interactions;
- decision points;
- alternate paths;
- failure/recovery paths;
- completion condition;
- externally visible side effects.

### Important distinction

A **journey is not a screen flow**.

The journey describes the user's task and observable interaction. Several journey steps may happen on one screen, and one step may span several views.

## 4. Interaction model

### Purpose

Define how a user operates the accepted application behavior.

### Owner

Interface Design.

### Inputs

- journeys/tasks;
- product semantics;
- application/domain outcomes;
- security/admission constraints.

### Output

For each task/action:

- action available to the user;
- required information;
- resulting visible state;
- validation/rejection behavior;
- confirmation/cancellation semantics;
- retry/recovery behavior;
- destructive-action safeguards;
- interruption/resumption behavior where relevant.

### Example

Instead of deciding "there is an Edit page", decide:

- user can initiate editing from entity detail;
- current values become editable;
- validation can reject individual fields;
- submission can succeed, conflict or fail operationally;
- cancellation preserves the original entity;
- after success the user observes the updated entity.

Only after these semantics are known should the design decide whether editing is a page, dialog, drawer or inline mode.

## 5. Information architecture

### Purpose

Define how product information and tasks are organized for human navigation.

### Owner

Interface Design.

### Inputs

- accepted tasks/journeys;
- domain concepts visible to users;
- frequency/importance/context of tasks.

### Output

- top-level information structure;
- task grouping;
- entity/content grouping;
- global vs contextual navigation;
- hierarchy;
- location/context model;
- labels and terminology constrained by domain/product language.

### Consequence

Information architecture answers "where does a user expect to find this?" before screen layout is designed.

## 6. Navigation model

### Purpose

Define supported movement between interaction contexts.

### Owner

Interface Design.

### Inputs

Information architecture + journeys.

### Output

- navigable locations;
- allowed transitions;
- entry points;
- exits;
- back/context preservation;
- deep-link behavior when relevant;
- redirect/guard behavior;
- cross-feature navigation semantics.

### Representation

Can be represented as a graph:

`Location + State --Action/Event--> Location + State`.

Routes/URLs are a possible realization, not the semantic model itself.

## 7. View / screen model

### Purpose

Partition interaction contexts into user-visible views.

### Owner

Interface Design.

### Inputs

- interaction model;
- information architecture;
- navigation model;
- device/platform constraints.

### Output

For each view/screen:

- purpose;
- task(s) supported;
- information shown;
- actions available;
- entry conditions;
- exit transitions;
- major regions;
- relevant contextual information.

### Rule

Screens are a derived design decision.

They should be justified by task/context cohesion rather than by backend resources or endpoints.

## 8. UI state model

### Purpose

Make every materially different user-visible state explicit.

### Owner

Interface Design, while preserving upstream product/application semantics.

### Inputs

Views + application/backend outcomes.

### Output

For each view/component, relevant states such as:

- initial;
- loading;
- loaded;
- empty;
- filtering/searching;
- partial;
- stale;
- submitting;
- success;
- validation failure;
- authorization rejection;
- conflict;
- unavailable/offline;
- operational failure;
- recoverable/retry state.

### Critical rule

A nominal "happy-path screen" is not a complete UI design.

Many frontend defects come from coding agents deciding missing states ad hoc.

## 9. Transition model

### Purpose

Make UI behavior executable and testable.

### Owner

Interface Design.

### Inputs

Interaction + UI state models.

### Output

Transitions of the form:

`State + user/system event -> next state + visible effect + allowed actions`.

Example:

`Editing + Submit(valid) -> Submitting -> Success -> Detail(updated)`

or

`Editing + Submit(conflict) -> Conflict -> user chooses Reload | Reapply | Cancel`.

### Benefit

This creates a direct bridge from product semantics to frontend test design.

## 10. Interaction patterns and semantic UI components

### Purpose

Define reusable interaction contracts.

### Owner

Interface Design.

### Inputs

Repeated interactions across views.

### Output

Examples:

- dialog;
- form;
- data table/grid;
- search/filter controls;
- combobox;
- tabs;
- navigation tree;
- notification/toast;
- destructive confirmation;
- pagination;
- bulk selection.

For each pattern:

- semantic purpose;
- states;
- supported interactions;
- events/outputs;
- keyboard behavior where applicable;
- focus behavior;
- accessible name/role/state requirements;
- error behavior.

W3C ARIA APG documents common accessible UI patterns, keyboard interaction and focus management and is useful as an external coverage lens for web interfaces. It should not replace project-specific interaction semantics.

References:
- https://www.w3.org/WAI/ARIA/apg/
- https://www.w3.org/WAI/ARIA/apg/practices/
- https://www.w3.org/WAI/ARIA/apg/practices/keyboard-interface/

## 11. Layout and responsive/adaptive behavior

### Purpose

Define how information and actions remain usable across supported presentation constraints.

### Owner

Interface Design; measurable constraints may belong to Quality Design.

### Inputs

- accepted platform/device requirements;
- view model;
- content hierarchy;
- interaction priorities.

### Output

- layout regions;
- resizing/reflow rules;
- responsive break behavior where needed;
- priority/order changes;
- overflow behavior;
- touch/pointer considerations;
- minimum interaction constraints where applicable.

### Rule

A responsive design is not a set of arbitrary pixel breakpoints.

Breakpoints are implementation/design-system mechanics derived from meaningful layout transitions.

## 12. Visual hierarchy and design system

### Purpose

Create a coherent reusable visual language after information and interaction semantics are known.

### Owner

Interface Design.

### Inputs

- interaction components;
- view hierarchy;
- branding/product visual constraints;
- accessibility/quality constraints.

### Output

Potentially:

- semantic color roles;
- typography hierarchy;
- spacing scale;
- sizing;
- border/radius/elevation;
- motion semantics;
- focus/error/success states;
- iconography rules;
- semantic design tokens;
- component visual variants.

Design tokens are suitable for canonical tool-neutral representation of reusable visual decisions. The Design Tokens Community Group published a stable 2025.10 exchange format, but Harness should treat it as an optional representation rather than mandatory semantics.

References:
- https://www.w3.org/community/design-tokens/
- https://www.w3.org/community/reports/design-tokens/CG-FINAL-format-20251028/

## 13. Accessibility/usability closure

### Purpose

Validate that the accepted interaction remains operable and understandable for required users and modes.

### Owner

Cross-authority analysis already represented in Harness by `human-interface-quality-analysis`.

### Inputs

Accepted UI design.

### Checks include

- keyboard operability;
- focus visibility and movement;
- structural semantics;
- accessible naming;
- screen-reader meaningful state;
- contrast/reflow requirements where applicable;
- error discovery/recovery;
- cognitive complexity;
- input alternatives.

W3C APG explicitly treats predictable keyboard focus, keyboard operability and component-specific interaction conventions as important accessible-interface concerns.

### Output

Covered concerns and routed gaps to Interface, Product, Quality, Obligation or Verification owners.

## 14. Backend/frontend interface mapping

### Purpose

Connect UI semantics to machine-interface outcomes without leaking transport models into UI semantics.

### Owners

Interface Design + System/Component Design.

### Inputs

- UI state/transition model;
- API/interface contracts;
- accepted error/failure semantics.

### Output

Mapping:

`machine outcome -> application/frontend semantic outcome -> UI state`.

Examples:

- HTTP 409 is not itself a user-visible semantic;
- it might map to `ConcurrentModification`, which maps to a Conflict UI state.

### Rule

UI code should not decide product-visible meaning directly from protocol codes.

## 15. Frontend technical architecture

### Purpose

Define technical structure needed to realize the accepted UI.

### Owner

System Architecture / Component Design.

### Inputs

All accepted frontend semantics plus stack/platform constraints.

### Output

- runtime/rendering model;
- frontend module/feature boundaries;
- routing implementation ownership;
- state ownership/lifetimes;
- API adapter boundaries;
- caching/invalidation;
- async coordination;
- authentication/session integration;
- error boundaries;
- dependency direction;
- shared UI policy;
- design-system integration;
- framework boundary.

### Important separation

This stage answers **how the frontend is structured technically**.

It must not redefine what screens mean or how users are expected to interact.

## 16. Frontend component design

### Purpose

Translate accepted screen/interaction contracts into implementation-facing boundaries.

### Owner

Component Design.

### Output

- page/container responsibilities;
- feature modules;
- domain-specific interaction components;
- reusable UI primitives;
- state controllers/hooks/services as justified;
- mapping/adaptor components;
- dependencies;
- public component contracts;
- intentionally private implementation freedom.

### Typical anti-patterns to prevent

- page component owns business rules;
- global store becomes default integration bus;
- backend DTOs used as UI models everywhere;
- generic shared-components folder becomes dependency sink;
- reusable visual primitive contains domain semantics;
- domain feature depends directly on another feature's internal components.

## 17. Test design

### Purpose

Convert accepted interaction semantics to executable observable contracts.

### Owner

Test Design.

### Inputs

- journeys;
- state/transition model;
- accessibility obligations;
- component contracts.

### Output

Tests/scenarios covering:

- primary journey;
- alternate/recovery paths;
- state transitions;
- validation;
- authorization-sensitive behavior;
- keyboard/focus interactions;
- responsive behavior where material;
- machine-outcome -> UI-state mapping.

### Rule

Tests verify UI semantics; tests do not invent them.

## 18. Verification

### Purpose

Prove the implemented frontend realizes accepted design.

### Owner

Verification Design.

### Evidence can include

- unit/component tests;
- interaction tests;
- browser integration tests;
- journey/E2E tests;
- accessibility tests;
- visual regression tests;
- manual usability evidence where required.

Automated accessibility tools provide partial evidence; they cannot substitute for accepted interaction semantics or all usability/accessibility evaluation.

## Recommended dependency graph

A useful default is:

```
Problem / User Evidence
        |
Product Requirements
        |
Domain / Application Use Cases
        |
User Tasks & Journeys
        |
Interaction Model
        |
+----------------------------+
|                            |
Information Architecture     UI State / Transition Model
|                            |
Navigation Model             |
|                            |
+-------------+--------------+
              |
         View / Screen Model
              |
     Interaction Patterns
              |
+-------------+-------------------+
|                                 |
Visual / Design System       Accessibility/Usability
|                                 |
+----------------+----------------+
                 |
       Frontend Architecture
                 |
       Frontend Component Design
                 |
            Test Design
                 |
            Verification
                 |
         Implementation Design
```

This graph is illustrative. A project can reorder independent work where dependencies allow it.

## What is canonical and what is projection

Harness should distinguish semantic source of truth from visual projections.

### Canonical candidates

- journeys/tasks;
- interaction model;
- navigation/information model;
- view/screen definitions;
- state/transition model;
- semantic component contracts;
- design tokens/rules where normative;
- frontend architecture;
- component design;
- tests/verification obligations.

### Projections

- clickable prototype;
- Figma frames;
- screenshots;
- generated flow diagrams;
- Storybook/documentation;
- route diagrams.

A Figma design may itself be canonical only if the project explicitly chooses it as an authoritative engineering artifact and can preserve traceability/versioning. Otherwise it is a projection of accepted interface knowledge.

## Suggested Harness ownership

No new `FRONTEND-DESIGN` Authority is required.

Use existing Authorities:

| Knowledge | Authority |
|---|---|
| user/problem evidence | Discovery |
| accepted user-visible requirements | Product Requirements |
| domain use cases | Domain/Application |
| user journeys/application orchestration | Application Design |
| interaction semantics | Interface Design |
| information architecture/navigation | Interface Design |
| views/screens | Interface Design |
| UI state/transitions | Interface Design |
| semantic UI patterns | Interface Design |
| visual/design system | Interface Design |
| accessibility/usability criteria | routed through Product/Interface/Quality/Obligation |
| frontend runtime architecture | System Architecture |
| frontend component/module design | Component Design |
| executable UI contracts | Test Design |
| proof strategy | Verification Design |
| coding slices | Implementation Design |

## Recommended Harness artifact chain

For a user-facing application, the smallest reusable chain should be approximately:

1. `product-requirements`
2. `domain-use-case` / application journey knowledge
3. `human-interface-design`
4. `human-interface-quality-analysis`
5. `system-architecture` with frontend-relevant technical constraints
6. `component-design` for frontend scope
7. `test-design`
8. `verification-strategy`
9. `implementation-design`

The `human-interface-design` artifact should internally contain coherent sections for:

- tasks/journeys consumed;
- information architecture;
- navigation;
- views/screens;
- states;
- transitions;
- interaction patterns;
- responsive behavior;
- semantic design-system constraints.

Do not create one Authority or mandatory artifact for every UX discipline name.

## Main risks in the current Harness model

### P0 — screen design can start too early

If an agent goes directly from requirements to screens, it will invent task decomposition and interaction semantics.

Required correction: require accepted journey/task semantics before screen design where the application is non-trivial.

### P0 — happy-path-only UI design

A screen inventory without explicit states/transitions leaves major product behavior to coding.

Required correction: `human-interface-design` must require relevant loading/empty/error/rejected/conflict/recovery states.

### P1 — UI/UX mixed with frontend technical architecture

Visual/interface design and React/Vue/module/state-management decisions have different owners and change independently.

Required correction: keep Interface Design and System/Component Design separate.

### P1 — Figma/prototype can accidentally become undocumented truth

Visual tools often contain decisions not represented in canonical knowledge.

Required correction: either explicitly make the design artifact authoritative or require it to be a traceable projection from canonical interface knowledge.

### P1 — design system can be introduced prematurely

A full design system is expensive and unnecessary for a small product.

Required correction: derive reusable patterns/tokens only after repeated or intentionally standardized decisions demonstrate value.

## Minimal pilot recommendation

Do not model all NAPMS UI first.

Take one representative journey and run the complete chain:

`requirements -> journey -> interaction -> navigation/view -> state transitions -> UI patterns -> frontend architecture -> test design`.

Choose a journey with:

- list/search/filter;
- detail;
- create/edit;
- validation;
- backend failure;
- permission-sensitive action;
- navigation/context preservation.

The pilot succeeds if an implementation agent can build the journey without inventing any materially user-visible behavior or major frontend structural decision.

## Final conclusion

Correct frontend design is not primarily the design of screens.

It is the progressive materialization of user-facing product semantics:

`requirements -> tasks -> interactions -> information/navigation -> views -> states/transitions -> reusable interaction/visual rules -> technical realization -> verification`.

Screens are one intermediate projection of that model.

For Harness, the key missing abstraction is therefore a strong `human-interface-design` artifact procedure, not a new frontend Authority.
