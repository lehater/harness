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
typed schema or project validator
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

## Existing-project policy and projection

Harness workspace files are optional integration structure, not mandatory ownership.

Before creating a new persistent Core graph, the agent must check whether the target repository already owns:

- a canonical artifact/dependency graph plus a compatible Harness projection;
- consumer/input contracts that declare required capabilities and Authorities;
- engineering completeness or subject-coverage policy.

When a compatible project-owned graph/projection exists, project it into Core in memory and preserve richer target-specific contracts. Do not create a second persistent `.harness/graph.yaml` merely to match Harness layout.

A Design Profile may be derived from several accepted project-owned policy sources. For example, a consumer contract may define which knowledge classes implementation needs while a completeness policy defines which bounded contexts must have tactical coverage. The selected scope is not COMPLETE until every applicable accepted policy is satisfied.

The `subject` field identifies the expectation but does not filter capability providers. If several same-Authority artifacts provide one broad capability for different subjects, subject-specific completeness requires subject-scoped CapabilityIds or a target-owned coverage check/profile. A broad capability alone must not be used as proof of per-subject coverage.

## Engineering Graph execution path

When the target project exposes an Engineering Graph, do not manually choose or maintain a Design Profile as the primary target policy.

Use:

```text
target Consumer
        ↓
Engineering Graph recursive closure
        ↓
derived Design Profile
        ↓
target state
        ↓
CREATE / WAIT / PENDING / COMPLETE
        ↓
agent_router for actionable CREATE
        ↓
grouped artifact work by Authority + subject + knowledge_kind
        ↓
registered artifact skill when available
        ↓
candidate → validation → semantic acceptance → Core provider
        ↓
reevaluate target Consumer
        ↓
when structurally COMPLETE, evaluate Engineering Coverage + applicable project validators
        ↓
claim implementation-documentation closure only when the derived conjunction passes
```

If the router returns `NO_KNOWLEDGE_KIND` or `NO_REGISTERED_SKILL`, the agent still has a valid CREATE frontier. It performs the work manually under the production contract or develops a reusable skill only when repeated consumer evidence justifies one.

## Coding handoff closure

`COMPLETE` from Target State proves structural knowledge availability only. Before handing a selected implementation scope to a coding agent, evaluate the derived implementation-design closure defined by the Integration Contract.

The handoff must fail closed when any applicable concern/subject remains non-terminal, a registered semantic claim lacks its deterministic validator evidence, an accepted requirement lacks verification disposition, a required TEST disposition lacks executable Test Design, a conditional architecture/repository precondition fails, or a blocking Question remains.

Do not persist a second readiness truth. The aggregate result is recomputed from canonical knowledge and validator results.
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
- which output contract represents the result;
- what evidence is required before registration.

A skill does not own target-project truth.

### Artifact contract

An artifact skill may produce either:

- a Harness-managed knowledge artifact with a typed Harness schema; or
- a project-native canonical artifact with a deterministic project validator.

Use a Harness schema when the knowledge has a stable reusable semantic shape such as a Domain Model or Verification Strategy.

Prefer a project-native artifact when the canonical result is large target-specific data, code-generation input, source registry or another format already owned naturally by the target repository.

Do not force project-specific data into a generic Harness DSL merely so every skill has a Harness schema.

Structural validation is necessary but not sufficient for semantic acceptance.

### Renderer

A renderer creates disposable human-readable documentation from accepted managed knowledge.

Generated documentation is never an independent source of truth.

## Candidate versus accepted artifact

The agent should draft an artifact as a candidate before registering it as a Core provider.

A target repository may use `.harness/candidates/**` as a disposable agent workbench. Files there are explicitly non-canonical:

- they are not Core `CanonicalArtifact` entries merely because they exist;
- they do not provide capabilities;
- managed-workspace validation/rendering ignores them;
- they may be partial or structurally valid while semantic acceptance is still pending;
- they should be deleted or moved to the project-native canonical location when the experiment is over.

This is a filesystem convention for the agent layer, not a new Core entity or workflow state.

For Harness-managed YAML, use:

```sh
python workspace.py validate-artifact /path/to/candidate.yaml
```

For project-native artifacts, run the target repository's deterministic validator against the exact required source/coverage contract.

Neither form of validation declares the capability provided.

Only after semantic acceptance should the agent:

1. move a Harness-managed artifact under `.harness/knowledge/**`, or place a project-native artifact at its target repository canonical path;
2. register the corresponding `CanonicalArtifact` in the active Core ownership projection: `.harness/graph.yaml` for a Harness-managed workspace, or the target repository's compatible project-owned graph/projection when that is the existing owner;
3. add the accepted `CapabilityId` to `provides`;
4. record the canonical artifact dependencies actually used;
5. render `docs/generated/**` only for Harness-managed artifacts that have a renderer;
6. re-evaluate target state.

## Semantic acceptance

Before registering `provides`, the agent must establish all of the following:

1. **Authority** — the artifact belongs to the Authority named by the expectation.
2. **Capability fit** — the artifact actually answers the required knowledge capability rather than merely resembling the requested document type.
3. **Source discipline** — accepted statements are supported by canonical project sources, explicit user decisions, or deterministic derivation from them.
4. **No invention** — unresolved product/domain/architecture choices are not silently filled in.
5. **Conflict handling** — conflicting canonical evidence creates or preserves a Core `Question`; the affected artifact is not accepted as unblocked.
6. **Dependency closure** — every canonical artifact whose semantics the new artifact relies on is represented by `depends_on`.
7. **Structural validity** — the candidate passes its Harness schema validator or project-native deterministic validator.
8. **Scope discipline** — the artifact does not broaden the selected Design Profile scope merely to look complete.

Registration in the Core graph is the acceptance boundary. No separate workflow-state entity is introduced.

## Unknowns and Questions

When a skill cannot produce the requested knowledge without choosing an unresolved semantic fact:

- identify the Authority that may decide it;
- create a Core `Question` addressed to that Authority;
- when an affected provider already exists, block that artifact with `blocks`;
- when the required provider does not yet exist, block the missing `CapabilityId` with `blocks_capabilities`;
- do not fabricate an answer inside the candidate.

The final semantic answer belongs in an Authority-owned canonical artifact, not in the Question itself. Resolving a capability-blocking Question does not itself provide the capability: after resolution, target state normally returns `CREATE` so the artifact skill can form the requested knowledge from the accepted decision.

## Reconstruction and blind source coverage

Structural target closure cannot detect source truth that disappeared **before** the Engineering Graph was formed.

For reconstruction/blind work where original source material is sanitized, filtered or separated from prior derived design, use a statement-level source-coverage artifact before claiming semantic readiness.

The assurance path is:

```text
original independently evidenced source
        ↓
statement-level source ledger
        ↓
exact-one disposition for every statement
        ↓
SOURCE COVERAGE COMPLETE
        ↓
Engineering Graph / Core structural closure
        ↓
IMPLEMENTATION STRUCTURAL COMPLETE
        ↓
coding-agent semantic challenge
        ↓
RECONSTRUCTION-READY
```

These gates are independent:

- **Source Coverage COMPLETE** proves no enumerated source statement disappeared silently during sanitization/classification.
- **Structural COMPLETE** proves every declared capability/prerequisite has an accepted unblocked provider.
- **Semantic challenge PASS** proves an implementation consumer is not still forced to make a material upstream decision from the accepted closure.

None substitutes for another.

For source-loss-sensitive work:
- classify at statement granularity, not whole-file granularity;
- split mixed source/design sentences when needed so observable constraints survive without importing prior solution choices;
- require an explicit exclusion rationale;
- treat a remaining classification/provenance QUESTION as source coverage INCOMPLETE;
- make a project-specific source-coverage capability a prerequisite of Product Requirements or the terminal consumer when the experiment requires blind/reconstruction assurance.

Use `skills/artifacts/source-coverage-audit/SKILL.md` and `source_coverage.py` for the reusable procedure/validator. The ledger is assurance evidence; admitted product/domain truth remains owned by its normal Authority artifacts.

## Implementation feedback

A `COMPLETE` Design Profile means that the declared knowledge is structurally available and unblocked at that moment. It is not proof that product code already implements that knowledge.

Classify implementation feedback before changing Harness state.

### Missing semantic decision

When implementation exposes a semantic case that the accepted provider does not actually decide:

1. stop only the affected implementation slice;
2. identify the highest owning Authority;
3. create a Core `Question` blocking the affected canonical provider, or the missing capability when no provider exists;
4. re-evaluate target state;
5. expect previously downstream expectations to become `WAIT` / `PENDING`;
6. resolve the Question only through Authority-owned canonical truth;
7. re-evaluate and resume implementation when the required knowledge is unblocked.

```text
COMPLETE
→ implementation discovers real semantic gap
→ Question
→ BLOCKED / WAIT
→ canonical decision
→ refined COMPLETE
→ resume implementation
```

### Implementation or evidence lag

When accepted canonical knowledge already decides the behavior, but current code, tests or other executable evidence do not yet realize/prove it:

- do **not** create a Core Question;
- do **not** add another Design Profile expectation for the same decision;
- keep the design target state `COMPLETE`;
- treat the finding as implementation or verification-evidence work under the target repository's own authorization and CI rules;
- use implementation findings only as evidence that the realization is incomplete, never as a reason to rewrite accepted semantic truth to match current code.

```text
COMPLETE
→ implementation/evidence does not match accepted knowledge
→ COMPLETE remains
→ authorized implementation / verification work
→ executable evidence catches up
```

This distinction prevents Harness from becoming an implementation-status or workflow engine.

Do not preserve a green `COMPLETE` state by silently choosing an implementation convention for an unresolved domain/architecture decision. Equally, do not manufacture a semantic Question merely because implementation lags behind already accepted knowledge.

## Skill contract

Every artifact skill should state:

- **Trigger** — which kind of missing knowledge it handles;
- **Inputs** — expectation, Authority and prerequisite canonical artifacts;
- **Read boundary** — the minimum source set the agent should inspect;
- **Procedure** — how the knowledge is derived;
- **Stop conditions** — when the agent must create a Question instead of continuing;
- **Output contract** — either the managed artifact schema or the project-native format and deterministic validator;
- **Acceptance checks** — artifact-specific checks in addition to the common semantic acceptance rules;
- **Registration** — expected Core dependency/provides relationship;
- **Human projection** — what generated document the renderer produces.

Do not make skills generic document writers. Their purpose is to obtain trustworthy engineering knowledge.
