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

There is no required project binding, manifest, pin, submodule or runtime coupling. A target repository may declare the small Core model needed by its consumer scenario while keeping canonical semantic truth in its existing artifacts.

Stage/Phase, Role/Person/Team, Task/Change, Workflow/Status machine, Gate/Approval, Readiness, Handoff, maturity/scoring, task capsules and a universal semantic DSL are outside Core v0. They require a demonstrated consumer failure and an acceptance test before any Core extension.

The older `docs/methodology/**` and `skills/**` content is retained pre-Core material and does not define Core v0.
