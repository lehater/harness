# Semantic calibration corpus audit v0

Status: completed; corpus v3 created from full ambiguity audit of v2.

## Purpose

Audit every calibration case under the explicit closed-world judgement rules in
live calibration protocol v2 before attributing future evaluator disagreement
to model quality.

A useful calibration case must make the expert verdict follow from the supplied
source, target, relation and protocol without requiring charitable completion or
unstated execution assumptions.

## Audit result

### Already discriminating

The following v2 cases were already sufficiently explicit:

- `semantic-weakening` — explicit denial is replaced by warning plus allowed execution;
- `semantic-inversion` — preservation is explicitly inverted to clearing;
- `semantic-subject-swap` — governed object changes from RESOURCE-A to RESOURCE-B;
- `valid-paraphrase` — denial semantics are directly re-expressed;
- `semantic-partial-loss` — one required validation-failure effect is explicitly omitted;
- `valid-subject-preservation` — owner/resource identity and non-owner rejection are explicit;
- `semantic-outcome-substitution` — audit recording does not provide visible changed state;
- `semantic-enforcement-gap` — UI availability does not establish edit-execution denial.

### Hardened in v3

Three positive controls had correct intended labels but left avoidable room for
interpretation.

#### valid-decomposition

v2 target omitted the source trigger from the decomposed statements:

`On validation failure ...` -> `Preserve ... / Explain ...`

v3 repeats the trigger on both decomposed effects so acceptance does not depend
on assuming the original condition still scopes the target list.

#### valid-aggregation

v2 used `Authorized edits expose the changed state` for a source requirement
about `Successful resource edits`.

The intended combination is valid because unauthorized edits are denied, but
the wording mixed authorization and success conditions. v3 states both
conditions explicitly: unauthorized edits are denied and every successful
authorized edit exposes changed state.

#### valid-strengthening

v2 required rejection only for `direct edit attempts` while the source forbids
unauthorized edit execution generally. Under protocol v2, an evaluator could
correctly reject the case because indirect execution paths were unstated.

v3 keeps the UI strengthening but explicitly rejects every resource-edit
execution attempt by an unauthorized actor.

## Relation coverage gap

Corpus v2 exercised:

- REALIZES: positive and negative;
- TRANSFORMS: positive only;
- PRESERVES: negative only;
- CONSTRAINS: no cases.

v3 adds:

- `valid-preservation` — positive PRESERVES control paired with the existing
  subject-swap negative;
- `valid-constraint-strengthening` — positive CONSTRAINS control;
- `semantic-constraint-weakening` — negative CONSTRAINS control.

The resulting bootstrap corpus contains 14 cases: seven ACCEPTED and seven
REJECTED. Every declared relation now has at least one accepted path, and every
relation except TRANSFORMS has an explicit rejected path. TRANSFORMS retains two
positive controls; its defect classes are already exercised through semantically
equivalent REALIZES/PRESERVES failures rather than adding a case solely for
numerical symmetry.

## Versioning

- v1 remains immutable because real provider evidence is fingerprint-bound to it;
- v2 remains immutable as the first closed-world protocol-aligned correction;
- v3 is the current calibration corpus;
- protocol v2 remains current because the audit found corpus wording/coverage
  defects, not a new protocol defect.

## Interpretation rule

Future live disagreement should be triaged in this order:

1. determine whether the case admits two reasonable readings under protocol v2;
2. if yes, repair the corpus as a specification defect;
3. if no, record the disagreement as evaluator behavior;
4. only compare evaluator/model quality after the oracle is unambiguous.

No Core, scorer, orchestration or provider abstraction change is required.
