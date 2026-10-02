# Harness Ability-to-Evidence Model v0

Status: canonical design blueprint.

## Purpose

Define the assurance denominator for Harness before additional test
implementation is designed or written.

This model answers, for every material Harness responsibility:

- what observable ability must hold;
- which material failure modes could violate it;
- which evidence methods can falsify those failures;
- the minimum useful test level from
  `docs/design/harness-assurance-policy-v0.md`;
- the minimum acceptable oracle class;
- what constitutes a pass;
- which evidence is deterministic versus judgement-dependent;
- where current evidence is sufficient, partial, or absent.

This document is intentionally **design before implementation**. It does not
require a specific validator, Scenario Suite case, pytest layout, fixture
directory, or agent-eval runner. Those implementation choices follow only after
the evidence contract is accepted.

## Relationship to other assurance owners

~~~text
Harness Assurance Policy
    defines evidence-selection rules, TL0-TL6, and oracle classes
        ↓
Harness Ability-to-Evidence Model
    defines the assurance denominator and required evidence
        ↓
test/eval design specifications
    define fixtures, protocols, normalization, and assertions
        ↓
validators / tests / Scenario Suite / eval runners
    execute the evidence
        ↓
CI Execution Policy
    decides when registered deterministic evidence runs
~~~

The Scenario Suite is one evidence provider. It is not the denominator.

The CI registry is one execution inventory. It is not the denominator.

An audit records observed coverage and defects. It is not the normative owner of
this model.

## Terminology

### Ability

A stable externally observable responsibility that Harness, or the
agent-enabled Harness operating model, claims to perform.

Ability IDs in this document are canonical assurance identifiers. They are not
Core entities and do not become project-domain state.

### Failure mode

A materially wrong observable result that would invalidate an ability.

Failure modes are phrased independently of the current implementation so they
survive refactors.

### Evidence method

A reusable proof technique. One test may use several methods.

### Minimum test level

The smallest TL0-TL6 scope capable of falsifying the failure mode without
bypassing the behavior under test.

"Minimum" does not mean "only". Larger evidence may supplement it, but cannot
replace it when the smaller oracle is required by the Assurance Policy.

### Pass criterion

The observable condition that must hold. For judgement-dependent abilities this
is semantic equivalence or bounded error, not literal prose equality.

## Evidence method catalog

| ID | Method | Primary use |
|---|---|---|
| EM-01 | Structural/schema contract | Required/forbidden shape, references, registration, inventory |
| EM-02 | Positive/negative example | Known valid and invalid behavior with direct expected outcome |
| EM-03 | Mutation test | Start from accepted state, change/remove one fact, assert exact reaction |
| EM-04 | Property/invariant test | General safety property across generated or enumerated states |
| EM-05 | Metamorphic test | Meaning-preserving/noise/reorder transformation should preserve semantic result |
| EM-06 | Deterministic regression | Reproduce a previously observed defect or boundary |
| EM-07 | Controlled composition | Exercise a short chain of separately owned mechanisms |
| EM-08 | Synthetic micro-project E2E | Exercise one project-shaped bounded procedure with authored oracle |
| EM-09 | Repeated clean-context agent eval | Measure semantic convergence of judgement-dependent behavior |
| EM-10 | Known real-project regression | Verify lower-level evidence survives understood real complexity |
| EM-11 | Independent holdout | Challenge portability/generalization on frozen external project/domain |
| EM-12 | Expert/calibration evaluation | Measure semantic evaluator/agent decisions against independent labels |
| EM-13 | Scale/stress test | Depth, breadth, cardinality, recomputation, runtime/memory envelope |
| EM-14 | Assurance meta-test | Verify evidence inventory, denominator coverage, provenance, and required mappings |
| EM-15 | Fault/crash/concurrency injection | Verify atomicity, stale-writer, interruption, retry, and publication semantics |

Methods describe proof shape, not implementation framework.

## Canonical ability catalog

The following IDs promote the audit-local AB-01..AB-21 model into stable
assurance identifiers.

| Ability | Observable contract | Execution nature |
|---|---|---|
| HA-A01 Core structural truth | Invalid ownership, dependencies, providers and Question references are rejected; valid Core state has deterministic ownership/blocking semantics. | Deterministic |
| HA-A02 Engineering Graph topology | Production ownership, prerequisites, acyclicity, liveness, and Consumer closure are valid and deterministic. | Deterministic |
| HA-A03 Target-state action semantics | CREATE/WAIT/PENDING/COMPLETE and prerequisite/blocker reactions are deterministic and cannot bypass required knowledge. | Deterministic |
| HA-A04 Authority boundary formation | Accepted decision/knowledge surfaces are grouped into cohesive independently changeable Authorities without arbitrary split/merge or joint-ownership leakage. | Judgement-dependent formation + deterministic validation |
| HA-A05 Capability discovery and granularity | Required project knowledge becomes the right project-specific Capability set, including novel knowledge absent from Reference Model templates, without omission, duplication, invention, or wrong granularity. | Judgement-dependent formation + deterministic validation |
| HA-A06 Applicability and Engineering Coverage | REQUIRED/N/A/UNKNOWN/QUESTION dispositions follow evidence; silence cannot become N/A; omitted territory remains visible. | Mixed |
| HA-A07 Project Authority assessment and migration | Authority applicability/status is preserved, reopened, split, retired, or migrated conservatively without unsupported inheritance. | Mixed |
| HA-A08 Design target selection | Selected scope/Consumer closure contains the knowledge required to proceed and excludes workflow/task concepts that are not engineering knowledge. | Judgement-dependent selection + deterministic evaluation |
| HA-A09 Existing-project bootstrap/reconcile | Existing canonical truth is reused, only the smallest needed Harness projection is formed, unknowns remain explicit, and unchanged reruns are idempotent. | Judgement-dependent procedure + deterministic mechanisms |
| HA-A10 Greenfield bootstrap | Explicit goal/scope can become a minimal valid initial engineering model and safe first frontier without pre-authored graph truth. | Judgement-dependent procedure |
| HA-A11 Source acquisition and completeness | Relevant accepted source boundaries are selected; once selected, source units/statements/scope atoms are completely dispositioned before completeness is claimed. | Judgement-dependent selection + deterministic completeness |
| HA-A12 Semantic derivation and admission | Required upstream semantics are preserved/transformed/constrained/realized without silent loss, cross-Authority invention, unsupported provenance, or contradiction. | Mixed; semantic judgement may be delegated |
| HA-A13 Questions and blockers | Genuine unresolved semantics become Questions owned by the deciding Authority; process/implementation failures do not become semantic Questions; resolution changes accepted knowledge. | Mixed |
| HA-A14 Lifecycle, currentness, replay, and graph evolution | Material semantic/prerequisite/policy changes invalidate downstream knowledge; replay is safe; graph evolution does not silently transfer or lose acceptance. | Deterministic |
| HA-A15 Decision/frontier orchestration and publication | Decision state, semantic gaps, coverage, failures, blockers, retries, and publication compose into one coherent next-action/project revision without false COMPLETE or partial visibility. | Deterministic composition |
| HA-A16 Agent/method/artifact routing | Task intent reaches the intended operation; deterministic routers enforce public/internal authorization; CREATE reaches the correct skill; non-actionable work is not executed. | Judgement-dependent selection + deterministic routing |
| HA-A17 Repository realization and projections | Repository/workspace/frontend/human projections derive from accepted truth and fail closed on missing structural or semantic prerequisites. | Deterministic/mixed |
| HA-A18 Consumer distribution and compatibility | A project gets a pinned reproducible public Consumer Pack; incomplete/incompatible/private-surface leakage fails closed. | Deterministic |
| HA-A19 CI and validation execution policy | Checks/workflows are inventoried, cost/stage rules hold, draft execution stays selective, and integration candidates cannot bypass required deterministic gates. | Deterministic/meta |
| HA-A20 External semantic assurance | Provider-backed judgement is request-bound, blinded where required, fail-closed, calibrated, and bounded by explicit corpus/provider/version evidence. | Judgement-dependent assurance |
| HA-A21 Cross-project portability | Generic Harness contracts operate across materially different project shapes without project-specific branches inside generic evaluation. | System/generalization |

## Ability-to-evidence summary

This table defines the minimum intended assurance shape. It does not claim that
the current repository already satisfies every row.

| Ability | Critical failure classes | Primary methods | Minimum useful TL | Minimum oracle | Judgement repetition? |
|---|---|---|---|---|---|
| HA-A01 | invalid accepted; valid rejected; ownership/reference ambiguity | EM-01/02/03/04/06 | TL0-TL1 | O1 | No |
| HA-A02 | duplicate producer; cycle; dead production; wrong closure; depth failure | EM-01/02/03/04/06/13 | TL1-TL2 | O1 | No |
| HA-A03 | false COMPLETE; wrong CREATE/WAIT/PENDING; blocker bypass | EM-02/03/04/07 | TL1-TL2 | O1 | No |
| HA-A04 | wrong split; wrong merge; overlap; unstable boundary; reference bias | EM-02/05/08/09/11/12 | TL1 then TL3-TL4 | O1 for synthetic; O3/O4 for generalization | Yes |
| HA-A05 | omission; invention; duplicate; wrong granularity; template bias | EM-02/03/05/08/09/11/12 | TL1 then TL3-TL4 | O1 for synthetic; O3/O4 for generalization | Yes |
| HA-A06 | wrong N/A; silent omission; UNKNOWN collapsed; wrong scope activation | EM-02/03/04/07/11 | TL1-TL2 | O1; O3 for portability | Only upstream fact discovery |
| HA-A07 | unsupported inheritance; lost applicability; wrong split/retire migration | EM-02/03/06/07/10 | TL1-TL2 | O1/O2 | Only if agent forms migration |
| HA-A08 | missing target knowledge; overbroad target; task-as-knowledge; unstable selection | EM-02/05/08/09/11 | TL1 then TL3-TL4 | O1/O3/O4 | Yes |
| HA-A09 | duplicate truth; whole-repo overreach; hidden unknown; non-idempotent rerun | EM-03/05/07/08/09/10 | TL2-TL4 | O1 then O2/O3 | Yes |
| HA-A10 | premature graph; omitted foundational knowledge; invented structure; unsafe first frontier | EM-05/08/09/11 | TL3-TL4 | O1 then O3/O4 | Yes |
| HA-A11 | missed source; irrelevant source; incomplete boundary; silent undispositioned atom | EM-02/03/05/08/09/10 | TL1 for completeness; TL3-TL4 for selection | O1/O2/O4 | Yes for source selection |
| HA-A12 | semantic loss; unsupported invention; bad provenance; contradiction accepted | EM-02/03/05/07/10/12 | TL1-TL2 | O1; O4 where delegated | Only delegated judgement |
| HA-A13 | missing Question; wrong owner; false Question; unchanged-resolution; blocker leak | EM-02/03/04/07/09 | TL1-TL2 | O1 | Agent compliance selectively |
| HA-A14 | stale remains current; current becomes stale; replay ordering; identity transfer; migration crash | EM-02/03/04/06/07/13 | TL1-TL2 | O1 | No |
| HA-A15 | conflicting frontiers; failed work becomes READY; partial publication; stale writer; false COMPLETE | EM-03/06/07/15 | TL2-TL3 | O1 | No |
| HA-A16 | wrong operation from intent; unauthorized internal route; wrong skill; WAIT executed; prompt-data controls routing | EM-02/05/07/08/09 | TL1 deterministic; TL3-TL4 intent/compliance | O1/O4 | Yes for intent/compliance |
| HA-A17 | projection becomes second truth; missing prerequisites ignored; inconsistent realization | EM-02/03/07/08/10 | TL1-TL3 | O1/O2 | Usually no |
| HA-A18 | unpinned pack; private surface leak; missing contract; incompatible upgrade accepted | EM-01/02/03/06/10 | TL1-TL2 | O1/O2 | No |
| HA-A19 | unregistered check; wrong stage; expensive draft work; final-gate bypass; assurance denominator missing | EM-01/02/03/14 | TL0-TL2 | O1 | No |
| HA-A20 | malformed run accepted; request mismatch; evaluator FP/FN; drift; provider-specific bias | EM-03/05/09/12 | TL4 plus calibration track | O4 | Yes |
| HA-A21 | generic behavior requires project branch; works only on co-design projects; holdout failure | EM-10/11/13 | TL5-TL6 | O2 then O3 | Only if tested path contains judgement |

## Detailed failure-mode design

### HA-A01 — Core structural truth

Failure modes:

- **A01-F01 invalid ownership accepted** — artifact/provider/Question ownership
  violates Core invariants but validation succeeds.
- **A01-F02 valid ownership rejected** — legal same-Authority/multi-provider or
  Question structure is rejected.
- **A01-F03 dangling reference accepted** — dependency, provider, blocker, or
  resolution target does not exist but state is accepted.
- **A01-F04 ambiguous result** — identical valid input yields different
  owner/blocking/affected semantics.
- **A01-F05 invalid Question resolution accepted** — unchanged or unrelated
  accepted knowledge clears a Question.

Required design:

- TL0 schema/static contract for representational invariants;
- TL1 positive/negative/mutation cases;
- property generation for reference/ownership combinations where economical;
- O1 hand-authored invariants;
- literal deterministic assertions are sufficient.

Pass: every invalid state fails closed with the intended error class and every
valid state produces one deterministic structural interpretation.

### HA-A02 — Engineering Graph topology

Failure modes:

- **A02-F01 duplicate/ambiguous Capability production**;
- **A02-F02 cyclic production topology accepted**;
- **A02-F03 dead/unreachable public Capability accepted when prohibited**;
- **A02-F04 Consumer recursive closure misses or invents prerequisites**;
- **A02-F05 graph result depends on declaration ordering**;
- **A02-F06 valid deep/broad graph fails because of implementation recursion or
  pathological traversal**.

Required design:

- TL1 graph fixtures and generated property cases;
- metamorphic reorder tests;
- TL2 closure interaction with target-state/profile;
- separate scale/depth fixtures under EM-13;
- O1.

Pass: normalized topology/closure is identical under irrelevant ordering and
valid graphs inside the declared support envelope do not fail for implementation
depth reasons.

### HA-A03 — Target-state action semantics

Failure modes:

- **A03-F01 false COMPLETE** with missing provider/prerequisite/evidence;
- **A03-F02 CREATE emitted although an existing provider must be admitted or
  revalidated**;
- **A03-F03 WAIT/PENDING/blocked work incorrectly becomes actionable**;
- **A03-F04 upstream blocker does not propagate**;
- **A03-F05 equivalent state representations produce different action**.

Required design:

- TL1 truth-table fixtures;
- mutation from known COMPLETE states;
- TL2 composition with graph, Questions, lifecycle, and routing;
- O1.

Pass: every material state vector maps to one expected action and monotonic
removal of evidence cannot preserve COMPLETE unless the removed evidence is
provably irrelevant.

### HA-A04 — Authority boundary formation

Failure modes:

- **A04-F01 over-split** — one independently changing semantic surface becomes
  several Authorities without an independent lifecycle/public contract;
- **A04-F02 over-merge** — independently changing/publicly separable surfaces
  are forced into one Authority;
- **A04-F03 joint ownership leak** — one canonical decision is effectively
  owned by several Authorities;
- **A04-F04 boundary follows file/module/team layout instead of semantic
  responsibility**;
- **A04-F05 Reference Model bias** — reusable template boundaries override
  project evidence;
- **A04-F06 instability** — clean contexts partition the same decision atoms
  materially differently.

Required design:

1. TL1 synthetic semantic atom sets with explicit expected partition.
2. Positive split, positive merge, overlap trap, and irrelevant-layout
   metamorphic variants.
3. TL2 composition with Capability/dependency formation.
4. TL3 controlled micro-project.
5. TL4 repeated clean-context comparison using pairwise atom-partition
   agreement.
6. TL6 independent holdout only after TL1-TL4 are credible.

Oracle:

- O1 for deliberately constructed synthetic atom sets;
- O3/O4 for unfamiliar/project-realistic judgement.

Pass is semantic partition agreement, not Authority-name equality.

### HA-A05 — Capability discovery and granularity

Failure modes:

- **A05-F01 omission** — independently necessary engineering knowledge is not
  represented;
- **A05-F02 invention/over-generation** — unsupported Capability is created;
- **A05-F03 duplicate semantic Capability** under different names;
- **A05-F04 over-split granularity** — one independently provable/lifecycle
  surface is fragmented;
- **A05-F05 over-merge granularity** — separately provable/changeable knowledge
  is collapsed;
- **A05-F06 Reference Model vocabulary bias**;
- **A05-F07 novel project Capability missed because no template exists**;
- **A05-F08 unstable Capability set across clean contexts**.

Required design:

1. TL1 minimal accepted-fact/decision fixtures with one expected Capability.
2. TL1 negative fixtures where plausible vocabulary must produce no Capability.
3. TL1 paired granularity fixtures: merge-required and split-required.
4. TL2 dependency/applicability composition.
5. TL3 micro-project with at least one novel Capability and one lexical trap.
6. TL4 repeated clean-context semantic matching.
7. TL6 holdout for generalization only after lower levels pass.

Primary measures:

- obligation recall;
- invention precision;
- duplicate semantic identity count;
- granularity match after semantic normalization;
- pairwise run convergence.

Oracle: O1 synthetic, O3/O4 generalization.

### HA-A06 — Applicability and Engineering Coverage

Failure modes:

- **A06-F01 silence becomes NOT_APPLICABLE**;
- **A06-F02 REQUIRED becomes optional/unknown without evidence**;
- **A06-F03 UNKNOWN becomes COMPLETE**;
- **A06-F04 irrelevant concern is activated and creates false work**;
- **A06-F05 required subject/concern territory is omitted from denominator**;
- **A06-F06 scope narrowing/broadening changes unrelated obligations**.

Required design:

- TL1 disposition truth table;
- mutation from accepted coverage by deleting evidence;
- metamorphic unrelated-concern additions;
- TL2 composition with Reference Model, Questions, and Consumer closure;
- independent holdout only for fact/template generalization.

Pass: every coverage atom has explicit evidence-backed terminal/nonterminal
disposition and no silence contributes to completion.

### HA-A07 — Project Authority assessment and migration

Failure modes:

- **A07-F01 retired Authority remains active without evidence**;
- **A07-F02 split Authorities inherit applicability indiscriminately**;
- **A07-F03 merge loses a previously required obligation**;
- **A07-F04 unchanged Authority unnecessarily reopens**;
- **A07-F05 migration depends on identifier spelling rather than accepted
  semantic identity/evidence**.

Required design:

- TL1 split/merge/retire fixtures;
- mutation from accepted assessment;
- TL2 composition with lifecycle/coverage;
- TL5 real-project migration regression where available;
- O1/O2.

Pass: migration is conservative: uncertainty remains explicit and acceptance is
never transferred to a new semantic owner without evidence.

### HA-A08 — Design target selection

Failure modes:

- **A08-F01 missing design knowledge** causes downstream implementation
  invention;
- **A08-F02 unnecessary knowledge** broadens scope;
- **A08-F03 task/workflow/delivery state is modeled as engineering knowledge**;
- **A08-F04 selected target is Reference-template driven rather than
  scope/evidence driven**;
- **A08-F05 clean runs select materially incompatible target closures**.

Required design:

- TL1 bounded scope-to-obligation cases;
- negative cases for task/process pseudo-capabilities;
- TL3 micro-project with explicit downstream implementation obligations;
- TL4 repeated selection on frozen scope;
- TL6 only for portability claims.

Pass: selected closure contains every oracle-required engineering obligation,
contains no prohibited workflow pseudo-knowledge, and converges semantically.

### HA-A09 — Existing-project bootstrap/reconcile

Failure modes:

- **A09-F01 duplicates existing canonical truth**;
- **A09-F02 invents a second graph instead of projecting project-owned truth**;
- **A09-F03 scans/models unrelated repository territory despite selected scope**;
- **A09-F04 converts insufficient evidence into guessed truth instead of
  Question/UNKNOWN**;
- **A09-F05 unchanged rerun changes project model or creates additional work**;
- **A09-F06 misses reusable existing providers/projections**.

Required design:

- TL2 deterministic projection/reuse composition;
- TL3 synthetic existing-project micro-project with partial Harness metadata;
- metamorphic addition of irrelevant repository files;
- repeated unchanged bootstrap for idempotence;
- TL4 fresh-agent runs because source/model selection is judgement-dependent;
- TL5 known-project regression after TL3/TL4.

Pass: normalized second run is semantically identical to the first; no duplicate
truth; unknowns remain explicit; unrelated files do not change selected model.

### HA-A10 — Greenfield bootstrap

Failure modes:

- **A10-F01 goal becomes an overbuilt project model**;
- **A10-F02 foundational knowledge omitted**;
- **A10-F03 guessed architecture/domain truth is accepted without evidence**;
- **A10-F04 first frontier permits downstream work before prerequisites**;
- **A10-F05 equivalent goals yield materially incompatible initial models**.

Required design:

- TL3 micro-project/goal fixtures because pre-authored graph inputs would bypass
  the ability;
- minimality and unknown-preservation oracle;
- TL4 repeated clean contexts;
- TL6 only after synthetic convergence.

Pass: model is the smallest oracle-compatible initial model, unresolved
semantics remain Questions/UNKNOWN, and frontier is safe.

### HA-A11 — Source acquisition and completeness

Failure modes:

- **A11-F01 relevant canonical source omitted**;
- **A11-F02 irrelevant/untrusted source promoted into canonical evidence**;
- **A11-F03 selected source boundary loses units/ranges**;
- **A11-F04 semantic atom/statement is left undispositioned while completeness
  is claimed**;
- **A11-F05 source ordering/noise changes semantic selection**;
- **A11-F06 agent follows instruction-like project content instead of treating
  it as evidence**.

Required design:

- TL1 deterministic boundary/completeness fixtures once source is selected;
- mutation deleting/adding one source unit;
- metamorphic reorder/noise;
- TL3 micro-project for actual source selection;
- TL4 agent runs for source selection/trust-boundary behavior;
- O1 for controlled fixtures, O4 where expert source relevance is needed.

Pass: selected boundary and dispositions match oracle; no missing source unit is
silently accepted; hostile content does not acquire instruction authority.

### HA-A12 — Semantic derivation and admission

Failure modes:

- **A12-F01 material upstream semantic atom silently lost**;
- **A12-F02 downstream claim invented without admissible source**;
- **A12-F03 source from undeclared Authority/prerequisite accepted**;
- **A12-F04 contradiction accepted**;
- **A12-F05 irrelevant source changes accepted result**;
- **A12-F06 semantic evaluator accepts/rejects contrary to labelled oracle**.

Required design:

- TL1 positive/negative derivation cases;
- mutation of required atoms;
- metamorphic reorder/irrelevant input;
- TL2 admission + lifecycle composition;
- real-project regression for known semantic-loss defects;
- EM-12 calibration where judgement is delegated.

Pass: every required source obligation is accounted for, every admitted claim has
allowed provenance, contradictions fail closed, and delegated judgement meets
its calibration protocol.

### HA-A13 — Questions and blockers

Failure modes:

- **A13-F01 missing Question for genuinely unresolved semantics**;
- **A13-F02 Question addressed to wrong Authority**;
- **A13-F03 process/tool/implementation failure becomes semantic Question**;
- **A13-F04 Question fails to block affected capability/artifact**;
- **A13-F05 unrelated Question blocks unrelated work**;
- **A13-F06 Question resolves against unchanged semantic acceptance**;
- **A13-F07 stale evaluation reopens a resolved Question**.

Required design:

- TL1 truth-table/negative/mutation fixtures;
- TL2 composition with target state, semantic admission, and lifecycle;
- repeated agent evidence only for classification of ambiguous semantic vs
  process failures.

Pass: Question existence, owner, blocking scope, and resolution identity match
the oracle.

### HA-A14 — Lifecycle, currentness, replay, and graph evolution

Failure modes:

- **A14-F01 changed prerequisite remains CURRENT**;
- **A14-F02 irrelevant change causes unnecessary stale propagation**;
- **A14-F03 acceptance-policy change does not stale prior acceptance**;
- **A14-F04 replay/list order changes current record**;
- **A14-F05 removed Capability causes runtime failure rather than inert history**;
- **A14-F06 rename/split/merge silently transfers acceptance**;
- **A14-F07 changed prerequisite topology is not detected**;
- **A14-F08 valid large/deep lifecycle graph exceeds implementation limits**.

Required design:

- TL1 mutation/property/regression fixtures;
- TL2 composition with graph evolution and semantic closure;
- deterministic replay/order metamorphic tests;
- scale/stress envelope;
- O1.

Pass: currentness depends only on declared current semantic/policy identities and
topology; graph evolution is conservative and deterministic.

### HA-A15 — Decision/frontier orchestration and publication

Failure modes:

- **A15-F01 multiple read models expose contradictory next actions**;
- **A15-F02 FAILED_VALIDATION becomes READY without explicit retry**;
- **A15-F03 blocker/coverage/semantic gap precedence is wrong**;
- **A15-F04 same Capability appears as duplicate work across layers**;
- **A15-F05 terminal completion is persisted partially**;
- **A15-F06 stale writer overwrites a newer project revision**;
- **A15-F07 crash exposes mixed revision**;
- **A15-F08 retry is non-idempotent or bypasses prerequisites**.

Required design:

- TL2 composed scenario matrix;
- mutation of each frontier input;
- EM-15 fault/CAS/crash injection;
- TL3 bounded publication workflow if filesystem/project integration matters;
- O1.

Pass: one coherent frontier/result is visible; publication is atomic at the
declared boundary; retry semantics are explicit and deterministic.

### HA-A16 — Agent/method/artifact routing

Failure modes:

- **A16-F01 natural-language task selects wrong public operation**;
- **A16-F02 internal operation is reachable without authorized parent**;
- **A16-F03 wrong method for canonical concern**;
- **A16-F04 wrong artifact skill for knowledge_kind**;
- **A16-F05 WAIT/PENDING/non-actionable work is routed to production**;
- **A16-F06 grouped CREATE work combines incompatible prerequisite boundaries**;
- **A16-F07 project/tool payload changes instruction authority or route**;
- **A16-F08 fresh contexts select inconsistent operations for same task**.

Required design:

- TL1 deterministic registry/router cases for explicit keys;
- TL2 CREATE/frontier-to-route composition;
- TL3 synthetic task + project fixture for actual operation selection;
- adversarial payload variants;
- TL4 repeated clean-context agent runs for intent/compliance;
- O1 for deterministic routing, O4 or independently authored task-intent oracle
  for agent selection.

Pass: normalized selected operation/route is oracle-compatible; authorization is
enforced; data cannot expand control authority.

### HA-A17 — Repository realization and projections

Failure modes:

- **A17-F01 projection becomes independent source of truth**;
- **A17-F02 stale projection is accepted as current**;
- **A17-F03 missing repository/environment/gate prerequisite is ignored**;
- **A17-F04 frontend/human/workspace projection claims closure with missing
  canonical semantics**;
- **A17-F05 equivalent canonical truth yields inconsistent projections**.

Required design:

- TL1 subsystem fixtures;
- mutation of canonical inputs;
- TL2 cross-projection composition;
- TL3 workspace/repository-shaped scenario;
- TL5 known-project integration regression where valuable.

Pass: projections are reproducibly derivable from accepted canonical inputs and
fail closed when required inputs are absent/stale.

### HA-A18 — Consumer distribution and compatibility

Failure modes:

- **A18-F01 moving/unpinned Harness revision is consumed**;
- **A18-F02 private Maintainer surface leaks into Consumer Pack**;
- **A18-F03 required public route/contract omitted from pack**;
- **A18-F04 incompatible consumer_api accepted**;
- **A18-F05 materialized pack differs from declared distribution manifest**;
- **A18-F06 upgrade breaks published identity without explicit compatibility
  handling**.

Required design:

- TL0/TL1 registry/manifest/pack equality checks;
- mutation of pins/API/routes;
- TL2 wrapper/materialization integration;
- TL5 target-project upgrade regression selectively.

Pass: same immutable input revision yields same public pack; unsupported
compatibility fails closed.

### HA-A19 — CI and validation execution policy

Failure modes:

- **A19-F01 validator/test/workflow exists outside inventory**;
- **A19-F02 check assigned wrong cost/stage**;
- **A19-F03 heavy/exhaustive work runs unnecessarily on draft synchronization**;
- **A19-F04 integration candidate can skip full deterministic gate**;
- **A19-F05 failure ordering spends expensive work before policy guard**;
- **A19-F06 all registered checks pass while an entire Harness ability has no
  evidence obligation**.

Required design:

- TL0/TL1 policy/meta-validator cases;
- workflow mutation tests;
- TL2 assurance meta-test linking ability denominator to evidence references;
- O1.

Pass: execution inventory is complete and valid, and the separate
Ability-to-Evidence denominator can expose missing assurance even when all
registered executable checks are green.

### HA-A20 — External semantic assurance

Failure modes:

- **A20-F01 malformed/incomplete provider output accepted**;
- **A20-F02 response is not bound to exact request/corpus/protocol/model/run**;
- **A20-F03 false-positive/false-negative rate is unknown**;
- **A20-F04 repeated identical requests are materially unstable**;
- **A20-F05 corpus is unrepresentative but broad correctness is claimed**;
- **A20-F06 model/provider change reuses stale calibration**;
- **A20-F07 evaluator shares hidden dependence with the oracle and is presented
  as independent**.

Required design:

- deterministic request-binding/fail-closed TL1 checks;
- expert-labelled calibration corpus;
- repeated clean-context/provider runs under EM-09/12;
- metamorphic cases;
- explicit drift/recalibration triggers;
- O4 for semantic correctness claims.

Pass: the exact deployed evaluator configuration has bounded, reported
corpus-specific error/stability evidence and no claim exceeds the calibrated
population.

### HA-A21 — Cross-project portability

Failure modes:

- **A21-F01 generic evaluator contains project-specific branch/identifier
  knowledge**;
- **A21-F02 mechanism works only on projects that co-designed it**;
- **A21-F03 direct-declaration works but adapter projection does not, or vice
  versa**;
- **A21-F04 project topology/scale shape exposes hidden generic assumption**;
- **A21-F05 independent holdout requires changing generic semantics before it can
  pass**.

Required design:

- TL5 known projects selected by distinct failure shapes;
- TL6 frozen independent project/domain holdouts;
- source inspection/meta-test preventing project-specific generic branches where
  mechanically detectable;
- scale/stress where project shape is the risk;
- O2 for known regression and O3 for holdout.

Pass: project-specific differences remain behind project-owned adapters/data and
the generic Harness contract is unchanged for the holdout.

## Cross-cutting failure classes

Several failure classes span multiple abilities and should not be implemented as
isolated one-off tests for every row.

| Cross-cutting class | Abilities | Preferred shared design |
|---|---|---|
| Omission / false COMPLETE | A03, A05, A06, A08, A11, A12, A15 | Mutation from accepted complete state + ability-specific oracle |
| Over-generation / invention | A04, A05, A08, A09, A10, A16 | Negative synthetic fixtures + semantic normalization |
| Wrong ownership/boundary | A01, A04, A07, A12, A13 | Partition/owner oracle + negative overlap cases |
| Replay/idempotence | A03, A09, A13, A14, A15, A18 | Unchanged rerun + reordered/stale evidence |
| Reference/template bias | A04, A05, A08 | Novel synthetic cases deliberately outside Reference Model |
| Prompt/instruction contamination | A11, A16, A20 | Adversarial evidence payload + control-channel assertions |
| Reproducibility | A04, A05, A08, A09, A10, A11, A16, A20 | Shared clean-context protocol + semantic IR |
| Scale/pathological shape | A02, A14, A17, A21 | Generated depth/breadth/cardinality fixtures |
| Atomicity/recovery | A15, A18 | Fault/CAS/crash injection |
| Assurance self-blindness | A19 plus all | Ability denominator meta-test independent from check inventory |

## Synthetic fixture families to design before implementation

The following fixture families are sufficient to start implementation without a
large real repository.

### SF-01 — Capability identity/granularity

Small accepted evidence sets covering:

- exactly one necessary Capability;
- no Capability;
- two separately provable Capabilities;
- one semantic Capability expressed with multiple vocabulary variants;
- attractive Reference Model template that is irrelevant;
- required project-specific Capability absent from Reference Model.

Primary abilities: HA-A05, HA-A06, HA-A08.

### SF-02 — Authority partition

A small set of decision/claim atoms with:

- mandatory merge;
- mandatory split;
- ambiguous evidence requiring Question rather than confident partition;
- misleading file/module grouping;
- misleading Reference Model grouping.

Primary abilities: HA-A04, HA-A07, HA-A13.

### SF-03 — Dependency necessity

Three to six capabilities where:

- one dependency is required;
- one plausible dependency is unnecessary;
- one hidden same-Authority semantic dependency must become explicit topology;
- one dependency change must stale exactly the correct downstream set.

Primary abilities: HA-A02, HA-A12, HA-A14.

### SF-04 — Applicability/coverage lattice

Controlled facts spanning REQUIRED, NOT_APPLICABLE, UNKNOWN, and QUESTION,
including silence and contradictory evidence.

Primary ability: HA-A06.

### SF-05 — Routing intent

Short natural-language tasks with independent intended operation plus
distractors, internal-route authorization variants, and instruction-like
project payloads.

Primary ability: HA-A16.

### SF-06 — Existing-project bootstrap micro-project

A tiny repository containing:

- existing project-owned graph-like truth;
- partial Harness metadata;
- unrelated files;
- one missing semantic fact;
- one reusable provider;
- one project-specific Capability;
- one misleading template vocabulary match.

Primary abilities: HA-A04, A05, A09, A11, A16.

### SF-07 — Greenfield bootstrap micro-project

A tiny explicit goal/scope with enough evidence to require a minimal initial
model while leaving at least one architectural/domain decision unresolved.

Primary abilities: HA-A05, A08, A10, A13, A16.

### SF-08 — Semantic derivation/admission

Small upstream/downstream semantic atom sets with loss, contradiction,
unsupported provenance, irrelevant input, and accepted transformation controls.

Primary ability: HA-A12.

### SF-09 — Lifecycle/evolution

Generated graph/state pairs covering semantic/policy change, prerequisite
topology change, rename/split/merge, stale replay records, and deep/broad DAGs.

Primary abilities: HA-A02, A14.

### SF-10 — Frontier/publication

Controlled cross-layer states plus stale-writer/interruption fault cases.

Primary ability: HA-A15.

## Judgement-dependent normalization contract

TL4 comparisons must not use literal generated prose as the correctness oracle.

Normalize relevant runs to a semantic intermediate representation containing the
subset required by the tested ability:

- accepted source/evidence identities;
- Authority membership over decision/claim atoms;
- Capability semantic identity:
  subject + knowledge kind + independently provable claim/decision surface;
- prerequisite/dependency edges;
- applicability dispositions;
- Questions and owning Authorities;
- omitted oracle obligations;
- invented obligations;
- selected Consumer closure;
- selected operation/skill identity;
- final frontier/result where relevant.

Names and prose may differ if the semantic identity is equivalent.

## Reproducibility measures

Do not aggregate the following into one opaque score by default:

- obligation recall;
- invention precision;
- duplicate semantic identity count;
- Authority partition agreement;
- Capability-set agreement after semantic matching;
- dependency precision/recall;
- applicability confusion matrix;
- Question-owner accuracy;
- operation-selection agreement;
- Consumer-closure agreement;
- pairwise run convergence;
- oracle agreement.

The specific ability/eval protocol chooses which measures are material and what
threshold is acceptable.

This blueprint intentionally does not set universal numeric thresholds.

## Oracle design rules

1. Freeze the oracle before the system-under-test run.
2. Do not generate expected output with the same implementation being tested.
3. Synthetic TL1-TL3 cases normally use O1 hand-authored contracts.
4. Known real-project regression normally uses O2 accepted project truth.
5. Independent portability holdouts use O3.
6. Blinded semantic judgement/calibration uses O4 where appropriate.
7. If an expected answer is legitimately non-unique, define invariant or
   semantic-equivalence bounds rather than forcing a false single golden answer.
8. Oracle ambiguity is a test-design failure; it must not be hidden as agent
   nondeterminism.

## Current-state design assessment

Baseline for this section: branch `audit/harness-corrections`, commit
`d7ee162505ab39ff8144e9424f779f577b396575`.

This is an implementation-planning snapshot, not a permanent claim. Later audits
may update it without changing the ability contracts above.

### Strongly evidenced deterministic areas

Current repository evidence is already substantial for:

- HA-A01 Core structural truth;
- HA-A02 graph validation/closure, including newly added deep-DAG regression;
- HA-A03 target-state action semantics;
- HA-A06 applicability/coverage after project facts are declared;
- HA-A12 semantic derivation/admission after source/semantic surfaces are
  selected;
- HA-A13 deterministic Question/blocker mechanics;
- HA-A14 lifecycle/currentness mechanics, with current branch corrections for
  replay and graph evolution still requiring their normal focused/re-audit
  completion;
- HA-A15 deterministic frontier/publication mechanisms, with current branch
  correction work still requiring normal verification where backlog items remain
  IN_PROGRESS;
- HA-A18 Consumer Pack/distribution;
- HA-A19 CI execution policy.

### Partially evidenced mixed/judgement areas

Current evidence is useful but does not prove the full ability for:

- HA-A04 Authority boundary formation;
- HA-A05 Capability discovery/granularity;
- HA-A07 Authority assessment when the assessment itself must be formed by an
  agent;
- HA-A08 Design target selection;
- HA-A09 existing-project bootstrap/reconcile;
- HA-A10 greenfield bootstrap;
- HA-A11 source selection;
- HA-A16 natural-language operation selection and adversarial agent compliance;
- HA-A17 project-shaped realization/projection integration;
- HA-A20 external semantic assurance representativeness;
- HA-A21 portability beyond co-design/known-project evidence.

### Highest-information missing evidence

The first new implementation work should target the lowest missing proof layer,
not the largest end-to-end scenario:

1. SF-01 Capability identity/granularity at TL1.
2. SF-02 Authority partition at TL1.
3. SF-03 dependency necessity at TL1/TL2.
4. SF-05 task-intent routing at TL1 for the semantic oracle, then TL3/TL4 for
   actual agent selection.
5. Compose SF-01/SF-02/SF-03 into SF-06 existing-project micro-project.
6. Only then add TL4 repeated clean-context execution.
7. Use known real projects after the synthetic mechanisms converge.
8. Add TL6 independent holdout last.

## Design-to-implementation handoff

Implementation must not begin by translating every row into a new test file.

For each planned evidence item, first create a compact test design record:

~~~text
test_design_id
ability
failure_modes
method_ids
test_level
fixture_family
oracle_class
input boundary
expected semantic result / invariants
normalization
pass criterion
negative/control cases
current evidence reused
new implementation needed
CI disposition candidate
~~~

The design record may map to an existing validator/scenario if that evidence
already satisfies it.

Only gaps require new executable code.

## Implementation ordering rule

Prioritize by:

1. release-critical ability with missing lower-level evidence;
2. false-COMPLETE/wrong-next-action risk;
3. inability to localize failure at current test level;
4. judgement-dependent behavior with no synthetic oracle;
5. repeated known real-world failure;
6. portability/generalization after lower levels are stable.

Do not prioritize by ease of writing the test or by raw scenario count.

## Non-goals

This blueprint does not:

- define a new Harness runtime entity;
- make Harness Ability IDs part of target-project state;
- require every change to reach TL6;
- prescribe exact file counts or agent-run counts;
- choose pytest versus Scenario Suite versus a dedicated eval runner in advance;
- define universal semantic-quality thresholds;
- require real-project evidence before lower-level synthetic mechanisms are
  designed.

## Concrete test design catalog

The framework-neutral catalog is
`docs/design/harness-test-design-catalog-v0.md`.

It now covers SF-01 through SF-14: isolated formation mechanisms, TL2
composition, existing/greenfield micro-projects, semantic/lifecycle/publication
mechanics, projections/distribution, CI assurance self-tests, evaluator
calibration, and real-project/holdout evidence. Every canonical HA-A01..HA-A21
ability has at least one designed evidence path.

All entries remain design artifacts until oracle/boundary review moves them from
DESIGN to READY. Implementation should begin only from reviewed READY entries.
