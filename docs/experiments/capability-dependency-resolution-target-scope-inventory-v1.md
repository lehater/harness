# PREP Tactical Domain target-scope source inventory v1

Date: 2026-10-08
Harness branch: `experiment/capability-dependency-resolution-v1` (PR #220, Draft)
Pinned PREP: `lehater/prep@c52ff8ec1a4732285b2b299bf11dca9869fb2fee`
Status: **read-only accepted-source inventory implemented; semantic coverage and target acceptance not established**

## Why

The source-bound and neutral-contrast Copilot studies show that descriptions
of a target's output obligations have a large effect on which direct providers
the model proposes. The PREP Tactical Domain target artifacts do not yet exist
as individually accepted Core-provided and semantically reviewed outputs.
The previous eight broad target-owned draft obligations are therefore still
operator hypotheses, not an authoritative completeness oracle.

Before independent review, the target candidate draft must visibly account
for the accepted inputs that might constrain it, including **negative rules
and responsibility boundaries**, without presuming that every product
behavior belongs in a domain model.

## Exact source selection

The experimental candidate file
`spec/dependency-resolution/project-pilots/prep-target-output-candidates-v1.yaml`
now contains fourteen explicit source selectors per target:

- Own accepted model context (`MC-01` or `MC-02`).
- Shared cross-context relationship contract (`TR-01`).
- Model Context `Boundary invariants`.
- Model Context `Behaviors without independent model contexts`.
- Model Context `Contexts not independently justified`.
- Model Context `Consumers` and `Reopening conditions`.
- Relevant accepted Domain Strategy responsibility (`DS-01` or `DS-02`).
- Domain Strategy `Strategic relationship constraints`.
- Domain Strategy `Product behaviors without independent strategic ownership`.
- Domain Strategy `Explicitly not established`.
- Domain Strategy `Consumers` and `Reopening conditions`.
- **All** accepted Product Capability requirement statements (currently 15), plus the accepted product artifact's six explicit non-goals.

These selectors intentionally go beyond the sections previously used as
prompt target obligations. They are not asserted to cover all upstream
Authorities, all facts in a document, future revisions or all eventual
Tactical Domain output semantics. Accepting a source selector does not
mean it is a direct graph prerequisite.

## Source-unit accounting, not semantic certification

`evals.project_target_scope_coverage` checks the exact clean Git snapshot,
Core registration and semantic-review revisions of each source. It extracts
bounded Markdown paragraphs/bullets and individually accepted YAML product
statements and explicit product non-goals into source units with:
- stable text-derived ID, source path, SHA-256, heading, source-local ID,
  providing Capability and its baseline review revision;
- the section's intended role (model context, cross-context, strategic,
  negative/boundary, application separation, product constraints);
- any **same-section cross-reference** from a draft obligation (not evidence
  that this individual statement's meaning is fulfilled).

**Every unit remains `UNREVIEWED`.** The report exposes the number of units
with no draft candidate even sharing their source section. In particular,
cross-cutting boundary policies, application-level exclusions and accepted
product statements are not silently classified as irrelevant or covered.

The report is `PENDING_INDEPENDENT_TARGET_SCOPE_REVIEW` with
`complete_target_output_semantics_proven=false`,
`independent_authority_review_performed=false`, and
`automatic_writeback_allowed=false`. It does **not** authorize target
contract acceptance or ADD/REMOVE of `requires`.

### Authority review questions

For each selected source unit, the future review must separately decide:

1. Does it constrain the target output's *domain semantics*, a shared
   relationship boundary, an application behavior, or a prohibited inference?
2. Which target-owned accepted obligation, if any, captures that meaning?
   A broad same-section citation is insufficient.
3. If outside this target's ownership, which Authority is responsible and
   what accepted boundary justifies excluding it?
4. Is the unit's required meaning already supplied by an accepted immediate
   provider, or independently required from another provider? Do not decide
   merely from graph reachability.
5. Is the obligation still missing, ambiguous, duplicated between the two
   Tactical Domain targets, or subject to an explicit unresolved design
   question?

The external reviewer must assess both models together, especially TR-01
and historical reference semantics, so that shared boundary rules are
preserved without accidentally assigning the same authoritative domain
truth to two independent models.

No reviewer decisions are synthesized by this script, by a Copilot call or
by section-level text matching. The output is a reproducible **review
backlog**, not an accepted scope-completeness certificate.

## Test and operation

Full-gate test `tests/test_dependency_resolution_target_scope_coverage.py`
uses an immutable synthetic Git snapshot with accepted/unaccepted Product
Capability requirements, positive model semantics, cross-context rules,
negative constraints, product non-goals and application behaviors. It asserts all accepted
requirements and non-goals appear, no draft requirement does, no source unit is
independently marked reviewed, and unexpected sources/scope omissions,
forged acceptance, duplicated selectors, stale SHA or dirty sources fail.

[Harness core PASS](https://github.com/lehater/harness/actions/runs/37811017084)
and [CI policy PASS](https://github.com/lehater/harness/actions/runs/37811007972)
after the initial implementation.

The disposable `experiment/cdr-live-run` branch stages the generator
before the existing manual Copilot scenario. The JSON inventory will be
preserved in the Actions evidence artifact whenever a new manual run occurs,
but **no such real PREP inventory run is claimed here**. A new Copilot call
is not necessary to evaluate this mechanical source-inventory design.

All modifications remain in the Harness experimental branches. PREP and
`harness/main` are unchanged.
