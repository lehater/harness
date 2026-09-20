# Harness managed knowledge workspace v0

The managed workspace is an opt-in target-project layout for projects that want Harness to own canonical machine-readable design knowledge and derive human-readable documentation from it.

It is not required for ordinary Core consumers and does not create a repository-to-repository binding.

## Layout

```text
project/
├── .harness/
│   ├── graph.yaml
│   ├── profile.yaml
│   ├── config.yaml            # optional
│   └── knowledge/
│       └── application-domain.yaml
└── docs/
    └── generated/
        └── application-domain.md
```

Responsibilities are intentionally separated:

- `.harness/graph.yaml` — ordinary Harness Core model; canonical ownership, capability providers and dependency topology;
- `.harness/profile.yaml` — ordinary Design Profile; canonical target state for the selected design scope;
- `.harness/knowledge/**` — canonical machine-readable semantic content for Harness-managed artifacts;
- `docs/generated/**` — disposable human-readable projections. Never edit them as sources of truth.

The default generated output is `docs/generated`. A project may override it:

```yaml
version: 1
kind: harness-workspace-config
generated:
  output: documentation/generated
```

## Knowledge artifact envelope

A managed canonical artifact references exactly one Core `CanonicalArtifact` by id:

```yaml
version: 1
kind: harness-knowledge-artifact
artifact: APPLICATION-DOMAIN
schema: domain-model/v1
title: Application Domain Model
content:
  purpose: Define the semantic meaning of an Application.
  terms:
    - term: Application
      meaning: A user-managed definition of one software application.
  concepts:
    - name: Application
      identity: Stable application identifier.
      responsibilities:
        - Own its component membership.
  invariants:
    - id: APPLICATION-COMPONENT-UNIQUE
      statement: A component may occur at most once inside one Application.
```

Ownership, provided capabilities and dependencies are not repeated here. They remain canonical in `.harness/graph.yaml`.

## Typed schemas, not a universal DSL

The envelope is generic; semantic content is not.

Each `schema` has a dedicated validator and renderer. Managed knowledge now includes `domain-model/v1`, `product-requirements/v1`, `verification-plan/v1` and `test-design/v1`. Additional schemas such as architecture must likewise be added from demonstrated project needs.

A schema controls:

- the minimum structured content required before the artifact is accepted;
- how that content is rendered for humans;
- schema-specific validation rules.

This prevents a generic bag of claims from becoming a weak universal engineering language.

## Canonical requirements and verification traceability

`product-requirements/v1` is the canonical Product Requirements representation for Harness-managed requirements.

Each normative requirement has:
- a stable unique `REQ-*` id;
- one independently reviewable statement;
- `ACCEPTED` or `RETIRED` status;
- non-empty `source_refs`;
- optional rationale.

Git history remains the revision mechanism. Requirement IDs are not document positions and must not be silently reused for materially different semantics.

`verification-plan/v1` gives every verification check:
- a stable check id;
- non-empty `verifies` references to accepted requirements/design obligations;
- one verification method: `TEST`, `ANALYSIS`, `INSPECTION` or `DEMONSTRATION`;
- concrete evidence.

Workspace validation enforces that every `ACCEPTED` managed Product Requirement has at least one verification disposition. A requirement therefore cannot disappear between canonical requirements and verification while the managed workspace remains valid.

For checks whose method is `TEST`, `test-design/v1` must contain at least one executable test contract referencing that verification check. Test Design owns precondition, controlled operation and observable oracle; it does not restate or invent the Product Requirement.

The trace is therefore:

```text
product-requirements/v1
  REQ-*
      ↓ verifies
verification-plan/v1
  VER-* + method
      ↓ when method=TEST
test-design/v1
  TEST-* + verification_refs
```

Other accepted design obligations may also be referenced by Verification checks. Not every engineering test needs to originate in Product Requirements, but every managed accepted Product Requirement must have an explicit verification disposition.

Generated Markdown for Requirements, Verification Strategy and Test Design is disposable review projection only.

## Candidate validation, acceptance and completeness

For a managed artifact, existence of a file is insufficient.

An agent may validate a candidate before making it canonical:

```sh
python workspace.py validate-artifact candidate.yaml
```

This checks only the typed artifact structure. It does **not** register a provider or establish semantic correctness.

After the agent applies the semantic acceptance contract in `docs/design/agent-artifact-workbench-v0.md`, the accepted artifact is moved under `.harness/knowledge/**` and registered in the Core graph with its Authority, dependencies and provided capability.

A registered managed knowledge document must pass its schema validator before the workspace is valid.

The pipeline is therefore:

```text
Design Profile expectation
        ↓
Core provider topology
        ↓
Harness knowledge artifact
        ↓
schema validation
        ↓
target-state evaluation
        ↓
human-readable projection
```

`COMPLETE` remains the Design Profile result. In managed mode it is reported only after every Harness-managed knowledge document has passed schema validation and every declared expectation prerequisite has been satisfied. Semantic acceptance remains an agent responsibility at the graph-registration boundary.

This still does not prove that a stakeholder decision is factually correct. Unknown or conflicting semantics must remain represented as Core `Question` blockers rather than invented content.

## Existing projects

A project can mix managed and existing canonical artifacts.

- existing project-owned documents may remain normal Core artifact paths;
- only artifacts whose paths are under `.harness/knowledge/` are managed and rendered by this workspace;
- migration may therefore proceed incrementally instead of copying all existing documentation into Harness.

## Generated documentation

Generated Markdown is a view, not canonical state:

```text
.harness/graph.yaml
        +
.harness/knowledge/**
        ↓
renderer
        ↓
docs/generated/**
```

Deleting generated files loses no accepted knowledge; rerunning the renderer restores them.

Current projections include Product Requirements, Domain Model, Verification Strategy and Test Design. Coverage is validated from canonical managed artifacts before rendering. Additional industry-recognizable document types should be introduced one at a time from demonstrated consumer needs.
