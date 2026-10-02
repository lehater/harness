# Harness DDD Context Review v0

Status: audit baseline for `audit/harness-corrections`.

## Domain

Harness is not primarily a document generator or workflow engine. Its domain is **governance of engineering knowledge for a software project**:

- what engineering knowledge is required;
- who owns each class of decision;
- what accepted knowledge currently exists;
- whether accepted knowledge is trustworthy and current;
- what unresolved semantic gap prevents progress;
- what the next admissible engineering action is.

The DDD model of Harness itself must therefore be separate from the DDD methodology that Harness can apply to a target project.

## Strategic decomposition

| Area | Type | Owns |
|---|---|---|
| Project Model | Core bounded context | project Authority instances, CapabilityIds, production topology, Consumers, CanonicalArtifact realization, Questions and structural target state |
| Engineering Coverage | Core bounded context | Concerns, applicability, subject obligations, proof requirements and completeness |
| Knowledge Assurance | Core bounded context | semantic evaluation, derivation proof, acceptance identity and currentness |
| Reference Engineering Model | Supporting bounded context | reusable Authority types, Capability templates, applicability predicates and reference-model evolution |
| Decision Governance | Supporting bounded context | alternatives, decision-space review, governance dispositions and execution assurance |
| Source Evidence | Supporting bounded context | source acquisition scope, lossless source boundaries and statement coverage |
| Repository Integration | Supporting bounded context / ACL | projection from project-native repository models into Harness published models |
| Managed Knowledge / Projection | Generic bounded context | optional managed artifact formats and disposable human projections |
| Application Layer | Not a bounded context | orchestration across contexts; owns no durable domain truth |

Machine-readable ownership is defined in `spec/architecture/harness-context-map-v0.yaml`.

## Single ownership of ubiquitous language

| Concept | Owner |
|---|---|
| project Authority | Project Model |
| reference Authority type | Reference Engineering Model |
| CapabilityId | Project Model |
| Capability template | Reference Engineering Model |
| Concern / applicability / coverage state | Engineering Coverage |
| SemanticEvaluation / AcceptanceIdentity / currentness | Knowledge Assurance |
| Decision alternatives / governance disposition | Decision Governance |
| Question | Project Model; other contexts may only propose one |
| Source-set/boundary/statement disposition | Source Evidence |
| next action / route / closure projection | Application Layer, derived and disposable |

This ownership rule is the main anti-duplication constraint.

## Context map

    Reference Engineering Model
              |
              | materialization proposal / published EngineeringGraph
              v
        Project Model <---------------- Repository Integration
            ^   ^
            |   |
            |   +--------- Knowledge Assurance <------ Source Evidence
            |                       ^
            |                       |
            |                 Decision evidence
            |                       |
            +---- Engineering Coverage          Decision Governance
                        ^                              ^
                        |                              |
                        +---------- Application Layer--+

Managed Knowledge / Projection is downstream of Project Model and Integration.

The Application Layer coordinates the feedback loop. No bounded context may depend on the Application Layer.

## Critical ownership decision

The largest conceptual overlap is between Reference Engineering Model and Engineering Coverage.

The rule is now canonicalized in `docs/design/model-completeness-ownership-v0.md`:

- **Coverage owns the question "is the selected project/scope sufficiently covered?"**
- **Reference Model owns the reusable mapping "given accepted project facts/concerns, which reusable capability templates could realize the required knowledge?"**
- **Project Model owns the actual project Engineering Graph.**

Therefore a Reference Model materialization can propose/derive a project graph, but it does not itself prove completeness. Conversely Coverage may expose a missing proof/obligation, but it must not become a second owner of the project graph.

This gives one direction:

    Coverage gap/obligation
        -> Application coordination
        -> Reference materialization when reusable mapping exists
        -> Project Model proposal/change
        -> Coverage re-evaluation

No circular ownership is needed.

## Aggregate/invariant boundaries

### Project Model

Primary invariants:

- one producer Authority per project CapabilityId;
- production prerequisites form an acyclic knowledge topology;
- CanonicalArtifact providers agree with project Authority ownership;
- unresolved Questions are owned by exactly one Authority and block explicit project knowledge;
- structural state is derived from the current graph/realization, never stored as independent truth.

### Engineering Coverage

Primary invariants:

- silence is not proof of NOT_APPLICABLE for manually classified concern families;
- every accepted scope atom is classified or explicitly excluded;
- every required concern has an admissible proof route or explicit unresolved work;
- `completion_ready` is derived only from terminal coverage/applicability state.

### Knowledge Assurance

Primary invariants:

- acceptance is Capability-granular;
- accepted evidence is bound to the rules/contracts under which it was accepted;
- currentness covers every material dependency that justified acceptance;
- a changed/new semantic dependency cannot remain CURRENT without explicit re-evaluation.

### Decision Governance

Primary invariants:

- alternative formation precedes choice;
- reviewed decision space and chosen disposition refer to the same decision identities;
- escalation creates a proposal for Project Model Question state, not a second decision state.

### Reference Engineering Model

Primary invariants:

- templates and Authority types are reusable identities, not project instances;
- applicability uses accepted project facts and fails closed on unresolved predicates;
- materialization emits project-model proposals; it never silently changes project truth.

## Application services

The following modules should be treated as orchestration/process-manager code rather than domain owners:

- `agent_router.py`
- `authority_context.py`
- `decision_pipeline.py`
- `decision_explorer_request.py`
- `semantic_admission.py`
- `semantic_closure.py`
- `semantic_questions.py`
- `graph_doctor.py`
- `skill_invariant_policy.py`

This reclassification explains why `semantic_admission.py` legitimately coordinates several contexts. Its current problem is naming/physical placement, not the mere fact that it orchestrates them.

## Current boundary violations

The import ratchet currently contains no explicit violations. BC-01 and BC-02 were removed by introducing an application-level Coverage orchestration boundary, and BC-03 was removed by separating the pure Decision Explorer request contract from application-level request derivation.

### BC-01: Coverage -> Integration — resolved

`engineering_coverage.py` now consumes only an already resolved Project Model realization.
Repository-native projection/alignment moved to `coverage_application.py`, which coordinates the Integration ACL before invoking the pure Coverage evaluator.

### BC-02: Coverage -> Application — resolved

Coverage now emits unrouted Coverage work items only. `coverage_application.py` decorates those derived work items with registered skill routes for application execution. Coverage output therefore remains valid when no agent/skill subsystem exists, while the application-facing scenario/API retains routed work.

### BC-03: Decision -> Application — resolved

`decision_explorer_contract.py` now owns the pure Decision Explorer request shape, deterministic request identity and evidence-binding validation inside the Decision bounded context.

`decision_explorer_request.py` remains in the Application Layer and derives concrete request inputs from Authority Context, Lifecycle and Engineering Graph before delegating request construction to the pure Decision contract. `decision_exploration.py` depends only on `decision_explorer_contract.py`, so the Decision bounded context no longer imports Application orchestration.

## Existing audit findings explained by the context map

The DDD view does not replace the backlog; it groups root causes.

- `HARN-001` -> Coverage invariant failure.
- `HARN-002`, `HARN-009`, `HARN-011` -> Assurance invariant/currentness failures.
- `HARN-003`, `HARN-005`, `HARN-006`, `HARN-013` -> Project Model <-> Assurance boundary ambiguity.
- `HARN-004`, `HARN-007`, `HARN-010`, `HARN-012`, `HARN-015` -> missing/ambiguous Application Layer transition semantics.
- `HARN-008` -> Reference Model <-> Coverage ownership ambiguity.
- `HARN-014` -> Project Model identity evolution boundary.

This is evidence that the defects are not independent accidents; several are manifestations of missing bounded-context ownership.

## Enforcement

`validators/validate_context_boundaries.py` enforces a ratchet:

- every root runtime module must belong to one context/layer or be explicitly classified as research/test;
- domain contexts may import only declared upstream contexts;
- any temporary violation must be explicitly declared, and the current map declares none;
- a new undeclared violation fails validation;
- once a known violation disappears, the validator fails until its exception is removed.

This prevents architecture debt from growing while allowing incremental correction.

Published cross-context module/symbol contracts are additionally enforced by the
same validator from `spec/architecture/harness-context-map-v0.yaml`; see
`docs/design/context-published-contracts-v0.md`.

## Refactoring order

Do not start with a repository-wide package move.

1. Establish context ownership and the import ratchet. **Done on the audit branch.**
2. Remove BC-01/BC-02 by separating pure Coverage evaluation from integration and skill routing. **Done on the audit branch.**
3. Remove BC-03 by splitting the Decision request contract from its application builder. **Done on the audit branch.**
4. Introduce stable published read models at context boundaries, especially Assurance -> Coverage. **Done: `docs/design/context-published-contracts-v0.md` plus machine-enforced `published_boundaries`.**
5. Resolve `HARN-008` explicitly: Coverage owns completeness; Reference Model owns reusable materialization. **Canonical ownership contract added on the audit branch.**
6. Fix functional P0 invariants inside their owning contexts.
7. Physically move modules under `src/harness/<context>/...`. **Now unblocked as an incremental migration governed by `docs/design/repository-layout-v0.md`.**

The final package move should be mechanical confirmation of boundaries already enforced semantically, not the mechanism used to discover them.
