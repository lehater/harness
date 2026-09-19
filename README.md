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

Start with `docs/design/core-v0.md`.

There is no required repository-to-repository runtime binding. A target repository may declare the small Core model needed by its consumer scenario while keeping canonical semantic truth in its existing artifacts.

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

`docs/methodology/**` remains retained pre-Core material. Agent-facing skills explicitly referenced by `docs/design/agent-artifact-workbench-v0.md` are part of the current agent operating layer above Core; they do not extend Core entities.
