# Sequential Decision Pipeline v0

Status: experimental.

## Purpose

Decision-governed work uses one sequential procedure per Capability rather than
separate Explorer/Producer execution roles.

The separation that matters is semantic:

```text
FORM OPTIONS
    ↓
REVIEW OPTIONS
    ↓
CHOOSE / ESCALATE
    ↓
PRODUCE CANDIDATE
    ↓
SEMANTIC ADMISSION
```

The same execution may perform all stages. No physical context isolation or
role handoff is claimed.

Non-governed knowledge kinds do not receive synthetic decision stages; they keep
the ordinary `PRODUCE CANDIDATE → SEMANTIC ADMISSION` path.

## Roadmap

Harness derives a project frontier from Engineering Graph, Core blockers and
Capability lifecycle currentness.

A Capability is READY when its direct prerequisites are CURRENT and it is not
blocked by an unresolved Core Question. CURRENT work is omitted by default.

After one READY Capability reaches a terminal outcome, recompute the roadmap.
Do not freeze a project-wide role frontier.

Possible terminal outcomes are:

- `CURRENT` — semantic admission succeeded;
- `BLOCKED` — unresolved semantics were published as Core Questions;
- `FAILED_VALIDATION` — the execution/evidence itself is invalid.

## Option formation

Decision Exploration is the option-formation evidence.

For CREATE, the pre-choice request contains accepted prerequisite/support
knowledge.

For REVISION or explicit REDO, it additionally contains the current accepted
provider. That provider is historical accepted truth and must be challenged;
it is not the future candidate.

The future candidate, decision review and selected/preferred solution remain
forbidden pre-choice inputs.

## Decision-space review

Before any choice, option formation must review the complete discovered decision
space for:

1. mixed decisions that should be split;
2. missing material cases/alternative classes;
3. conflicts with accepted canonical constraints;
4. decisions that actually belong to another Authority.

Every discovered decision point must be covered by this review and no material
gap may remain open.

This review is the quality boundary that prevents the later choice stage from
becoming a second Explorer/reviewer.

If the review finds an unresolved semantic fact, publish a normal Core Question
to the Authority that owns that fact. The affected Capability becomes blocked;
there is no special Reexploration Request protocol.

## Choice and production

After the decision space is reviewed:

- one viable alternative -> `DETERMINED`;
- multiple viable alternatives whose selection is delegated by autonomy ->
  `DELEGATED`;
- otherwise -> `ESCALATED` through the existing Core Question mechanism.

Governance evaluates exactly the reviewed decision/alternative set. Candidate
production follows the accepted dispositions and then goes through strict
semantic admission.

If a later stage discovers that the decision space itself was malformed despite
the review gate, treat that as `FAILED_VALIDATION`. Fix the option-formation
procedure/evidence and explicitly redo the Capability; do not create an
automatic Explorer/Producer loop.

## Explicit redo and idempotence

Normal repeated invocation over a fully CURRENT target is a no-op.

Explicit redo is the only ordinary override:

```text
CURRENT Capability
  + explicit redo
  -> READY in REDO mode
  -> current provider included as accepted baseline
  -> full pipeline runs again
```

Redo does not waive blockers or upstream currentness.

## Core boundary

Pipeline stages, roadmap buckets and execution outcomes remain orchestration
procedure above Core. Core continues to own only Authorities,
CanonicalArtifacts, CapabilityIds, dependencies and Questions.
