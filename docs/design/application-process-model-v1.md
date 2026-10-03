# Application Process Model v1

Status: canonical v1.

## Purpose

Define the minimum Harness ownership and acceptance boundary for canonical
application-process knowledge without imposing a universal workflow DSL or
notation-specific metamodel.

## Definition

An **Application Process** is the accepted specification of one bounded
occurrence of coordinated work.

APPLICATION-DESIGN owns only the process semantics that are not already owned
elsewhere:

1. **boundary** — what belongs to one process occurrence;
2. **composition** — constraints over participating work occurrences;
3. **continuation** — what permits valid continuation where continuation is
   independently material;
4. **completion** — when the occurrence reaches an accepted completion outcome.

The process does not become a second owner of the work, events, decisions,
actors, data or domain state that participate in it.

## Ownership

Application-process knowledge belongs to **APPLICATION-DESIGN**.

A process may be exposed as an independently addressable Capability, for
example:

```text
<project>.application-process.<scope>
```

Process Capability production is routed through the dedicated
`application-process-design` knowledge kind. This does not create a new
Authority: the decisions remain owned by APPLICATION-DESIGN. The separate
knowledge kind exists so routing, decision exploration and semantic admission
can enforce the Process v1 acceptance boundary without weakening or
overloading the broader `application-design` contract.

Do not introduce a `PROCESS-DESIGN` Authority or a Core Process entity.

## Canonical contract

A Process Capability must make the following semantics explicit when
applicable.

### Boundary

- stable process identity and scope;
- entry or trigger condition;
- what constitutes one process occurrence;
- accepted completion outcomes.

Accepted state created before the selected occurrence is an input or
precondition unless upstream semantics explicitly place its creation inside the
same occurrence.

### Referenced work

The process references existing accepted work such as:

- application operations;
- domain use cases;
- human/system tasks;
- subprocesses or other process capabilities.

The process owns the **participation and occurrence role** of that work inside
the process, not the work definition itself.

### Composition constraints

The process owns material constraints over possible work occurrences, including
where applicable:

- ordering or enabling;
- choice or exclusion;
- concurrency or synchronization;
- repetition;
- continuation or wait;
- decomposition or subprocess composition.

This is an open semantic vocabulary, not a Harness Core enum or universal DSL.

Generic source ordering must not be promoted to control semantics. Absence of an
ordering constraint must not be promoted to concurrency.

### Continuation

When a process can pause and later continue, the contract must state the
semantic condition that permits continuation.

Occurrence-identification or correlation semantics are canonical only when they
are required to determine which process occurrence may continue. Transport
correlation keys, broker metadata and workflow-engine identifiers remain
realization concerns.

### Recovery and compensation

Recovery, cancellation and compensation are explicit optional process
semantics when they change the accepted continuation or completion of the same
process occurrence.

Technical retry policy is not process truth unless the retry itself has
accepted application meaning.

### Semantic process progress

Independent process-progress state is canonical only when it is required to
decide valid continuation, recovery, cancellation or completion and cannot be
derived unambiguously from already accepted facts.

Do not introduce mandatory ProcessState. Workflow-engine, transaction, thread,
scheduler and queue-consumer state are not canonical process knowledge.

### Completion

The process owns the conditions under which its occurrence reaches each
accepted completion outcome.

Product Requirements or another upstream owner may own the desired product
outcome. The process owns only the mapping between its completion semantics and
that accepted upstream outcome.

## Referenced knowledge, not re-owned knowledge

Application Process may reference but must not redefine:

- Product outcomes and acceptance intent;
- Domain identities, invariants, lifecycle and state;
- Domain events and use-case semantics;
- Application operation definitions;
- Task and participant/role definitions;
- Decision logic;
- Data meaning and schema;
- Security entitlement and trust semantics;
- Interface and transport representation.

A process may bind referenced work to a referenced participant, event, decision,
data item or outcome where that binding is material to composition.

## Explicit neighboring boundaries

### Process vs State Machine

A Process specifies coordinated work occurrences and their composition.

A State Machine specifies valid states and transitions of one subject.

A domain state may enable process continuation and process work may cause a
domain state transition, but neither model re-owns the other.

### Process vs Event Model

An Event represents something that happened.

A Process may use an event as entry, continuation or outcome evidence, but the
event definition and transport topology remain independently owned.

A set of events is not itself a Process.

### Process vs Decision Model

A Decision produces an outcome from accepted inputs and decision logic.

A Process may reference the Decision and map its outcomes to continuation, but
does not copy or own the decision logic.

### Process vs Case Model

A Process is used when accepted coordination/composition itself is meaningful.

Do not force fundamentally case-like, situation-driven or discretionary work
into an increasingly universal Process metamodel merely to keep one behavioral
abstraction.

### Process vs Harness orchestration

Harness operation sequencing coordinates agent/runtime work. It is not target
project process truth and must never be promoted into the project's Process
Capability.

## Applicability

An explicit Process Capability is useful when downstream consumers would
otherwise have to reconstruct material composition, for example:

- cross-capability orchestration;
- conditional or alternative continuation;
- waits or external continuation;
- concurrency or synchronization;
- repetition;
- subprocess composition;
- material recovery or compensation;
- long-running or resumable execution;
- process-wide completion semantics.

It may be `NOT_APPLICABLE` when accepted operations/use cases already provide
all required downstream meaning and no independently valuable process
composition exists.

## Acceptance contract

An accepted Process Capability must satisfy:

1. **Boundary** — one process occurrence is distinguishable from prerequisites,
   domain history and provenance.
2. **Referenced work** — participating work traces to accepted upstream
   knowledge or an owned APPLICATION-DESIGN decision.
3. **Composition** — material constraints are explicit and use the narrowest
   supported semantics.
4. **Continuation** — waits/external continuation identify what permits valid
   continuation when applicable.
5. **Completion** — every material completion outcome has explicit completion
   semantics and, where needed, maps to an accepted upstream outcome.
6. **Ownership** — participating events, decisions, actors, data, domain state
   and operations are referenced rather than re-owned.
7. **Recovery** — cancellation/recovery/compensation is explicit when it affects
   accepted process meaning.
8. **Progress state** — independent semantic process state exists only when it
   cannot be derived from accepted facts.
9. **Unknown/NOT_APPLICABLE** — missing upstream meaning becomes a Question and
   irrelevant semantics are not invented.
10. **Consumer sufficiency** — a downstream consumer can understand the
    permitted organization of work and completion without reconstructing
    missing semantics from implementation or neighboring documents.

## Projection boundary

BPMN, UML Activity, sequence diagrams and similar notations are downstream,
source-bounded projections.

A projection:

- provides no independent CapabilityId;
- must not add project semantics;
- must fail closed rather than infer unsupported constructs;
- may be deleted and regenerated without loss of canonical knowledge.

Notation elements such as BPMN Gateways, Sequence Flows, Service Tasks, Message
Flows or workflow-engine state are not canonical Process concepts unless their
underlying meaning is independently present in accepted project knowledge.

## Non-goals

This contract does not introduce:

- a new Core entity or universal Process metamodel;
- a `PROCESS-DESIGN` Authority;
- a new Process Authority merely because `application-process-design` is routed;
- a universal process DSL or fixed constraint enum;
- BPMN as canonical truth;
- a workflow engine;
- mandatory ProcessState;
- decision logic, event schemas, domain lifecycle or data schemas;
- infrastructure messaging, persistence or runtime topology;
- Harness agent-operation sequencing as project behavior.

## Reference basis

The boundary is intentionally notation-independent and is informed by the
common distinctions found across:

- ISO 18629 / Process Specification Language (activity vs occurrence and
  constraints over occurrences);
- Workflow Patterns (control-flow behavior independent of a specific notation);
- BPMN (process notation and executable/projection constructs);
- UML Activities and State Machines (flow behavior vs subject lifecycle);
- DMN (decision semantics separated from process coordination);
- CMMN (case/situation-driven work distinct from prescribed process flow);
- declarative-process approaches such as Declare.

Harness uses these as reference semantics and coverage guidance, not as a
mandatory project representation.
