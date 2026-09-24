---
name: concurrency-consistency-design
description: "Use for actionable CREATE work that must define concurrent-state ordering, isolation, atomicity, conflict or retry/idempotency semantics."
---
# Concurrency / Consistency Design

## Trigger
Use for `knowledge_kind: concurrency-consistency-design` when interacting executions can affect correctness-constrained state.

## Inputs
Accepted invariants/correctness constraints, execution topology, retry/delivery semantics and relevant persistence knowledge.

## Read boundary
Read only accepted domain correctness constraints and system/data execution facts needed to reason about interacting executions. Do not invent invariants, storage representation or topology.

## Procedure
1. Identify interacting executions and protected correctness constraints.
2. Define serialization, atomicity and isolation boundaries only where required.
3. Define conflict, retry/idempotency and ordering semantics.
4. Route missing domain/data/system meaning upstream; do not invent it.
5. Produce the smallest accepted consistency contract needed by consumers.
6. Apply semantic acceptance and register only capabilities actually established.

## Stop conditions
Stop when protected invariants, execution topology, delivery/retry behavior or required persistence semantics are unresolved and materially affect the correctness contract.

## Output contract
Prefer project-native artifacts. Accepted output must state relevant interactions, protected constraints, ordering/isolation/atomicity rules, conflict and retry/idempotency semantics, evidence, consumers and reopening conditions.

## Acceptance checks
- every rule traces to an accepted correctness constraint and interaction mode;
- no concurrency machinery is invented without applicability evidence;
- domain invariants, storage representation and system topology are not re-owned;
- unresolved prerequisites remain Questions.

## Registration
Register accepted capabilities under `CONCURRENCY-CONSISTENCY-DESIGN`.

## Human projection
Project-native correctness/consistency documentation is sufficient; generated summaries are disposable projections.
