# Research — Human Documentation Projection v1

Status: research candidate.

## Question

How should Harness optimally generate a human-readable project documentation package from canonical engineering knowledge without creating a second source of truth, losing consumer scope, or forcing project-native artifacts into Harness-owned schemas?

## Prior work found

This research continues existing work rather than starting from zero.

### Harness: Project-native Human Projection v0

Commit `92e9cc37305c0709aefa0c0f6fcdab76e5f6db3e` introduced
`docs/design/project-native-human-projection-v0.md`.

Its central decisions remain correct:

- Human Projection is a view above Engineering Graph/Core.
- Generated output is disposable and non-canonical.
- Only accepted CanonicalArtifacts in the selected closure may supply engineering assertions.
- Project-native knowledge must not be copied into Harness-managed YAML merely for rendering.
- Every substantive generated section must retain source traceability.
- Questions/conflicts must remain visible rather than being silently resolved.
- Document taxonomy is presentation policy, not a Core concept.
- Promotion of generic renderer conventions was intentionally deferred until a second structurally different project existed.

That promotion criterion is now satisfied by NAPMS.

### Nutrition Management: semantic human projection

Commit `be5e2a128b535cf7041ca959d86596f2650a404b` added a human-readable design projection.

The generated set includes:

- `README.md`;
- `overview.md`;
- `domain-and-data.md`;
- `implementation-guide.md`;
- `verification-and-readiness.md`;
- later `frontend-guide.md`.

Strengths:

- high human readability;
- topic-oriented rather than file-oriented organization;
- one human section can synthesize several canonical Authorities/artifacts;
- every section names canonical source documents;
- design distinctions and coding boundaries are summarized in domain language;
- implementation/readiness is explained from the selected Harness Consumer rather than from one status file.

Weaknesses:

- the project does not contain a generic deterministic compiler that can recreate these narrative documents from arbitrary project-native canonical files;
- the semantic summaries are effectively agent-authored projections;
- source references are human-readable but not represented as a machine-verifiable claim/section manifest;
- byte-for-byte deterministic regeneration is not a realistic invariant for agent-authored prose;
- freshness can therefore only be guaranteed by an explicit regeneration/verification workflow.

Nutrition proves that useful documentation is not a concatenation of canonical source files.

### NAPMS: exact consumer documentation package

NAPMS introduced `tools/generate_human_context_package.py` during the engineering-knowledge pilot and retained a migrated version after moving to the canonical Harness runtime.

It derives:

- the selected Consumer closure;
- resolved provider artifacts;
- canonical artifact dependency closure;
- a machine-readable manifest;
- source snapshots;
- human folders grouped by artifact kind;
- a generated README.

Strengths:

- deterministic source selection;
- exact Consumer scope;
- no accidental inclusion of downstream/unrelated knowledge;
- manifest records exact canonical source set;
- source snapshot is useful for review/export/offline handoff;
- deletion of package has no semantic effect.

Weaknesses:

- human documents mostly wrap raw YAML/DSL in Markdown;
- grouping by source artifact kind is better navigation but not actual documentation synthesis;
- one canonical artifact becomes one generated file, so cross-Authority topics remain fragmented;
- the `SECTIONS` mapping is project-local renderer configuration;
- the package does not produce a concise architectural/product/implementation narrative comparable to Nutrition.

NAPMS proves that source selection and package reproducibility can be deterministic.

### Harness managed workspace

`workspace.py` already provides typed deterministic rendering for Harness-managed schemas such as:

- `product-requirements/v1`;
- `domain-model/v1`;
- `verification-plan/v1`;
- `test-design/v1`.

Strengths:

- typed validation before rendering;
- exact deterministic output;
- schema-specific renderers;
- traceability checks for managed requirements/verification/test design.

Weakness:

- it applies only when Harness owns typed managed knowledge;
- it should not force existing project-native canonical knowledge into duplicate schemas;
- it renders artifact-by-artifact rather than composing arbitrary project-wide topic documents.

This remains one rendering backend, not the universal project documentation architecture.

## Synthesis

The previous experiments solved three different subproblems:

```
Harness managed workspace
  = deterministic rendering of typed Harness-owned knowledge

NAPMS human context package
  = deterministic Consumer closure + provenance/package materialization

Nutrition human projection
  = useful cross-artifact human narrative
```

Trying to collapse these into one renderer would either:

- reduce human output to source wrapping;
- force duplicate semantic schemas;
- or allow an agent/LLM to decide which project knowledge belongs in a package.

The correct architecture separates source selection from presentation and from narrative synthesis.

## Proposed Human Documentation Projection v1

### Layer 1 — Projection Scope Compiler

Harness should own a deterministic generic compiler that accepts:

- Engineering Graph;
- Core realization/project projection;
- selected Consumer;
- optional selected CapabilityIds or presentation scope;
- optional project canonical graph adapter.

It outputs an ephemeral or persisted generated `projection-manifest.yaml`.

The compiler owns no engineering semantics. It derives:

- Harness version / baseline identity;
- selected Consumer;
- target state;
- required capability closure;
- resolved provider artifacts;
- canonical same-source dependency closure when available;
- unresolved Questions/blockers;
- source paths;
- source artifact kinds;
- Authority ownership;
- capabilities provided;
- optional project source revision/digests;
- document/presentation recipe identity.

This is the genericized strong part of NAPMS.

### Layer 2 — Presentation Recipe

A project may persist a small presentation recipe controlling only navigation/assembly.

Example conceptual shape:

```yaml
version: 1
kind: harness-human-projection
id: implementation-docs
consumer: BACKEND-IMPLEMENTATION
output: docs-generated/implementation

documents:
  - id: overview
    title: System Overview
    purpose: Explain product boundary, system shape and primary flow.
    sections:
      - id: product-boundary
        sources:
          capabilities: [example.requirements]
      - id: system-shape
        sources:
          knowledge_kinds: [system-architecture]
      - id: primary-flow
        sources:
          knowledge_kinds: [application-design, user-journey-design]

  - id: implementation
    title: Implementation Guide
    sections:
      - id: coding-boundary
        sources:
          knowledge_kinds: [component-design, implementation-design]
```

The recipe MAY select sources by:

- CapabilityId;
- knowledge_kind;
- Authority;
- explicit canonical artifact id;
- selected Consumer closure.

It MUST NOT contain domain/design assertions merely to make the generated prose work.

It is presentation/navigation policy, not a Capability provider.

### Layer 3 — Rendering backends

A generated document section may use one of three backends.

#### A. Typed renderer

For Harness-managed typed knowledge.

Reuse existing `workspace.py` renderers where possible.

Properties:

- deterministic;
- schema-aware;
- lossless enough for its schema;
- machine-verifiable.

#### B. Source-native renderer

For project-native artifacts whose content is already reasonably readable.

Examples:

- Markdown source;
- OpenAPI summary/index;
- Structurizr diagram/link/index;
- YAML table/index where structured extraction is defined by a project adapter.

This renderer restructures/links content without semantic summarization.

Properties:

- deterministic;
- adapter-defined extraction;
- never invents engineering claims.

#### C. Narrative projection

For topic-oriented human documents such as Nutrition's overview and implementation guide.

This is agent-authored/generated prose, not a deterministic parser transformation.

The agent receives only:

- projection manifest;
- exact allowed canonical sources for the section;
- section purpose/audience;
- unresolved Questions/blockers;
- projection skill rules.

The agent MUST produce a section with explicit machine-readable provenance metadata before/alongside rendering.

Conceptual intermediate representation:

```yaml
document: overview
section: system-shape
claims:
  - text: The MVP is one local modular monolith.
    sources:
      - artifact: TARGET-ARCHITECTURE
        path: docs/architecture/target-architecture.md
  - text: No bounded context is a network service.
    sources:
      - artifact: TARGET-ARCHITECTURE
        path: docs/architecture/target-architecture.md
```

The Markdown is rendered from this accepted projection representation.

This does **not** make each claim canonical engineering truth. The claim map is generated projection evidence proving where the prose came from.

## Why the intermediate claim/section representation matters

A free-form Markdown generator cannot be structurally verified.

A projection IR allows Harness to verify:

- every source artifact is inside the selected projection scope;
- every substantive narrative block has one or more source references;
- no source path is invented;
- unresolved Questions are represented where applicable;
- no generated document provides a Capability;
- deletion of the package leaves target state unchanged;
- a stale source baseline can be detected;
- one can regenerate Markdown without re-running semantic source selection.

The IR belongs under generated output, not canonical knowledge.

## Determinism

There are two different determinism requirements.

### Scope determinism — mandatory

For fixed:

- Harness version;
- project canonical baseline;
- Engineering Graph/Core realization;
- selected Consumer;
- presentation recipe;

the projection compiler MUST select the same source closure and produce the same semantic manifest.

This is a hard acceptance invariant.

### Prose determinism — not mandatory for narrative projection

Agent-generated prose need not be byte-for-byte stable.

Requiring exact text determinism would either force template-only low-quality docs or incorrectly turn one phrasing into semantic authority.

Instead narrative acceptance requires:

- same section contract;
- source-bounded claims;
- traceability;
- no contradictions with sources;
- no silent Question resolution;
- stable structural output;
- stale-baseline detection.

Typed/source-native renderers may still retain byte-level deterministic tests.

## Package structure

Recommended generic package:

```
docs-generated/<projection>/
├── README.md
├── manifest.yaml
├── projection-ir/
│   ├── overview.yaml
│   └── implementation.yaml
├── documents/
│   ├── overview.md
│   ├── architecture.md
│   ├── implementation.md
│   └── verification.md
├── sources/                 # optional snapshot/export mode
│   └── <canonical paths>
└── diagrams/                # optional copied/generated projection assets
```

Not every project must persist generated output in Git.

CI artifact publication is a valid mode.

## Package modes

### REVIEW

Human-readable docs + manifest + projection IR.

Good for repository review.

### HANDOFF

REVIEW plus canonical source snapshot and relevant generated diagrams.

Good for implementation handoff or external/offline review.

This generalizes the useful NAPMS package behavior.

### SITE

Same source manifest/IR rendered into a navigable static documentation site.

This is a later presentation backend and does not change projection semantics.

## Document taxonomy

Do not create one mandatory universal document list.

Instead Harness may ship reusable presentation profiles.

A software implementation profile could suggest:

- Overview / Product Boundary;
- Domain & Application;
- Architecture & Interfaces;
- Data & Security / Operability where applicable;
- Human Interface for frontend Consumers;
- Component & Implementation Guide;
- Verification / Test / Readiness;
- Open Questions / Reopening Conditions.

Only sections with accepted applicable knowledge are emitted.

The project may rename/regroup them.

## Consumer-specific documentation

Documentation must be generated for a selected Consumer or explicit capability scope.

Examples:

- BACKEND-IMPLEMENTATION package;
- FRONTEND-IMPLEMENTATION package;
- VERIFICATION package;
- full project design overview.

Do not generate a single undifferentiated repository dump and call it implementation documentation.

This follows both NAPMS and the original Human Projection v0 contract.

## Questions, missing knowledge and partial readiness

Projection must not require COMPLETE target state.

When selected target is incomplete:

- manifest records target state;
- unresolved Questions are listed;
- missing CREATE/PENDING/WAIT capabilities are visible;
- narrative must not fill those gaps;
- affected sections may be marked incomplete.

This makes the projection useful during design, not only at the end.

## Source conflict handling

If accepted canonical sources conflict materially:

- compiler exposes both sources;
- narrative renderer must not choose a winner;
- generated document marks the section conflicted/incomplete;
- normal Harness Question/Authority routing remains the mechanism for resolution.

Human Projection is not a conflict-resolution Authority.

## Staleness and regeneration

A generated package should record a source baseline.

Preferred baseline:

- project commit SHA when available;
- Harness version SHA;
- selected Consumer;
- hashes/digests of source artifacts or a deterministic manifest digest.

A validation command can then report:

- CURRENT;
- STALE_SOURCE;
- STALE_RECIPE;
- INVALID_TRACEABILITY.

Do not encode these as Core target states.

They are projection health only.

## Validation contract

A generic `human_projection.py validate` should verify at least:

1. selected Consumer exists;
2. manifest closure matches current Harness evaluation;
3. every projected source belongs to that closure/scope;
4. source paths exist;
5. every narrative section has allowed source references;
6. generated claim/section source refs resolve;
7. no projection file is registered as a provider;
8. unresolved Questions are preserved;
9. generated output is outside canonical knowledge roots;
10. package baseline/pin matches current inputs when freshness checking is requested.

For typed renderers, existing schema/render acceptance remains applicable.

## Agent skill

Add a reusable `human-documentation-projection` agent skill.

Its job is not to design the system.

It:

1. receives a projection manifest and section recipe;
2. reads only section-allowed canonical sources;
3. produces projection IR claims/blocks with source refs;
4. preserves ambiguity/questions;
5. renders concise audience-appropriate prose;
6. validates the projection package.

A semantic assertion with no allowed source is rejected rather than invented.

## Relationship to existing mechanisms

### Managed workspace

Keep it.

Its typed renderers become one backend.

Do not migrate project-native knowledge into managed schemas for documentation purposes.

### Authority execution context

Separate concern.

Authority context bounds **authoring/change** inputs and writes.

Human projection bounds **reading/presentation** through Consumer closure.

Do not reuse Authority write context as documentation scope.

### Engineering Graph / Core

No new Core entity is required.

Human projection consumes these models but does not alter them.

### Canonical graph adapter

Use it when the project owns artifact dependency structure, as NAPMS does.

Nutrition-like projects without the same graph shape can still project from Core/Engineering Graph providers.

## Evaluation against current projects

### Nutrition

Expected projection recipe:

- Overview;
- Domain & Data;
- Implementation Guide;
- Verification & Readiness;
- Frontend Guide.

The current human docs provide a strong target-quality fixture.

A v1 implementation should be able to reproduce the same *information architecture and source discipline* without requiring identical prose.

The current hand-authored generated docs become acceptance examples, not canonical semantic inputs.

### NAPMS

Expected package:

- exact BACKEND-IMPLEMENTATION closure;
- Overview;
- Domain/Application;
- Architecture/Security/Interfaces/Data;
- Implementation;
- Verification/Operability;
- manifest and optional source snapshot.

The current NAPMS package supplies the deterministic closure/manifest fixture.

A v1 implementation should improve the `human/` layer from raw YAML wrappers into topic documents while preserving the same exact source set.

Frontend documentation should be generated separately from the FRONTEND-IMPLEMENTATION Consumer and visibly remain incomplete until its missing capabilities are accepted.

### Harness itself

Harness managed workspace remains the typed-renderer fixture.

Harness can also use a project-native projection of its own design docs later as a third dogfood case.

## What should be canonicalized after prototype validation

Likely canonical:

- Project-native Human Projection v1 contract replacing experimental v0;
- deterministic projection manifest/compiler;
- presentation recipe schema;
- projection IR/provenance contract;
- generic validation rules;
- reusable human-documentation-projection skill;
- typed/source-native/narrative backend distinction;
- REVIEW/HANDOFF package modes.

Do not canonicalize yet:

- one fixed software-document taxonomy;
- one mandatory Markdown template;
- project-specific artifact-kind maps;
- an LLM-specific prompt format;
- generated prose itself;
- source snapshots as mandatory repository files;
- a new Documentation Authority or Core entity.

## Prototype sequence

1. Implement projection-manifest compiler in Harness.
2. Implement presentation recipe + validator.
3. Add source-native rendering and reuse managed typed renderers.
4. Add projection IR contract for narrative sections.
5. Add agent skill for source-bounded narrative generation.
6. Reproduce Nutrition information architecture as acceptance fixture.
7. Replace NAPMS project-local package compiler with the generic Harness compiler plus a small NAPMS presentation recipe.
8. Compare usefulness, closure exactness and traceability across both projects.
9. Only then promote v1 contract from research/experimental to canonical.

## Decision

The original Human Projection v0 research was directionally correct and deliberately unfinished.

Nutrition supplied the first proof of useful cross-artifact human documentation.
NAPMS now supplies the second structurally different proof of deterministic Consumer-scoped package materialization.

The optimal v1 is therefore not a universal document generator. It is a generic **source-bounded documentation projection system**:

```
Engineering Graph + Core/project graph + Consumer
        ↓
deterministic projection manifest
        ↓
project presentation recipe
        ↓
typed/source-native/narrative section projection
        ↓
projection IR with source traceability
        ↓
human-readable package
```

This preserves one canonical source of engineering truth while allowing high-quality human documentation and reproducible implementation handoff.
