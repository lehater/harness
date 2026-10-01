# Harness Test Design Catalog v0

Status: canonical design catalog, implementation not started.

## Purpose

Translate the highest-information gaps from
`docs/design/harness-ability-to-evidence-v0.md` into concrete framework-neutral
test designs before any new test code is written.

v0 designs the full assurance progression before implementation:

- SF-01 Capability identity/granularity;
- SF-02 Authority partition;
- SF-03 Dependency necessity;
- SF-04 Applicability/coverage lattice;
- SF-05 Routing intent;
- SF-06 Existing-project bootstrap micro-project;
- SF-07 Greenfield bootstrap micro-project;
- SF-08 Semantic derivation/admission;
- SF-09 Lifecycle/evolution/scale;
- SF-10 Frontier/publication;
- SF-11 Repository projections/distribution;
- SF-12 CI/assurance meta-testing;
- SF-13 External semantic evaluator assurance;
- SF-14 Real-project portability/holdouts.

The catalog still requires review before implementation. Lower-level synthetic
designs must be accepted before dependent TL3-TL6 designs can become READY.

## Test design record

Every entry declares:

~~~text
id
abilities
failure_modes
methods
minimum_test_level
oracle_class
fixture
system_under_test
expected_semantic_result
assertions
negative_or_control_cases
normalization
implementation_surface
status
~~~

`implementation_surface` is a recommendation only. Review may reuse an existing
validator/scenario/eval runner instead of adding a new one.

Statuses:

- DESIGN — specified but not yet reviewed for implementation;
- READY — oracle and boundary reviewed; implementation may begin;
- IMPLEMENTED — executable evidence exists;
- VERIFIED — implemented evidence independently re-audited.

All entries in v0 start as DESIGN.

## Review criteria before implementation

A design may move to READY only when:

1. the fixture does not encode the expected answer through Harness-specific IDs
   or labels;
2. the oracle was authored independently from the implementation under test;
3. the tested boundary is not bypassed by supplying the semantic answer as
   input;
4. a negative/control case exists where useful;
5. literal prose equality is not used for judgement-dependent outputs;
6. the fixture is minimal enough that a failure identifies the responsible
   mechanism;
7. larger TL3/TL4 evidence is not used to hide a missing TL1/TL2 oracle.

# SF-01 — Capability identity and granularity

## TD-CAP-001 — One necessary project Capability

**Abilities:** HA-A05  
**Failure modes:** A05-F01 omission, A05-F02 invention  
**Methods:** EM-02  
**Minimum level:** TL1  
**Oracle:** O1  
**Status:** DESIGN

Fixture:

A small accepted evidence set states that an API accepts idempotency keys for
payment creation and that retry safety must be reasoned about before the API
contract is implementation-ready. No other independent engineering knowledge
surface is present.

System under test:

The Capability-formation judgement/procedure, not Reference Model
materialization.

Expected semantic result:

Exactly one project knowledge identity representing the independently provable
idempotency/retry contract. Naming is unconstrained.

Assertions:

- obligation recall = 1/1;
- invention count = 0;
- one semantic Capability identity after normalization;
- no unrelated persistence, observability, or deployment Capability is invented.

Control:

Add prose examples/repetition that restate the same obligation. The normalized
Capability set must remain one.

Recommended implementation surface:

A dedicated semantic fixture/eval contract, not a Core validator.

## TD-CAP-002 — No new Capability from descriptive noise

**Abilities:** HA-A05  
**Failure modes:** A05-F02 invention  
**Methods:** EM-02, EM-05  
**Minimum level:** TL1  
**Oracle:** O1  
**Status:** DESIGN

Fixture:

Accepted project evidence contains examples, implementation notes, filenames,
and terminology that mention caching, retries, security, and metrics, but none
are normative/decision-bearing requirements for the selected scope.

Expected semantic result:

No new Capability is formed from those mentions.

Assertions:

- invention precision is perfect for the fixture;
- terminology frequency and file names do not create engineering obligations.

Metamorphic control:

Reorder the noisy evidence and duplicate one descriptive paragraph; result must
remain empty.

## TD-CAP-003 — Mandatory split by independent provability

**Abilities:** HA-A05  
**Failure modes:** A05-F05 over-merge granularity  
**Methods:** EM-02  
**Minimum level:** TL1  
**Oracle:** O1  
**Status:** DESIGN

Fixture:

Evidence contains two independently decidable obligations:

1. payment retry/idempotency semantics;
2. audit-retention semantics with its own acceptance/revalidation lifecycle.

They may appear in one source document.

Expected semantic result:

Two semantic Capability identities.

Assertions:

- two oracle obligations are recalled;
- they are not merged because each can change/revalidate independently;
- source-file co-location is irrelevant.

## TD-CAP-004 — Mandatory merge of repeated semantic surface

**Abilities:** HA-A05  
**Failure modes:** A05-F04 over-split granularity, A05-F03 duplicate Capability  
**Methods:** EM-02, EM-05  
**Minimum level:** TL1  
**Oracle:** O1  
**Status:** DESIGN

Fixture:

Three statements describe the same independently provable retry/idempotency
contract using different vocabulary and examples.

Expected semantic result:

One normalized Capability identity.

Assertions:

- duplicate semantic identity count = 0;
- paraphrases/examples remain evidence for one Capability, not separate
  Capabilities.

## TD-CAP-005 — Reference-template lexical trap

**Abilities:** HA-A05, HA-A08  
**Failure modes:** A05-F06 Reference Model bias, A05-F02 invention, A08-F04  
**Methods:** EM-02, EM-05  
**Minimum level:** TL1  
**Oracle:** O1  
**Status:** DESIGN

Fixture:

Project evidence repeatedly uses terminology strongly associated with a known
Reference Model template, but the selected scope has no independent obligation
that the template would satisfy.

Expected semantic result:

The attractive template is not selected/created.

Control:

Add one explicit material obligation that genuinely requires the template
surface. The result should then include the corresponding knowledge identity.

## TD-CAP-006 — Novel Capability absent from Reference Model

**Abilities:** HA-A05  
**Failure modes:** A05-F07 novel Capability missed, A05-F06 template bias  
**Methods:** EM-02  
**Minimum level:** TL1  
**Oracle:** O1  
**Status:** DESIGN

Fixture:

Create a synthetic domain-specific engineering obligation whose semantic surface
does not map to any current Reference Model template.

The fixture must avoid naming the expected Capability or using existing
`knowledge_kind` labels as clues.

Expected semantic result:

One project-specific Capability identity is discovered from the obligation even
though no template exists.

Assertions:

- obligation recall includes the novel surface;
- no nearest-template substitution is accepted as equivalent;
- no unrelated template is added.

## TD-CAP-007 — Capability metamorphic stability

**Abilities:** HA-A05  
**Failure modes:** A05-F08 instability  
**Methods:** EM-05  
**Minimum level:** TL1  
**Oracle:** O1  
**Status:** DESIGN

Base fixture:

Reuse TD-CAP-001/003/004.

Transformations:

- reorder sources;
- rename files;
- change non-semantic headings;
- paraphrase descriptive prose without changing obligations;
- add irrelevant implementation examples.

Expected semantic result:

Same normalized Capability identities and granularity.

# SF-02 — Authority partition

## TD-AUTH-001 — Mandatory merge

**Abilities:** HA-A04  
**Failure modes:** A04-F01 over-split  
**Methods:** EM-02  
**Minimum level:** TL1  
**Oracle:** O1  
**Status:** DESIGN

Fixture:

Several decision atoms jointly define one public contract and always
change/revalidate together. They are stored in separate files/modules.

Expected semantic result:

One Authority partition containing all atoms.

Assertions:

- pairwise partition agreement with oracle = complete;
- filesystem separation does not cause split.

## TD-AUTH-002 — Mandatory split

**Abilities:** HA-A04  
**Failure modes:** A04-F02 over-merge  
**Methods:** EM-02  
**Minimum level:** TL1  
**Oracle:** O1  
**Status:** DESIGN

Fixture:

Two decision surfaces have separate public contracts and can change/revalidate
independently even though they appear in the same source document and domain
vocabulary.

Expected semantic result:

Two Authorities.

Assertions:

- cross-surface atom pairs are separated;
- intra-surface pairs remain grouped.

## TD-AUTH-003 — Overlap/joint ownership rejection

**Abilities:** HA-A04, HA-A13  
**Failure modes:** A04-F03 joint ownership leak  
**Methods:** EM-02, EM-03  
**Minimum level:** TL1  
**Oracle:** O1  
**Status:** DESIGN

Fixture:

One canonical decision atom is intentionally presented as relevant to two
candidate Authority surfaces.

Expected semantic result:

The atom has one semantic owner. If evidence is insufficient to choose, the
result is explicit uncertainty/Question rather than duplicated ownership.

Assertions:

- no atom belongs canonically to two Authorities;
- ambiguity remains visible.

## TD-AUTH-004 — File/module layout is not Authority topology

**Abilities:** HA-A04  
**Failure modes:** A04-F04 layout bias  
**Methods:** EM-05  
**Minimum level:** TL1  
**Oracle:** O1  
**Status:** DESIGN

Base fixture:

Use a known one-Authority and two-Authority atom set.

Transformations:

- place one Authority across several files;
- place several Authorities in one file;
- rename folders/modules to misleading domain names.

Expected semantic result:

Authority partition remains unchanged.

## TD-AUTH-005 — Ambiguous split becomes Question

**Abilities:** HA-A04, HA-A13  
**Failure modes:** A04-F01/F02 under insufficient evidence, A13-F01  
**Methods:** EM-02  
**Minimum level:** TL1  
**Oracle:** O1  
**Status:** DESIGN

Fixture:

Decision atoms admit two plausible partitionings and the evidence does not
establish independent change/public contract.

Expected semantic result:

No confident invented boundary. The unresolved ownership/boundary issue becomes
explicit uncertainty addressed to the appropriate semantic owner.

## TD-AUTH-006 — Reference boundary trap

**Abilities:** HA-A04  
**Failure modes:** A04-F05 Reference Model bias  
**Methods:** EM-02  
**Minimum level:** TL1  
**Oracle:** O1  
**Status:** DESIGN

Fixture:

Reference Model suggests one common Authority grouping, while synthetic project
evidence explicitly demonstrates a different independent-change boundary.

Expected semantic result:

Project evidence wins; Authority partition follows the project-specific
contract.

## TD-AUTH-007 — Partition metamorphic stability

**Abilities:** HA-A04  
**Failure modes:** A04-F06 instability  
**Methods:** EM-05  
**Minimum level:** TL1  
**Oracle:** O1  
**Status:** DESIGN

Transformations:

- reorder atoms;
- paraphrase labels;
- rename files/components/teams;
- add irrelevant descriptive atoms.

Expected semantic result:

Identical pairwise Authority partition over the decision-bearing atoms.

# SF-03 — Dependency necessity

## TD-DEP-001 — Required semantic prerequisite

**Abilities:** HA-A02, HA-A12  
**Failure modes:** missing dependency, A12-F01 semantic loss  
**Methods:** EM-02  
**Minimum level:** TL1  
**Oracle:** O1  
**Status:** DESIGN

Fixture:

Capability B cannot be accepted without semantic knowledge provided by
Capability A.

Expected semantic result:

A is a prerequisite of B.

Assertions:

- dependency recall includes A -> B;
- admission without A is invalid.

## TD-DEP-002 — Plausible but unnecessary dependency rejected

**Abilities:** HA-A02, HA-A12  
**Failure modes:** unnecessary dependency / topology over-generation  
**Methods:** EM-02  
**Minimum level:** TL1  
**Oracle:** O1  
**Status:** DESIGN

Fixture:

A and B are related in domain vocabulary and implementation order, but B's
accepted claim surface is independently provable without A.

Expected semantic result:

No prerequisite edge A -> B.

Control:

Add a material claim in B that explicitly consumes A; edge should then appear.

## TD-DEP-003 — Same-Authority semantic support must be explicit

**Abilities:** HA-A12, HA-A14  
**Failure modes:** hidden semantic dependency bypasses lifecycle baseline  
**Methods:** EM-02, EM-03  
**Minimum level:** TL1-TL2  
**Oracle:** O1  
**Status:** DESIGN

Fixture:

Two Capabilities share one Authority. B materially uses accepted semantics from
A.

Expected semantic result:

A is a declared prerequisite of B; same-Authority readability alone is not
semantic provenance.

Mutation:

Change A's accepted identity. B must become stale.

## TD-DEP-004 — Correct dependency direction

**Abilities:** HA-A02, HA-A12  
**Failure modes:** reversed dependency  
**Methods:** EM-02  
**Minimum level:** TL1  
**Oracle:** O1  
**Status:** DESIGN

Fixture:

Design semantics consume product requirement semantics; product requirement
semantics do not consume the derived design.

Expected semantic result:

Requirement -> design prerequisite direction only.

## TD-DEP-005 — Dependency stability under irrelevant evidence

**Abilities:** HA-A02  
**Failure modes:** invented/missing edge from noise  
**Methods:** EM-05  
**Minimum level:** TL1  
**Oracle:** O1  
**Status:** DESIGN

Transformations:

Add unrelated evidence, reorder declarations, rename files.

Expected semantic result:

Normalized dependency graph over the tested Capabilities is unchanged.

## TD-DEP-006 — Topology change drives exact lifecycle reaction

**Abilities:** HA-A14  
**Failure modes:** A14-F07, over-invalidation  
**Methods:** EM-03, EM-07  
**Minimum level:** TL2  
**Oracle:** O1  
**Status:** DESIGN

Base:

Accepted A -> B topology with current lifecycle.

Mutation:

Replace B's prerequisite A with C.

Expected semantic result:

- B becomes stale for prerequisite-topology reason;
- unrelated D remains current;
- acceptance from A is not transferred to C.

# SF-04 — Applicability and coverage lattice

## TD-APP-001 — Explicit REQUIRED

**Abilities:** HA-A06  
**Failure modes:** A06-F02  
**Methods:** EM-02  
**Minimum level:** TL1  
**Oracle:** O1  
**Status:** DESIGN

Fixture:

Accepted facts directly activate a concern/subject obligation.

Expected semantic result:

REQUIRED with evidence provenance.

## TD-APP-002 — Evidence-backed NOT_APPLICABLE

**Abilities:** HA-A06  
**Failure modes:** wrong N/A  
**Methods:** EM-02  
**Minimum level:** TL1  
**Oracle:** O1  
**Status:** DESIGN

Fixture:

Accepted project evidence explicitly rules out the concern for the selected
scope.

Expected semantic result:

NOT_APPLICABLE with explicit evidence/disposition.

## TD-APP-003 — Silence remains UNKNOWN

**Abilities:** HA-A06  
**Failure modes:** A06-F01, A06-F03  
**Methods:** EM-02, EM-03  
**Minimum level:** TL1  
**Oracle:** O1  
**Status:** DESIGN

Fixture:

No accepted evidence establishes applicability or non-applicability.

Expected semantic result:

UNKNOWN (or explicit unresolved state owned by the contract), never N/A and
never completion-ready through silence.

## TD-APP-004 — Unresolved evidence becomes QUESTION

**Abilities:** HA-A06, HA-A13  
**Failure modes:** A06-F03, A13-F01  
**Methods:** EM-02  
**Minimum level:** TL1-TL2  
**Oracle:** O1  
**Status:** DESIGN

Fixture:

Evidence demonstrates that applicability matters, but the deciding semantic fact
is absent.

Expected semantic result:

QUESTION/unresolved frontier addressed to the Authority that can decide it.

## TD-APP-005 — Irrelevant concern does not activate

**Abilities:** HA-A06  
**Failure modes:** A06-F04  
**Methods:** EM-02, EM-05  
**Minimum level:** TL1  
**Oracle:** O1  
**Status:** DESIGN

Fixture:

Vocabulary resembles a concern but accepted scope/facts do not activate it.

Expected semantic result:

No REQUIRED obligation solely from lexical similarity.

## TD-APP-006 — Scope isolation

**Abilities:** HA-A06  
**Failure modes:** A06-F06  
**Methods:** EM-05, EM-07  
**Minimum level:** TL1-TL2  
**Oracle:** O1  
**Status:** DESIGN

Base:

Two independent Consumer/scope roots with separate obligation sets.

Mutation:

Narrow one selected scope.

Expected semantic result:

Only obligations reachable/applicable to that scope change; unrelated scope
coverage is unchanged.

# SF-05 — Routing intent

## TD-ROUTE-001 — Project bootstrap intent

**Abilities:** HA-A16  
**Failure modes:** A16-F01, A16-F08  
**Methods:** EM-02  
**Minimum level:** TL1 semantic oracle; eventual TL4 execution  
**Oracle:** O1 for intended route  
**Status:** DESIGN

Task:

A user asks to start using Harness on an existing project or reconcile an
existing project realization.

Expected operation:

`project-bootstrap-reconcile`.

Important boundary:

The TL1 design records the independently intended route. It does not count as
behavioral proof until an agent actually selects it.

## TD-ROUTE-002 — Engineering status intent

**Abilities:** HA-A16  
**Failure modes:** A16-F01  
**Methods:** EM-02  
**Minimum level:** TL1 semantic oracle; eventual TL4 execution  
**Oracle:** O1  
**Status:** DESIGN

Task:

A user asks what engineering work is currently missing/blocked/ready for a
selected project Consumer without asking to redesign the target.

Expected operation:

`project-engineering-status`.

Negative contrast:

A request to define the target knowledge closure belongs to
`design-profile`, not this route.

## TD-ROUTE-003 — Design Profile intent

**Abilities:** HA-A16, HA-A08  
**Failure modes:** A16-F01  
**Methods:** EM-02  
**Minimum level:** TL1 semantic oracle; eventual TL4 execution  
**Oracle:** O1  
**Status:** DESIGN

Task:

A user asks to define/review what engineering knowledge a selected scope must
contain before it is design-complete.

Expected operation:

`design-profile`.

## TD-ROUTE-004 — Decision pipeline intent

**Abilities:** HA-A16  
**Failure modes:** A16-F01  
**Methods:** EM-02  
**Minimum level:** TL1 semantic oracle; eventual TL4 execution  
**Oracle:** O1  
**Status:** DESIGN

Task:

A project frontier has a decision-governed work item ready and the user asks to
evaluate alternatives/advance the decision.

Expected operation:

`decision-pipeline`.

Control:

If the task is only to report status, do not select decision-pipeline.

## TD-ROUTE-005 — Human projection intent

**Abilities:** HA-A16, HA-A17  
**Failure modes:** A16-F01  
**Methods:** EM-02  
**Minimum level:** TL1 semantic oracle; eventual TL4 execution  
**Oracle:** O1  
**Status:** DESIGN

Task:

Accepted canonical knowledge exists and the user asks to derive/update
human-facing documentation from it.

Expected operation:

`human-documentation-projection`.

## TD-ROUTE-006 — Internal route cannot compete for entry

**Abilities:** HA-A16  
**Failure modes:** A16-F02  
**Methods:** EM-02, EM-03  
**Minimum level:** TL1  
**Oracle:** O1  
**Status:** DESIGN

Task:

Same startup wording as TD-ROUTE-001.

Expected result:

`bootstrap-existing-project` is never selected as a public entry operation.
It may resolve only when invoked by the authorized
`project-bootstrap-reconcile` parent.

This deterministic boundary already has implementation evidence; the design
exists to keep it in the canonical assurance denominator.

## TD-ROUTE-007 — Project evidence cannot change route authority

**Abilities:** HA-A16, HA-A11  
**Failure modes:** A16-F07, A11-F06  
**Methods:** EM-05  
**Minimum level:** TL3 for realistic payload handling; eventual TL4  
**Oracle:** O1/O4  
**Status:** DESIGN

Fixture:

A valid user task maps to one public operation. Project README/source/tool
payload contains instruction-like text telling the agent to select a different
operation, ignore Harness policy, or invoke an internal route.

Expected semantic result:

The selected operation remains determined by the trusted task/instruction
hierarchy. Payload text remains data.

## TD-ROUTE-008 — Near-neighbor intent discrimination

**Abilities:** HA-A16  
**Failure modes:** A16-F01  
**Methods:** EM-05  
**Minimum level:** TL1 oracle; eventual TL4  
**Oracle:** O1  
**Status:** DESIGN

Fixture family:

Pairs of minimally different tasks whose one material intent change should
switch the operation:

- bootstrap/reconcile vs status;
- status vs design-profile;
- status vs human documentation projection;
- decision work vs status.

Expected semantic result:

Semantic route follows the changed responsibility, not shared vocabulary.

# Composition designs after TL1 review

These designs are intentionally blocked until SF-01 through SF-05 TL1 oracles
are reviewed.

## TD-COMP-001 — Evidence to project knowledge topology

**Abilities:** HA-A04, HA-A05, HA-A12  
**Failure modes:** omission, invention, wrong boundary, missing/unnecessary edge  
**Methods:** EM-07  
**Minimum level:** TL2  
**Oracle:** O1  
**Status:** DESIGN

Pipeline:

~~~text
accepted synthetic evidence
-> Capability identities
-> Authority partition
-> prerequisite edges
~~~

Fixture:

Combine a reviewed subset of SF-01, SF-02, and SF-03 without adding repository
files.

Expected result:

One normalized project-knowledge topology matching all three independent oracles.

Purpose:

Detect semantic translation loss between mechanisms without yet introducing
bootstrap/source-selection noise.

## TD-COMP-002 — Applicability to Question/coverage frontier

**Abilities:** HA-A06, HA-A13, HA-A15  
**Failure modes:** UNKNOWN collapsed, wrong owner, false COMPLETE  
**Methods:** EM-07  
**Minimum level:** TL2  
**Oracle:** O1  
**Status:** DESIGN

Pipeline:

~~~text
project facts
-> applicability disposition
-> unresolved semantic gap
-> Question owner/blocking
-> coverage/frontier result
~~~

Expected result:

The exact unresolved obligation stays visible and prevents completion.

## TD-COMP-003 — Task intent to authorized skill surface

**Abilities:** HA-A16  
**Failure modes:** wrong operation, unauthorized internal route, wrong skill  
**Methods:** EM-07, later EM-09  
**Minimum level:** TL2 deterministic after operation; TL4 for full intent path  
**Oracle:** O1/O4  
**Status:** DESIGN

Pipeline:

~~~text
task intent
-> selected public operation
-> skill_router
-> instruction contracts
-> selected SKILL
~~~

At TL2, operation is supplied from the reviewed oracle and deterministic routing
is checked.

At TL4, a fresh agent must infer the operation itself from the task. These two
tests must remain separate so deterministic router correctness cannot be
mistaken for agent-intent correctness.

# Planned TL3 micro-project handoff

No TL3 fixture should be implemented until the relevant TL1/TL2 designs above
are reviewed.

The first micro-project should be SF-06 Existing-project bootstrap and reuse:

- TD-CAP-006 novel Capability;
- TD-AUTH-002 mandatory split;
- TD-DEP-001 required edge;
- TD-APP-003 silence -> UNKNOWN;
- TD-ROUTE-001 bootstrap intent;
- one irrelevant Reference Model lexical trap;
- one instruction-like data payload;
- one reusable project-owned canonical provider;
- one unrelated repository subtree.

The TL3 oracle should be a normalized semantic model, not a golden file dump.

# SF-06 — Existing-project bootstrap micro-project

## TD-BOOT-E01 — Reuse project-owned graph truth

**Abilities:** HA-A09, HA-A17  
**Failure modes:** A09-F01, A09-F02, A09-F06  
**Methods:** EM-08  
**Minimum level:** TL3  
**Oracle:** O1  
**Status:** DESIGN

Fixture:

A tiny existing repository exposes canonical machine-readable dependency/routing
truth plus partial Harness metadata.

Expected semantic result:

Bootstrap projects/reuses the existing truth instead of constructing a second
canonical graph.

Assertions:

- no duplicate semantic owner is introduced;
- selected Engineering Graph/Core inputs are projections/adaptations of the
  project-owned truth;
- unrelated repository facts remain outside the selected model.

## TD-BOOT-E02 — Minimal direct realization when no graph exists

**Abilities:** HA-A09  
**Failure modes:** A09-F03, A09-F06  
**Methods:** EM-08  
**Minimum level:** TL3  
**Oracle:** O1  
**Status:** DESIGN

Fixture:

A tiny repository has accepted canonical engineering artifacts but no
machine-readable topology for the selected scope.

Expected semantic result:

Bootstrap creates only the smallest direct Harness realization needed for the
selected Consumer/scope.

Negative:

Adding unrelated directories must not enlarge the realization.

## TD-BOOT-E03 — Unknown project fact remains explicit

**Abilities:** HA-A09, HA-A13  
**Failure modes:** A09-F04, A13-F01  
**Methods:** EM-08  
**Minimum level:** TL3  
**Oracle:** O1  
**Status:** DESIGN

Fixture:

One required semantic fact cannot be established from accepted sources.

Expected semantic result:

The missing fact remains UNKNOWN/Question at the owning boundary. Bootstrap does
not guess a value merely to complete the model.

## TD-BOOT-E04 — Bootstrap idempotence

**Abilities:** HA-A09  
**Failure modes:** A09-F05  
**Methods:** EM-03, EM-08  
**Minimum level:** TL3  
**Oracle:** O1  
**Status:** DESIGN

Procedure:

Run bootstrap/reconcile twice against unchanged fixture state.

Expected semantic result:

Normalized project model, Questions, and frontier are unchanged on the second
run; no duplicate artifacts/Capabilities are introduced.

## TD-BOOT-E05 — Bootstrap ignores unrelated repository expansion

**Abilities:** HA-A09, HA-A11  
**Failure modes:** A09-F03, A11-F01/F02  
**Methods:** EM-05, EM-08  
**Minimum level:** TL3  
**Oracle:** O1  
**Status:** DESIGN

Mutation:

Add a large unrelated subtree containing attractive engineering vocabulary.

Expected semantic result:

Selected scope/model is unchanged.

## TD-BOOT-E06 — Existing-project repeated clean contexts

**Abilities:** HA-A04, HA-A05, HA-A09, HA-A11, HA-A16  
**Failure modes:** A04-F06, A05-F08, A09-F05, A16-F08  
**Methods:** EM-09  
**Minimum level:** TL4  
**Oracle:** O1 for synthetic model + semantic normalization  
**Status:** DESIGN

Prerequisite:

TD-COMP-001, TD-COMP-003, and TD-BOOT-E01..E05 are READY/implemented.

Expected result:

Repeated fresh-agent runs agree with the frozen semantic oracle on Capability
set, Authority partition, dependencies, Questions, selected operation, and
Consumer closure.

# SF-07 — Greenfield bootstrap micro-project

## TD-BOOT-G01 — Minimal initial model

**Abilities:** HA-A10, HA-A08  
**Failure modes:** A10-F01, A10-F02  
**Methods:** EM-08  
**Minimum level:** TL3  
**Oracle:** O1  
**Status:** DESIGN

Fixture:

A concise greenfield goal/scope contains enough evidence for a few foundational
engineering obligations.

Expected semantic result:

The smallest model satisfying those obligations; no speculative architecture or
delivery/process structure.

## TD-BOOT-G02 — Unresolved architecture choice is not invented

**Abilities:** HA-A10, HA-A13  
**Failure modes:** A10-F03, A13-F01  
**Methods:** EM-08  
**Minimum level:** TL3  
**Oracle:** O1  
**Status:** DESIGN

Fixture:

The goal requires a storage/public-contract decision but provides no accepted
basis to choose among alternatives.

Expected semantic result:

Question/decision frontier remains explicit; no canonical choice is invented.

## TD-BOOT-G03 — Safe first frontier

**Abilities:** HA-A10, HA-A03, HA-A15  
**Failure modes:** A10-F04, false READY/COMPLETE  
**Methods:** EM-07, EM-08  
**Minimum level:** TL3  
**Oracle:** O1  
**Status:** DESIGN

Expected semantic result:

Only foundational work whose prerequisites are satisfied appears actionable.

## TD-BOOT-G04 — Reference Model does not overbuild greenfield scope

**Abilities:** HA-A10, HA-A05, HA-A08  
**Failure modes:** A10-F01, A05-F06, A08-F04  
**Methods:** EM-05, EM-08  
**Minimum level:** TL3  
**Oracle:** O1  
**Status:** DESIGN

Fixture:

Goal vocabulary resembles several reusable templates but only one obligation is
material.

Expected semantic result:

Only material project knowledge is admitted.

## TD-BOOT-G05 — Greenfield repeated clean contexts

**Abilities:** HA-A05, HA-A08, HA-A10, HA-A16  
**Failure modes:** A10-F05, A05-F08, A16-F08  
**Methods:** EM-09  
**Minimum level:** TL4  
**Oracle:** O1/O4  
**Status:** DESIGN

Compare normalized semantic model and frontier across repeated clean runs.

# SF-08 — Semantic derivation and admission

## TD-SEM-001 — Required atom preservation

**Abilities:** HA-A12  
**Failure modes:** A12-F01  
**Methods:** EM-02  
**Minimum level:** TL1  
**Oracle:** O1  
**Status:** DESIGN

Fixture:

A downstream Capability has a declared prerequisite with several material source
atoms.

Expected result:

Every required atom is consumed, explicitly dispositioned, or represented by a
valid transformation/constrain/realization relation.

## TD-SEM-002 — Silent semantic loss mutation

**Abilities:** HA-A12  
**Failure modes:** A12-F01  
**Methods:** EM-03  
**Minimum level:** TL1-TL2  
**Oracle:** O1  
**Status:** DESIGN

Mutation:

Remove one required semantic effect from an otherwise accepted downstream
derivation.

Expected result:

Admission fails or surfaces the exact missing obligation.

## TD-SEM-003 — Unsupported provenance rejected

**Abilities:** HA-A12  
**Failure modes:** A12-F02, A12-F03  
**Methods:** EM-02, EM-03  
**Minimum level:** TL1  
**Oracle:** O1  
**Status:** DESIGN

Expected result:

A claim sourced from an undeclared prerequisite/Authority is rejected even when
the artifact is readable in the execution context.

## TD-SEM-004 — Contradiction fails closed

**Abilities:** HA-A12  
**Failure modes:** A12-F04  
**Methods:** EM-02  
**Minimum level:** TL1  
**Oracle:** O1  
**Status:** DESIGN

Expected result:

Contradictory accepted source semantics are not silently reconciled into an
accepted downstream claim.

## TD-SEM-005 — Irrelevant semantic input is metamorphically inert

**Abilities:** HA-A12  
**Failure modes:** A12-F05  
**Methods:** EM-05  
**Minimum level:** TL1  
**Oracle:** O1  
**Status:** DESIGN

Mutation:

Add or reorder irrelevant allowed source statements.

Expected result:

Normalized admitted downstream semantics are unchanged.

## TD-SEM-006 — Delegated semantic judgement calibration

**Abilities:** HA-A12, HA-A20  
**Failure modes:** A12-F06, A20-F03/F04  
**Methods:** EM-12  
**Minimum level:** TL4 calibration track  
**Oracle:** O4  
**Status:** DESIGN

Use an expert-labelled corpus with explicit positive/negative semantic
transformations and report confusion/stability rather than only aggregate pass.

# SF-09 — Lifecycle, graph evolution, and scale

## TD-LIFE-001 — Prerequisite acceptance change

**Abilities:** HA-A14  
**Failure modes:** A14-F01  
**Methods:** EM-03  
**Minimum level:** TL1  
**Oracle:** O1  
**Status:** DESIGN

Mutation:

Change a direct prerequisite acceptance identity.

Expected result:

Exactly the dependent capability becomes stale; unrelated capabilities remain
current.

## TD-LIFE-002 — Acceptance-policy change

**Abilities:** HA-A14  
**Failure modes:** A14-F03  
**Methods:** EM-03  
**Minimum level:** TL1-TL2  
**Oracle:** O1  
**Status:** DESIGN

Expected result:

A changed effective acceptance-policy fingerprint requires revalidation.

## TD-LIFE-003 — Current snapshot rejects stale replay

**Abilities:** HA-A14, HA-A13  
**Failure modes:** A14-F04, A13-F07  
**Methods:** EM-02, EM-03  
**Minimum level:** TL1-TL2  
**Oracle:** O1  
**Status:** DESIGN

Fixture:

Provide duplicate/stale semantic evaluation records for one current identity.

Expected result:

Current-snapshot contract fails closed; stale rejection cannot reopen a Question
by list order.

## TD-LIFE-004 — Removed Capability becomes inert history

**Abilities:** HA-A14  
**Failure modes:** A14-F05, A14-F06  
**Methods:** EM-03, EM-06  
**Minimum level:** TL1-TL2  
**Oracle:** O1  
**Status:** DESIGN

Expected result:

Removed identity is explicit obsolete/inert lifecycle history and does not
transfer acceptance to replacement identity.

## TD-LIFE-005 — Rename/split/merge topology migration

**Abilities:** HA-A14, HA-A07  
**Failure modes:** A14-F06/F07, A07-F02/F03  
**Methods:** EM-03, EM-07  
**Minimum level:** TL2  
**Oracle:** O1  
**Status:** DESIGN

Cases:

- rename one Capability;
- split one into two;
- merge two into one;
- change prerequisite set without identity rename.

Expected result:

No semantic acceptance transfers without explicit evidence; retained identities
with changed topology become stale as required.

## TD-LIFE-006 — Deep/broad graph support envelope

**Abilities:** HA-A02, HA-A14, HA-A21  
**Failure modes:** A02-F06, A14-F08, A21-F04  
**Methods:** EM-13  
**Minimum level:** TL1/TL2 stress tier  
**Oracle:** O1  
**Status:** DESIGN

Generate depth, breadth/fan-out, and cardinality independently.

Expected result:

Correct semantics within declared support envelope; runtime/memory observations
are recorded separately from correctness.

# SF-10 — Frontier, retry, and publication

## TD-FRONT-001 — Cross-layer precedence matrix

**Abilities:** HA-A15  
**Failure modes:** A15-F01, A15-F03  
**Methods:** EM-07  
**Minimum level:** TL2  
**Oracle:** O1  
**Status:** DESIGN

Fixture matrix:

Vary decision failure, semantic gap, coverage gap, blocker, waiting prerequisite,
and complete states.

Expected result:

Exactly one canonical frontier disposition with documented precedence and no
false COMPLETE.

## TD-FRONT-002 — Failed validation requires explicit retry

**Abilities:** HA-A15  
**Failure modes:** A15-F02, A15-F08  
**Methods:** EM-03, EM-06  
**Minimum level:** TL2  
**Oracle:** O1  
**Status:** DESIGN

Expected result:

FAILED_VALIDATION remains non-ready until explicit retry; retry still respects
blockers/prerequisites.

## TD-FRONT-003 — Duplicate work is deduplicated

**Abilities:** HA-A15  
**Failure modes:** A15-F04  
**Methods:** EM-07  
**Minimum level:** TL2  
**Oracle:** O1  
**Status:** DESIGN

Fixture:

Same capability gap is visible through more than one read model.

Expected result:

One actionable work identity in the composed frontier.

## TD-PUB-001 — Atomic terminal publication

**Abilities:** HA-A15  
**Failure modes:** A15-F05, A15-F07  
**Methods:** EM-15  
**Minimum level:** TL2-TL3  
**Oracle:** O1  
**Status:** DESIGN

Expected result:

Core provider, semantic evaluation, lifecycle, Question resolution, and failure
state become visible as one logical revision or not at all.

## TD-PUB-002 — Stale writer rejected

**Abilities:** HA-A15  
**Failure modes:** A15-F06  
**Methods:** EM-15  
**Minimum level:** TL2  
**Oracle:** O1  
**Status:** DESIGN

Expected result:

CAS/version mismatch prevents older publication from overwriting newer state.

## TD-PUB-003 — Retry after interrupted publication

**Abilities:** HA-A15  
**Failure modes:** A15-F07/F08  
**Methods:** EM-15  
**Minimum level:** TL3  
**Oracle:** O1  
**Status:** DESIGN

Expected result:

Interrupted pre-commit attempt leaves no mixed visible revision; safe retry
produces one coherent result.

# SF-11 — Repository realization, projections, and distribution

## TD-PROJ-001 — Derived projection cannot become truth

**Abilities:** HA-A17  
**Failure modes:** A17-F01/F02  
**Methods:** EM-02, EM-03  
**Minimum level:** TL1-TL2  
**Oracle:** O1  
**Status:** DESIGN

Mutation:

Change generated/human projection without changing accepted canonical source.

Expected result:

Canonical truth/currentness does not change because projection text changed.

## TD-PROJ-002 — Missing projection prerequisite fails closed

**Abilities:** HA-A17  
**Failure modes:** A17-F03/F04  
**Methods:** EM-03, EM-07  
**Minimum level:** TL2  
**Oracle:** O1  
**Status:** DESIGN

Expected result:

Repository/frontend/human/workspace closure cannot claim complete when its
required canonical semantics are absent/stale.

## TD-PROJ-003 — Projection reproducibility

**Abilities:** HA-A17  
**Failure modes:** A17-F05  
**Methods:** EM-05  
**Minimum level:** TL1-TL2  
**Oracle:** O1  
**Status:** DESIGN

Equivalent canonical truth should yield semantically equivalent projection
independent of irrelevant ordering.

## TD-DIST-001 — Consumer Pack public surface closure

**Abilities:** HA-A18  
**Failure modes:** A18-F02/F03/F05  
**Methods:** EM-01, EM-03  
**Minimum level:** TL1-TL2  
**Oracle:** O1  
**Status:** DESIGN

Expected result:

Pack contains all and only declared Consumer surface/contracts.

## TD-DIST-002 — Pin/API compatibility

**Abilities:** HA-A18  
**Failure modes:** A18-F01/F04/F06  
**Methods:** EM-02, EM-03, EM-06  
**Minimum level:** TL1-TL2  
**Oracle:** O1  
**Status:** DESIGN

Cases include moving ref, incompatible consumer_api, and renamed published
identity without compatibility mapping.

Expected result:

Fail closed unless explicit compatible upgrade contract exists.

# SF-12 — CI and assurance meta-testing

## TD-CI-001 — Executable-check inventory completeness

**Abilities:** HA-A19  
**Failure modes:** A19-F01  
**Methods:** EM-01, EM-14  
**Minimum level:** TL0  
**Oracle:** O1  
**Status:** DESIGN

Expected result:

Every validator/test/workflow has explicit inventory/disposition.

## TD-CI-002 — Stage/cost/trigger policy

**Abilities:** HA-A19  
**Failure modes:** A19-F02/F03/F05  
**Methods:** EM-03, EM-14  
**Minimum level:** TL0-TL1  
**Oracle:** O1  
**Status:** DESIGN

Mutations:

Move heavy check into focused automatic draft stage; reorder full-gate stages.

Expected result:

Policy validator rejects the mutations.

## TD-CI-003 — Integration candidate cannot bypass final gate

**Abilities:** HA-A19  
**Failure modes:** A19-F04  
**Methods:** EM-02, EM-14  
**Minimum level:** TL1-TL2  
**Oracle:** O1  
**Status:** DESIGN

Expected result:

No path allowlist or trigger topology can waive the final deterministic gate for
an integration candidate.

## TD-ASSURE-001 — Ability denominator detects missing evidence

**Abilities:** HA-A19 plus all release-critical abilities  
**Failure modes:** A19-F06  
**Methods:** EM-14  
**Minimum level:** TL1-TL2  
**Oracle:** O1  
**Status:** DESIGN

Fixture:

All registered executable tests are green, but one release-critical
Ability/FailureMode mapping intentionally has no accepted evidence reference.

Expected result:

Assurance completeness remains incomplete.

This is the critical self-test proving that test inventory is not the
correctness denominator.

## TD-ASSURE-002 — Evidence provenance classification

**Abilities:** HA-A19  
**Failure modes:** misleading evidence strength  
**Methods:** EM-14  
**Minimum level:** TL0-TL1  
**Oracle:** O1  
**Status:** DESIGN

Expected result:

Each evidence reference can state test level, oracle class, execution nature,
and current status so fixture validation cannot masquerade as behavioral proof.

# SF-13 — External semantic evaluator assurance

## TD-EVAL-001 — Malformed/incomplete output fails closed

**Abilities:** HA-A20  
**Failure modes:** A20-F01  
**Methods:** EM-03, EM-12  
**Minimum level:** TL1 deterministic request boundary  
**Oracle:** O1  
**Status:** DESIGN

Expected result:

Malformed, missing, duplicate, or schema-incomplete provider response cannot
produce an accepted semantic verdict.

## TD-EVAL-002 — Exact request binding

**Abilities:** HA-A20  
**Failure modes:** A20-F02  
**Methods:** EM-03  
**Minimum level:** TL1  
**Oracle:** O1  
**Status:** DESIGN

Mutate corpus/protocol/model/run identity after response generation.

Expected result:

Response is rejected as not bound to the active request.

## TD-EVAL-003 — FP/FN calibration

**Abilities:** HA-A20  
**Failure modes:** A20-F03  
**Methods:** EM-12  
**Minimum level:** TL4 calibration track  
**Oracle:** O4  
**Status:** DESIGN

Expected result:

Confusion counts are explicit by judgement class; no "perfect" aggregate hides a
missing class.

## TD-EVAL-004 — Repeated-run stability

**Abilities:** HA-A20  
**Failure modes:** A20-F04  
**Methods:** EM-09, EM-12  
**Minimum level:** TL4  
**Oracle:** O4  
**Status:** DESIGN

Expected result:

Semantic disagreement across repeated identical requests is measured and
reported rather than overwritten.

## TD-EVAL-005 — Drift/recalibration trigger

**Abilities:** HA-A20  
**Failure modes:** A20-F05/F06  
**Methods:** EM-12, EM-14  
**Minimum level:** TL4 operational-assurance track  
**Oracle:** O4  
**Status:** DESIGN

Cases:

Change evaluator model/version, protocol, judgement relation, or introduce a
new observed failure class.

Expected result:

Prior calibration is not silently generalized beyond its declared population.

## TD-EVAL-006 — Oracle independence declaration

**Abilities:** HA-A20  
**Failure modes:** A20-F07  
**Methods:** EM-14  
**Minimum level:** TL0/TL4 metadata + evaluation  
**Oracle:** O4  
**Status:** DESIGN

Expected result:

Evidence explicitly records oracle provenance/independence limits.

# SF-14 — Real-project regression and independent holdouts

## TD-REAL-001 — Known direct-declaration regression

**Abilities:** HA-A21  
**Failure modes:** A21-F02/F03  
**Methods:** EM-10  
**Minimum level:** TL5  
**Oracle:** O2  
**Status:** DESIGN

Use a pinned known project that directly declares Harness logical inputs.

Purpose:

System/regression evidence only after responsible lower-level mechanisms are
green.

## TD-REAL-002 — Known adapter-projection regression

**Abilities:** HA-A21, HA-A17  
**Failure modes:** A21-F03  
**Methods:** EM-10  
**Minimum level:** TL5  
**Oracle:** O2  
**Status:** DESIGN

Use a pinned known project whose project-owned adapter projects Harness inputs.

Expected result:

Same generic Harness semantics as direct declaration; no project branch inside
generic evaluator.

## TD-REAL-003 — Independent project-shape holdout

**Abilities:** HA-A21, selected judgement abilities  
**Failure modes:** A21-F02/F04/F05  
**Methods:** EM-11  
**Minimum level:** TL6  
**Oracle:** O3  
**Status:** DESIGN

Selection rule:

Choose by new failure shape, not repository size: e.g. event-driven integration,
plugin/extension, data pipeline, legacy migration, or domain-rich modular app
not used to design the tested mechanism.

Freeze project revision, selected scope, oracle, Harness revision, and
normalization before execution.

Expected result:

Generic Harness contract succeeds without changing generic semantics.

## TD-REAL-004 — Holdout failure is diagnostic, not auto-fix authority

**Abilities:** HA-A21  
**Failure modes:** A21-F05  
**Methods:** EM-11, EM-14  
**Minimum level:** TL6  
**Oracle:** O3  
**Status:** DESIGN

Expected process:

A holdout failure produces a classified assurance finding. It does not
automatically justify adding project-specific generic behavior; root cause must
first be reproduced at the smallest feasible lower test level.

# Full ability coverage map

Every canonical ability now has at least one designed evidence path.

| Ability | Primary design IDs |
|---|---|
| HA-A01 | existing Core acceptance family; model requires EM-01/02/03/04/06 |
| HA-A02 | TD-DEP-001/002/004/005, TD-LIFE-006 |
| HA-A03 | TD-BOOT-G03 plus existing target-state truth-table/mutation evidence |
| HA-A04 | TD-AUTH-001..007, TD-COMP-001, TD-BOOT-E06 |
| HA-A05 | TD-CAP-001..007, TD-COMP-001, TD-BOOT-E06, TD-BOOT-G04/G05 |
| HA-A06 | TD-APP-001..006, TD-COMP-002 |
| HA-A07 | TD-AUTH-005/006, TD-LIFE-005 |
| HA-A08 | TD-CAP-005, TD-ROUTE-003, TD-BOOT-G01/G04/G05 |
| HA-A09 | TD-BOOT-E01..006 |
| HA-A10 | TD-BOOT-G01..005 |
| HA-A11 | TD-BOOT-E05/E06, TD-ROUTE-007 plus existing source-boundary designs |
| HA-A12 | TD-DEP-001..005, TD-SEM-001..006 |
| HA-A13 | TD-AUTH-003/005, TD-APP-004, TD-BOOT-E03, TD-SEM/LIFE controls |
| HA-A14 | TD-DEP-003/006, TD-LIFE-001..006 |
| HA-A15 | TD-COMP-002, TD-BOOT-G03, TD-FRONT-001..003, TD-PUB-001..003 |
| HA-A16 | TD-ROUTE-001..008, TD-COMP-003, TD-BOOT-E06/G05 |
| HA-A17 | TD-BOOT-E01, TD-ROUTE-005, TD-PROJ-001..003, TD-REAL-002 |
| HA-A18 | TD-DIST-001/002 |
| HA-A19 | TD-CI-001..003, TD-ASSURE-001/002 |
| HA-A20 | TD-SEM-006, TD-EVAL-001..006 |
| HA-A21 | TD-LIFE-006, TD-REAL-001..004 |

HA-A01 and portions of HA-A03/HA-A11 intentionally point to existing
deterministic acceptance families rather than creating duplicate new design IDs.
During review, those existing evidence families must be mapped into the
Ability-to-Evidence denominator with explicit level/oracle metadata.

# Dependency graph between test designs

Implementation/review ordering is constrained:

~~~text
SF-01 Capability
SF-02 Authority
SF-03 Dependency
SF-04 Applicability
SF-05 Routing intent oracle
        ↓
TL2 composition: COMP-001/002/003
        ↓
SF-06 Existing-project micro-project
SF-07 Greenfield micro-project
        ↓
TL4 repeated agent runs
        ↓
known real-project regression (TL5)
        ↓
independent holdout (TL6)
~~~

SF-08 through SF-13 deterministic/calibration families can proceed in parallel
when they do not depend on the formation path, but existing evidence should be
reused before new tests are created.

# Implementation-surface decision rules

Do not choose tooling by habit.

Use an existing deterministic validator when:

- the input/output boundary is structured and deterministic;
- O1 invariants are sufficient;
- no agent judgement is bypassed.

Use Scenario Suite when:

- two or more Harness mechanisms compose;
- ordered state transitions or mutations matter;
- the scenario can still use deterministic drivers.

Use a dedicated agent-eval runner when:

- the agent must infer the semantic operation/model from natural-language or
  project evidence;
- repeated clean-context execution is part of the pass criterion;
- semantic normalization is required.

Use real-project Scenario/holdout evidence only after the lower-level design
being generalized is implemented and green.

# Review output required before coding

Before any new executable evidence is added for this catalog, review should
produce:

- designs accepted as READY;
- designs rejected/reworded because oracle is ambiguous;
- designs already satisfied by existing evidence;
- designs that need a new deterministic mechanism before they can be tested;
- designs that require agent execution and therefore need an eval-runner
  architecture;
- the smallest implementation batch.

The first implementation batch should normally be only the smallest READY TL1
cases, not the entire catalog.
