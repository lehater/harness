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
```

Each provider assertion contains:

- the selected CanonicalArtifact provider;
- one public CapabilityId;
- an opaque semantic `acceptance_id`;
- the exact current prerequisite Capability acceptance identities against which
  that capability was accepted.

The identity is Capability-granular, not file-revision-granular. One artifact
may therefore expose several independently current capabilities.

## Derived states

### CURRENT

A Capability is CURRENT only when:

1. a lifecycle assertion exists for the selected provider;
2. every production prerequisite is CURRENT;
3. every recorded prerequisite acceptance identity equals the currently
   selected prerequisite acceptance identity.

### STALE

A provider/assertion exists but at least one prerequisite is non-current or its
current acceptance identity differs from the recorded baseline.

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

When an upstream acceptance identity changes:

```text
upstream accepted revision changes
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
file dependencies.

## Admission integration

`semantic_admission.py` emits the lifecycle assertion for an ACCEPTED
candidate. For non-root productions, admission fails unless every production
prerequisite is CURRENT and therefore has an acceptance identity that can be
recorded in the new baseline.

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
