---
name: source-classification-registry
description: "Use for an actionable CREATE that requires exhaustive explicit classification of versioned source entities into a controlled project taxonomy. Prefer a project-native registry plus deterministic validator; do not invent heuristic classifications or force large project data into a generic Harness schema."
---

# Source Classification Registry

## Trigger

Use when a target-state `CREATE` requires a complete mapping from a pinned external/source identity set to one controlled project classification and the mapping itself is canonical project data.

The Nutrition Management BLS 4.0 category registry is the acceptance consumer for this skill.

## Inputs

- the actionable `CREATE` expectation and owning Authority;
- the accepted source-identity artifact;
- the accepted project taxonomy/classification artifact;
- any accepted policy governing assignment semantics;
- the exact source entity set to cover.

## Read boundary

Read only:

- the pinned source entity identifiers and evidence needed to classify them;
- the canonical project taxonomy;
- the accepted assignment policy;
- existing project-native data/validator conventions relevant to the registry.

Historical WIP may be used as implementation evidence, never as accepted semantic truth.

## Procedure

1. Confirm the expectation is `CREATE`, not `WAIT` or `PENDING`.
2. Confirm the source identity/version and expected entity cardinality are accepted.
3. Confirm the taxonomy and assignment policy are accepted.
4. Choose a project-native deterministic registry format appropriate for the target repository.
5. Require exactly one explicit assignment for every source entity.
6. Reject duplicate source ids, unknown source ids, missing source ids and invalid category values.
7. Do not infer canonical assignment from names, code prefixes, source-native groups, embeddings or model output unless an accepted policy explicitly authorizes that derivation.
8. Agent/model-assisted classification may propose candidate assignments, but ambiguous cases remain unaccepted until reviewed under the owning Authority.
9. Build or reuse a target-project validator that compares registry coverage to the exact pinned source set.
10. Only after the full registry passes deterministic validation and semantic review should it be registered as the provider capability.
11. Re-evaluate target state.

## Stop conditions

Create or preserve a Core Question instead of accepting the registry when:

- the accepted policy does not determine how ambiguous source items are classified;
- the source entity set cannot be reproduced from the pinned source identity;
- a category value requires changing the taxonomy;
- completeness can only be achieved with an implicit fallback;
- conflicting accepted evidence exists for an assignment.

## Output contract

Prefer a **project-native canonical artifact**, not a Harness-managed schema, when the registry is large target-specific data.

The output contract must specify:

- deterministic file format;
- source/version identity;
- source entity key;
- controlled category vocabulary;
- exact-coverage validator;
- deterministic ordering/serialization where relevant.

For the Nutrition Management BLS consumer, the intended artifact shape is a project-owned JSON registry conceptually equivalent to:

```json
{
  "mappings": [
    {"source_code": "A000001", "category": "fruit_and_vegetables"}
  ]
}
```

The actual accepted registry must cover the complete pinned source set, not a sample.

## Acceptance checks

- source/version matches the accepted input baseline;
- every source entity occurs exactly once;
- no extra source entity is present;
- every category belongs to the accepted controlled taxonomy;
- difficult cases are explicit decisions, not default fallbacks;
- deterministic validation succeeds against the exact pinned source set;
- the registry is owned by the Authority named by the expectation.

## Registration

Register the project-native registry as a normal Core `CanonicalArtifact`.

Its dependencies should include the canonical source identity, taxonomy and assignment-policy artifacts actually relied upon.

Its `provides` must name the classification capability from the actionable expectation.

## Human projection

Optional. Large classification registries do not require a generated Markdown copy merely to satisfy Harness.
