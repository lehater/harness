---
name: application-design
description: "Use for actionable CREATE work that composes accepted domain/product behavior into application commands, queries, orchestration and consistency semantics without re-owning domain truth or selecting infrastructure."
---

# Application Design

## Trigger

Use when actionable work has `knowledge_kind: application-design` and accepted behavior spans multiple domain responsibilities, requires orchestration, application-level materialization or explicit command/query consistency semantics.

## Inputs

- accepted Product Requirements/acceptance semantics;
- accepted Strategic/Tactical Domain and Domain Use-Case contracts;
- accepted quality/security constraints already available;
- unresolved application-composition Questions.

## Read boundary

Use accepted owner contracts. Do not infer application semantics from controllers, services, transactions, queues or existing implementation.

## Procedure

1. Enumerate application commands/queries/materializations required by accepted use cases.
2. For each operation identify semantic owner(s) read and the single owner(s) permitted to mutate.
3. Define orchestration order only where it affects accepted validity, atomicity, time or failure meaning.
4. Define cross-owner reference validation and snapshot/currentness requirements without selecting database/API mechanics unless upstream architecture already constrains them.
5. Define application outcomes: success, domain rejection, unresolved result, dependency failure and cancellation where material.
6. Define idempotency/concurrency/application-time semantics only when accepted behavior requires them; route physical locking/isolation representation to Data/System.
7. Keep domain invariants in Domain ownership, external representation in Interface, trust/protection in Security and runtime topology in System.
8. State implementation freedoms and explicit NOT_APPLICABLE choices.
9. Route missing upstream semantics as Questions rather than filling them with application conventions.
10. Produce/register the project-native application design and reevaluate.

## Stop conditions

Stop when orchestration requires an undecided domain invariant, product outcome, security entitlement, quality target or ownership rule; or when atomicity/currentness cannot be stated without first resolving upstream semantics.

## Output contract

Useful content may include:
- application commands/queries/materializations;
- owner collaboration and read/write responsibilities;
- orchestration/atomicity/currentness semantics;
- application-level error/outcome distinctions;
- synchronous/asynchronous applicability;
- implementation freedoms;
- Questions.

## Acceptance checks

- application composition never becomes a second domain owner;
- each write has explicit semantic ownership;
- cross-owner consistency is sufficient for downstream architecture/data design;
- failure/unresolved distinctions match accepted behavior;
- no infrastructure default is promoted to semantic truth.

## Registration

Register under APPLICATION-DESIGN only when the application-composition contract is independently valuable; provide all grouped capabilities actually established.

## Human projection

Prefer operation-oriented orchestration contracts rather than framework service/class diagrams.
