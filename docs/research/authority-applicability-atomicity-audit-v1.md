# Research — Authority applicability atomicity audit v1

Status: research candidate.

## Decision rule

Authority is a safe Project Authority Registry unit only when its material decision family is applicability-atomic. Different capability consumers are normal. Split only when sibling decision families show independent applicability, decision identity, accepted outputs, consumers and lifecycle.

## Findings

### STRATEGIC-DOMAIN-DESIGN — SPLIT REQUIRED before registry canonicalization

Current boundary combines two independently applicable decision families:

1. Domain Strategy: subdomain landscape, strategic classification, investment/domain vision.
2. Model Context Strategy: bounded model-language applicability, context relationships and translation contracts.

Falsification cases exist in both directions:
- one coherent business area can need multiple model languages/translation boundaries while no strategic subdomain classification is material;
- a product can need strategic subdomain/investment decisions while operating one coherent model context with no independent context-boundary contract.

The families have distinct accepted outputs, consumers and change lifecycles. Keeping one applicability bit would hide real REQUIRED/N/A combinations.

Candidate split names:
- DOMAIN-STRATEGY
- MODEL-CONTEXT-STRATEGY

Do not canonicalize names until catalog migration and production contracts are updated together.

### SYSTEM-ARCHITECTURE — SPLIT CANDIDATE: concurrency/consistency

System topology and concurrent-state semantics can activate independently. Concurrency/consistency may be required because accepted invariants plus execution/retry topology create ordering/isolation/atomicity obligations, even when the broader topology is already stable.

However existing research also treats concurrency-consistency as cross-Authority analysis and currently routes realization constraints through System Architecture/Data/Verification. Before introducing a new Authority, require a fixture proving an independently accepted concurrency contract with independent consumers/lifecycle that cannot coherently remain a System Architecture production contract.

Result: WATCH. Registry canonicalization must either prove System Architecture applicability remains atomic or split this boundary.

### QUALITY-DESIGN — KEEP for current evidence

Performance/capacity and availability/reliability have independently selectable constraints, but current repository evidence treats QUALITY-DESIGN as ownership of the common class: explicit measurable realization quality constraints. Specialized analyses route targets into that accepted constraint contract.

Different quality dimensions and consumers do not yet prove independent ownership/lifecycle. Keep one Authority unless a fixture demonstrates one quality family must remain independently live while another changes without changing the common quality contract.

## Registry gate

Project Authority Registry is not ready for canonicalization while STRATEGIC-DOMAIN-DESIGN remains non-atomic and SYSTEM-ARCHITECTURE remains unresolved.

Add applicability_atomicity to the Authority boundary audit:
- semantic_cohesion
- independent_change
- public_contract
- applicability_atomicity

Do not introduce PARTIALLY_APPLICABLE as a workaround.
