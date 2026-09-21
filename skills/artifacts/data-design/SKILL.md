---
name: data-design
description: "Use for actionable CREATE work that defines physical persistence ownership, durable representation, constraints and transaction/isolation semantics from accepted domain/application/system/security truth."
---

# Data Design

## Trigger

Use when actionable work has `knowledge_kind: data-design` and persistence topology, schema constraints, durable representation or storage transaction semantics require independent decisions.

## Inputs

- accepted Domain and Application semantics;
- accepted System Architecture consistency/topology constraints;
- accepted Security/Quality requirements affecting storage;
- accepted lifecycle/history/provenance semantics;
- unresolved Data Design Questions.

## Read boundary

Use accepted semantic owners as truth. Existing tables, ORM models, migrations and production database shape are evidence only unless explicitly canonical inputs.

## Procedure

1. Assign physical persistence ownership to the accepted semantic owners; forbid accidental shared-write ownership.
2. Map stable identities, state, history and relationships into the smallest durable representation that preserves accepted meaning.
3. Define owner-local integrity constraints, uniqueness and temporal constraints required for correctness.
4. Define cross-owner reference representation and validation without inventing semantic ownership.
5. Define transaction/isolation/locking/version representation where Application/System consistency semantics require a physical realization.
6. Define durable idempotency/audit/provenance representation only when upstream contracts require it.
7. Define migration/schema-state constraints needed by the selected implementation; route non-trivial transition/coexistence semantics to Change Transition Design.
8. Apply accepted Security/Quality lifecycle/retention constraints; do not invent retention, encryption or backup policy.
9. State indexes/query plans/storage types as implementation freedoms unless they affect accepted semantics.
10. Route missing domain/application/security/quality meaning as Questions; produce/register the project-native data design and reevaluate.

## Stop conditions

Stop when identity/lifecycle/history semantics are unresolved; cross-owner transaction meaning is undecided; retention/protection obligations are required but absent; or a migration requires material intermediate-state decisions not owned by Data Design.

## Output contract

Useful content may include:
- physical ownership/schema boundaries;
- durable entities/tables/records and semantic keys;
- integrity/uniqueness/temporal constraints;
- cross-owner reference rules;
- transaction/isolation/locking/version requirements;
- migration/schema-state constraints;
- retention/protection applicability;
- implementation freedoms;
- Questions.

## Acceptance checks

- storage does not become a second semantic owner;
- every required constraint traces to accepted meaning;
- cross-owner FKs/writes are not introduced by convenience;
- transaction mechanics realize, not redefine, Application/System consistency;
- unknown lifecycle/security/retention policy is not silently defaulted;
- implementation can build persistence without inventing material data semantics.
- concrete database/runtime/tool choices appear only when the accepted input closure authorizes them; otherwise they remain Implementation Design decisions;
- material persistence assertions carry provenance to their semantic owner; copying a downstream implementation choice into Data Design is a semantic ownership violation;

## Registration

Register under DATA-DESIGN only when persistence decisions have independent value; provide all grouped data capabilities actually established.

## Human projection

Prefer project-native persistence/transaction documentation; schema diagrams are optional projections, not separate truth.
