# UI Design Convergence v0 — Prep VIEW-KNOWLEDGE Pilot

Status: known-project pilot evidence.

## Purpose

Exercise Evidence-Driven UI Design Convergence against one real vertical slice:

Prep TASK-U-EXPLORE-KNOWLEDGE
-> J-KNOWLEDGE-ORIENTATION
-> IX-KNOWLEDGE
-> VIEW-KNOWLEDGE
-> Presentation / executable prototype evidence.

This pilot tests whether the mechanism reduces design freedom using accepted semantics and evidence rather than selecting a preferred visual form by taste.

It does not change Prep canonical product/interface truth.

## Pinned inputs

Harness main examined at:

0fde383ab2c33f83ac851ec4f9bb12da51391c0a

Prep main examined at:

bccc614d393f40ce9fb97ff6e8b9eb26eabbd961

Primary Prep inputs:

- docs/application/task-model.yaml
- docs/application/user-journeys.md
- docs/interface/information-architecture.yaml
- docs/interface/interaction-design.yaml
- docs/interface/interface-topology.yaml
- docs/interface/presentation-system.md
- docs/interface/screen-view-design.md
- experiments/knowledge_representation/**
- experiments/frontend_design_assurance_audit/**

## Step 1 — upstream task facts

TASK-U-EXPLORE-KNOWLEDGE requires the learner to:

- orient within Subject Knowledge relevant to active target/focus;
- inspect meaningful relation meaning/direction;
- narrow or expand semantic scope;
- move between overview and detail;
- select Knowledge;
- preserve Knowledge identity independently of learner state, target, capability and presentation;
- retain task-complete semantic access if a richer visualization is unavailable/unusable.

The Task Model explicitly states that no graph, 2D/3D representation, route, page, modal, component or layout is required.

J-KNOWLEDGE-ORIENTATION repeats that representation choice is downstream and does not require graph, list, 2D or 3D.

Therefore a spatial graph cannot be derived directly from the task.

## Step 2 — accepted interaction/topology constraints

IX-KNOWLEDGE requires:

- query knowledge;
- narrow/expand scope;
- select knowledge;
- follow meaningful relation;
- move between overview/detail;
- loading/empty/ready/selected/unavailable states;
- non-spatial keyboard-operable task-critical path.

VIEW-KNOWLEDGE currently defines:

- query controls;
- task-complete non-spatial results;
- optional relationship overview;
- selected detail;
- degradation preserving query/results/detail and relation meaning.

These are strong constraints. They still leave a real material representation decision open.

## Step 3 — material decision points

### KD-01 — primary representation for semantic inspection

Question:

What representation should carry task-complete concept lookup, exact concept metadata and inspectable relation meaning?

Predicates:

- the user consumes symbolic labels, relation predicates and exact descriptive text;
- exact identity and meaning must remain inspectable;
- search/query and bounded results are required;
- density may reach at least tens/hundreds of concepts.

Evidence rule:

Cognitive-fit evidence supports structured symbolic representation for symbolic/exact-value tasks.

Disposition:

DETERMINED at representation-family level.

Selected family:

query + structured list/table/result set + selected detail.

Remaining freedom:

exact list/table/card presentation, density and layout remain open unless another decision resolves them.

### KD-02 — role of relationship visualization

Question:

Should a spatial relationship visualization exist and, if so, should it be primary/default?

Predicates:

- relationship orientation is a real task;
- relation meaning/direction matters;
- task can be completed non-spatially;
- actual frequency and importance of topology-oriented subtasks are not established by current Task Model;
- actual representative-user benefit of spatial overview is not established.

Disposition:

EMPIRICAL_VALIDATION_REQUIRED.

Reason:

Upstream semantics justify relationship inspection, not a specific spatial representation or default prominence.

### KD-03 — 2D versus 3D spatial representation

Question:

If a spatial overview is useful, which spatial form is justified?

Predicates:

- existing prototype evidence demonstrates 3D technical feasibility and stress behavior;
- current Presentation System prefers a 2D relationship overview;
- the representative-user assurance pack explicitly requires comparison of 3D and non-spatial task performance;
- no executed representative-user result was found that discriminates the alternatives.

Disposition:

EMPIRICAL_VALIDATION_REQUIRED.

The current 2D-default / 3D-experimental policy is a reasonable risk-reducing interim constraint, but it is not evidence that 2D is the empirically best production default for Prep.

### KD-04 — task-critical accessibility path

Question:

Can the Knowledge task depend on direct graph manipulation?

Predicates:

- required task-critical functions include query, select, traverse/inspect relation and move between overview/detail;
- current accepted interface semantics explicitly require a non-spatial keyboard-operable path.

Disposition:

DETERMINED.

A graph may supplement but may not become the only task-complete interaction path.

### KD-05 — degradation under scale/performance pressure

Question:

What may be removed when the spatial renderer becomes costly or unusable?

Predicates:

- semantic access must survive richer-visualization failure;
- current prototype contains 250/1000-node stress fixtures;
- current Presentation System treats spatial visualization as presentation state.

Disposition:

DETERMINED at semantic level.

Allowed degradation:

reduce/omit spatial richness while preserving query/results/detail and relationship semantics.

Renderer-specific optimization remains implementation/evidence work.

## Step 4 — executable evidence found

### R0 structured KnowledgeWorkspace

The existing Storybook workspace provides deterministic executable evidence for:

- initial structured overview;
- search results;
- search-to-focus transition;
- selection without silent focus mutation;
- focused local context;
- relation filters;
- 48-row and 144-row structured density fixtures.

The implementation exposes semantic headings, regions, table/list structures and explicit detail.

This is strong E2 evidence that a non-spatial task-complete candidate can be implemented and exercised.

It does not prove representative-user comprehension.

### R2 3D capability spike

The existing R2 stories provide executable evidence for:

- search to focus;
- hover-neighbor relation exposure;
- orbit/camera controls;
- relation filtering;
- renderer settings;
- 250/1000-node deterministic stress fixtures;
- instanced/batched renderer variants;
- Knowledge Graph snapshot integration.

The experiment README correctly states that headless Storybook checks do not prove WebGL performance and that manual hardware-accelerated checks are required.

This is useful E2 feasibility/interaction evidence.

It does not establish that 3D improves the Prep user task.

## Step 5 — evidence-based elimination

Rejected as production default:

- 3D-only Knowledge interaction;
  reason: violates accepted task-complete non-spatial path and lacks representative task evidence.

Rejected:

- graph coordinates/geometry as Knowledge truth;
  reason: conflicts with accepted semantic boundary.

Rejected:

- random selection among list/cards/2D/3D based on agent preference;
  reason: KD-01 is partly determined by task properties and KD-02/KD-03 require explicit empirical discrimination.

Retained:

- structured query/results/detail as task-complete baseline;
- optional relationship visualization as a candidate for orientation;
- spatial form/default prominence as unresolved empirical decision.

## Step 6 — evaluation coverage

E0 structural:

PASS for the examined slice.

Task, Journey, Interaction, Topology and Screen/View references exist and agree on the representation-independent semantic obligations.

E1 analytical:

PASS with one material unresolved decision.

No semantic reason was found to make spatial visualization task-critical. A symbolic baseline is justified. Spatial-default value remains empirical.

E2 executable:

PASS for prototype-validation readiness.

Both structured and spatial prototype evidence exist. Storybook interaction coverage demonstrates substantial contract realizability.

E3 representative user:

NOT SATISFIED.

The existing Representative-User Design Assurance Pack defines a Knowledge comparison scenario, but the current repository evidence examined here contains the protocol/template, not completed representative-user results closing the decision.

## Pilot convergence result

    subject: PREP / VIEW-KNOWLEDGE
    semantic_design_complete: true
    prototype_validation_ready: true
    executable_candidate_evidence: true
    representative_user_evidence_required: true
    representative_user_evidence_complete: false
    ui_design_ready_for_production: false

Blocking material uncertainty:

- whether relationship visualization materially improves the representative learner's orientation tasks;
- which representation should be the production default/prominence for those tasks;
- whether current labels/grouping satisfy representative-user findability/comprehension assumptions.

## What the pilot proves

The mechanism does not need to invent several arbitrary full-screen designs.

It was able to:

1. derive a task-complete symbolic representation family from task properties plus accepted semantics;
2. prove that direct graph manipulation cannot become the only task path;
3. preserve a relationship-visualization option only for the subtask that can justify it;
4. reuse existing executable prototype evidence instead of generating a new prototype merely for process compliance;
5. stop at the exact point where project-local human evidence is required;
6. distinguish prototype-valid from production-UI-ready.

This is the intended convergence behavior.

## Consequence for Prep

No canonical Prep artifact should be rewritten from this Harness pilot alone.

The next project action, when Prep resumes UI validation, is to execute the already-defined representative-user Knowledge task comparison and feed the findings back through the owning interface artifacts.

If task evidence shows that a spatial overview is not useful, Presentation System / Screen View should remove or demote it.

If evidence shows a reliable task benefit, the accepted contract may promote the appropriate spatial pattern with a bounded rationale.

If representative users reveal a Task/IA/Concept mismatch, the correction must be routed upstream rather than patched in presentation code.

## Consequence for Harness implementation

This pilot supports implementing the minimum v0 mechanism as:

- UI Decision Rule catalog;
- material UI decision evidence fields;
- convergence evaluator;
- integration with existing Decision Governance and human-interface-quality-analysis.

It does not support adding a new UX Authority, a UI workflow stage, or a global UX score.
