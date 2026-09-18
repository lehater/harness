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

## Consumer contracts above Core

When a downstream consumer needs a specific, self-contained set of engineering knowledge, `consumers/contract.py` can evaluate a consumer-specific contract on top of an ordinary Core v0 model.

A requirement names:

- the required `CapabilityId`;
- the Authority expected to own that capability;
- an opaque target representation requested by the consumer;
- optionally, a capability that is canonical evidence for `NOT_APPLICABLE`.

Evaluation yields only `PROVIDED`, `NOT_APPLICABLE`, or `DESIGN_GAP`, plus unresolved blocking Questions affecting the selected providers. A missing requirement yields a Core-compatible Question draft addressed to the expected Authority. The final answer still belongs in that Authority's canonical artifact.

`project_package` runs only for a satisfied contract. It emits a projection plan containing source artifact IDs, source paths and requested representations. It does not render, copy or reinterpret target semantics.

This layer is intentionally not Harness Core. See `docs/design/consumer-contract-v0.md`.

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

The older `docs/methodology/**` and `skills/**` content is retained pre-Core material and does not define Core v0.
