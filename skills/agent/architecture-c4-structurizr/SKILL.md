---
name: architecture-c4-structurizr
description: "Generate a source-bounded C4 architecture projection as Structurizr DSL from one Human Projection plan section without creating architecture semantics."
---

# Architecture C4 Structurizr Projection

Status: canonical v1 slice.

## Trigger

Use only when the public `human-documentation-projection` operation has a
compiled plan section whose `renderer` is
`architecture-c4-structurizr`, and the coordinator resolves this internal
operation through `harness.application.skill_router` with
`invoked_by=human-documentation-projection`.

## Inputs

- current Human Projection manifest;
- current Human Projection plan;
- exact document id and section id routed to this operation;
- canonical source artifacts listed in that plan section;
- `spec/projection/structurizr-c4-v1.yaml`;
- target repository root.

## Read boundary

Read only CanonicalArtifacts listed in the selected plan section's `sources`.

Resolve their paths from the current manifest. Do not search the repository for
additional architecture, implementation or diagram material.

Do not read:
- `docs/generated/**` as engineering authority;
- implementation/code unless it is itself one of the selected
  CanonicalArtifacts;
- unrelated architecture prose to fill a conventional C4 level;
- previous generated Structurizr output as semantic input.

## Procedure

1. Confirm the manifest is current against its recorded source digests when
   digests are present.
2. Load `spec/projection/structurizr-c4-v1.yaml`; do not duplicate or override
   its stable projection conventions inside the generated file.
3. Read the exact selected CanonicalArtifacts and extract only architecture
   structure they explicitly support:
   - architecture-relevant people/roles when explicit;
   - the target software system and explicit external software systems;
   - containers only when the selected canonical sources define that boundary;
   - components only when the selected sources explicitly define component
     structure;
   - relationships only when their endpoints, direction and meaning are
     supported by selected canonical sources.
4. Never infer containers from packages/processes, components from classes, or
   relationships from implementation merely because such a C4 view would look
   more complete.
5. Assign deterministic DSL identifiers. Prefer explicit stable canonical
   identifiers when they are valid Structurizr identifiers; otherwise derive a
   stable `a-zA-Z_0-9` identifier from the canonical element identity/name and
   reuse the same mapping throughout the file.
6. Generate one standalone Structurizr `workspace` using the profile:
   - `!identifiers hierarchical`;
   - `!impliedRelationships false`;
   - explicit `model` and `views` blocks;
   - an explicit-key System Context view;
   - a Container view when containers exist;
   - Component views only for containers whose components are explicitly
     supported;
   - `include *` and the profile's `autoLayout` direction in every generated
     C4 view;
   - no includes, scripts, plugins, workspace extension or local styles.
7. Write the DSL to the profile-owned generated path
   `docs/generated/architecture/workspace.dsl`.
8. Generate deterministic provenance from the current manifest/plan rather than
   hand-writing it:

   ```sh
   python -m harness.workspace.structurizr_projection provenance \
     --manifest <manifest.yaml> \
     --plan <plan.yaml> \
     --document <document-id> \
     --section <section-id> \
     --profile spec/projection/structurizr-c4-v1.yaml \
     --output docs/generated/architecture/workspace.dsl.provenance.yaml
   ```

9. Validate source/provenance binding and the supported DSL subset:

   ```sh
   python -m harness.workspace.structurizr_projection validate \
     --manifest <manifest.yaml> \
     --plan <plan.yaml> \
     --document <document-id> \
     --section <section-id> \
     --profile spec/projection/structurizr-c4-v1.yaml \
     --dsl docs/generated/architecture/workspace.dsl \
     --provenance docs/generated/architecture/workspace.dsl.provenance.yaml
   ```

10. When a pinned Structurizr parser/validator is available in the target
    execution environment, run it as an additional syntax check. The Harness
    slice does not download or silently select an external Structurizr runtime.

## Stop conditions

Stop this projection without inventing architecture when:

- the selected plan section has no canonical sources;
- a required element boundary or relationship is ambiguous/conflicting;
- a requested Container or Component view would require reading sources outside
  the plan;
- the manifest/source baseline is stale;
- the output cannot satisfy the profile without introducing unsupported
  architecture semantics.

A projection failure is not a Core Question unless the underlying accepted
architecture itself contains a genuine unresolved semantic Question owned by an
Authority.

## Output contract

Generated outputs are:

- `docs/generated/architecture/workspace.dsl`;
- `docs/generated/architecture/workspace.dsl.provenance.yaml`.

They are disposable projections, never CanonicalArtifacts and never Capability
providers. Deleting them must not change target state.

The provenance sidecar binds the output to the projection operation, profile,
manifest digest, selected CanonicalArtifact ids/paths/digests, and output paths.

## Acceptance checks

- the operation was routed as an authorized internal Consumer operation;
- every semantic C4 element/relationship is supported by selected canonical
  sources;
- no generated document is used as semantic input;
- implied relationships are disabled;
- view keys are explicit and stable;
- Container/Component views appear only when corresponding model levels exist;
- every generated C4 view uses the profile layout and `include *`;
- forbidden executable/import directives are absent;
- provenance exactly matches the current manifest/plan/profile;
- `harness.workspace.structurizr_projection validate` passes;
- generated outputs remain under `docs/generated/**`.
