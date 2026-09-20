# Lifecycle-aware evaluation validation: Nutrition Management

Status: experiment result against current canonical Nutrition Management Harness graph.

## Inputs

Validated against the current project-owned:
- `.harness/engineering-graph.yaml`;
- `.harness/graph.yaml`.

Production code was not used as design evidence.

## Why Nutrition is a useful case

Nutrition has a non-trivial semantic graph:
- Product -> strategic domain -> multiple bounded semantic owners;
- convergence into Purchase Planning;
- Architecture;
- Application/Data/Interface;
- Engineering Policy/Component/Verification/Implementation Design;
- an independent BLS source/evidence/classification subgraph.

This exposes fan-out, fan-in and multiple downstream consumers, so stale propagation can be evaluated more realistically than a linear synthetic chain.

## Structural finding

The project already contains almost exactly the topology needed for lifecycle invalidation:
- Engineering Graph production `requires` declares semantic prerequisites by CapabilityId;
- Core graph materializes accepted providers and file-level dependencies.

The two graphs are broadly aligned for the implementation path, but they are not semantically identical and must not be conflated. Lifecycle invalidation must follow Engineering Graph `requires`, not `.harness/graph.yaml depends_on`.

## Scenario N1 — Product requirements superseded

Seed:
`nutrition-management.requirements` changes from revision R1 to R2.

Immediate stale frontier according to production contracts:
- domain boundaries;
- Nutrition Targeting domain;
- Food Knowledge domain;
- Market Catalog domain;
- Purchase Planning domain;
- Architecture-related downstream work cannot be current until its direct prerequisites are revalidated.

Expected lifecycle behavior:
1. Product R2 remains CURRENT as the newly accepted root.
2. Direct consumers accepted against R1 become REVALIDATE candidates.
3. Their downstream consumers remain PENDING rather than all being independently actionable.
4. Revalidation advances the frontier through the DAG.
5. IMPLEMENTATION cannot remain COMPLETE while required capabilities are stale.

This confirms the synthetic experiment's frontier semantics on a fan-out graph.

## Scenario N2 — Food Knowledge domain superseded

Seed:
`nutrition-management.domain.food-knowledge` F1 -> F2.

Direct semantic consumers include:
- nutrient evidence semantics;
- category taxonomy;
- BLS source identity/structure;
- Purchase Planning domain;
- gap-suggestion ranking;
- Architecture;
- Application Design;
- Verification Strategy.

This is an important result: one semantic capability has many independent consumers owned by different Authorities. A manually authored Question for each downstream artifact would duplicate topology and be easy to miss. Derived stale propagation is materially safer.

At the same time, all consumers must not be blindly rewritten. Each owner gets REVALIDATE only when its own prerequisites are current.

## Scenario N3 — BLS source identity superseded

Seed:
`nutrition-management.food-knowledge.bls-v4.source-identity` B1 -> B2.

Engineering Graph routes impact to:
- source code set;
- evidence semantics;
- errata policy;
- category-assignment policy;
- then normalization/category assignment/production package/verification according to their own prerequisites.

The current Core file graph has BLS evidence and errata artifacts depending on `BLS-V4-SOURCE-BASELINE`, which provides both source identity and source structure.

This demonstrates why lifecycle baseline must be CapabilityId-based rather than only artifact-revision-based.

If one artifact revision changes because **source structure** metadata changed while **source identity** semantics did not, consumers requiring only source identity should not necessarily become stale.

## P0 correction to the initial prototype

The prototype in PR #30 records:
`accepted_prerequisites: capability -> artifact revision`.

Nutrition demonstrates that this is too coarse when one CanonicalArtifact provides multiple independently consumed capabilities.

Required model is instead:
- **current capability revision identity**, not merely artifact revision;
- provider may expose one revision identity for several capabilities only when they intentionally share one semantic acceptance lifecycle;
- accepted prerequisite baseline records `CapabilityId -> capability revision identity`.

Artifact revision may remain useful provenance, but it is not sufficient as the semantic invalidation key.

## Scenario N4 — Architecture superseded

Seed:
`nutrition-management.architecture` A1 -> A2.

Direct production consumers include:
- Application Design;
- Data Design indirectly through Application;
- Engineering Policy;
- Implementation Stack;
- Verification Strategy.

Component Design depends on Engineering Policy, Application, Data, Interface and Implementation Stack. It should remain PENDING until those immediate prerequisites have independently revalidated. This prevents Component Design from being declared current merely because the architecture file changed.

## Scenario N5 — one source artifact provides two capabilities

`BLS-V4-SOURCE-BASELINE` currently provides:
- source identity;
- source structure.

Only source identity is used by several Engineering Graph production contracts. Source structure currently has no downstream production requirement in that graph.

Therefore artifact-level revision invalidation would create false-positive staleness.

This is decisive evidence against making CanonicalArtifact revision itself the only lifecycle identity.

## Required refinement

The lifecycle experiment should distinguish three identities:

1. **Artifact revision** — project/document provenance; optional and project-owned.
2. **Capability revision** — identity of accepted semantic knowledge exposed to consumers.
3. **Accepted prerequisite baseline** — `CapabilityId -> capability revision` used when accepting a produced capability.

A CanonicalArtifact may materialize several capabilities with different capability revisions/baselines.

Conceptual example:

```yaml
artifact: BLS-V4-SOURCE-BASELINE
artifact_revision: git:abc123
provides:
  - capability: ...source-identity
    revision: source-id:v4
    accepted_prerequisites:
      ...domain.food-knowledge: fk:7
  - capability: ...source-structure
    revision: source-structure:v4.1
    accepted_prerequisites:
      ...domain.food-knowledge: fk:7
```

This is conceptual only; it is not yet a Core schema proposal.

## Integration consequence

Current Core v0 `provides: [CapabilityId]` cannot attach independent lifecycle metadata to each provided capability.

Therefore if lifecycle validation proves necessary, either:
- Core v1 evolves `provides` into capability-provider records while preserving string shorthand compatibility; or
- a separate lifecycle projection overlays capability revision/baseline metadata keyed by artifact + CapabilityId.

The second option should be tested first because it minimizes Core change and allows mature repositories to project existing version/provenance systems.

## Validation result

The central lifecycle hypothesis is **confirmed**, but the first prototype representation is **not sufficient**.

Confirmed:
- stale propagation is needed;
- Engineering Graph production prerequisites are the correct propagation topology;
- REVALIDATE frontier is preferable to mass invalidation work;
- generic Lifecycle Authority remains unnecessary;
- explicit Authority-owned revalidation remains necessary.

Refuted/refined:
- artifact revision is not a sufficient semantic revision identity;
- baseline must be capability-granular.

## Next experiment

Revise PR #30 to use a separate lifecycle projection:

```yaml
version: 1
kind: harness-capability-lifecycle
providers:
  - artifact: ...
    capability: ...
    revision: ...
    accepted_prerequisites:
      capability: revision
```

Then repeat the BLS multi-capability scenario and the Architecture fan-out scenario. Only after that should NAPMS be used as the second independent project validation.
