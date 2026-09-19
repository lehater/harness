---
name: implementation-design
description: "Use for actionable CREATE work requiring implementation plan, slicing, migration concerns or completion criteria after upstream design is accepted. Translate accepted design into bounded executable work without reopening or inventing product/domain/architecture decisions."
---

# Implementation Design

## Trigger

Use when actionable grouped work has `knowledge_kind: implementation-design`,
including implementation-plan and completion-criteria capabilities owned by
Implementation Design.

## Inputs

- actionable work and Implementation Design Authority;
- accepted upstream Requirements, Domain/Application, Architecture, Interface,
  Data, Quality, Security and Operability knowledge applicable to the scope;
- target repository build/test/deployment constraints.

## Read boundary

Read canonical design required by the selected implementation scope plus existing
code/build structure needed to plan realization.

Implementation code is evidence about current state, not authority over upstream
semantics.

## Procedure

1. Confirm all required upstream engineering knowledge is accepted/unblocked.
2. Define the implementation boundary and explicit exclusions.
3. Partition realization into the smallest coherent slices that preserve accepted
   ownership/contracts.
4. Order slices only where a real implementation dependency exists.
5. Identify migrations/data transitions and compatibility risks when applicable.
6. Identify code/test/CI surfaces each slice must change.
7. Define completion criteria that prove the accepted design is realized.
8. If any slice would require a new product/domain/architecture/interface
   decision, create/route a Question upstream instead of embedding the decision in
   the implementation plan.
9. Do not treat this artifact as authorization to merge/deploy unless the target
   repository explicitly assigns it that role.
10. Produce project-native implementation design, semantically accept/register
    and reevaluate.

## Stop conditions

Stop when:

- an implementation slice requires inventing upstream semantics;
- required interface/data/security/quality contracts are absent;
- migration safety depends on an unresolved design decision;
- completion cannot be stated without changing accepted requirements.

## Output contract

Prefer project-native plan/readiness artifacts.

Useful content may include:

- implementation boundary;
- slices and real dependencies;
- repository/module surfaces;
- migrations;
- risks;
- completion criteria;
- unresolved upstream Questions.

One artifact may provide implementation-plan and completion-criteria capabilities
when the project owns them together; they may also be separate production outputs.

## Acceptance checks

- every slice realizes accepted design rather than redefining it;
- sequencing is justified by dependencies, not methodology stages;
- completion criteria trace to canonical contracts;
- no hidden/manual state fabrication is required for supported behavior;
- unresolved design gaps are routed upstream.

## Registration

Register accepted implementation-design artifact(s) under Implementation Design,
with dependencies on the canonical design actually consumed.

## Human projection

Normally the project-native plan/readiness artifact is directly human-readable.
