# External Dependency / Supply-Chain Analysis

## Purpose

Check that material external dependencies and acquired artifacts are semantically owned and that realized dependency evidence can be verified against accepted engineering constraints without turning inventory/provenance into design truth.

## Inputs

- accepted Engineering Graph capabilities and Authority ownership;
- relevant CanonicalArtifacts;
- project-owned dependency selections and constraints;
- available lock/SBOM/provenance/signature/advisory/service evidence.

Production code is not design evidence.

## Procedure

For each material library, tool, base image, external data source, generated/acquired artifact or external service:

1. Identify the semantic capability or engineering need that makes the dependency relevant.
2. Identify the Authority owning that need and, separately, the Authority owning concrete selection when different.
3. Identify accepted architecture, security, quality and engineering-policy constraints.
4. Identify applicable external obligations through Obligation Analysis when law/license/contract/policy applies.
5. Identify selected realization and immutable/resolved identity where the project supplies one.
6. Identify provenance/integrity/inventory evidence. Treat it as evidence, never as accepted design solely because it exists.
7. Identify Verification evidence comparing realization against accepted constraints.
8. Route vulnerability, compromise, deprecation or upstream-change evidence to the semantic owner allowed to decide the response.
9. Use Capability Lifecycle only after an accepted capability assertion changes.
10. Use Change Transition Design when replacement introduces material coexistence, ordering, rollback, irreversible or retirement states.

## Output states

- COVERED — ownership, accepted constraints and required evidence closure are sufficient.
- NOT_APPLICABLE — concern does not apply, with canonical evidence.
- DEFERRED_NONBLOCKING — explicitly deferred with reopening condition.
- QUESTION — semantic ownership/applicability/resolution is unresolved.

## Invariants

- package/service identity is not an Authority boundary;
- SBOM/lockfile/manifest/signature/provenance/scanner output is not design truth;
- new vulnerability evidence is not automatically a Question or design change;
- dependency semantics are capability-first;
- implementation selection cannot redefine upstream product/domain/architecture semantics;
- evidence failure may reject a realized artifact without superseding accepted engineering knowledge;
- do not duplicate project-native supply-chain history in Harness.

## Escalation

Create a new Authority or Core primitive only after a demonstrated consumer failure that cannot be represented through existing Authority, Capability, CanonicalArtifact, Question, lifecycle and transition semantics.
