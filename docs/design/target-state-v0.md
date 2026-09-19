# Harness design target state v0

A Design Profile declares the engineering knowledge that must exist before a selected scope is considered design-complete.

It is a layer above Harness Core v0. It does not add workflow, task, stage, approval or artifact-content semantics to Core.

## Contract

A profile is YAML:

```yaml
version: 1
kind: harness-design-profile
id: APPLICATION-DESIGN

expectations:
  - id: APPLICATION-DOMAIN
    subject: APPLICATION
    capability: application.domain-semantics
    authority: DOMAIN

  - id: APPLICATION-ARCHITECTURE
    subject: APPLICATION
    capability: application.architecture
    authority: ARCHITECTURE
    depends_on: [APPLICATION-DOMAIN]
```

Each expectation means:

- `subject` — the scope/entity for which knowledge is required;
- `capability` — the required engineering knowledge identifier;
- `authority` — the Authority that must own the canonical provider;
- `id` — stable identifier for the expectation;
- optional `depends_on` — prerequisite expectation ids that must be satisfied before this knowledge is actionable.

The profile declares required knowledge, not where or how that knowledge must be documented.

`depends_on` is knowledge ordering for the agent, not a project workflow. It answers whether the downstream knowledge can responsibly be formed without inventing an upstream decision.

Dependencies must reference expectations in the same profile and must be acyclic.

## Evaluation

`target_state.py PROFILE MODEL` evaluates the declared target state against a normal Core v0 model.

For an expectation whose prerequisites are satisfied:

1. no canonical provider for the capability -> `CREATE`;
2. provider exists under another Authority -> invalid profile/model combination;
3. provider exists but is transitively blocked by unresolved Questions -> `WAIT`;
4. provider exists under the expected Authority and is not blocked -> satisfied.

An expectation whose prerequisites are not yet satisfied is `PENDING`.

The aggregate state is:

- `COMPLETE` — every expectation is satisfied;
- `READY` — at least one missing expectation is an actionable `CREATE`;
- `BLOCKED` — nothing can be created now; remaining work is waiting on blockers or prerequisite closure.

Example empty-project frontier:

```text
DOMAIN        -> CREATE
ARCHITECTURE  -> PENDING on DOMAIN
VERIFICATION  -> PENDING on ARCHITECTURE
```

This prevents an agent from designing downstream knowledge before its accepted prerequisites exist.

## Meaning of COMPLETE

`COMPLETE` is structural design completeness for the declared profile:

- every required CapabilityId has an accepted canonical provider;
- each provider belongs to the expected Authority;
- all expectation prerequisites are satisfied;
- no required provider is blocked by an unresolved Question;
- the underlying Core model is structurally valid.

It is not proof that arbitrary document prose is semantically correct and it is not proof that the profile itself contains every expectation that a project should have.

During the current agent-driven phase, profile completeness remains an agent judgement supported by the `design-profile` skill and project-specific evidence.

## Empty projects

The target-state evaluator can operate once the project has a minimal Core graph containing the Authorities referenced by the profile.

Use prerequisite ordering so that only the first responsible knowledge frontier appears as `CREATE`. Downstream expectations remain `PENDING`.

Bootstrapping Authorities and creating resulting CanonicalArtifacts are agent responsibilities described by `skills/agent/bootstrap-existing-project/SKILL.md` and the artifact workbench.

## Design boundary

Design Profile is intentionally small. It does not prescribe:

- document templates or file paths;
- a universal artifact taxonomy;
- project stages or workflow status;
- implementation tasks;
- approval/readiness gates;
- semantic interpretation of arbitrary prose.

Starter profiles under `profiles/**` are reusable checklists, not universal proof that a selected target is complete. An agent must adapt them to the target repository and scope.
