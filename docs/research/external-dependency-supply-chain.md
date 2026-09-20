# External Dependency / Acquisition / Software Supply-Chain Lifecycle Research

Status: research candidate. No Core change.

## Question

Does Harness need a new Authority or Core entity for external software dependencies, acquisition, build provenance, SBOM, reproducibility and software supply-chain lifecycle?

## External evidence

The research uses:
- NIST SSDF (SP 800-218): secure development includes acquiring and maintaining third-party components under explicit security practices.
- SLSA v1.2: source and build trust are separate tracks; build provenance records what produced an artifact, by which process and from which inputs; consumers verify actual provenance against expectations.
- SPDX: software-package metadata can represent explicit relationships among packages, files and documents.
- OpenSSF Scorecard: external project security posture is evidence for dependency-selection/risk decisions, not ownership of the application's semantic requirements.

These sources consistently separate: selection/requirements, source identity, build provenance, integrity evidence, and consumer verification.

## Candidate boundary

A tempting Authority is EXTERNAL-DEPENDENCY-DESIGN or SUPPLY-CHAIN-DESIGN.

Atomicity test:

### Semantic cohesion — FAIL

The candidate combines materially different decisions:
- whether a product needs an external capability;
- whether build-vs-buy is acceptable;
- which supplier/package/service is selected;
- legal/license obligations;
- security/trust requirements;
- version/update compatibility;
- runtime failure/degradation semantics;
- build and artifact provenance;
- vulnerability response;
- retirement/migration.

These do not form one atomic engineering decision boundary.

### Independent change — FAIL

A dependency can change because:
- domain/application needs change;
- architecture changes;
- security policy changes;
- license/legal obligations change;
- an upstream release is incompatible;
- a vulnerability or compromise is discovered;
- build provenance becomes unacceptable;
- operational reliability changes.

The owner of the affected semantic decision varies.

### Public producer/consumer contract — FAIL as one Authority

No single reusable capability is consumed by all downstream work. Consumers need different accepted facts: selected external capability, compatibility constraints, trust/security constraints, build provenance expectations, license obligations, or transition plan.

Verdict: do not create a generic EXTERNAL-DEPENDENCY or SUPPLY-CHAIN Authority.

## Ownership decomposition

### Product / Domain / Application

Own why an external capability is needed and the semantics the application expects from it. A package name is not the requirement.

### System Architecture

Own placement of external systems/components and architectural trust/runtime boundaries.

### Implementation Design

Own concrete technology/package/service selection when selection is an implementation decision constrained by accepted upstream design.

### Security Architecture

Own trust boundaries, admissibility/enforcement structure and security constraints for acquired dependencies when applicable.

### Security Analysis

Own threat/control/applicability coverage, including dependency and supply-chain threats, without becoming the owner of the dependency semantics.

### Obligation Analysis

Own provenance/applicability/coverage of licenses, contracts, regulation and organizational mandates imposed by external components or suppliers.

### Quality Design

Own required compatibility, performance, availability and other measurable quality constraints.

### Change Transition Design

Own material version migration, coexistence, rollout, rollback and retirement semantics when changing an external dependency creates non-trivial transition states.

### Verification Design / Test Design

Own proof that selected/acquired artifacts satisfy compatibility, integrity and behavioral expectations.

## Important distinction: design truth vs acquired-artifact evidence

Harness must not treat an SBOM, lockfile, package manifest, vulnerability scan, signature or SLSA provenance as accepted engineering design merely because it exists.

They are evidence/materialization of the realized supply chain.

Canonical design says what is acceptable.
Acquisition/build evidence says what was actually obtained or produced.
Verification compares actual evidence with accepted expectations.

This is analogous to the lifecycle distinction between accepted semantic assertion and physical artifact revision.

## Dependency identity

A dependency reference needs at least conceptual separation between:
1. semantic role/capability expected by the application;
2. selected supplier/package/service identity;
3. selected version/range/revision;
4. resolved immutable artifact identity where available;
5. provenance/integrity evidence;
6. lifecycle/update state.

Collapsing these into a package/version string loses the reason for selection and makes replacement analysis unreliable.

This does not imply new Core entities. These facts may remain project-owned artifacts/capabilities.

## Build provenance and reproducibility

SLSA demonstrates that build provenance is a consumer-verifiable statement about artifact production inputs/process/builder, not the application's engineering decision itself.

Therefore BUILD-PROVENANCE is not an Authority.

Reproducibility is similarly not a universal Authority:
- required reproducibility level is a Quality/Security/Engineering Policy constraint;
- build mechanism belongs to implementation/build tooling;
- proof belongs to Verification;
- provenance is evidence.

## SBOM

SBOM is an inventory/evidence projection, not an Authority.

It may be generated from the realized dependency graph and used by Security Analysis, Obligation Analysis, incident response and verification. Making SBOM canonical design truth would invert the dependency: implementation inventory would become the source of requirements.

## Vulnerability and upstream-change lifecycle

A new CVE/advisory/upstream release is new evidence, not automatically new accepted truth.

Routing:
1. evidence identifies affected acquired dependency;
2. Security Analysis determines applicability/coverage for security findings;
3. owning semantic Authority decides required design change;
4. Capability Lifecycle marks dependent accepted knowledge stale only when an accepted upstream capability assertion changes;
5. Change Transition Design applies when replacement/migration has material intermediate states;
6. Verification proves the new realized dependency satisfies accepted constraints.

Do not create Questions merely because a scanner produced a finding. A Question is warranted when semantic applicability or required resolution is unresolved.

## External services

SaaS/API dependencies fit the same model even when no package artifact exists.

Their evidence may include:
- API/version identity;
- contract/SLA;
- trust/security attestations;
- observed compatibility;
- provider lifecycle/deprecation notice.

The ownership decomposition remains the same. Therefore a package-centric Core model would be too narrow.

## P0 findings

1. Generic dependency/supply-chain Authority fails atomicity.
2. SBOM, lockfiles, signatures and provenance are evidence/projections, not accepted design truth.
3. Dependency semantics must be capability-first; package/service identity is a selected realization.
4. Vulnerability/upstream events are evidence and must route to semantic owners rather than directly mutate design.
5. Build provenance and dependency inventory must not be forced into Core v0.

## P1 findings

1. Harness needs a reusable external-dependency/acquisition analysis method that checks ownership and evidence closure across existing Authorities.
2. The analysis must work for libraries, tools, container/base images, generated artifacts and external services.
3. Supply-chain expectations should be expressible as capabilities/constraints and verified against project-owned provenance/SBOM/lock evidence.
4. Material dependency upgrades should compose with Capability Lifecycle and Change Transition Design rather than invent another lifecycle system.

## Proposed reusable analysis

For every material external dependency:
- identify required semantic capability;
- identify Authority owning the need/selection;
- record accepted selection constraints;
- identify immutable/resolved realization evidence where applicable;
- identify trust/security requirements;
- identify legal/contract/license obligations;
- identify compatibility/quality constraints;
- identify provenance/integrity expectations;
- identify verification evidence;
- define upstream-change/vulnerability routing;
- determine whether migration requires Change Transition Design.

Output states:
- COVERED;
- NOT_APPLICABLE;
- DEFERRED_NONBLOCKING with reopening condition;
- QUESTION.

## Core decision

No Core v0 change is justified.

Existing concepts are sufficient:
- Authority owns semantic decisions;
- Capability expresses accepted dependency-related knowledge;
- CanonicalArtifact materializes it;
- Question represents unresolved semantic gaps;
- Engineering Graph routes consumers;
- Capability Lifecycle handles accepted-knowledge supersession;
- Change Transition Design handles non-trivial migration.

Supply-chain inventory/provenance remains project/integration evidence unless a future consumer failure proves a common missing Core primitive.

## Next validation

Validate this decomposition against:
1. Nutrition Management — Python/application dependencies plus BLS external data-source acquisition;
2. NAPMS — architecture/tooling dependencies and any external service/package constraints.

The validation must use canonical design artifacts, not production code as design evidence.
