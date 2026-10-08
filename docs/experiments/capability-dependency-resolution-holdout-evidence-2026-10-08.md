# Capability Dependency Resolution — first blind holdout, repeated provider runs

Date: 2026-10-08
Repository: `lehater/harness`
Experiment PR: #220 (`experiment/capability-dependency-resolution-v1`)
Execution snapshot: `experiment/cdr-live-run@e6dffdac9ffef669b592a148ef3a890ff805e857`
Source input: `spec/dependency-resolution/holdout-inputs-v1.yaml`
Draft oracle: `spec/dependency-resolution/holdout-oracle-v1.yaml`
Status: **real provider execution confirmed; semantic reliability NOT established**

## Evidence identity

Workflow: [GitHub Actions run 37756377957](https://github.com/lehater/harness/actions/runs/37756377957);
manually dispatched and re-run without modifying the input corpus.

- [Attempt 1](https://github.com/lehater/harness/actions/runs/37756377957/attempts/1): job `dependency-resolution` PASS, evaluation `MATCHES_DRAFT_ORACLE`.
- [Attempt 2](https://github.com/lehater/harness/actions/runs/37756377957/attempts/2): job PASS, evaluation `DIFFERS_OR_INCOMPLETE`.
- Both attempts: GitHub Copilot CLI 1.0.86, requested model `auto`, provider-reported resolved model `gpt-6-luna`.
- Both: `calibration_claim=NOT_ESTABLISHED`, `independence=UNVERIFIED`.
- Evidence artifact: `dependency-resolution-live-evidence` on the respective run attempts.
- The agent received **7 label-blinded holdout cases** HLD-01..HLD-07. All oracle entries have `review_status=AUTHOR_DRAFT` and cannot be presented as independent expert truth.

## Scoring relative to provisional author-draft oracle

| Measure | Attempt 1 | Attempt 2 |
| --- | --- | --- |
| Full-case matches | 7/7 | 6/7 |
| Expected direct edges found | 8/8 | 8/8 |
| Extra direct edges | 0 | 1 |
| Missed direct edges | 0 | 0 |
| Edge precision | 1.0 | 8/9 ~= 0.889 |
| Edge recall | 1.0 | 1.0 |
| Semantic direct-need disagreements | none | HLD-01: 1 extra pair |
| Workflow transport/integrity | PASS | PASS |

HLD-02..HLD-07 matched the draft oracle in both attempts, including contract-only vs accepted evidence in HLD-02, same-Authority dependency in HLD-03, shared canonical file in HLD-04, lexical decoy in HLD-05, two providers for one obligation in HLD-06, and empty external prerequisite set in HLD-07.

## The revealing HLD-01 mismatch

Target: `holdout.partner-sharing-workflow`.
Two target obligations:

- `encode-partner-message`: use the accepted external partner field contract.
- `enforce-release-consent`: prevent transmission absent a valid data-sharing consent rule.

The catalog offers `holdout.partner-field-contract` (accepted field meanings),
`holdout.product-sharing-intent` (accepted *general permission for users to
choose to share selected records*), and `holdout.network-transport-plan`
(accepted transport/retry semantics). It contains **no explicit provider of a
consent enforcement rule**; unlike seed case CDR-04, the holdout includes no
`known_uncertainties` hint.

Attempt 1, appropriate under the proposed labels:

- `status=UNRESOLVED`;
- `proposed_requires=[holdout.partner-field-contract]`;
- need for `encode-partner-message` mapped to partner field contract;
- `unresolved_obligations=[enforce-release-consent]`.

Attempt 2:

- `status=UNRESOLVED`;
- `proposed_requires=[holdout.partner-field-contract, holdout.product-sharing-intent]`;
- **additional `input_needs` pair `enforce-release-consent -> holdout.product-sharing-intent`**;
- `unresolved_obligations` still includes `enforce-release-consent`.

That added pair is not justified by the catalog's stated semantic surface.
General user-directed sharing intent is not an accepted consent rule or
enforcement contract. At most it supplies relevant context; the actual consent
obligation remains without an accepted provider. This is a **semantic direct-edge
false positive** according to the explicitly scoped source contract.

The model therefore demonstrated the ability to report `UNRESOLVED` while
still making an unsupported provider-edge proposal. A successful transport
result, or even a correct unresolved status, does **not** guarantee that
`proposed_requires` is trustworthy.

## Architecture consequence

The fail-closed contract must distinguish:

1. A direct knowledge supplier whose accepted semantic surface is materially
   *consumed* by an output obligation.
2. A `CONTRACT_ONLY` planned provider that justifies **provisional** topology
   despite unresolved admitted semantics.
3. Contextually related or contributory knowledge that **does not** justify
   a direct edge.
4. Missing rule/owner whose obligation remains `UNRESOLVED`.

For every proposed edge, the agent should provide explicit source references
and the specific consumed, source-supported semantic rule. A generic matching
topic, enabling intent, or non-normative background statement is insufficient.
An output obligation may have multiple legitimate direct providers but should
not gain a dependency merely because multiple sources are related.

These distinctions require *semantic* evaluation and owner review. A
deterministic validator can require evidence fields and reject invalid
references, but cannot prove that a quoted statement entails the needed rule.

### Follow-up acceptance test

Before allowing `ADD` proposals to be promoted:

- Introduce a **new independently authored, unseen** test set for
  intent-vs-policy, disclosure-vs-consent, notification-vs-enforcement,
  descriptive history-vs-normative constraints, and mixed partially
  supported obligations.
- Retain HLD-01 as a fixed regression case, **not** a new holdout.
- Demand provenance-grounded need explanations and reject unsupported
  edge suggestions for adoption; do not automatically make up missing rules.
- Separate topology-level repeatability from direct-need justification
  repeatability; with two attempts HLD-01 direct edges are not stable.
- Keep automatic graph changes disabled. Human/Authority review remains
  mandatory for `ADD`, `REMOVE_CANDIDATE`, and ambiguous provider proposals.

## Epistemic and operational limits

This is a small, authored fixture set; its oracle is not independently reviewed.
Execution isolation is provider-adapter reported and tagged `UNVERIFIED`.
The observed model name is Copilot CLI provenance, not an immutable model build.
The holdout's provider catalog is deliberately bounded: success within that
catalog does not establish repository-wide source discovery, contract extraction,
or complete provider inventory.

Do not change the oracle just to match either Copilot attempt; do not
merge PR #220, enable the route, or modify the accepted PREP graph based on
these tests. Archive both raw result sets and their provenance.

## Disposition

**Technical proof:** PASS — GitHub Copilot executes blinded Dependency
Resolution through Harness Scenario Suite and produces request-bound evidence.

**Semantic candidate reliability:** PARTIAL — first run 7/7, repeated run
6/7 under the same stated task due to an unsupported direct prerequisite.

**Next engineering work:** evidence-grounding contract and semantic negative
regressions before a new blind evaluation; independent expert oracle review
remains required.
