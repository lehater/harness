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
Harness-generated Decision Explorer Request when required
        ↓
isolated pre-choice Decision Exploration
        ↓
artifact producer forms candidate + governance disposition
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
Engineering Graph / Core / lifecycle / semantic / coverage read models
        ↓
Project Frontier
        ↓
READY action / FAILED_VALIDATION / BLOCKED / INCOMPLETE / WAITING / COMPLETE
        ↓
Capability action → Decision Pipeline + artifact skill
Coverage action   → owning coverage/reconciliation procedure
Question blocker  → owning Authority
        ↓
candidate → governance → validation → semantic acceptance → Core provider
        ↓
recompute source read models + Project Frontier
```

If the router returns `NO_KNOWLEDGE_KIND` or `NO_REGISTERED_SKILL`, the agent still has a valid CREATE frontier. It performs the work manually under the production contract or develops a reusable skill only when repeated consumer evidence justifies one.

## Coding handoff closure

`COMPLETE` from Target State proves structural knowledge availability only. Before handing a selected implementation scope to a coding agent, evaluate the derived implementation-design closure defined by the Integration Contract.

The handoff must fail closed when any applicable concern/subject remains non-terminal, a registered semantic claim lacks its deterministic validator evidence, an accepted requirement lacks verification disposition, a required TEST disposition lacks executable Test Design, a conditional architecture/repository precondition fails, or a blocking Question remains.

Do not persist a second readiness truth. The aggregate result is recomputed from canonical knowledge and validator results through `project_frontier.py`. Agents consume that projection rather than manually assigning precedence between Target State, Decision Roadmap, Semantic Closure and Engineering Coverage.
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
4. **Authority direction** — when the production contract requires machine-addressable source ownership, every source assertion identifies its owning Authority and only admitted upstream/same-Authority sources may justify the candidate. Restating or reconfirming a downstream decision does not promote it into upstream truth.
5. **No invention** — unresolved product/domain/architecture choices are not silently filled in.
6. **Decision diligence** — when the knowledge kind participates in Decision Governance, Harness first derives a pre-choice Decision Exploration Request. Option formation discovers materially distinct alternatives and then critically reviews the full decision space for mixed concerns, missing material cases, accepted-constraint conflicts and Authority-boundary mistakes before any choice. REDO/REVISION may read the current accepted provider as baseline; the future candidate/preselected solution remains forbidden. Choice may use only the reviewed alternative set; non-delegated or unresolved choices become blocking Core Questions.
7. **Conflict handling** — conflicting canonical evidence creates or preserves a Core `Question`; the affected artifact is not accepted as unblocked.
8. **Dependency closure** — every canonical artifact whose semantics the new artifact relies on is represented by `depends_on`.
9. **Structural validity** — the candidate passes its Harness schema validator or project-native deterministic validator.
10. **Scope discipline** — the artifact does not broaden the selected Design Profile scope merely to look complete.

Registration in the Core graph is the acceptance boundary. No separate workflow-state entity is introduced.

## Semantic completeness and automatic Questions

For knowledge kinds with machine-addressable semantic obligations, strict
admission evaluates the obligation surface before accepting the capability.

```text
knowledge-kind obligation
        ↓
assertion or explicit disposition
        ↓
missing / DEFERRED / QUESTION
        ↓
deterministic Core Question proposal
        ↓
owning Authority
        ↓
capability blocked
        ↓
canonical artifact revised
        ↓
admission + lifecycle revalidation
```

`NOT_APPLICABLE` closes an obligation only with explicit rationale.
`DEFERRED` and `QUESTION` remain open. Validation/process defects such as
missing review checks, invalid provenance or wrong Authority never become
Questions; the producing agent must fix those directly.

A project may extend a reusable knowledge-kind contract with a
`harness-knowledge-kind-semantic-overlay` when completeness depends on
project-specific semantics. The overlay adds obligations without creating a
second canonical product/domain truth.

Semantic closure projects generated Questions in memory before computing target
status, so a structurally present provider cannot preserve a misleading
`COMPLETE` result when its accepted semantic evaluation contains an open
obligation.

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
accepted acquisition scope
        ↓
source-set coverage relative to that scope
        ↓
selected immutable source baseline
        ↓
lossless source boundary / deterministic native item inventory
        ↓
covered source unit -> statement enumeration review
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

- **Source Set COMPLETE** proves every evidence channel required by an accepted acquisition contract was explicitly reviewed and met its minimum source-item requirement. The claim is relative to that contract; Harness does not claim open-world evidence completeness.
- **Source Boundary COMPLETE** proves every line/item in each selected immutable source entered a review unit exactly once; it does not interpret semantic meaning.
- **Statement Enumeration Review** checks one bounded source unit at a time so a material statement cannot disappear before the source ledger.
- **Source Coverage COMPLETE** proves no enumerated source statement disappeared silently during sanitization/classification. It does not by itself prove raw-source boundary completeness or that an ADMITTED rewrite/extracted semantic surface preserved every material clause.
- **Semantic Surface Admission** reviews each admitted canonical statement against the machine-addressable semantic atoms derived from it when those atoms will be used as the authoritative downstream derivation surface. Missing/weakened atoms are rejected before downstream derivation begins.
- **Structural COMPLETE** proves every declared capability/prerequisite has an accepted unblocked provider.
- **Semantic challenge PASS** proves an implementation consumer is not still forced to make a material upstream decision from the accepted closure.

None substitutes for another. Semantic Surface Admission is an assurance boundary composed from existing source coverage, semantic acceptance and semantic judgement mechanisms; it is not a new Core entity or workflow state.

For source-loss-sensitive work:
- establish the acquisition scope before claiming source closure; derive it from a project-owned canonical dependency/evidence graph when possible, otherwise from an accepted read-boundary/reconstruction protocol or explicit Authority/research decision;
- never report contract-relative `SOURCE_SET_COMPLETE` as proof that no unknown external evidence source exists;
- classify at statement granularity, not whole-file granularity;
- when admitted statements are decomposed into `semantic_assertions`, admit that statement -> atom transformation explicitly before using the atoms as a derivation baseline;
- split mixed source/design sentences when needed so observable constraints survive without importing prior solution choices;
- require an explicit exclusion rationale;
- treat a remaining classification/provenance QUESTION as source coverage INCOMPLETE;
- make a project-specific source-coverage capability a prerequisite of Product Requirements or the terminal consumer when the experiment requires blind/reconstruction assurance.

Use `skills/artifacts/source-coverage-audit/SKILL.md`, `source_set.py`, `source_boundary.py` and `source_coverage.py` for the reusable procedure/validators. The ledger is assurance evidence; admitted product/domain truth remains owned by its normal Authority artifacts.

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


## Sequential decision execution

Decision-governed production uses a single derived Capability frontier. For one
READY Capability the agent runs option formation, critical decision-space
review, choice/escalation, candidate production and semantic admission
sequentially. There is no Explorer/Producer execution-role handoff.

CURRENT work is omitted by default. Explicit redo may place a CURRENT
Capability back into the frontier without bypassing blockers or prerequisite
currentness. In REDO/REVISION, the current accepted provider is an allowed
baseline input to option formation; only the future candidate/preselected
solution remains forbidden.

After one Capability reaches CURRENT, BLOCKED or FAILED_VALIDATION, recompute
the frontier. See `docs/design/decision-pipeline-v0.md` and
`skills/agent/decision-pipeline/SKILL.md`.

## Mandatory strict admission for routed artifact skills

The prose skill contract is not itself evidence that the skill was obeyed.

For every production whose `knowledge_kind` is registered in
`skills/artifact-skill-registry-v0.yaml`, full engineering closure requires
strict semantic admission through `semantic_admission.py`.

The admission boundary composes:

1. the Engineering Graph production contract;
2. the derived Authority execution context;
3. canonical read/write provenance;
4. source-Authority direction derived from direct production prerequisites;
5. the knowledge-kind semantic-review contract;
6. the Harness-generated pre-choice Decision Exploration Request when the knowledge kind is decision-governed;
7. accepted option-formation evidence, including a COMPLETE decision-space review bound to that request;
8. accepted Decision Governance over exactly the reviewed decision/alternative set;
9. deterministic semantic acceptance;
10. a capability acceptance identity and exact prerequisite acceptance baseline.

A routed skill may not satisfy full closure merely because a file exists, a
schema validates, or a bare semantic evaluation is absent. Migration/static
evaluation may retain legacy provider behavior, but `semantic_closure.py`
fails closed for missing admission evidence.

Semantic review is intentionally used for rules that cannot be proven from
structure alone, such as whether Product Requirements stayed at observable
product level instead of importing a downstream Domain/Architecture choice.
The machine-enforced invariant is that this review is mandatory and that its
required checks are explicit.

Every active artifact skill is classified by
`spec/semantic-acceptance/skill-invariant-policy-v1.yaml` as either:

- `ENFORCED` through a routed knowledge-kind admission contract; or
- intentionally judgement-only/non-owning with an explicit rationale.

An unclassified active skill is a Harness validation failure.

## Semantic currentness

Accepted knowledge is not permanently current.

`capability_lifecycle.py` records one acceptance identity per selected
Capability and the exact prerequisite acceptance identities against which it was
accepted. If an upstream identity changes, the direct consumer becomes
`STALE` and is exposed as `REVALIDATE`; further downstream work remains
non-current until revalidation restores the chain.

`semantic_closure.py` requires both an ACCEPTED strict admission and CURRENT
lifecycle assertion for every capability in the selected Consumer closure.
Structural `COMPLETE` without those proofs is not full engineering closure.
