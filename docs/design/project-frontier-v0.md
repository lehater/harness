# Project Frontier v0

Status: canonical application projection.

## Purpose

`harness.application.project_frontier` is the single application-layer next-action projection
for a selected Consumer. It composes existing Harness read models without
becoming a new owner of engineering truth.

Inputs remain owned by their contexts:

- Decision Roadmap — Capability execution readiness, blockers, lifecycle gaps
  and persisted decision-validation failures;
- Semantic Closure — strict admission/currentness gaps and semantic Question
  frontier;
- Engineering Coverage — concern applicability/completeness and coverage work;
- optional structural CREATE routing — artifact-skill execution route.

Project Frontier answers one question:

> Given the current read models, what work is actionable now, what prevents
> progress, and is the selected Consumer fully closed?

## Contract

The projection is derived and disposable:

```yaml
version: 1
kind: harness-project-frontier
target: IMPLEMENTATION
status: READY
next_actions: [...]
failed_validation: [...]
blocked: [...]
waiting: [...]
gaps: [...]
source_status: {...}
```

It is never persisted as project truth.

## Status semantics

Status is derived in this order:

1. **READY** — at least one executable next action exists.
2. **FAILED_VALIDATION** — no executable work exists and a persisted Decision
   Pipeline validation failure requires explicit retry.
3. **BLOCKED** — no executable work exists and unresolved Questions block the
   selected closure.
4. **INCOMPLETE** — no executable work exists but lifecycle/admission/metadata
   evidence is insufficient for closure.
5. **WAITING** — no executable work exists and remaining work waits on an
   upstream frontier.
6. **COMPLETE** — Decision Roadmap is COMPLETE, Semantic Closure is COMPLETE and
   Engineering Coverage has `completion_ready: true`.

A source cannot force COMPLETE by itself.

## Capability work deduplication

Decision Roadmap owns executable Capability work. If Semantic Closure or
Engineering Coverage reports `PRODUCE_CAPABILITY`, `VALIDATE_SEMANTICS` or
`REVALIDATE_SEMANTICS` for the same READY Capability, Project Frontier attaches
that evidence to the Decision work unit instead of emitting a second competing
action.

Coverage work that is not represented by a Capability execution remains an
independent next action, for example `MODEL_PRODUCTION_CONTRACT`,
`CLASSIFY_ACCEPTED_SCOPE` or `DECLARE_SUBJECT_INVENTORY`.

Question work is reported under `blocked`; prerequisite-only work under
`waiting`; lifecycle/currentness evidence gaps under `gaps`.

## Boundary

Project Frontier is an Application Layer process manager/read-model composer.
It must not:

- mutate Core, lifecycle, semantic or coverage state;
- reinterpret semantic findings;
- infer applicability;
- choose a provider or Authority;
- invent a workflow state in the project model.

Domain evaluators remain independently testable and authoritative for their
own vocabulary. Project Frontier owns only cross-layer precedence and
normalization.

## CLI

```sh
python -m harness.application.project_frontier IMPLEMENTATION \
  decision-roadmap.yaml \
  semantic-closure.yaml \
  engineering-coverage.yaml \
  --create-routing structural-routing.yaml
```

Exit code is zero only for COMPLETE; non-complete states remain observable
without being mistaken for closure.
