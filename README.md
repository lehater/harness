# Harness

Repository-independent Core for engineering-knowledge ownership.

Harness Core v0 models only:

- `Authority`;
- `CanonicalArtifact`;
- `Question`;
- `CapabilityId`;
- canonical-artifact dependencies.

From that declared structure it derives `affected`, unresolved `questions`, capability `resolve` / `owner`, `blocked`, and `resolve-question`.

Target repositories remain the source of product/domain/architecture truth. Harness validates ownership, references, dependencies and capability ownership; it does not copy or interpret arbitrary engineering semantics.

Start with `docs/design/core-v0.md`. For project integration, use `docs/design/integration-contract-v0.md`.

There is no required repository-to-repository runtime binding. A target repository may declare the small Core model needed by its consumer scenario while keeping canonical semantic truth in its existing artifacts.

## Engineering Graph v0

Engineering Graph v0 is the canonical normative producer/consumer layer above Core.

Core remains the accepted knowledge state. The Engineering Graph declares:

- atomic engineering Authorities;
- each Authority's required upstream capabilities;
- the capabilities each Authority is uniquely allowed to produce;
- terminal consumers such as `IMPLEMENTATION`.

Selecting a consumer recursively derives the Design Profile needed to satisfy that consumer. The profile is therefore a view of producer/consumer policy rather than a second manually maintained policy list.

```sh
python engineering_graph.py validate /path/to/engineering-graph.yaml
python engineering_graph.py profile /path/to/engineering-graph.yaml IMPLEMENTATION
python engineering_graph.py evaluate /path/to/engineering-graph.yaml IMPLEMENTATION /path/to/core-model.yaml
```

See `docs/design/engineering-graph-v0.md`. The repository integration boundary is defined by `docs/design/integration-contract-v0.md` and has been validated against Nutrition Management, NAPMS, and the greenfield acceptance project.

## User-facing/frontend design

User-facing applications use the same Engineering Graph and Core semantics as backend work. Harness adds reusable `user-journey-design` and `human-interface-design` production procedures while retaining Application Design, Interface Design, System Architecture, Security, Component, Verification, Test and Implementation ownership boundaries.

See `docs/design/frontend-design-v0.md` and the executable `examples/user-facing-application/**` fixture.

## Design target state

A Design Profile can declare the engineering knowledge required for a selected scope as stable expectations of `subject + CapabilityId + Authority`.

`target_state.py` evaluates that target against a Core model:

- missing canonical provider -> `CREATE`;
- provider blocked by unresolved Questions -> `WAIT`;
- every expectation has an unblocked provider under the expected Authority -> `COMPLETE`.

This is structural design completeness, not semantic interpretation of arbitrary document prose. Expectations may declare prerequisite expectations; downstream knowledge remains `PENDING` until those prerequisites are satisfied. See `docs/design/target-state-v0.md`.

## Managed knowledge workspace

Projects that want Harness to own machine-readable design knowledge may opt into a local `.harness/` workspace:

```text
.harness/
  graph.yaml
  profile.yaml
  config.yaml
  knowledge/**
docs/generated/**
```

`.harness/graph.yaml` owns topology, `.harness/knowledge/**` owns typed canonical content, and `docs/generated/**` contains disposable human-readable projections.

`workspace.py validate PROJECT` validates the workspace. `workspace.py validate-artifact CANDIDATE.yaml` validates a candidate before acceptance. `workspace.py render PROJECT` validates accepted managed knowledge and regenerates documentation.

Current typed knowledge schemas are `domain-model/v1` and the consumer-piloted `verification-plan/v1`. Additional schemas are intentionally added one at a time instead of introducing a universal semantic DSL. See `docs/design/managed-knowledge-v0.md`.

## Agent-driven use

Harness is currently designed to be operated by an engineering agent rather than to autonomously design a repository.

The reusable agent loop is documented in `docs/design/agent-artifact-workbench-v0.md`. It uses:

- `skills/agent/design-profile/SKILL.md` to define/review the target knowledge;
- `skills/agent/bootstrap-existing-project/SKILL.md` to reuse existing canonical project truth;
- artifact-specific skills under `skills/artifacts/**` for actionable `CREATE` expectations; skills may produce typed `.harness/knowledge` or project-native canonical artifacts when that is the natural target format;
- starter profiles under `profiles/**` as adaptable checklists, not universal completeness proofs.

Schema validation does not itself accept semantics. The agent registers `provides` only after the artifact passes semantic acceptance.

## Existing canonical graphs

When a target repository already owns artifact paths and dependency routing in a canonical graph, do not copy that graph into Harness metadata.

`adapters/canonical_graph.py` can project a selected part of such a graph into Core v0. The consumer projection declares only Harness-specific metadata:

```yaml
version: 1
kind: harness-canonical-graph-projection
source_graph: canonical-graph.yaml

authorities:
  - id: DOMAIN
  - id: ARCHITECTURE

bindings:
  - artifact: DOMAIN-MODEL
    authority: DOMAIN
    provides: [example.domain-semantics]
  - artifact: PERSISTENCE
    authority: ARCHITECTURE
    provides: [example.persistence-design]

questions: []
```

`artifact` references an existing source-graph node. Artifact `path` and `depends_on` are always derived from that source graph. When unselected routing nodes lie between two selected artifacts, the adapter contracts that path while preserving dependency reachability.

Example invocation:

```sh
python adapters/canonical_graph.py /path/to/project/docs/harness-core.yaml
```

The emitted YAML is an ordinary Core v0 model and can be passed to `harness.py`. Projection metadata is integration metadata, not a second source of product/domain/architecture truth.

## Projects without a canonical graph

Do not build a generic parser that tries to infer engineering ownership and dependencies from arbitrary prose.

For a consumer scenario, declare the smallest direct Core model that names only the canonical artifacts needed for that scenario. `path` and `depends_on` may be declared directly because no other machine-readable routing owner exists.

The model may stay ephemeral. Persist it only when the target repository benefits from maintaining that integration metadata. Do not create a full-repository Harness inventory merely for completeness.

If the target repository later gains its own canonical graph, prefer projecting that graph instead of maintaining duplicated routing metadata.

Stage/Phase, Role/Person/Team, Task/Change, Workflow/Status machine, Gate/Approval, Readiness, Handoff, maturity/scoring, task capsules and a universal semantic DSL are outside Core v0. They require a demonstrated consumer failure and an acceptance test before any Core extension.

`skills/agent/**` and `skills/artifacts/**` are the active v0 agent operating layer above Core. Existing `skills/core/**`, `skills/ddd/**`, `skills/software-product/**` and `docs/methodology/**` are retained pre-Core material unless a future consumer-driven migration explicitly promotes them. Active agent skills do not extend Core entities.


## Graph Doctor

`graph_doctor.py` performs one non-destructive diagnostic pass over the Engineering Graph, Core/project realization, canonical files and project-graph alignment.

It aggregates stable findings with severity, owner, evidence and suggested human actions. Semantic auto-fix is intentionally not performed.

```sh
python graph_doctor.py .harness/engineering-graph.yaml \
  --core-model .harness/graph.yaml \
  --target IMPLEMENTATION \
  --source-root .

python graph_doctor.py .harness/engineering-graph.yaml \
  --core-model .harness/graph.yaml \
  --json
```

See `docs/design/graph-doctor-v1.md`.


## Human Documentation Projection

`human_projection.py` derives a deterministic, Consumer-scoped documentation
manifest from accepted Engineering Graph/Core knowledge, validates a
project-owned presentation recipe, and materializes source-bounded narrative
packages.

Generated documentation remains disposable and non-canonical. Narrative claims
must reference canonical artifacts allowed by the selected section; optional
evidence validation binds claims to excerpts from current canonical sources.

```sh
python human_projection.py compile \
  .harness/engineering-graph.yaml \
  .harness/graph.yaml \
  FRONTEND-IMPLEMENTATION \
  --recipe docs/human-projection/frontend.yaml \
  --source-root . \
  --output-manifest /tmp/manifest.yaml \
  --output-plan /tmp/plan.yaml
```

See `docs/design/human-documentation-projection-v1.md` and
`skills/agent/human-documentation-projection/SKILL.md`.
