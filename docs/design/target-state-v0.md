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
```

Each expectation means:

- `subject` — the scope/entity for which knowledge is required;
- `capability` — the required engineering knowledge identifier;
- `authority` — the Authority that must own the canonical provider;
- `id` — stable identifier for the expectation.

The profile declares required knowledge, not where or how that knowledge must be documented.

## Evaluation

`target_state.py PROFILE MODEL` evaluates the declared target state against a normal Core v0 model.

For every expectation:

1. no canonical provider for the capability -> `CREATE`;
2. provider exists under another Authority -> invalid profile/model combination;
3. provider exists but is transitively blocked by unresolved Questions -> `WAIT`;
4. provider exists under the expected Authority and is not blocked -> satisfied.

The aggregate state is:

- `COMPLETE` — every expectation is satisfied;
- `READY` — at least one missing expectation can be created now;
- `BLOCKED` — no expectation can advance because the remaining providers are blocked.

## Meaning of COMPLETE

`COMPLETE` is structural design completeness for the declared profile:

- every required CapabilityId has an accepted canonical provider;
- each provider belongs to the expected Authority;
- no required provider is blocked by an unresolved Question;
- the underlying Core model is structurally valid.

It is not proof that arbitrary document prose is semantically correct. A future artifact workbench must validate artifact-specific content before declaring a CapabilityId as provided by a canonical artifact.

## Empty projects

The target-state evaluator can operate once the project has a minimal Core graph containing the Authorities referenced by the profile. Missing capabilities then appear as `CREATE` actions.

Bootstrapping Authorities and creating the resulting CanonicalArtifacts are separate responsibilities and are not part of this contract.

## Design boundary

Design Profile is intentionally small. It does not prescribe:

- document templates or file paths;
- a universal artifact taxonomy;
- project stages or workflow status;
- implementation tasks;
- approval/readiness gates;
- semantic interpretation of arbitrary prose.

Those concerns should be added only when a concrete consumer scenario demonstrates that the current contract is insufficient.
