# Real-project assurance adoption v0

Status: completed for the initial two-slice adoption batch.

## Purpose

Exercise the completed source-to-derivation assurance chain on new real project
slices without extending Harness in advance.

The adoption question is operational:

- which assurance steps apply unchanged;
- where a real project produces RED;
- where repeated manual work may justify later automation;
- which defect classes recur;
- where semantic judgement is still necessary.

The experiment does not reopen the completed trust-boundary or open-world
completeness research.

## Baselines

Harness:

`lehater/harness@9dd77c9eaa49115fa5082232dc74fb70da34a7be`

NAPMS:

`lehater/napms@42481577fab7f795cf3a2118b7b6f1c3c075d066`

Research branch:

`research/real-project-assurance-adoption-v0`

## Slice 1 — Application Components

Selected chain:

```text
problem evidence
    ->
application-components user need
    ->
product requirements
    ->
task / human journey
    ->
HTTP + human interface / screen design
    ->
frontend verification
    ->
frontend test design
```

This slice was not a primary target of the preceding request-authority,
materialization or backend verification-oracle calibration work.

### Canonical dependency basis

The pinned NAPMS graphs establish the relevant dependencies:

- `FIRST-MVP-HCD-PROBLEM-EVIDENCE`
  -> `FIRST-MVP-HCD-USER-NEEDS`
  -> `FIRST-MVP-REQUIREMENTS`;
- application-components Task Model and User Journey consume the accepted HCD
  requirement surface;
- frontend Human Interface / Screen View design consumes the accepted product,
  journey and interface knowledge;
- `engineering.frontend.verification` directly consumes
  `engineering.requirements.product-intent`;
- `engineering.frontend.test-design` directly consumes
  `engineering.frontend.verification`.

The accepted frontend subject-obligation registry explicitly binds
`Interaction management` to `REQ-INT-001`, `REQ-INT-002` and `REQ-INT-003`.

## Accepted acquisition scope

The existing project-owned dependency chain is used as the acquisition
contract. No new evidence taxonomy is introduced.

Required channels:

- `problem-evidence`;
- `user-needs`;
- `product-requirements`.

The executable scenario is:

`spec/scenario-suite/scenarios/real-project-assurance-adoption-application-components.yaml`

## End-to-end result

### Source-set coverage

Result: `ACCEPTED`.

All three acquisition channels are present and COMPLETE relative to the
accepted acquisition contract.

### Lossless source boundaries

Result: `ACCEPTED`.

The selected immutable Application Components source units are covered
losslessly:

- problem semantic-decision unit: 13 / 13 lines;
- `NEED-APP-01` unit: 13 / 13 lines;
- `REQ-APP-001` .. `REQ-INT-003` unit: 48 / 48 lines.

### Statement enumeration / disposition

Result: `COMPLETE`.

Local review identifies and dispositions:

- 3 problem semantic-decision statements;
- 1 Application Components user-need statement;
- 5 accepted product-requirement statements.

No statement in the selected semantic units remains undispositioned.

### Accepted requirement semantic surface

Result: `ACCEPTED`.

Five requirement atoms are admitted:

1. Application is a reusable communication profile independent from deployment
   realization;
2. Component is a communication participant/role, not a network device;
3. Interaction endpoints belong to the same Application and cross-Application
   Interaction is rejected;
4. multiple independently meaningful directed reasons may exist for one
   Component pair;
5. each Interaction carries complete minimal traffic semantics for its
   independently meaningful reason.

The extraction is explicitly locally reviewed for statement completeness and
meaning preservation.

### Requirements -> frontend verification

Result: `REJECTED`.

Four of five consumed requirement atoms have real counterparts in
`docs/plans/mvp-frontend-verification.yaml`:

- reusable Application meaning independent from deployment;
- Component participant semantics;
- distinct Interaction reasons;
- complete Interaction traffic semantics.

The fifth atom has no verification counterpart:

```text
REQ-INT-001.same-application-boundary
    =
Interaction endpoints belong to the same Application;
cross-Application Interaction is rejected.
```

Deterministic consumed-atom accounting therefore emits:

```text
UNDISPOSITIONED_SOURCE
owner_authority = VERIFICATION-DESIGN
```

The four declared links are separately reviewed as semantically justified. The
RED does not depend on an LLM verdict.

### Frontend verification -> test design

Result: `ACCEPTED` for the currently declared verification surface.

`mvp-frontend-test-design.yaml` faithfully mirrors the four Interaction /
Application / Component verification atoms that actually survived into frontend
verification.

Therefore the root loss is upstream of Test Design: Test Design inherits an
already incomplete Verification Design surface.

## Canonical corroboration

The missing atom is not an invented expectation.

NAPMS preserves the same semantic rule in several independent canonical places:

- `REQ-INT-001` explicitly prohibits cross-Application Interaction;
- the Application Components Task Model requires both Components to belong to
  one Application and requires rejection of cross-Application endpoint pairs;
- the Application Components Human Journey says the system rejects endpoint
  pairs crossing Application-profile boundaries;
- HTTP requirements require Interaction creation to resolve Component owners
  server-side and reject Components belonging to different Applications;
- the frontend subject-obligation registry explicitly includes `REQ-INT-001`.

But frontend verification says only:

> Interaction management supports distinct directed reasons and complete traffic
> semantics.

And `UI-INTERACTION` test intent says only:

> Directed Interactions preserve distinct reasons and traffic semantics.

The same-Application rejection invariant is absent from both downstream
oracles.

## Defect

Defect group:

`NAPMS-FRONTEND-VERIFICATION-CROSS-APPLICATION-INTERACTION-LOSS`

Classification:

- real canonical defect;
- semantic partial loss;
- structurally traced but semantically uncovered;
- owner: `VERIFICATION-DESIGN`;
- detection: deterministic after accepted atomization;
- semantic judgement required only for truth of the four positive links.

This is a new concrete NAPMS defect, but not a new generic Harness defect
class. It is another real instance of the already established
`structural traceability != semantic coverage` class.

## Slice 2 — Deployment management positive control

Purpose: test specificity on an independent real downstream slice rather than
search only for failures.

The control starts at the already accepted product-requirement boundary
`REQ-DEP-001` and follows:

```text
REQ-DEP-001
    ->
frontend verification
    ->
frontend test design
```

The immutable requirement unit is covered 7 / 7 lines, its single meaningful
statement is admitted, and its semantic atom is locally accepted:

```text
ComponentDeployment binds Component to Resource
independently from Resource current address.
```

Canonical frontend verification preserves the same meaning:

> Deployment management binds Component to Resource independent from current
> address.

`UI-DEPLOYMENT` preserves it again in Test Design.

Results:

- requirement boundary: `ACCEPTED`;
- statement coverage: `COMPLETE`;
- semantic surface: `ACCEPTED`;
- requirements -> frontend verification: 1 / 1, `ACCEPTED`;
- frontend verification -> test design: 1 / 1, `ACCEPTED`.

The positive control is executable in:

`spec/scenario-suite/scenarios/real-project-assurance-adoption-deployment-control.yaml`

This matters because the same mechanisms that reject the Application
Components omission accept an intact real derivation.

## Adoption findings after two slices

### Existing chain

No Harness framework change was required.

The following existing mechanisms were sufficient:

- `source.set`;
- `source.boundary`;
- `source.coverage`;
- `semantic.acceptance`;
- `semantic.derivation`;
- ordinary Scenario Suite composition.

Both scenario additions pass the unchanged `harness core` workflow.

### Real defects

One new concrete canonical defect was found:

`NAPMS-FRONTEND-VERIFICATION-CROSS-APPLICATION-INTERACTION-LOSS`.

No new generic defect class was needed. It is another real instance of
semantic partial loss despite structural traceability.

The Deployment control produced no defect.

### Repeated operational friction

Evidence authoring repeated across both slices:

- select exact immutable source units;
- calculate and record source-boundary fingerprints;
- enumerate meaningful statements;
- admit semantic atoms;
- declare atom links;
- bind narrow semantic review to positive links.

This is now repeated work, but it is not a capability failure of the existing
assurance model. Two slices are not enough evidence for a new Core entity,
semantic DSL or orchestration framework.

The first automation candidate, if later slices confirm the cost, is a
project-side evidence-authoring helper that prepares manifests/ledgers from
explicitly selected source units while leaving semantic admission and link
truth review explicit.

### LLM dependence

No live LLM execution was required in either slice.

After local atom admission:

- missing consumed atoms are deterministic;
- source and boundary completeness are deterministic;
- statement disposition coverage is deterministic;
- derivation coverage is deterministic;
- only positive atom-link truth remains semantic review.

Therefore this adoption batch does not justify increasing LLM use or changing
the GPT-6 Luna baseline policy.

## Initial adoption conclusion

The source-to-derivation assurance chain survives first real-project adoption
without architectural extension.

Observed behavior is discriminating:

- one real partial-loss defect is rejected and localized to
  `VERIFICATION-DESIGN`;
- one intact real derivation is accepted end-to-end from the selected
  requirement boundary.

The next useful scaling step is another independent project/slice, preferably
outside the already calibrated NAPMS areas, to determine whether evidence
authoring friction persists across project shapes. Framework automation should
remain deferred until that repeated cost becomes a concrete adoption blocker.
