# CDR — independently accepted target-output contract readiness v1

Date: 2026-10-08
Harness research PR: #220 (Draft)
Pinned PREP reference: `lehater/prep@c52ff8ec1a4732285b2b299bf11dca9869fb2fee`
State: **read-only readiness gate implemented, verified in synthetic pinned-project CI; PREP canonical target contract acceptance remains blocked**.

## Discovery: upstream is not the target

The first three real PREP Copilot studies showed that a source section placed
inside a target output obligation can induce an unjustified direct-source
proposal, even when the source is legitimate and reviewed. This led to the
independent-directness criterion.

A separate unresolved issue is that **accepted upstream** source material
does not establish the **target's own independently accepted output contract**.

At the pinned PREP commit:
- Both `prep.preparation-information-model` and
  `prep.recorded-activity-history-model` have production declarations
  under `TACTICAL-DOMAIN-DESIGN` in
  `.harness/engineering-graph.yaml`.
- Neither Capability has a providing Core artifact in `.harness/core.yaml`.
- Neither Capability has its own semantic review revision in
  `.harness/semantic-baseline.yaml`.
- `prep.product-capabilities`, `prep.domain-strategy` and
  `prep.model-context-strategy` **are** accepted, reviewed upstream
  providers. This distinction does not confer acceptance on the two
  Tactical Domain output artifacts.

A production declaration describes intended responsibility and output
kind, not an accepted contract with independently reviewable detailed
obligations. Absence in Core and semantic baseline on this snapshot is a
positive, source-backed blocker, not a model hallucination.

## New deterministic read-only gate

`evals/project_target_contract_readiness.py` reads an exact clean, pinned
Git checkout and checks each requested target against:
1. unique Engineering Graph producer and owning Authority;
2. unique Core artifact that **provides the target Capability**, matching
   producer Authority and resolving to an actual file;
3. the target Capability's own recorded semantic review revision and
   meaningful review basis in the baseline;
4. detectable, distinct, explicit output-obligation IDs when a structured
   YAML target artifact is present;
5. independent acceptance of those **target obligations**, which this
   version explicitly **cannot infer** from registry entries or a review
   statement alone.

The full result is always
`BLOCKED_PENDING_INDEPENDENT_TARGET_ACCEPTANCE`. Cases are
`NOT_INDEPENDENTLY_ACCEPTED`, with granular blockers. Even if every
structural artifact exists, the independent-adjudication blocker is retained
until a separately designed Authority decision mechanism provides
verifiable evidence.

The narrow YAML obligation detector is an experiment-side structural
indicator, **not a new mandatory canonical PREP artifact format**.
Markdown prose is not auto-promoted as a machine-verifiable output
obligation. No source is modified, and neither a reviewer role string nor
an LLM explanation can overwrite these blockers.

This audit is attached to Phase B output as
`TARGET_OUTPUT_CONTRACT_READINESS` per case and
`target_output_contract_readiness` for the whole run.
It is generated only after blind model evaluation, when the canonical
project snapshot is consulted for reconciliation. The readiness state is
never supplied to the evaluated agent as a target oracle.

The temporary `experiment/cdr-live-run` workflow has an additional
non-agent step to generate `dependency-resolution-target-readiness.json`
from the same exact checkout. This is independently useful evidence even
if the provider evaluation later fails, but it is not a live result until
the workflow is manually run again.

## Draft target-owned obligations for future consideration

`spec/dependency-resolution/project-pilots/prep-target-output-candidates-v1.yaml`
contains **broad, deliberately noncanonical candidates**, four per
Tactical Domain Capability:
- Preparation Information: meanings/distinctions; knowledge and
  relationship meanings; semantic boundary with historical facts;
  negative learner-state invariants.
- Recorded Activity History: historical activity/result facts;
  reference semantics; historical-context preservation; negative
  learner-state invariants.

Each candidate points to source **scope sections**, not declared graph
`requires`, and carries `CANDIDATE_NOT_ACCEPTED`. The drafts preserve
scope rather than prescribing technical structures, entity decompositions,
storage design, graph topology or application behavior. They do not belong
in PREP Core and must not be used as an oracle.

The corresponding candidate review questions remain open: perspective
exploration as a semantic constraint; historical exploration versus
application behavior; direct-vs-inherited meaning from Domain Strategy;
and responsibility boundaries within/between model contexts.

## What is still required for an actual approval

The target Authority must decide what the outputs really promise, produce
and accept their own target artifacts under PREP's ordinary governance
when the design reaches that stage, and record target-specific semantic
reviews. A stronger future mechanism must also tie each individual
obligation to independent Authority adjudication and immutable reviewed
source revisions.

Only after that can an independent directness reviewer test actual rule
consumption, sufficiency of retained intermediates and change sensitivity
without quoting an upstream statement as the target obligation.

**No automatic ADD or REMOVE is supported at any point in this v1 research
tool. No changes have been made to PREP or Harness main.**

## Verification

Full Harness tests cover both planned-only targets and a synthetic
registered/reviewed structured target. Neither is misclassified as
independently accepted. Tests also reject stale Git commits, dirty tracked
checkout, duplicate target IDs, and free-form Markdown as if it were
structured target-obligation evidence.

After implementation:
- [Harness core PASS](https://github.com/lehater/harness/actions/runs/37809894901)
- [CI policy PASS](https://github.com/lehater/harness/actions/runs/37809894873)

No new Copilot run is required to establish the source-backed absence of
registered target contracts. An actual live run of the standalone CLI
would confirm the exact generated JSON report on the pinned PREP checkout.
