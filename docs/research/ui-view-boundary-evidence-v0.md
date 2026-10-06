# Research — Evidence for UI Screen/View Boundaries v0

Status: research evidence; non-normative.

## Purpose

Capture the evidence base for deciding semantic screen/view boundaries in complex
user-facing applications before wireframes or frontend implementation.

The concrete question is:

> Given accepted Task Model, User Journeys, Conceptual Interface, Information
> Architecture and Interaction Design, by what evidence-backed criteria should
> Interface Topology decide which views exist and which information/actions stay
> together inside a view?

This document does not change Harness behavior or canonical artifact contracts.
It supplies research evidence and provisional candidate rules for later
validation against real project topologies.

## Executive result

There is no defensible universal rule such as `one task = one screen`,
`one entity = one screen` or `one route = one view`.

A useful engineering model is:

> A view boundary is the presentation/navigation boundary of a coherent
> interaction context: a user goal or decision, the information that must remain
> available while pursuing it, the actions and working state involved, and the
> commit/recovery/mode semantics that make the context meaningfully continuous.

This is a synthesis, not terminology prescribed by one standard. It fits the
separation already present in Harness:

`Task -> Interaction Context -> Interface Topology -> Screen/View Composition`.

The strongest research-supported implication is narrower:

> Information participating in one mental operation, comparison or decision
> should not be separated in a way that forces avoidable recall, refinding or
> repeated context reconstruction.

That implication may justify one region, adjacent panes or one view. It does not
require one flat page.

## Evidence classes

This document distinguishes:

- **STANDARD** — ISO or comparable normative guidance;
- **EMPIRICAL** — experimental/observational evidence;
- **MODEL** — established theoretical/predictive model;
- **HEURISTIC** — mature practitioner guidance;
- **CONVENTION** — platform/design-system convention;
- **SYNTHESIS** — engineering rule inferred from several sources and requiring
  project validation.

Evidence strength is stated as STRONG, MODERATE or LIMITED relative to this
specific screen-boundary question.

## 1. Composition units are not interchangeable

Relevant concepts describe different dimensions:

| Dimension | Typical units | Responsibility |
|---|---|---|
| Intent | goal, user need | why the user acts |
| Activity | activity, task, subtask | what work is performed |
| Interaction | interaction context, sequence, decision/action cluster | how work proceeds |
| Domain | entity, value, relation | what the work is about |
| Presentation | view, region, pane, disclosure | what is presented together |
| Navigation | destination, route, history entry | where movement occurs |
| Operational state | mode, workspace, transaction | which interaction rules/state are active |

ISO 9241-115:2024 distinguishes task, interaction sequence and view rather than
defining a one-to-one mapping between them. This supports treating
task-to-view mapping as many-to-many.

**Evidence:** STANDARD, STRONG.

Consequences:

- one task may require several views;
- several tightly coupled subtasks may share one view;
- one domain entity may appear in several views;
- one view may combine data from several domain entities;
- one semantic relation may appear as adjacent panes on wide screens and
  sequential presentations on compact screens.

## 2. Co-location follows information dependency, not data ownership

Wickens and Carswell's Proximity Compatibility Principle argues that displays
supporting a common mental operation should have corresponding perceptual
proximity. Split-attention research similarly shows costs when users must
mentally integrate separated but mutually dependent information.

The transfer from instructional split-attention experiments to arbitrary
application UI is not exact, but the underlying evidence is strong enough to
treat simultaneous information dependency as a primary topology input.

**Candidate implication:**

If information items A and B are required for the same comparison, diagnosis,
selection or edit-with-feedback operation, separation across navigation
destinations requires positive justification.

**Evidence:** EMPIRICAL + MODEL, STRONG for comparison/integration tasks;
MODERATE for broad application generalization.

## 3. Recall and resumption costs matter at boundaries

Recognition-over-recall guidance is consistent with cognitive evidence that
users perform better when the interface supplies relevant cues instead of
requiring internal memory. Interruption/resumption research shows measurable
cost when users must reconstruct suspended task state, and external cues can
support resumption.

A navigation transition is not automatically equivalent to an interruption,
but a transition that hides required information, selection state or unfinished
intent creates an analogous reconstruction cost.

**Evidence:** EMPIRICAL + HEURISTIC, MODERATE-to-STRONG.

Boundary consequence:

Repeated `A -> B -> A` movement under one unchanged goal is a signal to inspect
whether A and B should become one view, adjacent panes, persistent context or a
local disclosure.

## 4. "One thing per page" is conditional guidance

GOV.UK recommends starting many transactional forms with one thing per page,
especially for unfamiliar, linear or branching interactions. The same guidance
explicitly allows grouping and notes that internal/expert systems may need
rapid repetition, switching or simultaneous visibility.

Baymard checkout research also shows that raw step count is a weak proxy for
user effort compared with the actual work required.

Therefore `one task per screen` is useful as a decomposition prompt, not as a
general invariant.

Good applicability:

- unfamiliar low-frequency transaction;
- wizard or branching questionnaire;
- focused data entry with validation/recovery;
- strong sequential dependency.

Poor applicability:

- comparison and diagnosis;
- exploratory planning;
- editing with continuous preview/context;
- monitoring;
- expert/high-frequency workflows;
- tasks with frequent bidirectional switching.

**Evidence:** HEURISTIC + domain EMPIRICAL evidence, STRONG for rejecting a
universal one-task/one-screen rule.

## 5. Entity-centric UI is conditionally valid

Entity-centric composition is justified when the entity is itself a durable
user task object with recognizable identity, lifecycle, revisit/deep-link value,
history and a coherent family of actions.

It is suspicious when the topology mirrors REST resources, aggregates,
database tables or bounded contexts while representative user decisions span
several of them.

GOV.UK service guidance explicitly warns against allowing organizational or
technical structure to determine the service presented to the user. ISO
human-centred interaction principles similarly prioritize suitability for the
user's task and context.

**Candidate implication:**

Backend/domain boundaries are valid data/behavior ownership boundaries, but are
not sufficient evidence for a user-visible view boundary.

**Evidence:** STANDARD + HEURISTIC, STRONG.

A task-specific UI read/projection may legitimately aggregate several domain
entities without changing domain ownership.

## 6. Progressive disclosure separates secondary complexity, not critical context

Progressive disclosure is useful when advanced, rare or conditional information
would otherwise compete with the primary task.

It becomes harmful when the hidden content is repeatedly required for the
current decision, or when users must alternate continuously between the primary
surface and the disclosed content.

**Evidence:** HEURISTIC, MODERATE-to-STRONG.

## 7. Modal interaction is a semantic interruption

Fluent and Apple platform guidance treat dialogs/sheets/popovers as scoped
interaction surfaces with different interruption and context-preservation
semantics.

A modal is appropriate for a short scoped decision, confirmation or blocking
subtask. It is a poor substitute for a durable workspace or long exploratory
workflow, especially when the user must repeatedly consult the parent context.

**Evidence:** CONVENTION + HEURISTIC, MODERATE.

## 8. Responsive transformation should preserve semantic relationships

Material/Android canonical layouts demonstrate list-detail and supporting-pane
relationships that can be simultaneous on larger viewports and sequential on
compact viewports.

This supports separating semantic topology from physical layout: viewport size
may alter presentation topology without necessarily changing the underlying
interaction relationship.

**Evidence:** CONVENTION, MODERATE.

## Working model: Interaction Context

For topology analysis, treat an Interaction Context as a compact description of:

- current goal/subgoal or decision;
- required information;
- primary actions;
- transient working state that should survive local interaction;
- mode/role/authorization semantics when material;
- commit/cancel/recovery semantics;
- entry/exit conditions.

Harness already asks Interaction Design to partition work into coherent
interaction contexts before final screen boundaries. The research therefore
does not justify a new process entity by itself.

A **Decision Context** is a useful specialization for analysis: the alternatives,
constraints, evidence and actions that must be jointly available to make one
decision. It should remain analytical vocabulary unless project evidence shows
a need for a separate canonical type.

## Information dependency levels

A lightweight analysis scale can make topology decisions reviewable:

| Level | Meaning | Typical topology implication |
|---|---|---|
| D3 — simultaneous | information must be compared/combined at once | same view; often adjacent regions/panes |
| D2 — persistent | information should remain visible through the operation | persistent region/pane/context summary |
| D1 — retrievable | information is occasionally needed with low retrieval cost | local disclosure/detail is sufficient |
| D0 — independent | information is not needed to continue the current work | separate destination is acceptable |

This D0-D3 scale is SYNTHESIS. It is intentionally non-normative until tested
against representative project topologies.

## Keep-together / separate criteria

| Factor | Prefer together | Prefer separate |
|---|---|---|
| Goal/decision | same immediate outcome | independently meaningful outcome |
| Information dependency | D2/D3 dependency | D0/D1 dependency |
| Task cohesion | actions operate on one working context | actions are weakly related |
| Sequence | frequent A-B-A switching | rare one-way transition |
| Working state | shared transient selection/edit state | independent resumable state |
| Recall/refinding | separation requires memory/refinding | transition loses no needed context |
| Commit/recovery | one commit/recovery unit | distinct transaction/recovery semantics |
| Mode/role | same operational rules | material mode/authority change |
| Disclosure | secondary/conditional content | primary content with independent lifecycle |
| Addressability | meaningful only relative to parent | independently linkable/revisitable |
| Visual competition | information is jointly used | integration creates unrelated competition |

No individual row is sufficient by itself. Topology is a trade-off between the
cost of separation and the cost of integration.

## Primitive selection matrix

| Primitive | Use when | Strong warning sign |
|---|---|---|
| Region in one view | content is D2/D3 and continuously relevant | region has independent lifecycle and little joint use |
| Supporting/split pane | secondary context must remain observable with primary work | panes are actually independent destinations |
| Inline disclosure | local optional/advanced information | hidden content is required for task completion |
| Popover | small contextual, nonessential support | essential context or long task |
| Detail view | object has durable identity/revisit value | detail exists only to support the parent decision |
| Modal/dialog/sheet | short scoped interruption/confirmation | long exploration or repeated parent consultation |
| Separate view | new interaction context or resumable stage | boundary exists only because backend data is separate |
| Navigation destination | place needs durable independent identity | transient state of the current action |
| Workspace/mode | long-lived activity with stable toolset/context | simple linear transaction |

## Topology audit method

### 1. Interaction Context Inventory

For every material context record:

- trigger;
- goal/subgoal;
- central decision/action;
- D3 simultaneous information;
- D2 persistent information;
- working state;
- primary actions;
- commit boundary;
- recovery/back semantics;
- role/mode;
- completion/exit.

### 2. Task / Decision -> Interaction Context -> View coverage matrix

For each scenario step or material decision, record:

- owning interaction context;
- primary view responsibility;
- supporting views/regions;
- transition boundary;
- commit/recovery boundary.

Look for:

- no primary owner;
- multiple competing primary owners;
- one view owning unrelated primary decisions;
- repeated transitions between views belonging to one context.

### 3. Information Dependency Matrix

For every material decision:

`Decision -> required information -> semantic/domain source -> D0-D3 -> UI location`.

A D3 decision whose inputs are spread across independent destinations is a
high-priority review finding.

### 4. Boundary Walkthrough

At every proposed view transition ask:

1. Does the user goal change?
2. Which required information disappears?
3. Which working state must survive?
4. What must now be remembered?
5. Is the destination predictable from available information scent?
6. Did mode/role/authorization semantics change?
7. Did commit/recovery semantics change?
8. Can the user resume/back out without reconstructing work?
9. What user problem is solved by this boundary?

If the only answer to (9) is "different entity/API/table/component", the
boundary is not justified yet.

### 5. Context-switch analysis

Flag transitions combining:

- unchanged goal;
- high transition frequency;
- high refinding/resumption cost;
- hidden transient state;
- no meaningful commit/mode boundary.

These are strong merge/pane candidates.

## Merge and split signals

### Two views are merge/pane candidates when

- they support the same primary decision;
- a D3 dependency crosses the boundary;
- representative flow repeatedly alternates between them;
- users must transfer values through memory;
- they share one transient working state;
- commit occurs only after working with both;
- one of them has little independent revisit value.

### One view is a split/disclosure candidate when

- it owns multiple independently describable primary responsibilities;
- information for one responsibility is noise for the other;
- a responsibility is rare/advanced/conditional;
- responsibilities have different commit/recovery semantics;
- role/mode changes materially;
- one part needs independent deep-link/resumption semantics;
- competing action sets obscure the current work.

## Provisional candidate rules

These are **research candidates only**. They do not modify the current Harness
skill/output contracts.

### P0 candidates

- **VB-01 — User-semantic responsibility.** Every task view should state its
  responsibility as user goal/decision + required information + result, not only
  as a domain entity label.
- **VB-02 — Required-at-once completeness.** D3 information for the primary
  decision should be simultaneously accessible without cross-destination recall.
- **VB-03 — Persistent context.** D2 information should remain available while
  the operation that depends on it continues.
- **VB-04 — Explicit operational boundary.** Material mode, role, authorization,
  commit or destructive-consequence changes should be perceptible.
- **VB-05 — Recoverability.** Back/cancel/resume semantics and transient-state
  preservation should be explicit at material navigation boundaries.

### P1 candidates

- **VB-06 — Responsibility cohesion.** A task view should own one coherent
  interaction responsibility or be explicitly identified as a workspace/frame.
- **VB-07 — No competing semantic ownership.** One primary user decision should
  not have multiple uncoordinated primary views.
- **VB-08 — Context-switch review.** Repeated A-B-A movement under one goal
  should trigger merge/pane/persistent-context analysis.
- **VB-09 — No implementation-shaped boundary.** Entity, aggregate, table,
  endpoint, service or bounded-context separation is insufficient by itself to
  justify a view.
- **VB-10 — Progressive separation.** Rare/advanced/conditional content should
  be a disclosure/detail candidate when it is not required by the primary
  decision.
- **VB-11 — Independent destination test.** A standalone view should have a
  distinct goal, revisit/deep-link value, resumable state, commit boundary or
  operational mode that makes it independently meaningful.

### P2 candidates

- **VB-12 — Adaptive semantic preservation.** Responsive variants should
  preserve material semantic relationships even when panes become sequential
  presentations.
- **VB-13 — Expert-efficiency check.** High-frequency/expert workflows should
  explicitly review the cost of micro-screen decomposition.
- **VB-14 — Cognitive-dimensions review.** Material topology should be inspectable
  for visibility/juxtaposability, hidden dependencies, hard mental operations,
  premature commitment and viscosity.

## Relationship to current Harness

Current responsibilities already align with most of the research:

- `interaction-design` partitions USER work into coherent interaction contexts
  without final screen boundaries;
- `interface-topology-design` defines the view/context inventory, primary
  responsibility and navigation continuity;
- `screen-view-design` owns local regions, hierarchy, patterns, variants and
  responsive transformations;
- `docs/design/ui-design-convergence-v0.md` already proposes evidence-backed UI
  Decision Rules rather than universal UI laws.

The current unresolved question is narrower:

> Which of the candidate boundary criteria above are stable enough to become
> reusable UI Decision Rules and/or acceptance checks in Interaction/Topology
> procedures?

This research does **not** yet justify:

- a new Authority;
- a new Core entity;
- a new knowledge kind;
- a new mandatory Interaction Context Mapping artifact;
- adding D0-D3 to project truth;
- changing Screen/View or Interface Topology skill contracts.

## Validation plan before promotion

Use an existing real project's accepted `VIEW-*` topology as the first
validation corpus.

1. Map representative Task/Decision -> Interaction Context -> VIEW.
2. Build the Information Dependency Matrix.
3. Run the Boundary Walkthrough across representative scenarios.
4. Classify each view as keep / merge / split / region / disclosure / workspace
   candidate.
5. Compare findings with independently reviewable user/task evidence.
6. Record false positives: candidate rules that would force worse topology.
7. Record missing discriminators: cases where the framework cannot decide.
8. Promote only rules that improve decisions across more than one materially
   different interaction shape or have sufficiently direct external evidence.

A candidate should remain guidance rather than a normative acceptance check when
reasonable products can violate it without creating a demonstrated user/task
failure.

## Sources and evidence basis

Primary sources:

- ISO 9241-115:2024, *Guidance on conceptual design, user-system interaction
  design, user interface design, and navigation design*:
  https://www.iso.org/obp/ui/#iso:std:iso:9241:-115:ed-1:v1:en
  — STANDARD, STRONG.
- ISO 9241-210:2019, *Human-centred design for interactive systems*:
  https://www.iso.org/standard/77520.html
  — STANDARD, STRONG for process/context; indirect for exact screen boundaries.
- ISO 9241-110, interaction principles:
  https://www.iso.org/obp/ui/#iso:std:iso:9241:-110
  — STANDARD, STRONG for task suitability; indirect for topology mechanics.
- Wickens & Carswell, Proximity Compatibility Principle:
  https://doi.org/10.1518/001872095779049408
  — EMPIRICAL/MODEL, STRONG for information integration and display proximity.
- Chandler & Sweller, split-attention / cognitive-load work:
  https://doi.org/10.1111/j.2044-8279.1992.tb01017.x
  — EMPIRICAL, STRONG in instructional integration; MODERATE transfer to
  arbitrary application UI.
- Pirolli, *Information Foraging Theory*:
  https://academic.oup.com/book/7603
  — MODEL/EMPIRICAL program, MODERATE-to-STRONG for navigation/refinding costs.
- Wharton et al., Cognitive Walkthrough:
  https://www.colorado.edu/ics/sites/default/files/attached-files/93-07.pdf
  — METHOD/MODEL, STRONG as an analytical evaluation procedure.
- Blackwell & Green, Cognitive Dimensions framework:
  https://www.cl.cam.ac.uk/~afb21/CognitiveDimensions/CDtutorial.pdf
  — MODEL/HEURISTIC, MODERATE for structural inspection.
- Nielsen Norman Group, usability heuristics:
  https://www.nngroup.com/articles/ten-usability-heuristics/
  — HEURISTIC, MODERATE.
- Nielsen Norman Group, progressive disclosure:
  https://www.nngroup.com/articles/progressive-disclosure/
  — HEURISTIC, MODERATE.
- GOV.UK Service Manual, structuring forms:
  https://www.gov.uk/service-manual/design/form-structure
  — HEURISTIC/PRACTITIONER CONVENTION, STRONG for government transactional
  services; conditional outside that context.
- GOV.UK Service Manual, services for government users:
  https://www.gov.uk/service-manual/design/services-for-government-users
  — HEURISTIC, useful counterexample to universal one-thing-per-page.
- GOV.UK Service Manual, scoping a service:
  https://www.gov.uk/service-manual/design/scoping-your-service
  — HEURISTIC, STRONG against organization/technology-driven user structure.
- Baymard, checkout flow/form-field research:
  https://baymard.com/research-articles/checkout-flow-average-form-fields
  — EMPIRICAL, STRONG within ecommerce checkout; LIMITED as a universal rule.
- Android/Material canonical layouts:
  https://developer.android.com/develop/ui/views/layout/canonical-layouts
  — PLATFORM CONVENTION, MODERATE.
- Microsoft Fluent, dialog/popover guidance:
  https://fluent2.microsoft.design/components/web/react/core/dialog/usage
  https://fluent2.microsoft.design/components/web/react/core/popover/usage
  — PLATFORM CONVENTION/HEURISTIC, MODERATE.
- Apple Human Interface Guidelines, split views:
  https://developer.apple.com/design/human-interface-guidelines/split-views
  — PLATFORM CONVENTION, MODERATE.

## Research limitations

- There is no single experimental literature that directly yields a universal
  algorithm from task models to application screen inventories.
- Several evidence streams address narrower mechanisms such as visual
  integration, interruption, forms or navigation and must be composed with
  judgement.
- Platform design systems encode conventions and ecosystem expectations, not
  universal HCI laws.
- Domain-specific evidence, especially ecommerce forms, must not be generalized
  without checking the interaction shape.
- The D0-D3 scale, primitive matrix, merge/split signals and VB-* rules are
  SYNTHESIS and require project validation before canonicalization.

## Related Harness material

- `skills/artifacts/interaction-design/SKILL.md`
- `skills/artifacts/interface-topology-design/SKILL.md`
- `skills/artifacts/screen-view-design/SKILL.md`
- `docs/design/ui-design-convergence-v0.md`
- `docs/design/frontend-design-v0.md`
- `docs/audit/harness-evolution-radar.md`
