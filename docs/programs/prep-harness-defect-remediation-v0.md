# Prep / Harness defect remediation program v0

Status: ACTIVE  
Canonical owner: Harness remediation program  
Canonical repository: `lehater/harness`  
Canonical path: `docs/programs/prep-harness-defect-remediation-v0.md`  
Affected downstream project: `lehater/prep`

## 1. Purpose

This document is the canonical cross-repository control document for the defect-remediation program triggered by the Prep interface audit.

The program has two ordered objectives:

1. repair Harness mechanisms that allowed the known defect classes to be accepted or to pass verification;
2. only after the corresponding Harness protection exists, revalidate and repair Prep from canonical design through executable implementation.

The main risk controlled by this document is defect loss across long-running work, multiple chats/agents, repository branches and repeated revalidation.

This document is therefore both:

- the immutable defect register;
- the execution protocol for every remediation iteration.

No chat transcript, issue, branch, implementation commit or generated report replaces this register.

## 2. Non-negotiable rules

### R1 — Stable defect identity

Every observed Prep defect receives one immutable `PREP-UX-###` id.

Every systemic Harness defect or assurance gap receives one immutable `HARNESS-###` id.

An id is never reused and a registered defect is never deleted. If later analysis changes its interpretation, update its classification/status and append history. If two defects are proven equivalent, retain both ids and mark one `DUPLICATE_OF:<id>`.

### R2 — Harness first

Until the Harness phase for a Prep defect has a terminal disposition, no semantic or UI repair for that defect is made in Prep.

Allowed Prep work during the Harness-first phase is limited to evidence collection and this program's repository pointer/reference.

A Harness terminal disposition is one of:

- `HARNESS_FIXED` — a Harness mechanism/regression was added or repaired and the responsible Harness defect has reached `INTEGRATED` in Harness `main`;
- `HARNESS_NO_CHANGE_JUSTIFIED` — evidence-backed analysis proves that the observed Prep defect is outside Harness responsibility, identifies the owning Prep authority, explains why no reusable Harness invariant is missing, and records the justification in this register.

Silence, an unmerged Harness fix, or an unsupported assertion that a problem is "Prep-specific" is not a terminal disposition.

Prep may enter `PREP_REVALIDATION` for a defect only when every mapped Harness dependency has one of these terminal dispositions. When any dependency is `HARNESS_FIXED`, Prep must first pin `.harness-version` to a Harness `main` commit containing that integrated fix.

### R3 — RED before Harness fix

For every `HARNESS-###` mechanism defect, first add or identify a failing regression that represents at least one real Prep-derived failure mode.

The preferred order is:

```
real Prep defect
  -> minimal Harness reproduction/mutation
  -> RED
  -> Harness fix
  -> GREEN
```

Do not use a synthetic abstraction when the real Prep case can be represented directly.

### R4 — Preserve upstream authority

Harness fixes may strengthen admission, derivation, decision exploration, verification coverage or traceability.

Harness must not encode Prep-specific UI choices such as "use a table" or "merge these two screens" as universal truth.

The framework should require a decision, semantic distinction, observable realization or evidence obligation; the owning Prep authority chooses the concrete design.

### R5 — Prep revalidation before Prep implementation

After Harness protection exists, Prep is repaired in canonical authority order.

Do not patch React first and retrofit design afterward.

For each affected defect, reopen the earliest Prep authority where the corrected decision belongs, then propagate currentness downstream through accepted artifacts, Verification/Test Design and Implementation Design before changing production frontend behavior.

### R6 — Closure requires two proofs

A Prep defect can become `CLOSED` only when both are true:

1. Harness proof: the responsible defect class is rejected/detected or explicitly classified as project-only;
2. Prep proof: the corrected canonical decision is realized and verified in the current frontend.

A green Prep E2E suite alone is not closure.

### R7 — Evidence-backed reclassification

Classification, priority, dependency mapping and status may change when new evidence is found, but the defect id does not change.

Every such change must preserve the previous meaning in history/evidence and record why the new classification is better supported. Reclassification never permits deletion, id reuse or silent merging.

### R8 — New findings are registered before remediation

A newly discovered real defect is appended to this document with the next free stable id before work expands to fix it.

The registration must include at least: observable finding, priority, current classification, mapped dependency/owner when known, initial status, and evidence location. Investigation may refine these fields later under R7.

### R9 — BLOCKED and rejected findings remain auditable

`BLOCKED:<reason>` preserves the defect and records the concrete unmet dependency or missing evidence needed to resume.

`REJECTED_AS_NOT_DEFECT:<evidence>` is a terminal finding disposition only when evidence demonstrates that the reported behavior conforms to the accepted authority. The id and history remain in the register.

Neither state removes the item from the denominator.

### R10 — GREEN is an evidence state

For a Harness mechanism fix, `HARNESS_GREEN` requires all of the following:

1. the same regression/reproduction that established RED now passes;
2. relevant deterministic Harness checks pass;
3. at least one positive control demonstrates that legitimate design freedom is still accepted when applicable;
4. evidence identifies the scenario/test, affected files and commit/PR.

A fix implementation without this evidence remains `FIX_IMPLEMENTED`.

## 3. Status model

Every Prep defect moves through this state machine:

```
REGISTERED
  -> REPRODUCED
  -> ROOT_CAUSE_CLASSIFIED
  -> HARNESS_DISPOSITIONED
  -> PREP_REVALIDATION
  -> PREP_IMPLEMENTATION
  -> PREP_VALIDATED
  -> CLOSED
```

Allowed exceptional statuses:

- `BLOCKED:<reason>`
- `DUPLICATE_OF:<id>`
- `REJECTED_AS_NOT_DEFECT:<evidence>`

Every Harness defect moves through:

```
REGISTERED
  -> REPRODUCED
  -> HARNESS_RED
  -> FIX_IMPLEMENTED
  -> HARNESS_GREEN
  -> INTEGRATED
```

A status change must record evidence: file/path, scenario/test id, commit/PR or explicit analysis result.

State-machine transitions are monotonic by default. If later evidence invalidates an earlier transition, the register must explicitly record the rollback/reclassification and its evidence rather than rewriting history.

## 4. Canonical Prep defect register

The register intentionally keeps observed symptoms separate even when several share one root cause.

| ID | Priority | Defect | Current classification | Harness dependencies | Status |
|---|---:|---|---|---|---|
| PREP-UX-001 | P0 | Active Target is not sufficiently explicit as the central preparation context. | usability/presentation finding; semantic chain currently appears intact | HARNESS-005 | REGISTERED |
| PREP-UX-002 | P0 | `Targets` and `Target` are exposed as peer navigation/destinations although a single user-facing Targets area may better preserve the mental model. | exploration-coverage gap; current split is canonical in IA/Topology | HARNESS-003, HARNESS-008 | REGISTERED |
| PREP-UX-003 | P0 | No explicit cross-context interaction model distinguishes opened/inspected Target, selected-for-comparison Target, candidate-to-continue and active Target. | authority/interaction-model gap | HARNESS-004, HARNESS-005 | REGISTERED |
| PREP-UX-004 | P1 | Capability is insufficiently visible as a first-class user-facing meaning across target requirements, current state and gaps. | observable-realization gap | HARNESS-005 | REGISTERED |
| PREP-UX-005 | P1 | Knowledge has no user-operated Required Capability selector although Journey, Interaction, Presentation, Screen/View, Test Design and query/state contracts require/support it. | implementation drift + verification/traceability gap | HARNESS-001, HARNESS-002, HARNESS-005 | REPRODUCED |
| PREP-UX-006 | P1 | Focus presentation is too easy to interpret as Capability; the distinct meanings are not made sufficiently observable. | observable semantic-distinction gap | HARNESS-004, HARNESS-005 | REGISTERED |
| PREP-UX-007 | P1 | Target comparison is rendered as independent cards rather than an operationally aligned comparison over common dimensions. | presentation derivation + verification gap | HARNESS-001, HARNESS-002, HARNESS-006 | REPRODUCED |
| PREP-UX-008 | P1 | Current Position uses repeated cards for homogeneous/comparable state information where a collection/table-like representation may better support scanning and comparison. | representation decision not sufficiently explored | HARNESS-006 | REGISTERED |
| PREP-UX-009 | P1 | Target requirements use repeated cards where a structured collection/table-like representation may better express homogeneous requirement dimensions. | representation decision not sufficiently explored | HARNESS-006 | REGISTERED |
| PREP-UX-010 | P1 | Shared `DataTable` exists but its use across applicable homogeneous collections is inconsistent. | presentation/component policy coverage gap | HARNESS-006 | REGISTERED |
| PREP-UX-011 | P1 | No sufficiently explicit application-level decision rule governs when information should be Table/List/Card/Detail/Workflow/Graph/aligned comparison. | presentation decision-space gap | HARNESS-006 | REGISTERED |
| PREP-UX-012 | P2 | Selection mechanics are duplicated/inconsistent across candidate selection, comparison selection and other selectable task surfaces. | shared interaction-role/pattern gap | HARNESS-004, HARNESS-006 | REGISTERED |
| PREP-UX-013 | P2 | User-facing grouping/navigation is insufficiently separated from task/application/component ownership boundaries. | boundary/local grouping exploration gap | HARNESS-003, HARNESS-008 | REGISTERED |
| PREP-UX-014 | P2 | Required Capability scope appears mainly as an incoming badge/context indicator rather than as a normal local Knowledge filter control. | observable-control realization gap; related to but distinct from PREP-UX-005 | HARNESS-002, HARNESS-005 | REPRODUCED |
| PREP-UX-015 | P3 | `Surface`/`Card` is used as a default presentation container too broadly. | representation-default bias | HARNESS-006 | REGISTERED |
| PREP-UX-016 | P3 | Table-first/aligned alternatives were not explicitly explored for several comparison/collection decisions. | decision-exploration gap | HARNESS-006 | REGISTERED |

### Registration policy

This table is the denominator.

Newly discovered defects are appended with the next id. Existing rows are never silently merged or removed.

The priority may change after root-cause analysis, but the id and history remain.

## 5. Canonical Harness defect register

| ID | Priority | Systemic defect / missing protection | Primary affected Prep defects | Status |
|---|---:|---|---|---|
| HARNESS-001 | P0 | Semantic-surface admission permits compound summary assertions whose internal independently losable user obligations are not atomized; downstream semantic derivation can therefore report coverage while a sub-obligation disappears. | 005, 007 | REGISTERED |
| HARNESS-002 | P0 | Test Design semantic contracts are not sufficiently bound to concrete executable test actions/oracles; an E2E can exist and be green while testing a weaker operation than the accepted Test Design contract. | 005, 007, 014 | REGISTERED |
| HARNESS-003 | P1 | Decision Governance can close a broad view-boundary axis without proving that each material concrete boundary received the relevant local alternatives/challenges. | 002, 013 | REGISTERED |
| HARNESS-004 | P1 | Interaction Design lacks a strong applicability rule requiring one cross-context role/state contract when the same conceptual entity participates in multiple user-visible roles with different side effects. | 003, 006, 012 | REGISTERED |
| HARNESS-005 | P1 | User-facing semantic distinctions/actions can be preserved abstractly without an explicit mapping to an observable user mechanism that makes the distinction/action available and understandable. | 001, 003, 004, 005, 006, 014 | REGISTERED |
| HARNESS-006 | P1 | Presentation/Screen decision exploration lacks a sufficiently explicit representation-selection axis for homogeneous collections and aligned comparison (card/list/table/detail/workflow/graph/comparison). | 007, 008, 009, 010, 011, 012, 015, 016 | REGISTERED |
| HARNESS-007 | P2 | There is no standard review projection that shows Journey/Interaction -> Screen obligation -> Test operation/oracle -> executable implementation evidence and exposes the first missing link. | all, diagnostic support | REGISTERED |
| HARNESS-008 | P1 | Human-interface grouping/topology is insufficiently challenged against mirroring task/application/component decomposition; current guidance rejects backend-shaped IA but does not strongly guard against responsibility-shaped UI grouping. | 002, 013 | REGISTERED |

## 6. Known reproduced evidence

### PREP-UX-005 / PREP-UX-014 — Required Capability filter

Accepted chain currently contains the obligation through:

```
User Journey
  -> Application Design
  -> Interaction Design
  -> Presentation System
  -> Screen/View Design
  -> Frontend Test Design
  -> Frontend Implementation Design
```

The current frontend keeps `requiredCapabilityRef` in query/state and can receive an incoming Required Capability scope, but the Knowledge toolbar exposes the active value as `.knowledge-capability-scope` rather than a user-operated selector.

Current Playwright coverage verifies incoming contextual scope and reset behavior, not the accepted Test Design operation "apply and clear a Required-Capability scope" from within Knowledge.

This is the mandatory first Harness RED reproduction because it proves the program's central failure class.

### PREP-UX-002 — Targets / Target

The current separation is already canonical in Prep Information Architecture and Interface Topology, and its broad topology decision exploration selected separate task-responsibility views.

Therefore it must not be "fixed in React". The Harness-side question is whether boundary-local exploration should have been required for the concrete `VIEW-TARGETS <-> VIEW-TARGET` boundary and whether user-facing grouping may differ from application/task ownership.

## 7. Execution strategy

### Phase 0 — Freeze and register

Goal: establish one complete denominator before any repair.

Actions:

1. merge this control document into Harness;
2. merge the thin reference document into Prep;
3. do not change Prep UI for any registered defect during the Harness-first phase;
4. append any newly discovered defect immediately before investigating it.

Exit criterion:

- every known defect has an id, priority, owner class and current status.

### Phase 1 — Harness semantic-assurance foundation

Order:

1. HARNESS-001 — semantic-surface completeness/atom granularity;
2. HARNESS-002 — Test Design -> executable evidence conformance;
3. HARNESS-007 — traceability projection after the two underlying chains are machine-addressable.

First required regression:

```
Knowledge Required Capability control mutation:
  retain query/state/support
  retain incoming Capability context/badge
  retain reset
  remove user-operated selector
Expected Harness result: RED
```

A valid fix must reject/detect the semantic loss without encoding a Prep-specific React component or literal selector implementation.

Exit criterion:

- the capability-filter mutation is RED before the fix and GREEN only when the user-operable obligation and executable evidence are both present.

### Phase 2 — Harness human-interface decision protections

Order:

1. HARNESS-004 — interaction-role/state applicability;
2. HARNESS-005 — user-observable realization mapping;
3. HARNESS-003 — boundary-local Decision Governance;
4. HARNESS-008 — UI grouping vs task/application ownership;
5. HARNESS-006 — representation-selection decision axis.

For each mechanism use at least one real Prep defect as RED calibration and one positive control where current design freedom must remain accepted.

Exit criterion:

- every `HARNESS-###` has a concrete regression, implementation change or explicit no-change disposition, and all Harness deterministic checks are green.

### Phase 3 — Integrate Harness and repin Prep

Actions:

1. integrate Harness fixes into `main`;
2. identify the exact integrated Harness commit;
3. update Prep's `.harness-version` only after Harness integration;
4. run Harness currentness/coverage on Prep;
5. treat resulting stale/downstream work as expected revalidation, not as a reason to bypass the new rules.

Exit criterion:

- Prep is evaluated by the corrected Harness version.

### Phase 4 — Prep canonical revalidation

For each `PREP-UX-###`, reopen the earliest owning authority.

Default order:

```
Conceptual Interface / IA / Interaction
  -> Interface Topology
  -> Presentation System
  -> Screen/View
  -> Verification
  -> Test Design
  -> Component / Implementation Design
```

Only touch an earlier layer if the defect actually belongs there.

Examples:

- PREP-UX-002 starts at IA/Topology decision revalidation;
- PREP-UX-003 starts at Interaction Design;
- PREP-UX-005 starts by revalidating the already-correct interaction/screen/test obligations under the strengthened Harness rather than inventing new semantics;
- PREP-UX-007 starts at presentation/screen comparison semantics;
- PREP-UX-008/009/010/011/015/016 start at representation decision exploration, not React components.

Exit criterion:

- every active Prep defect has an accepted canonical repair path and all affected downstream capabilities are current.

### Phase 5 — Prep implementation repair

Only now change production frontend.

Rules:

- implementation follows the newly current canonical artifacts;
- every repaired defect has executable evidence bound to the accepted Test Design operation/oracle;
- no implementation change is accepted merely because it "looks better";
- shared primitives are changed only when the canonical representation/pattern decision is shared.

Exit criterion:

- all affected deterministic/unit/contract/browser tests and Harness currentness checks pass.

### Phase 6 — Program closure

For every `PREP-UX-###`:

1. verify Harness disposition;
2. verify canonical Prep repair;
3. verify implementation evidence;
4. verify no sibling defect was accidentally hidden by the change;
5. set `CLOSED` with evidence.

Program closure requires:

- zero registered defects in a non-terminal state;
- zero unresolved P0/P1;
- all P2/P3 either closed or explicitly `REJECTED_AS_NOT_DEFECT` with evidence;
- Prep pinned to the integrated Harness baseline that contains the protections used for closure.

## 8. Work-package strategy for multiple chats/agents

One chat/agent should own one coherent mechanism or one bounded Prep revalidation group.

Do not assign "fix all UI issues" to one agent.

Recommended Harness work packages:

- WP-H1: HARNESS-001 semantic-surface completeness;
- WP-H2: HARNESS-002 executable Test Design conformance;
- WP-H3: HARNESS-004 + HARNESS-005 interaction roles and observable realization;
- WP-H4: HARNESS-003 + HARNESS-008 boundary-local UI grouping;
- WP-H5: HARNESS-006 representation decision axis;
- WP-H6: HARNESS-007 traceability projection and full regression matrix.

Recommended Prep work packages after Harness integration:

- WP-P1: PREP-UX-001/002/003/013 — Target context, navigation and interaction roles;
- WP-P2: PREP-UX-004/005/006/014 — Capability, Focus and Knowledge scope;
- WP-P3: PREP-UX-007 — Target comparison;
- WP-P4: PREP-UX-008/009/010/011/015/016 — collection/comparison representation system;
- WP-P5: PREP-UX-012 — shared selection mechanics after semantic roles are settled;
- WP-P6: end-to-end verification/currentness closure.

Work packages may be split further, but defect ids must remain unchanged.

## 9. Required handoff contract for every chat/agent

Every remediation chat must begin by reading this document and declaring:

```
Program document:
  docs/programs/prep-harness-defect-remediation-v0.md

Scope:
  HARNESS-### and/or PREP-UX-###

Starting statuses:
  ...

Allowed repository:
  harness | prep

Upstream artifacts to treat as authority:
  ...

Explicit non-goals:
  ...
```

Every chat must end with:

```
IDs processed:
  ...

Status transitions:
  OLD -> NEW

Evidence:
  tests/scenarios/files/commits

New defects discovered:
  PREP-UX-### / HARNESS-### appended to canonical register
  or NONE

Remaining blockers:
  ...

Recommended next work:
  ...
```

A chat must not declare a defect closed if another required phase remains.

### Stage gate

An executor chat/agent does not choose or start the next program stage on its own.

After every stage or corrective stage:

1. the executor stops after completing its bounded scope;
2. the executor produces the required handoff report and evidence;
3. the user transfers that report to the managing chat;
4. the managing chat verifies repository state, evidence and register transitions;
5. only the managing chat issues the prompt for the next stage or a corrective stage.

An executor may recommend the next stage, but that recommendation has no execution authority.

### Definition of stage/work-package completion

Every stage/work package must define before execution:

- explicit scope and non-goals;
- starting statuses;
- exit criteria.

Its closing report must contain:

- evidence for every claimed transition;
- repository commits/PRs;
- relevant test/check commands and results;
- canonical-register changes;
- newly discovered defects;
- unresolved risks/blockers;
- deviations from the prompt.

A stage/work package is `COMPLETE` only when every exit criterion is evidenced. If required evidence or an exit criterion is missing, the result is `INCOMPLETE`; if progress is prevented by an external dependency or safety/repository constraint, the result is `BLOCKED`.

## 10. Defect-processing checklist

For each Prep defect, answer these in order:

1. What is the observable failure?
2. Can it be reproduced from current Prep?
3. What is the earliest accepted authority where the wrong/missing decision appears?
4. Is the defect:
   - derivation loss,
   - verification gap,
   - implementation drift,
   - authority gap,
   - exploration-coverage gap,
   - usability-only finding,
   - or mixed?
5. Which `HARNESS-###` should have prevented or exposed it?
6. Is there a Harness RED reproduction?
7. Is the Harness protection integrated?
8. Is Prep repinned to that Harness?
9. Which Prep canonical artifacts must be reopened?
10. What executable evidence proves the corrected behavior?
11. Have sibling defects with shared surfaces been rechecked?
12. Only then: can status become `CLOSED`?

## 11. Change-control rules for this document

This document is intentionally mutable but auditable.

Allowed changes:

- append new defect ids;
- change status/priority/classification with evidence;
- refine work-package ordering;
- add links to regression scenarios/commits;
- mark terminal dispositions.

Forbidden changes:

- renumber existing ids;
- delete old defects;
- rewrite history to make a formerly observed defect disappear;
- close a defect without Harness and Prep evidence;
- copy the register into another repository and let both copies diverge.

The Prep repository contains only a pointer to this canonical register.

This file in Harness is the single source of truth for the denominator, statuses, classifications, mappings, execution ordering and evidence history. Any issue, report or Prep-side document may reference ids but must not maintain a second authoritative register. If a duplicate register is discovered, stop updating it and reconcile all unique information back into this document before further status transitions.

## 12. Current program frontier

The immediate next action is:

```
WP-H1
HARNESS-001
semantic-surface completeness / atom granularity

first RED:
PREP-UX-005 Required Capability selector omission
```

After WP-H1, proceed to WP-H2 so that accepted Test Design operations are also bound to executable evidence.

Prep semantic/UI changes remain frozen until the Harness work required by the affected ids reaches a terminal Harness disposition.
