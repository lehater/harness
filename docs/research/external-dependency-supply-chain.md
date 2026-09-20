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


## Real-project validation

### Nutrition Management

Evidence used: current canonical Harness graph and accepted design artifacts only. Production code was not inspected.

Nutrition provides two deliberately different dependency classes.

**BLS 4.0 external data source.** Food Knowledge explicitly owns accepted external-food data decisions and publishes separate source-identity, source-structure, source-code-set, evidence-semantics, errata and production-package capabilities. The accepted domain design says BLS 4.0 is the preferred/canonical MVP semantic baseline, retains provenance at the finest available level, permits manual/external preparation, and does not require online synchronization.

This is a strong counterexample to a generic SUPPLY-CHAIN Authority. The external source is part of Food Knowledge semantics: changing source identity can change accepted domain evidence semantics. Acquisition/import mechanics remain outer adapters and verification is separately owned. The existing capability graph already distinguishes source identity from derived/import knowledge.

**Implementation dependencies.** Accepted Implementation Design selects Python 3.14, uv with committed lockfile, SQLite, Alembic, SQLAlchemy, SCIP/PySCIPOpt and pytest, while explicitly stating that these are implementation choices rather than domain semantics. This independently confirms that concrete package/tool selection can be owned by Implementation Design while upstream semantic requirements remain elsewhere.

The committed lockfile requirement is evidence/control over resolved realization. It does not become the semantic owner of why SQLAlchemy, PySCIPOpt or another dependency is acceptable.

Nutrition verdict: PASS. Existing Authorities and capability granularity can express both semantic external data dependencies and implementation package/tool dependencies without a new Authority.

### NAPMS

Evidence used: current canonical graph, Harness responsibility contracts and canonical design-control contract only. Production code/tests were not used as design truth.

NAPMS explicitly states:
- product code/tests are forbidden as design truth;
- external Harness runtime dependency is forbidden;
- one semantic fact has one current owner;
- technologies/packages/deployment units must not cause an Authority split by themselves;
- generators may not invent missing semantic details;
- missing downstream knowledge routes to the Authority allowed to decide it.

This directly rejects technology/package identity as an Authority boundary.

NAPMS also separates System Architecture, Security Architecture, Quality, Security Analysis, Operability, Implementation Design and Verification Design through public capability contracts. An acquired dependency can therefore impose different concerns on different owners without requiring one supply-chain owner.

The control-plane rule that implementation must not depend at runtime on the external Harness repository is itself an accepted dependency constraint. It is project design truth. A package manifest or SBOM could prove whether realization obeys it, but cannot replace that rule.

NAPMS verdict: PASS. The model needs dependency evidence integration, not another Authority.

## Adversarial scenarios

### A — implementation library vulnerability

A CVE in SQLAlchemy/PySCIPOpt does not by itself rewrite Nutrition design. Security Analysis evaluates applicability. If the selected stack must change, Implementation Design owns the replacement selection; architecture/security/quality owners are involved only when their accepted constraints change. A non-trivial migration invokes Change Transition Design.

PASS without new Authority.

### B — BLS source supersession

A new BLS source/version is not merely a package upgrade. Food Knowledge owns whether the new source preserves/changes canonical nutrient semantics. Its accepted source-identity capability may receive a new acceptance assertion, after which Capability Lifecycle derives stale consumers.

A generic supply-chain owner would be semantically wrong here because it could not decide Food Knowledge equivalence.

PASS without new Authority.

### C — compromised build artifact with unchanged design

If source/design selections remain accepted but a resolved binary/package has unacceptable provenance/integrity, the failure is realization/evidence-level. Verification/security controls reject the artifact. No semantic capability needs to be superseded unless the response changes an accepted engineering decision.

This proves that acquired-artifact validity cannot be represented solely through Capability Lifecycle: lifecycle tracks accepted knowledge, while artifact provenance tracks realization evidence.

PASS, but exposes an integration requirement.

### D — external SaaS deprecation

Provider deprecation evidence routes to the Authority owning the external service's required semantic/architectural role. If replacement requires coexistence, data migration or staged cutover, Change Transition Design applies. License/contract changes route through Obligation Analysis.

PASS without package-specific Core semantics.

## Refined conclusion

The two projects confirm the no-new-Authority result, but expose a precise missing integration concern:

Harness needs a reusable **acquisition/supply-chain evidence analysis**, not a new semantic owner.

Its purpose is to prove that realized external dependencies satisfy accepted constraints while preserving the distinction:
- accepted engineering capability/constraint;
- selected realization identity;
- resolved immutable artifact/service identity;
- provenance/integrity/inventory evidence;
- verification result.

This analysis must not promote lockfiles, SBOMs, signatures, scanner findings or provenance statements into CanonicalArtifact design truth.

## Promotion criterion

Canonicalize the reusable analysis only if it can be expressed as a consumer of existing accepted capabilities and project-owned evidence without introducing duplicated dependency truth.

A future Core primitive is justified only if multiple integrations demonstrate that the same minimal acquired-artifact identity/provenance fact must be persisted by Harness itself rather than referenced from project-native evidence systems.

Current Nutrition and NAPMS evidence does not demonstrate that need.


## Contradiction and boundary review

Reviewed against the canonical Security Analysis and Capability Lifecycle contracts, plus the accepted boundaries established by the Obligation and Change Transition research.

### Security Analysis

No ownership collision.

Security Analysis determines threat/control applicability and routes security gaps to their semantic owners. External Dependency Analysis has a broader but shallower role: it checks dependency acquisition/evidence closure across security, quality, obligation, implementation and transition concerns.

Rule: when the question is "is this dependency/provenance/advisory security-relevant and what control is required?", Security Analysis owns the answer. External Dependency Analysis only requires that this route and its evidence closure exist.

### Obligation Analysis

No ownership collision.

License, supplier contract, regulation and organizational mandate provenance/applicability remain Obligation Analysis semantics. External Dependency Analysis must consume/route them and must not independently interpret license/legal applicability.

### Capability Lifecycle

No collision.

Capability Lifecycle tracks currentness of accepted semantic assertions. Supply-chain evidence tracks whether a realized/acquired artifact satisfies accepted constraints.

A provenance failure with unchanged accepted design must not produce STALE. Conversely a changed accepted dependency-selection capability can make downstream knowledge STALE even before a new artifact is acquired.

### Change Transition Design

No collision.

External Dependency Analysis detects that replacement may require migration/coexistence/cutover/rollback. It does not own those transition semantics. Material transition routes to CHANGE-TRANSITION-DESIGN.

### Verification

No collision.

External Dependency Analysis identifies required evidence categories and traceability closure. Verification Design owns what evidence proves accepted requirements and how proof is structured. The analysis must not invent test strategy.

### Atomicity of the analysis itself

This is intentionally an analysis method, not an Authority.

Its cohesion is a single audit question: "For each material external dependency, can accepted need/constraints be traced to selected realization and sufficient acquisition/provenance/verification evidence, with changes routed to the correct semantic owner?"

Its output does not become a new source of dependency truth. It is coverage/routing analysis.

Therefore the method may cross Authorities without violating Authority atomicity, in the same way Security Analysis can evaluate accepted design without owning it.

## Final research verdict

P0: no contradiction with Core, Engineering Graph, Capability Lifecycle or existing Authority boundaries.

P0: do not create EXTERNAL-DEPENDENCY-DESIGN, SUPPLY-CHAIN-DESIGN, SBOM, PROVENANCE or BUILD Authority.

P1: canonicalize External Dependency / Supply-Chain Analysis as a reusable cross-Authority analysis skill.

P1: keep actual inventory, lock, SBOM, signatures, attestations and build provenance project/integration-owned.

P1: route security interpretation to Security Analysis, normative source applicability to Obligation Analysis, accepted semantic changes to the owning Authority, semantic supersession through Capability Lifecycle, material migration through Change Transition Design, and proof design through Verification.

P2: future build/reproducibility research may refine evidence expectations but should not reopen the Authority conclusion unless it demonstrates an independently changing public semantic contract.
