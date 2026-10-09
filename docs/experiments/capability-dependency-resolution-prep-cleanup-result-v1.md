# PREP existing-requires cleanup — exact, one-edge draft (2026-10-09)

**Status:** source-bound experiment, NOT accepted PREP topology. This file documents a concrete cleaned Engineering Graph, not a blanket transitive reduction. Neither PREP `main` nor Harness `main` is changed.

## Source and reproducibility

- Immutable baseline: `lehater/prep@d9adf4ca51049894437f1ed3d4f74fe94936c896`.
- Original file: `.harness/engineering-graph.yaml`, 34 produced Capabilities and 110 direct edges.
- [Cleaned graph copy](../../spec/dependency-resolution/project-pilots/prep-engineering-graph-cleaned-draft-v1.yaml) is intended to be byte-for-byte identical to that accepted source except the **one** direct requires entry below. It has 109 direct edges.
- Baseline graph has 67 edges transitively reachable by another already declared path, across 26 targets, with no cycles/missing providers. **This is not a list of 67 removable edges.**
- Direct artifact prerequisites from PREP `.harness/core.yaml` correspond to **66 of those 67** flagged edges; retain them in the graph for this cleanup. Core dependency records are evidence of existing explicitly authored intent, **not independent proof** that every such link is materially direct; further changes must be separately adjudicated.

## Single proposed removal

`prep.frontend-system-architecture -> prep.application-design`

- Existing accepted alternative contract path: `prep.frontend-system-architecture -> prep.machine-interfaces -> prep.application-design`. A second longer path also exists through presentation/screen/interaction.
- Accepted target artifact `docs/architecture/frontend-system-architecture.md`, **Purpose**, reads: “The frontend consumes accepted Application semantics through transport-neutral Machine Interface operations.” This is an explicit mediation statement, stronger than reachability alone.
- Canonical provider contract `docs/interface/machine-interface.md`, **Purpose**, defines the consumer-visible, transport-neutral execution of accepted application operations and bounded Process semantics. It owns that public mediation boundary.
- Accepted Core artifact `FRONTEND-SYSTEM-ARCHITECTURE` has direct `depends_on` values `SYSTEM-ARCHITECTURE`, `PRESENTATION-SYSTEM`, `SCREEN-VIEW-DESIGN`, `MACHINE-INTERFACES`, `FRONTEND-PERFORMANCE-CAPACITY`; **not** `APPLICATION-DESIGN`. This makes the Graph-only edge independently suspicious.
- Counterfactual semantic judgment: changing the internal Application Design while leaving the public Machine Interface and separately accepted screen/presentation/frontend constraints unchanged should not require a new frontend structural contract. A changed Machine Interface does require revalidation and its direct edge remains.
- No provider or target artifact text, accepted Core dependency, lifecycle assertion, or semantic-baseline review is rewritten by this experiment.

**Proposed disposition**: `REMOVE_CANDIDATE_SOURCE_GROUNDED`. Do not mark `AUTHORITY_ACCEPTED` or merge into PREP without the existing project governance confirming this semantic judgment and republishing the changed dependency topology.

## Separate finding: do not automatically add an edge

Core `FRONTEND-SYSTEM-ARCHITECTURE` directly depends on `SYSTEM-ARCHITECTURE`, while Engineering Graph does **not** directly declare `prep.frontend-system-architecture -> prep.system-architecture`. These are different abstraction levels; Core `depends_on` is an **artifact-level** prerequisite, and `requires` is a **Capability-level semantic** dependency. Their mismatch is a review signal, *not proof that the other direct edge must be added*. The frontend architecture explicitly says it is independently evolvable from backend runtime topology; this distinction needs separate adjudication.

## Why the other 66 are not mechanically deleted

All 66 surviving flags are already represented as direct Core artifact prerequisites. A graph-theoretic transitive reduction would erase semantic-specific source consumption that may not be mediated by the intermediate Capability's public contract. Examples: Interface Verification explicitly verifies Task Model and Interaction Design; Data Design directly preserves Knowledge, Learning and Learner semantics even though each is reachable by other paths. These direct meanings must remain unless individually contradicted by stronger accepted evidence.

## Validation contract

A full regression against the exact proposed copy must check:

1. The entire cleaned graph is exactly the pinned baseline **minus one targeted line**.
2. All nodes, Authority owners, producer contracts, consumer entries and every other direct edge are identical.
3. Alternative reachability, full consumer closure and all existing dependency paths other than the one edge remain unchanged; cycles and unknown providers stay zero.
4. Harness Engineering Graph validation, Greenfield regression, and full Harness regression pass.
5. PREP acceptance/currentness/publication is **not** silently asserted from a structural pass. A topology update that invalidates the accepted project publication must be reported as a governance blocker rather than repaired by editing accepted publication fingerprints without approval.

No `ADD`, no broader `REMOVE`, no writeback permission, and no snapshot or canonical change in PREP.
