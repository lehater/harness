# Harness Evolution Radar

Status: active non-defect evolution ledger.

Purpose: preserve potentially useful directions, recommendations and research
questions without turning them into defects or mandatory backlog work.

This file is deliberately separate from
`docs/audit/harness-audit-backlog.md`.

Classification and routing rules are canonicalized in `docs/audit/README.md`.

## Classification

### Types

- `RECOMMENDATION` — there is already reasonable evidence that the direction
  would improve Harness, but adopting it is optional.
- `RESEARCH` — the question needs an experiment, comparison or additional
  project evidence before a design choice should be made.
- `IDEA` — a potentially useful hypothesis with insufficient evidence yet.

### Statuses

- `CAPTURED` — recorded so it is not lost.
- `INVESTIGATING` — active research or experiment exists.
- `VALIDATED` — evidence supports the direction; adoption is still optional.
- `ADOPTED` — promoted into an architecture/specification/implementation
  decision.
- `PARKED` — intentionally postponed until a stated precondition is met.
- `REJECTED` — evidence showed the idea should not be pursued.

## Boundary with defects and decisions

Use these three ledgers differently:

```text
Audit Backlog
  = something is demonstrably wrong now

Evolution Radar
  = something might make Harness better

ADR / canonical spec
  = Harness has decided to adopt a direction
```

A Radar item may later:

- reveal a real defect -> create/reuse a `HARN-*` item and link it;
- become an accepted design -> move the normative content into an ADR/spec and
  mark the Radar item `ADOPTED`;
- remain useful but non-urgent -> `PARKED`;
- fail its experiment -> `REJECTED`.

Do not change a `HARN-*` severity merely because a related improvement idea
exists here. Do not describe an `EVO-*` item as technical debt unless a
separate defect has been demonstrated.

## Current radar

| ID | Type | Status | Area | Direction |
|---|---|---|---|---|
| EVO-001 | RECOMMENDATION | VALIDATED | Skill engineering | Add behavioral execution evals for important Harness skills. |
| EVO-002 | RECOMMENDATION | VALIDATED | Skill engineering | Define a common Harness skill anatomy with explicit applicability, procedure and verification evidence. |
| EVO-003 | RESEARCH | CAPTURED | DDD / skills | Evaluate a distinct Method / Procedure Library boundary for reusable engineering methods. |
| EVO-004 | RECOMMENDATION | VALIDATED | Routing | Preserve deterministic routing for artifact-production skills; use intent/trigger routing only where work is genuinely selected from natural language. |
| EVO-005 | RECOMMENDATION | CAPTURED | Context engineering | Make progressive disclosure and minimal-context loading an explicit Harness skill-design principle. |
| EVO-006 | RECOMMENDATION | CAPTURED | Skill composition | Prefer cross-skill composition over copying shared procedures into many skills. |
| EVO-007 | RECOMMENDATION | CAPTURED | Portability | Keep reusable skills model-neutral and describe capabilities/procedures rather than runtime-specific workarounds. |
| EVO-008 | IDEA | CAPTURED | Agent reliability | Add Red Flags / anti-rationalization guidance selectively to judgement-heavy skills. |
| EVO-009 | RESEARCH | INVESTIGATING | Application model | Explore one derived CapabilityState read model that composes structural, blocker, admission, currentness and applicability dimensions. |
| EVO-010 | RESEARCH | INVESTIGATING | Application layer | Explore one canonical transition/process-manager boundary for applying an execution outcome coherently across Core, evaluations, lifecycle and Questions. |
| EVO-011 | RESEARCH | CAPTURED | DDD boundaries | Introduce stable published read models/contracts between bounded contexts instead of importing another context's internal data structures. |
| EVO-012 | RESEARCH | CAPTURED | Reference model | Define evidence-based promotion criteria for the Reference Engineering Model using materially different real projects. |
| EVO-013 | RECOMMENDATION | PARKED | Physical architecture | Move runtime modules into packages matching bounded contexts only after logical boundaries and dependency direction are stable. |
| EVO-014 | RECOMMENDATION | ADOPTED | Architecture governance | Maintain a machine-readable bounded-context map plus architecture ratchet. |
| EVO-015 | RESEARCH | CAPTURED | Skill compatibility | Evaluate compatibility with the broader Agent Skills conventions without making Harness depend on one agent/runtime. |
| EVO-016 | IDEA | CAPTURED | External methods | Allow Harness application orchestration to consume external Agent-Skill-like engineering procedures without making them project truth. |
| EVO-017 | RESEARCH | CAPTURED | Skill evaluation | Split skill quality measurement into structural, routing and behavioral tiers appropriate to Harness semantics. |
| EVO-018 | RECOMMENDATION | CAPTURED | Skill identity | Treat published skill names/identities as compatibility contracts and require explicit alias/migration handling when renamed. |
| EVO-019 | RESEARCH | CAPTURED | Reference vs Coverage | Test the target ownership rule: Coverage proves completeness, Reference Model proposes reusable realizations, Project Model owns the accepted project graph. |
| EVO-020 | IDEA | CAPTURED | Context lifecycle | Define restartable agent-session boundaries from durable project artifacts so long-running work can resume without conversation history becoming project truth. |
| EVO-021 | RECOMMENDATION | ADOPTED | Instruction architecture | Standardize the ownership chain: AGENTS bootstrap/invariants -> router -> task skill -> canonical policy/spec. |
| EVO-022 | RESEARCH | ADOPTED | Agent routing | Add an explicit registry/router and overlap tests for `skills/agent/**`; keep artifact routing deterministic by `knowledge_kind`. |
| EVO-023 | RECOMMENDATION | ADOPTED | Root instructions | Shrink `AGENTS.md` to always-on invariants, bootstrap/routing rules and minimal navigation; remove task-specific workflows from it. |
| EVO-024 | RESEARCH | PARKED | Artifact skills | Pilot a common artifact-production procedure so artifact skills carry domain-specific deltas instead of repeating generic registration/projection/acceptance mechanics. |
| EVO-025 | RECOMMENDATION | ADOPTED | Skill lifecycle | Quarantine or migrate inactive pre-Core `SKILL.md` files so discovery surfaces expose only active skills. |
| EVO-026 | RECOMMENDATION | ADOPTED | Documentation ownership | Keep README/workbench documents descriptive or semantic-contract oriented; task execution procedures should route into skills instead of being independently maintained in several prose files. |
| EVO-027 | RESEARCH | ADOPTED | Method/analysis routing | Give non-owning `judgement_only` analysis skills an explicit routing surface, likely outside the artifact-production registry. |
| EVO-028 | RECOMMENDATION | ADOPTED | Skill distribution | Separate Maintainer and Consumer skill surfaces; distribute the Consumer surface as a pinned locally materialized pack rather than copied project skills. |
| EVO-029 | RESEARCH | CAPTURED | Conditional producer promotion | Decide when the research CHANGE-TRANSITION-DESIGN contract is mature enough to receive a canonical `knowledge_kind` and deterministic artifact-production route. |

## Detailed entries

### EVO-001 — Behavioral execution evals for skills

**Type:** RECOMMENDATION  
**Status:** VALIDATED

**Direction**

Add real-agent behavioral tests for important Harness skills. A test should run a
skill against a controlled fixture and grade the observable artifact/execution
trace against explicit expectations.

Example:

```text
fixture Problem Evidence
+ product-requirements SKILL
+ mixed observable requirement / architecture choice
        ↓
agent execution
        ↓
expect:
  observable constraint preserved
  architecture choice not promoted upstream
  unresolved product choice becomes Question
```

**Why useful**

Current deterministic validators can prove schemas, state transitions and
machine-enforced contracts, but they cannot prove that an agent reading a
`SKILL.md` actually follows its judgement procedure.

**Evidence**

The public `addyosmani/agent-skills` repository uses structural, routing and
behavioral skill evals. Harness already has Scenario Suite infrastructure that
can provide the project-specific side of this idea.

**Not a defect**

Harness may remain functionally correct without agent-execution evals. This is
additional assurance over procedure quality.

**Related**

- `spec/scenario-suite/**`
- `skill_invariant_policy.py`
- EVO-017

---

### EVO-002 — Common Harness skill anatomy

**Type:** RECOMMENDATION  
**Status:** VALIDATED

**Direction**

Define a light common contract for active Harness skills. Preserve the useful
Harness-specific structure rather than copying another repository literally.

Candidate fields/sections:

```text
name + stable identity
what / when
when NOT to use
inputs
read boundary
procedure
stop/escalation conditions
output contract
verification evidence
registration/side effects
optional red flags
```

Artifact-production skills may additionally declare the knowledge kind and
semantic acceptance expectations.

**Why useful**

Harness skills are already structured, but the structure varies. A common
anatomy makes skills easier to validate, compare, compose and behavior-test.

**Not a defect**

Existing skills can be valid without identical headings.

**Related**

- `skills/artifacts/**`
- `skills/agent/**`
- EVO-008
- EVO-018

---

### EVO-003 — Method / Procedure Library boundary

**Type:** RESEARCH  
**Status:** CAPTURED

**Question**

Should reusable methods such as TDD, debugging, code review, source-driven
development and context engineering form a distinct supporting/generic
`Method / Procedure Library` boundary, separate from Harness
artifact-production skills?

Candidate distinction:

```text
Artifact Production Skill
  = how to produce one kind of accepted engineering knowledge

Engineering Method Skill
  = reusable procedure used while doing many kinds of work
```

**Potential value**

It would prevent `skills/artifacts/**` from becoming a repository-wide home
for every engineering practice and make external method packs composable.

**Evidence needed**

Pilot at least two methods reused by several artifact/application workflows and
show that the separation reduces duplication/context without creating another
orchestration layer.

**Not a defect**

Harness currently works with one skill tree.

---

### EVO-004 — Deterministic artifact-skill routing

**Type:** RECOMMENDATION  
**Status:** VALIDATED

**Direction**

Keep artifact-production routing explicit:

```text
Capability
  -> knowledge_kind
  -> artifact-skill-registry
  -> SKILL.md
```

Do not replace this with lexical/natural-language skill discovery.

Natural-language trigger/routing evaluation is useful only for application/meta
skills whose applicability is genuinely inferred from user intent.

**Why useful**

This preserves one of Harness's advantages over generic skill packs: the project
model determines which engineering knowledge is required.

**Not a defect**

This records a design direction to preserve rather than a current failure.

**Related**

- `skills/artifact-skill-registry-v0.yaml`
- `agent_router.py`
- EVO-017

---

### EVO-005 — Progressive disclosure and context budget

**Type:** RECOMMENDATION  
**Status:** CAPTURED

**Direction**

Make minimal-context loading a first-class skill-design principle:

1. keep only skill identity/description available for discovery;
2. load full procedure only when selected;
3. load supporting references only when the procedure reaches them;
4. prefer machine execution/results over embedding large reference material;
5. persist conclusions and accepted state rather than conversation history.

**Why useful**

This reinforces Harness's Authority Context and clean-context goals while
reducing stale-context influence.

**Evidence needed**

Measure context size and behavioral quality on a representative long workflow
before and after progressive loading.

**Not a defect**

This is an efficiency/reliability improvement.

**Related**

- `authority_context.py`
- EVO-020

---

### EVO-006 — Cross-skill composition instead of duplication

**Type:** RECOMMENDATION  
**Status:** CAPTURED

**Direction**

When several skills need the same reusable procedure, reference/compose one
method skill or shared contract instead of copying the same instructions into
each `SKILL.md`.

Composition must not create hidden mandatory dependencies: each dependency
should be explicit and versionable.

**Why useful**

Reduces drift between artifact skills and keeps each procedure small.

**Not a defect**

Some duplication can be acceptable when it improves self-containment; this is a
default preference, not a universal prohibition.

---

### EVO-007 — Model-neutral reusable skills

**Type:** RECOMMENDATION  
**Status:** CAPTURED

**Direction**

Write reusable procedures in terms of required capabilities and observable
evidence, not quirks of a particular model version or private tool command.

Runtime adapters may translate a generic step into Codex/Claude/etc. mechanics.

**Why useful**

Avoids overfitting Harness methodology to temporary model failures and improves
portability.

**Not a defect**

Runtime-specific skills can still be appropriate when the runtime itself is the
subject of the procedure.

---

### EVO-008 — Red Flags and anti-rationalization guidance

**Type:** IDEA  
**Status:** CAPTURED

**Direction**

For judgement-heavy skills, consider explicit observable failure patterns such
as:

- inventing missing semantics instead of opening a Question;
- reading outside the Authority boundary "for context";
- treating implementation behavior as upstream requirement evidence;
- skipping verification because the artifact looks plausible.

Use this selectively. Do not add repetitive motivational prose to deterministic
skills.

**Evidence needed**

Behavioral evals should show that these sections reduce real failure modes
before they become a repository-wide convention.

**Not a defect**

This is prompt/procedure hardening.

---

### EVO-009 — Unified CapabilityState read model

**Type:** RESEARCH  
**Status:** INVESTIGATING

**Question**

Would one derived, non-canonical read model make cross-layer behavior easier to
reason about?

Candidate dimensions:

```text
applicability: REQUIRED | NOT_APPLICABLE | UNKNOWN
provider:      MISSING | PRESENT
blocker:       NONE | QUESTION
admission:     UNKNOWN | REJECTED | ACCEPTED
currentness:   UNKNOWN | STALE | CURRENT
```

Application actions could then be derived from the tuple instead of each
subsystem publishing a partially overlapping frontier.

**Important constraint**

This must be a derived Application read model, not a new source of project
truth.

**Why research**

It may simplify HARN-007, but it could also merely centralize complexity without
removing it.

**Related defects**

- HARN-007
- HARN-004
- HARN-015

---

### EVO-010 — Canonical application transition boundary

**Type:** RESEARCH  
**Status:** INVESTIGATING

**Question**

Should the Application Layer expose one transition boundary of the form:

```text
current published project state
+ execution outcome/evidence
        ↓
validated coherent next published state
```

The transition would coordinate Core realization changes, current semantic
evaluation, lifecycle assertion and Question resolution without making the
Application Layer an owner of those facts.

**Potential value**

Reduces partial-persistence states and makes retries/replay explicit.

**Important constraint**

Each bounded context still validates/owns its own invariant. The transition is
coordination, not a mega-aggregate.

**Related defects**

- HARN-012
- HARN-006
- HARN-009
- HARN-015

---

### EVO-011 — Published cross-context read models

**Type:** RESEARCH  
**Status:** CAPTURED

**Direction**

Replace direct reads of another bounded context's internal representation with a
small published contract where the dependency is stable.

Likely candidates:

- Knowledge Assurance -> Coverage;
- Integration -> Project Model;
- Coverage -> Application;
- Decision Governance -> Application request builder.

**Why useful**

Makes the DDD boundaries semantic rather than merely package names and should
make later physical restructuring mechanical.

**Evidence needed**

Extract one boundary and show reduced coupling without duplicating truth.

**Related**

- `docs/audit/harness-ddd-context-map.md`
- HARN-016

---

### EVO-012 — Reference Engineering Model promotion criteria

**Type:** RESEARCH  
**Status:** CAPTURED

**Question**

What evidence is required before the current research Reference Engineering
Model becomes a canonical reusable layer?

Candidate criteria:

- materially different real-project archetypes;
- stable Authority/Capability-template identities;
- fail-closed applicability behavior;
- explicit migration semantics for rename/split/merge;
- demonstrated reduction in omitted engineering knowledge;
- no project-specific branches inside reusable materialization logic.

**Not a defect**

The Reference Model is intentionally research today.

**Related**

- EVO-019
- HARN-008
- HARN-014

---

### EVO-013 — Physical packages by bounded context

**Type:** RECOMMENDATION  
**Status:** PARKED

**Direction**

Eventually reorganize runtime modules toward a package shape such as:

```text
src/harness/
  project_model/
  coverage/
  assurance/
  reference_model/
  decision/
  evidence/
  integration/
  workspace/
  application/
```

**Precondition**

Do not perform this while context ownership and dependency direction are still
changing. First remove or explicitly decide the logical boundary violations.

**Why parked**

A package move now would mostly relocate the same coupling and create migration
noise.

**Related**

- HARN-016
- EVO-011

---

### EVO-014 — Architecture context-map ratchet

**Type:** RECOMMENDATION  
**Status:** ADOPTED

**Decision already implemented on audit branch**

Harness now has:

- `spec/architecture/harness-context-map-v0.yaml`;
- `validators/validate_context_boundaries.py`;
- `docs/audit/harness-ddd-context-map.md`.

The validator rejects new undeclared context dependency violations and also
forces removal of stale exceptions after a violation is fixed.

**Why keep an ADOPTED entry**

The Radar records where an improvement idea went. Normative content remains in
the architecture files, not here.

---

### EVO-015 — Compatibility with Agent Skills conventions

**Type:** RESEARCH  
**Status:** CAPTURED

**Question**

Which parts of the emerging/general Agent Skills conventions can Harness adopt
without coupling itself to one runtime or replacing Harness-specific semantics?

Areas worth comparing:

- `SKILL.md` metadata/anatomy;
- self-contained supporting references/scripts;
- stable skill naming;
- progressive disclosure;
- behavioral eval fixture format;
- distribution/installation conventions.

**Boundary**

Harness-specific concepts such as Authority, Capability, semantic admission and
lifecycle must remain Harness domain concepts rather than being forced into a
generic skill format.

---

### EVO-016 — External engineering-method packs

**Type:** IDEA  
**Status:** CAPTURED

**Direction**

Explore whether the Application/Procedure layer can invoke externally supplied
method skills, for example TDD or code review, while keeping:

- project truth in Harness/project canonical artifacts;
- deterministic Harness capability routing;
- external procedures non-authoritative;
- explicit compatibility/version boundaries.

Conceptually:

```text
Harness determines WHAT knowledge/action is admissible
        ↓
Procedure Library determines HOW to execute a reusable method
        ↓
Harness validates resulting evidence/state
```

**Not a defect**

Harness does not need external packs to operate.

---

### EVO-017 — Three-tier skill quality model

**Type:** RESEARCH  
**Status:** CAPTURED

**Direction**

Adapt the useful separation seen in Agent Skills:

1. **Structural** — metadata, references, policy classification, required
   sections/contracts.
2. **Routing** — only for intent-routed skills; verify positive/negative
   applicability and collisions.
3. **Behavioral** — run an agent over controlled fixtures and grade observable
   behavior/evidence.

For deterministic artifact skills, Tier 2 should validate registry ownership,
not lexical similarity.

**Potential mapping**

```text
Harness existing:
  skill_invariant_policy -> much of Tier 1
  artifact-skill-registry -> deterministic routing
  Scenario Suite -> cross-layer behavioral substrate

Missing:
  agent-execution behavioral tests of individual procedures
```

**Related**

- EVO-001
- EVO-004

---

### EVO-018 — Stable skill identity and migration

**Type:** RECOMMENDATION  
**Status:** CAPTURED

**Direction**

Treat a published skill name referenced by registries, other skills, external
projects or evals as a compatibility identifier.

A rename should use an explicit alias/migration rule rather than silently
breaking references.

**Why useful**

As Harness skills become reusable across repositories, skill identity becomes
part of the integration surface.

**Not a defect**

Current repository-local renames may still be manageable mechanically.

---

### EVO-019 — Reference Model / Coverage ownership experiment

**Type:** RESEARCH  
**Status:** CAPTURED

**Hypothesis**

The clean ownership rule is:

```text
Engineering Coverage
  owns: is the selected scope sufficiently covered?

Reference Engineering Model
  owns: which reusable Capability Templates can realize required knowledge
        from accepted facts/concerns?

Project Model
  owns: which concrete Engineering Graph is accepted for this project?
```

**Experiment**

Apply this rule to at least:

- a small greenfield service;
- a mature project with an existing canonical graph;
- a project where several reference Authorities are legitimately N/A;
- a project requiring project-specific Authorities/capabilities.

Measure whether any context must duplicate another context's truth to complete
the loop.

**Possible outcomes**

- validated -> promote the ownership relationship to canonical architecture;
- fails -> refine the boundaries before promoting Reference Model;
- exposes false completeness -> link/create a HARN defect.

**Related**

- HARN-008
- EVO-012

---

### EVO-020 — Restartable agent-session boundaries

**Type:** IDEA  
**Status:** CAPTURED

**Direction**

Define what must be persisted at a safe session/task boundary so a fresh agent
context can continue without relying on chat history:

- accepted scope/decision artifacts;
- current capability/action state;
- repository/working-tree state;
- verification evidence;
- unresolved Questions;
- required approvals.

Harness durable project state should remain the source of truth; conversation
summaries are convenience only.

**Why useful**

Supports long-running agent work and the clean-context principle without adding
conversation memory to the domain model.

**Not a defect**

Current sessions can operate without formal restart contracts.

**Related**

- EVO-005
- EVO-010

## Intake protocol

When a potentially useful thought appears during an audit or implementation:

1. Ask whether current behavior is demonstrably incorrect.
   - yes -> use/reuse `HARN-*`;
   - no -> continue here.
2. Search this Radar for the same underlying idea.
3. Reuse the existing `EVO-*` when the direction is the same.
4. Record the smallest useful statement: direction/question, expected value,
   evidence needed, and why it is not currently a defect.
5. Do not schedule implementation merely because an item exists here.
6. Promote only when evidence or an explicit architecture decision justifies it.
7. When promoted, put normative details in the owning spec/ADR and leave only a
   short `ADOPTED` pointer here.

## Sources of future Radar items

Useful sources include:

- repeated audit observations that do not prove a defect;
- comparisons with external engineering/agent methodologies;
- DDD/context-map reviews;
- real-project integration friction;
- recurring agent mistakes not enforceable by current deterministic contracts;
- opportunities to delete or simplify a Harness abstraction;
- evidence that a research layer is mature enough for canonicalization.


---

### EVO-021 — Instruction ownership hierarchy

**Type:** RECOMMENDATION  
**Status:** VALIDATED

Adopt one scalable ownership chain:

```text
AGENTS.md       = always-on repository invariants + bootstrap
agent router    = choose the applicable workflow
SKILL.md        = executable task procedure
canonical spec  = semantic/normative source of truth
README          = human-facing summary/projection
```

A skill consumes canonical policy; it does not become a second policy owner.
AUD-005 found concrete routing ambiguity where this ownership is currently
distributed. The hierarchy itself is an architecture recommendation; HARN-017
tracks the demonstrated defect.

### EVO-022 — Agent-skill registry and routing evaluation

**Type:** RESEARCH  
**Status:** ADOPTED

Introduce a machine-readable registry for active `skills/agent/**` with stable
identity, trigger class, exclusions and explicit precedence/composition where
needed. Add positive/negative/overlap routing fixtures.

Use project startup as the first collision case. Artifact-production routing
remains deterministic through `knowledge_kind -> skill`; do not replace that
with lexical routing.

Related: HARN-017, EVO-004, EVO-017.

### EVO-023 — Minimal root AGENTS

**Type:** RECOMMENDATION  
**Status:** ADOPTED

Keep root `AGENTS.md` for information required before task classification:
repository-wide safety/workflow invariants, truth-boundary invariants and the
instruction to discover/apply the active routed skill.

Move task-specific audit capture, project startup, Scenario Suite change
procedure and similar workflows into routed skills. This is progressive
disclosure, not merely shortening the file.

### EVO-024 — Common artifact-production procedure

**Type:** RESEARCH  
**Status:** PARKED

AUD-005 found `Human projection` in 45 artifact skills, registration-related
text in 41, and semantic-acceptance references in at least 23.

Test whether generic mechanics can be expressed once:

```text
common artifact procedure:
  candidate lifecycle
  generic Question discipline
  semantic-admission handoff
  registration semantics
  human projection rules

artifact-specific skill:
  inputs/read boundary
  judgement procedure
  stop conditions
  output contract
  domain-specific acceptance
```

Pilot only on `product-requirements`, `domain-model` and
`verification-strategy` first. Self-contained repetition may still win; let
behavioral evidence decide.

**Pilot result (AUD-007)**

The three skills share a structural skeleton, but their acceptance, registration,
read-boundary and decision semantics remain materially different. The reusable
part is already owned by the common semantic-admission/workbench contracts.
Extracting a base procedure now would add another indirection layer without
proven behavioral or context-budget benefit.

Keep the idea PARKED until behavioral evals or measured context duplication show
a concrete failure that a shared procedure would remove.

### EVO-025 — Quarantine inactive skills

**Type:** RECOMMENDATION  
**Status:** ADOPTED

Inactive procedures should not remain indistinguishable from active
`SKILL.md` discovery. Classify legacy skills as promote/archive/delete. Move
historical material to non-executable documentation form; promote only skills
with an active consumer and registry entry.

Related defect: HARN-018.

### EVO-026 — README/workbench ownership discipline

**Type:** RECOMMENDATION  
**Status:** ADOPTED

Keep `README.md` as product explanation and links. Keep
`agent-artifact-workbench-v0.md` focused on Application-layer concepts,
invariants and boundaries. Put operational sequences, stop conditions and
checklists in routed skills. Keep normative domain rules in their canonical
design/spec owners.

The goal is not to delete examples, but to remove independently maintained
copies of the same executable procedure.


### EVO-027 — Routing for non-owning analysis/method skills

**Type:** RESEARCH  
**Status:** ADOPTED

Eleven current `judgement_only` skills are deliberately not artifact providers,
but they are still executable procedures. Their selection therefore needs an
explicit owner.

Candidate direction:

```text
Engineering Coverage / Application evidence
        -> analysis/method route
        -> reliability-analysis / obligation-analysis / ...
        -> findings routed to semantic owners

Capability + knowledge_kind
        -> artifact route
        -> artifact-production skill
```

Do not force non-owning analyses into `knowledge_kind` merely to reuse the
artifact router. That would confuse "procedure that discovers/routes gaps" with
"provider of accepted project knowledge".

This is a concrete place to test EVO-003's Method / Procedure Library boundary.

Related defect: HARN-019.


### EVO-028 — Maintainer / Consumer skill surfaces and distribution

**Type:** RECOMMENDATION  
**Status:** ADOPTED

The architectural decision is now owned by
`docs/design/agent-skill-surfaces-and-consumer-distribution-v0.md`.

Summary:

- Harness-maintenance skills remain inside the Harness development surface;
- target repositories activate only the Harness Consumer Surface;
- Consumer procedures are distributed as a pinned versioned Consumer Pack;
- agents read the exact pack from local materialization, not remote per-skill
  links;
- target projects reference stable identities, not Harness source-tree paths;
- checkout/submodule/package/cache are transport choices, not semantic
  contracts;
- explicit local checkout override supports Harness/consumer co-development.

Further normative changes belong in the design contract, not this Radar entry.


### EVO-029 — CHANGE-TRANSITION-DESIGN producer promotion

**Type:** RESEARCH  
**Status:** CAPTURED

`change-transition-design` is not a non-owning method. Research evidence
supports a conditional CHANGE-TRANSITION-DESIGN Authority, and the Reference
Engineering Model contains a conditional TRANSITION-CONTRACT template, but that
research template does not yet publish a canonical `knowledge_kind`.

Do not assign a fake method route or invent a production kind merely to eliminate
an unrouted source file.

Promotion should require:

- Reference Model ownership/applicability to be accepted beyond research status;
- a stable project Capability/knowledge-kind contract;
- evidence from materially different transition cases;
- clear admission/currentness semantics for the resulting transition contract.

Until then the skill remains development-side research material and is excluded
from the Consumer Pack because its surface entry is `route_status: unrouted`.
