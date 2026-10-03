---
name: application-process-design
description: "Use for actionable CREATE work that must establish independently consumable application-process knowledge: one bounded process occurrence, its referenced work, composition, continuation and completion semantics."
---

# Application Process Design

## Trigger

Use when actionable work has `knowledge_kind: application-process-design`.

The Capability must already exist in the project Engineering Graph. This skill
does not decide that a Process Capability is required and does not invent
project topology. Capability discovery/applicability belongs to the selected
Design Profile and Engineering Coverage.

## Inputs

- the selected Process Capability and its declared production prerequisites;
- accepted Product outcomes/acceptance semantics actually required by the process;
- accepted Domain Use Cases, domain identities/state/events actually referenced;
- accepted Application operations and Task/Journey knowledge actually referenced;
- accepted Security/Quality/Concurrency knowledge only when it constrains process semantics;
- unresolved APPLICATION-DESIGN Questions for the selected process scope.

## Read boundary

Load and obey `docs/design/application-process-model-v1.md`.

Read only accepted owner contracts admitted through the Capability's declared
`requires` boundary. Do not reconstruct process truth from controllers,
services, queues, database transactions, workflow-engine state, BPMN diagrams
or implementation ordering.

## Decision exploration

Before forming the candidate, run the `decision-explorer` agent skill for
`application-process-design` using the registered decision axes.

Explore materially different choices for occurrence boundary, composition,
continuation/correlation and completion/recovery where those choices are owned
by APPLICATION-DESIGN. Missing upstream meaning or a non-delegated material
choice becomes a blocking Question.

## Procedure

1. Define the stable process identity/scope and one occurrence boundary.
2. Identify entry/trigger semantics and accepted completion outcomes.
3. Reference participating operations/use cases/tasks/subprocesses without
   copying their owned semantics.
4. State only material composition constraints supported by accepted knowledge:
   ordering/enabling, choice/exclusion, concurrency/synchronization, repetition,
   continuation/wait and decomposition where applicable.
5. Define continuation/correlation semantics only when needed to decide which
   occurrence may continue; keep transport/broker/workflow-engine identifiers
   out of canonical process truth.
6. State cancellation/recovery/compensation only when they change accepted
   continuation or completion. Keep technical retry mechanics in their owning
   design boundary.
7. Introduce semantic process progress only when valid continuation/recovery/
   completion cannot be derived from existing accepted facts.
8. Map process completion to accepted upstream outcomes without re-owning those
   outcomes.
9. Record unsupported or unknown material semantics as Questions. Record
   NOT_APPLICABLE only where the project has enough evidence to exclude them.
10. Produce/register the smallest project-native canonical Process artifact and
    reevaluate downstream closure.

## Stop conditions

Stop and route a Question when process construction would otherwise have to
invent a Product outcome, Domain invariant/state/event meaning, Decision logic,
participant responsibility, Security entitlement, consistency rule or
architecture/runtime mechanism.

Stop when the process occurrence boundary itself cannot be distinguished from
pre-existing state, domain history or a neighboring process.

## Output contract

Produce one project-native Process contract sufficient for downstream consumers
to understand, without implementation reconstruction:

- process identity and occurrence boundary;
- entry/trigger semantics;
- referenced participating work;
- material composition constraints;
- continuation/correlation when applicable;
- recovery/compensation when applicable;
- independent semantic progress when applicable;
- completion outcomes and completion-to-upstream-outcome mapping;
- explicit Questions and NOT_APPLICABLE dispositions.

Represent canonical semantic assertions using these owned assertion kinds:

- `application-process-boundary`;
- `application-process-work-reference`;
- `application-process-composition`;
- `application-process-continuation`;
- `application-process-recovery`;
- `application-process-progress`;
- `application-process-completion`.

## Acceptance checks

- one bounded process occurrence is explicit;
- participating work is referenced rather than semantically re-owned;
- at least one independently valuable composition relation is explicit;
- continuation/correlation is explicit when material and does not encode
  transport/runtime identifiers;
- recovery/compensation is explicit when material and is not reduced to
  implementation retry mechanics;
- process progress is canonical only when independently meaningful;
- completion semantics are explicit and map to upstream outcomes without
  re-owning them;
- no BPMN/workflow-engine/runtime topology construct is promoted to canonical
  meaning merely because it exists in a projection or implementation;
- every assertion is traceable to accepted prerequisites or an owned
  APPLICATION-DESIGN decision;
- downstream consumers can use the Process Capability without reconstructing
  missing process semantics.

## Registration

Register the produced Capability under APPLICATION-DESIGN with
`knowledge_kind: application-process-design`.

The Capability's `requires` list must contain every canonical capability whose
semantics are materially consumed by the process and no generic union of all
possible process inputs.

## Human projection

Prefer the smallest readable process contract. BPMN, UML Activity and similar
diagrams are disposable downstream projections and must not become the
canonical artifact.
