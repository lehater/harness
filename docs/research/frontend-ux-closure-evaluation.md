# Evaluation — granular frontend UX knowledge closure

Status: completed experimental evaluation. Candidate for canonicalization; no merge is authorized by this document.

Branches:

- Harness: `research/frontend-ux-closure-v1`
- Prep consumer test: `research/frontend-ux-closure-v1`

## Verdict

The experiment supports adopting the granular frontend UX knowledge model into Harness.

The central result is:

> HUMAN-INTERFACE-DESIGN remains one Authority, but non-trivial frontend work benefits from independently addressable Conceptual Interface, Information Architecture, Interaction, Interface Topology, Presentation System and Screen/View knowledge contracts.

No new Core entity, frontend workflow, UI/UX Authority or mandatory document format is required.

A site map, app map, wireframe, Figma file or prototype remains a projection/evidence surface. Canonical completeness comes from machine-addressable knowledge dependencies.

## Final dependency model

```text
Product/Application semantics
        ↓
Task Model
        ↓
User Journeys
        ↓
Conceptual Interface Model
        ├───────────────┐
        ▼               ▼
Information         Interaction
Architecture        Design
        └───────┬───────┘
                ▼
        Interface Topology
        ├──────────────► early interface verification when applicable
        ▼
        Presentation System
                ↓
        Screen / View Design
                ↓
        downstream architecture/component/verification/implementation
```

This is dependency topology, not a workflow/stage machine.

## What was validated

### Independent knowledge without Authority proliferation

The following knowledge kinds carry materially different decisions under HUMAN-INTERFACE-DESIGN:

- `conceptual-interface-model`;
- `information-architecture-design`;
- `interaction-design`;
- `interface-topology-design`;
- existing `presentation-system-design`;
- existing `screen-view-design`.

`human-interface-design` remains compatibility-only for projects that intentionally keep conceptual/IA/interaction/topology knowledge inseparable.

### Task → interaction → topology → screen completeness

Executable validation proves:

```text
USER task
  -> Interaction Design context or explicit no-ui disposition
      -> Interface Topology task view or explicit non-view disposition
          -> required Screen/View subject
```

Material shells/workspaces are represented as explicit `structural: true` topology views. They participate in navigation and Screen/View coverage without falsely claiming a USER task.

### Site/app maps remain projections

Prep exposed three structural frames that originally existed only in its site map:

- Application Shell;
- LearningTarget Workspace;
- Curation Workspace.

Those frames were moved into canonical Interface Topology. The site map can therefore remain a disposable/human-readable projection rather than a hidden semantic owner.

### IA and Interaction remain independent until Topology

Real-project testing found an accidental dependency where Interaction contexts referenced IA locations despite IA and Interaction being intended parallel production branches.

The model was corrected:

- Interaction Design owns actions/responses/states and task coverage;
- Information Architecture owns organization/findability;
- Interface Topology maps accepted interaction contexts into accepted information locations/views.

### Existing-project migration gaps are detected non-destructively

Reconciliation must not rewrite a project Engineering Graph merely because Harness reference policy changes.

Engineering Coverage now provides the independent migration/completeness lens:

- a `FRONTEND` Consumer activates conceptual/IA/interaction/topology concerns even when the project graph has no granular providers;
- the legacy broad user-facing fixture therefore produces `MISSING / MODEL_PRODUCTION_CONTRACT` for those concerns;
- Authority-role routing identifies HUMAN-INTERFACE-DESIGN as the capable owner;
- `project-bootstrap-reconcile` explicitly requires this Coverage diagnostic after conservative reconciliation;
- no project Capability is silently inserted.

This closes the class of failure that previously allowed a project such as Prep to omit Task Model or another newly required semantic layer without an explicit diagnostic.

### Topology → Screen/View subject coverage is generic

Harness provides `evaluate_topology_screen_subject_coverage(topology, screen_subjects)`.

Interface Topology owns the expected subject set. Each project may extract Screen/View subject ids from its own canonical format through a project-owned adapter.

Prep embeds stable ids in its existing Screen/View Markdown and no longer maintains a duplicated coverage sidecar.

### Semantic quality is not confused with structural closure

The four new interface concerns require semantic evaluation.

Regression proves:

- provider exists without semantic acceptance → `MISSING / VALIDATE_SEMANTICS`;
- accepted semantic evidence for the capability/claim → `COVERED`.

The structural evaluator therefore proves closure/references, not that an IA is usable or a conceptual model is correct. Human/agent judgement and verification evidence remain separate as intended by Harness.

## Real Prep consumer evidence

Applying the model to Prep found defects that the synthetic fixture initially missed and improved the project model:

- missing explicit Task Model was corrected;
- Learning/Curation concepts were separated from domain entities;
- IA and Interaction were made independently addressable;
- 19 material view/frame subjects were made canonical in Interface Topology;
- three shared structural frames were made explicit;
- Screen/View coverage is derived from topology rather than a sidecar;
- broad `prep.human-interface` was removed from the experimental graph;
- the human-interface prose document remains only a non-canonical synthesis projection.

Prep's product/domain semantics were not changed by this experiment.

## Compatibility

The broad `human-interface-design` knowledge kind remains registered for existing/project-specific graphs.

A legacy project has two valid paths after Harness upgrade:

1. adopt granular capabilities; or
2. intentionally retain one broad capability and declare/semantically accept the granular concern claims it genuinely owns.

Silence is not a third path: FRONTEND consumer coverage surfaces the missing concern contracts.

The legacy `examples/user-facing-application/**` fixture is intentionally retained to test that migration behavior.

## Early verification

The experiment proves that IA/findability/interaction/topology verification can exist before local Screen/View realization without introducing a graph cycle.

This is supported, not universally mandated. Project/consumer evidence decides whether early verification is independently valuable.

## Validation result

At the final functional revision before this evaluation update:

- Harness full `make harness-check`: PASS;
- Prep full `Validate` workflow while pinned to the experimental Harness: PASS.

The branch also passed after canonical-facing README/frontend-design/skill cleanup, eliminating the old broad-interface model from normative frontend guidance.

## Recommendation

The architectural experiment is successful.

The current branch is a **canonicalization candidate** rather than a rejected or still-open research hypothesis.

Before merge, the remaining work is procedural rather than architectural:

- review the diff and migration note;
- decide whether the new knowledge kinds/concerns should become current Harness policy;
- if approved, merge/squash according to repository policy;
- then reconcile consumer projects using conservative graph reconciliation plus Engineering Coverage.

No merge into `main` is performed without explicit authorization.
