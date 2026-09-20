# Capability Lifecycle Projection v0

Status: experimental contract validated against Nutrition Management and NAPMS.

## Purpose

Represent whether accepted Capability knowledge is still current against the accepted prerequisite Capability acceptance identitys on which its semantic acceptance depended, without changing Harness Core v0 or duplicating project-owned history.

## Boundary

This projection owns no engineering decision. It is derived/integration knowledge.

It does not introduce an Authority, workflow, approval, task, incident, evidence or generic change entity.

## Document shape

```yaml
version: 1
kind: harness-capability-lifecycle
providers:
  - artifact: TARGET-ARCHITECTURE
    capability: nutrition-management.architecture
    acceptance_id: architecture-acceptance-7
    accepted_prerequisites:
      nutrition-management.requirements: requirements-acceptance-4
      nutrition-management.domain.context-contracts: context-contracts-3
```

## Provider assertion

Each entry identifies one currently selected accepted Capability assertion.

Required fields:
- `artifact`: current CanonicalArtifact provider id in the Core realization;
- `capability`: CapabilityId provided by that artifact;
- `acceptance_id`: opaque stable identity of this accepted semantic assertion;
- `accepted_prerequisites`: exact mapping of every Engineering Graph production prerequisite CapabilityId to the prerequisite acceptance identity against which this assertion was accepted.

Acceptance identity is opaque. Harness must not infer order, age or superiority from its spelling or timestamp.

Revalidation may create a new acceptance identity even when materialized artifact bytes do not change, because semantic acceptance against a new baseline is a new assertion.

## Granularity

Lifecycle identity is Capability-granular, not artifact-granular.

One CanonicalArtifact may provide several Capabilities with:
- independent acceptance identities;
- independent prerequisite baselines;
- intentionally shared acceptance identities when the project explicitly models one semantic acceptance lifecycle.

Artifact revision/provenance may exist in the project but is not the invalidation key.

## Validation

For every lifecycle provider:
1. artifact exists in current Core realization;
2. artifact currently provides the CapabilityId;
3. CapabilityId exists in the Engineering Graph production topology;
4. accepted prerequisite keys equal the production prerequisite CapabilityIds exactly;
5. prerequisite acceptance identity values are non-empty opaque identities.

A lifecycle projection may be partial as integration data, but partial coverage cannot prove lifecycle-aware completeness.

## Derived states

For a Capability in the selected consumer closure:

### CURRENT
- a current provider exists;
- lifecycle assertion exists;
- every production prerequisite is CURRENT;
- every current prerequisite acceptance identity equals the recorded accepted prerequisite acceptance identity.

### STALE
Provider/assertion exists but at least one production prerequisite is not CURRENT or its current revision differs from the recorded baseline.

STALE means "not proven current against the selected baseline". It does not mean semantically wrong.

### UNKNOWN
Provider exists but lifecycle assertion/required revision coverage is unavailable.

UNKNOWN must never satisfy lifecycle-aware target completeness. It is reported as a lifecycle coverage gap, not REVALIDATE: Harness lacks enough acceptance evidence to claim staleness.

### MISSING
No current Core provider exists. Existing Core CREATE/WAIT semantics remain authoritative.

## Frontier

Evaluation order remains prerequisite-first.

- missing provider + no blocker -> CREATE;
- missing/provider blocked by unresolved Question -> WAIT;
- provider CURRENT -> SATISFIED;
- provider STALE or UNKNOWN and all target prerequisites are satisfied/current -> REVALIDATE;
- downstream whose prerequisites are not satisfied/current -> PENDING.

REVALIDATE routes to the Capability's owning Authority. It does not automatically change semantic truth.

If revalidation discovers uncertainty, the owner creates/routes a Question through normal Harness semantics.

## Supersession

Selecting a new current Capability acceptance identity:
- does not delete historical acceptance identities;
- does not assert downstream knowledge is wrong;
- causes baseline mismatch in direct consumers;
- makes those consumers STALE;
- propagates non-currentness transitively through the production DAG.

History remains project-owned. Harness only needs the current projection plus opaque identities needed to compare baselines.

## Integration

Projects may persist or derive this projection.

Adapters SHOULD reuse project-native accepted revision/provenance identity when it has the required semantics.

Adapters MUST NOT:
- use timestamps as semantic validity;
- use file modification alone as semantic acceptance;
- treat every file dependency as a production prerequisite;
- fabricate missing acceptance identities;
- duplicate project history merely to satisfy Harness.

## Backward compatibility

Core v0 remains valid without this projection.

Without lifecycle metadata, static Core/Engineering Graph evaluation continues to answer structural readiness under v0 semantics.

Lifecycle-aware evaluation must explicitly report unavailable/UNKNOWN coverage rather than silently treating legacy providers as CURRENT.

## Evidence

Nutrition Management demonstrated:
- fan-out/fan-in stale propagation;
- a single artifact providing independently consumed source-identity/source-structure capabilities;
- false positives from artifact-level acceptance identities.

NAPMS demonstrated:
- multiple public capabilities from System Architecture and Product Requirements;
- capability contracts more precise than canonical file dependencies;
- existing consumed-input race protection does not cover post-acceptance supersession.

## Promotion criterion

Do not promote lifecycle facts into Core until integration evidence shows that keeping them as a projection causes concrete consumer failure or unavoidable duplicated truth.

Current evidence supports this projection boundary.
