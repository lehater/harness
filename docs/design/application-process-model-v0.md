# Application Process Model v0

Status: canonical v0.

## Purpose

Define the Harness ownership and knowledge boundary for project application
processes: causal and temporal composition of accepted work across application
operations, domain responsibilities and participating actors.

This contract defines process knowledge independently of any diagram notation.
BPMN, UML Activity, sequence diagrams and similar representations are generated
projections of accepted process knowledge, not semantic owners.

## Problem

Harness already represents several process-adjacent knowledge kinds:

- Domain Use-Case Design owns bounded domain behavior, including trigger,
  preconditions, inputs, effects, rejections and postconditions;
- Application Design owns commands, queries, materializations, orchestration,
  failure semantics, continuation and currentness;
- Task Model owns intended human work, responsibility allocation, ordering and
  task dependencies;
- User Journey Design owns bounded user-goal interaction, alternate paths,
  recovery and completion.

Those contracts intentionally serve different consumers. None alone guarantees a
complete answer to the project-level question:

> How does this application process progress from trigger to completion,
> including decisions, waits, parallel work, failure and recovery?

The missing concept is therefore a process knowledge contract, not a diagram
format and not a Harness execution workflow.

## Definition

An **application process** is an accepted causal/temporal composition of
application-relevant work that explains how a bounded outcome is reached.

A process may coordinate:

- application operations;
- domain-use-case outcomes;
- user, system and external-actor activities;
- decisions and guarded alternatives;
- events and externally observable facts;
- waits, timers and continuation points;
- parallel and converging paths;
- failure, cancellation, recovery and compensation;
- completion conditions and semantic postconditions.

Commands, queries, events and activities may participate in a process, but none
of them is itself the process.

### Process instance boundary

A process contract must distinguish the work that belongs to one process
instance from knowledge that merely makes that work possible.

In particular, these relations are not interchangeable:

- a **precondition** must already hold before the process activity can proceed;
- a **control precedence** relation means one process activity or outcome
  causally enables another within the selected process instance;
- a **data dependency** means later work requires information produced or
  selected elsewhere, without by itself defining execution order;
- **provenance** explains why an accepted fact or activity exists and does not
  imply runtime sequencing;
- **concurrency** means accepted work may overlap;
- **synchronization/convergence** means continuation depends on completion or
  outcomes from more than one accepted branch.

An explanatory list, dependency chain, domain history or artifact provenance
must not be projected as process control flow merely because it is ordered in a
source document.

The process boundary should therefore identify the initiating condition and the
bounded completion outcome of one meaningful execution. Accepted state created
before that boundary is an input or precondition unless the owning project
semantics explicitly make its creation part of the same process.

## Ownership

Application process knowledge is owned by **APPLICATION-DESIGN**.

The existing Authority already owns application-level composition and
orchestration across accepted product/domain behavior. Process knowledge is a
more explicit contract inside that decision boundary, not evidence for a new
Authority.

Do not introduce a PROCESS-DESIGN Authority unless concrete project evidence
shows an independently applicable decision family with:

1. semantic cohesion distinct from Application Design;
2. an independently changing lifecycle;
3. a public producer/consumer contract that would otherwise be distorted;
4. real consumers that require the split.

Until that evidence exists, a separate Authority would duplicate orchestration
ownership.

## Canonical knowledge boundary

Canonical process knowledge describes meaning required to understand execution
progression. Useful dimensions include, where applicable:

- process purpose / desired outcome;
- scope and stable process identity;
- trigger / initiating event;
- participants and responsibility allocation;
- preconditions;
- required inputs and references;
- activities / application operations;
- produced outcomes and relevant events;
- typed causal relations, including control precedence, data dependency,
  preconditions, provenance and concurrency where material;
- branch conditions / decisions;
- parallelism and convergence;
- waits, timers and external continuation;
- success completion conditions;
- failure and cancellation paths;
- recovery / compensation semantics;
- semantic postconditions;
- unresolved Questions and upstream references.

Not every process needs every dimension. Missing material semantics must remain
explicitly unresolved rather than being invented by a projection or
implementation.

A process contract should use the narrowest relation semantics supported by
accepted knowledge. Generic source ordering must not be promoted to causal
ordering, and absence of an ordering constraint must not be promoted to
parallelism.

### Process state and progress

Process progress is canonical application knowledge only when it carries
project meaning required to decide valid continuation, recovery, cancellation
or completion and cannot be derived unambiguously from already accepted domain
or application facts.

Keep these state categories separate:

- **domain state** is owned by the relevant Domain Authority;
- **semantic process state/progress**, when independently material, belongs to
  APPLICATION-DESIGN;
- **application orchestration state** belongs to APPLICATION-DESIGN only where
  its meaning survives implementation choices;
- **persisted workflow-engine state** is a realization concern owned by the
  relevant Architecture/Data/Implementation decisions;
- **technical execution state** such as thread, transaction, queue-consumer or
  scheduler state is implementation/runtime knowledge.

Do not introduce a mandatory ProcessState Core entity. A short-lived process
whose continuation is fully determined by existing accepted facts may need no
independent canonical process-state representation.

## Inputs

Application process knowledge may consume accepted canonical knowledge from:

- Product Requirements;
- Domain Use-Case Design;
- Tactical Domain Design where identities, lifecycle or invariants affect flow;
- Application Design operations and orchestration decisions;
- Task Model and User Journey knowledge where human work participates;
- Security Architecture where authorization changes observable process paths;
- Concurrency/Consistency Design where interacting executions affect correctness;
- other accepted owner contracts required by the selected process scope.

Dependencies are semantic prerequisites, not workflow stages.

## Output

The output is a project-native canonical process contract sufficient for
downstream consumers to understand progression without inferring missing
orchestration from implementation.

A useful output identifies the bounded process and makes material flow semantics
machine- or human-addressable enough to support downstream design, verification
and projection.

The exact storage representation is project-native. Harness does not require a
universal process DSL in Core.

## Relationship to neighboring knowledge

### Domain Use Cases

Domain Use-Case Design owns bounded domain behavior.

It answers:

> What domain behavior occurs for this responsibility, under what
> preconditions, and with what semantic outcomes?

It deliberately does not own cross-use-case workflow sequencing.

Application Process knowledge may compose accepted use-case outcomes but must
not redefine their domain truth.

### Application operations

Commands, queries and materializations are application operations.

They answer:

> What application responsibility can be requested or observed?

A process answers a different question:

> How are such responsibilities causally and temporally composed to reach a
> bounded outcome?

Operation identity can therefore be reused as a process activity without making
the operation itself a process.

### Task Model

Task Model owns intended human work and responsibility allocation for user goals.

A process may include USER, SYSTEM or EXTERNAL_ACTOR activities from task
knowledge, but process control-flow completeness and human-task completeness are
different concerns.

### User Journey

User Journey Design owns one user-goal-oriented interaction scenario, including
observable alternate/recovery paths.

A user journey can be a process view or contributor to process knowledge, but
the application process may span work with no user interaction, several actors,
long waits or cross-capability orchestration beyond a single journey.

### Concurrency and consistency

Process knowledge may state that work can proceed concurrently or must wait for
another outcome.

Correctness rules for interacting executions — isolation, ordering, conflict,
retry/idempotency and consistency semantics — remain owned by
CONCURRENCY-CONSISTENCY-DESIGN when independently applicable.

### System Architecture

Process semantics do not select runtime topology, queues, protocols, service
boundaries or deployment mechanisms.

Architecture may realize an accepted process, but implementation topology is not
process truth.

### Domain process concepts

A project's domain model may contain concepts named Process, Business Process,
Workflow or similar terms. Such a concept remains domain-owned when it carries
business identity, lifecycle, invariants or meaning.

An Application Process is the application-level causal/temporal composition of
accepted work. It must not silently reinterpret a domain Business Process as an
executable workflow, and a matching name does not establish identity between
the two concepts.

If a domain Process participates in an Application Process, reference its
accepted domain identity and semantics rather than copying or extending them
inside the application process contract.

## Projection boundary

Process notation is downstream representation.

The canonical direction is:

```text
accepted project knowledge
        ↓
canonical application-process knowledge
        ↓
source-bounded projection
        ├─ BPMN
        ├─ UML Activity
        ├─ Sequence
        └─ other process views
```

A generated process diagram:

- provides no CapabilityId;
- does not become canonical because it is checked into Git;
- must not invent missing flow semantics;
- must preserve source provenance and freshness;
- may be deleted and regenerated without losing accepted engineering truth.

Specialized process-diagram generation uses
`docs/design/document-projection-operations-v0.md`.

A BPMN projection is therefore a future projection vertical slice, not the
definition of the process knowledge model.

## Separation from Harness operation orchestration

Project application processes and Harness agent-operation orchestration are
different semantic domains.

`docs/design/operation-orchestration-v0.md` defines how the active agent
coordinates routed Harness operations. That sequencing:

- is an agent execution mechanism;
- is not project truth;
- is not a project workflow/state-machine engine;
- must not be reused as the canonical model of the target application's process.

Application Process Model describes the target project's accepted behavior.

## Capability and knowledge-kind direction

This contract establishes the semantic boundary but does **not** yet add a new
registered knowledge kind or mandatory CapabilityId family.

A process may be exposed as an independently addressable Capability inside
APPLICATION-DESIGN before any new knowledge kind exists, for example:

```text
<project>.application-process.<scope>
```

Such a Capability can still use the existing `application-design`
knowledge kind when the same Application Design procedure can produce and
accept it coherently. Capability identity expresses independently consumable
project knowledge; it does not require a one-to-one Authority or knowledge-kind
split.

Introduce a routed `application-process-design` knowledge kind only after a
vertical slice demonstrates that process production needs a materially distinct
procedure, acceptance contract or lifecycle that would distort the existing
`application-design` route.

Do not add that registry/runtime surface merely because a diagram format exists.

## Applicability

Explicit process knowledge is useful when accepted behavior contains material
composition that downstream consumers would otherwise have to reconstruct, for
example:

- cross-capability orchestration;
- multiple participants;
- conditional branches;
- asynchronous waits or external continuation;
- parallel work;
- material failure/recovery/compensation paths;
- long-running or resumable execution;
- process-wide completion semantics.

It may remain NOT_APPLICABLE when independent use cases/operations already
provide all required downstream meaning and no material flow has to be owned.

## Acceptance criteria

An accepted process contract should satisfy:

1. every material activity traces to accepted upstream behavior or an owned
   Application Design decision;
2. the process-instance boundary distinguishes in-process work from
   prerequisites, domain history and provenance;
3. domain outcomes and invariants are consumed rather than re-owned;
4. material causal relations distinguish control precedence from preconditions,
   data dependency, provenance and concurrency rather than using generic source
   ordering as control flow;
5. branching, waiting, parallelism, convergence and completion semantics are
   explicit only where accepted knowledge supports them;
6. failures, cancellation, alternate outcomes and recovery remain
   distinguishable where they affect accepted behavior;
7. process state/progress is explicit only when independently semantic, and
   technical workflow/runtime state is not promoted to project truth;
8. unresolved upstream meaning becomes a Question rather than an invented path;
9. transport, persistence and runtime topology are not promoted to process
   semantics without an owning upstream decision;
10. a notation-specific projection can be produced without adding new project
    meaning.

## Non-goals

This contract does not introduce:

- a new Core entity;
- a PROCESS-DESIGN Authority;
- a universal project workflow engine;
- Stage, Phase, Gate, Approval or Handoff semantics;
- a universal process DSL;
- BPMN as canonical truth;
- infrastructure messaging semantics;
- task/project-management workflow;
- Harness agent-operation sequencing as project behavior.

## Validation evidence

Two separate checks are required because NAPMS currently pins an older Harness
runtime.

### Real-project semantic evidence

NAPMS `main` pins Harness
`d85bbf9152381605a5d3e8b166d15cc70b1d420c`, while the Harness baseline used
for this model is `2c38f2c1560a64406ca089a60e69b64e3ab9dba4` (67 commits ahead).

A real-project thin slice in NAPMS draft PR #202 added:

```text
engineering.application.process.policy-export
authority: APPLICATION-JOURNEY-DESIGN
knowledge_kind: application-design
```

Under the pinned older runtime the project remains structurally valid and the
System Architecture contract can consume the process Capability directly.
This establishes useful project evidence, but it is not by itself proof of
compatibility with current Harness.

A direct NAPMS repin experiment in draft PR #203 fails before process semantics
are evaluated because NAPMS still invokes retired Harness root-script paths such
as `repository_realization.py` and `engineering_coverage.py`. Current Harness
uses the packaged/distribution layout. This is an integration-migration gap,
not evidence against the process model.

### Current-Harness executable evidence

Harness draft PR #177 adds an isolated Scenario Suite case directly on current
`main`. The full `make harness-check` gate passes.

The scenario proves that current Harness:

- routes a missing process Capability through the existing
  `application-design` skill;
- treats the process as an independently addressable Capability without a new
  Authority or knowledge kind;
- supplies that Capability as the direct input to System Architecture;
- keeps the broader Journey only as same-Authority supporting upstream context.

Together these checks support a separate process Capability inside the existing
Application Design Authority and provide no evidence for a new Core concept,
`PROCESS-DESIGN` Authority or routed `application-process-design` knowledge
kind.

A subsequent source-bounded BPMN v0 projection in NAPMS PR #202 reads only
the canonical process artifact. Its design/architecture/coverage/integration
checks pass. The renderer fails closed when waits, timers, parallelism,
convergence, compensation or independent process state become applicable, and
does not infer Service Tasks, Message Flows or other runtime-specific BPMN
semantics. This provides concrete evidence that BPMN can remain a disposable
projection when the canonical process contract is sufficiently explicit.

## Adoption sequence

Use the smallest evidence-driven path:

1. exercise this boundary against one real project process;
2. expose one minimal process Capability under APPLICATION-DESIGN using the
   existing `application-design` route;
3. test whether a downstream consumer can use that Capability and its declared
   dependency closure without reconstructing control flow from neighboring
   artifacts;
4. introduce `application-process-design` only if the production/acceptance
   procedure proves materially distinct from ordinary Application Design;
5. after canonical process knowledge exists, implement one process-projection
   vertical slice, with BPMN as a candidate rather than a prerequisite;
6. extract shared abstractions only after more than one process projection or
   producer demonstrates the same invariant.
