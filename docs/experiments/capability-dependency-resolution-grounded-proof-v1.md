# Capability Dependency Resolution — source-grounded proposal proof (experimental v1)

Date: 2026-10-08
Branch: `experiment/capability-dependency-resolution-v1`
Status: **deterministic preflight implemented and passing CI; real grounded-model evaluation pending**
Scope: no canonical Engineering Graph, Core, Lifecycle, Project Publication or PREP updates; skill route remains `unrouted`.

## Defect motivating this refinement

The repeated HLD-01 holdout run (GitHub Actions
[37756377957 attempt 2](https://github.com/lehater/harness/actions/runs/37756377957/attempts/2))
incorrectly proposed `holdout.product-sharing-intent` as a direct provider for
`enforce-release-consent`. The statement about choosing to share information
does not itself establish a normative consent rule. The model correctly marked
the obligation UNRESOLVED, but still added this unsupported edge.

A mechanical graph check cannot detect that semantic mismatch. Merely requiring
the model to produce a rationale also cannot prove a source actually entails
the obligation. This preflight narrows what may be treated as an actionable
dependency proposal.

## Source-grounded-v1 request

New blind corpora declare:

`evidence_contract: source-grounded-v1`

The operator-selected process driver passes this marker without sharing
`baseline_requires`, `expected_requires`, expert labels or the oracle.
The Copilot adapter requests, for each input-need:

```yaml
obligation: enforce-rule
provider: example.policy
claim_index: 0                # zero-based index into provider semantic_surface[]
basis: DIRECT_ACCEPTED        # or PLANNED_CONTRACT
consumption_rationale: >-
  This explicit accepted rule constrains the target's deny operation.
```

The index and basis must align with an available public provider claim.
A provider marked CONTRACT_ONLY is not allowed to masquerade as accepted
knowledge. This is an **experiment-only assertion schema**, not a new persistent
Core entity or a change to Engineering Graph `requires`.

## Deterministic preflight

`evals/dependency_resolution_evidence.py` verifies:
- cited provider and obligation exist within the blinded case;
- the cited claim index exists in the provider's public semantic_surface[];
- evidence basis matches ACCEPTED_EVIDENCE or CONTRACT_ONLY;
- every proposed edge is covered by at least one syntactically grounded need;
- cited needs have a nontrivial, nonempty consumption rationale;
- a DIRECT_ACCEPTED edge pointing at the same explicitly UNRESOLVED obligation
  causes REVIEW_REQUIRED rather than eligibility for adoption;
- CONTRACT_ONLY yields PROVISIONAL and REVIEW_REQUIRED, not accepted truth;
- invalid references and mismatched edges fail the evidence preflight.

**The preflight does not evaluate semantic entailment.** A model can still quote
a valid but irrelevant claim and invent a superficially plausible rationale.
Human or independently validated semantic review remains mandatory before
applying any edge. `automatic_writeback_allowed` is always false.

It also does not imply that every obligation has exactly one provider.
The separate `input_needs[]` entries may cite multiple independent sources.

The preflight is opt-in via `evidence_contract`; prior seed and holdout
corpora remain unchanged so that their historical scores stay reproducible.

## Regression coverage

- New cases: `spec/dependency-resolution/adversarial-inputs-v1.yaml` and
  separate `adversarial-oracle-v1.yaml` (six unseen cases ADV-01..06).
- `tests/test_dependency_resolution_grounding.py` checks source-reference
  boundaries, basis mismatch, nontrivial rationale, proposed edge congruence,
  planned-provider review and the known HLD-01 unsupported edge.
- Existing historical evaluator and transport tests still execute in the
  canonical full Harness gate.

The six adversarial cases cover:
1. optional sharing intent falsely treated as data-release authority;
2. warning vs enforcement of duplicate-payment prevention;
3. audit/logging vs authorization constraints;
4. a planned VAT contract vs already accepted tax rules;
5. two independent rule owners governing a single deletion obligation;
6. descriptive page-view metrics vs actual inventory state.

These labels are `AUTHOR_DRAFT`; they are not independently certified.
The evaluated agent has never been run on the six adversarial cases as of
this report. Do not adjust the oracle just to match future model predictions.

## Execution boundary

A disposable `experiment/cdr-live-run` branch contains the exact six new
inputs and corresponding hidden oracle plus a temporary manual Copilot
workflow. Existing Harness CI policy prohibits PR-triggered external LLM
execution. A real provider run must be launched via workflow_dispatch from
the GitHub Actions UI, selecting `experiment/cdr-live-run`.

Before enabling any production route, require:
- real repeated blinded adversarial runs, with complete raw prediction rows
  and independent review of false-positive cases;
- an expert-reviewed subset of ground truth that was not authored by the
  evaluated model;
- confidence policy for uncertain or conflicting sources;
- project revision consistency before automatic graph writes.

No dependency edge may be silently added, kept or deleted because of a
structurally valid reference alone.
