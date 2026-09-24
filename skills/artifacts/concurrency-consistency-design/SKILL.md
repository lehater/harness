---
name: concurrency-consistency-design
description: "Use for actionable CREATE work that must define concurrent-state ordering, isolation, atomicity, conflict or retry/idempotency semantics."
---
# Concurrency / Consistency Design
## Trigger
Use for `knowledge_kind: concurrency-consistency-design` when interacting executions can affect correctness-constrained state.
## Inputs
Accepted invariants/correctness constraints, execution topology, retry/delivery semantics and relevant persistence knowledge.
## Procedure
1. Identify interacting executions and protected correctness constraints.
2. Define serialization/atomicity/isolation boundaries only where required.
3. Define conflict, retry/idempotency and ordering semantics.
4. Route missing domain/data/system meaning upstream; do not invent it.
5. Produce the smallest accepted consistency contract needed by consumers.
## Acceptance
Every rule traces to a correctness constraint and interaction mode; no concurrency machinery is invented without applicability evidence.
## Registration
Register under CONCURRENCY-CONSISTENCY-DESIGN.
