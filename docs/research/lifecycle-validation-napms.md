# Lifecycle-aware evaluation validation: NAPMS

Status: second independent project validation.

## Evidence boundary

Validated against current canonical design-control artifacts:
- `docs/canonical-graph.yaml`;
- `docs/harness-core.yaml`;
- `docs/spec/harness-control-plane.yaml`.

Production code/tests were not used as design truth.

## Result

NAPMS independently confirms the capability-granular lifecycle model found through Nutrition, and exposes an additional integration requirement: lifecycle metadata must be projectable from a mature project-owned canonical graph/control plane rather than forcing a second persistent Harness graph.

## Existing NAPMS semantics already anticipate the problem

The control plane already requires:
- change the smallest owning canonical artifact set;
- determine downstream impact from the graph;
- reevaluate affected responsibility contracts;
- stop a coherent write if a consumed canonical input changes.

These rules establish that consumed-input currentness matters, but they do not persist/prove which accepted semantic revision of each consumed capability an output was accepted against.

Therefore the lifecycle gap is real even in a mature graph.

## Scenario P1 — security architecture changes

`engineering.architecture.security` is produced by SECURITY-ARCHITECTURE-DESIGN and consumed by:
- Interface Design;
- Quality Design;
- Security Analysis;
- Operability Design;
- Implementation Design;
- Verification Design;
- IMPLEMENTATION consumer.

If the security architecture changes, downstream artifacts must not all be blindly edited. The first direct consumers need semantic revalidation; later consumers remain pending until their prerequisite baseline is current.

This matches the REVALIDATE frontier model.

## Scenario P2 — system architecture has multiple public capabilities

SYSTEM-ARCHITECTURE materializes several independently consumed capabilities, including:
- C4 model;
- architecture rules;
- module contracts;
- async-messaging non-applicability evidence.

A single artifact/node revision is therefore not a safe semantic invalidation key. A change to one public capability must not automatically invalidate consumers of another unless their production contract actually requires it.

This independently confirms Nutrition's BLS multi-capability finding.

## Scenario P3 — Product Requirements exposes multiple capabilities

FIRST-MVP-REQUIREMENTS provides at least:
- product intent;
- acceptance semantics.

Different downstream consumers require different ones. Verification consumes acceptance; many design Authorities consume product intent.

Therefore capability revision must be independently addressable even when both are materialized by one canonical artifact.

## Scenario P4 — canonical graph dependencies are not enough

NAPMS canonical graph owns routing/dependency metadata and Harness contracts additionally express semantic capability requirements.

Lifecycle invalidation cannot simply traverse every canonical file dependency:
- internal same-Authority refinement edges exist;
- one artifact may expose no public capability;
- one artifact may expose several capabilities;
- a consumer contract can distinguish which capability is actually required.

The correct invalidation topology is the public capability contract graph, while the canonical graph remains the project-owned source for artifact routing.

## Scenario P5 — current control-plane race rule

The existing rule "a consumed canonical input changes before a coherent write" is a local concurrency safeguard.

Lifecycle staleness is broader:
- input may change after the downstream artifact was accepted;
- the change may be discovered days/releases later;
- downstream knowledge remains historically accepted but is no longer proven current.

Therefore the lifecycle mechanism is not redundant with optimistic write/concurrency checks.

## Architecture conclusion

Two independent projects now support the same decomposition:

1. CanonicalArtifact remains project-owned materialization/routing identity.
2. CapabilityId remains semantic public-contract identity.
3. Lifecycle projection associates current semantic revision with `artifact + CapabilityId`.
4. Each produced capability records accepted prerequisite capability revisions.
5. Engineering Graph/consumer contracts provide invalidation topology.
6. Evaluator derives CURRENT/STALE.
7. Agent frontier exposes REVALIDATE only for directly actionable stale knowledge.
8. Authority remains the only owner allowed to accept/revalidate semantics.
9. Question remains the mechanism for unresolved semantic uncertainty.

No new Authority is justified.

## Core decision

Evidence now supports a lifecycle extension, but still does **not** require embedding lifecycle fields into CanonicalArtifact in Core v0.

Preferred next design:
- define `harness-capability-lifecycle` as an optional projection contract above Core;
- adapters may derive it from project-native revision/provenance systems;
- Core v0 stays backward compatible;
- lifecycle-aware target evaluation is enabled only when projection coverage is sufficient for the selected consumer closure;
- partial/unknown coverage must never be reported CURRENT.

Only if repeated integrations show that every project must persist the same lifecycle facts in Core should they move into a future Core version.

## P0 findings

1. Capability-granular revision identity is independently confirmed by Nutrition and NAPMS.
2. Artifact-level revision invalidation is false-positive prone.
3. Currentness cannot be inferred from latest file content or timestamps.
4. Partial lifecycle coverage must fail closed for lifecycle-aware completeness: UNKNOWN is not CURRENT.
5. Project-native routing/history must be projected, not duplicated.

## P1 findings

1. NAPMS already contains control-plane semantics compatible with lifecycle-aware revalidation.
2. Existing write-race protection is necessary but insufficient for post-acceptance staleness.
3. Internal same-Authority artifacts without public capabilities need no lifecycle identity unless they are separately consumed as public knowledge.
4. Multiple capabilities from one artifact may intentionally share a revision, but this must be an explicit projection choice rather than an artifact-level assumption.

## Validation verdict

**PASS with refined representation.**

The lifecycle problem is demonstrated on two structurally different real projects.

The correct next step is no longer more ontology research. It is to finish the optional lifecycle projection contract and executable acceptance tests, then decide whether PR #29 research and the refined experiment are ready for canonicalization.
