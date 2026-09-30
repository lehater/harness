# Reference Engineering Model v0 — research closure

Status: research result. No Harness Core canonicalization.

## Result

The original universal Reference Engineering Graph hypothesis survives only in a weaker and more useful form:

Reference Engineering Model + Accepted Project Truth Snapshot + Materialization Request -> deterministic fixed-point reconciliation -> existing Project Engineering Graph.

The Reference Model owns reusable construction rules. The generated graph remains the ordinary project Engineering Graph consumed by current Harness semantics. No Core entity is added.

## Top-down derivation

The catalog was derived from the canonical Engineering Coverage proof space, not from project graphs:

1. start from all 118 canonical semantic proof claims;
2. preserve current Authority ownership boundaries;
3. group claims only when the output is independently acceptable reusable engineering knowledge;
4. keep cross-Authority analysis methods as skills/lenses when no residual semantic product exists;
5. use PREP/NAPMS only after the model is frozen, as regression evidence.

Result: 39 Reference Capability Templates and 46 normalized predicates. Every canonical proof claim is routed to exactly one template claim surface. A claim surface is competence, not proof: a project capability emits only intrinsic primary claims plus exact claims activated by accepted concern applicability.

## Important falsification result

A generic Application Design template was too coarse. Application failure semantics can be independently required even when orchestration is not material, so v0 separates APPLICATION-FAILURE-CONTRACT from APPLICATION-ORCHESTRATION while keeping one Application Design Authority.

Generic reliability, recovery/continuity, performance/capacity, data-evidence, offline/sync, event-sourcing, consensus and generic risk analysis are not default Capability Types. Existing Harness research treats these as analysis/routing lenses unless an independently consumed semantic contract is proven.

## Convergence

For one immutable project-truth snapshot the materializer is deterministic and finite because it requires:

- no negation-by-absence;
- no self-activation from a template's own output;
- finite accepted subject inventories;
- an acyclic union of possible semantic REQUIRES edges;
- three-valued applicability;
- fail-closed conflict handling.

New accepted knowledge starts a new snapshot/materialization epoch. NOT_APPLICABLE never creates a fake CapabilityId.

## Independent hold-outs

The frozen model is tested against:

- ephemeral CLI;
- reusable library/SDK;
- offline-first synchronization;
- event-sourced service;
- Kubernetes-style controller;
- distributed consensus/storage;
- multi-tenant SaaS;
- regulated payments;
- zero-downtime migration;
- safety-critical system;
- AI/agentic system.

The first nine materialize STABLE. Safety and AI intentionally return REFERENCE_MODEL_GAP because the canonical Concern Catalog contains specialized.safety and specialized.ai while the canonical semantic proof contract does not yet define stable proof claims for those specializations. The experiment must expose that gap instead of inventing HAZARD-ANALYSIS or AI-RISK-ANALYSIS.

External stress-case sources include Android offline-first guidance, Microsoft Event Sourcing, Kubernetes controller documentation, the Raft paper, AWS SaaS tenant isolation, AWS Transactional Outbox, GitLab multi-version compatibility, PCI DSS, NASA software safety guidance and NIST AI RMF.

## Regression-only evidence

PREP and NAPMS are compatibility checks, not universality oracles. The executable regression requires at least 0.80 coverage of generated reusable knowledge kinds by each existing fixture, with explicit legacy aliases for older NAPMS aggregation.

## Mutation suite

The validator requires fail-closed behavior for cyclic REQUIRES, missing templates, unknown predicates, self-activation, contradictory project facts, REQUIRED/N/A conflict, dependency versus N/A conflict, missing subject inventory and unbounded scope expansion.

## Canonicalization decision

Do not change Harness Core and do not yet declare Reference Engineering Model v0 canonical.

Retain it as an optional research layer because it materializes the existing Engineering Graph, is deterministic, fails closed and exposes known incompleteness. Promotion should require another frozen external hold-out batch and a reference-model version-evolution/migration experiment, plus an explicit decision for safety/AI specialization proof semantics.

Current architecture:

optional Reference Engineering Model (research)
-> reference materializer
-> canonical existing Engineering Graph
-> unchanged Harness Core

## External references

- https://developer.android.com/topic/architecture/data-layer/offline-first
- https://learn.microsoft.com/azure/architecture/patterns/event-sourcing
- https://kubernetes.io/docs/concepts/architecture/controller/
- https://raft.github.io/raft.pdf
- https://docs.aws.amazon.com/whitepapers/latest/saas-tenant-isolation-strategies/
- https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/transactional-outbox.html
- https://docs.gitlab.com/development/multi_version_compatibility/
- https://www.pcisecuritystandards.org/standards/pci-dss/
- https://swehb.nasa.gov/
- https://airc.nist.gov/airmf-resources/airmf/
