# Strategic DDD convergence

Use when S2 work shows that semantic ownership, language or Bounded Context relationships are unsettled. The current model is a hypothesis to challenge, not proof that existing boundaries are correct.

Load only the affected scope: accepted requirements creating the semantic need; affected domain/context artifacts; accepted ADRs constraining ownership; concrete consumer/provider semantic needs; code/persistence only as secondary evidence when needed.

Capabilities, journeys and use cases are evidence, not automatic Bounded Contexts.

Look for semantic cohesion around ubiquitous language, authoritative decisions/facts, identity/lifecycle/invariants, authority/responsibility, independent change and stable semantic inputs/outputs.

For each candidate context make explicit its purpose, authoritative responsibility, decisions/facts owned, key identities/lifecycles/invariants, required inputs and public outputs.

Bad-boundary signals include duplicated/missing authority, dependence on peer-private domain models, split semantic lifecycle/invariants, or boundaries justified only by table/service/screen/package/deployment structure.

For each material context edge identify provider/owner, consumer, semantic input/output, crossing identity references, material time/unknown/provenance semantics and consumer obligations.

Strategic work is coherent when responsibilities have one owner, required relationships/contracts are explicit, consumers do not require peer-private models, no P0/P1 ownership contradiction remains, and remaining delivery questions can safely route to Architecture.

Promote accepted results only into target-project domain owners.
