# PREP CDR — source-unit responsibility routing v1

Date: 2026-10-08
Status: **read-only reviewer worksheet + explicit operator hypotheses; no accepted target ownership decisions**
Research PR: [Harness #220](https://github.com/lehater/harness/pull/220) (Draft)
Reference snapshot: `lehater/prep@c52ff8ec1a4732285b2b299bf11dca9869fb2fee`
No changes to canonical PREP or Harness main.

## Boundary: evidence ownership is not semantic ownership

A product requirement accepted under `PRODUCT-CAPABILITIES` may define observable
application behavior while constraining the semantics of one or both Tactical
Domain models. These are not mutually exclusive. A source file's Authority is
the Authority of its evidence, **not an automatic declaration that the
target-output meaning is owned by that same Authority**.

The previous target-scope inventory returned one record per accepted source
statement per target. Both PREP Tactical Domain drafts include the same
global boundary, consumer, cross-context and accepted product units. Treating
those duplicates as unrelated target requirements would silently assign
shared semantics to each model.

`evals.project_target_responsibility_routing.build_routing_worksheet`
combines the two immutable source-unit ledgers into **one deduplicated review
queue**, preserving source path, file hash, semantic revision, local claim ID,
exact text and all target references, without changing accepted upstream
claims or pretending to accept target-owned output obligations.

## Semantic review tracks

The future reviewer must consider five **candidate tracks**, not force a
single owner from a source heading:

- `PREPARATION_INFORMATION`: current information concepts, knowledge,
  relationship semantics and the boundary that current information does not
  prove what a person knows or can do.
- `RECORDED_ACTIVITY_HISTORY`: immutable historical meaning of recorded
  activity/results, temporal and historical context, while excluding
  learner-state conclusions.
- `SHARED_CROSS_CONTEXT`: governing relationships between current
  information and historical facts, including references through later
  changes, without transferring the authoritative meaning of either model.
- `APPLICATION_DESIGN`: orchestration of information lifecycle,
  exploration, selection, transfer and recording actions while preserving
  accepted domain meanings.
- `UNDETERMINED`: neither section location nor product phrasing settles
  the semantic boundary; independent review is needed.

An *effect* axis remains separate: `DOMAIN_SEMANTICS`,
`SHARED_BOUNDARY`, `APPLICATION_BEHAVIOR`,
`PROHIBITED_INFERENCE`, `REOPENING_OR_GOVERNANCE` or
`UNDETERMINED`. This matters because "do not infer mastery" is a negative
invariant, not merely an unowned product feature, and "reopen the context if
its semantics diverge" is a governance condition, not necessarily a model
entity.

## Candidate routing evidence

Only direct, **source-location-based candidate hints** are generated for
the four named accepted source sections MC-01, MC-02, DS-01, DS-02 and the
TR-01 cross-context contract. Generic consumer sections are flagged as
potential application and cross-context review material; global negative
rules and product non-goals remain `UNDETERMINED`.

Separate explicit operator-authored routing hypotheses live at
`spec/dependency-resolution/project-pilots/prep-product-routing-hypotheses-v1.yaml`.
They cover **all 15 accepted** product requirement IDs exactly once:

| Product requirement area | Preliminary candidate review tracks | Critical distinction |
| --- | --- | --- |
| Introduce/retain/change/remove information | Application Design; current information/history and sometimes shared boundary | Action lifecycle is not automatically domain semantic ownership |
| Distinguish knowledge and relationship meanings | Preparation Information; sometimes shared boundary | Only accepted meaning/invariants belong to tactical model |
| Explore from different perspectives | Application Design and Preparation Information | Prior real Copilot runs disagreed about whether perspective exploration is a direct semantic constraint |
| Select/transfer part of information externally | Application Design plus semantic preservation in current/history | External-use behavior does not create its own accepted model context |
| Record activity and retain time/results | Application Design for action; Recorded Activity History for facts | Executing a recording action differs from owning a historical fact |
| Relate activity/preserve history context | Recorded Activity History and shared boundary | Historical meaning survives changes in current information |
| Explore historical activity | Application Design and Recorded Activity History | Inspection may be product behavior using already retained historical semantics |

Every proposal is `CANDIDATE_NOT_ACCEPTED`; none is a target acceptance,
authoritative routing rule or `requires` edge.

## Fail-closed contract

- **Stable identity**: the same source unit cited by both models is
  represented once. Conflicting source text, revision, owner-of-source or
  hash with the same unit ID fails closed.
- **Full product inventory**: product draft proposals must account for
  every ACCEPTED product requirement once, with no unknown or duplicate
  IDs; no invented acceptance status or release of writeback.
- **Independent effects**: a reviewer may classify a source unit's
  routing and its semantic effect separately; section-role hints never
  count as semantic proof.
- **No self-approval**: all units remain
  `review_state=UNREVIEWED`,
  `semantic_route=UNDETERMINED`,
  `semantic_effect=UNDETERMINED`,
  `target_output_obligation_mapping_verified=false`.
- **No forced commitment**: a structurally complete *review draft* with
  a grounded rationale for every source unit is still
  `DRAFT_COMPLETE_FOR_REVIEW`, NOT accepted or ready to amend PREP.
  Duplicated, unknown or source-drifted assessment rows fail closed.
- **No graph topology action**: `automatic_writeback_allowed=false`
  throughout; neither positive hints nor negative exclusions justify
  adding/removing direct dependencies.

The output is `PENDING_INDEPENDENT_RESPONSIBILITY_REVIEW`. It records
which source units are used by one or both targets and preserves every
non-goal and reopening condition as an unresolved unit.

## Necessary next acceptance step

The owning Tactical Domain Authority must review the deduplicated source
unit queue across **both** target models in the same pass. It must decide
semantic ownership, effect, application consumers and explicit shared
boundaries at individual-claim level. It must also determine whether the
four broadly drafted obligations per target capture all independently
necessary semantics or should be revised.

This is separate from review of direct prerequisites: even a checked
semantic responsibility mapping does not by itself show that a source
is an **immediately required** provider rather than inherited through a
retained public contract. Neither independent acceptance of target
obligations nor directness is yet demonstrated.

The worksheet generator can run deterministically on the pinned PREP
inventory; no new Copilot run is needed to test its implementation.
