# Real-project assurance adoption v0

Status: active; first real-project slice completed.

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

## Adoption findings after slice 1

The existing assurance mechanisms were sufficient without changes to Core,
Scenario Suite orchestration, semantic DSL, provider registry or workflow
state.

The main scaling cost observed so far is evidence authoring:

- selecting exact immutable source units;
- writing lossless boundary manifests;
- enumerating meaningful statements;
- admitting semantic atoms;
- declaring honest atom links.

This is real operational friction, but one slice is insufficient evidence for
a new abstraction or automation layer.

No LLM execution was required for the RED. The omission is deterministic once
the five-atom source surface is accepted.

## Next experiment

Run a second independent real slice and specifically measure whether the same
manual evidence-authoring work and the same verification-loss pattern recur.
Only repeated concrete friction should justify automation.
