# Harness Engineering Graph v0

Status: experimental, branch-only.

This model formalizes the producer/consumer idea that originally motivated Harness.

Harness Core remains the accepted **state of engineering knowledge**:

- Authority ownership;
- CanonicalArtifact providers;
- CapabilityIds;
- artifact dependencies;
- unresolved Questions and blocking.

The Engineering Graph defines the **normative production topology** above that state:

- which Authority is allowed to produce each engineering capability;
- which capabilities an Authority requires before it can responsibly produce its own knowledge;
- which capabilities a terminal consumer requires;
- how a target consumer expands recursively into an upstream engineering-knowledge closure.

It is a graph of engineering responsibility, not a phase/stage workflow.

## Entities

### Authority

An Authority is one atomic boundary of engineering decision ownership.

Each Authority declares:

- `responsibility` — the coherent class of decisions it owns;
- `boundary.semantic_cohesion` — why the decisions belong together;
- `boundary.independent_change` — why this knowledge can change independently of neighbouring Authorities;
- `boundary.public_contract` — what the Authority consumes and exposes to other Authorities;
- `requires` — capabilities that must be accepted before this Authority can form its outputs;
- `produces` — capabilities for which this Authority is the unique semantic producer.

The three boundary statements are the structural atomicity test. Harness can require them to exist but cannot mechanically prove their semantic truth.

### Capability

A CapabilityId names accepted engineering knowledge, not a file and not a task.

Exactly one Authority in one Engineering Graph may declare a CapabilityId in `produces`.

A CanonicalArtifact in Core materializes an accepted capability by listing the same CapabilityId in `provides`.

The Engineering Graph therefore knows the producer even before any provider artifact exists. This removes the need to repeat the expected Authority manually in a Design Profile.

### Requirement

A producer or terminal consumer may require a CapabilityId.

A requirement may carry `subject` metadata for the derived target view. In v0, provider resolution remains CapabilityId-based. If different subjects require independently provable coverage, the project must expose distinct subject-scoped CapabilityIds or a project-owned coverage projection that derives them.

Do not use one broad CapabilityId with different subjects and assume `subject` filters providers.

### Consumer

A Consumer is a terminal or externally selected target that consumes engineering knowledge but does not need to produce more engineering knowledge inside the selected graph.

`IMPLEMENTATION` is the primary example, but the model does not make it special. A project may target deployment preparation, an interface slice, verification design or another consumer.

## Document shape

```yaml
version: 1
kind: harness-engineering-graph
id: EXAMPLE
default_subject: EXAMPLE-PROJECT

authorities:
  - id: DISCOVERY
    responsibility: Own accepted problem evidence.
    boundary:
      semantic_cohesion: One class of knowledge about observed problems.
      independent_change: Evidence may change before requirements change.
      public_contract: Produces accepted problem evidence for Product Requirements.
    requires: []
    produces:
      - example.problem

  - id: PRODUCT-REQUIREMENTS
    responsibility: Own accepted product intent and acceptance semantics.
    boundary:
      semantic_cohesion: One class of product decisions.
      independent_change: Requirements may change without changing discovery evidence.
      public_contract: Consumes problem evidence and produces product requirements.
    requires:
      - capability: example.problem
    produces:
      - example.requirements

consumers:
  - id: IMPLEMENTATION
    purpose: Build the accepted product without inventing design decisions.
    requires:
      - capability: example.requirements
```

## Derived target

Selecting a consumer recursively expands its required capabilities.

For every required capability:

1. find its unique producer Authority;
2. add that capability to the target closure;
3. add the producer Authority's own input requirements;
4. repeat until root Authorities with no inputs are reached.

The result is a derived Design Profile. The profile is a view, not another policy owner.

```text
target consumer
      ↓
required capabilities
      ↓
producer Authorities
      ↓
their required capabilities
      ↓
recursive upstream closure
      ↓
derived Design Profile
      ↓
Core target-state evaluation
```

## Runtime semantics

Against a Core model:

- provider exists and is unblocked -> SATISFIED;
- provider missing, producer inputs satisfied, no capability Question -> CREATE at the declared producer Authority;
- provider or missing capability blocked by unresolved Question -> WAIT;
- producer inputs not yet satisfied -> PENDING;
- every derived expectation satisfied -> COMPLETE.

Question resolution changes canonical truth; it does not itself fabricate the requested capability.

## Questions and feedback

Questions are dynamic semantic feedback edges, not workflow tasks.

When an Authority cannot form an output without an unresolved upstream decision:

```text
consumer/producer attempts knowledge
        ↓
semantic gap discovered
        ↓
Question routed to deciding Authority
        ↓
affected knowledge WAIT
        ↓
Authority-owned canonical decision
        ↓
Question resolved
        ↓
graph reevaluated
```

If accepted canonical knowledge already decides the case and only code/tests lag, the Engineering Graph remains complete. Implementation state is not added to Core.

## Applicability

The Engineering Graph has no universal `N/A` state.

If project policy says an engineering requirement is not applicable only when accepted evidence proves that fact, the project translates the requirement to that evidence CapabilityId. The project-specific applicability rule remains owned by the project policy.

## Coverage and subjects

A consumer contract answers **which classes of engineering knowledge are needed**.

A project completeness policy may additionally answer **for which subjects those capabilities must exist**.

Both are legitimate inputs to graph construction/projection.

In v0, independent subject coverage is represented by distinct CapabilityIds, for example:

```text
engineering.domain.tactical-model@BC-RESOURCE-CATALOGUE
engineering.domain.tactical-model@BC-ACCESS-POLICY
```

The exact encoding is adapter/project policy. The important invariant is that two independently required subject instances must not collapse onto one broad provider key.

A future first-class parameterized Capability model requires additional consumer evidence before changing Core.

## Atomicity and graph shape

Stable Authority input dependencies must form a DAG.

Feedback is expressed through Questions and canonical repair, not by introducing static producer cycles.

If two groups of outputs need materially different upstream contracts, that is evidence that the Authority boundary may not be atomic and should be reviewed or split.

## Relationship to project artifacts

The Engineering Graph does not prescribe repository layout.

A simple project may store the graph directly under `.harness/**`.

A mature project may already own equivalent Authority/consumer/completeness policy. An adapter should project that policy into this model in memory rather than create a duplicate persistent graph.

CanonicalArtifact contents remain project-owned.

## Non-goals

Engineering Graph v0 does not model:

- project-management stages;
- tasks or tickets;
- people/agent roles;
- approvals or handoffs;
- implementation progress;
- maturity scores;
- one mandatory software methodology;
- automatic semantic correctness.

It models the dependency graph of engineering knowledge needed to reach a selected consumer.
