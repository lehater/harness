# Research — Frontend interaction semantic closure v1

Status: validated architecture; minimal universal evaluator implementation on research branch.

## Architectural conclusion

The recurring frontend failures are not evidence for a new UI/UX Authority and do not justify five independent mandatory knowledge kinds.

The actual gap is **semantic closure depth** between accepted Journey/Domain/Machine Interface knowledge and Screen/View realization.

Existing ownership remains correct:

- APPLICATION-DESIGN owns accepted user task/journey semantics.
- DOMAIN / DOMAIN-USE-CASE-DESIGN owns business state, mutability, invariants and outcomes.
- SECURITY owns authorization/trust semantics.
- INTERFACE-DESIGN owns navigation, user-visible actions, reference interaction, state/outcome representation and Screen/View contracts.
- Machine Interface owns stable operations/request/response shapes.
- Presentation providers remain downstream realization.

Harness Core already has the required graph primitives: Authority, capability requires/provides, consumers, semantic evaluations and blocking propagation. No Core entity is added.

## P0 gap

A Screen/View semantic evaluation could previously validate only semantics that were already declared. It did not prove that:

- every screen traced to an accepted task;
- every canonical authoring route had deterministic parent/direct-link/success/cancel semantics;
- every material reference selection had candidate/search/dependency/submitted-value semantics;
- every accepted machine-operation response had a UI state/transition;
- every required screen was actually included in strict semantic closure by the consuming project.

This permits implementation to invent interaction truth.

## Minimal universal model

Strict interaction closure extends existing Screen/View/Human Interface contracts rather than creating a parallel artifact family.

### Task trace

```yaml
semantic_contract:
  task_refs: [DEPLOYMENT-MANAGEMENT]
```

Task existence is checked against the accepted journey/task inventory supplied by the project navigation contract.

### Navigation

```yaml
routes:
  - path: /deployments/:deploymentRef
    workspace: DEPLOYMENT-DETAIL
    parent: navigation:deployments
    direct_link: canonical
  - path: /deployments/new
    workspace: DEPLOYMENTS
    mode: create
    parent: navigation:deployments
    direct_link: canonical
    success: navigation:deployment-detail
    cancel: navigation:deployments
```

A top-level/root route uses an explicit not-applicable object with rationale for parent.

### Actions

Actions continue to use the existing Screen/View capability policy:

```yaml
commands:
  - {id: create-deployment, operation_id: createDeployment}
capabilities:
  allowed:
    - {id: create-deployment, backed_by: command:create-deployment}
```

Strict closure additionally rejects a declared command with no accepted user-visible capability.

### References

```yaml
references:
  - id: component
    use: display-selection
    identity: componentRef
    display:
      primary: [name, applicationName]
      technical_identity: componentRef
    candidates:
      operation_id: listComponents
      mode: independent
      search: server-backed
    submitted_value: componentRef
    submits_to: command:create-deployment
```

Dependent selection adds `mode: dependent` and non-empty `depends_on`.
Workflow-constrained selection uses `mode: workflow`; its candidate source must itself be authoritative for the task-oriented candidate set.

Screen composition binds a concrete reference interaction through a contract id rather than re-inventing candidate semantics locally.

### Outcomes

Existing `state_mapping` remains valid. Command/read success transitions that are not screen states use `outcome_mapping`:

```yaml
outcome_mapping:
  command:create-deployment.201: navigation:deployment-detail
```

Every OpenAPI response code for a bound operation must appear in state/outcome mapping or in an explicit `outcome_exclusions` item with rationale.

## Dependency graph

Before:

```text
Requirements → Journey → Domain/API
  → Human Interface → Navigation → Screen/View
  → Frontend Architecture → Component/Verification/Test → Implementation
```

The topology remains unchanged. The semantic acceptance edge is strengthened:

```text
Journey/Domain/Security/Machine Interface
  ↓
Human Interface semantics
  ↓
Screen/View + strict interaction closure evaluation
  ├─ task trace
  ├─ route parent/direct-link/success/cancel
  ├─ action↔command closure
  ├─ reference candidate/dependency closure
  └─ operation outcome closure
  ↓ ACCEPTED only
Frontend Architecture → Component/Verification/Test → Implementation
```

A rejected semantic evaluation makes the Screen/View capability unusable. Existing dependency propagation blocks implementation.

## Authority decision

No new Authority.

No new mandatory knowledge kind.

The model is intentionally a stricter semantic contract/evaluator under INTERFACE-DESIGN. Creating FRONTEND-INTERACTION-DESIGN would duplicate Application Journey and Human Interface ownership and introduce lifecycle ambiguity.

## Universal versus project truth

Harness knows only generic concepts:

- task ref;
- route/workspace;
- action/read/command;
- reference identity/display/candidate/dependency/submitted value;
- user-visible state/transition;
- operation outcome;
- semantic closure.

Harness never knows Application, Component, Deployment, Connectivity Need, Access Request or MUI.

NAPMS supplies those concrete values.

## NAPMS scenario check

| Scenario | Required semantic closure | Expected status if missing |
|---|---|---|
| Create Application | task, createApplication command, success/rejection/conflict/unavailable mapping, parent/cancel/success route | BLOCKED |
| Add Component | Component task, addComponent command, application context, outcomes, cancel/success | BLOCKED |
| Create Interaction | Interaction task, source/destination Component references and candidates, createInteraction outcomes | BLOCKED |
| Create Deployment | Component + Resource display/selection contracts, createDeployment outcomes | BLOCKED |
| Declare Connectivity Need | Interaction selection plus participant dependent on selected Interaction endpoints | BLOCKED |
| Submit Access Request | task-oriented eligible subject semantics tying Need → Revision → Source/Destination Deployment | BLOCKED |
| Attach Policy Rule justification | recognizable Connectivity Need candidate semantics + attach command outcomes | BLOCKED |
| Edit/Rename Application | accepted domain/application mutation command + machine operation | BLOCKED while absent |
| Edit/Rename Component | accepted domain/application mutation command + machine operation | BLOCKED while absent |
| Direct detail navigation | canonical route, parent, direct-link behavior, readable reference presentation | BLOCKED |

The important Access Request assertion is that four independent UUID inputs cannot satisfy a workflow reference contract. The project must materialize an authoritative workflow candidate source/dependency contract.

## Projections

The following are derivable views, not authorities:

- User Task Map from task refs/journeys;
- Workspace Map from routes/parents/transitions;
- Screen Map from route↔workspace↔Screen/View contracts;
- Action Matrix from allowed capabilities and command/read/navigation backing;
- Reference Dependency Map from reference contracts and depends_on;
- State Transition Map from state/outcome mappings.

## Migration

1. Enable strict interaction closure in Harness acceptance fixtures.
2. Repin NAPMS to the validated Harness commit.
3. Evaluate **all** required NAPMS workspaces, not a pilot subset.
4. Materialize task refs, canonical route closure, reference contracts and exhaustive outcome mappings.
5. Treat missing mutation/candidate APIs as upstream Questions/UNRESOLVED rather than UI implementation tasks.
6. Generate maps/matrices only after canonical semantics pass.
7. Continue frontend fixes from the accepted graph.

## Priority

- P0: full required-screen semantic evaluation; action-command closure; reference dependency/candidate closure; operation outcome closure; blocking propagation.
- P1: canonical parent/direct-link/success/cancel semantics and task trace.
- P2: generated task/workspace/action/reference/state projections.
- P3: visualization/style of those projections.
