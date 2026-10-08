# PREP Tactical Domain — eight-obligation semantic review and v2 proposal

Date: 2026-10-08
Status: **operator-authored proposal for independent Tactical Domain Authority review, NOT accepted**
Research: [Harness PR #220](https://github.com/lehater/harness/pull/220) (Draft)
Pinned accepted PREP sources: `lehater/prep@c52ff8ec1a4732285b2b299bf11dca9869fb2fee`
Drafts: [v1](../../spec/dependency-resolution/project-pilots/prep-target-output-candidates-v1.yaml) → [v2](../../spec/dependency-resolution/project-pilots/prep-target-obligation-revision-v2.yaml)

## Substantive finding

The old eight draft statements mixed two different contract roles:

- **Six outputs** describe something the target Capability must define:
  current information meanings, relationship meanings, its side of the
  history boundary; historical facts, relationships to information, and
  preserved historical context.
- **Two governing constraints** prohibit erroneous inferences from those
  outputs: the existence of knowledge or a defined capability does not
  prove learner possession, while recorded activity does not prove
  learner mastery/readiness. Such constraints remain mandatory and
  independently visible, but are **not independently produced objects,
  third semantic owners or graph providers**.

The recommended revision retains **all eight stable IDs**: six are
`REFINE_OUTPUT`, two are `RECAST_AS_GOVERNING_CONSTRAINT`.
None is omitted, merged away or independently accepted. Output count
changes without throwing away its constraints.

## Individual decision proposals

| v1 obligation | Proposal | Substantive rationale | Still unresolved |
| --- | --- | --- | --- |
| `PI-SEMANTIC-CONCEPTS` | REFINE_OUTPUT | Own open-ended goal/capability/knowledge/material semantics and their distinctions | No mandated fixed taxonomy or one-context-per-kind split |
| `PI-KNOWLEDGE-AND-RELATIONS` | REFINE_OUTPUT | Retain kinds of knowledge, typed relationship meanings and semantic basis for perspectives | Does exploration impose new domain rule or merely consume the model? |
| `PI-BOUNDARY-TO-HISTORY` | REFINE_OUTPUT | Explicit current-information side of TR-01 without taking ownership of recorded facts | How much belongs to shared relationship contract? |
| `PI-NEGATIVE-INVARIANTS` | RECAST_AS_GOVERNING_CONSTRAINT | Constrain all PI outputs; knowledge/capability definitions cannot assert learner mastery/possession | Which safeguards are testable as semantic invariants? |
| `RH-RECORDED-FACTS` | REFINE_OUTPUT | History of activity, optional result, time and context; no mandatory storage design | Minimum facts when no result exists |
| `RH-REFERENCED-INFORMATION` | REFINE_OUTPUT | Meaning of links to information concerned; history does not redefine current information | Shared TR-01 ownership and local historical reference meaning |
| `RH-PRESERVED-CONTEXT` | REFINE_OUTPUT | Continued intelligibility as current information changes/removes, distinct from simply having a reference | Which semantic invariants vs lifecycle mechanisms? |
| `RH-NEGATIVE-INVARIANTS` | RECAST_AS_GOVERNING_CONSTRAINT | Constrain all RH outputs; historical facts are not assertions of learner state/readiness | Avoid implicit learner-state interpretation by consumers |

### Why not split or merge other concepts?

- Distinguishing `PI-SEMANTIC-CONCEPTS` from relationships preserves
  meaningful facets of the **same accepted MC-01**, not new model contexts.
  A decomposition into new capabilities is unsupported at this level.
- The two TR-01 sides must **not** be collapsed into one owner. History
  may refer to current information, but the historical fact and current
  information keep distinct meanings. Shared consumption does not
  prove duplicated authoritative ownership.
- `RH-REFERENCED-INFORMATION` and `RH-PRESERVED-CONTEXT` are
  related but semantically distinct: what a record refers to versus
  what must remain intelligible when its referent changes later.
  There is no accepted evidence that either facet is disposable.
- Product-level lifecycle, selection, transfer, recording operation and
  exploration stay possible Application Design consumers, not
  automatically new Tactical Domain outputs. Do not erase their
  potential constraints on domain meaning.
- Retaining the perspective semantics in PI relations does **not**
  resolve the earlier inconsistency of Copilot classifications for
  `REQ-CAP-EXPLORE-PERSPECTIVES`.

## Source evidence, not source echo

The accepted MC-01 and MC-02 define own semantic languages;
TR-01 explicitly requires cross-context distinction, reference meaning
and preserved historic intelligibility. DS-01 emphasizes exploration
from different perspectives. DS-02 and the Product Capability non-goals
forbid inferred learner mastery. These source contracts **inform** the
proposed target-owned formulation but cannot be copied into a target
obligation and then cited back as independent proof of an immediate
`requires` edge.

The v2 candidate has no direct provider assignments, no graph mutation,
no separate accepted target Core artifact and no independent reviewed
output contract. The earlier 123-unit audit remains the source review
queue; mechanical association does not settle semantic sufficiency.

## Gate implementation

`evals.project_target_obligation_revision.validate_revision` checks
the proposal against the original v1 without touching PREP or running
the evaluator. It requires:

1. The same exact source commit and the same target owning Authority.
2. Identical target set, with **every original obligation accounted for
   exactly once** through a stable ID and `supersedes_v1` lineage.
3. Explicit `REFINE_OUTPUT` vs `RECAST_AS_GOVERNING_CONSTRAINT`
   and every resulting constraint's applicability to existing local
   outputs.
4. The original cited source sections retained in each revised item.
5. Substantive changed text, review rationale and an unresolved question.
6. No asserted independent review, completeness, acceptance or
   writeback, and no embedded `requires`/`depends_on` graph edits.

This is structural **conservation**, not semantic correctness certification.
It may not detect an omitted meaning inside a paraphrase; the relevant
Authority must evaluate the original accepted evidence as well as v2.

## Next governance action

An independent reviewer for `TACTICAL-DOMAIN-DESIGN` should decide,
against the pinned PREP accepted sources:

- whether the six positive outputs are adequate and nonoverlapping;
- whether both negative constraints govern each output appropriately;
- how to express the two sides of TR-01 without competing owners;
- whether perspective/history exploration adds domain invariants;
- what semantics of changed/deleted referenced information must persist.

Only after accepting an actual independently specified and reviewed
target contract in PREP can the directness review examine which
suppliers are semantically indispensable. **No approval is implied by this
document or its passing CI checks.**

No PREP or Harness main modifications, graph rewrites or production
CDR routing have occurred.
