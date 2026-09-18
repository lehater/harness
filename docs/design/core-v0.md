# Harness Core v0

Harness Core manages boundaries of engineering knowledge and decision ownership. It does not model work stages, human/agent roles, tasks, gates, approvals, handoffs or a workflow state machine.

## Entities

- **Authority** — one semantic ownership boundary for canonical engineering decisions.
- **CanonicalArtifact** — one addressable source of accepted truth, owned by exactly one Authority.
- **CapabilityId** — a value identifier for knowledge/capability provided by canonical artifacts. Multiple providers are allowed only inside one Authority.
- **Question** — a material unresolved semantic gap addressed to the Authority allowed to decide it.

A Question contains no final semantic answer. Resolution means the addressed Authority changed canonical truth and the Question now references the canonical artifact containing that decision.

## Relations

- Authority owns CanonicalArtifact.
- CanonicalArtifact provides CapabilityId.
- CanonicalArtifact may `depends_on` other CanonicalArtifact IDs.
- Question is addressed to one Authority.
- An unresolved Question may `blocks` downstream artifacts.
- A resolved Question has `resolution: <artifact-id>` and that artifact must belong to the addressed Authority.

## Project model

A target project may declare Core data as YAML:

```yaml
authorities:
  - id: DOMAIN
artifacts:
  - id: DOMAIN-MODEL
    authority: DOMAIN
    path: docs/domain.yaml
    provides: [domain.example]
    depends_on: []
questions:
  - id: Q-1
    authority: DOMAIN
    text: What semantic choice remains unresolved?
    blocks: [DOWNSTREAM]
```

`path` addresses the project-owned canonical source. Harness owns only structural interpretation of this declaration; the target repository remains authoritative for the artifact contents.

## Derived operations

`harness.py` provides:

- `validate MODEL`
- `affected MODEL ARTIFACT`
- `questions MODEL [--authority AUTHORITY]`
- `resolve MODEL CAPABILITY_ID`
- `owner MODEL CAPABILITY_ID`
- `blocked MODEL ARTIFACT`
- `resolve-question MODEL QUESTION ARTIFACT [--write]`

Core validates declared ownership, references, dependencies and capability ownership. It does not interpret arbitrary artifact semantics.
