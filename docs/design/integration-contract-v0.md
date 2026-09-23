# Harness Integration Contract v0

Status: canonical.

This document defines the repository-independent boundary between Harness and a project that uses it.

## Contract

Every integrated project presents the same two logical inputs to Harness:

1. an **Engineering Graph**: normative producer/consumer topology for engineering knowledge;
2. a **Core realization**: the accepted current knowledge state used to evaluate that topology.

Harness evaluates a selected Consumer and returns the derived target state (`COMPLETE`, `CREATE`, `WAIT`, `PENDING`) and may route actionable `CREATE` work through the agent skill registry.

The contract is logical, not a mandatory directory layout. Projects may persist either input or derive it at invocation time.

## Ownership boundary

The project owns product/domain/architecture truth, CanonicalArtifact semantic acceptance, project-specific CapabilityIds, applicability/coverage policy, and mapping existing project truth into the Harness inputs.

Harness owns Engineering Graph validation, producer/prerequisite rules, recursive Consumer closure, Core structural validation, target-state evaluation, and generic CREATE-to-skill routing by `knowledge_kind`.

Harness must not infer project semantics from arbitrary prose or require duplication of an existing canonical graph merely to integrate.

## Integration modes

There are two conforming modes. They differ only in how the same logical inputs are obtained.

### Direct declaration

Use when the project has no existing machine-readable owner for the relevant topology/state. A conventional layout is:

```text
.harness/
  engineering-graph.yaml
  core.yaml
```

The filenames are conventional, not Core entities. Persist only integration metadata with continuing project value.

### Adapter projection

Use when the project already has canonical machine-readable graphs, completeness policy, or other structured ownership metadata. A project-owned adapter derives an Engineering Graph and/or Core realization. Derived documents may remain ephemeral.

Adapter output must satisfy exactly the same Harness schemas and runtime semantics as direct declaration. Harness evaluation must contain no project-specific branches.

## Canonical invocation

A conforming integration performs the equivalent of:

```sh
python engineering_graph.py validate <engineering-graph>
python engineering_graph.py evaluate <engineering-graph> <consumer> <core-realization>
```

For agent execution, actionable CREATE results may additionally be routed with `agent_router.py`.

CI may generate either input before these calls. How Harness itself is obtained (checkout, package, image, or another versioned distribution) is deployment policy, not part of the semantic integration contract. CI must use an explicit Harness version rather than an unpinned moving branch.

## Derived Design Profiles

A Design Profile derived from an Engineering Graph is a runtime view. It is not a second normative policy owner and normally must not be persisted.

A separately authored Design Profile remains supported for consumers of `target_state.py`, but it is not required by the canonical Engineering Graph integration.

## Managed workspace

The managed knowledge workspace is optional and orthogonal. A project may use `.harness/knowledge/**`, `workspace.py`, and generated documentation when it wants Harness-managed typed semantic artifacts. This does not change the Engineering Graph/Core integration contract and must not force other projects to adopt managed knowledge.

## Project graph consistency

When a project already owns an authoritative canonical artifact graph, Harness may validate the projected artifact routing against the Engineering Graph capability topology.

For a complete selected projection:

- every selected canonical artifact has exactly one Authority binding;
- every provided CapabilityId agrees with its Engineering Graph producer Authority;
- cross-Authority artifact dependencies must not introduce an upstream Authority absent from capability prerequisites (hidden dependency);
- capability prerequisites must not claim an upstream Authority absent from the project artifact dependency graph (phantom dependency).

The comparison is performed at the Authority/capability frontier. Harness does not require one artifact edge for every capability edge and does not become the owner of the project graph.

## Authority execution context

Harness may derive an ephemeral bounded execution context for one Authority from the Engineering Graph and Core realization.

The context contains accepted upstream provider artifacts, same-Authority supporting closure, owned artifacts, public outputs, downstream consumers, blockers and allowed canonical read/write paths.

It is routing data, not a CanonicalArtifact, task, approval, stage or workflow state.

Projects may provide format-specific reference extractors, but Harness owns validation against the derived allowed-read boundary. Write-set validation must reject changes to canonical artifacts outside the selected Authority and must reject production while required inputs are blocked.

## CI boundary

Permanent project CI should verify the contract, not preserve pilot experiments. A normal integration check should obtain a pinned Harness version, derive inputs when adapters are used, validate the Engineering Graph and Core realization, evaluate selected Consumer(s), and enforce project-owned target assertions.

Large mutation scenarios used to prove Harness semantics belong in Harness acceptance tests. Consumer repositories should retain only assertions that express their own integration contract.

## Implementation design closure

For a selected implementation Consumer, coding authorization is a **derived conjunction** over existing contracts. It is not a new Core state, Stage, Gate or Readiness entity.

A project may claim its design/documentation closure complete only when all applicable assertions are true:

- the selected implementation Consumer target evaluates `COMPLETE`;
- Engineering Coverage for the same Consumer/Scope has `completion_ready=true`, no remaining work and no blocking Question frontier;
- subject/scope obligations are terminal for every accepted scope atom;
- every canonical artifact in the selected closure has passed its owning semantic/structural acceptance contract;
- accepted requirements have terminal verification dispositions, and every `TEST` disposition has an executable test contract when Test Design is applicable;
- architecture-driver closure, repository realization and other conditional preconditions required by the selected closure pass their own validators;
- project graph/realization diagnostics contain no blocking structural error;
- project-native deterministic validators that justify registered semantic claims pass.

The aggregate check is disposable derived evidence. It must not become another source of product/domain/architecture truth.

A project should expose one normal local/CI command that fails if any of the applicable assertions above fail. Separate workflows may retain redundant checks, but a green structural target alone must never be presented as full implementation-documentation closure.
## Portability invariant

Nutrition Management and NAPMS must be able to use the same Harness evaluator and result semantics. Nutrition may directly declare its Engineering Graph/Core realization. NAPMS may project them from its existing canonical graph and completeness/coverage policy. That difference is behind the project-owned adapter boundary.

If supporting either project requires project-specific logic inside Harness evaluation, the integration contract has failed and the abstraction must be reconsidered.

## Project engineering policy and coding boundary

Projects may represent selected engineering principles or design discipline as ordinary project-owned capabilities. Harness does not make SOLID, Clean Architecture, DDD, CQRS, REST or similar methods universal evaluator invariants.

When a project needs such discipline to constrain downstream design, the recommended pattern is:

```text
project engineering-policy capability
        ↓
applicable architecture/application/component production
        ↓
component-design capability
        ↓
implementation design / coding consumer
```

The policy artifact states concrete observable obligations; reusable artifact skills contain method knowledge for applying them. The Engineering Graph expresses when the accepted policy is a prerequisite.

Projects that intend to hand implementation to coding agents with little architecturally significant freedom should expose an accepted component-design capability covering responsibility, contract ownership, dependency direction, composition/mapping boundaries and explicit implementation freedoms.

This pattern requires no new Core entity and does not change Integration Contract v0.

## Verification, Test Design and implementation boundary

Projects that need executable test semantics before coding may model Test Design as an ordinary conditional capability. The recommended dependency direction is:

```text
accepted semantic/design capabilities
        ↓
verification-design capability
        ↓
test-design capability
        ↓
implementation-design / coding consumer
```

Verification Design owns what evidence must prove accepted engineering knowledge. Test Design, when independently valuable, refines that obligation into executable preconditions, operations, observable oracles, invariants and property/state-machine obligations. Concrete test code remains implementation evidence rather than becoming semantic authority merely because it is written first.

Harness does not make TDD universal. RED/GREEN/refactor or another test-first sequence is project engineering/process policy. Existing projects may project legacy artifacts into these capabilities without mechanically reordering files; a legacy artifact that mixes verification and implementation-readiness concerns may need semantic splitting during migration.

This pattern requires no new Core entity.

## Non-contract pilot material

Names such as `*-pilot`, experimental mutation workflows, research findings and branch-specific pinning are evidence used to establish this contract. They are not required parts of an integrated project's permanent repository.

## Versioning

This is Integration Contract v0. Breaking changes to the logical Engineering Graph/Core boundary require an explicit contract revision and consumer migration. Additive tooling or new distribution mechanisms do not by themselves change the semantic contract.


## Strict semantic admission and currentness

Structural Core/Target-State evaluation remains backward compatible for
migration and graph inspection. It is no longer sufficient by itself to claim
full implementation-documentation closure for routed engineering knowledge.

For every selected Consumer capability whose `knowledge_kind` is registered
to an active artifact skill:

- a provider must have ACCEPTED strict semantic-admission evidence;
- the admission must derive allowed source Authorities from the Engineering
  Graph production prerequisites rather than from a hand-maintained allowlist;
- referenced canonical source assertions must identify their source artifact and
  agree with its Authority ownership;
- candidate writes and canonical references must stay inside the derived
  Authority execution context;
- required judgement checks from the knowledge-kind semantic contract must be
  explicitly accepted;
- the provider must have a CURRENT capability lifecycle assertion whose
  acceptance identity matches the semantic admission;
- its recorded prerequisite acceptance identities must match the currently
  selected prerequisite identities.

Missing admission evidence is not interpreted as semantic rejection; it is
insufficient proof for strict closure. Upstream supersession makes direct
consumers STALE/REVALIDATE and prevents downstream CURRENT closure until their
owning Authorities revalidate.

The canonical strict check is `semantic_closure.py`. Projects may wrap it in
their own CI entrypoint, but a green structural target alone must not be
presented as full engineering closure.
