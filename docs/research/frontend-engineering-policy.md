# Research — Frontend Engineering Policy for agent-guided UI design

Status: research candidate; not canonical Harness Core semantics.

## Question

Which established UI/UX rules, heuristics and standards are useful for Harness to steer an engineering agent toward sound frontend design without turning subjective design taste into universal Core rules?

## Research conclusion

Harness should not adopt one universal "frontend Clean Architecture" checklist.

The useful model is layered:

1. **Project Engineering Policy** — selected cross-cutting interaction/design obligations that downstream Interface/Component/Implementation Design must obey.
2. **Human Interface Quality Analysis** — reusable heuristic coverage lens that finds omissions and routes them to the owning Authority.
3. **Obligation/Quality contracts** — only where a project explicitly adopts a standard/conformance level or measurable quality target.
4. **Verification/Test Design** — executable evidence for the accepted interface/policy obligations.

No new UI/UX/Accessibility Authority or Core entity is justified.

## Sources reviewed

Primary:
- Nielsen Norman Group — 10 Usability Heuristics for User Interface Design.
- W3C/WAI — WCAG 2.2 and Understanding documents.
- U.S. Web Design System — Design Principles and Accessibility guidance.

Supporting design heuristics considered:
- Gestalt grouping/hierarchy principles;
- Fitts's Law;
- Hick-Hyman choice-complexity principle;
- progressive disclosure;
- recognition over recall;
- task-centered/user-centered design;
- design-system reuse/continuity.

These supporting heuristics are useful as reasoning lenses but are not project requirements by themselves.

## Classification

### A. Strong default analysis lenses

These should be applied to user-facing Human Interface Design even when the project does not create a durable named policy capability.

#### A1. Task-first / user-goal-first design

Rule:
- derive views and navigation from accepted user goals/journeys;
- do not mirror backend modules, database tables or CRUD resources unless that structure is also natural for the task.

Why Harness:
- this directly protects the APPLICATION-DESIGN -> INTERFACE-DESIGN boundary;
- it prevents coding agents from treating an API/resource catalogue as an information architecture.

Owner:
- journey semantics: APPLICATION-DESIGN;
- resulting information architecture: INTERFACE-DESIGN.

Agent check:
- for every top-level workspace/view, identify the journey/task it serves;
- if no accepted task justifies it, treat it as suspect.

#### A2. Visibility of system state and explicit state design

Rule:
- every material asynchronous/action state has an explicit user-visible semantic state;
- loading, empty, submitting, success, validation rejection, authorization rejection, conflict/stale, unavailable, not-found and recoverable failure remain distinct when their meanings differ upstream.

Why Harness:
- this is a particularly strong fit because Harness already models failure semantics and upstream outcome ownership;
- it prevents transport codes or incidental spinner/error handling from becoming UI semantics.

Owner:
- semantic outcomes: upstream Product/Domain/Application/Security;
- visible mapping: INTERFACE-DESIGN;
- proof: VERIFICATION/TEST-DESIGN.

#### A3. Match the interface to accepted domain language

Rule:
- prefer user/domain concepts over storage/API/framework terminology;
- do not expose transport status, DTO names or internal lifecycle labels as product meaning.

Why Harness:
- preserves DDD/application ownership through the presentation boundary.

Owner:
- terminology/meaning: Product/Domain;
- presentation wording/grouping: INTERFACE-DESIGN.

#### A4. User control, reversibility and safe destructive actions

Rule:
- where upstream semantics permit cancellation/retry/reversal, expose it clearly;
- irreversible/destructive operations require sufficient consequence visibility and safeguards;
- do not invent undo when the domain does not support it.

Owner:
- reversibility semantics: Product/Domain/Application;
- confirmation/cancellation interaction: INTERFACE-DESIGN.

#### A5. Error prevention before error reporting

Rule:
- constrain invalid choices using accepted knowledge when possible;
- use selection/discovery instead of requiring users to recall opaque identifiers;
- preserve authoritative server validation;
- present errors at the level the user can act on.

Why Harness:
- catches a common agent failure: generating generic forms from DTO schemas.

Owner:
- validity: Domain/Application;
- prevention/presentation: INTERFACE-DESIGN;
- verification: TEST-DESIGN.

#### A6. Recognition over recall

Rule:
- do not make users remember stable IDs, prior values, valid reference choices or hidden state when the accepted system can present them;
- expose identifiers progressively when operationally useful, rather than making them the primary interaction vocabulary.

Use:
- default heuristic, not absolute law.

#### A7. Consistency and continuity

Rule:
- equivalent actions/states use consistent labels, placement patterns and interaction semantics within one product;
- reuse accepted project design-system patterns before inventing local variants;
- consistency must not erase domain distinctions.

Use:
- good Engineering Policy candidate where multiple screens/features share a frontend.

### B. Accessibility rules with strong executable value

Accessibility should remain a cross-Authority concern.

A project may:
- adopt WCAG 2.2 AA (or another level) as an explicit obligation/quality contract; or
- accept narrower accessibility expectations without claiming formal conformance.

High-value agent obligations:
- complete keyboard operability for supported actions;
- visible and non-obscured focus;
- logical focus order after navigation/dialog/action;
- semantic names/roles/labels;
- status changes announced without requiring visual observation;
- no color-only meaning;
- sufficient target size/spacing where the selected conformance contract requires it;
- responsive/reflow behavior that preserves meaning and operability;
- errors identified and associated with actionable input;
- consistent navigation/identification.

Important:
- automated accessibility tools are evidence only, not complete proof;
- claiming WCAG conformance requires project acceptance of the conformance obligation and appropriate verification.

### C. Layout/composition heuristics

These are useful while deriving wireframes/layout but should not become universal pass/fail rules.

#### C1. Gestalt grouping

Use proximity, similarity and visual hierarchy so semantically related information/actions form visible groups.

Harness translation:
- each layout group should correspond to a coherent task/state/concept;
- visual grouping must not imply a domain relationship that does not exist.

#### C2. Progressive disclosure

Primary task/current state should dominate; secondary diagnostics, provenance/history and rare operations may be progressively exposed when doing so does not hide information required for safe decisions.

Harness translation:
- classify information as task-critical, decision-supporting or secondary;
- preserve user access to provenance/technical detail where required.

#### C3. Fitts-oriented target design

Frequent/important actions should not be unnecessarily difficult to activate.

Do not encode Fitts's Law formula as a Harness acceptance gate.
Use concrete accessibility target-size requirements when the project adopts them.

#### C4. Hick-oriented choice management

Avoid presenting large undifferentiated choice sets where search/filter/grouping or staged selection can reflect the accepted task.

Do not set arbitrary maximum choice counts.

#### C5. Visual hierarchy from task priority

Wireframe hierarchy should follow:
1. user goal/current context;
2. primary current state/information;
3. primary next action;
4. decision-supporting details;
5. secondary/history/provenance/advanced actions.

This is a useful agent construction rule, not independent business truth.

### D. Useful only when selected by project context

#### Design system

Create a durable design-system capability only when shared visual/presentation decisions have independent consumers/lifecycle.

Otherwise:
- local reusable components/tokens remain implementation mechanics;
- do not make Atomic Design, Storybook or a specific component library mandatory.

#### Responsive design

Require only the platforms/viewports accepted by Product/Quality/Interface Design.

Do not automatically invent mobile-first or desktop-first requirements.

#### User research / usability testing

Real user evidence is valuable and USWDS explicitly recommends designing from real user needs and prototypes.

Harness rule:
- agents may synthesize accepted research evidence;
- agents must not invent user-research findings;
- missing material user evidence can become a Product/Discovery Question or a Verification activity, depending on scope.

#### Prototypes/wireframes

Use wireframes when spatial composition materially constrains implementation or reduces coding-agent freedom.

They remain INTERFACE-DESIGN artifacts/projections.

A wireframe may be canonical when the project explicitly treats layout/composition decisions as accepted interface semantics.

Do not require Figma.

## Rules that should NOT become universal Harness policy

### Miller's "7 +/- 2"

Do not use as a numeric UI acceptance rule.
It is commonly overgeneralized from working-memory research and is not a sound universal menu/form limit.

Use the broader principle: reduce unnecessary cognitive load and externalize information users would otherwise need to remember.

### Jakob's Law

Useful reminder to prefer familiar interaction patterns, but too context-dependent for an acceptance gate.

Translate to:
- prefer established platform/product conventions unless the task gives a reason to differ;
- never let familiarity override accepted domain semantics.

### Material Design / Apple HIG / USWDS component rules

Use only when the project selects the corresponding platform/design system.

Their higher-level principles can inform analysis, but vendor-specific component/layout rules are not universal Harness semantics.

### Atomic Design

Possible implementation/design-system organization technique, not a general product/interface requirement.

### Universal SPA/global-state/component architecture prescriptions

These belong to Frontend System Architecture/Component Design after upstream semantics are accepted.

## Recommended Harness integration

### 1. Keep Core unchanged

No new Core entity or Authority.

### 2. Strengthen human-interface-quality-analysis

Use a fixed analysis matrix with these concern families:

- task/goal alignment;
- system-state visibility;
- domain-language match;
- user control/reversibility;
- consistency/continuity;
- error prevention/recovery;
- recognition vs recall;
- cognitive/choice complexity;
- information grouping/hierarchy;
- progressive disclosure;
- keyboard/focus;
- semantic labels/roles/status;
- non-visual equivalence/no color-only meaning;
- pointer/target interaction;
- responsive/reflow;
- authentication/authorization-sensitive interaction.

Each finding routes to Product, Application, Interface, Quality, Obligation, Security, Verification or Test Design.

### 3. Add layout/wireframe derivation to Human Interface Design

After task/state semantics are accepted:

1. identify primary task and current context;
2. rank information/actions by task importance;
3. group semantically related information/actions;
4. decide persistent vs progressively disclosed content;
5. place primary action/state where it remains discoverable;
6. sketch relevant states, not only the happy-path loaded state;
7. verify keyboard/focus/read order does not contradict spatial layout;
8. keep pixels/style tokens/framework mechanics unconstrained unless project policy owns them.

### 4. Support project-native frontend Engineering Policy

A project can select obligations such as:

- task-first IA;
- explicit UI state model;
- domain language over DTO terminology;
- recognition over recall;
- error prevention;
- continuity/reuse;
- progressive disclosure;
- accessibility baseline or formal WCAG target.

The existing engineering-policy knowledge kind is sufficient.

### 5. Make Test Design consume accepted policy/interface obligations

Where accepted, derive executable tests for:

- every required state mapping;
- keyboard reachability/focus restoration;
- status announcements;
- error association and recovery;
- authorization-sensitive actions;
- responsive/reflow invariants;
- destructive-action safeguards;
- key navigation/journey completion.

Avoid snapshot/visual-regression tests as semantic truth unless a visual invariant is intentionally canonical.

## Suggested default agent behavior

When no explicit frontend Engineering Policy exists, the agent should:

1. apply the reusable analysis lenses;
2. not silently turn a heuristic into a project requirement;
3. flag material missing decisions;
4. propose the smallest project-native policy only when downstream design needs durable constraints;
5. continue with implementation freedom where multiple UI realizations satisfy accepted semantics.

## Validation against NAPMS/Nutrition

The proposed matrix explains failures already observed:

- NAPMS: browser authentication lifecycle is an upstream Security gap; state/authorization analysis finds it before component design.
- NAPMS: Resource current/history layout follows task priority + progressive disclosure without requiring a special UI Authority.
- Nutrition: result states such as mapped_complete/partial/no-plan/technical failure require explicit state visibility and domain-language mapping.
- Nutrition: Product/Market/Household list/detail/edit patterns require recognition over recall and discovery rather than raw identifier entry.

No observed case requires a new Harness Core concept.

## Canonicalization recommendation

Recommended to promote:
- the analysis matrix into `human-interface-quality-analysis`;
- layout/wireframe derivation rules into `human-interface-design`;
- frontend examples into `engineering-policy`;
- frontend-specific Test Design examples into `test-design`.

Do not promote:
- named heuristic laws as universal hard requirements;
- arbitrary cognitive-load numbers;
- a mandatory design system/framework;
- a new UI/UX Authority;
- mandatory Figma/prototype artifacts.

