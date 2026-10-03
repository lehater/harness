# Evidence-Driven UI Design Convergence v0

Status: experimental design.

## Purpose

Define how Harness turns accepted user/task/interface semantics into justified UI decisions without treating the first plausible screen composition as production authority.

The mechanism narrows the admissible UI design space by combining:

- accepted upstream semantics and obligations;
- reusable evidence-backed UI decision rules;
- the existing Decision Exploration / Decision Governance pipeline;
- analytical and executable evaluation;
- representative-user evidence only where the remaining uncertainty is genuinely empirical.

The result is not a new UI generator. It is an assurance mechanism for answering:

> Why is this UI decision sufficiently justified to stop exploring and allow production-facing frontend design to continue?

## Concrete consumer failure

Prep demonstrates the failure this design addresses.

Its current frontend chain is structurally complete from Product Capability through Task, Journey, Interaction, Topology, Screen/View and Machine Interface, yet the project audit explicitly concludes PROTOTYPE_READY_PRODUCTION_UX_NOT_VALIDATED.

Specific examples:

- Information Architecture marks material findability assumptions VALIDATE while downstream screen and presentation decisions already exist.
- Presentation System selects a mixed spatial/non-spatial Knowledge representation before representative task evidence has established which representation should be the default.
- A coded Knowledge prototype and a 3D capability spike exist, but the representative-user validation pack still contains unexecuted validation obligations.
- Structural completeness therefore cannot be used as proof that the production UI is good.

This is a concrete consumer failure, so an application-layer convergence/readiness projection is justified. No Core extension is required.

## Boundary

This design does not add:

- a new Authority;
- a Stage or workflow entity;
- a Core Gate/Approval/Readiness entity;
- a generic UX score;
- a new canonical prototype artifact kind;
- a parallel design-rationale authority.

HUMAN-INTERFACE-DESIGN remains the owner of interface semantics.

Decision Exploration and Decision Governance remain the generic mechanism for material alternatives.

Prototype code, screenshots, measurements and user-study records are evidence/projections unless a target project explicitly grants them canonical semantic ownership.

UI DESIGN READY is a derived assurance disposition above Core. It may later be required by a user-facing production Consumer, but it is not stored as Core truth.

## Quality model

Harness should not flatten UI quality into one scalar.

Use four distinct classes.

### Outcome qualities

These describe whether the interface works for the intended people and tasks:

- effectiveness / task success;
- efficiency / effort and time where material;
- recoverability and error safety;
- accessibility;
- comprehensibility;
- learnability where repeated use matters;
- satisfaction;
- appropriate confidence and trust.

### Design mechanisms

These are means, not final objectives:

- information scent;
- recognition support;
- feedback and visibility of state;
- predictability and consistency;
- visual hierarchy;
- information grouping and density;
- context preservation;
- orientation;
- progressive disclosure;
- target size and movement constraints;
- semantic and keyboard equivalence.

A mechanism is useful only when its expected effect matches the task/context.

### Observable measures

Examples:

- task completion;
- error count/type;
- time-on-task;
- navigation/backtracking;
- first action / first click;
- abandonment;
- assistance required.

### Subjective measures

Examples:

- perceived workload;
- confidence;
- trust;
- satisfaction;
- perceived clarity;
- aesthetic impression.

Subjective measures cannot replace task performance, and task performance cannot answer all subjective questions.

## Evidence dimensions

Evidence is not one linear hierarchy. Harness should track three independent dimensions.

### Semantic authority

Determines what the UI is allowed or required to mean:

Product / Task / Domain / Application / Security / Interface semantics / applicable obligations.

Representative-user preference cannot authorize a product action that upstream semantics do not provide.

### General design evidence

Determines which design consequences are reasonable under stated conditions:

- accessibility standards and applicable platform requirements;
- replicated/direct HCI evidence;
- predictive human-performance models;
- mature interaction conventions;
- heuristics;
- expert opinion.

Popular heuristics remain heuristics unless their applicability and evidence justify a stronger status.

### Project-local empirical evidence

Determines whether the chosen design works for this product population and task:

- analytical inspection;
- executable prototype evidence;
- representative-user task evidence;
- production behavioral evidence.

Project-local evidence does not rewrite upstream product/domain semantics; it can trigger their re-examination through the normal ownership model when it exposes a mismatch.

## UI Decision Rule catalog

The first reusable addition should be a catalog, not a new project Authority.

Conceptual location:

catalogs/ui/decision-rules-v0.yaml

Minimum rule shape:

    id: UI-RULE-...
    question: material decision the rule helps resolve
    observable_predicates:
      - task/context facts that must be true
    consequence:
      preferred: [...]
      allowed: [...]
      disallowed: [...]
    applicability:
      requires: [...]
      excludes: [...]
    exceptions:
      - condition and consequence
    evidence:
      class: STANDARD | EMPIRICAL | MODEL | CONVENTION | HEURISTIC | EXPERT
      strength: STRONG | MODERATE | WEAK
      sources: [...]
    project_validation:
      required_when: [...]
      suggested_method: ...
    freedom_remaining: [...]

Rules are conditional decision knowledge, not global UI laws.

Example classes:

- symbolic exact-value comparison -> comparative tabular/list representation becomes a strong candidate;
- topology/relationship orientation -> relationship visualization may become a candidate;
- task-critical pointer interaction -> equivalent keyboard/semantic access is required when applicable;
- destructive/high-cost action -> explicit prevention/recovery strategy is required;
- large or performance-sensitive visualization -> degradation must preserve task-complete semantic access.

A rule must state what it leaves undecided. Harness must not pretend that a rule selecting a representation family also determines exact layout, typography or component structure.

## Material UI Decision evidence

Presentation System and Screen/View Design should be able to attach evidence to consequential decisions without introducing another canonical owner.

Conceptual record:

    decision_id:
    subject:
    question:
    materiality:
    input_facts:
    applied_rules:
    candidate_alternatives:
    eliminated:
      - alternative
        reason
        evidence_refs
    selected:
    selection_basis:
    residual_uncertainty:
    required_evaluation:
    evidence_refs:
    disposition: DETERMINED | DELEGATED | EMPIRICAL_VALIDATION_REQUIRED

DETERMINED means constraints/evidence leave one viable alternative.

DELEGATED uses existing Decision Governance when several same-Authority alternatives remain and policy permits a choice.

EMPIRICAL_VALIDATION_REQUIRED means semantic reasoning cannot distinguish the remaining alternatives reliably. It must not be converted into random agent preference.

## Systematic exploration

The UI specialization of the existing decision pipeline is:

    accepted Task / Journey / Concept / IA / Interaction / Topology
      -> discover material UI decision points
      -> derive observable task/context predicates
      -> apply hard semantic / obligation constraints
      -> apply relevant UI Decision Rules
      -> construct only admissible alternative classes
      -> eliminate alternatives with evidence
      -> one viable alternative: DETERMINED
      -> multiple viable alternatives: existing Decision Exploration / Governance
      -> unresolved empirical discriminator: targeted prototype/evaluation
      -> update evidence
      -> convergence disposition

Alternatives are generated only for an actual open decision axis.

The mechanism must not generate several whole screens that vary multiple unrelated dimensions merely to avoid design fixation.

Design-fixation evidence supports deliberate exploration, but parallel alternatives are useful only when they challenge a material unresolved decision.

## Evaluation ladder

Choose the cheapest evidence capable of discriminating the open decision.

### E0 — structural / deterministic

Examples:

- task-to-view/action/state traceability;
- impossible state detection;
- missing semantics;
- policy/standards checks;
- automated accessibility checks;
- responsive/state fixture completeness.

### E1 — analytical

Examples:

- heuristic evaluation;
- cognitive walkthrough;
- consistency inspection;
- task-based inspection;
- information-scent review;
- predictive-model checks where assumptions hold.

Evaluator judgement is useful signal, not an oracle.

### E2 — executable prototype

Examples:

- deterministic fixtures;
- interaction stories;
- keyboard/focus checks;
- state transitions;
- responsive viewport matrix;
- screenshot/state evidence;
- accessibility tooling plus required manual checks;
- performance/degradation behavior.

Prototype fidelity is selected from the question being tested. A visual-hierarchy question needs realistic presentation; a navigation question may need only a skeletal interaction; a runtime/performance question requires executable approximation.

### E3 — representative-user task evidence

Use only when the unresolved variable depends on actual user comprehension, mental model, findability, workload, trust, preference conditioned on performance, or similar empirical behavior.

The user performs a task. The user is not asked to design the UI.

### E4 — production behavioral evidence

Post-release evidence may re-open accepted UI decisions when real behavior contradicts assumptions. It is not a prerequisite for initial implementation unless the project explicitly requires it.

## Accessibility

Applicable accessibility requirements are constraints, not optional UX preference.

Automated tools provide partial evidence only. Manual/human judgement remains necessary for criteria and usability aspects that automation cannot establish.

Task-critical direct manipulation may supplement named/semantic/keyboard-operable actions but cannot silently become the only path where applicable requirements demand equivalence.

## Prototype-as-code

Harness may use:

    canonical UI semantics
      -> generated/scaffolded HTML/React
      -> deterministic fixtures
      -> Storybook or equivalent interaction surfaces
      -> Playwright/browser checks
      -> screenshots/states/traces
      -> evaluation evidence

The prototype remains evidence/projection.

It becomes production structure only through the normal production Consumer closure and downstream Frontend Architecture / Component / Implementation design.

## UI DESIGN READY

UI DESIGN READY is a derived assurance projection, not a Core entity.

Conceptual output:

    subject:
    ui_design_ready: true | false
    blocking_findings:
    residual_uncertainty:
    material_decisions:
    evaluation_coverage:
    evidence_refs:

A subject is ready when all of the following hold for its declared risk/task scope:

1. Critical USER tasks have a UI/non-UI disposition.
2. Actions, information, states and recovery trace to accepted semantics.
3. No material UI capability is introduced only by a component/template/provider.
4. Applicable accessibility obligations have sufficient evidence.
5. Every material presentation/composition decision has an explicit basis.
6. No unresolved alternative remains merely because the agent stopped exploring.
7. Critical interaction/recovery paths have executable evidence when execution is material.
8. Empirical uncertainty that can materially change task success or meaning has the required representative-user evidence.
9. Prototype behavior does not contradict accepted Screen/View and Presentation contracts.
10. Remaining freedom is explicitly classified as controlled freedom or ordinary implementation detail.

UI DESIGN READY does not mean universal usability. It means the declared production design scope has no known unresolved material design uncertainty beyond explicitly accepted residual risk.

## Downstream blocking

The initial implementation should avoid adding a new Core capability merely to represent readiness.

Instead:

- semantic design remains represented by existing capabilities;
- convergence evidence is consumed by an assurance/evaluator layer;
- a user-facing production Consumer may require a successful convergence result before claiming production implementation readiness;
- failed convergence does not erase accepted semantic design; it records why production continuation is unjustified.

If implementation proves that the Engineering Graph cannot express this consumer constraint without semantic duplication, that concrete failure may justify a later graph-level contract extension.

## Relationship to existing Harness mechanisms

- Decision Governance owns how alternatives are explored and chosen.
- human-interface-quality-analysis owns usability/accessibility concern coverage and routing.
- presentation-system-design owns shared presentation semantics.
- screen-view-design owns concrete view composition semantics.
- verification-strategy and test-design own project proof obligations.
- Harness Assurance Policy owns evidence-selection principles.
- this design composes those mechanisms for UI convergence; it does not replace them.

## Evidence basis

Primary/strong references used for this design:

- ISO 9241-11:2018, Usability: Definitions and concepts:
  https://www.iso.org/standard/63500.html
- ISO 9241-210:2019, Human-centred design for interactive systems:
  https://www.iso.org/standard/77520.html
- W3C WCAG 2.2:
  https://www.w3.org/TR/WCAG22/
- W3C guidance on evaluation tools and the need for human judgement:
  https://www.w3.org/WAI/test-evaluate/tools/selecting/
- Vessey, Cognitive Fit: A Theory-Based Analysis of the Graphs Versus Tables Literature:
  https://doi.org/10.1111/j.1540-5915.1991.tb00344.x
- Jansson & Smith, Design fixation:
  https://doi.org/10.1016/0142-694X(91)90003-F
- Dow et al., Parallel prototyping leads to better design results, more divergence, and increased self-efficacy:
  https://doi.org/10.1145/1879831.1879836
- Hertzum & Jacobsen, The Evaluator Effect:
  https://doi.org/10.1207/S15327590IJHC1304_05

## Initial implementation sequence

P0:
- establish this design and the Prep pilot as the accepted architecture direction;
- define a machine-readable UI Decision Rule catalog schema;
- define material-decision evidence accepted by Presentation System / Screen View procedures;
- add a convergence evaluator with deterministic checks for fields that are structurally decidable.

P1:
- integrate UI decision axes with existing Decision Governance;
- integrate executable prototype evidence from Verification/Test surfaces;
- support E3 evidence obligations without pretending they are deterministic checks.

P2:
- add reusable rule content incrementally from independently justified evidence;
- add production-behavior feedback only for consumers that need it.

Do not introduce a universal UI DSL or a generic UX score.
