# Authority hard audit — batch 2

Method: decision → accepted knowledge → concrete consumer → dependency necessity → encapsulation → cohesion → independent evolution → applicability atomicity.

## TACTICAL-DOMAIN-DESIGN — KEEP

Decision identity: domain identities, lifecycles, invariants and semantic operations.

Knowledge output: accepted tactical domain model/invariants.

Consumers: Application, Component, Data mapping and Verification. Consumers need accepted invariants/identity semantics and must not invent them. Encapsulation holds because storage/transport/component decisions consume domain semantics without owning them.

Applicability atomicity: entities/value objects/aggregates/events are modeling forms, not independent applicability families. They refine one tactical semantic model.

Verdict: KEEP.

## APPLICATION-DESIGN — KEEP, narrow boundary

Decision identity: application-level orchestration/composition across accepted product/domain behavior.

Knowledge output: application flows/orchestration semantics.

Consumers: Interface, Component, Implementation and Verification where they need orchestration without re-deciding domain truth.

Falsification: journeys that only describe user interaction belong to interface/presentation ownership; domain behavior belongs upstream. Application Authority is justified only for cross-responsibility orchestration/materialization knowledge with real downstream consumers.

Verdict: KEEP with narrow orchestration boundary.

## SYSTEM-ARCHITECTURE — SPLIT CANDIDATE / canonicalization blocker

Current decision family includes topology/runtime boundaries plus dependency/consistency rules.

Topology output: system architecture/runtime topology.
Concurrency-consistency output: ordering/isolation/atomicity/retry consistency contract.

Hard test: concurrent-state semantics can become REQUIRED from accepted invariants + parallel execution/retries while no new topology decision is required. Conversely topology can be material while shared-state concurrency semantics are N/A. Consumers also differ: concurrency contract is directly consumed by Data/Component/Verification/Implementation.

This satisfies independent applicability and accepted-output evidence. Independent lifecycle is strongly plausible. Remaining question is whether consistency rules are a sub-contract of architecture or deserve independent Authority identity.

Verdict: SPLIT CANDIDATE. Before canonicalization run explicit fixture proving independent lifecycle/encapsulation. Do not treat current SYSTEM-ARCHITECTURE applicability as safely atomic yet.

## SECURITY-ARCHITECTURE — KEEP

Decision identity: trust boundaries, trusted identity, admission, credential/session protection and enforcement structure.

Knowledge output: accepted security architecture/trust and enforcement constraints.

Consumers: System, Interface, Data, Component, Operability, Verification and Implementation. These consumers require security constraints but do not need to co-own security reasoning.

Applicability atomicity: trust/identity/admission/protection can be selectively consumed but currently form one mutually constraining security structure. No fixture proves independently live Authority families.

Verdict: KEEP.

## Batch result

- TACTICAL-DOMAIN-DESIGN: KEEP
- APPLICATION-DESIGN: KEEP, narrow
- SYSTEM-ARCHITECTURE: SPLIT CANDIDATE / blocker
- SECURITY-ARCHITECTURE: KEEP

P1: SYSTEM-ARCHITECTURE still prevents treating the entire Authority catalog as applicability-atomic.
