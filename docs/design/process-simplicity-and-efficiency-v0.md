# Process Simplicity and Efficiency v0

Status: canonical repository-wide process and agent constraint.

## Purpose

Harness protects engineering correctness, authority boundaries, traceability,
reproducibility, lifecycle guarantees and publication atomicity. The process
used to obtain those guarantees is itself an engineering cost and must remain
proportional to the risk and semantic complexity being protected.

This contract constrains **how** Harness procedures are designed and executed.
It does not weaken any semantic or authority invariant.

## Normative rule

When two procedures provide equivalent engineering guarantees, Harness must
prefer the materially simpler procedure.

A procedure is simpler when, for the same required guarantees, it has fewer:

- execution steps;
- persisted or generated artifacts;
- external round trips;
- manual transitions;
- duplicated representations of the same state;
- repeated computations over unchanged inputs;
- coordination boundaries;
- feedback delays.

Harness must not introduce ceremony, intermediate artifacts, workflow stages,
CI runs, persistence records or abstractions unless they protect a concrete
invariant or satisfy an explicit requirement.

## Required guarantees

Process simplification must preserve every guarantee that applies to the
operation, including:

- semantic correctness and fail-closed behavior;
- Authority ownership and human-owned decision boundaries;
- deterministic/reproducible evaluation where required;
- semantic admission and lifecycle/currentness guarantees;
- traceability sufficient to reconstruct accepted engineering state;
- Project Publication CAS and atomic visibility;
- no fabricated acceptance identity or acceptance rationale;
- compatibility and migration obligations.

The simplification target is therefore **minimum sufficient process**, not
minimum validation.

## Validation placement

Run validation at the cheapest layer that can prove the relevant invariant.

Local deterministic checks should reject malformed inputs before expensive
semantic evaluation or remote execution when they provide the same proof.
Incremental or affected checks should be used during iteration; broader gates
belong at coherent verification boundaries.

CI is a verification boundary, not an interactive exploration mechanism. A
Harness API that forces repeated commit -> CI -> single blocker -> commit cycles
for deterministic local questions is a process-design smell.

## Coherent operations

Prefer one coherent application operation over a sequence of loosely
coordinated project-side commands when the sequence protects one application
invariant.

Within that operation:

- reuse accepted CURRENT state whose relevant fingerprints and dependencies are
  unchanged;
- evaluate only the affected dependency closure when that preserves the same
  correctness proof;
- aggregate independent blockers when doing so is safe;
- stop only where semantic/Authority input is actually required;
- keep intermediate working state non-current;
- publish one coherent next Project Publication through the existing atomic/CAS
  boundary.

Resumability may preserve bounded reconciliation progress, but it must not
create a second semantic source of truth or evolve into a general-purpose
workflow engine.

## Process complexity smells

The following observations require an explicit simplify/consolidate/relocate
review:

- repeated identical validation over unchanged inputs;
- repeated manual orchestration of the same semantic sequence;
- recurring project-specific glue around a generic Harness responsibility;
- remote execution used where an equivalent local deterministic check exists;
- duplicated generated state without an ownership/reproducibility need;
- full pipeline restart after a local blocker;
- durable persistence of data that is only ephemeral execution state or cache;
- several layers with materially equivalent responsibility;
- artifact proliferation without a concrete invariant owner.

A smell is evidence to investigate, not permission to remove required evidence.

## Capability placement

Repeated project-specific glue for the same generic workflow is evidence that a
Harness application capability is missing or poorly placed. Move the generic
mechanics into Harness when the responsibility is stable and repeated; keep
project semantics and project-owned policy in the project.

Automation may own mechanics such as topology traversal, fingerprint/currentness
comparison, deterministic preflight, blocker aggregation, publication assembly
and closure evaluation.

Automation must not invent Authority decisions, semantic evidence, acceptance
rationale, product/domain meaning, or acceptance identity. In short:
**automate mechanics, not authority**.

## Persistence rule

Persist state only when ownership, invariant protection, reproducibility,
restartability or auditability requires durability.

Reproducible generated evidence, caches, diagnostics and temporary candidates
should remain disposable unless a concrete contract requires retention.
Physical representation may be optimized independently of logical publication
semantics when atomicity, deterministic revision identity, parent/CAS semantics,
historical readability and compatibility remain preserved.

## Design review questions

For every new Harness process step, artifact, persistence record, abstraction or
remote execution boundary, reviewers should be able to answer:

1. Which concrete invariant or explicit requirement does this protect?
2. Is there a cheaper layer that can prove the same thing?
3. Can accepted unchanged state be reused safely?
4. Can independent failures be reported together?
5. Is generic orchestration being pushed into a target project?
6. Does the proposed state duplicate an existing owner?
7. Is complexity proportional to the semantic risk?

If the engineering guarantee can be obtained substantially more simply, the
simpler procedure is the required design.
