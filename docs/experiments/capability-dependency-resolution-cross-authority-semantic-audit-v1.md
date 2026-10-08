# PREP CDR — joint semantic audit of eight proposed Tactical Domain outputs

Date: 2026-10-08
Research status: **noncanonical, read-only, not independently adjudicated**
Harness PR: [#220](https://github.com/lehater/harness/pull/220) (Draft)
Immutable PREP source: `lehater/prep@c52ff8ec1a4732285b2b299bf11dca9869fb2fee`

## Purpose

The earlier experiments examined the two PREP Tactical Domain Capabilities
from multiple directions: a bounded inventory of accepted source statements,
responsibility-routing hypotheses, claim-by-claim accepted Product Capability
annotations, and claim-by-claim Model Context/Domain Strategy annotations.
None independently proved the *completeness* or acceptance of the target
output obligations. Direct dependency proposals varied with how the
unaccepted target obligations were formulated.

`evals.project_target_semantic_audit` now joins those **separate, source-bound
unaccepted** evidence streams into one report on the **eight operator-drafted
output obligations** (four per target):

- `prep.preparation-information-model`: PI-SEMANTIC-CONCEPTS,
  PI-KNOWLEDGE-AND-RELATIONS, PI-BOUNDARY-TO-HISTORY,
  PI-NEGATIVE-INVARIANTS.
- `prep.recorded-activity-history-model`: RH-RECORDED-FACTS,
  RH-REFERENCED-INFORMATION, RH-PRESERVED-CONTEXT,
  RH-NEGATIVE-INVARIANTS.

Source evidence is explicitly partitioned into **21 product units** (15 accepted
requirements and six non-goals) and **102 selected MC/DS source units**.
Thus the combined, scoped inventory contains **123 distinct source units**.
These are accepted *source statements*, not 123 individually accepted tactical
requirements. Other unselected sources and future revisions are outside the
verified scope.

## What the report answers

For each of the eight *draft* obligations, the audit reports:

1. The exact draft text and every candidate **claim-level** source link,
   including immutable source ID, accepted provider, file SHA-256 and text.
2. Whether a possible supporting/limiting claim came from Product Capabilities
   or from Model Context Strategy / Domain Strategy.
3. Explicit `OPEN_SCOPE_QUESTION` or `POSSIBLE_SHARED_BOUNDARY` links.
4. Source claims proposed to constrain **both** target models: a review
   signal for shared consumption versus duplicated semantic ownership,
   **never proof of duplication**.
5. Missing *hypothesis links*, distinct from genuinely missing accepted
   output semantics. Missing product mapping is not automatically a
   requirement gap; an MC/DS claim may be the relevant constraint.
6. Every original unresolved question from the Tactical Domain draft.

It preserves source statements with **no proposed target link** rather than
silently discarding consumer rules, no-goals, source traceability, exclusions
and strategy reopening conditions.

## Main ownership questions for Authority review

**Preparation Information ↔ Recorded Activity History.** The accepted TR-01
contract governs the distinction between current information meanings and
historical facts. PI-BOUNDARY-TO-HISTORY, RH-REFERENCED-INFORMATION and
RH-PRESERVED-CONTEXT may all consume parts of this one shared boundary.
The reviewer must separate *two legitimate obligations honoring one shared
contract* from duplicated ownership of a single authoritative semantic rule.

**Negative invariants.** Both target models may be prohibited from inferring
learner state or mastery from their own information. This is compatible with
separate positive obligations for meaning and recorded facts. A negative
constraint used in both contexts is not, by itself, redundant or evidence
that there should be one new shared Capability.

**Application behavior.** Information lifecycle changes, selection,
external transfer, recording operations and exploration remain possible
Application Design behaviors. When an action is constrained by domain
meaning, the action should not be silently promoted into an independent
Tactical Domain output. `REQ-CAP-EXPLORE-PERSPECTIVES` and
`REQ-CAP-EXPLORE-HISTORY` remain intentionally open: previously observed
real agent runs did not establish a stable, independently accepted
classification of their semantic impacts.

**Strategic lineage and source echo.** DS-01 / DS-02 trace to accepted
Product Capabilities, but ancestry or source text copied into a target
obligation cannot establish a direct `prep.domain-strategy` prerequisite.
Accepted Model Context Strategy already refines strategic responsibilities,
and the directness of any extra DS edge remains unproven.

## Assurance boundary

The module independently cross-checks that all source rows in the product and
MC/DS report belong to the same pinned, deduplicated source worksheet; that
source path, file hash, exact statement, provider and revision match; that
every accepted product and strategic source unit is accounted for exactly
once in its appropriate stream; that proposed target links refer to the
eight actual *draft* obligations; and that no input falsely claims
independent review, output acceptance or graph write permission.

It is fail-closed on source mismatch, omitted, extra or duplicated claims,
stale project SHA, invented target obligations, forged semantic acceptance
and graph-write promotion. A negative test may be rejected by an earlier
guard than the one it targeted; the test suite controls the input case
carefully so each invariant is exercised meaningfully.

**No semantic adjudication is performed.** Even a perfectly complete
mechanical report retains:

- `status=REVIEW_REQUIRED_NO_SEMANTIC_ORACLE`;
- `unreviewed_source_units=123` for this bounded pilot;
- `independent_authority_review_performed=false`;
- `complete_target_output_semantics_established=false`;
- `duplicate_authoritative_ownership_established=false`;
- `automatic_writeback_allowed=false`.

The optional `experiment/cdr-live-run` workflow stages the JSON evidence
`dependency-resolution-target-semantic-audit.json` **before** the blind
Copilot step. Merely staging the step is not an actual PREP execution;
independence and semantic correctness need an Authority decision, not a
model rerun or a source-link checksum.

## Next decision gate

The owner of Tactical Domain Design must independently decide, claim by
claim, which target output obligations are actually needed, which are only
constraints on existing obligations, which are shared cross-context
contracts, and which are solely Application Design or governance.

Once that semantic contract is independently accepted *in PREP's regular
governance*, the directness criterion from the previous experiment may be
applied to actual accepted obligations. Do not use the draft report to
automatically add, remove or rewire any capability dependency.

No canonical PREP or Harness main modifications occurred in this stage.
