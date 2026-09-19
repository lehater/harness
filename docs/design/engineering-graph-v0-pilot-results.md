# Engineering Graph v0 — consumer pilot results

Status: experimental evidence for `pilot/engineering-graph-v0`.

## Harness acceptance

The internal acceptance fixture proves:

- a target Consumer recursively expands through production contracts;
- an empty Core realization exposes only immediately producible root knowledge as `CREATE`;
- accepting that root advances the frontier to the next production contract;
- an unresolved capability Question produces `WAIT`;
- downstream production remains `PENDING`;
- complete accepted providers produce `COMPLETE`;
- static production dependency cycles are rejected;
- one CapabilityId cannot have multiple semantic producer Authorities;
- one broad CapabilityId cannot be used as independently provable coverage for several subjects.

The first draft used one `Authority.requires` list for every output. Nutrition Management immediately falsified that abstraction: one Authority may own several related outputs with different prerequisites. v0 therefore uses **per-capability production contracts**.

## Nutrition Management

Pilot branch: `pilot/engineering-graph-v0`.

Nutrition stores an explicit `.harness/engineering-graph.yaml` because it does not already have an equivalent producer/consumer policy model.

Observed results:

- `IMPLEMENTATION` derives to `COMPLETE` from the accepted Core state;
- a literally empty Core realization (`artifacts: [], questions: []`) derives its Authorities from Engineering Graph and exposes only `nutrition-management.problem` as root `CREATE`;
- after accepting Problem, the next frontier is only `nutrition-management.requirements`;
- `THEORETICAL-GAP-SUGGESTIONS` derives `COMPLETE`;
- `NUTRIENT-EVIDENCE-PROPAGATION` derives `COMPLETE`;
- `BLS-V4-PRODUCTION-IMPORT` derives the real current frontier:
  - source-code-set -> `CREATE`;
  - category assignment / package contract / import verification -> downstream `PENDING`.

This replaces manual ordering policy with one producer/consumer graph while preserving the already-observed runtime semantics.

## NAPMS

Pilot branch: `pilot/engineering-graph-v0`.

NAPMS already owns richer policy sources:

- `docs/canonical-graph.yaml`;
- `docs/harness-core.yaml`;
- `docs/engineering-knowledge-completeness.yaml`;
- explicit artifact `knowledge_coverage`.

The pilot does not persist another Engineering Graph. A project adapter composes those sources into one transient `harness-engineering-graph` and one transient Core realization.

Observed results:

- first-MVP `IMPLEMENTATION` -> `COMPLETE`;
- removing Core `authorities` entirely does not change the result; Authority definitions are projected from Engineering Graph;
- several canonical artifacts under one Authority may provide one broad capability; the adapter correctly collapses those artifacts to one semantic production contract;
- missing `engineering.interface.resource-detail-ui` -> exactly one `CREATE`;
- missing Resource Catalogue scoped tactical coverage -> exactly one scoped `CREATE`;
- unresolved Interface Question -> the affected interface capability is `WAIT`.

This confirms that one Engineering Graph model can sit above both a Harness-managed workspace and a mature project-native engineering model.

## Confirmed model boundary

The evidence currently supports this split:

### Engineering Graph — normative engineering topology

- atomic Authority definitions;
- unique semantic producer for each CapabilityId;
- per-capability production prerequisites;
- terminal Consumers and their required capabilities;
- subject/scoped capability requirements;
- recursive target closure.

### Core realization — accepted current knowledge state

- CanonicalArtifacts;
- artifact dependencies;
- provided CapabilityIds;
- Questions;
- blocking/resolution.

Authority IDs may still appear in an existing Core representation for compatibility, but Engineering Graph is sufficient to project them for evaluation.

### Derived Design Profile

A Design Profile is now demonstrably a target-specific projection of Engineering Graph policy. It should not be the primary policy owner when an Engineering Graph is available.

## Still unproven

Do not merge this model to `main` yet.

The following remain validation targets:

- first-class parameterized/scoped capabilities instead of adapter-encoded subject CapabilityIds;
- automatic artifact-skill routing from a production contract;
- whether project-specific applicability rules need any standard contract beyond evidence CapabilityIds;
- projects whose engineering knowledge topology legitimately contains feedback that cannot be represented as Questions over an acyclic production graph;
- larger graphs with many simultaneous unresolved Questions and multiple active target Consumers.

The model should remain branch-only until at least the standard Authority catalog and one greenfield end-to-end run are exercised.


## Greenfield end-to-end pilot

Reference project:
`examples/greenfield-csv-deduplicator/**`.

The project was intentionally smaller than NAPMS and instantiated only:

- DISCOVERY;
- PRODUCT-REQUIREMENTS;
- SYSTEM-ARCHITECTURE;
- INTERFACE-DESIGN;
- IMPLEMENTATION-DESIGN;
- VERIFICATION-DESIGN.

DDD, persistence, security, quality and operability Authorities were omitted
because no independently owned decision class required those boundaries.

The branch history records an agent-operated progression. Each artifact was
created only after the current Engineering Graph evaluation exposed the matching
`CREATE` frontier.

Observed sequence:

1. empty Core realization -> only `csv-deduplicator.problem-evidence` CREATE;
2. accepted Problem Evidence -> Product Intent + Acceptance CREATE in parallel;
3. accepted Product Requirements -> Architecture CREATE;
4. accepted Architecture -> CLI Contract CREATE;
5. accepted CLI Contract -> Implementation Plan CREATE;
6. accepted Implementation Plan -> Completion Criteria and Verification Strategy
   CREATE in parallel;
7. accepted Verification Strategy -> Acceptance Scenarios CREATE;
8. accepted Acceptance Scenarios -> target `IMPLEMENTATION` becomes `COMPLETE`.

No manually maintained Design Profile or explicit gate checklist was changed
during the progression. The target was derived from the same Engineering Graph
at every commit.

The pilot also confirms:

- one canonical artifact may materialize several capabilities from one Authority
  when they form one coherent accepted specification;
- the graph naturally exposes parallel design work when prerequisites permit it;
- the implementation readiness boundary is a satisfied terminal Consumer
  contract rather than a special Gate entity;
- a materially simpler project can omit most NAPMS Authorities without changing
  the Harness execution model.

## Reference Authority catalog

`catalogs/software-authorities-v0.yaml` now records an experimental reference
catalog distilled from NAPMS, Nutrition and legacy methodology.

The catalog standardizes the Authority atomicity test:

- semantic cohesion;
- independent change;
- public contract.

It separates baseline boundary candidates from conditional ones. The catalog is
not a required document sequence and does not contain project CapabilityIds.
Concrete production contracts remain project Engineering Graph data.

The greenfield pilot validates that a project can instantiate a strict subset of
the reference catalog while using the same Engineering Graph runtime semantics.

## Updated remaining validation targets

The following are no longer unproven:

- cross-consumer Nutrition/NAPMS compatibility;
- Authority ownership projection into an otherwise empty Core realization;
- a real agent-operated greenfield path from empty state to IMPLEMENTATION
  COMPLETE;
- a smaller project shape that omits most NAPMS Authorities.

Still deliberately experimental:

- first-class parameterized/scoped capabilities instead of adapter-encoded
  subject CapabilityIds;
- automatic artifact-skill routing from production contracts;
- whether production contracts should reference an artifact type/skill contract
  or remain pure knowledge topology;
- project-specific applicability beyond the already proven evidence-capability
  pattern;
- legitimate engineering feedback topologies that may challenge the static DAG
  assumption.


## Semantic CREATE-to-skill routing

Engineering Graph production contracts may now declare an optional
`knowledge_kind`.

This separates:

- project-specific CapabilityId;
- repository-independent semantic knowledge kind;
- installed artifact skill implementation.

`agent_router.py` routes only actionable `CREATE` work through
`skills/artifact-skill-registry-v0.yaml`.

Observed evidence:

- greenfield `csv-deduplicator.verification-strategy` routes to the existing
  reusable `verification-strategy` skill even though its CapabilityId has no
  Nutrition/NAPMS naming relationship;
- the real Nutrition BLS frontier
  `nutrition-management.food-knowledge.bls-v4.source-code-set` routes to
  `pinned-source-entity-set`;
- WAIT work is never routed to an artifact skill;
- unknown/missing knowledge kinds remain valid CREATE work but are reported as
  `UNROUTED`, preserving the distinction between engineering readiness and
  available automation.

The greenfield Product Requirements step also showed that one canonical artifact
may satisfy several simultaneously actionable capabilities. The router therefore
groups CREATE work by `Authority + subject + knowledge_kind`.

Two greenfield capabilities:

- `csv-deduplicator.product-intent`;
- `csv-deduplicator.acceptance`;

become one `product-requirements` artifact-work item rather than two fake tasks.

This grouping is an agent execution view, not a new Core Task/Workflow entity.

## Applicability evidence

NAPMS Engineering Graph projection was tested with the project-native
not-applicable rule for asynchronous messaging.

The existing contract states that an asynchronous interface contract is not
required when the accepted capability
`engineering.architecture.async-messaging-not-applicable` proves that fact.

The adapter translates this to an ordinary upstream capability requirement.

Observed behavior after removing only that evidence provider:

- IMPLEMENTATION target -> READY;
- exactly `engineering.architecture.async-messaging-not-applicable` -> CREATE;
- no special N/A state;
- no WAIT.

This confirms the current applicability rule: applicability remains project-owned
policy and Harness consumes its accepted evidence as normal engineering knowledge.


## Full greenfield artifact-skill coverage

The greenfield pilot now classifies every production capability in its
IMPLEMENTATION closure with a reusable `knowledge_kind` and verifies a registered
artifact skill for every possible frontier.

Registered greenfield path:

```text
problem-evidence
→ problem-evidence skill

product-intent + acceptance
→ one grouped product-requirements work item
→ product-requirements skill

architecture
→ system-architecture skill

CLI contract
→ interface-contract skill

implementation plan
→ implementation-design skill

completion criteria
→ implementation-design skill

verification strategy
→ verification-strategy skill

acceptance scenarios
→ acceptance-scenarios skill
```

The greenfield workflow starts from the final accepted model, removes each
provider (or coherent provider capability group) in turn, reevaluates
IMPLEMENTATION, and proves the newly exposed CREATE routes to exactly one expected
skill work item.

The artifact skills are repository-independent procedures. Their outputs remain
project-native where NAPMS/greenfield/Nutrition demonstrate different natural
formats.

New skills justified by repeated evidence:

- `problem-evidence` — NAPMS Discovery, Nutrition Problem/Evidence, greenfield;
- `product-requirements` — NAPMS Product Requirements, Nutrition Product
  Requirements, greenfield;
- `system-architecture` — NAPMS system rules, Nutrition target architecture,
  greenfield;
- `interface-contract` — NAPMS external interface contracts and greenfield CLI;
- `implementation-design` — NAPMS readiness design and greenfield plan/completion;
- `acceptance-scenarios` — NAPMS test intent and greenfield scenarios.

This proves skill routing can cover a complete simple software-product design
path without putting skill names into CapabilityIds or Core state.

## Scoped capability conclusion

First-class subject-parameterized capabilities remain deliberately deferred.

See `docs/design/scoped-capabilities-research-v0.md`.

The current evidence supports explicit scoped CapabilityIds in project/adaptor
projection, but does not yet define universal subject propagation through
production prerequisites.
