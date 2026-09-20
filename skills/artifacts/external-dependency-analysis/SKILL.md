---
name: external-dependency-analysis
description: "Use to analyze material external dependencies and acquired-artifact evidence, trace accepted constraints to selected realizations, and route supply-chain gaps without turning inventory or provenance into design truth."
---

# External Dependency / Supply-Chain Analysis

## Trigger

Use when a material library, tool, base image, external data source, acquired/generated artifact or external service must be checked for ownership, acquisition/provenance evidence, upstream-change routing or supply-chain closure.

## Inputs

- accepted Engineering Graph capabilities and Authority ownership;
- relevant CanonicalArtifacts;
- project-owned dependency selections and constraints;
- available lock/SBOM/provenance/signature/advisory/service evidence;
- accepted build/reproducibility/artifact-identity constraints and build provenance where applicable.

## Read boundary

Accepted canonical design is authority. Production code is not design evidence. Lockfiles, manifests, SBOMs, signatures, attestations, scanner findings and build provenance are realization evidence unless a project explicitly accepts a semantic fact through its owning Authority.

## Procedure

1. Identify the semantic capability or engineering need that makes the dependency relevant.
2. Identify the Authority owning that need and, separately, the Authority owning concrete selection when different.
3. Identify accepted architecture, security, quality and engineering-policy constraints.
4. Route law/license/contract/policy applicability to Obligation Analysis when applicable.
5. Identify selected realization and immutable/resolved identity where the project supplies one.
6. Identify provenance/integrity/inventory evidence without promoting it to design truth.
7. Identify Verification evidence comparing realization against accepted constraints.
8. Route vulnerability, compromise, deprecation or upstream-change evidence to the semantic owner allowed to decide the response.
9. Use Capability Lifecycle only after an accepted capability assertion changes.
10. Use Change Transition Design when replacement introduces material coexistence, ordering, rollback, irreversible or retirement states.
11. For produced software artifacts, trace accepted source/build-environment/build-instruction identity, reproducibility expectations and build provenance where applicable; treat attestations as realization evidence.
12. Record each concern as COVERED, NOT_APPLICABLE, DEFERRED_NONBLOCKING with reopening condition, or QUESTION.

## Stop conditions

Stop and route a QUESTION when accepted dependency semantics, selection constraints, security applicability, normative applicability or required response cannot be decided by the analysis itself. Do not invent an upstream decision from package metadata or scanner evidence.

## Output contract

Produce dependency/evidence coverage containing semantic need, owning Authority, accepted constraints, selected realization when known, evidence references, verification closure, change routing and one explicit coverage state per material concern.

## Acceptance checks

- every material dependency traces to an accepted need or constraint;
- package/service identity is not treated as an Authority boundary;
- realization evidence is not silently promoted to canonical design;
- security and obligation interpretation route to their owning analyses;
- evidence failure may reject a realization without falsely making accepted knowledge STALE;
- accepted semantic changes use Capability Lifecycle;
- material migration routes to Change Transition Design;
- verification evidence traces to accepted constraints;
- reproducibility/provenance expectations are explicit rather than inferred from build tooling;
- build attestations do not become design truth;
- project-native supply-chain history is not duplicated in Harness.

## Registration

Register as a reusable cross-Authority analysis skill. Do not register EXTERNAL-DEPENDENCY-DESIGN, SUPPLY-CHAIN-DESIGN, SBOM, PROVENANCE or BUILD as an Authority solely to host this analysis.

## Human projection

Prefer a concise dependency/evidence coverage view organized by material dependency, accepted constraints, realization evidence, coverage state and routed gaps. Do not copy a package inventory or scanner report as the analysis.

## Invariants

- dependency semantics are capability-first;
- implementation selection cannot redefine upstream product/domain/architecture semantics;
- new vulnerability evidence is not automatically a Question or design change;
- Capability Lifecycle tracks accepted semantic assertions, not acquired-artifact integrity.
