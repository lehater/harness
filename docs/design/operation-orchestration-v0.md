# Operation Orchestration v0

Status: canonical.

## Purpose

Define how an agent composes several routed Harness operations into one user
use case while keeping routing centralized and skills independently owned.

Harness uses a manager/coordinator model: the agent retains control of the
overall request and resolves each new semantic responsibility through the typed
router.

## Terms

- **Coordinator** — the active agent managing the user-level use case.
- **Operation** — one semantic responsibility with explicit trigger, inputs,
  procedure and completion/output.
- **Router** — `harness.application.skill_router`, which resolves an operation identity to its
  registered skill.
- **Skill** — the executable procedure implementing one routed responsibility.
- **Substep** — a technical action inside an operation, such as reading a file,
  running a validator or invoking a deterministic script.

## Core invariants

1. The coordinator owns sequencing across operations.
2. Every new operation responsibility is resolved through `harness.application.skill_router`.
3. A skill may name a semantic next/internal operation, but it must not bind to
   another skill by physical filesystem path as its orchestration mechanism.
4. Ordinary substeps inside one responsibility do not require rerouting.
5. Public operations are valid use-case entrypoints.
6. Internal operations are composable implementation procedures. They are
   reachable only from a concrete declared parent public operation. Runtime
   routing must supply that parent operation identity and validate it against the
   internal route's registry `invoked_by` authorization.
7. The router resolves routes; it is not a workflow/state-machine engine.
8. Operation sequencing is not project truth and must not introduce Stage,
   Phase, Gate, Handoff or universal workflow-state entities into Core.
9. When equivalent guarantees can be preserved with fewer coordination
   boundaries, external round trips or repeated work, use the smaller process
   defined by `docs/design/process-simplicity-and-efficiency-v0.md`.

## Operation contract

A routed operation should make these boundaries explicit in its skill:

- Trigger;
- Inputs;
- Procedure;
- Output / completion condition;
- Stop/escalation conditions when continuation would violate another owner.

A universal serialized `OperationResult` type is not required in v0. Introduce
one only after multiple consumers demonstrate a need for machine-readable
cross-operation state.

## Composition algorithm

```text
user request
    ↓
coordinator identifies current operation
    ↓
skill_router
    ↓
selected skill
    ↓
execute responsibility
    ↓
responsibility complete?
    ├─ use case complete -> finish
    └─ another responsibility required
           ↓
       coordinator identifies semantic operation
           ↓
       skill_router
           ↓
       next skill
```

The continuation decision belongs to the coordinator using operation semantics,
not to a hard-coded physical skill-to-skill call.

## Process economy

Coordinator ownership does not imply that every repeated technical transition
must remain an agent-level operation. When a stable sequence repeatedly
performs one application responsibility and can preserve all participating
invariants internally, consolidate it behind the owning Application boundary.

In particular, repeated project-side loops around currentness calculation,
deterministic validation, blocker aggregation and coherent publication are
evidence to consider an Application service rather than normalizing more glue or
CI choreography.

The router remains a procedure-discovery boundary, not a workflow engine.
Consolidation belongs in the application capability that owns the coherent
operation.

## Public and internal operations

A public operation may require a reusable internal operation. The parent skill
may reference the internal **operation id**. The coordinator then resolves that
id through the router while supplying the parent operation identity.

```text
project-bootstrap-reconcile
    ↓ needs minimal Core bootstrap
bootstrap-existing-project
    ↓
skill_router operation --surface consumer \
  --operation bootstrap-existing-project \
  --invoked-by project-bootstrap-reconcile
    ↓
registered internal skill
```

The registry's `invoked_by` relation is the machine-readable authorization for
that composition. The router verifies both that the supplied parent is a
registered public operation and that the target internal route authorizes it.
A boolean internal-routing bypass is not a valid authorization contract. A
direct `SKILL.md` filesystem path is not the orchestration contract.

Specialized generated-document projections use the same composition mechanism;
`docs/design/document-projection-operations-v0.md` defines their projection-
specific boundary without introducing another router or route class.

## Failure and retry

An operation reports failure/blocking in terms owned by its domain contract.
The coordinator does not silently reinterpret a failed operation as success or
skip to a downstream responsibility.

Retry policy belongs to the operation/domain that owns the failed state. A retry
that changes semantic responsibility is routed again like any other operation.

## Contract discovery

Instruction discovery follows
`docs/design/agent-instruction-architecture-v0.md`.

The selected skill names the canonical policies/specs needed for its procedure.
The coordinator loads those references progressively rather than scanning the
whole repository.

## Compatibility rule

Existing composite procedures should be interpreted through this contract first.
If an existing skill names another registered operation, treat that as a
semantic continuation and route it. Record a defect only when repository
evidence demonstrates incompatible executable behavior; do not create migration
work from wording alone.
