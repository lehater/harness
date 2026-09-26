---
name: implementation-design
description: "Use for actionable CREATE work requiring implementation plan, slicing, repository realization or completion criteria after upstream design is accepted. Translate accepted design into bounded executable work without reopening or inventing product/domain/architecture decisions."
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

## Decision exploration

Before forming the candidate, run the `decision-explorer` agent skill against the accepted prerequisites and this knowledge kind's registered axes. The resulting noncanonical exploration evidence must exist before any preferred solution is selected.

Before semantic acceptance, inspect the decision axes registered for
`implementation-design`: slice boundaries, repository realization,
dependency/tooling choices, migration/transition, verification enforcement, and
delivery gates. Do not infer that the first repository/tooling realization is
the only acceptable realization.

At `EXPLORE` or deeper, challenge material choices with distinct alternatives
and a counterfactual. Select among multiple viable implementation-owned
alternatives only within project autonomy. Any option that would change accepted
Product, Domain, Application, Architecture, Interface, Data, Security, or
Quality semantics must be escalated to the owning Authority instead.

## Procedure

1. Confirm all required upstream engineering knowledge is accepted/unblocked.
2. Define the implementation boundary and explicit exclusions.
3. Partition realization into the smallest coherent slices that preserve accepted
   ownership/contracts.
4. Order slices only where a real implementation dependency exists.
5. Identify migrations/data transitions and compatibility risks when applicable.
6. Derive repository realization from accepted semantic/component boundaries: physical module/package roots, composition root, source/generated/test/migration/configuration topology and explicit implementation freedoms. Do not prescribe a universal folder layout.
7. For every applicable engineering/security/quality/supply-chain obligation, select a concrete deterministic enforcement mechanism or record an explicit terminal disposition. Keep the obligation independent from the selected tool.
8. Define the reproducible dependency/tool environment. If the project's delivery workflow has merge/release gating, define its authoritative reproducible gate; local/pre-commit checks may optimize feedback but do not replace that gate.
9. Identify code/test/CI surfaces each slice must change.
10. Define completion criteria that prove the accepted design is realized.
11. If any slice would require a new product/domain/architecture/interface
   decision, create/route a Question upstream instead of embedding the decision in
   the implementation plan.
12. Do not treat this artifact as authorization to merge/deploy unless the target
   repository explicitly assigns it that role.
13. Produce project-native implementation design, semantically accept/register
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
- repository/module surfaces and semantic-to-physical mapping;
- dependency-rule enforcement and composition root;
- applicable tooling obligations and selected concrete tools;
- source/generated/test/migration/configuration topology;
- reproducible dependency/tool environment;
- authoritative merge/release gate when applicable and optional local fast-feedback subset;
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
- architecturally significant dependency rules have deterministic mechanical enforcement;
- every applicable tooling/security/supply-chain obligation has enforcement or an explicit disposition;
- generated artifacts identify their canonical source and regeneration path;
- applicable merge/release gate semantics are authoritative and reproducible from versioned project inputs, or non-applicability is explicit;
- no hidden/manual state fabrication is required for supported behavior;
- unresolved design gaps are routed upstream.

## Registration

Register accepted implementation-design artifact(s) under Implementation Design,
with dependencies on the canonical design actually consumed.

## Human projection

Normally the project-native plan/readiness artifact is directly human-readable.
