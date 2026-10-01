# Capability Lifecycle Projection v1

Status: canonical.

## Purpose

Prove whether an accepted Capability assertion is still current against the
accepted prerequisite Capability assertions on which its semantic acceptance
depended.

Lifecycle currentness is derived integration knowledge. It owns no engineering
decision and introduces no workflow, task, approval, incident or generic
evidence entity.

## Representation

```yaml
version: 1
kind: harness-capability-lifecycle
providers:
  - artifact: TARGET-ARCHITECTURE
    capability: example.architecture
    acceptance_id: architecture-acceptance-7
    accepted_prerequisites:
      example.requirements: requirements-acceptance-4
      example.domain: domain-acceptance-3
    semantic_atom_fingerprints:
      ARCH-BOUNDARY: SAF-...
    accepted_prerequisite_semantics:
      example.requirements:
        exhaustive: true
        semantic_atoms:
          REQ-AUTHORIZATION: SAF-...
        source_surface_fingerprints:
          REQ-AUTHORIZATION: SAF-...
          REQ-NONAPPLICABLE-NOTE: SAF-...
```

Each provider assertion contains:

- the selected CanonicalArtifact provider;
- one public CapabilityId;
- an opaque semantic `acceptance_id`;
- the exact current prerequisite Capability acceptance identities against which
  that capability was accepted;
- optional fingerprints for its accepted semantic atoms;
- optional exhaustive prerequisite-semantic baselines containing both consumed-atom fingerprints and the complete accepted upstream source surface.
- optional `acceptance_policy_fingerprint` binding the accepted provider to the effective semantic/decision/evaluator rules used by strict admission.

The acceptance identity remains Capability-granular. When no authoritative
semantic baseline is available, lifecycle retains the conservative
Capability-level behavior. A finer baseline is admitted only from an ACCEPTED
derivation evaluation whose lifecycle dependency surface is explicitly
exhaustive: every upstream semantic assertion must be either consumed or
explicitly dispositioned. This prevents partial dependency evidence from
suppressing necessary revalidation.

## Derived states

### CURRENT

A Capability is CURRENT only when:

1. a lifecycle assertion exists for the selected provider;
2. every production prerequisite is CURRENT;
3. for a prerequisite without a semantic baseline, its recorded acceptance
   identity equals the current acceptance identity;
4. for a prerequisite with an exhaustive semantic baseline, every consumed atom still exists with the recorded fingerprint and the complete upstream semantic surface has the same atom ids and fingerprints as when the derivation was accepted. A changed, added or removed atom that was previously dispositioned as irrelevant changes the exhaustive decision surface and therefore requires revalidation.
5. when the caller supplies current acceptance-policy fingerprints, the provider's recorded `acceptance_policy_fingerprint` matches the current fingerprint for that Capability. A missing or different baseline is STALE because currentness under changed acceptance rules has not been proven.

### STALE

A provider/assertion exists but at least one prerequisite is non-current, a
coarse acceptance baseline changed, or a consumed semantic atom is missing or
has a different fingerprint.

STALE means "not proven current against the selected baseline", not
"semantically wrong".

The owning Authority must explicitly revalidate or replace the capability.

### UNKNOWN

A provider exists but required lifecycle evidence is absent.

UNKNOWN never satisfies strict semantic/currentness closure and is not reported
as REVALIDATE because Harness lacks evidence that the capability was accepted
against any known baseline.

### MISSING

No current provider exists. Ordinary CREATE/WAIT semantics remain applicable.

## Propagation

When relevant accepted upstream knowledge changes:

```text
upstream accepted revision changes
        ↓
consumed atom changed? ── no ──→ downstream may remain CURRENT
        │
       yes
        ↓
direct accepted consumer = STALE / REVALIDATE
        ↓
later consumers remain non-current / PENDING
        ↓
owner revalidates against new baseline
        ↓
new acceptance identity + baseline
        ↓
CURRENT chain restored
```

Staleness follows Engineering Graph production prerequisites, not arbitrary
file dependencies. Strict semantic admission therefore rejects material semantic
provenance from a canonical artifact that is merely readable through
same-Authority `depends_on` support but is absent from the target production's
declared prerequisite capabilities. If that support is semantically material,
the Engineering Graph must expose it as a prerequisite so it receives an
acceptance/currentness baseline.

## Graph evolution and identity reconciliation

A lifecycle projection is a currentness projection, not an identity-migration
authority. Engineering Graph evolution therefore follows fail-safe identity
semantics:

- a lifecycle assertion whose CapabilityId is no longer produced by the current
  Engineering Graph is **obsolete** and inert; it does not invalidate the graph
  and cannot satisfy any new CapabilityId;
- when an existing CapabilityId's direct prerequisite set changes, its previous
  acceptance remains evidence that a provider existed, but its lifecycle state is
  STALE with a PREREQUISITE_TOPOLOGY mismatch until the owning Authority
  revalidates against the new prerequisite contract;
- rename, split and merge are never inferred from names, artifacts or list
  position. A newly introduced CapabilityId follows ordinary MISSING/UNKNOWN
  and semantic-admission rules and receives a new acceptance identity;
- obsolete rows may be retained in project-native history, but should be pruned
  from the next current publication snapshot. obsolete_lifecycle_rows exposes
  them deterministically for that reconciliation.

This keeps migration explicit without introducing a workflow or transferring
semantic acceptance across changed identities.

## Admission integration

`semantic_admission.py` emits the lifecycle assertion for an ACCEPTED
candidate. It publishes semantic atom fingerprints for accepted assertions.
For non-root productions, admission fails unless every production prerequisite
is CURRENT and therefore has an acceptance identity that can be recorded in the
new baseline. When ACCEPTED and exhaustive semantic-derivation evaluations are supplied,
admission records a self-describing `exhaustive: true` baseline with both the
consumed-source fingerprints and `source_surface_fingerprints` for every
upstream semantic assertion that was classified during derivation. Non-exhaustive derivation evaluations are not trusted for selective lifecycle baselines.

`semantic_closure.py` requires the selected lifecycle assertion to match the
ACCEPTED semantic-admission identity for every routed capability in the
Consumer closure.

## Compatibility

Core v0 structural evaluation remains available for migration and graph
inspection. Legacy providers without lifecycle metadata are not silently
treated as CURRENT by strict semantic/currentness closure.

Projects may persist or derive the lifecycle projection from project-native
revision/provenance systems. They must not fabricate acceptance identities from
timestamps or file modification times.

## Non-goals

Do not add:

- Stage/Phase;
- Task/Workflow/Approval;
- Incident/Event;
- generic Evidence;
- timestamps as semantic currentness;
- automatic semantic reacceptance.
