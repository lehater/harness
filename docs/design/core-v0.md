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


## Pilot evidence

Core v0 has been exercised against two independent target repositories.

### Pilot 1 — NAPMS

A real Application Communication Catalogue change enforced the already-canonical invariant that one directed Component pair may have at most one Interaction inside one Application Definition.

The pilot confirmed that Core can:

- locate the semantic owner and canonical providers through CapabilityId;
- separate semantic, persistence, runtime and verification capabilities without inventing workflow state;
- use `affected` to identify potential downstream impact;
- leave `Question` absent when upstream semantics are already sufficient.

The consumer issues discovered during the pilot were CI/integration problems in NAPMS, not missing Core concepts.

### Pilot 2 — Nutrition Management

A draft BLS 4.0 Food Knowledge implementation exposed a real semantic gap around source-value precision/provenance and also revealed disagreement between accepted ADRs and living domain artifacts.

The pilot confirmed that Core can:

- address the unresolved semantic question to the Food Knowledge Authority;
- block the XLSX normalization boundary and downstream verification while the question is unresolved;
- resolve the question only by changing an artifact owned by that Authority;
- remove the downstream block after canonical truth is repaired;
- continue implementation without introducing Stage, Gate, Approval, Handoff or workflow machinery.

The canonical repair merged through the target repository's normal PR/CI path, and the synchronized downstream implementation remained green. No Core behavior change was required.

### Current conclusion

The two pilots do not justify a Core v0.1 model extension.

Observed usage guidance:

- `Question` is exceptional, not a mandatory work item.
- `affected` is a dependency-impact closure, not a mandatory file-change list.
- target repositories remain authoritative for semantic and dependency truth; a Core model should project existing project truth rather than create a second canonical graph.
- Git branch synchronization, CI configuration and other delivery mechanics remain outside Core.
- a future Core extension still requires a concrete consumer failure and an acceptance fixture reproducing it before behavior changes.

Still unproven are consumer ergonomics for deriving/projecting Core declarations from existing repository metadata and whether additional consumers expose a structural case that the current four entities cannot express. These are validation targets, not new Core concepts.
