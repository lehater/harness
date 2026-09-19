# Agent artifact workbench v0

Harness is currently an engineering control surface for an agent, not an autonomous project designer.

The agent owns judgement. Harness supplies explicit target knowledge, ownership, dependency ordering, typed artifact contracts and deterministic structural validation.

## Operating loop

```text
target task / scope
        ↓
choose or adapt Design Profile
        ↓
bootstrap smallest useful Core graph
        ↓
target_state
        ↓
CREATE / WAIT / PENDING / COMPLETE
        ↓
artifact skill for one CREATE
        ↓
candidate canonical knowledge
        ↓
schema validation
        ↓
semantic acceptance by the agent
        ↓
register CanonicalArtifact + provides + dependencies
        ↓
render human documentation
        ↓
target_state again
```

The agent must never treat `CREATE` as permission to invent missing product/domain decisions. `CREATE` means that the required knowledge has no accepted provider yet.

## Responsibilities

### Core and target state

Harness Core answers ownership, dependency, blocking and capability-provider questions.

Design Profile answers what engineering knowledge is required for the selected scope.

Expectation `depends_on` orders knowledge acquisition. A missing expectation is actionable as `CREATE` only after all prerequisite expectations are satisfied. Downstream missing knowledge is `PENDING`.

### Artifact skill

An artifact skill explains how an agent obtains one kind of engineering knowledge.

A skill owns judgement-heavy procedure:

- which canonical sources are relevant;
- what semantic questions must be answered;
- what contradictions or unknowns prevent acceptance;
- which typed schema represents the result;
- what evidence is required before registration.

A skill does not own target-project truth.

### Artifact schema

A schema validates the structural contract of a managed knowledge artifact.

Schema validity is necessary but not sufficient for semantic acceptance.

### Renderer

A renderer creates disposable human-readable documentation from accepted managed knowledge.

Generated documentation is never an independent source of truth.

## Candidate versus accepted artifact

The agent should draft a managed artifact as a candidate before registering it as a Core provider.

Use:

```sh
python workspace.py validate-artifact /path/to/candidate.yaml
```

This validates the artifact schema without declaring the capability provided.

Only after semantic acceptance should the agent:

1. place the artifact under `.harness/knowledge/**`;
2. register the corresponding `CanonicalArtifact` in `.harness/graph.yaml`;
3. add the accepted `CapabilityId` to `provides`;
4. record the canonical artifact dependencies actually used;
5. render `docs/generated/**`;
6. re-evaluate target state.

## Semantic acceptance

Before registering `provides`, the agent must establish all of the following:

1. **Authority** — the artifact belongs to the Authority named by the expectation.
2. **Capability fit** — the artifact actually answers the required knowledge capability rather than merely resembling the requested document type.
3. **Source discipline** — accepted statements are supported by canonical project sources, explicit user decisions, or deterministic derivation from them.
4. **No invention** — unresolved product/domain/architecture choices are not silently filled in.
5. **Conflict handling** — conflicting canonical evidence creates or preserves a Core `Question`; the affected artifact is not accepted as unblocked.
6. **Dependency closure** — every canonical artifact whose semantics the new artifact relies on is represented by `depends_on`.
7. **Schema validity** — the candidate passes its schema-specific validator.
8. **Scope discipline** — the artifact does not broaden the selected Design Profile scope merely to look complete.

Registration in the Core graph is the acceptance boundary. No separate workflow-state entity is introduced.

## Unknowns and Questions

When a skill cannot produce the requested knowledge without choosing an unresolved semantic fact:

- identify the Authority that may decide it;
- create a Core `Question` addressed to that Authority;
- block the affected artifact or downstream provider;
- do not fabricate an answer inside the candidate.

The final semantic answer belongs in an Authority-owned canonical artifact, not in the Question itself.

## Skill contract

Every artifact skill should state:

- **Trigger** — which kind of missing knowledge it handles;
- **Inputs** — expectation, Authority and prerequisite canonical artifacts;
- **Read boundary** — the minimum source set the agent should inspect;
- **Procedure** — how the knowledge is derived;
- **Stop conditions** — when the agent must create a Question instead of continuing;
- **Output schema** — the managed artifact schema;
- **Acceptance checks** — artifact-specific checks in addition to the common semantic acceptance rules;
- **Registration** — expected Core dependency/provides relationship;
- **Human projection** — what generated document the renderer produces.

Do not make skills generic document writers. Their purpose is to obtain trustworthy engineering knowledge.
