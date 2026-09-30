# Reference Engineering Model evolution and migration v0

Status: research result.

## Question

Can Reference Engineering Model snapshots evolve without silently invalidating historical evidence or leaving stale project capabilities behind?

## Result

Partially, but canonical promotion is premature without explicit snapshot provenance.

The experiment establishes a minimal model:

immutable Reference Model snapshot
→ deterministic fingerprint
→ explicit migration map for destructive identity changes
→ rematerialization
→ obsolete/new project CapabilityId diff

Template rename, split, merge and predicate rename are all detectable. Removed template or predicate identities fail closed unless an explicit migration operation accounts for them.

## Historical reproducibility

Current v0 materialization is deterministic for the same:

- Reference Model snapshot;
- accepted project-fact snapshot;
- materialization request;
- materializer semantics.

However the emitted materialization result does **not** contain the Reference Model fingerprint. Therefore a stored result cannot independently identify the exact Reference Model snapshot that produced it.

For research this is acceptable because the repository commit retains the snapshot. For canonical long-lived materialization evidence this is a promotion blocker.

## Rename experiment

Renaming `IMPLEMENTATION-STACK` to `IMPLEMENTATION-TOOLCHAIN` while preserving semantics:

- changes the Reference Model fingerprint;
- requires an explicit rename map;
- changes the generated CapabilityId;
- makes the old `*.implementation-stack` capability explicitly obsolete;
- creates a new `*.implementation-toolchain` capability.

The old capability must not remain current merely because its semantics look similar.

## Predicate evolution

Renaming `toolchain_selection_material` while migrating the accepted fact preserves the generated Engineering Graph exactly, but still changes Reference Model identity.

Therefore graph equality is not sufficient historical provenance.

## Split and merge

Explicit split and merge operations make destructive identity changes classifiable. This experiment deliberately does not define automatic semantic migration between split/merged templates; that requires project-specific accepted truth and must not be invented by the migration layer.

## Canonicalization consequence

Before Reference Engineering Model can become canonical, materialization evidence needs an explicit binding to at least:

- Reference Model fingerprint/version;
- accepted project-truth snapshot identity;
- materialization request identity;
- materializer semantics/version.

A model change then requires rematerialization, and obsolete generated capabilities must be surfaced rather than silently retained.

No Harness Core extension is required by this result.
