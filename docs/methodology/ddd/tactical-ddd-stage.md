# Tactical DDD stage

Use inside an accepted Bounded Context boundary to define semantic identities, lifecycles, invariants and domain operations owned by that context.

Tactical DDD does not design persistence schemas, framework objects, transport DTOs or package structure.

## Working loop

1. State the semantic question without starting from a class/table proposal.
2. Confirm the accepted context owns the fact/decision; if unclear, return to Strategic DDD.
3. Identify the accepted requirement/context responsibility creating the need.
4. Define semantic identity and sameness over time where material.
5. Define meaningful lifecycle states/transitions only where required.
6. Define invariants and one semantic owner for each.
7. Distinguish authoritative domain state, source evidence, derived/rebuildable state and ephemeral calculation.
8. Define domain operations/facts in domain language.
9. Challenge persistence/framework/transport leakage.
10. Remove entities/state machines/aggregates that own no independent identity, lifecycle or invariant.
11. Resolve or route unknowns.
12. Update the smallest canonical domain owner in the target project.

## Coherence checks

- semantic identity is explicit where ambiguity matters;
- lifecycle distinctions change domain meaning, not only technical state;
- every invariant has one owner and justified consistency boundary;
- aggregate boundaries follow invariant ownership, not storage convenience;
- technical IDs/cache keys/row versions are not mistaken for semantic identity;
- derived/source state is distinguished from authoritative truth;
- domain operations do not depend on peer-context private models;
- no unresolved P0/P1 tactical contradiction remains.
