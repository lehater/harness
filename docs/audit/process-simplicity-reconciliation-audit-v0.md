# Process Simplicity and Reconciliation Audit v0

Status: completed architecture/process audit; implementation proceeds in semantic
slices on a non-main branch.

Date: 2026-10-05

## Scope and evidence boundary

The audit used AP-02, AP-04, AP-05, AP-09, AP-11, AP-13, AP-15, AP-18,
AP-19, AP-20 and AP-22. Evidence came from current Harness canonical
contracts/source/tests plus the current `lehater/prep` default-branch state as
an empirical consumer case. Git history was not used to reconstruct project
semantics.

## Current state

| Component | Responsibility | Input -> output | Persistence / expensive work |
|---|---|---|---|
| Semantic Admission | Strict acceptance of one Capability | graph + Core + candidate + source/evidence + lifecycle -> semantic evaluation + lifecycle assertion | Recomputes current policy fingerprints and lifecycle currentness; Decision Governance is evaluated after artifact semantics. |
| Capability Lifecycle | Currentness projection | accepted identities/fingerprints + graph -> CURRENT/STALE/UNKNOWN | Derived; exhaustive dependency baselines can be large. |
| Decision Pipeline | One READY Capability decision/execution contract | roadmap item + candidate/evidence -> terminal Capability outcome | Procedure explicitly publishes one result, recomputes roadmap, then continues. |
| Project Publication | Atomic visibility/CAS owner | current revision + coherent component snapshot -> next revision | Whole-snapshot YAML; direct-file adapter is crash-safe and CAS guarded. |
| Semantic Closure | Strict target semantic/currentness closure | graph + publication evidence + policies -> COMPLETE/INCOMPLETE | Derived; evaluates target closure and policy currentness. |
| Project Frontier | Aggregate next-action read model | structural + decision + semantic + coverage sources -> one ordered frontier | Derived/disposable; already exposes structural and semantic source status. |
| Project bootstrap reconcile | Start/reconcile project model and applicability | selected project/scope -> reconciled registry/Core/status | Agent procedure; does not own semantic revalidation-to-publication. |
| Consumer API/router | Typed procedure discovery and instruction delivery | operation/method/knowledge kind -> skill + instruction contracts | Consumer Pack sync/materialization is an external setup boundary. |

The important architectural fact is that Harness already owns the primitives
needed for reconciliation but does not own their repeated application-level
coordination.

## Findings

### P1 — Reconciliation orchestration is outside its natural application owner

`decision-pipeline` requires the coordinator to publish a terminal Capability,
recompute the roadmap and continue. No bounded application operation owns the
multi-Capability loop. A consumer therefore has to assemble lifecycle,
admission, closure, coverage and publication itself.

Current `prep/main` contains `tools/full_harness_revalidate.py`, which imports
multiple Harness subsystems and manually composes this generic loop. That is
direct evidence of project-side glue around a generic Harness responsibility.

**Root cause:** orchestration semantics exist in a skill/prose loop but not in
an Application service boundary.

### P1 — Cheap deterministic decision failures are discovered too late

`semantic_admission.admit_artifact` evaluates artifact semantics before
Decision Exploration / execution assurance / Decision Governance. Governance
errors such as an invalid DETERMINED disposition or insufficient delegation
autonomy do not require full semantic admission to detect.

**Root cause:** the decision validators are composable pure mechanisms, but
there is no preflight application surface and admission ordering does not expose
a cheap rejection boundary.

### P1 — Per-Capability publication amplifies external coordination cost

Atomic Project Publication is correct and must remain the visibility boundary.
The Decision Pipeline procedure, however, makes a terminal publication after one
Capability before recomputing the next item. When several deterministic stale
Capabilities can be revalidated without Authority input, this exposes internal
coordination as repeated publication/commit/CI opportunities.

**Root cause:** atomic publication and unit-of-orchestration are coupled more
tightly than the invariant requires.

### P2 — Publication physical representation duplicates large evidence

The current Prep publication is 1,397,298 bytes / 22,256 lines. Approximate
serialized section sizes are:

- Core model: 10,116 characters;
- semantic evaluations: 1,021,434 characters;
- lifecycle: 365,430 characters;
- decision failures: 92 characters.

The size is therefore dominated by semantic/lifecycle evidence, not Core.
Semantic evaluations also embed lifecycle assertions while the publication
persists a separate lifecycle projection. This is a measurable representation
cost, but not yet a correctness defect and not sufficient evidence to introduce
content-addressed storage immediately.

### P2 — Disposable candidate workbench accumulates durable clutter

Current Prep has 268 files under `.harness/candidates` totaling about
1.68 MB. The canonical Agent Artifact Workbench explicitly defines that
location as disposable and says candidates should be deleted or moved when the
experiment ends.

**Root cause:** lifecycle/retention responsibility for disposable workbench
material is documented but not operationally enforced or surfaced.

### P0 — none found in audited scope

Project Publication already provides deterministic revision identity, CAS and
atomic visibility. Acceptance identity remains caller/admission owned, and the
structural-vs-semantic distinction is already represented in Project Frontier.
The simplification work must preserve these boundaries.

## Complexity map

```text
semantic change
    -> project/agent determines affected capabilities
    -> repeated policy/currentness derivation
    -> candidate/decision validation
    -> one-capability admission
    -> whole publication assembly/serialization
    -> publish
    -> recompute roadmap/frontier/closure
    -> repeat externally
```

The dominant design smell is not Python computation itself. The expensive shape
is the number of coordination transitions: project scripts, publication writes,
commits, Consumer Pack/CI startups and repeated full read-model derivations.

Harness repository CI has already adopted the correct local principle for its
own development: affected deterministic checks during iteration and full gates
at coherent checkpoints. Consumer reconciliation lacks an equivalent
application boundary.

## Architecture options

### A — Extend the existing Decision Pipeline procedure

Keep the runtime primitives unchanged and teach the skill to batch more work and
preflight decisions.

Advantages: smallest code change and no new application module.

Weakness: generic orchestration remains agent/project responsibility; resumable
or incremental behavior is still procedural and difficult to test as one
contract. This does not remove the root cause.

### B — Bounded Reconciliation Application Service

Add one Application service over existing lifecycle/admission/frontier/
publication primitives. It derives affected work, performs cheap preflight,
reuses unaffected CURRENT state, aggregates independent blockers and assembles
one final publication. Intermediate state is derived/non-current. Resume is
bound to current publication revision plus plan/input fingerprints; no second
semantic store is introduced.

Advantages: puts generic mechanics in Harness, preserves existing bounded
contexts and Project Publication, supports one-session UX, and remains
deterministically testable.

Cost: requires a new application contract and Consumer surface wiring.

### C — Persisted reconciliation transaction/session engine

Persist working steps, completed actions, blockers and resume state as a durable
transaction.

Advantages: strongest restartability and maximal compute reuse.

Weakness: introduces another lifecycle/state machine, persistence/migration
semantics and a coordination source that can drift from Project Publication.
Current evidence does not justify that complexity.

## Recommended target

Choose **B**.

The reconciliation service is an Application coordinator, not a new domain
aggregate. Project Publication remains the sole current-state visibility
boundary. Lifecycle, admission, Decision Governance, Coverage and Core keep
their existing invariant ownership.

Initial resume should be a revision/fingerprint-bound continuation token rather
than durable workflow state. If real measurements later show that recomputing
the bounded plan is expensive, a disposable cache can be added independently.

## Implementation slices

1. **S1 — global Process Simplicity and Efficiency contract.** Route it to every
   skill as a global instruction contract and make orchestration/ownership
   validation aware of it.
2. **S2 — decision preflight.** Expose Decision Exploration/Governance checks
   before full semantic artifact evaluation and reuse the same function inside
   strict admission.
3. **S3 — reconciliation plan/read model.** Derive selected target status,
   affected/stale frontier, unchanged CURRENT capabilities and independent
   blockers without mutating publication.
4. **S4 — incremental deterministic revalidation.** Execute only affected
   capabilities for which all semantic/evidence inputs and real acceptance
   identities are supplied; never fabricate identity/rationale.
5. **S5 — blocker frontier + continuation token.** Return all safely independent
   blockers and bind continuation to publication revision/plan fingerprint.
6. **S6 — one final publication.** Assemble the coherent next snapshot and use
   existing CAS/atomic publish once.
7. **S7 — Consumer API/skill integration.** Make the existing
   project-bootstrap/reconcile responsibility invoke the application service
   rather than requiring project-side glue.
8. **S8 — persistence compaction only if measured.** Benchmark parse/serialize/
   diff/tooling costs before choosing inline/content-addressed/hybrid v2.
9. **S9 — candidate retention/diagnostics.** Distinguish durable evidence from
   disposable workbench/cache output and provide cleanup/diagnostic guidance.

## Required regression scenarios

The implementation must cover policy staleness propagation, unaffected branch
reuse, multiple independent blockers, preflight rejection, continuation after a
blocker, no fabricated acceptance identity, single atomic publication, CAS
conflict, final semantic closure and legacy publication compatibility.
