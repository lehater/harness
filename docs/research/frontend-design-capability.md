# Frontend Design Capability Research

Status: research result, not canonicalized  
Date: 2026-09-20

## Purpose

Determine whether Harness can design a frontend from accepted product/domain/system knowledge to implementation-ready frontend knowledge, and identify the smallest justified changes if it cannot.

This research evaluates Harness as an engineering-knowledge system, not as a UI-generation tool.

## Result

Harness currently covers important parts of frontend engineering, but it does **not yet provide a complete frontend-design path**.

The Core model is sufficient. The main gap is in the agent/artifact layer:

- `INTERFACE-DESIGN` already owns human interaction and representation decisions;
- `APPLICATION-DESIGN`, `SYSTEM-ARCHITECTURE`, `SECURITY-ARCHITECTURE`, `QUALITY-DESIGN`, `COMPONENT-DESIGN`, `TEST-DESIGN` and `VERIFICATION-DESIGN` can own their existing frontend-relevant decisions;
- `human-interface-quality-analysis` already routes accessibility/usability concerns correctly;
- the current `interface-contract` skill is too generic to reliably derive a non-trivial frontend design.

Therefore the missing capability is not a new Core entity or a generic `FRONTEND-DESIGN` Authority. It is a reusable frontend-oriented decomposition of accepted Interface Design knowledge plus frontend realization constraints.

## What a complete frontend design must decide

A coding agent should not have to invent any material item below.

### 1. User/task interaction semantics

Responsibility: Interface Design.

Required knowledge:

- user-visible tasks and journey entry/exit points;
- supported actions per task;
- state transitions visible to the user;
- success, empty, loading, partial, unavailable, rejected and recoverable-error states;
- confirmation/cancellation/retry semantics;
- navigation consequences of actions;
- visibility and interaction rules derived from authorization/product policy.

This is more precise than a list of pages.

### 2. Information architecture and navigation

Responsibility: Interface Design, derived from accepted Product/Application semantics.

Required knowledge:

- navigation model;
- screen/route hierarchy where routes are relevant;
- task grouping;
- contextual vs global navigation;
- deep-link semantics where applicable;
- preservation/restoration of user context;
- canonical location of actions and information.

A route table alone is insufficient because it does not define the information model or task topology.

### 3. View/state model

Responsibility: Interface Design for user-visible state; Application/System for upstream semantics.

Required knowledge:

- view states and transition triggers;
- mapping from accepted backend/application outcomes to user-visible states;
- stale/refresh/conflict semantics when applicable;
- optimistic/pessimistic interaction policy where externally observable;
- destructive-action safeguards;
- interruption and resumability semantics.

This prevents frontend code from inventing product behavior.

### 4. Interaction component contracts

Responsibility: Interface Design.

Required knowledge:

- semantic UI components/patterns used by the product;
- inputs, outputs/events and states;
- keyboard/pointer/touch behavior where applicable;
- focus behavior;
- accessible name/role/state semantics;
- validation and error-presentation behavior;
- composition rules when a component expresses product interaction semantics.

These are interaction contracts, not React/Vue/Svelte component APIs.

W3C ARIA Authoring Practices is useful as a coverage lens for web widgets and keyboard/focus behavior, but remains external guidance unless a project makes the relevant requirements applicable.

References:
- https://www.w3.org/WAI/ARIA/apg/
- https://www.w3.org/WAI/ARIA/apg/practices/

### 5. Visual/design-system decisions

Responsibility: Interface Design when externally observable and intentionally standardized; Implementation Design for local mechanics.

Required knowledge when the product needs a coherent reusable visual system:

- semantic design tokens;
- typography hierarchy;
- spacing/sizing rules;
- color roles and state roles;
- elevation/border/radius/motion conventions when material;
- responsive layout rules;
- component variants that carry supported semantics.

A design-token representation can be canonical and tool-neutral. The Design Tokens Community Group published a stable 2025.10 format that can be used when interoperability is useful, but Harness should not require that format.

Reference:
- https://www.w3.org/community/reports/design-tokens/CG-FINAL-format-20251028/

### 6. Frontend technical architecture

Responsibility: System Architecture + Component Design, not Interface Design.

Required knowledge can include:

- frontend runtime/deployment boundary;
- client/server rendering model when material;
- route ownership;
- state ownership and lifetime;
- API/adaptor boundaries;
- cache/invalidation ownership;
- authentication/session integration;
- feature/module dependency direction;
- cross-feature shared component policy;
- composition/root wiring;
- allowed framework coupling;
- error boundary strategy;
- performance/resource constraints that affect architecture.

This is where "frontend architecture" belongs. Creating a FRONTEND-ARCHITECTURE Authority would mix a technology surface with already distinct decision owners.

### 7. Accessibility and usability closure

Responsibility is already correctly distributed by Harness.

Current `human-interface-quality-analysis` should remain the reusable cross-authority analysis.

It should consume accepted frontend interaction design and route:

- interaction/presentation semantics -> Interface Design;
- measurable constraints -> Quality Design;
- externally imposed conformance -> Obligation Analysis;
- proof -> Verification/Test.

WCAG and ISO 9241-210 are useful coverage lenses, not automatic project requirements.

References:
- https://www.w3.org/TR/WCAG22/
- https://www.iso.org/standard/77520.html

### 8. Frontend verification/test design

Responsibility: Verification Design + Test Design.

Expected evidence includes:

- journey/task acceptance;
- state-transition coverage;
- interaction component contracts;
- keyboard/focus behavior where applicable;
- accessibility semantics;
- responsive behavior where accepted;
- authorization visibility/action rules;
- backend-to-view outcome mapping;
- visual-regression checks only where visual invariants are intentionally accepted.

Snapshot testing must not become the source of frontend semantics.

## Current Harness coverage

### Already sufficient

- Core: Authority / CanonicalArtifact / CapabilityId / Question / dependencies.
- Product Requirements: user-visible requirements and acceptance expectations.
- Application Design: journeys and orchestration.
- Interface Design Authority: correct ownership boundary for human-interface semantics.
- System Architecture: frontend runtime/topology decisions.
- Security Architecture/Analysis: session, trust and admission constraints.
- Quality Design: performance and measurable quality constraints.
- Component Design: implementation-facing frontend modules, ports and dependencies.
- Human Interface Quality Analysis: accessibility/usability closure.
- Test/Verification Design: executable evidence and traceability.

### Material gaps

#### P0 — no frontend-oriented Interface Design procedure

The existing `interface-contract` skill allows a "UI interaction contract", but its procedure is intentionally generic. It does not force coverage of:

- navigation/information architecture;
- explicit UI state model;
- task-level transitions;
- error/empty/loading/partial states;
- focus/keyboard interaction;
- responsive behavior;
- semantic component patterns;
- design-system decisions.

Consequence: two agents can consume the same accepted requirements and produce materially different frontends while both satisfying the current skill.

#### P0 — software application Design Profile does not require Interface Design

`profiles/software-application-design-v0.yaml` currently expects:

problem -> requirements -> domain -> architecture -> verification.

For a user-facing application this profile can report design completion without any canonical human-interface design.

The profile should either be made explicitly minimal/non-UI, or a user-facing application profile should add conditional Interface Design and downstream frontend Component/Test knowledge.

#### P1 — frontend Component Design guidance is generic

The existing Component Design skill is structurally sound, but frontend-specific failure modes are not called out:

- shared UI becoming an unbounded dependency hub;
- pages owning business semantics;
- server DTOs leaking directly into UI;
- global state used as default coordination;
- feature modules coupled through framework stores/routes;
- reusable visual primitives mixed with domain-specific interaction components.

A specialized frontend component-design analysis/skill may be justified if a pilot demonstrates repeatable value.

#### P1 — design-system knowledge has no dedicated reusable artifact procedure

Interface Design can own it, and Core does not need a new entity. However, Harness currently lacks a procedure that distinguishes:

- semantic interaction contracts;
- visual language/tokens;
- implementation-specific CSS/component mechanics.

Without this split, style decisions tend to be hidden in code or Figma-like projections and lose canonical traceability.

#### P1 — no explicit frontend target-state composition

Harness has the primitives to express frontend completeness but no reusable profile that composes them.

A user-facing frontend target state should be able to require, when applicable:

1. accepted product/user tasks;
2. accepted application journeys;
3. accepted human-interface interaction model;
4. accepted navigation/information architecture;
5. accepted frontend architecture;
6. accepted frontend component boundaries;
7. interface-quality closure;
8. frontend test design;
9. verification strategy;
10. implementation design.

## Atomicity test

### Should Harness add FRONTEND-DESIGN Authority?

No.

It fails atomicity because frontend work contains decisions with independent owners and lifecycles:

- user-visible behavior -> Product;
- journey/orchestration -> Application;
- interaction/navigation/presentation -> Interface;
- runtime/dependency/cache/rendering -> System Architecture;
- trust/session/admission -> Security;
- performance/accessibility targets -> Quality/Obligation;
- code-facing module/components -> Component Design;
- proof -> Test/Verification.

A generic FRONTEND-DESIGN Authority would become a technology silo.

### Should Interface Design be split?

Not yet.

Current evidence supports one Interface Design owner with several artifact kinds/capabilities. Interaction model, navigation model and visual-system decisions all concern the supported external human interface and are strongly coupled.

Split only if a real project demonstrates independently changing decision sets with different consumers and stable public contracts.

## Minimal proposed Harness extension

Do not change Core.

Add the following only at the agent/artifact/profile layer.

### A. New artifact skill: human-interface-design

Purpose: turn accepted product/application/domain/system constraints into canonical human-interface design.

Minimum output contract:

- surfaces/tasks;
- navigation/information architecture;
- screen/view model;
- user-visible state model;
- interaction/action semantics;
- loading/empty/error/partial/retry semantics;
- focus/keyboard/input behavior where applicable;
- responsive/adaptive rules where applicable;
- authorization-driven visibility/action behavior;
- semantic component/pattern inventory;
- unresolved Questions routed upstream.

This should be the main frontend semantic artifact skill.

### B. Optional artifact skill: design-system

Use only when a project has reusable visual-system decisions with independent downstream consumers.

Output can contain semantic tokens, typography, spacing, responsive primitives and supported component variants.

It remains owned by Interface Design.

### C. User-facing application Design Profile

Add a separate profile rather than making every software application require UI knowledge.

Suggested capability chain:

`problem -> requirements -> domain/application -> architecture -> human-interface -> interface-quality -> frontend-component-design -> test-design -> verification -> implementation-design`

Dependencies should remain a graph, not a forced stage machine.

### D. Frontend pilot before canonicalization

Validate on a real user-facing slice, preferably NAPMS, without treating its existing web code as authority.

Pilot input:

- canonical NAPMS requirements/domain/application/backend interface knowledge;
- existing accepted security/quality constraints;
- no reuse of current frontend implementation decisions unless independently canonical.

Pilot success condition:

A fresh agent can derive an implementation-ready frontend design and the resulting design can explain all material UI decisions without reading the existing frontend source.

Compare the blind design with the existing UI only after the design is complete, using differences to discover missing canonical knowledge rather than to copy implementation choices.

## Suggested pilot scope

Use one non-trivial end-to-end journey rather than the whole frontend.

A good candidate should include:

- list/search/filter state;
- detail state;
- create/edit action;
- validation/rejection;
- authorization-sensitive action;
- loading/empty/error behavior;
- navigation/back-context preservation.

The pilot should expose whether the proposed human-interface-design contract is sufficient before adding further specialization.

## Acceptance criteria for Harness frontend capability

Harness can be considered capable of frontend design when, for a user-facing slice:

1. target-state evaluation detects missing human-interface knowledge;
2. an agent can create that knowledge without reading implementation code as authority;
3. all material user-visible states/actions/navigation are explicit;
4. frontend technical architecture decisions are owned outside Interface Design where appropriate;
5. coding does not need to invent product-visible behavior, state semantics or major dependency structure;
6. accessibility/usability concerns are routed through existing quality analysis;
7. tests trace to accepted interaction semantics;
8. visual/design-system decisions are canonical when they are meant to constrain implementation;
9. unresolved upstream semantics become Questions;
10. two independent implementation agents can produce behaviorally equivalent frontends from the same accepted design while retaining private implementation freedom.

## Conclusion

Harness is structurally capable of supporting frontend design, but its current active layer is incomplete for doing so reliably.

The smallest useful change is:

- keep Core and Authority catalog unchanged;
- strengthen Interface Design through a dedicated `human-interface-design` artifact skill;
- add a user-facing application Design Profile;
- validate the model with a blind frontend-design pilot on one NAPMS journey;
- only then decide whether a separate design-system skill or frontend-specific Component Design guidance has demonstrated value.
