# Frontend Blind Pilot — Result

Status: research result / non-canonical  
Date: 2026-09-20

## Goal

Validate that Harness can extend its existing producer/consumer model to frontend design without Core changes, and that a blind agent can derive useful user-interface knowledge from accepted NAPMS upstream truth without reading prior UI design or frontend implementation.

## Structural experiment

Experimental Harness additions on the research branch:

- `user-journey-design` artifact skill under APPLICATION-DESIGN;
- `human-interface-design` artifact skill under INTERFACE-DESIGN;
- skill-registry routes for both kinds;
- `examples/frontend-blind-pilot/engineering-graph.yaml`;
- progressive Core realization snapshots;
- `validators/validate_frontend_blind_pilot.py`.

The graph deliberately reuses existing knowledge kinds for downstream work:

- frontend architecture -> `system-architecture`;
- frontend component design -> `component-design`;
- verification -> `verification-strategy`;
- executable UI contracts -> `test-design`;
- realization slicing -> `implementation-design`.

Expected CREATE progression:

1. user-journey-design;
2. human-interface-design;
3. system-architecture for frontend scope;
4. component-design + verification-strategy;
5. test-design;
6. implementation-design;
7. COMPLETE.

No Core, Engineering Graph, target-state or router semantic change is required.

## Blind semantic experiment

### Allowed NAPMS inputs

- first-MVP Product Requirements;
- first-MVP cross-context use case;
- module contracts;
- Security Architecture;
- Quality Requirements;
- HTTP contract requirements.

### Excluded until candidate completion

- `docs/contracts/ui/**`;
- `docs-legacy/ui/**`;
- `web/**`;
- frontend tests/screenshots;
- prior wireframes/prototypes.

Blind outputs:

- `candidate-user-journey.md`;
- `candidate-human-interface.md`.

## What the blind design recovered correctly

The blind candidate independently recovered the important semantic separation:

- Resource/Application/Business basis are preparation knowledge, not permission;
- request admission is distinct from permission decision;
- NotAllowed creates no authoritative current Rule;
- Allowed produces a stable current Rule;
- ACTIVE/INACTIVE is distinct from permission decision;
- export is distinct from request/decision/current Rule;
- COMPLETE vs UNRESOLVED export must remain explicit;
- loading/empty/unresolved/denied/failure states must not collapse;
- trusted actor/authority evidence is never authored by frontend fields;
- frontend should expose semantic references and provenance without becoming owner of business truth.

It also produced a usable task-oriented information architecture:

- Resources;
- Applications;
- Business Connectivity;
- Access Requests;
- Current Access;
- Policy Export.

This was obtained without reading prior UI artifacts.

## Comparison with existing NAPMS UI knowledge

### Equivalent or compatible decisions

Existing UI material independently confirms several blind decisions:

- human-readable semantics should lead while stable technical identifiers remain inspectable;
- Resource identity is stable independently from realization;
- business Need, permission/decision and current/effective policy are distinct;
- denied/unknown/technical failure states must remain distinguishable;
- browser-side hiding/disabling is presentation only; backend remains authoritative;
- current and historical truth must not be collapsed;
- normalized export is backend-produced and frontend must not reconstruct semantic truth.

This supports the proposed `human-interface-design` skill boundary.

### Accepted UI knowledge not derivable from selected canonical upstream

Legacy accepted Web UI direction contains additional UX/quality requirements:

- desktop-first control-plane interaction;
- WCAG 2.2 AA target;
- server-side paging/filter/search for potentially unbounded collections;
- explicit responsive bands;
- dense operational table/form bias;
- normal user journey described as responsibility/resource-centric;
- specific Connectivity/Checker-oriented navigation.

These were correctly absent from the blind candidate because they were not present in the selected current canonical upstream inputs.

Harness must not invent them.

If these decisions remain required for the current target, they need accepted canonical ownership and graph participation:

- supported user/task orientation -> Product/Application;
- accessibility conformance target -> Product/Obligation/Quality as applicable;
- paging/filter/search requirement -> Product/Interface/Quality depending on semantic reason;
- responsive/device support -> Product/Interface/Quality;
- visual density/layout policy -> Interface Design.

### Existing canonical UI pilot artifacts are narrower than full frontend closure

Current canonical graph contains:

- `MVP-UI-NAVIGATION`;
- `RESOURCE-DETAIL-UI`.

These are explicitly scoped to a Resource-history pilot and do not constitute whole-MVP frontend design.

Therefore Harness must support subject/slice-scoped frontend capabilities rather than treating one UI artifact as proof that the entire frontend is designed.

## Important finding: frontend completeness is consumer-specific

A backend implementation consumer does not need all human-interface capabilities.

A frontend implementation consumer does.

Therefore do not globally insert UI requirements into every application Design Profile.

Correct model:

- one Engineering Graph;
- different terminal Consumers;
- frontend Consumer recursively requires frontend-specific knowledge closure;
- shared Product/Domain/Security/API capabilities are reused.

This matches Harness architecture better than separate backend/frontend workflows.

## Required Harness changes if pilot is promoted

### P0

1. Add reusable `user-journey-design` skill.
2. Add reusable `human-interface-design` skill.
3. Register both knowledge kinds.
4. Provide a frontend/user-facing Engineering Graph example or consumer pattern.
5. Ensure a frontend consumer cannot be COMPLETE while human-interface knowledge is missing.

### P1

1. Integrate `human-interface-quality-analysis` into the frontend closure/acceptance model.
2. Define guidance for frontend-scoped System Architecture and Component Design.
3. Add a conditional design-system procedure only when reusable visual decisions have independent downstream value.
4. Add source/coverage checks so required UX constraints such as device/accessibility/paging policy cannot disappear between Product evidence and Interface Design.

### No change

- Harness Core;
- Authority/Artifact/Capability/Question primitives;
- Engineering Graph evaluator;
- target-state semantics;
- agent-router semantics;
- generic FRONTEND-DESIGN Authority.

## Questions exposed by the pilot

### Q1 — where should user journeys live?

The reference Authority catalog already assigns journeys to APPLICATION-DESIGN. The new dedicated journey skill is therefore a production specialization, not an Authority change.

Result: resolved by existing ownership.

### Q2 — should navigation/screens/states be separate capabilities?

Not by default.

They change together and share the same downstream Interface Design consumers in this pilot. One `human-interface-design` capability is the smallest useful unit.

Split only if another project shows independent lifecycle/consumers.

### Q3 — should design system be mandatory?

No.

The blind candidate was semantically implementation-ready without choosing typography, tokens or component library.

Design system becomes a separate Interface Design capability only when the project intentionally requires reusable visual constraints.

### Q4 — should Figma be canonical?

Tool choice is orthogonal.

A Figma artifact can be canonical only when the project explicitly assigns it Authority ownership and traceable versioned contract meaning. Otherwise it is a projection/review surface.

## Pilot verdict

The Harness architecture is compatible with frontend design.

The missing functionality is primarily **production knowledge**, not orchestration machinery.

The proposed minimal extension survives both tests:

1. structural producer/consumer decomposition;
2. blind semantic reconstruction from real NAPMS upstream truth.

The pilot also demonstrates an important safety property: Harness did not need to copy hidden decisions from the existing frontend. Missing UX requirements remained missing rather than being guessed.

## Next validation

Before canonicalization:

1. complete CI validation of the experimental graph/skills;
2. add interface-quality analysis to the experimental frontend closure;
3. run a second blind slice focused on Resource detail/history because NAPMS already has a narrow canonical UI contract suitable for exact comparison;
4. challenge the resulting closure with an implementation-agent review;
5. only then promote skills/reference guidance into main.


## Follow-up validation

### Second blind slice: Resource detail/history

A second blind reconstruction used Resource Catalogue use-case/domain semantics while excluding existing UI contracts.

It independently recovered the important canonical Resource-detail semantics:

- stable ResourceId workspace identity;
- current facts primary;
- explicit absence of current facts;
- history subordinate to Resource detail;
- loading/not-found/error separation;
- mutation refresh preserving current/history distinction;
- retry behavior;
- Resource/Site/responsibility semantics kept distinct from authority.

It deliberately did not invent exact route syntax or whether History is a tab/disclosure/inline region. Those are legitimate Interface Design choices rather than derivable domain truth.

Result: the `human-interface-design` boundary survives a second materially narrower slice.

### Human-interface quality integration

Accessibility/usability coverage does not require a new Authority or default persistent capability.

The existing `human-interface-quality-analysis` is now invoked by the experimental Human Interface Design procedure before semantic acceptance. Findings are routed to Product, Interface, Quality, Obligation and Verification/Test owners.

A persistent quality/conformance capability is justified only when a project has an independently consumed durable contract.

### Coding-boundary challenge

Attempting to continue from Human Interface Design into Frontend Architecture exposed a real missing upstream decision:

the accepted NAPMS backend security contract defines OIDC bearer-token validation, but does not define the browser-side authentication/session lifecycle needed by the separate Web Application.

Missing semantics include browser credential acquisition, refresh/re-authentication, storage boundary and logout/invalidation responsibility.

The pilot models this as a Question addressed to SECURITY-ARCHITECTURE which blocks the accepted Security Architecture artifact.

Harness then correctly reports the frontend target as BLOCKED and does not route downstream Frontend Architecture/Component/Test/Implementation work.

This validates frontend feedback routing with existing Core Question semantics.

### Executable validation

`validators/validate_frontend_blind_pilot.py` now verifies:

- CREATE frontier ordering from journey through implementation design;
- parallel Component Design + Verification frontier after frontend architecture;
- terminal COMPLETE state when the experimental closure is fully materialized;
- BLOCKED propagation for the browser-auth Security Architecture Question.

GitHub Actions `harness core` run 218 passed, including `make harness-check` and the frontend pilot validator.

## Updated promotion assessment

Evidence now supports promotion of the minimal frontend capability set:

- `user-journey-design` under APPLICATION-DESIGN;
- `human-interface-design` under INTERFACE-DESIGN;
- corresponding artifact-skill registry routes;
- frontend consumer/example guidance;
- frontend blind-pilot acceptance fixture.

Evidence still does not justify:

- FRONTEND-DESIGN/UI-DESIGN/UX-DESIGN Authority;
- frontend-specific Core entities;
- mandatory design-system capability;
- frontend-specific evaluator/router semantics;
- Figma-specific Core integration.

Before merging the research branch, the remaining review is mainly canonicalization hygiene: decide which experimental examples/research artifacts belong in the permanent repository and reduce the branch to the smallest durable change set.
