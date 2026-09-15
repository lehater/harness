# Strategic DDD convergence

## Purpose

Converge on coherent semantic ownership and Bounded Context boundaries when ownership, language or context relationships are unsettled.

The current target-project model is a hypothesis to challenge, not proof that existing boundaries are correct.

## Inputs

Load only the affected target-project scope:
- accepted requirements creating the semantic need;
- affected domain/context artifacts;
- accepted ADRs constraining ownership;
- concrete consumer/provider semantic needs;
- code/persistence only as secondary evidence when needed.

## Boundary evidence

Capabilities, journeys and use cases are evidence, not automatic Bounded Contexts.

Look for semantic cohesion around ubiquitous language, authoritative decisions/facts, identity/lifecycle/invariants, authority/responsibility, independent change and stable semantic inputs/outputs.

For each candidate context make explicit its purpose, authoritative responsibility, decisions/facts owned, key identities/lifecycles/invariants, required inputs and public semantic outputs.

## Bad-boundary signals

- two contexts claim authority over the same fact/decision;
- no context owns a required fact/decision;
- one context must understand peer-private entities/state transitions;
- one semantic lifecycle/invariant is artificially split;
- the boundary exists only because of a table, service, screen, package or deployment.

## Relationship contract

For each material context edge state provider/owner, consumer, semantic input/request when applicable, semantic output/fact, identity references, time/unknown/provenance semantics where material, consumer obligations and forbidden reinterpretation.

The contract is semantic before it is transport or storage design.

## Convergence

Strategic work is coherent for the affected scope when authoritative responsibilities have one owner, required relationships/contracts are explicit, consumers do not need peer-private models, and no unresolved P0/P1 ownership/boundary contradiction remains.

Promote only accepted results to the target project's canonical domain owner.
