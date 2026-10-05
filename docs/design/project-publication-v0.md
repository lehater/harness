# Project Publication v0

Status: canonical.

## Purpose

A Capability completion may change several coordinated Harness views at once:
Core realization, semantic evaluations, capability lifecycle evidence, Core
Questions and Decision Pipeline failure evidence.

Those facts must become visible as one logical project revision. A reader must
observe either the previously published revision or the complete next revision,
never a mixture assembled from partially persisted components.

Project Publication is an Application/Integration boundary. It is not a Core
entity, workflow state, approval, task or second source of engineering truth.

## Logical snapshot

The canonical logical envelope is:

```yaml
version: 1
kind: harness-project-publication
revision: sha256:...
parent_revision: sha256:... | null
state:
  core_model: {...}
  semantic_evaluations:
    version: 1
    kind: harness-semantic-evaluation-set
    semantic_evaluations: [...]
    derivation_evaluations: [...]
  lifecycle:
    version: 1
    kind: harness-capability-lifecycle
    providers: [...]
  decision_failures:
    version: 1
    kind: harness-decision-failure-set
    failures: [...]
```

`revision` is a deterministic digest of `parent_revision + state`. It is an
integration identity for one coherent published snapshot. It does not replace
Capability acceptance identities.

The component documents retain their existing semantic owners. The publication
only binds which versions are visible together. The semantic-evaluation component
is the current snapshot defined by the semantic-acceptance contract: duplicate
artifact identities `(artifact, capability)` and duplicate derivation-edge
identities `(source_capability, target_capability)` fail closed before a
publication revision is accepted.

## Invariants

1. **Single visibility boundary.** Read models participating in the strict agent
   loop consume components from one validated publication revision.
2. **Coherent acceptance.** When a lifecycle row and semantic evaluation exist
   for the same artifact/capability, accepted admission identity and lifecycle
   acceptance identity agree.
3. **No partial mutation.** Editing one component without recomputing and
   publishing the complete envelope invalidates the publication revision.
4. **Compare-and-swap.** A transition names the revision it was prepared
   against. Publication fails if another writer has already changed the current
   revision.
5. **Terminal outcome validation.**
   - `CURRENT` requires a Core provider, matching ACCEPTED semantic admission,
     matching lifecycle assertion, no Core blocker and no persisted failure for
     the Capability.
   - `BLOCKED` requires an unresolved Core blocker affecting the Capability or
     one of its providers.
   - `FAILED_VALIDATION` requires current Decision Pipeline failure evidence for
     the Capability.
6. **Idempotence.** Re-applying the same complete state against its current
   revision is a no-op.
7. **No hidden persistence owner.** Harness validates and prepares the logical
   transition. The project integration owns durable storage.

## Transition

```text
published revision R
        ↓
agent forms terminal Capability result
        ↓
prepare complete next Core/evaluation/lifecycle/failure state
        ↓
validate terminal outcome + cross-component coherence
        ↓
CAS(expected=R)
        ↓
atomic publish R'
        ↓
recompute Decision Roadmap / Semantic Closure / Project Frontier from R'
```

A coordinator must not publish Core, lifecycle, semantic evaluation or failure
files one by one and then recompute between writes.

Question resolution is part of the next Core realization. A CURRENT transition
therefore becomes visible together with the accepted evaluation/lifecycle state
that justifies the resolved semantic identity.

## Direct declaration

A direct Harness-managed integration may persist one
`.harness/project-publication.yaml` and use
`project_publication.publish_project_publication`.

The helper takes an inter-process publication lock, re-reads the current
revision under that lock, checks the expected revision, writes a validated
temporary file in the destination directory, flushes it, then atomically
replaces the published path. A crash before replace leaves the previous revision
visible; concurrent writers serialize before the compare-and-swap check. After
replace, readers validate the revision before consuming the state.

The publication revision is defined over the decoded logical state, not over a
particular YAML spelling. The direct-file writer may therefore use lossless
serialization-level deduplication such as YAML anchors/aliases for repeated
fingerprint maps. Reading that file must reconstruct the same logical mapping,
and representational deduplication must not change revision, acceptance,
currentness or terminal-outcome semantics.

Separate convenience files such as `core.yaml` may still exist as generated or
migration views, but they must not be independently treated as the authoritative
strict-pipeline publication boundary.

## Adapter projection

A project-native adapter does not need to store the Harness YAML envelope.
It must provide equivalent semantics:

- one project-native snapshot/transaction identity;
- atomic visibility of all state needed to derive the four logical components;
- compare-and-swap or equivalent optimistic concurrency against the revision
  used to prepare the transition;
- reconstruction of one valid `harness-project-publication` view for Harness
  readers.

A database transaction, immutable repository commit, content-addressed snapshot
plus atomic pointer, or another project-owned mechanism is valid when it
satisfies those semantics.

Harness must not duplicate an existing project transaction/version system merely
to obtain its own persistence format.

## Recovery

After interruption, restart from the last valid published revision.

Temporary/staged files and uncommitted project-native transaction state are not
Harness truth. The coordinator recomputes the frontier from the last valid
publication and may retry the transition.

A mismatched digest, stale expected revision, mixed acceptance identity or
invalid terminal outcome fails closed before the new state is consumed.

## Migration

Legacy/static integrations remain readable through the existing individual
Core/lifecycle/semantic inputs.

They may not claim crash-consistent Decision Pipeline completion until their
agent execution path adopts this publication boundary or an equivalent
project-native atomic snapshot adapter.

This is an additive Application/Integration contract. It does not change Core
v0 entities or require a universal storage backend.
