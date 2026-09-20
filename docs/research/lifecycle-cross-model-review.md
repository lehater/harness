# Lifecycle cross-model contradiction review

Scope: decision-lifecycle research and capability-lifecycle experiment against canonical Core v0, Engineering Graph v0 and Design Target State v0.

## Verdict

The lifecycle projection can remain an optional layer above the existing models. No Core v0 entity or canonical v0 evaluator semantics need to be changed.

One important correction is required in the experimental evaluator: UNKNOWN lifecycle coverage must not be presented as REVALIDATE. REVALIDATE asserts that an accepted assertion is known stale against a changed baseline and can be semantically reaccepted by its owner. UNKNOWN means Harness lacks the lifecycle evidence needed to decide currentness and must report lifecycle evaluation as unavailable/incomplete.

## Compatibility matrix

### Core v0

Core owns accepted knowledge state:
- Authority;
- CanonicalArtifact;
- Question;
- CapabilityId;
- artifact dependencies.

Lifecycle projection does not change those facts. It references current Core providers by artifact id and CapabilityId.

PASS.

### Engineering Graph v0

Engineering Graph owns capability production prerequisites. This is exactly the semantic dependency topology required for baseline comparison.

Lifecycle must not use Core artifact `depends_on` as its invalidation topology.

PASS.

### Design Target State v0

Target State v0 intentionally defines structural completeness:
- provider -> SATISFIED;
- Question-blocked -> WAIT;
- missing -> CREATE;
- unresolved prerequisites -> PENDING;
- all structurally satisfied -> COMPLETE.

Lifecycle-aware completeness is a stricter optional evaluation and must not silently redefine the meaning of canonical v0 COMPLETE.

Therefore both results may legitimately coexist:
- `structural_status: COMPLETE`;
- `lifecycle_status: INCOMPLETE/READY/COMPLETE`.

PASS with naming/reporting separation.

## Finding P0 — UNKNOWN is not REVALIDATE

Current experiment groups every non-CURRENT provider under REVALIDATE.

This is semantically wrong for UNKNOWN.

REVALIDATE requires evidence of:
- current accepted assertion exists;
- its accepted baseline is known;
- a prerequisite current revision/baseline mismatch makes it STALE.

UNKNOWN means one or more required lifecycle assertions are absent. The owner cannot be told to revalidate against a baseline Harness cannot identify.

Required behavior:
- STALE + prerequisites current -> REVALIDATE;
- UNKNOWN -> lifecycle coverage gap;
- downstream -> PENDING/UNKNOWN as appropriate;
- lifecycle-aware status cannot be COMPLETE.

This is an integration metadata gap, not automatically an engineering Question. A Question is only appropriate if obtaining the missing lifecycle assertion exposes actual semantic uncertainty.

## Finding P1 — structural COMPLETE must remain stable

Do not modify `target_state.py` v0 to make lifecycle metadata mandatory.

A legacy repository with no lifecycle projection must retain its current structural evaluation.

Lifecycle evaluator should report a separate status and may include the structural result for comparison.

## Finding P1 — revision identity is acceptance identity

The word `revision` can be misread as file/content revision.

Contract must explicitly define it as capability acceptance revision/assertion identity. Artifact Git SHA may be used only when the integration guarantees that each semantic reacceptance gets a distinct identity even with unchanged bytes; ordinary content SHA alone does not satisfy that requirement.

Prefer field name `acceptance_id` before canonicalization.

Then:
`accepted_prerequisites: CapabilityId -> prerequisite acceptance_id`.

This removes the most dangerous ambiguity from the contract.

## Finding P1 — exact baseline coverage

The experiment correctly requires baseline keys to equal production prerequisites exactly.

This is necessary because:
- missing prerequisite key cannot prove acceptance;
- extra key would create a hidden invalidation edge outside Engineering Graph.

Keep this invariant.

## Finding P1 — current selection is external/project-owned

The projection contains the currently selected assertion only. Harness must not select "latest" from historical assertions.

Historical storage, ordering and supersession records remain project-owned. Adapter/integration supplies the selected current assertion.

Keep this invariant.

## Finding P2 — root capabilities

Root production contracts have empty accepted baseline. They can be CURRENT when a current accepted assertion exists.

Changing a root means the integration selects a new acceptance_id. Direct consumers then become STALE by baseline mismatch.

No special root lifecycle entity is required.

## Finding P2 — Questions precedence

Question blocking remains semantically stronger than lifecycle actionability:
- unresolved blocking Question -> WAIT;
- do not also expose REVALIDATE for the same expectation.

The experiment already follows this precedence.

## Finding P2 — CREATE precedence

Missing Core provider remains CREATE/WAIT according to canonical v0 semantics. Missing lifecycle assertion for an existing provider is not CREATE.

Keep these concepts separate.

## Canonical shape recommendation

Rename:
- `revision` -> `acceptance_id`;
- baseline values are acceptance ids.

Derived lifecycle state:
- CURRENT;
- STALE;
- UNKNOWN.

Target actions remain:
- CREATE;
- WAIT;
- REVALIDATE;
- PENDING.

Add a separate collection/action:
- `lifecycle_gaps` (or equivalent) for UNKNOWN coverage.

Do not introduce a generic `FIX_METADATA` engineering action; lifecycle projection is integration evidence, not semantic engineering output.

## Promotion decision

After the P0 UNKNOWN correction and acceptance_id rename, the experimental layer is compatible with Core v0/Engineering Graph v0/Target State v0.

No demonstrated contradiction requires Core v1.

The candidate can then be promoted as an optional canonical integration/evaluation layer while retaining static v0 behavior.
