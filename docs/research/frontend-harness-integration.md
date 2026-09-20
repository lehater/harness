# Frontend Design Integration into Harness

Status: research result, not canonicalized  
Date: 2026-09-20

## Research question

Can the current Harness producer/consumer model drive user-interface and frontend design from accepted requirements to implementation-ready knowledge without introducing a parallel frontend workflow or breaking Core semantics?

## Result

Yes.

The current Harness Core and Engineering Graph are structurally sufficient.

Frontend design should be represented as an additional branch of the existing engineering-knowledge graph:

- existing Authorities retain their semantic ownership;
- new frontend-specific capabilities describe missing accepted knowledge;
- reusable artifact skills produce those capabilities;
- production prerequisites establish safe ordering;
- the target frontend implementation Consumer recursively obtains the required closure;
- unresolved semantics use the existing Question mechanism;
- Design Profile remains a derived view of the graph.

No frontend-specific Core entity, Stage, workflow engine or generic FRONTEND-DESIGN Authority is required.

The current gap is in the active agent layer: Harness has the ownership boundaries, but not enough frontend-oriented production contracts and skills to reliably materialize them.

## 1. Why frontend must fit the existing Harness model

Harness models engineering knowledge, not methodology stages.

Therefore the intended model is not:

```
BACKEND PROCESS
FRONTEND PROCESS
SECURITY PROCESS
TEST PROCESS
```

It is one producer/consumer graph in which different implementation consumers require different knowledge closures.

For example:

```
                      PRODUCT REQUIREMENTS
                              |
                  DOMAIN / APPLICATION SEMANTICS
                              |
                  +-----------+-----------+
                  |                       |
          BACKEND INTERFACES        USER JOURNEYS
                                          |
                                HUMAN INTERFACE DESIGN
                                          |
                                FRONTEND ARCHITECTURE
                                          |
                               FRONTEND COMPONENT DESIGN
                                          |
                  +-----------------------+------------------+
                  |                                          |
            VERIFICATION                                TEST DESIGN
                  +-----------------------+------------------+
                                          |
                              IMPLEMENTATION DESIGN
                                          |
                              FRONTEND IMPLEMENTATION
```

This is a dependency graph, not a mandatory sequential project process.

## 2. Existing Authorities are sufficient

### PRODUCT-REQUIREMENTS

Owns:

- target users/actors;
- accepted outcomes;
- externally observable product behavior;
- scope;
- product-visible constraints;
- acceptance expectations.

Frontend consequences are downstream projections of this truth.

### DOMAIN / DOMAIN-USE-CASE

Owns:

- domain language;
- domain states and invariants;
- use-case outcomes;
- business rejection semantics.

UI must represent these semantics, not reinterpret them.

### APPLICATION-DESIGN

Owns:

- application-level composition;
- user/system journeys;
- cross-capability orchestration;
- externally meaningful application outcomes.

The current Authority catalog already states that Application Design owns journeys.

### INTERFACE-DESIGN

Owns the supported human interaction boundary:

- interaction semantics;
- information architecture;
- navigation;
- views/screens;
- UI states;
- transitions;
- semantic interaction patterns;
- presentation conventions;
- design-system decisions when they are canonical externally observable constraints.

This remains one Authority unless a real project later demonstrates independent ownership boundaries.

### SYSTEM-ARCHITECTURE

Owns frontend technical/runtime structure:

- browser/mobile/desktop runtime boundary;
- rendering topology;
- deployment boundary;
- frontend module topology when architectural;
- client/server responsibility;
- state/cache ownership when architectural;
- interaction with backend/runtime services.

### SECURITY-ARCHITECTURE

Owns frontend-relevant trust constraints:

- authentication/session boundary;
- trusted identity;
- admission/enforcement structure;
- protected data constraints;
- browser-origin/session protection where applicable.

It does not own whether a business action is allowed; Product/Domain owns that semantic policy.

### QUALITY-DESIGN

Owns measurable architecture-significant constraints:

- interaction latency targets;
- frontend resource/performance constraints;
- availability/degradation requirements;
- explicitly accepted accessibility/usability quality constraints when measurable.

### COMPONENT-DESIGN

Owns code-facing frontend decomposition:

- feature/page/component responsibilities;
- frontend ports/adapters;
- state ownership;
- dependency direction;
- shared component boundaries;
- mapping between API/application models and view models.

### VERIFICATION-DESIGN

Owns what evidence proves the frontend realizes accepted knowledge.

### TEST-DESIGN

Owns executable frontend behavioral contracts before concrete test code.

### IMPLEMENTATION-DESIGN

Owns realization slices after the upstream frontend knowledge is accepted.

## 3. Current Harness gaps

### P0 — User Journey capability is not explicit in the active execution layer

The Authority catalog says Application Design may own journeys, but the current `application-design` skill is primarily operation-oriented:

- commands;
- queries;
- materializations;
- orchestration;
- consistency/outcomes.

It does not reliably force formation of a user-task/journey model.

Consequence:

an agent can move from Product Requirements toward Interface Design without a canonical task-oriented interaction context.

### Required correction

Add a reusable knowledge kind such as:

`user-journey-design`

owned by APPLICATION-DESIGN.

A project-specific capability may look like:

`napms.frontend.user-journeys`

The reusable skill should produce:

- actor;
- user goal;
- entry condition;
- meaningful interaction sequence;
- decision/alternate paths;
- failure/recovery paths;
- completion condition;
- externally visible side effects.

It must explicitly state that a journey is not a screen flow.

---

### P0 — Human interface production is currently too generic

The existing `interface-contract` skill correctly supports human interfaces in principle, but its contract is designed to cover HTTP, CLI, files and UI through one generic procedure.

That is insufficient for a non-trivial GUI.

A coding agent can still be forced to invent:

- information architecture;
- navigation;
- screen/view boundaries;
- UI state model;
- state transitions;
- loading/empty/error/conflict states;
- focus/keyboard behavior;
- responsive behavior;
- semantic UI patterns.

### Required correction

Add a dedicated knowledge kind:

`human-interface-design`

owned by INTERFACE-DESIGN.

This is not a new Authority.

A project-specific capability may be:

`napms.frontend.human-interface`

The artifact procedure should consume accepted user journeys and product/domain/application semantics and produce a canonical human-interface model.

---

### P0 — Current default software application profile can complete without UI knowledge

`profiles/software-application-design-v0.yaml` requires only:

`problem -> requirements -> domain -> architecture -> verification`.

For a user-facing application this can report COMPLETE even when no user journey, human-interface design, frontend architecture or frontend component design exists.

### Required correction

Do not make all software applications require GUI design.

Add a separate user-facing/frontend target policy or Engineering Graph consumer.

Examples:

- `FRONTEND-IMPLEMENTATION`;
- `USER-FACING-APPLICATION-IMPLEMENTATION`.

The Engineering Graph should be the primary policy owner where available; a Design Profile is derived from it.

---

### P1 — Frontend technical architecture is not specialized, but the existing System Architecture boundary is adequate

No new Authority is required.

The existing `system-architecture` skill can already operate on a frontend-scoped capability, provided its production contract has the correct inputs.

Candidate capability:

`project.frontend.architecture`

Possible prerequisites:

- accepted product requirements;
- accepted application/user journeys;
- accepted human-interface design;
- applicable quality/security architecture.

This lets architecture decide technical realization after user-visible semantics exist.

A separate `frontend-architecture` knowledge kind should be introduced only if pilots show that the generic system-architecture procedure repeatedly misses frontend-specific decisions.

---

### P1 — Frontend Component Design needs a scoped contract

The existing `component-design` skill is suitable structurally.

A frontend-scoped capability can reuse it:

`project.frontend.component-design`

with prerequisites such as:

- human-interface design;
- frontend architecture;
- backend/machine interface contracts;
- engineering policy;
- optional design-system constraints.

A specialized frontend component skill is not initially necessary.

Pilot evidence should determine whether generic Component Design repeatedly misses frontend-specific concerns.

---

### P1 — Human-interface quality analysis is not integrated into routing

Harness already contains:

`skills/artifacts/human-interface-quality-analysis/SKILL.md`

but it is not currently registered in `skills/artifact-skill-registry-v0.yaml`.

The skill intentionally performs cross-Authority accessibility/usability coverage and routes findings to their semantic owners.

This is conceptually correct.

Open design question:

whether interface-quality coverage needs a persistent independently consumed capability, or whether the analysis should be invoked as part of semantic acceptance/verification for human-interface design.

Do not add a new Accessibility or Usability Authority merely to make routing convenient.

Validate this in the frontend pilot.

## 4. Proposed minimum production graph

The minimal frontend-capable graph can be represented with existing Engineering Graph semantics.

Illustrative capabilities:

```yaml
APPLICATION-DESIGN:
  produces:
    - capability: app.user-journeys
      knowledge_kind: user-journey-design
      requires:
        - app.requirements
        - app.domain-use-cases

INTERFACE-DESIGN:
  produces:
    - capability: app.human-interface
      knowledge_kind: human-interface-design
      requires:
        - app.requirements
        - app.user-journeys
        - app.domain-use-cases

SYSTEM-ARCHITECTURE:
  produces:
    - capability: app.frontend-architecture
      knowledge_kind: system-architecture
      requires:
        - app.human-interface
        - app.quality-constraints
        - app.security-architecture

COMPONENT-DESIGN:
  produces:
    - capability: app.frontend-component-design
      knowledge_kind: component-design
      requires:
        - app.human-interface
        - app.frontend-architecture
        - app.backend-interface-contract

VERIFICATION-DESIGN:
  produces:
    - capability: app.frontend-verification
      knowledge_kind: verification-strategy
      requires:
        - app.requirements
        - app.human-interface
        - app.frontend-architecture

TEST-DESIGN:
  produces:
    - capability: app.frontend-test-design
      knowledge_kind: test-design
      requires:
        - app.frontend-verification
        - app.human-interface

IMPLEMENTATION-DESIGN:
  produces:
    - capability: app.frontend-implementation-design
      knowledge_kind: implementation-design
      requires:
        - app.frontend-component-design
        - app.frontend-test-design
        - app.frontend-verification

consumers:
  - id: FRONTEND-IMPLEMENTATION
    requires:
      - app.frontend-implementation-design
```

This is illustrative, not a universal mandatory graph.

Projects can omit or merge capabilities when the knowledge has no independent value.

## 5. Why this graph does not break Harness

### Core remains unchanged

All required semantics already exist:

- Authority;
- CapabilityId;
- CanonicalArtifact;
- dependencies;
- Question;
- blocking.

### Engineering Graph remains unchanged

The frontend branch uses ordinary production contracts.

No new evaluator semantics are required.

### Agent Router remains unchanged

`agent_router.py` already routes any production with a registered `knowledge_kind`.

Required additions are registry entries/skills, not router behavior.

### Design Profile remains unchanged

A frontend consumer recursively derives the required Design Profile.

No frontend-specific status or stage is needed.

### Questions remain unchanged

Examples:

- journey cannot decide an outcome -> Question to Product/Domain;
- interface cannot decide whether an action is allowed -> Question to Product/Domain;
- interface needs unresolved identity/session behavior -> Question to Security Architecture;
- frontend architecture needs an absent latency/resource target -> Question to Quality;
- Component Design discovers incompatible API semantics -> Question to Interface/Application owner.

The same feedback model used for backend, security and tests applies.

## 6. Artifact boundary proposal

### user-journey-design

Owner: APPLICATION-DESIGN.

Purpose:

materialize task-oriented application interaction before screen decisions.

Inputs:

- requirements;
- domain/use cases;
- roles/entitlements where accepted.

Outputs:

- actors;
- goals;
- entry/exit conditions;
- meaningful user/system steps;
- alternate/failure/recovery paths;
- visible side effects.

Stops on missing product/domain/application semantics.

### human-interface-design

Owner: INTERFACE-DESIGN.

Purpose:

materialize the supported human interface from accepted journeys.

Inputs:

- requirements;
- journeys;
- domain/application outcomes;
- applicable security constraints;
- platform/channel constraints already accepted.

Outputs:

- information architecture;
- navigation model;
- views/screens;
- view purpose;
- actions;
- UI states;
- state transitions;
- validation/error/recovery representation;
- semantic interaction patterns;
- focus/keyboard/input semantics where applicable;
- responsive/adaptive rules where applicable;
- authorization-sensitive visibility behavior;
- unresolved Questions.

This artifact should explicitly preserve implementation freedom:

- React/Vue/Svelte component structure;
- CSS mechanics;
- private hooks/helpers;
- state library;
- exact pixel values unless canonical design-system constraints require them.

### design-system (conditional)

Owner: INTERFACE-DESIGN.

Do not make mandatory.

Use when reusable presentation decisions have independent downstream value.

Possible output:

- semantic color roles;
- typography hierarchy;
- spacing/sizing tokens;
- focus/error/success roles;
- layout primitives;
- motion rules;
- supported visual variants.

A Figma file, token file or another representation can materialize this capability if the project makes it canonical and traceable.

## 7. Frontend security integration

Frontend design must consume security decisions but must not move security ownership into UI.

Examples:

### Product/Domain owns

- who may invoke an action;
- which information may be visible by business policy.

### Security Architecture owns

- trusted identity/session;
- authentication boundary;
- admission/enforcement structure;
- protected credential/session mechanics.

### Interface Design owns

- how denied/unavailable actions are represented;
- whether an action is hidden, disabled or shown with an explanatory rejection, subject to accepted product/security semantics;
- secure interaction constraints visible to the user.

### Component/System owns

- implementation placement;
- routing guards;
- API adapters;
- browser/session integration.

Security Analysis can inspect the resulting frontend branch and route gaps exactly as it already does for backend/system design.

## 8. Frontend Test Design integration

Frontend Test Design naturally extends the already canonical Test Design model.

A frontend test contract may refine:

- journey;
- UI state transition;
- interaction pattern;
- navigation;
- permission-sensitive behavior;
- validation/recovery;
- keyboard/focus behavior;
- backend-outcome -> UI-state mapping.

Example semantic test contract:

```
precondition:
  user is viewing editable entity in Loaded state

operation:
  submit invalid change

oracle:
  entity remains unchanged;
  view enters ValidationError;
  field-specific accepted rejection is visible;
  focus/recovery behavior follows accepted interface contract
```

Concrete Playwright/Vitest/Testing Library mechanics remain test implementation.

This is exactly analogous to backend Test Design: executable oracles are derived from accepted semantics, not invented by tests.

## 9. Visual/UI tooling boundary

Harness should remain tool-neutral.

Possible tools/artifacts:

- Figma;
- Storybook;
- design-token files;
- state diagrams;
- flow diagrams;
- prototypes.

They fall into two categories.

### Canonical

A tool artifact may be canonical when the project deliberately assigns it Authority ownership, versioning and downstream contract meaning.

### Projection

Otherwise it is a generated/review visualization of canonical Harness/project knowledge.

This distinction prevents screenshots/Figma frames from silently becoming an untracked second source of product truth.

## 10. Recommended frontend consumer closure

For a non-trivial user-facing implementation, the implementation consumer should be unable to become COMPLETE while material frontend decisions remain absent.

Approximate closure:

```
Problem / Evidence
      |
Product Requirements
      |
Domain Use Cases
      |
User Journey Design
      |
Human Interface Design
      |
+-----+--------------------------+
|                                |
Interface Quality          Frontend Architecture
|                                |
+----------------+---------------+
                 |
      Frontend Component Design
                 |
          Verification Design
                 |
             Test Design
                 |
       Implementation Design
                 |
       FRONTEND IMPLEMENTATION
```

Security, Quality, backend Interface and Engineering Policy attach as prerequisites where applicable.

The exact graph should remain project-specific.

## 11. Applicability discipline

Not every application needs every frontend artifact.

### Simple UI

A trivial administrative form may merge:

- user journey;
- human-interface design;
- design-system decisions

into one Interface/Application artifact if no independent consumers/lifecycles exist.

### Non-trivial product UI

Explicit capabilities are justified when coding would otherwise invent:

- navigation;
- state transitions;
- error/recovery;
- responsive behavior;
- shared interaction patterns;
- frontend architecture;
- component boundaries.

Harness should use the same atomicity/consumer-failure rule already used for Security and Test Design.

## 12. Validation strategy

Do not canonicalize based only on this research.

Use a blind pilot on NAPMS.

### Input

Allow the frontend-design agent to read:

- accepted problem/requirements;
- accepted domain/use-case/application knowledge;
- accepted backend interface contracts;
- accepted architecture/security/quality constraints.

Do not use current `web/**` implementation as design authority.

Existing frontend code may be examined only after the blind design is complete.

### Pilot target

Select one non-trivial user journey containing:

- collection/list;
- search/filter;
- detail;
- create/edit action;
- validation;
- rejection/failure;
- authorization-sensitive behavior;
- navigation/back-context;
- loading/empty/error states.

### Harness execution

1. add candidate production contracts to an experimental project Engineering Graph;
2. route `user-journey-design`;
3. route `human-interface-design`;
4. reuse System Architecture for frontend architecture;
5. reuse Component Design for frontend code structure;
6. apply human-interface quality analysis;
7. derive Verification/Test Design;
8. derive Implementation Design;
9. challenge the closure with a fresh coding-agent review.

### Success criteria

The experiment succeeds if:

1. no Core/evaluator/router change is needed;
2. target state exposes the correct first CREATE frontier;
3. each downstream frontend capability remains PENDING until its real prerequisites exist;
4. unresolved product/security/domain facts become Questions;
5. a fresh coding agent can implement the selected journey without inventing user-visible semantics;
6. the coding agent does not need to invent major frontend module/state/dependency structure;
7. UI tests can derive their oracles solely from accepted design;
8. accessibility/usability analysis can route gaps without taking semantic ownership;
9. comparison with existing NAPMS frontend finds differences as either implementation choices or missing canonical decisions, not hidden prerequisites required by Harness;
10. FRONTEND-IMPLEMENTATION becomes COMPLETE only when the full selected knowledge closure exists.

## 13. Canonicalization candidates after pilot

If the pilot succeeds, the likely Harness changes are small.

### Add

- `skills/artifacts/user-journey-design/SKILL.md`;
- `skills/artifacts/human-interface-design/SKILL.md`;
- corresponding entries in `artifact-skill-registry-v0.yaml`;
- a reusable user-facing/frontend Engineering Graph example/profile;
- agent-layer validation for the new skills.

### Possibly add after evidence

- `design-system` skill;
- frontend-specific Component Design guidance;
- persistent interface-quality coverage capability.

### Do not add without new evidence

- FRONTEND-DESIGN Authority;
- UI/UX Core entities;
- Screen/Route/Component as Core entities;
- workflow stages;
- Figma-specific Core integration;
- frontend-specific target-state semantics.

## Conclusion

Harness can support frontend design using the same architectural idea that already proved useful for backend, Security and Test Design.

The necessary change is not a second frontend methodology inside Harness.

It is to make previously implicit frontend engineering knowledge explicit in the existing producer/consumer graph:

`Requirements -> User Journeys -> Human Interface Design -> Frontend Architecture -> Frontend Component Design -> Verification/Test -> Implementation Design`.

The strongest immediate gaps are two reusable production procedures:

1. `user-journey-design` under APPLICATION-DESIGN;
2. `human-interface-design` under INTERFACE-DESIGN.

Everything downstream can initially reuse existing System Architecture, Component Design, Verification, Test Design and Implementation Design mechanics.

The correct next validation is a blind NAPMS frontend journey pilot before canonicalizing these additions.
