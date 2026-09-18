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

Stage/Phase, Role/Person/Team, Task/Change, Workflow/Status machine, Gate/Approval, Readiness, Handoff, maturity/scoring, task capsules and a universal semantic DSL are outside Core v0. They require a demonstrated consumer failure and an acceptance test before any Core extension.

The older `docs/methodology/**` and `skills/**` content is retained pre-Core material and does not define Core v0.
