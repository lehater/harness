# Deep audit — SYSTEM-ARCHITECTURE

Verdict: SPLIT concurrency/consistency ownership from topology architecture.

## SYSTEM-ARCHITECTURE residual
Decision: system/runtime decomposition, runtime boundaries, dependency topology and technical interaction structure.
Accepted knowledge: system architecture/runtime topology.
Consumers: Component, Interface/Data realization, Implementation, Verification.
Encapsulation: downstream consumers need topology constraints, not architecture reasoning internals.

## CONCURRENCY-CONSISTENCY candidate
Decision: ordering, isolation, atomicity, conflict, retry/idempotency and consistency semantics when multiple executions can interact with correctness-constrained state.
Accepted knowledge: concurrency/consistency contract.
Consumers: Data, Component, Implementation and Verification/Test.
Activation evidence: accepted correctness constraints + interacting executions + correctness depends on ordering/isolation/atomicity.
N/A evidence: interaction cannot occur or cannot affect correctness.

Independent applicability is bidirectional: material topology can exist with no concurrent-state decision; concurrency semantics can become material while topology remains unchanged. The accepted consistency contract can change because retry/delivery/mutation semantics change without changing system decomposition.

Final research decision: current SYSTEM-ARCHITECTURE is not applicability-atomic. Candidate separate Authority: CONCURRENCY-CONSISTENCY-DESIGN. Final naming/capability migration remains canonicalization work.
