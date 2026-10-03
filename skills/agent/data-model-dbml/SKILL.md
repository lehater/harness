---
name: data-model-dbml
description: "Generate one source-bounded DBML data-model projection for an explicit persistence scope without creating data semantics."
---

# Data Model DBML Projection

Status: canonical v1 slice.

## Trigger

Use only when the public `human-documentation-projection` operation has a
compiled plan section whose `renderer` is `data-model-dbml`, the section has
an explicit `scope`, and the coordinator resolves this internal operation
through `harness.application.skill_router` with
`invoked_by=human-documentation-projection`.

## Inputs

- current Human Projection manifest;
- current Human Projection plan;
- exact document id and section id routed to this operation;
- explicit persistence/data-model `scope-id` from that plan section;
- exact canonical source artifacts listed in that plan section;
- `spec/projection/dbml-data-model-v1.yaml`;
- target repository root.

## Read boundary

Read only CanonicalArtifacts listed in the selected plan section's `sources`.
Resolve their paths from the current manifest.

The normal primary source is accepted `data-design`. Additional canonical
sources such as `domain-model` or `interface-contract` may be used only when
they are already listed by the plan.

Do not search by knowledge kind and do not scan the repository. Do not use:

- `docs/generated/**`;
- previous DBML output;
- schema migrations;
- ORM entities;
- SQL DDL;
- unrelated implementation files;

as semantic authority unless a non-generated file is itself one of the exact
CanonicalArtifacts selected by the plan.

## Procedure

1. Confirm the manifest is current against recorded source digests when digests
   are present.
2. Confirm the plan section has `renderer: data-model-dbml` and an explicit
   `scope`. Treat the scope as persistence ownership identity, not
   automatically as a bounded-context id.
3. Load `spec/projection/dbml-data-model-v1.yaml`; stable DBML subset, naming,
   ordering, path, relationship and validation policy belong to that profile.
4. Read only the selected CanonicalArtifacts. Project only explicitly accepted
   data-model semantics:
   - tables;
   - columns;
   - primary keys;
   - foreign keys;
   - unique constraints;
   - nullability;
   - supported basic data types;
   - explicit relationships;
   - enums only when explicit in canonical data design.
5. Preserve the canonical ownership/scope boundary. Multiple plan sections may
   invoke this same renderer for different scopes.
6. Do not invent physical details absent from the selected canonical sources,
   including indexes, varchar lengths, defaults, cascade behavior,
   partitioning, generated columns or database-specific storage options.
   The profile permits an `indexes` block only as DBML syntax for an explicit
   composite primary-key or unique constraint; a bare/non-unique physical index
   is unsupported.
7. Emit the profile-required generated header and deterministic declaration
   order. Represent foreign keys using the profile relationship form.
8. Write the DBML to
   `docs/generated/data/<scope-id>/model.dbml`.
9. Generate deterministic provenance:

   ```sh
   python -m harness.workspace.dbml_projection provenance \
     --manifest <manifest.yaml> \
     --plan <plan.yaml> \
     --document <document-id> \
     --section <section-id> \
     --scope <scope-id> \
     --profile spec/projection/dbml-data-model-v1.yaml \
     --output docs/generated/data/<scope-id>/model.dbml.provenance.yaml
   ```

10. Validate source/provenance binding and the supported DBML subset:

   ```sh
   python -m harness.workspace.dbml_projection validate \
     --manifest <manifest.yaml> \
     --plan <plan.yaml> \
     --document <document-id> \
     --section <section-id> \
     --scope <scope-id> \
     --profile spec/projection/dbml-data-model-v1.yaml \
     --dbml docs/generated/data/<scope-id>/model.dbml \
     --provenance docs/generated/data/<scope-id>/model.dbml.provenance.yaml
   ```

## Stop conditions

Stop without inventing data semantics when:

- the selected section has no canonical sources;
- the scope is missing or invalid;
- table/column/key/relationship meaning is ambiguous or conflicting;
- a required representation would need a source outside the plan;
- a selected source is generated output;
- the manifest/source baseline is stale;
- accepted semantics require a DBML construct outside the v1 supported subset.

## Output contract

For `scope-id = <scope-id>` the generated outputs are:

- `docs/generated/data/<scope-id>/model.dbml`;
- `docs/generated/data/<scope-id>/model.dbml.provenance.yaml`.

They are disposable projections, never CanonicalArtifacts and never Capability
providers.

The provenance sidecar binds projection id, profile id/version, scope id,
manifest digest, selected CanonicalArtifact ids/paths/digests and both output
paths.

## Acceptance checks

- routing is authorized only from `human-documentation-projection`;
- scope identity in the request, plan, output path and provenance is identical;
- every semantic DBML declaration is supported by selected canonical sources;
- no generated file is used as source authority;
- duplicate tables/columns are rejected;
- PK/unique/FK declarations are structurally consistent;
- relationship endpoints exist;
- unsupported constructs and physical details are rejected;
- provenance exactly matches current manifest/plan/profile;
- `harness.workspace.dbml_projection validate` passes;
- generated outputs remain under `docs/generated/**`.
