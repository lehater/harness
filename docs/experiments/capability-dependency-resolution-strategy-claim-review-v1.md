# PREP CDR — claim-level Model Context and Domain Strategy review v1

Date: 2026-10-08
Status: **operator hypotheses only; no Authority acceptance, expert oracle or graph writeback**
Harness: experiment/capability-dependency-resolution-v1, PR #220 (Draft)
Pinned source: `lehater/prep@c52ff8ec1a4732285b2b299bf11dca9869fb2fee`

## Scope and result

The preceding workflow inventoried all selected accepted PREP source paragraphs and
bullets but left the Model Context Strategy and Domain Strategy claims unclassified.
This pilot distinguishes **source semantic obligations** from source-document
headings, supporting traceability, excluded scope, application consumers, and
reopening/governance conditions, without adopting any of them as tactical outputs.

`spec/dependency-resolution/project-pilots/prep-strategy-claim-hypotheses-v1.yaml`
contains an exact-text-bound, individually indexed operator hypothesis for each
of **102 selected source units** spanning MC-01, MC-02, TR-01, DS-01, DS-02,
cross-context constraints, ownership exclusions, boundary invariants, consumers
and reopening rules.

The hypotheses are deliberately *not* an accepted semantic classification.

| Provisional class | Units | Meaning for review |
| --- | ---: | --- |
| `TARGET_SEMANTIC_CANDIDATE` | 21 | May constrain a particular draft Tactical Domain output |
| `SHARED_BOUNDARY_CANDIDATE` | 12 | May govern semantics across the two models |
| `NEGATIVE_INVARIANT_CANDIDATE` | 9 | May prevent learner-state conclusions, topology commitments or semantic collapse |
| `APPLICATION_CONSUMER` | 14 | Behavior or consumer contract; not a new domain invariant by default |
| `GOVERNANCE_CONDITION` | 14 | Authority consumers or conditions for revisiting accepted strategy |
| `SCOPE_EXCLUSION` | 17 | No independent owner or mandated implementation; *does not ban the underlying concept* |
| `STRUCTURAL_OR_TRACE_CONTEXT` | 13 | Section/list introductions, `Derived from` lineage and business criticality justification |
| `UNDETERMINED` | 2 | Perspective exploration and cross-context exploration semantic impact unresolved |
| **Total** | **102** | **102 pending semantic reviews; zero accepted output obligations** |

Each unit retains exact accepted wording, source path, source local index and
upstream SHA-256 and semantic-review revision in the resulting worksheet.
The source text is checked against the original immutable snapshot so an
unchanged list index cannot silently authorize a changed source statement.
All proposed links are to the eight previously drafted, not accepted, target
obligations. No new PREP artifacts or graph edges are generated.

### Key distinctions

- MC-01 / DS-01: Goals, capabilities, knowledge kinds, materials and
  relationship meanings may constrain **Preparation Information**; none
  automatically mandates fixed context decomposition, taxonomy or graph topology.
- MC-02 / DS-02: Recorded activities, results, temporal and historical context
  may constrain **Recorded Activity History**; they do not establish personal
  knowledge, mastery, competence or readiness.
- TR-01 and accepted strategic relationship constraints: historical facts may
  relate to current information without redefining the latter. Shared
  relationship semantics are not automatically duplicated domain ownership.
- Accepted Product Capability behavior and strategy consumer descriptions:
  lifecycle operations, selection, external use and exploration can live at
  **Application Design** while consuming accepted domain meanings. A mere
  reference to their source is not a new direct prerequisite.
- `Derived from` is **product-to-strategy traceability**, not proof of a direct
  Tactical Domain -> Domain Strategy dependency.
- Exclusions, product non-goals, and reopening conditions are governance and
  boundary evidence, not positive domain entities.
- The interpretation of `EXPLORE-PERSPECTIVES` and use of both contexts in
  exploration remain explicitly unsettled.

## Implementation and fail-closed rules

New `evals.project_strategy_claim_review.build_strategy_claim_review`
consumes the existing unreviewed, deduplicated source responsibility worksheet,
the unaccepted Tactical Domain candidate file, and the 102 exact-source
operator hypotheses. It verifies all source unit indices and original wording,
rejects duplicate/unknown/omitted units, unsupported dispositions, invented
target obligations, contradictory acceptance labels and stale revisions.

A result row records the proposed disposition, optional specific target draft
obligations, optional application/shared consumers, source provenance, and a
review reason. Every row and the enclosing report set:
- `claim_semantically_adjudicated=false`;
- `target_obligation_accepted=false`;
- `direct_provider_necessity_proven=false`;
- `complete_target_output_semantics_proven=false`;
- `automatic_writeback_allowed=false`.

This is exhaustive **accounting within the selected MC/DS source scope**,
not a proof of complete cross-Authority sources or accepted tactical semantics.
A reviewer must assess each claim's applicability, precise target ownership,
shared responsibility and evidence for each proposed obligation link. The
classification can be revised or discarded without retaining compatibility
with this draft.

The disposable `experiment/cdr-live-run` workflow stages the deterministic
`dependency-resolution-strategy-claim-review.json` artifact **before**
the blind Copilot evaluation. The annotations are **not** added to that
evaluator's request; no new real execution is implied by staging.

## Verification and next gate

`tests/test_dependency_resolution_strategy_claim_review.py` is registered in
the full Harness gate; it exercises all 102 recorded source units and
negative cases (missing, repeated, changed, forged, invalid target, stale
revision, self-approval). The structural fixture uses recorded accepted
wording; a real pinned checkout through the manual PREP workflow is needed
to verify the extraction against live PREP files.

Next: prepare an **independent semantic review worksheet** with explicit
owner disposition for disputed assertions and candidate-to-output semantics;
do not bypass PREP's Tactical Domain Authority merely because the source
inventory is complete. Only after actual target artifact acceptance and
directness adjudication may the Engineering Graph be reconsidered.

Neither `lehater/prep` nor `harness/main` was modified.
