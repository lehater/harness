# Software-product change lifecycle

Route non-trivial software-product changes from evidence to implementation without allowing a lower layer to invent unresolved higher-layer truth.

```text
S0 Problem / Evidence
  -> S1 Requirements
  -> S2 Domain Design
  -> S3 Architecture
  -> S4 Implementation Readiness
  -> Implementation
```

This is a reasoning model, not a runtime workflow engine and not a waterfall. Enter at the earliest layer whose accepted truth may change.

Each stage has Inputs -> Work -> Outputs -> Gate. A document existing does not mean the gate passed.

- S0 output: bounded problem/outcome, relevant evidence, explicit unknowns.
- S1 output: observable behavior, constraints and quality expectations.
- S2 output: coherent semantic ownership, language, identities, lifecycles, invariants and context contracts.
- S3 output: realization structure and technical constraints that preserve accepted semantics.
- S4 output: bounded implementation slice, tests/migrations/risks and executable acceptance evidence.

Strategic and Tactical DDD are routes inside S2, not separate top-level stages.

Routing: implementation-only detail -> S4; architecture concern -> S3; domain semantic concern -> S2; accepted behavior/quality concern -> S1; unclear need/conflicting evidence -> S0.

Outcomes: PASS, REWORK, REOPEN(Sx), BLOCKED. P0/P1 findings prevent PASS for guarantees they affect. Repeat work only when the iteration is expected to change evidence, accepted knowledge, decision state, problem state or uncertainty scope.
