# Harness Engineering Graph v0

Status: canonical v0.

This model formalizes the producer/consumer idea that originally motivated Harness. Its repository boundary is defined by `integration-contract-v0.md`.

Harness Core remains the accepted **state of engineering knowledge**:

- Authority ownership;
- CanonicalArtifact providers;
- CapabilityIds;
- artifact dependencies;
- unresolved Questions and blocking.

The Engineering Graph defines the **normative production topology** above that state:

- which Authority owns production of each engineering capability;
- which accepted upstream capabilities are required to produce each specific capability;
- which capabilities a terminal consumer requires;
- how a selected target consumer expands recursively into an upstream engineering-knowledge closure.

It is a graph of engineering responsibility, not a phase/stage workflow.

## Authority

An Authority is one atomic boundary of engineering decision ownership.

Each Authority declares:

- `responsibility` — the coherent class of decisions it owns;
- `boundary.semantic_cohesion` — why those decisions belong together;
- `boundary.independent_change` — why the knowledge can change independently of neighbouring Authorities;
- `boundary.public_contract` — what the Authority exposes to downstream engineering work;
- `produces` — one or more **production contracts**.

The three boundary statements are the structural atomicity test. Harness can require them to exist but cannot mechanically prove their semantic truth.

An Authority does not have one global prerequisite list. Different outputs owned by the same semantic Authority may legitimately need different upstream knowledge.

## Production contract

A production contract belongs to exactly one Authority and declares:

- the CapabilityId produced;
- the upstream CapabilityIds required specifically to form that output.

Example:

```yaml
- id: PRODUCT
  responsibility: Own product decisions.
  boundary:
    semantic_cohesion: One class of accepted product decisions.
    independent_change: Product decisions can change independently of architecture.
    public_contract: Produces problem framing and product requirements.
  produces:
    - capability: example.problem
      requires: []
    - capability: example.requirements
      requires:
        - capability: example.problem
```

This allows one Authority to own several related outputs without forcing every output to wait for the union of all Authority inputs.

If two outputs are semantically unrelated, that remains evidence that the Authority should be split. Different prerequisite sets alone do not force a split.

## Capability

A CapabilityId names accepted engineering knowledge, not a file and not a task.

Exactly one Authority in one Engineering Graph may own the production contract for a CapabilityId.

A CanonicalArtifact in Core materializes an accepted capability by listing the same CapabilityId in `provides`.

The Engineering Graph therefore knows the producer before any provider artifact exists. CREATE can be routed without copying Authority into a manually authored Design Profile.

## Requirement

A production contract or terminal Consumer may require a CapabilityId.

A requirement may carry `subject` metadata for the derived target view. In v0, provider resolution remains CapabilityId-based. If different subjects require independently provable coverage, the project must expose distinct subject-scoped CapabilityIds or a project-owned coverage projection that derives them.

Do not use one broad CapabilityId with different subjects and assume `subject` filters providers.

## Public capability liveness

Every produced public CapabilityId must have a reason to exist in the selected Engineering Graph.

A produced capability must either:

- be required by another production contract or Consumer; or
- be declared explicitly in `terminal_capabilities` with its owning Authority and a reason.

An already-consumed capability cannot also be declared terminal. This catches stale or accidentally-public outputs without turning private intermediate artifact facts into capabilities.

## Consumer

A Consumer is a selected terminal target that consumes engineering knowledge but does not need to produce more engineering knowledge inside the selected graph.

`IMPLEMENTATION` is the primary example, but it is not special. A project may target deployment preparation, interface implementation, verification design or another terminal consumer.

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
      public_contract: Produces accepted problem evidence.
    produces:
      - capability: example.problem
        requires: []

  - id: PRODUCT
    responsibility: Own product intent and acceptance semantics.
    boundary:
      semantic_cohesion: One class of product decisions.
      independent_change: Product intent may change while architecture remains stable.
      public_contract: Produces accepted product requirements.
    produces:
      - capability: example.requirements
        requires:
          - capability: example.problem

consumers:
  - id: IMPLEMENTATION
    purpose: Build accepted behavior without inventing design decisions.
    requires:
      - capability: example.requirements

terminal_capabilities: []
```

A string in `produces` is shorthand for a root production contract with no prerequisites.

## Knowledge kind and agent routing

A production contract may optionally declare `knowledge_kind`.

```yaml
- capability: project.verification.strategy
  knowledge_kind: verification-strategy
  requires:
    - capability: project.architecture
```

The three identities have different purposes:

- **CapabilityId** — project-specific accepted knowledge identity used by producer/consumer topology and Core providers;
- **knowledge_kind** — repository-independent semantic class of knowledge used only by the agent execution layer;
- **artifact skill** — one registered procedure capable of forming that knowledge kind.

Engineering Graph validation and target-state evaluation do not require `knowledge_kind`. A missing or unsupported kind leaves an actionable `CREATE` **unrouted**; it never changes `CREATE` into `WAIT` or `PENDING`.

`agent_router.py` maps actionable CREATE work through `skills/artifact-skill-registry-v0.yaml`.

When several simultaneously actionable capabilities share the same Authority, subject and knowledge kind, the router groups them into one artifact-work item. This reflects cases such as one Product Requirements artifact providing both product-intent and acceptance capabilities. Grouping is an agent execution projection, not a Core task entity.

## Derived target

Selecting a Consumer recursively expands its required capabilities.

For each required capability:

1. find its unique producer Authority;
2. add the capability to the target closure;
3. read that capability's production contract;
4. add its upstream requirements;
5. repeat until root production contracts are reached.

The result is a derived Design Profile. The profile is a view, not another policy owner.

```text
target consumer
      ↓
required capabilities
      ↓
production contracts
      ↓
upstream required capabilities
      ↓
recursive closure
      ↓
derived Design Profile
      ↓
Core target-state evaluation
```

## Runtime semantics

Against a Core model:

- provider exists and is unblocked -> SATISFIED;
- provider missing, production prerequisites satisfied, no capability Question -> CREATE at the declared producer Authority;
- provider or missing capability blocked by unresolved Question -> WAIT;
- production prerequisites not yet satisfied -> PENDING;
- every derived expectation satisfied -> COMPLETE.

Question resolution changes canonical truth; it does not itself fabricate the requested capability.

## Questions and feedback

Questions are dynamic semantic feedback edges, not workflow tasks.

When production cannot continue without an unresolved semantic decision:

```text
producer attempts capability
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

If accepted canonical knowledge already decides the case and only code/tests lag, the Engineering Graph remains COMPLETE. Implementation status is not added to Core.

## Applicability

The Engineering Graph has no universal `N/A` state.

If project policy says a requirement is not applicable only when accepted evidence proves that fact, the project translates the requirement to that evidence CapabilityId. The project-specific applicability rule remains owned by the project policy.

## Coverage and subjects

A consumer contract answers **which classes of engineering knowledge are needed**.

A project completeness policy may additionally answer **for which subjects those capabilities must exist**.

Both may contribute production/consumer requirements to the projected Engineering Graph.

In v0, independent subject coverage is represented by distinct CapabilityIds, for example:

```text
engineering.domain.tactical-model@BC-RESOURCE-CATALOGUE
engineering.domain.tactical-model@BC-ACCESS-POLICY
```

The exact encoding is adapter/project policy. The invariant is that independently required subject instances must not collapse onto one broad provider key.

A first-class parameterized Capability model remains a future candidate requiring more consumer evidence.

## Atomicity and graph shape

Stable **capability production dependencies** must form a DAG.

Two production contracts owned by the same Authority may depend on one another if they remain acyclic. This represents internal refinement inside one semantic responsibility boundary.

Feedback is expressed through Questions and canonical repair, not static production cycles.

Authority atomicity is about semantic responsibility, independent change and public contract—not about forcing every output to share identical prerequisites.

## Core realization

Engineering Graph is the normative owner of Authority definitions for the selected engineering model.

A Core realization therefore does not need to duplicate the Authority list merely to evaluate current knowledge state. During Engineering Graph evaluation, missing Authority declarations are projected into the Core model in memory before Core validation.

Existing repositories may continue to declare Authorities in their Core/projection metadata; those declarations remain compatible. This projection rule mainly matters for new or partially bootstrapped projects:

```yaml
artifacts: []
questions: []
```

is enough realization state for a valid Engineering Graph to expose the first root `CREATE`.

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
