# PREP CDR — accepted source claim to draft target-output obligation review v1

Date: 2026-10-08
Status: **experimental, noncanonical, read-only; no independent target or dependency decision**
PR: [Harness #220](https://github.com/lehater/harness/pull/220) (Draft)
Immutable PREP reference: `lehater/prep@c52ff8ec1a4732285b2b299bf11dca9869fb2fee`

## What is being separated

A Product Capabilities requirement is an **accepted product requirement**,
not necessarily an accepted Tactical Domain output obligation. An accepted
negative boundary can constrain two different models without requiring
duplicated semantic ownership. Application actions can consume domain
semantics without becoming invariants of the domain model.

The prior deduplicated source responsibility worksheet identifies a statement
once, even when both domain targets consume the source section. This
experiment now asks a more precise question: which **particular candidate
obligation**, if any, might be constrained by each accepted source statement?
The answer is an operator hypothesis and an Authority-review question, not
an algorithmic or model-certified mapping.

## Implementation

`evals.project_target_claim_mapping.build_claim_mapping` accepts:

1. The deduplicated, unreviewed responsibility worksheet for exact PREP commit.
2. The four draft target obligations per Tactical Domain Capability, explicitly
   `CANDIDATE_NOT_ACCEPTED`.
3. An optional, wholly separate operator-authored mapping proposal file
   `spec/dependency-resolution/project-pilots/prep-claim-obligation-hypotheses-v1.yaml`.

The proposal covers **all 15 individually accepted Product Capability
requirements and all 6 explicit product non-goals**, exactly once.

Each proposed link names the accepted source claim ID and a specific
**draft** target obligation ID, plus a noncanonical relationship such as
`CANDIDATE_SEMANTIC_CONSTRAINT`, `CANDIDATE_NEGATIVE_INVARIANT`,
`POSSIBLE_SHARED_BOUNDARY` or `OPEN_SCOPE_QUESTION`.
Possible Application Design or cross-context consumers are recorded on
a separate axis and do **not** create new domain-model responsibilities.

The generator rejects unknown or duplicate claims, source-digest mismatches
when supplied, stale project revisions, undefined target obligations,
duplicate links, unsupported relationship labels, incomplete product claim
coverage and attempted acceptance. It outputs a separate review row for
**every source unit**, including accepted model/strategic claims that were not
operator-classified in this iteration. Those rows remain
`UNCLASSIFIED_REQUIRES_REVIEW`, never silently discarded.

### Most important distinctions

| Accepted product source | Draft review direction | Not established |
| --- | --- | --- |
| Knowledge kinds and relationship meanings | Candidate constraint of Preparation Information semantics | A fixed taxonomy, storage schema or graph topology |
| Introduce, retain, select or transfer information | Candidate Application Design behavior; semantic implications remain open | That the entire behavior belongs to a Tactical Domain model |
| Change or remove current information | Application lifecycle plus a possible history/current-information boundary | Who owns every invariant or the exact direct `requires` |
| Recorded activity, temporal and reference preservation | Candidate Recorded Activity History constraints, with shared references reviewed separately | Runtime implementation or ownership of the current information |
| Explore from perspectives | Application behavior, possibly a direct Preparation Information semantic constraint | Whether model-semantic directness was established; real Copilot runs disagreed |
| Explore historical activity | Application behavior, possibly a Recorded Activity History constraint | An additional independently owned historical model invariant |
| No learner state/mastery conclusions | Candidate negative invariant for both models | That underlying capabilities or activity facts must not exist |
| No mandated taxonomy/topology/technology/statistics | Candidate exclusions or out-of-scope design controls | A fixed data representation or a new provider edge |

For the accepted Product Capability artifact, **21/21 draft operator
assessments** means only *one review hypothesis per source unit exists*,
not that its semantics are covered, true, accepted or directly consumed.
All existing upstream strategy source statements stay in the global backlog
until a claim-specific independent assessment is performed.

The output retains immutable source identity, original statement,
candidate links, external routes, per-target hints and review disposition.
It also identifies target draft obligation IDs with no product-claim link.
Such an omission is not automatically a missing domain obligation:
the model-context or strategic contracts might independently define it.

## Nonpromotion invariants

Every report declares:
- `PENDING_INDEPENDENT_CLAIM_TO_OBLIGATION_REVIEW`;
- `authority_review_performed=false`;
- `all_accepted_source_semantics_covered=false`;
- `target_obligations_independently_accepted=false`;
- `direct_provider_necessity_established=false` for every source unit;
- `automatic_writeback_allowed=false`.

A 21/21 filled mapping is **not** a semantic oracle, target-scope
acceptance, topology calibration or Permission to remove/add edges.

## Verification and next work

`tests/test_dependency_resolution_claim_mapping.py` is registered in
the full Harness gate. It checks complete positive and negative product
mapping, open claims outside the product artifact, cross-target references,
nonpromotion, missing/duplicate/unknown claim IDs, unexpected/duplicated
target obligation links, accepted status and snapshot mismatch.

[Harness core PASS](https://github.com/lehater/harness/actions/runs/37814356551)
and [CI policy PASS](https://github.com/lehater/harness/actions/runs/37814340284).

The disposable `experiment/cdr-live-run` branch also stages the purely
deterministic mapping step before Copilot, saving
`dependency-resolution-claim-mapping-review.json`. This staged step has
**not** been run against PREP in a new Actions execution yet.

**Next:** independent claim-by-claim semantic review of the accepted
model-context and strategic source units, with explicit TARGET / SHARED /
APPLICATION / EXCLUDED / UNDETERMINED dispositions. Only then consider
reworking or accepting target output obligations within PREP's actual
TACTICAL-DOMAIN-DESIGN governance. Directness evaluation follows acceptance.

Neither PREP nor `harness/main` is modified.
