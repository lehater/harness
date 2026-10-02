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

The roadmap top-level `frontier_status` is not a generic empty/non-empty flag.
It is one of `READY`, `FAILED_VALIDATION`, `BLOCKED`, `INCOMPLETE`,
`WAITING` or `COMPLETE`. This preserves the reason no Capability is READY
and lets the Application Layer compose the roadmap without reverse-engineering
its buckets.

An existing Core provider without a matching lifecycle assertion is not missing
knowledge and must never enter CREATE. The roadmap reports it under
`lifecycle_gaps` with state `UNKNOWN`. Existing-project reconciliation must
establish accepted lifecycle evidence for the existing provider (or replace it
through an explicit semantic change); Harness must not create a duplicate
canonical provider merely to fill integration metadata.

After one READY Capability reaches a terminal outcome, recompute the roadmap.
Do not freeze a project-wide role frontier.

`FAILED_VALIDATION` is persisted outside Core as
`harness-decision-failure-set` evidence keyed by Capability. While that
evidence remains current, ordinary roadmap recomputation exposes the Capability
under `failed_validation` and does not make it READY again. An explicit redo
acknowledges retry intent. If the failed attempt was CREATE and therefore has no
current provider, retry remains CREATE mode; it must not fabricate a REDO
baseline.

Possible terminal outcomes are:

- `CURRENT` — semantic admission succeeded;
- `BLOCKED` — unresolved semantics were published as Core Questions;
- `FAILED_VALIDATION` — the execution/evidence itself is invalid.

A terminal outcome is not visible merely because its component evidence has been
computed. The coordinator prepares the complete next Project Publication and
publishes it against the revision from which the work was derived. Core changes,
semantic evaluation, lifecycle assertion, Question resolution and failure
evidence therefore cross one logical visibility boundary. See
`docs/design/project-publication-v0.md`.

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

For a failed CREATE, explicit redo means "retry the failed pipeline attempt", not
"redo accepted knowledge". The roadmap therefore emits
`EXPLICIT_RETRY_FAILED_VALIDATION` with `decision_request_mode: CREATE`.
A new terminal result replaces/clears the persisted failure evidence in the
same atomic Project Publication as the other terminal-result facts; this
orchestration evidence never becomes Core truth.

## Core boundary

Pipeline stages, roadmap buckets and execution outcomes remain orchestration
procedure above Core. Core continues to own only Authorities,
CanonicalArtifacts, CapabilityIds, dependencies and Questions.

The cross-layer `harness.application.project_frontier` projection consumes this roadmap together
with Semantic Closure and Engineering Coverage. Decision Pipeline does not own
their precedence or redefine their domain states.
