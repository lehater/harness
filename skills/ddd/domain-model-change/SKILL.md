---
name: domain-model-change
description: "Use when a requirement, design question, code finding or stakeholder clarification may change target-project domain semantics, identity, lifecycle, invariants, responsibility ownership, Bounded Context boundaries or cross-context contracts."
---

# Domain Model Change

1. State the trigger as evidence, not as a conclusion.
2. Classify the highest affected owner: Requirements, Tactical DDD, Strategic DDD, Architecture or implementation-only.
3. Read only the smallest affected target-project canonical evidence.
4. Separate accepted facts, constraints, proposals, hypotheses, unknowns and conflicts using the Harness decision protocol.
5. Use Strategic DDD convergence when ownership/boundaries/relationships are affected.
6. Use Tactical DDD when identity/lifecycle/invariants inside an accepted context are affected.
7. Update the highest affected target-project canonical owner first.
8. Propagate only the required downstream delta.

A journey, use case, capability, class, table, API, package, service or deployment unit is not automatically a Bounded Context.
