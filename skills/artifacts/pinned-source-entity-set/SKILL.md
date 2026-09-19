---
name: pinned-source-entity-set
description: "Use for an actionable CREATE requiring the exact identity set contained in a pinned external source. Derive a deterministic project-native entity baseline from verified source bytes; do not substitute counts, examples or unverified mirrors for the exact set."
---

# Pinned Source Entity Set

## Trigger

Use when a downstream artifact requires the exact entities present in a pinned external data source and source identity/version alone is insufficient.

## Inputs

- actionable `CREATE` expectation and owning Authority;
- accepted external source identity/version;
- exact expected source-file digest;
- source structure sufficient to extract entity identifiers;
- verified source bytes.

## Procedure

1. Confirm the expectation is `CREATE`.
2. Verify the input bytes against the accepted cryptographic digest before extraction.
3. Extract only the stable entity identity needed by downstream work.
4. Preserve source version and source digest in the generated baseline.
5. Validate expected cardinality when the accepted source baseline defines one.
6. Reject duplicate, missing or structurally invalid identifiers.
7. Serialize the entity set deterministically.
8. Validate the project-native candidate independently from downstream classification/normalization.
9. Semantically accept and register it only when it is derived from the pinned bytes and exactly represents the required entity set.
10. Re-evaluate target state.

## Stop conditions

Do not accept the entity-set artifact when:

- exact pinned source bytes are unavailable;
- the supplied bytes do not match the accepted digest;
- source structure differs from the accepted extraction boundary;
- entity identifiers are duplicated or expected cardinality is violated;
- extraction requires guessing identity from display names or other unstable fields.

Missing source bytes are an execution/input availability issue, not automatically a Core Question. Create a Core Question only if the source itself exposes a semantic ambiguity that the owning Authority must decide.

## Output contract

Prefer a small project-native deterministic artifact containing:

- source version/identity;
- verified source digest;
- complete stable entity-id set.

Example shape:

```json
{
  "source_version": "v1",
  "source_sha256": "...",
  "entity_ids": ["entity-001", "entity-002"]
}
```

The exact field names belong to the target project.

## Acceptance checks

- source digest equals accepted canonical source identity;
- entity identifiers are extracted, not inferred;
- entity set is complete for the selected source boundary;
- identifiers are unique;
- deterministic rebuild from the same bytes is byte-identical;
- artifact belongs to the Authority named by the expectation.

## Registration

Register the accepted project-native entity-set artifact as a normal Core `CanonicalArtifact`.

It depends on the canonical source-identity artifact and provides the exact entity-set CapabilityId required by downstream skills.

## Human projection

Normally none. This is machine-readable project evidence rather than a human document.
