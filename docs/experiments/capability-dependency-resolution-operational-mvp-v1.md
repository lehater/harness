# Capability Dependency Resolution — operational MVP (read-only)

Status: **opt-in experimental entrypoints implemented, not routed or canonical**
Harness PR: [#220](https://github.com/lehater/harness/pull/220), Draft.
Sources: exact 40-character Git revision of the project; no dirty tracked files.

## Goal and four checkpoints

**Definition of done for the ultimate CDR capability:** when creating or
revising any Capability, identify materially required *direct* providers from
the target's own independently governed outputs; show traceable source
evidence; distinguish inherited/indirect constraints from direct ones; audit
existing graph for missing or suspect edges; react to changes in accepted
contracts; and apply only adequately reviewed, authorized graph transitions.

**The present MVP provides evidence and review proposals, not accepted
semantic decisions.** Existing PREP evidence demonstrates how including
Domain Strategy quotations as target-output obligations can spuriously
create direct `requires`. The operational route is therefore separated:

1. **Algorithm:** explicit target output obligations and governing constraints
   are input, accepted provider public contracts are discovered from the
   pinned project Core + semantic baseline + Engineering Graph, and agent
   source citations are checked. A textual citation is not semantic proof.
   Target output completeness, provider change counterfactual and independent
   Authority adjudication remain review gates.
2. **Create Capability:** `evals.cdr_operational.prepare_intake` accepts
   `harness-cdr-capability-intake-v1` even for a Capability **not yet
   declared** in the Engineering Graph. It creates a blinded source-only
   discovery request. `evals.cdr_operational.reconcile_intake` checks
   an external evaluator's source-cited predictions on the identical pinned
   project and reports `KEEP`, `ADD`, unresolved outputs, source-echo
   flags, existing transitive access and independent review packets.
   No `requires` list is supplied to the evaluator.
3. **Audit existing graph:** `evals.cdr_graph_audit` is a **separate
   on-demand command**, not invoked when each new Capability is defined.
   It checks duplicate/malformed and unknown direct suppliers, self-edges,
   directed cycles, transitively reachable existing direct edges and reverse
   structural change-impact. Structural transitive paths do **not** prove
   semantic redundancy; no removal proposals or implicit graph rewrites.
4. **Harness integration:** opt-in `make cdr-prepare`,
   `make cdr-reconcile`, and `make cdr-audit` commands and a
   source-pinned synthetic integration test in the full `harness-check`
   CI gate. These commands do **not** run automatically during normal
   Harness Capability creation. Enabling such routing, accepting semantic
   verdicts or canonical `requires` writeback requires a separately
   reviewed lifecycle integration/change. The experimental PR cannot
   silently assume authorization.

## Source contract

`spec/dependency-resolution/project-pilots/prep-operational-intake-v1.yaml`
is a noncanonical **example**, intentionally based on three positive
current-information outputs plus a cross-cutting no-learner-inference
constraint. It is not a PREP accepted Core artifact or expert oracle.

Expected input structure:

```yaml
kind: harness-cdr-capability-intake-v1
version: 1
status: DRAFT_NOT_ACCEPTED
source_commit: <exact forty-character git SHA>
automatic_writeback_allowed: false
target:
  capability: x.example
  authority: TACTICAL
  knowledge_kind: domain-model
  output_obligations:
    - id: SEMANTIC-MEANING
      description: >-
        Define the domain meaning of an identified target output without
        choosing an implementation technology or copying supplier passages.
  governing_constraints:
    - id: NO_UNJUSTIFIED_INFERENCE
      description: >-
        The target output must not assert an unestablished person-state fact.
      applies_to_outputs: [SEMANTIC-MEANING]
```

Input is **operator-authorized draft**, not a source of accepted semantics.
It may constrain model prompting, but no model-proposed edge is adopted.
Provider discovery includes only reviewed Core-registered graph producers.
The exact input and provider inventory are rebuilt before reconciliation,
using the pinned clean checkout, to prevent unseen source revisions.

## Operator commands

From Harness checkout:

```sh
make cdr-prepare PROJECT_ROOT=/path/to/project PROJECT_COMMIT=<sha> \
  CDR_INTAKE=spec/dependency-resolution/project-pilots/prep-operational-intake-v1.yaml \
  CDR_OUTPUT=/tmp/cdr-source-only-input.json
```

This writes a `harness-dependency-resolution-calibration-inputs` corpus
whose case can be passed to the existing externally configured, blinded
`dependency.discovery.execute_process` scenario driver. An external
model's response is still experimental and must be independently checked.
It must be bound to exactly the same case ID, output obligations, and
accepted provider claim indices. The existing process driver has an
external-executable environment and no production mutation interface.

```sh
make cdr-reconcile PROJECT_ROOT=/path/to/project PROJECT_COMMIT=<sha> \
  CDR_INTAKE=spec/dependency-resolution/project-pilots/prep-operational-intake-v1.yaml \
  CDR_PREDICTIONS=/tmp/cdr-predictions.json \
  CDR_OUTPUT=/tmp/cdr-review.json

make cdr-audit PROJECT_ROOT=/path/to/project PROJECT_COMMIT=<sha> \
  CDR_OUTPUT=/tmp/cdr-graph-audit.json
```

A prediction file is a validated source-grounded
`harness-dependency-resolution-predictions` report, not free-form
chat text. No hidden `requires` or evaluator oracle are supplied
upstream. All three commands are read-only against the target repository
and require explicit invocation and explicit output file destinations.

## Governance-review extension

Following the source-grounded reconciliation, two additional explicit
read-only commands prepare and check the review required before any
future decision to adopt a dependency:

- `make cdr-dossier` — assemble accepted-source claims, independent
  target-contract readiness blockers, and five directness questions for
  every proposed added provider.
- `make cdr-check-review` — regenerate that dossier from the same exact
  pinned clean Git project and check an independently prepared
  **PROPOSED_NOT_ACCEPTED** review draft. Its success means only that
  review material is complete enough for Authority consideration,
  never that a new direct edge is approved.

See [CDR governance gate v1](capability-dependency-resolution-approval-gate-v1.md)
for review criteria, commands, provenance and outstanding acceptance
requirements. Even a structurally complete reviewer draft cannot authorize
a project graph rewrite.

## Correctness boundaries

The operational intake verifies shape, target identity, output/constraint
IDs, that references do not point to removed/unknown outputs, and
that source descriptions do not quote a complete public claim or directly
name accepted provider Capability IDs. It rejects stale commits,
dirty tracked projects, unanswered Core questions, mismatched Core
Authority ownership and absent reviewed sources.

**It cannot automatically prove:**
- the target draft represents the complete intended output semantics;
- a cited accepted claim actually entails an output invariant;
- an alternative immediate provider fully mediates a supposedly direct rule;
- absence of a suggested edge establishes that the edge is unnecessary;
- an apparently redundant graph path is a semantically redundant edge.

The reconciliation consequently requires independent review and always
keeps `REMOVE_CANDIDATE=[]`, `semantic_entailment_verified=false`,
`target_contract_independently_accepted=false` and
`automatic_writeback_allowed=false`.

Whole-graph audit is costlier than local creation and intentionally separate.
Reverse-reachability change impact is a **candidate review scope**, not a
proof that all downstream Capabilities must change. Actual **missing**
dependencies cannot be proven from graph structure alone: they require
target output and provider semantic review.

## Known blockers to production routing

1. The pinned PREP Tactical Domain targets do not yet have their own
   independently accepted Core output contracts or semantic reviews.
   The v2 six-outputs/two-constraints document is a **draft**, not an
   independently governed target contract.
2. The independent five-part direct-necessity review is not an executable
   truth oracle. Reviewer approval, authority ownership and actual
   target source acceptance are not established by these tests.
3. This branch intentionally does not modify Harness's default
   Capability-creation orchestration, add production writeback or
   automatically certify a model-generated dependency.

The operational MVP can be evaluated and refined safely without
creating false `requires`. **A production rollout is blocked on the
actual Authority acceptance / governance decision, not on another round
of identical Copilot sampling.**

## Verification

The `tests/test_cdr_operational.py` no-network synthetic Git experiment
creates a new, not-yet-declared Capability, discovers accepted providers,
checks the blinded request, reconciles two source-anchored input needs,
checks failed citations and missing output needs, audits a graph with
one transitive edge, computes reverse change impacts, and detects
unknown suppliers and graph cycles. Additional project experiments remain
read-only and on the feature branch.

No PREP or Harness main changes; no routing activation or graph writes.
