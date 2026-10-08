# Capability Dependency Resolution — oracle review and holdout design v1

Date: 2026-10-08
Status: **candidate source-based review, NOT independent expert validation**
Repository: `lehater/harness`, branch `experiment/capability-dependency-resolution-v1`
PREP source: `lehater/prep` branch `mvp-vertical-slice`, observed commit
`c52ff8ec1a4732285b2b299bf11dca9869fb2fee`.

## CDR-06: material direct inputs and multiple semantic sources

The initial draft oracle for `prep.recorded-activity-history-model` assigns
`preserve-temporal-context` and `preserve-historical-meaning` only to
`prep.product-capabilities`; `distinguish-history` is assigned to
`prep.model-context-strategy`.

The actual accepted project source contract is broader:

- `docs/architecture/model-context-map.md`, MC-02, lines 29–41: Recorded
  Activity History owns temporal context and the retention of intelligible
  historical facts after related information changes or removal.
- The same document, TR-01, lines 45–55: historical-context preservation,
  current-vs-history distinction, cross-context relationship meanings.
- `.harness/knowledge/product-capabilities.yaml`, lines 95–108:
  `REQ-CAP-PRESERVE-TIME` and `REQ-CAP-PRESERVE-HISTORY-CONTEXT`
  impose product behavior obligations on the same two subjects.

**Assessment:** The Copilot-added direct-need pairs from `model-context-strategy`
in runs 37754939856 attempts 1/2 have positive documentary support. This is
not proof that each pair is independently necessary for the tactical output:
that judgement must distinguish (a) domain semantic ownership and (b) product
acceptance constraints, rather than counting a second source as necessary
merely because it mentions the subject.

**Decision:** Keep draft oracle unchanged, mark CDR-06 **REVIEW_REQUIRED** at the
semantic-grounding level, and do not mark the source-derived assessment as
independent expert certification. Do not suppress extra need mappings merely
to obtain a perfect scorer status. A future reviewed oracle may recognize
multiple accepted direct needs per obligation, as already supported in the
`input_needs[]` schema.

Reviewer checklist:
1. Does Tactical Domain Design independently consume domain history meaning
   *and* product preservation requirements, for each specific obligation?
2. Should `preserve-temporal-context` split into time-of-occurrence vs
   reference-to-Preparation-Information obligations, and should retention
   similarly be decomposed?
3. Are both direct provider edges necessary despite one source summarizing
   the other?
4. Does the PREP project contract define any third direct provider absent
   from the bounded catalog?

Until checked, 11/11 agreement against a **draft** set of provider edges is
evidence of small-corpus repeatability, not correctness.

## Holdout suite HLD-01..07

Location:
- Label-free input: `spec/dependency-resolution/holdout-inputs-v1.yaml`
- Separate candidate oracle: `spec/dependency-resolution/holdout-oracle-v1.yaml`
- Regression harness: `tests/test_dependency_resolution_holdout.py`

The holdout assesses, respectively:

| Case | Challenge | Distinct risk |
|---|---|---|
| HLD-01 | Missing consent provider, **no explicit uncertainty hint** | Scorer overfit to CDR-04 hint |
| HLD-02 | Contract-only tax provider + accepted invoice vocabulary | Confusing contract planning with accepted semantics |
| HLD-03 | Target and required provider in same Authority | Omitting local explicit dependency |
| HLD-04 | Two providers in one canonical file; one needed | Artifact co-location causes false edge |
| HLD-05 | Similar provider name, unrelated semantic content | Lexical retrieval instead of direct consumption |
| HLD-06 | One obligation consumes two distinct providers | Single-source-per-obligation assumption |
| HLD-07 | Explicitly self-contained output | Always inventing an external prerequisite |

**Oracle governance:** This provisional set is author-designed and must remain
`AUTHOR_DRAFT`. Its labels are separate from the agent request. The expected
results are not proof of semantic ground truth. Do not modify the holdout
oracle to match a model response without an explicit source-grounded reviewer
decision; preserve any disagreements as findings.

**Execution policy:** The normal Harness CI tests data/protocol invariants
using synthetic predictions only, not semantic quality. A real Copilot holdout
run requires explicit operator-triggered GitHub Actions
`workflow_dispatch`, not a pull-request or push trigger. No accepted
Engineering Graph, Core, Lifecycle, Publication or PREP file is changed.

## Acceptance criteria for further rollout

- Every proposed direct edge is grounded to an actual target obligation and
  accepted provider semantics or an explicitly designated provisional
  contract-only producer.
- No missing-provider hints are needed to detect at least HLD-01.
- Multi-source dependencies are represented as distinct direct-need pairs,
  without introducing duplicates or unrelated provider edges.
- Separate structural scoring (`requires` providers) and semantic direct-need
  scoring must be reported; neither is overclaimed as validation against an
  independently certified oracle.
- Any failure in an unseen case produces a concrete review finding rather
  than automated changes to the accepted Engineering Graph.
- The real model output and execution provenance are retained for audit.

Next action: run HLD-01..07 blinded once using the established manual Copilot
GitHub Actions job; assess observed predictions before choosing any tuning.
