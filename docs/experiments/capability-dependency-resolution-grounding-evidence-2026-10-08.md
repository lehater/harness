# Capability Dependency Resolution — source-grounded adversarial evaluation

Date: 2026-10-08
Repository: `lehater/harness`
Evaluation code branch: `experiment/cdr-live-run` at `9b9e22d738185904d1e6fcfa500dd68ed849b29f`.
Primary implementation: `experiment/capability-dependency-resolution-v1` (draft PR #220).
Provider: GitHub Copilot CLI v1.0.86, requested model `auto`, observed resolved model `gpt-6-luna`.
Evidence status: **two real blinded runs; provisional oracle, not independently expert-reviewed**.

## Runs

- [GitHub Actions run 37758146990, attempt 1](https://github.com/lehater/harness/actions/runs/37758146990/attempts/1) — workflow PASS; comparison `MATCHES_DRAFT_ORACLE`.
- [GitHub Actions run 37758146990, attempt 2](https://github.com/lehater/harness/actions/runs/37758146990/attempts/2) — workflow PASS; comparison `MATCHES_DRAFT_ORACLE`.
- Workflow job `dependency-resolution`; both completed with provider response and request-bound evaluation.
- Both: 6/6 full case matches, 7/7 expected direct edges, 0 extra and 0 missed edges, 0 direct-need disagreements. `edge_comparison.precision=1`, `edge_comparison.recall=1` **relative to this small AUTHOR_DRAFT oracle only**.
- Both: `calibration_claim=NOT_ESTABLISHED`, `independence=UNVERIFIED`.
- The workflow-produced `dependency-resolution-live-evidence` artifacts and job logs contain complete `model_results` and `bound_predictions` for later qualitative review.

## Grounding inspection

The model used the new opt-in `source-grounded-v1` protocol, returning for every direct need: provider, obligation, public-claim `claim_index`, `basis`, and a consumption rationale. In both runs the deterministic preflight accepted the claim references and declared acceptance status. None of these checks attests that the source *semantically entails* a rule; `semantic_entailment_verified=false` throughout.

| Case | Intended challenge | Both model attempts |
| --- | --- | --- |
| ADV-01 | User export intent is not private-data release authority | Correctly UNRESOLVED; only partner-field contract proposed |
| ADV-02 | Warning and telemetry are not duplicate-settlement prevention | Only accepted payment-settlement rule proposed |
| ADV-03 | Audit logging and access preferences are not authorization constraints | Correctly UNRESOLVED with zero direct providers |
| ADV-04 | Planned VAT supplier vs accepted currency vocabulary | Correct planned plus accepted source, tax obligation UNRESOLVED, proof REVIEW_REQUIRED |
| ADV-05 | Product role AND domain tenancy invariant | Both direct sources proposed for one obligation |
| ADV-06 | Analytics page requests vs domain stock state | Only stock formula source proposed |

For example, ADV-01 cited the external profile-field rule as accepted input to `encode-profile-format`, while preserving `enforce-data-release-authority` as unresolved. No general product sharing-intent edge appeared in either run. The previously observed holdout HLD-01 false-positive class was therefore avoided on this new related but non-identical example.

ADV-04 cited the planned jurisdiction/VAT contract as `PLANNED_CONTRACT`, not `DIRECT_ACCEPTED`, and the accepted ISO currency amount vocabulary separately. The validator returned `UNACCEPTED_PROVIDER_CONTRACT` and `REVIEW_REQUIRED`, with automatic writeback false.

All `referenced_claims[].claim_index` values on this dataset were 0 because each provider in this particular adversarial fixture has one public semantic surface claim; this run does **not** test selection among multiple conflicting or distractor statements inside one provider.

## Limits and decisions

- The six adversarial cases were authored after the HLD-01 failure and the model instruction explicitly warns against intent-as-consent errors. The observations support the effectiveness of the revised procedure **on these cases**, but cannot isolate the effect of the stronger model instructions versus structured proof protocol or scorer.
- Re-running the same cases does not make them new holdout cases.
- Labels remain `AUTHOR_DRAFT`, not independently reviewed by a separate semantic authority. Case scope is a bounded synthetic provider catalog rather than unrestricted project-wide source discovery.
- Model identity comes from Copilot CLI, not an immutable provider/model build.
- `adoption_eligible_requires` names references surviving deterministic preflight; it does not mean the edges are independently proven correct. `semantic_entailment_verified=false` and `automatic_writeback_allowed=false` are always maintained.
- The known CDR-06 semantic granularity question from PREP remains unresolved at the expert-oracle level.
- No accepted PREP or Harness project graph was changed, and CDR remains `unrouted`.

## Next decision

This validates a small **read-only proposal-and-evidence experiment** with stronger structural safeguards. Do not enable automatic `requires` mutation or production routing solely on the basis of these results.

Before promotion: independent semantic review of the oracle, multiple candidate claims per provider (including irrelevant/wrong normative statements), unbounded or incomplete discovery testing, real PREP snapshot read-only audit, and project-snapshot-consistent graph topology change policy.
