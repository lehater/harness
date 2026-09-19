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

- a true greenfield project where the agent creates accepted artifacts from the root frontier all the way to an implementation-ready target;
- a standard/reference Authority catalog for new software projects, separated from project-specific topology;
- first-class parameterized/scoped capabilities instead of adapter-encoded subject CapabilityIds;
- automatic artifact-skill routing from a production contract;
- whether project-specific applicability rules need any standard contract beyond evidence CapabilityIds;
- projects whose engineering knowledge topology legitimately contains feedback that cannot be represented as Questions over an acyclic production graph;
- larger graphs with many simultaneous unresolved Questions and multiple active target Consumers.

The model should remain branch-only until at least the standard Authority catalog and one greenfield end-to-end run are exercised.
