# Decision lifecycle, evidence feedback, reopening and supersession research

Status: research conclusion.

## Problem

Harness v0 models the currently accepted state of engineering knowledge and unresolved Questions. Engineering Graph models production topology. This is sufficient to reach a consumer such as IMPLEMENTATION, but it does not yet define what happens when already accepted knowledge becomes stale after new evidence or upstream change.

Examples:
- production incident contradicts an accepted failure assumption;
- verification discovers an accepted design is incomplete;
- vulnerability disclosure invalidates a security assumption;
- external API/provider version changes;
- normative source changes applicability;
- user evidence changes product truth;
- an upstream accepted capability is superseded.

The problem is not implementation progress. It is lifecycle of accepted engineering knowledge.

## Required distinctions

### New evidence is not automatically new truth

Incident, telemetry, test failure, vulnerability report or external change is evidence. It may create a Question or invalidate an assumption, but it must not silently rewrite an Authority-owned decision.

### Supersession is not deletion

Historical accepted knowledge may remain important for explaining old releases, migrations, incidents and transition constraints. Replacing current truth must not require pretending the previous artifact never existed.

### Staleness is not semantic rejection

A downstream capability can become unusable because one of its prerequisites changed even before anyone proves the downstream content wrong. It is stale with respect to the new accepted prerequisite baseline.

### Reopening is not workflow status

A Question represents unresolved semantics. "Reopen" means a new unresolved semantic gap exists against accepted/current knowledge; it is not reopening a ticket.

## Candidate ownership models

### A. DECISION-LIFECYCLE Authority

Rejected.

Lifecycle invalidation can originate from Product evidence, Security, Obligation sources, Quality evidence, dependency changes, verification and architecture evolution. A generic Authority would not own the underlying decision and therefore cannot authoritatively decide whether knowledge remains valid.

Atomicity:
- semantic cohesion: FAIL — groups changes by lifecycle event rather than decision kind;
- independent change: FAIL — validity follows upstream/evidence changes owned elsewhere;
- public contract: FAIL — consumers need current accepted capability validity, not a separate lifecycle semantic product.

### B. EVIDENCE-ANALYSIS Authority

Rejected as a generic baseline.

Security Analysis and Obligation Analysis already demonstrate cases where a specific analysis has coherent applicability/coverage semantics. Generic evidence has no single interpretation model. Production telemetry, user research, legal source change and vulnerability disclosure require different owners.

### C. Graph lifecycle semantics above Core

Supported.

Harness needs a derived rule for whether a currently provided capability is valid against its accepted prerequisite baseline. This is topology/state evaluation, not a new semantic owner.

## Minimal lifecycle model

A capability provider is **CURRENT** only when:
1. it is the selected canonical provider;
2. it is not blocked by unresolved Questions;
3. every production prerequisite resolves to a CURRENT provider;
4. the provider was accepted against the same prerequisite revisions/current identities that are now selected.

If an upstream prerequisite is superseded, downstream accepted knowledge becomes **STALE** until its owning Authority revalidates or replaces it.

This is analogous to build invalidation, but semantic acceptance remains Authority-owned.

## Why current Core v0 is insufficient

Core currently knows:
- artifact identity/path/Authority;
- provides;
- artifact dependencies;
- Questions/blocking.

It can derive transitive blocking, but cannot distinguish:
- downstream artifact accepted against prerequisite revision A;
- prerequisite A later superseded by B;
- downstream artifact has not yet been revalidated against B.

A plain dependency edge only says "depends on capability/artifact"; it does not preserve the accepted prerequisite baseline.

Therefore a consumer can incorrectly remain COMPLETE after an upstream replacement unless an agent manually creates Questions everywhere.

That is a demonstrated lifecycle gap.

## Proposed minimal extension

Do **not** add Stage, Status, Approval, Change, Incident or Evidence entities.

Add immutable/current identity semantics for canonical accepted knowledge sufficient to compare prerequisite baselines.

Conceptual shape:

- every accepted CanonicalArtifact realization has a stable **revision identity**;
- a provider records the prerequisite provider revision identities against which it was accepted;
- project integration identifies the currently selected canonical revision for each provider/capability;
- evaluator derives CURRENT or STALE;
- STALE behaves as unsatisfied for downstream consumer completeness;
- owning Authority may revalidate unchanged semantic content against the new baseline, producing a new accepted revision/baseline, or replace content;
- unresolved semantic uncertainty is still represented by Question.

The exact persistence shape must remain minimal and adapter-friendly. Existing project-owned version/revision systems should be projected rather than duplicated.

## Supersession rules

1. A new accepted provider revision supersedes the previous current revision for the same project-owned canonical knowledge identity.
2. Superseded history remains addressable where the target repository supports it.
3. Supersession does not automatically declare downstream knowledge wrong.
4. It invalidates downstream CURRENT status when recorded prerequisite baseline no longer matches.
5. Revalidation is an Authority-owned semantic acceptance action, not automatic timestamp refresh.
6. If revalidation discovers a semantic gap, create Question.
7. If transition between old/new accepted states is material, CHANGE-TRANSITION-DESIGN owns the transition contract.

## Feedback routing

| Evidence/change | First routing |
| --- | --- |
| User/problem evidence | Discovery/Product |
| Domain contradiction | owning Domain Authority |
| Verification/test failure | Verification/Test routes Question to semantic owner |
| Production incident/telemetry | Operability provides evidence; semantic Question routes to affected owner |
| Vulnerability/threat change | Security Analysis |
| Normative source/version change | Obligation Analysis |
| Dependency/provider change | System/Interface/Security/Engineering Policy as applicable |
| Quality target miss | Quality Design + System/Implementation investigation |
| Upstream capability supersession | derived stale propagation; downstream owner revalidates |

Evidence does not bypass Authority ownership.

## Validation scenario 1 — product change

Product requirement R1 -> Architecture A1 -> Interface I1 -> Implementation Design D1.

Product accepts R2 superseding R1.

Expected:
- A1 becomes stale against Product R2;
- I1 and D1 become stale transitively;
- Harness no longer reports IMPLEMENTATION COMPLETE;
- Architecture may revalidate unchanged topology as A2 against R2 or change it;
- only then can Interface revalidate, then downstream;
- no generic Lifecycle Authority decides semantics.

Current v0 cannot prove A1 was accepted against R1 rather than R2.

## Validation scenario 2 — vulnerability disclosure

Security Architecture S1 accepted against threat/control analysis T1. New vulnerability evidence causes Security Analysis T2/current coverage change.

Expected:
- if S1's prerequisite baseline includes T1, S1 becomes stale;
- Security Architecture decides whether S1 remains sufficient;
- revalidation may produce S2 with unchanged structure but new baseline;
- Verification/Test obligations may change;
- implementation remains blocked from assuming old security coverage is current.

The vulnerability itself is not a Core entity.

## Validation scenario 3 — external obligation changes

Obligation coverage O1 routes constraints into Product/Data/Security. Normative source changes and O2 is accepted.

Downstream knowledge based on O1 becomes stale according to recorded prerequisites. Owners decide whether semantics actually change. This prevents both extremes:
- silently keeping old design;
- blindly rewriting every downstream artifact.

## Validation scenario 4 — production incident

Operability evidence shows timeout behavior violates an accepted reliability assumption.

Operability does not rewrite Application/System semantics. It creates/routs a Question. If upstream accepted capability changes, baseline mismatch then propagates staleness structurally.

This separates **evidence feedback** from **accepted-knowledge invalidation**.

## Impact propagation

Staleness should follow production prerequisites, not arbitrary repository file dependencies.

Reason:
- Engineering Graph prerequisites express semantic production dependency.
- file dependencies may include rendering, packaging or documentation relationships not sufficient for semantic invalidation.

Project-native canonical graphs may project semantic prerequisite revision identities when they own equivalent routing.

## Core vs Engineering Graph placement

Production prerequisite topology belongs to Engineering Graph.

Accepted provider realization/baseline belongs to current knowledge state, therefore the minimum revision/baseline facts belong at the Core/integration boundary.

Derived STALE/CURRENT evaluation belongs above the raw model, similar to blocked/target-state evaluation.

This is the first researched case in the current closure program that justifies a **minimal Core evolution candidate**.

## Compatibility strategy

v0 models without revision/baseline metadata remain valid in legacy/static mode:
- current provider behaves as today;
- no staleness can be proven;
- lifecycle-aware evaluation should report lifecycle coverage as unavailable rather than invent freshness.

A project opts into lifecycle-aware evaluation when its adapter/model can provide revision identities and acceptance baselines.

This avoids forcing repositories to duplicate existing history/version systems.

## What must not be added

Do not add:
- universal Event;
- Incident;
- Change Request;
- Task;
- Workflow;
- Approval;
- lifecycle stage machine;
- generic Evidence entity;
- timestamps as a proxy for semantic validity;
- automatic semantic acceptance.

## P0 findings

1. Current v0 can remain structurally COMPLETE after an upstream accepted provider is replaced; dependency edges alone cannot prove whether downstream knowledge was accepted against the new prerequisite.
2. Manual Questions are insufficient as the only mechanism because upstream supersession can structurally invalidate many downstream capabilities before semantic review occurs.
3. Staleness must be derived, not owned by a generic lifecycle Authority.
4. Revalidation must remain Authority-owned and explicit; automatic propagation must never assert semantic correctness.

## P1 findings

1. Minimal revision identity + accepted prerequisite baseline is sufficient conceptually; no generic Change/Evidence entity is justified.
2. Semantic invalidation should follow Engineering Graph production prerequisites.
3. Historical superseded knowledge should remain project-owned/addressable when available.
4. CHANGE-TRANSITION-DESIGN applies only when moving between accepted states introduces material transition semantics.

## Recommendation

Prototype lifecycle-aware evaluation as an experimental v1 extension before changing canonical Core:
- add a small optional revision/baseline projection;
- create acceptance tests for supersession -> stale propagation -> revalidation;
- validate against Nutrition and NAPMS project-native artifact graphs;
- prove adapters can project existing revision/version identity without duplicating project truth;
- only then decide whether to promote fields into Core v1.
