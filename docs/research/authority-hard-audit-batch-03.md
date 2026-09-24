# Authority hard audit — batch 3

## INTERFACE-DESIGN — SPLIT CANDIDATE

Current boundary says machine or human interfaces and shared technical representations.

Machine interface contracts and human interaction/presentation decisions can be independently applicable, produce different accepted knowledge, have different consumers and evolve independently. Repository already has distinct artifact kinds/skills for interface-contract, human-interface-design, presentation-system-design and screen-view-design.

A project can expose only machine APIs; another can have a local human UI with no public machine contract. One applicability bit therefore risks hiding independent families.

Verdict: SPLIT CANDIDATE. Audit machine-interface vs human-interface ownership explicitly before canonicalization.

## DATA-DESIGN — KEEP

Decision identity: durable physical data representation, persistence topology/schema constraints.

Knowledge output: persistence/storage contract.

Consumers: System/Component/Implementation/Verification and transition work. They need storage constraints without owning domain semantics.

Replication/recovery choices do not automatically form separate Authorities; they remain refinements until independent accepted contracts, consumers and lifecycle are demonstrated.

Verdict: KEEP.

## QUALITY-DESIGN — KEEP, with dimension falsification tests

Decision identity: accepted measurable realization constraints (performance, availability, scale, reliability etc.), not their realization.

Knowledge output: quality constraint contracts.

Consumers: System, Component, Operability, Verification, Implementation.

Independent quality dimensions are separately applicable, but applicability of the Authority asks whether any independently material realization-quality constraint requires ownership. Once REQUIRED, different capabilities can exist beneath it. Current evidence does not prove separate ownership classes.

Verdict: KEEP. Add fixtures showing dimension-selective capabilities without PARTIALLY_APPLICABLE Authority semantics.

## SECURITY-ANALYSIS — KEEP as analysis/coverage Authority

Decision identity: applicability and coverage of threats/controls against accepted design; route gaps rather than repair design.

Knowledge output: accepted security coverage evidence, verification obligations and Questions.

Consumers: Verification and owning design Authorities via routed gaps. Coverage evidence has terminal/audit value as well.

Encapsulation: survives only if analysis never owns trust/product/system decisions.

Applicability atomicity: threat/control families are dimensions of one coverage analysis contract.

Verdict: KEEP with strict non-ownership invariant.

## Batch result

- INTERFACE-DESIGN: SPLIT CANDIDATE
- DATA-DESIGN: KEEP
- QUALITY-DESIGN: KEEP
- SECURITY-ANALYSIS: KEEP

P1: INTERFACE-DESIGN needs explicit machine-vs-human boundary audit.
