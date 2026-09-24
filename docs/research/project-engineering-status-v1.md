# Project Engineering Status v1 — research design

Status: experimental. This document does not change Core v0.

## Decision

Project-wide engineering status is a generated read model over reference Authority applicability plus existing project engineering knowledge. It is not a second semantic source of truth and not a workflow state machine.

The project must be able to answer, for every reference Authority: has this ownership boundary been assessed for this project, and if so is it REQUIRED, NOT_APPLICABLE, or UNRESOLVED?

Authority applicability is project state. Capability production/completion remains derived from Engineering Graph, Core providers and Questions.

## Bootstrap

A project bootstrap projects every reference Authority into an applicability registry with state UNASSESSED. The registry stores only project-specific assessment truth; it does not copy Authority definitions.

When the Harness reference catalog gains an Authority, an existing project sees it as UNASSESSED until assessed. Removal/rename requires an explicit catalog migration rule rather than silently deleting project assessment evidence.

## Authority assessment contract

Every Authority that is considered by Harness must finish the assessment step by recording exactly one state:

- UNASSESSED — no accepted project assessment yet;
- REQUIRED — this Authority owns at least one material project decision/accepted knowledge obligation;
- NOT_APPLICABLE — accepted project evidence proves this Authority is not needed in the current scope;
- UNRESOLVED — evidence is insufficient to decide REQUIRED versus NOT_APPLICABLE.

A non-UNASSESSED assessment records evidence, rationale, evidence dependencies and reopening conditions. UNRESOLVED additionally exposes a Question or explicit unresolved obligation.

An Authority must not write a manual completion/progress status. For REQUIRED Authorities, completion is derived from active production contracts, Capability providers, prerequisites and Questions.

## Applicability atomicity

This registry is safe only if Authority is an atomic applicability boundary.

Selective consumption of several Capabilities from one REQUIRED Authority is normal. But if independent decision families inside one Authority repeatedly have independent REQUIRED/NOT_APPLICABLE outcomes, independent accepted outputs, consumers and lifecycles, that is a boundary-split signal rather than a reason to invent PARTIALLY_APPLICABLE.

Do not add PARTIALLY_APPLICABLE.

## Derived operational status

For a REQUIRED Authority, derive a summary from its project-active capability contracts:

- COMPLETE — all active required capabilities are SATISFIED;
- BLOCKED — at least one active capability is WAIT due to an unresolved Question;
- IN_PROGRESS — accepted output exists for part of the active capability set while work remains;
- NOT_STARTED — active required capabilities exist but no accepted output has been formed yet;
- STALE — only when lifecycle-aware evidence proves accepted knowledge depends on an obsolete baseline.

These labels are a human projection. Engineering Graph/Core runtime semantics remain authoritative.

## Natural update during Authority work

Harness execution should not require a separate status-maintenance pass.

Before producing knowledge through an Authority:
1. resolve its project applicability assessment;
2. persist REQUIRED / NOT_APPLICABLE / UNRESOLVED with evidence;
3. only REQUIRED enters production routing;
4. production changes canonical artifacts/questions, not a manual progress field;
5. status projection is regenerated from current truth.

If an upstream evidence dependency changes, affected applicability assessments are reopened to UNASSESSED or UNRESOLVED according to the accepted invalidation policy; they must not silently remain N/A/REQUIRED.

## Projection

Conceptual pipeline:

```text
Reference Authority Catalog
        +
Project Authority Assessments
        +
Engineering Graph / Core
        +
CanonicalArtifacts / Questions
        +
Lifecycle evidence
        ↓
Project Engineering Status
```

The generated table should minimally expose:

| Authority | Applicability | Operational status | Evidence/artifacts | Blocking |
|---|---|---|---|---|

The generated document is disposable. Editing it must never change project truth.

## Relationship to Engineering Coverage Map

Project Engineering Status is Authority-centric and answers: which engineering ownership boundaries have been assessed and what is their current project state?

Engineering Coverage Map is Concern-centric and answers: across a reusable engineering lens, which semantic concerns are covered, missing, blocked, stale, N/A or unassessed?

They may be rendered together, but must not become duplicate sources of applicability truth.

## Core compatibility

No new Core entity is required by this experiment. Core continues to model Authority, CanonicalArtifact, CapabilityId and Question. The assessment registry is project/reference-layer state until concrete consumer evidence requires first-class Core identity.

This also preserves the existing rule that a Core model projects project truth rather than creating a duplicate canonical graph.

## Acceptance criteria

The experiment passes when:
1. bootstrap covers every catalog Authority exactly once as UNASSESSED;
2. every non-UNASSESSED row has evidence, rationale, dependencies and reopening conditions;
3. NOT_APPLICABLE cannot be inferred from silence;
4. REQUIRED completion is derived, never manually authored;
5. UNRESOLVED exposes a blocker/question;
6. no PARTIALLY_APPLICABLE state exists;
7. adding a catalog Authority produces one new UNASSESSED project row without copying its definition;
8. generated status rows are reproducible from source state;
9. applicability-atomicity failures are reported as Authority boundary findings.
