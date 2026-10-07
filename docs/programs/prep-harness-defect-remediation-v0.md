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
| PREP-UX-002 | P0 | `Targets` and `Target` are exposed as peer navigation/destinations although a single user-facing Targets area may better preserve the mental model. | IA revalidation selected one Targets parent with distinct candidate-comparison and active-Target sublocations; navigation/view realization remains downstream | HARNESS-003, HARNESS-008 | PREP_REVALIDATION |
| PREP-UX-003 | P0 | No explicit cross-context interaction model distinguishes opened/inspected Target, selected-for-comparison Target, candidate-to-continue and active Target. | Interaction role gap reproduced and revalidated: three material Target roles are now explicit; opened/inspected is not a distinct role because inspection adds no separate role lifecycle/side effect | HARNESS-004, HARNESS-005 | PREP_REVALIDATION |
| PREP-UX-004 | P1 | Capability is insufficiently visible as a first-class user-facing meaning across target requirements, current state and gaps. | observable-realization gap | HARNESS-005 | REGISTERED |
| PREP-UX-005 | P1 | Knowledge has no user-operated Required Capability selector although Journey, Interaction, Presentation, Screen/View, Test Design and query/state contracts require/support it. | Interaction revalidation independently preserves apply and clear Required Capability scope actions; observable realization/implementation remains downstream | HARNESS-001, HARNESS-002, HARNESS-005 | PREP_REVALIDATION |
| PREP-UX-006 | P1 | Focus presentation is too easy to interpret as Capability; the distinct meanings are not made sufficiently observable. | Interaction distinction gap reproduced and revalidated: Capability Knowledge scope and Next Focus cannot silently mutate each other; observable presentation remains downstream | HARNESS-004, HARNESS-005 | PREP_REVALIDATION |
| PREP-UX-007 | P1 | Target comparison is rendered as independent cards rather than an operationally aligned comparison over common dimensions. | presentation derivation + verification gap | HARNESS-001, HARNESS-002, HARNESS-006 | HARNESS_DISPOSITIONED |
| PREP-UX-008 | P1 | Current Position uses repeated cards for homogeneous/comparable state information where a collection/table-like representation may better support scanning and comparison. | representation decision not sufficiently explored | HARNESS-006 | HARNESS_DISPOSITIONED |
| PREP-UX-009 | P1 | Target requirements use repeated cards where a structured collection/table-like representation may better express homogeneous requirement dimensions. | representation decision not sufficiently explored | HARNESS-006 | HARNESS_DISPOSITIONED |
| PREP-UX-010 | P1 | Shared `DataTable` exists but its use across applicable homogeneous collections is inconsistent. | presentation/component policy coverage gap | HARNESS-006 | HARNESS_DISPOSITIONED |
| PREP-UX-011 | P1 | No sufficiently explicit application-level decision rule governs when information should be Table/List/Card/Detail/Workflow/Graph/aligned comparison. | presentation decision-space gap | HARNESS-006 | HARNESS_DISPOSITIONED |
| PREP-UX-012 | P2 | Selection mechanics are duplicated/inconsistent across candidate selection, comparison selection and other selectable task surfaces. | shared interaction-role/pattern gap | HARNESS-004, HARNESS-006 | BLOCKED:same-role-equivalence-not-established |
| PREP-UX-013 | P2 | User-facing grouping/navigation is insufficiently separated from task/application/component ownership boundaries. | IA grouping was re-derived from user-facing Target cohesion rather than responsibility decomposition; downstream navigation/topology realization remains pending | HARNESS-003, HARNESS-008 | PREP_REVALIDATION |
| PREP-UX-014 | P2 | Required Capability scope appears mainly as an incoming badge/context indicator rather than as a normal local Knowledge filter control. | Interaction revalidation requires independent apply/clear scope actions; concrete local-control realization remains downstream | HARNESS-002, HARNESS-005 | PREP_REVALIDATION |
| PREP-UX-015 | P3 | `Surface`/`Card` is used as a default presentation container too broadly. | representation-default bias | HARNESS-006 | HARNESS_DISPOSITIONED |
| PREP-UX-016 | P3 | Table-first/aligned alternatives were not explicitly explored for several comparison/collection decisions. | decision-exploration gap | HARNESS-006 | HARNESS_DISPOSITIONED |

### Registration policy

This table is the denominator.

Newly discovered defects are appended with the next id. Existing rows are never silently merged or removed.

The priority may change after root-cause analysis, but the id and history remain.

## 5. Canonical Harness defect register

| ID | Priority | Systemic defect / missing protection | Primary affected Prep defects | Status |
|---|---:|---|---|---|
| HARNESS-001 | P0 | Semantic-surface admission permits compound summary assertions whose internal independently losable user obligations are not atomized; downstream semantic derivation can therefore report coverage while a sub-obligation disappears. | 005, 007 | INTEGRATED |
| HARNESS-002 | P0 | Test Design semantic contracts are not sufficiently bound to concrete executable test actions/oracles; an E2E can exist and be green while testing a weaker operation than the accepted Test Design contract. | 005, 007, 014 | INTEGRATED |
| HARNESS-003 | P1 | Decision Governance can close a broad view-boundary axis without proving that each material concrete boundary received the relevant local alternatives/challenges. | 002, 013 | INTEGRATED |
| HARNESS-004 | P1 | Interaction Design lacks a strong applicability rule requiring one cross-context role/state contract when the same conceptual entity participates in multiple user-visible roles with different side effects. | 003, 006, 012 | INTEGRATED |
| HARNESS-005 | P1 | User-facing semantic distinctions/actions can be preserved abstractly without an explicit mapping to an observable user mechanism that makes the distinction/action available and understandable. | 001, 003, 004, 005, 006, 014 | INTEGRATED |
| HARNESS-006 | P1 | Presentation/Screen decision exploration lacks a sufficiently explicit representation-selection axis for homogeneous collections and aligned comparison (card/list/table/detail/workflow/graph/comparison). | 007, 008, 009, 010, 011, 012, 015, 016 | INTEGRATED |
| HARNESS-007 | P2 | There is no standard review projection that shows Journey/Interaction -> Screen obligation -> Test operation/oracle -> executable implementation evidence and exposes the first missing link. | all, diagnostic support | INTEGRATED |
| HARNESS-008 | P1 | Human-interface grouping/topology is insufficiently challenged against mirroring task/application/component decomposition; current guidance rejects backend-shaped IA but does not strongly guard against responsibility-shaped UI grouping. | 002, 013 | INTEGRATED |

## 6. Known reproduced evidence

### HARNESS-001 — independently losable semantic-obligation granularity

Status history for WP-H1:

```
REGISTERED
  -> REPRODUCED
  -> HARNESS_RED
  -> FIX_IMPLEMENTED
  -> HARNESS_GREEN
  -> INTEGRATED
```

RED evidence:

- regression: `tests/test_semantic_admission.py::test_independently_losable_obligation_granularity`;
- RED-only commit: `8b46439306af81f3c71224524733b51a7fe4f987`;
- CI run `37578888796` failed because the baseline evaluator returned `ACCEPTED` for a surface that retained visible-scope, clear-scope and a coarse reversible-scope summary while the independently losable apply/select obligation was marked `COLLAPSED`.

Root cause:

Semantic admission required an ACCEPTED semantic review and named review checks, but had no deterministic accounting contract for independently losable obligations identified by that semantic review. Downstream derivation therefore received only the already-coarsened accepted assertion set; an obligation lost before that boundary could never become an `UNDISPOSITIONED_SOURCE`.

Implemented invariant:

- the existing semantic-review boundary identifies independently losable user-observable obligations and records them under `semantic_review.independent_obligations`;
- when `independent-obligation-granularity` is required, each `ACCOUNTED` obligation must reference an existing semantic assertion;
- one semantic assertion cannot account for multiple independently losable obligations;
- `COLLAPSED`, `MISSING` and `QUESTION` obligations reject admission;
- the check is required for `user-journey-design`, `interaction-design`, `presentation-system-design` and `screen-view-design`;
- no natural-language heuristic or Prep-specific control type is encoded.

Positive control:

A cohesive assertion with one user-observable lifecycle remains `ACCEPTED`; the invariant does not require sentence-level atomization.

GREEN evidence:

- fix/regression branch head: `1be08061d5bd5da8748a8b7669559e7b39449c8c`;
- `harness core` / `make harness-check`: run `37579171037` PASS;
- `Greenfield Engineering Graph`: run `37579171021` PASS;
- PR: #198.

Integration evidence: PR #198 was squash-merged to Harness `main` as `64915278c04d14ecd385efd22f974b82529cfdaa`. `PREP-UX-005` stays `REPRODUCED`; HARNESS-002 and HARNESS-005 remain unresolved dependencies, so it does not advance to `HARNESS_DISPOSITIONED`.

### HARNESS-002 — executable Test Design conformance

Status history for WP-H2:

```
REGISTERED
  -> REPRODUCED
  -> HARNESS_RED
  -> FIX_IMPLEMENTED
  -> HARNESS_GREEN
  -> INTEGRATED
```

RED evidence:

- regression: `tests/test_test_realization_conformance.py::test_test_design_realization_rejects_missing_operation`;
- RED-only commit: `60aeaeb78123260ea4e01df5e509de323c0ff9d1`;
- CI run `37582618670` failed after the baseline `repository_realization` evaluator returned `complete: true` for executable evidence that covered scoped-state observation, clear/reset and restored-state observation while omitting `OP-APPLY`.

Root cause:

Accepted Test Design defined the executable behavioral contract, but its operation/oracle content was not independently addressable for realization accounting and Harness had no conformance boundary from that contract to concrete executable evidence. Repository realization could therefore be complete while a green test exercised only a weaker neighboring flow.

Implemented invariant:

- independently executable/verifiable Test Design operations and oracles use stable `operation_obligations` / `oracle_obligations` ids;
- executable test code remains noncanonical implementation evidence and binds concrete test locators to those canonical ids;
- a binding contributes coverage only after an ACCEPTED `executable-correspondence` semantic review and only when its referenced executable evidence is `PASSED`;
- deterministic assurance then accounts every required operation/oracle and reports the exact missing obligation;
- no regex/AST/framework-specific inference or Prep-specific semantics are used; one executable may cover several obligations and several executables may jointly realize one contract.

Negative mutations:

- missing `OP-APPLY`: REJECTED with `TEST_REALIZATION_OPERATION_MISSING`;
- missing `ORACLE-RESTORED`: REJECTED with `TEST_REALIZATION_ORACLE_MISSING`;
- an unreviewed binding claim does not count as correspondence.

Positive controls:

- full realization of all operation/oracle obligations: ACCEPTED;
- one-test and split-test organizations both realize the same Test Design contract: ACCEPTED.

GREEN evidence:

- validated implementation head: `17798f12547ea05578607fa3cef3f7302345fb20`;
- `harness core` / `make harness-check`: run `37582648536` PASS;
- `CI policy`: run `37582648539` PASS;
- `Greenfield Engineering Graph`: run `37582648533` PASS;
- PR: #200.

Integration evidence: PR #200 was squash-merged to Harness `main` as `6b46b99603e2b805d7777e6c76d1a9e5a42d4850`. `PREP-UX-005`, `PREP-UX-007` and `PREP-UX-014` remain unchanged because their complete Harness dependency sets are not yet terminal. Prep and `.harness-version` remain unchanged.

### HARNESS-004 — cross-context interaction role coherence

Status history for WP-H3:

```
REGISTERED
  -> REPRODUCED
  -> HARNESS_RED
  -> FIX_IMPLEMENTED
  -> HARNESS_GREEN
  -> INTEGRATED
```

RED evidence:

- RED-only commit: `2fa11201c64f05408437f5b89d11962ebd043537`;
- regression: `tests/test_semantic_admission.py::test_h3_role_and_observable_realization_false_greens`;
- CI run `37587959599` failed after baseline semantic admission returned `ACCEPTED` for a candidate that collapsed two semantically required material roles into one generic selected role.

Root cause:

Interaction Design could describe actions/states locally and HARNESS-001 could account independently losable obligations, but there was no semantically activated cross-context role contract. Harness therefore had no deterministic boundary for proving that material lifecycle/side-effect distinctions of one conceptual entity were represented coherently across contexts.

Implemented invariant:

- `interaction-role-coherence` is a required Interaction Design semantic-review check;
- semantic review owns applicability in `semantic_review.interaction_role_requirements`; Harness does not infer applicability from matching subjects/labels;
- when a concept is marked `REQUIRED`, canonical `interaction_roles` provide stable role id, concept ref, meaning, entry/exit, transitions, side effects, forbidden side effects and observable distinction;
- semantic review identifies which facets/transitions are material, then deterministic admission checks their presence;
- `NOT_REQUIRED`/an explicitly reviewed empty requirement set preserves same-role/multiple-context designs without multi-role ceremony;
- no Prep Target ontology or concrete presentation primitive is encoded.

Negative mutations:

- role conflation: REJECTED with missing required roles;
- missing material forbidden side effect: REJECTED with `INTERACTION_ROLE_REQUIRED_FACET_MISSING`;
- missing material transition: REJECTED with `INTERACTION_ROLE_REQUIRED_TRANSITION_MISSING`.

Positive controls:

- same role/lifecycle across multiple contexts: ACCEPTED without a multi-role contract;
- complete materially distinct multi-role contract: ACCEPTED.

GREEN evidence:

- regression: `tests/test_semantic_admission.py::test_interaction_role_coherence_regressions`;
- validated implementation/register head: `e6caa7e814f74ab683ea000d189545420c3ee22e`;
- `harness core` / full `make harness-check`: run `37588353194` PASS;
- `Greenfield Engineering Graph`: run `37588353257` PASS;
- PR: #203.

Integration evidence: PR #203 was squash-merged to Harness `main` as `1f006277afbb1d8083c565cbe41830dbfebf6a21`.

### HARNESS-005 — observable semantic realization conformance

Status history for WP-H3:

```
REGISTERED
  -> REPRODUCED
  -> HARNESS_RED
  -> FIX_IMPLEMENTED
  -> HARNESS_GREEN
  -> INTEGRATED
```

RED evidence:

- RED-only commit: `2fa11201c64f05408437f5b89d11962ebd043537`;
- regression: `tests/test_semantic_admission.py::test_h3_role_and_observable_realization_false_greens`;
- CI run `37587959599` failed after baseline semantic derivation returned `ACCEPTED` when the user action to apply scope was linked only to the neighboring current-state realization.

Root cause:

Semantic derivation could structurally cover a source assertion through an allowed link, optionally with target provenance, but did not distinguish observable ACTION/STATE/DISTINCTION realization or require semantic correspondence for that realization. A source id could therefore be linked to a neighboring observable state and count as covered without a usable mechanism for the actual user-facing action.

Implemented invariant:

- Interaction semantic review classifies independently losable user-facing semantics in `observable_realization_obligations` as ACTION, STATE or DISTINCTION and REQUIRED, NOT_APPLICABLE or QUESTION;
- a derivation obligation with `observable_realization: true` selects only semantically REQUIRED sources for downstream accounting;
- REQUIRED sources count as covered only through `REALIZES` links to explicit `observable-realization` target assertions with the same observable category and source provenance;
- observable realization automatically requires request-bound semantic judgement with `observable-realization-correspondence`;
- deterministic accounting then rejects every required source without an accepted realization;
- legitimate semantic-review `NOT_APPLICABLE` remains possible with rationale;
- no button/menu/control/layout/DOM/CSS primitive is mandated.

Negative mutations:

- missing action realization: REJECTED with `UNDISPOSITIONED_SOURCE`;
- collapsed semantic distinction: REJECTED when request-bound correspondence judgement rejects the claimed realization;
- reference-only realization: REJECTED with `OBSERVABLE_REALIZATION_TARGET_MISSING`;
- STATE cannot substitute for an independent ACTION because observable category must match.

Positive controls:

- an abstract accepted interaction mechanism realizes ACTION without constraining button/menu/keyboard/etc.: ACCEPTED;
- legitimate non-UI/non-applicability from accepted source semantic review: ACCEPTED.

GREEN evidence:

- regression: `tests/test_semantic_admission.py::test_observable_realization_regressions`;
- validated implementation/register head: `e6caa7e814f74ab683ea000d189545420c3ee22e`;
- `harness core` / full `make harness-check`: run `37588353194` PASS;
- `Greenfield Engineering Graph`: run `37588353257` PASS;
- PR: #203.

Integration evidence: PR #203 was squash-merged to Harness `main` as `1f006277afbb1d8083c565cbe41830dbfebf6a21`.

### HARNESS-003 — boundary-local Decision Governance

Status history for WP-H4:

```
REGISTERED
  -> REPRODUCED
  -> HARNESS_RED
  -> FIX_IMPLEMENTED
  -> HARNESS_GREEN
```

RED evidence:

- regression: WP-H4 block in `tests/test_decision_governance.py`, broad-decision false coverage;
- validated RED-only commit: `494431a4eb890e1294461d2bc4843d99aaed3269`;
- evidence PR: #207 (closed without merge);
- `harness core` run `37591336184` failed because baseline Decision Exploration and Governance both returned `ACCEPTED` for `overall-view-structure` while material `BOUNDARY-A-B` had no boundary-local decision subject or probes.

Root cause:

Decision Governance was complete only at axis/decision-point level. The `view-boundaries` axis had no stable machine-addressable concrete-boundary subject, so one broad topology decision could satisfy global probe/review completeness while silently standing in for several materially contestable boundaries.

Implemented invariant:

- `view-boundaries` declares `subject_scope: view-boundary`;
- Interface Topology semantic review records stable material boundary ids, participants, materiality, contestability and disposition;
- every materially contestable boundary references decision evidence whose explored decision point explicitly names that boundary as a subject;
- subject-scoped decision probes are bound to that decision point and independently satisfy required strategy diversity and alternative coverage;
- deterministic material boundaries may omit artificial alternatives only with explicit accepted-constraint evidence and rationale;
- one decision may govern several boundaries only when semantic review explicitly attests a shared decision group and semantic equivalence.

Negative mutations:

- broad decision false coverage: REJECTED with `VIEW_BOUNDARY_DECISION_COVERAGE_MISSING`;
- boundary mentioned but unchallenged: REJECTED with `DECISION_SUBJECT_PROBE_DIVERSITY_INSUFFICIENT`;
- indiscriminate shared decision: REJECTED with `VIEW_BOUNDARY_SHARED_DECISION_REVIEW_REQUIRED`.

Positive controls:

- boundary-local merge/separate exploration: ACCEPTED;
- deterministic boundary alongside a locally explored contestable boundary: ACCEPTED without synthetic alternatives;
- semantically attested shared decision across multiple boundaries: ACCEPTED.

GREEN evidence:

- validated implementation head: `02eda9b6615ec3e5a7c6ef3b350bfbd792c430c3`;
- `harness core` / full `make harness-check`: run `37591066168` PASS;
- `Greenfield Engineering Graph`: run `37591066142` PASS;
- implementation PR: #206.

Integration evidence: PR #206 was squash-merged to Harness `main` as `f48049dc5458043660158cbf8526a7105cc20817`; `HARNESS-003 -> INTEGRATED`.

### HARNESS-008 — user-facing basis for topology separation

Status history for WP-H4:

```
REGISTERED
  -> REPRODUCED
  -> HARNESS_RED
  -> FIX_IMPLEMENTED
  -> HARNESS_GREEN
```

RED evidence:

- regression: WP-H4 block in `tests/test_decision_governance.py`, responsibility-shaped boundary false green;
- validated RED-only commit: `494431a4eb890e1294461d2bc4843d99aaed3269`;
- evidence PR: #207 (closed without merge);
- `harness core` run `37591336184` showed baseline semantic acceptance returned `ACCEPTED` when the only basis for separate `VIEW-A` / `VIEW-B` was different tasks/application capabilities.

Root cause:

Topology guidance rejected implementation-shaped entities/routes/components, but admission had no structured semantic classification of boundary rationale. Task/application responsibility decomposition could therefore be restated as user-semantic prose and become an apparently valid separate destination without independent user-facing boundary evidence.

Implemented invariant:

- `view-boundary-semantics` is required for `interface-topology-design`;
- semantic review classifies rationale bases as `USER_FACING`, `UPSTREAM_RESPONSIBILITY`, `IMPLEMENTATION_STRUCTURE` or `OTHER`; deterministic assurance consumes that classification and never keyword-matches prose;
- a material `SEPARATE` outcome requires at least one accepted `USER_FACING` basis;
- task/journey/application capability/use-case/component/route/data ownership remains analysis input and may coexist with a `MERGED` user-facing outcome;
- IA locations remain conceptual organization/findability inputs and do not imply views, pages or routes.

Negative mutation:

- responsibility-shaped separate view with no independent user-facing basis: REJECTED with `VIEW_BOUNDARY_USER_FACING_BASIS_REQUIRED`.

Positive freedom controls:

- two upstream task/application responsibilities in one user-facing area: ACCEPTED;
- one task may span multiple views when a real user-facing boundary basis is present: ACCEPTED by the same local-boundary control;
- real independent resume/mode/authorization or commit/recovery semantics may justify separation without prescribing a universal topology.

GREEN evidence:

- validated implementation head: `02eda9b6615ec3e5a7c6ef3b350bfbd792c430c3`;
- `harness core` / full `make harness-check`: run `37591066168` PASS;
- `Greenfield Engineering Graph`: run `37591066142` PASS;
- implementation PR: #206.

Prep calibration:

- current Prep `.harness/candidates/frontend-boundary-topology-exploration.yaml` has one broad `preparation-view-boundaries` decision and no boundary-local subject for `VIEW-TARGETS ↔ VIEW-TARGET`;
- current topology admission selects `task-responsibility-views-with-contextual-recovery`, while IA keeps `LOC-TARGETS` and `LOC-TARGET` as conceptual locations and explicitly leaves page/view count downstream;
- corrected Harness therefore requires this concrete material boundary to be explicitly re-examined; WP-H4 does not decide whether the eventual result is merge or separation.

Integration evidence: PR #206 was squash-merged to Harness `main` as `f48049dc5458043660158cbf8526a7105cc20817`; `HARNESS-008 -> INTEGRATED`.

Prep dependency disposition after WP-H4:

- `PREP-UX-002`: `REGISTERED -> REPRODUCED -> ROOT_CAUSE_CLASSIFIED -> HARNESS_DISPOSITIONED`. Current Prep evidence reproduces the peer `Targets` / `Target` split and shows that its only topology exploration is the broad `preparation-view-boundaries` decision; HARNESS-003 and HARNESS-008 are both integrated. This disposition requires later Prep revalidation of the concrete boundary and does not prescribe merge.
- `PREP-UX-013`: `REGISTERED -> REPRODUCED -> ROOT_CAUSE_CLASSIFIED -> HARNESS_DISPOSITIONED`. Current Prep topology maps user-facing destinations directly to distinct task responsibilities/IA locations while the broad decision evidence does not independently prove each material user-facing boundary; both mapped Harness dependencies are integrated.
- Prep remains unchanged, `.harness-version` is unchanged, and WP-H4 does not enter `PREP_REVALIDATION`.


Prep dependency disposition after WP-H3:

- `PREP-UX-005`: `REPRODUCED -> ROOT_CAUSE_CLASSIFIED -> HARNESS_DISPOSITIONED`; its mapped HARNESS-001, HARNESS-002 and HARNESS-005 dependencies are all integrated. The observed missing local apply/select behavior remains a Prep repair/revalidation concern; no Prep repair starts in WP-H3.
- `PREP-UX-014`: `REPRODUCED -> ROOT_CAUSE_CLASSIFIED -> HARNESS_DISPOSITIONED`; HARNESS-002 and HARNESS-005 are integrated. Its local-filter realization remains for later Prep revalidation.
- `PREP-UX-001`, `PREP-UX-003`, `PREP-UX-004` and `PREP-UX-006` now have their mapped WP-H3 Harness dependencies terminal, but their own statuses remain `REGISTERED`; WP-H3 does not skip their reproduction/root-cause states.
- `PREP-UX-012` has HARNESS-004 terminal but still depends on unresolved HARNESS-006; `PREP-UX-007` likewise remains blocked on HARNESS-006.
- Prep and `.harness-version` remain unchanged. No Prep revalidation is started.

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


### HARNESS-006 — task-grounded representation selection

Status history for WP-H5:

```
REGISTERED
  -> REPRODUCED
  -> HARNESS_RED
  -> FIX_IMPLEMENTED
  -> HARNESS_GREEN
  -> INTEGRATED
```

RED evidence:

- regression: WP-H5 block in `tests/test_decision_governance.py`;
- RED-only commit: `09a77ce5c648aca4f9f1da5acce67db1c466362d`;
- `harness core` run `37593472987` failed because baseline preflight returned `ACCEPTED` with no findings for material `REP-COMPARE-A-B` while all legacy Presentation axes were complete;
- the same RED block also covers homogeneous collection fallthrough with `REP-HOMOGENEOUS-COLLECTION`.

Root cause:

Presentation/System and Screen/View semantic review had no machine-addressable material representation subjects, so Decision Governance could close broad presentation/composition axes while collection/comparison form fell through to existing patterns or primitives. Decision Exploration evaluation also discarded per-alternative material effects, so Governance could not prove that a task-relevant dimension such as cross-entity alignment was actually challenged.

Implemented invariant:

- Presentation System and Screen/View now require semantic `representation-selection-applicability` review;
- semantic review records stable representation-subject ids, task/information/accepted-constraint basis, material dimensions, required challenge strategies and DECIDE/INHERIT/OVERRIDE disposition;
- both knowledge kinds expose subject-scoped `representation-selection` Decision Governance;
- Decision Exploration preserves alternative material effects, and Governance proves required challenge coverage plus actual variation of every required material dimension;
- implementation primitives and legacy implementations cannot be the sole authority for a material representation choice;
- a local decision against an inherited shared default must be an explicit justified OVERRIDE;
- no card/list/table/detail/graph enum or Prep-specific representation policy is encoded.

Negative mutations:

- unexplored material comparison: REJECTED;
- cosmetic card-only diversity for an alignment requirement: REJECTED with `REPRESENTATION_REQUIRED_DIMENSION_NOT_CHALLENGED`;
- implementation primitive as sole authority: REJECTED with `REPRESENTATION_TASK_BASIS_REQUIRED`;
- homogeneous collection fallthrough: REJECTED;
- silent local deviation from a shared default: REJECTED with `REPRESENTATION_OVERRIDE_DISPOSITION_REQUIRED`.

Positive controls:

- justified rich-entity cards: ACCEPTED;
- non-table homogeneous collection: ACCEPTED;
- synchronized-column aligned comparison: ACCEPTED without requiring an HTML table;
- graph/mixed relational representation: ACCEPTED;
- explicit shared-default override with rationale: ACCEPTED;
- wide-aligned/narrow-serialized responsive transformation: ACCEPTED.

Prep calibration:

- `PREP-UX-007`: `REPRODUCED -> ROOT_CAUSE_CLASSIFIED`; earliest owner `PS-PATTERN-TARGET-COMPARISON`. Canonical Presentation/Screen semantics require aligned comparison over common requirement/state/gap dimensions, while `TargetDirectionFeature.tsx` renders each candidate as an independent `comparison-card`.
- `PREP-UX-008`: `REGISTERED -> REPRODUCED -> ROOT_CAUSE_CLASSIFIED`; earliest owner `PS-PATTERN-STATE-BASIS` / local application `SV-CURRENT`. Current Position renders repeated `state-card` and `gap-card` collections without representation-specific decision evidence.
- `PREP-UX-009`: `REGISTERED -> REPRODUCED -> ROOT_CAUSE_CLASSIFIED`; earliest owner `SV-TARGET`. Target requirements are the dominant accepted work surface but are emitted as repeated `requirement-card` surfaces without a task-grounded collection representation decision.
- `PREP-UX-010`: `REGISTERED -> REPRODUCED -> ROOT_CAUSE_CLASSIFIED`; earliest owner Presentation System reusable representation policy. Shared `DataTable` exists and Knowledge uses it, while other homogeneous collections use repeated surfaces; no accepted representation default/override policy explains the difference. This does not imply broader DataTable use.
- `PREP-UX-011`: `REGISTERED -> REPRODUCED -> ROOT_CAUSE_CLASSIFIED`; earliest owner Presentation System. Current accepted decision evidence has application-surface/knowledge-representation/information-density/control-surface but no material collection/comparison representation-selection decision.
- `PREP-UX-012`: `REGISTERED -> BLOCKED:same-role-equivalence-not-established`. Current evidence shows different accepted actions/roles: candidate comparison multi-select, candidate-to-continue, Next-focus and support selection. Their different checkbox/radio mechanics do not prove same-role pattern inconsistency. Resume only with evidence identifying two instances of the same accepted interaction role whose materially different mechanics lack rationale.
- `PREP-UX-015`: `REGISTERED -> REPRODUCED -> ROOT_CAUSE_CLASSIFIED`; earliest owner Presentation System representation policy. Repeated `Surface`/`ChoiceCard` use across comparison/state/requirements confirms default-container bias where no material representation decision exists; cards remain valid after explicit exploration.
- `PREP-UX-016`: `REGISTERED -> REPRODUCED -> ROOT_CAUSE_CLASSIFIED`; earliest owner Presentation System / Screen decision evidence. Current exploration contains no representation-selection subject and therefore does not explicitly challenge aligned/structured alternatives for the reproduced comparison/collection cases.

GREEN evidence:

- validated implementation head: `c62b83283e7faef0fe292b5c3bee975774baef82`;
- `harness core` / full `make harness-check`: run `37594152582` PASS;
- `Greenfield Engineering Graph`: run `37594152606` PASS;
- implementation PR: #209.

Integration evidence: PR #209 was squash-merged to Harness `main` as `f5338be9f2f5cfb87dd967f6cee24ed62be94092`; `HARNESS-006 -> INTEGRATED`.

Prep dependency disposition after WP-H5:

- `PREP-UX-007`: `ROOT_CAUSE_CLASSIFIED -> HARNESS_DISPOSITIONED`; HARNESS-001, HARNESS-002 and HARNESS-006 are all integrated. Later Prep revalidation must reopen the target-comparison representation decision; H5 does not prescribe table versus matrix/rows/columns.
- `PREP-UX-008`: `ROOT_CAUSE_CLASSIFIED -> HARNESS_DISPOSITIONED`; HARNESS-006 is integrated. Later Prep revalidation must decide the Current Position collection representation from task semantics.
- `PREP-UX-009`: `ROOT_CAUSE_CLASSIFIED -> HARNESS_DISPOSITIONED`; HARNESS-006 is integrated. Later Prep revalidation must decide the Target requirements representation rather than inherit repeated cards by default.
- `PREP-UX-010`: `ROOT_CAUSE_CLASSIFIED -> HARNESS_DISPOSITIONED`; HARNESS-006 is integrated. DataTable remains an implementation primitive, not authority for the future decision.
- `PREP-UX-011`: `ROOT_CAUSE_CLASSIFIED -> HARNESS_DISPOSITIONED`; HARNESS-006 is integrated. The corrected Harness now provides the missing reusable representation decision space.
- `PREP-UX-015`: `ROOT_CAUSE_CLASSIFIED -> HARNESS_DISPOSITIONED`; HARNESS-006 is integrated. Later Prep revalidation may retain cards where explicitly justified.
- `PREP-UX-016`: `ROOT_CAUSE_CLASSIFIED -> HARNESS_DISPOSITIONED`; HARNESS-006 is integrated. Material comparison/collection subjects now require task-appropriate alternative challenge.
- `PREP-UX-012` remains `BLOCKED:same-role-equivalence-not-established` even though HARNESS-004 and HARNESS-006 are integrated: current evidence establishes several different selection roles, not two instances of the same accepted role with unjustified representation mechanics.
- Prep remains unchanged, `.harness-version` is unchanged, and WP-H5 does not enter `PREP_REVALIDATION`.



### HARNESS-007 — first-missing-link assurance trace projection

Status history for WP-H6:

```
REGISTERED
  -> REPRODUCED
  -> HARNESS_RED
  -> FIX_IMPLEMENTED
  -> HARNESS_GREEN
  -> INTEGRATED
```

RED evidence:

- regression: `tests/test_traceability_projection.py::test_t1_interaction_to_screen_missing_is_first`;
- validated RED-only head: `e6ef3ccffec7dae9ad44c8d8d00fdd9e80ff372f`;
- `harness core` run `37597009341` failed with `ModuleNotFoundError: harness.assurance.traceability_projection` after CI policy had accepted the registered focused check;
- the RED therefore proves absence of the standard composed diagnostic projection without weakening or re-breaking H1-H6/H8.

Root cause:

H1-H6/H8 exposed machine-addressable semantic, observable-realization, Test Design and executable-conformance truth, but no standard read model composed those accepted results per independently addressable root obligation. Reviewers still had to correlate several evaluations manually and determine the earliest unusable edge themselves.

Projection contract:

- `harness.assurance.traceability_projection.build_traceability_projection` is a deterministic disposable read model in the Assurance bounded context;
- the request selects exact semantic ids/capabilities, Test Design contract id and stable operation/oracle ids;
- Interaction -> Screen and Screen -> Test Design consume existing `harness-semantic-derivation-evaluation` results and accepted links/provenance;
- Test Design contract accounting consumes canonical `test-design/v1` stable obligation ids;
- Test Design -> executable consumes H2 `harness-test-realization-evaluation`; executable source code is never reinterpreted;
- supplied lifecycle/currentness state may mark the earliest unusable edge `STALE`; the projection does not recompute currentness;
- output is `harness-traceability-projection` with stage statuses, semantic ids, evidence/finding refs, overall status, deterministic `first_missing_link` and optional `missing_obligation`;
- an upstream unresolved edge leaves later stages `BLOCKED_BY_UPSTREAM`/`NOT_EVALUABLE` rather than emitting misleading downstream root causes;
- accepted `NOT_APPLICABLE` dispositions terminate as `DISPOSITIONED`; one-to-many accepted realizations are preserved;
- the projection is noncanonical, supplies no Capability and is not a semantic acceptance gate.

Mutation and positive-control evidence:

- T1 Interaction -> Screen missing: `INTERACTION_TO_SCREEN`;
- T2 Screen -> Test Design missing: `SCREEN_TO_TEST_DESIGN`;
- T3 missing stable Test Design operation: `TEST_DESIGN_CONTRACT` with `missing_obligation`;
- T4 Test Design -> executable missing: H2 finding reused at `TEST_DESIGN_TO_EXECUTABLE`;
- T5 unresolved semantic correspondence: `QUESTION` at the owning upstream edge, with later stages blocked;
- complete chain returns `COMPLETE` and null first missing link;
- legitimate disposition, one-to-many realization, unrelated-evidence invariance and materially different executable organizations remain valid;
- `test_composed_vertical_chain_complete_then_exact_middle_mutation` composes H3 derivation, Screen -> Test Design derivation, H2 executable realization and H7 projection, then removes exactly the Screen -> Test Design APPLY link and identifies that edge.

Program regression matrix:

- `spec/assurance/prep-harness-remediation-regression-matrix-v0.yaml` maps HARNESS-001..008 only to RED/GREEN/positive executable evidence and owner checks;
- `checks/validate_prep_harness_regression_matrix.py` requires all eight ids, live test/scenario paths and anchors, at least one positive/freedom control per id, and registered owner checks;
- mutable register fields such as status/priority/description are forbidden in the matrix, so this metadata cannot become a second defect/status register.

GREEN evidence:

- validated implementation head: `5f054abb352c47f1a4909b5d37f4d0f9ff0a3c78`;
- `harness core` / full `make harness-check`: run `37598091912` PASS;
- `Greenfield Engineering Graph`: run `37598091885` PASS;
- CI policy: run `37598091876` PASS;
- implementation PR: #211.

Integration evidence: PR #211 was squash-merged to Harness `main` as `24b748cde9b8082c3834662f9fbac74cea5b0294`; `HARNESS-007 -> INTEGRATED`.

Harness-phase closure audit:

- HARNESS-001: INTEGRATED;
- HARNESS-002: INTEGRATED;
- HARNESS-003: INTEGRATED;
- HARNESS-004: INTEGRATED;
- HARNESS-005: INTEGRATED;
- HARNESS-006: INTEGRATED;
- HARNESS-007: INTEGRATED;
- HARNESS-008: INTEGRATED;
- Harness remediation phase is terminal for HARNESS-001..008;
- next program stage may be Stage HI: final Harness baseline freeze -> Prep `.harness-version` repin -> Harness currentness/coverage evaluation;
- Stage HI is not executed by WP-H6.

Prep calibration/status:

- the PREP-UX-005-shaped APPLY/STATE fixture reproduces why the projection is useful: neighboring current-scope state/evidence cannot hide the missing APPLY Interaction -> Screen realization;
- Prep is unchanged and its `.harness-version` is unchanged; no Prep revalidation is started;
- no PREP-UX status transition is caused by H7; `PREP-UX-012` remains `BLOCKED:same-role-equivalence-not-established`.

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

Stage HI is COMPLETE.

HARNESS_REMEDIATION_BASELINE:

- execution baseline: `ed04058ff35ffbbaf735d0ecbd7c1f592e3abf71`;
- HARNESS-001..008: terminal `INTEGRATED`;
- this execution baseline remains frozen even after later register-only program commits.

Prep repin:

- starting Prep `main`: `d31a5f8ebe1ad7a526567efb302e52e29579ce6b`;
- `.harness/harness-binding.json`: `f6ef8bbd9b01da5e94b21b1b4785ca7a13bb478d` -> `ed04058ff35ffbbaf735d0ecbd7c1f592e3abf71`;
- `.harness-version`: `f6ef8bbd9b01da5e94b21b1b4785ca7a13bb478d` -> `ed04058ff35ffbbaf735d0ecbd7c1f592e3abf71`;
- Prep PR #81 was squash-merged to `main` as `a3eed460b81f50ee299f45751168d1932a97f99e`;
- final Prep diff contained only the two Harness pin surfaces.

Stage-HI validation evidence:

- temporary non-gating diagnostic run `37600943584`, job `112724878560`;
- Consumer API sync materialized `/home/runner/.cache/harness/v1/ed04058ff35ffbbaf735d0ecbd7c1f592e3abf71`: PASS;
- legacy checkout resolved exact `ed04058ff35ffbbaf735d0ecbd7c1f592e3abf71`: PASS;
- `python tools/semantic_baseline.py`: PASS — 34 semantic evaluations, 109 derivation evaluations, 34 lifecycle providers;
- `python tools/check_harness_integration.py`: PASS;
- `python tools/full_harness_revalidate.py`: EXPECTED INCOMPLETE at `CURRENT-REVALIDATION`, with `semantic_gaps=[]`;
- `python tools/validate_docs.py`: PASS;
- final required Prep PR validation run `37601065003`: PASS.

First actionable revalidation frontier:

1. `prep.user-journeys` / `USER-JOURNEYS` — `STALE` under `APPLICATION-DESIGN` because the accepted acceptance-policy fingerprint differs from the current Harness policy.
2. `prep.conceptual-interface-model` and `prep.information-architecture` — downstream `STALE` because `prep.user-journeys` is stale; they are not independent root causes yet.
3. `prep.interaction-design`, `prep.interface-topology`, `prep.presentation-system`, and `prep.screen-view-design` also have direct acceptance-policy currentness mismatches under the strengthened Harness, but their repair order must respect the upstream `user-journeys` frontier.

Defect impact:

- PREP-UX-001..016 statuses remain unchanged by Stage HI;
- the new baseline makes the registered defects eligible for the next canonical revalidation phase but does not move them to `PREP_REVALIDATION`;
- `PREP-UX-012` remains `BLOCKED:same-role-equivalence-not-established`;
- no new defect class was discovered.

Program state:

- Harness remediation phase: COMPLETE;
- Prep canonical revalidation: AUTHORIZED BUT NOT STARTED;
- no Prep canonical/design/frontend repair was performed during Stage HI;
- the previously suggested WP-P1 ordering must not skip the earlier `prep.user-journeys` currentness dependency; the managing chat must choose whether to add that prerequisite to WP-P1 or authorize a bounded prerequisite stage first.

### STAGE-P0 completion record — prep.user-journeys prerequisite revalidation

This record supersedes the Stage-HI *current frontier* statement above while preserving Stage HI as execution history.

STAGE-P0:

- result: COMPLETE;
- capability: `prep.user-journeys`;
- authority: `APPLICATION-DESIGN`;
- starting Prep `main`: `a3eed460b81f50ee299f45751168d1932a97f99e`;
- old acceptance: `PREP-USER-JOURNEYS-STRICT-5`;
- reproduced stale cause: acceptance-policy fingerprint mismatch;
- old candidate under the corrected H1 policy: REJECTED with `SEMANTIC_REVIEW_CHECKS_MISSING` for `independent-obligation-granularity` and `INDEPENDENT_OBLIGATION_REVIEW_REQUIRED`.

Journey revalidation:

- canonical `docs/application/user-journeys.md`: UNCHANGED;
- reason: canonical Journey meaning already expressed the required learner operations; the accepted semantic admission surface was too coarse;
- independent-obligation-granularity: PASS;
- independently accounted obligations: 60;
- Required Capability apply/select scope independently preserved: YES — `UJ-KNOWLEDGE-APPLY-CAPABILITY-SCOPE`;
- Required Capability clear scope independently preserved: YES — `UJ-KNOWLEDGE-CLEAR-CAPABILITY-SCOPE`;
- incoming derivations from `prep.task-model`, `prep.application-design`, `prep.application-process.activity-evidence-cycle`, and `prep.application-process.prepare-support`: PASS;
- new acceptance: `PREP-USER-JOURNEYS-STRICT-6`;
- `prep.user-journeys`: CURRENT.

Publication and validation:

- bounded publication diagnostic workflow run: `37603430706`;
- pinned Consumer Pack: `ed04058ff35ffbbaf735d0ecbd7c1f592e3abf71`;
- typed `user-journey-design` route: PASS;
- `python tools/semantic_baseline.py`: PASS;
- `python tools/check_harness_integration.py`: PASS;
- `python tools/full_harness_revalidate.py`: EXPECTED INCOMPLETE with `semantic_gaps=[]`;
- `python tools/validate_docs.py`: PASS;
- no downstream artifact was reaccepted;
- temporary revalidation runner/workflow were removed before integration;
- Prep PR #82 required validation run `37603609935`: PASS;
- Prep PR #82 squash-merged to `main` as `24a2ca1dcea5f258333c6f27264f591586c9ea8d`.

Post-P0 first actionable frontier:

1. `prep.conceptual-interface-model` / `HUMAN-INTERFACE-DESIGN` — STALE because its accepted `prep.user-journeys` semantic surface is `PREP-USER-JOURNEYS-STRICT-5` while the current upstream is `PREP-USER-JOURNEYS-STRICT-6`, including the newly independent Journey atoms.
2. Downstream Information Architecture and later Human Interface / verification / architecture capabilities remain stale and must be handled only in their own authorized stages.

Defect impact:

- PREP-UX-001..016: UNCHANGED;
- PREP-UX-012: `BLOCKED:same-role-equivalence-not-established`;
- new PREP defects: NONE.

Program state after STAGE-P0:

- `HARNESS_REMEDIATION_BASELINE` remains `ed04058ff35ffbbaf735d0ecbd7c1f592e3abf71`;
- Harness remediation mechanisms remain unchanged by this register-only update;
- STAGE-P0: COMPLETE;
- next stage: not started; the managing chat chooses it from the new frontier.

### STAGE-P0-CIM completion record — conceptual-interface-model revalidation

This record supersedes the STAGE-P0 *current frontier* statement above while preserving prior stages as execution history.

STAGE-P0-CIM:

- result: COMPLETE;
- capability: `prep.conceptual-interface-model`;
- authority: `HUMAN-INTERFACE-DESIGN`;
- starting Prep `main`: `24a2ca1dcea5f258333c6f27264f591586c9ea8d`;
- old acceptance: `PREP-CONCEPTUAL-INTERFACE-MODEL-STRICT-5`;
- reproduced stale cause: accepted `prep.user-journeys` semantic surface was `PREP-USER-JOURNEYS-STRICT-5` while the current upstream provider is `PREP-USER-JOURNEYS-STRICT-6`, with newly independent Journey atoms.

Conceptual Interface revalidation:

- canonical `docs/interface/conceptual-interface-model.yaml`: UNCHANGED;
- reason: the canonical model already preserves candidate Target comparison, active preparation Target, learner-state separation, reversible Capability-derived Knowledge scope, Knowledge identity, and the Gap/uncertainty -> Next Focus relationship;
- current Journey exhaustive accounting: PASS — 78 required sources, 76 accepted derivation links, 2 explicit dispositions, 0 unresolved;
- `UJ-KNOWLEDGE-APPLY-CAPABILITY-SCOPE`: NOT_APPLICABLE to additional CIM semantics because invocation belongs to Interaction Design while `CIM-KNOWLEDGE-SCOPE` and `CIM-REL-CAPABILITY-KNOWLEDGE` preserve the underlying reversible conceptual scope;
- `UJ-KNOWLEDGE-CLEAR-CAPABILITY-SCOPE`: same boundary; clear invocation remains downstream Interaction behavior;
- Target comparison / candidate / active Target / learner-state conceptual distinctions: sufficient without introducing interaction-role entities;
- Capability vs Next Focus / PreparationIntent distinction and Gap/uncertainty -> Next Focus relationship: sufficient;
- current prerequisites `prep.task-model`, `prep.user-journeys`, `prep.application-design`, `prep.knowledge-model`, `prep.learning-design`, and `prep.learner-model`: CURRENT;
- new acceptance: `PREP-CONCEPTUAL-INTERFACE-MODEL-STRICT-6`;
- `prep.conceptual-interface-model`: CURRENT;
- no downstream artifact was reaccepted.

Publication and validation:

- bounded publication diagnostic runs: `37605757802` and `37605969619`;
- pinned Consumer Pack / Harness runtime: `ed04058ff35ffbbaf735d0ecbd7c1f592e3abf71`;
- `python tools/semantic_baseline.py`: PASS;
- `python tools/check_harness_integration.py`: PASS;
- `python tools/full_harness_revalidate.py`: EXPECTED INCOMPLETE with `semantic_gaps=[]`; remaining failures are downstream currentness gaps;
- `python tools/validate_docs.py`: PASS;
- maintained Anki reference tests: PASS;
- temporary revalidation runner/workflow were removed before integration;
- Prep PR #83 required validation run `37606175893`: PASS;
- Prep PR #83 squash-merged to `main` as `ea6f5977df8e71937a38ab2ea01721f581a00939`.

Post-P0-CIM first actionable frontier:

1. `prep.information-architecture` / `HUMAN-INTERFACE-DESIGN` — STALE against current `PREP-USER-JOURNEYS-STRICT-6` and `PREP-CONCEPTUAL-INTERFACE-MODEL-STRICT-6`; revalidation belongs to its own stage.
2. Interaction Design, Presentation System and later Human Interface / verification / architecture capabilities remain downstream stale and are not reaccepted here.

Defect impact:

- PREP-UX-001..016: UNCHANGED;
- PREP-UX-012: `BLOCKED:same-role-equivalence-not-established`;
- new PREP defects: NONE.

Program state after STAGE-P0-CIM:

- `HARNESS_REMEDIATION_BASELINE` remains `ed04058ff35ffbbaf735d0ecbd7c1f592e3abf71`;
- Harness runtime/remediation mechanisms remain unchanged by this register-only update;
- STAGE-P0-CIM: COMPLETE;
- next stage: not started; the managing chat chooses it from the new frontier.

### STAGE-P1-IA completion record — information-architecture revalidation

This record supersedes the STAGE-P0-CIM *current frontier* statement above while preserving prior stages as execution history.

STAGE-P1-IA:

- result: COMPLETE;
- capability: `prep.information-architecture`;
- authority: `HUMAN-INTERFACE-DESIGN`;
- starting Prep `main`: `ea6f5977df8e71937a38ab2ea01721f581a00939`;
- old acceptance: `PREP-INFORMATION-ARCHITECTURE-STRICT-6`;
- reproduced stale cause: accepted prerequisite surfaces were `PREP-USER-JOURNEYS-STRICT-5` and `PREP-CONCEPTUAL-INTERFACE-MODEL-STRICT-5`, while current providers are STRICT-6.

Target grouping decision:

- evaluated separate sibling locations, one unified Target area, and one Target parent with distinct sublocations;
- selected: one `Targets` parent information area with distinct `Candidate comparison` and `Active Target` sublocations;
- rationale: comparison and active-Target work organize information about the same user-facing Target concept and form a reversible compare -> choose -> establish/refine -> reconsider continuum; peer singular/plural locations were not justified merely by separate Journey/task responsibilities;
- a fully undifferentiated single location was rejected because candidate-comparison and active-Target information needs remain materially distinct;
- the decision has no page/view/route implication; IA location identity remains conceptual organization/findability only;
- responsibility/task/frontend decomposition was not used as proof.

Canonical IA and derivation:

- canonical `docs/interface/information-architecture.yaml`: CHANGED to the parent+sublocations grouping;
- active Target remains shared preparation context;
- Knowledge remains independently findable;
- Required Capability-derived Knowledge scope remains local exploration state and apply/clear does not become global truth;
- Required Capability, Knowledge scope and Next Focus/PreparationIntent remain distinct;
- Journey STRICT-6 exhaustive accounting: PASS — 78 required, 71 linked, 7 explicit IA-boundary dispositions, 0 unresolved;
- CIM STRICT-6 exhaustive accounting: PASS — 31/31 linked, 0 unresolved;
- Task Model exhaustive accounting: PASS — 115/115 linked, 0 unresolved;
- current prerequisites `prep.conceptual-interface-model`, `prep.task-model`, and `prep.user-journeys`: CURRENT;
- new acceptance: `PREP-INFORMATION-ARCHITECTURE-STRICT-7`;
- `prep.information-architecture`: CURRENT;
- no downstream artifact was reaccepted.

Publication and validation:

- bounded publication diagnostic run: `37607841300`;
- pinned Consumer Pack / Harness runtime: `ed04058ff35ffbbaf735d0ecbd7c1f592e3abf71`;
- `python tools/semantic_baseline.py`: PASS;
- `python tools/check_harness_integration.py`: PASS;
- `python tools/full_harness_revalidate.py`: EXPECTED INCOMPLETE with `semantic_gaps=[]`; remaining failures are downstream currentness gaps;
- `python tools/validate_docs.py`: PASS;
- maintained Anki reference tests: PASS;
- temporary revalidation runner/workflow were removed before integration;
- Prep PR #84 required validation run `37608052810`: PASS;
- Prep PR #84 squash-merged to `main` as `48746464d751904e6960951b59203b35a5aff94e`.

Defect transitions:

- PREP-UX-002: `HARNESS_DISPOSITIONED -> PREP_REVALIDATION`; IA-local split was corrected, while route/view/navigation realization remains for downstream Topology revalidation;
- PREP-UX-013: `HARNESS_DISPOSITIONED -> PREP_REVALIDATION`; IA grouping is now explicitly based on user-facing conceptual/task cohesion, while downstream navigation realization remains pending;
- PREP-UX-012 remains `BLOCKED:same-role-equivalence-not-established`;
- all other PREP-UX statuses: UNCHANGED;
- new PREP defects: NONE.

Post-P1-IA first actionable frontier:

1. `prep.interaction-design` / `HUMAN-INTERFACE-DESIGN` — STALE due its current acceptance-policy mismatch and its accepted `prep.user-journeys` surface remaining STRICT-5 while current Journey is STRICT-6.
2. `prep.interface-topology` is also STALE, including the changed IA STRICT-7 surface, but is not the earlier actionable frontier because it requires `prep.interaction-design`, which is still STALE.

Program state after STAGE-P1-IA:

- `HARNESS_REMEDIATION_BASELINE` remains `ed04058ff35ffbbaf735d0ecbd7c1f592e3abf71`;
- Harness runtime/remediation mechanisms remain unchanged by this register-only update;
- STAGE-P1-IA: COMPLETE;
- next stage: not started.



## Stage P1 Interaction Design revalidation — 2026-10-07

Prep evidence: PR `lehater/prep#85` was squash-merged to Prep `main` as `e7f0e73a5bee52a9e61633766d7841fbe20371ad`. The scoped revalidation published `PREP-INTERACTION-DESIGN-STRICT-6` and restored `prep.interaction-design = CURRENT` without reaccepting downstream artifacts.

- `PREP-UX-003`: `REGISTERED -> REPRODUCED -> ROOT_CAUSE_CLASSIFIED -> HARNESS_DISPOSITIONED -> PREP_REVALIDATION`. Reproduction confirmed that locally correct Target behavior lacked an explicit cross-context role contract. The accepted Interaction now defines `selected-for-comparison`, `candidate-to-continue`, and `active-target`, including side effects, forbidden side effects, and `candidate-to-continue -> active-target`. Merely opened/inspected Target is not a fourth role because no distinct role lifecycle or side effect was established.
- `PREP-UX-005`: `HARNESS_DISPOSITIONED -> PREP_REVALIDATION`. `UJ-KNOWLEDGE-APPLY-CAPABILITY-SCOPE` and `UJ-KNOWLEDGE-CLEAR-CAPABILITY-SCOPE` derive to separate accepted Interaction ACTION assertions. Concrete control realization and implementation remain downstream.
- `PREP-UX-006`: `REGISTERED -> REPRODUCED -> ROOT_CAUSE_CLASSIFIED -> HARNESS_DISPOSITIONED -> PREP_REVALIDATION`. The Interaction-owned omission was the missing explicit cross-context distinction: Required Capability may scope Knowledge while Next Focus is PreparationIntent; applying/clearing Capability scope cannot silently choose/revise Next Focus, and changing Next Focus cannot silently mutate Capability identity/scope. Concrete presentation remains downstream.
- `PREP-UX-014`: `HARNESS_DISPOSITIONED -> PREP_REVALIDATION`. Interaction now independently requires apply and clear Capability-scope actions; the local filter/control realization remains a downstream Screen/Presentation concern.
- `PREP-UX-001`: unchanged `REGISTERED`. Interaction already preserves Active Target as visible/recoverable preparation context; earliest remaining owner is downstream presentation/screen/usability.
- `PREP-UX-004`: unchanged `REGISTERED`. Required Capability remains semantically inspectable in Target requirements and usable as Knowledge scope; the remaining defect is observable presentation downstream.
- `PREP-UX-012`: unchanged `BLOCKED:same-role-equivalence-not-established`. Revalidated roles demonstrate that comparison selection, candidate-to-continue, and active Target are materially different roles; no two occurrences of the same accepted role with unjustified inconsistent mechanics were established.
- `PREP-UX-002` and `PREP-UX-013`: unchanged at `PREP_REVALIDATION`.
- No Prep defect advances to `PREP_IMPLEMENTATION` in this stage.
- First new actionable Prep frontier after publication is `prep.interface-topology`; this register update does not start that stage.
- Harness runtime/pin is unchanged: `ed04058ff35ffbbaf735d0ecbd7c1f592e3abf71`.
