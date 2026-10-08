# PREP real-project CDR — cross-authority coverage pilot, first live run

Date: 2026-10-08
Workflow: [GitHub Actions run 37804487025](https://github.com/lehater/harness/actions/runs/37804487025)
Job: dependency-resolution, PASS
Evidence artifact: dependency-resolution-live-evidence, id 11561784445
Execution SHA: `experiment/cdr-live-run@e9ab9e8e933bf842cf69756f9efc347265527118`
Pinned input snapshot: `lehater/prep@c52ff8ec1a4732285b2b299bf11dca9869fb2fee`
Harness PR: #220 (Draft)
Result: **read-only discovery and coverage assessment succeeded; semantic applicability NOT independently adjudicated; topology writeback disabled**.

## Evaluation identity

- Oracle-free source-traceability-v1, with source-grounded-v1 claim references.
- Provider GitHub Copilot CLI 1.0.86, requested model `auto`, reported resolved model `gpt-6-luna`.
- One provider invocation, no schema retry; isolated client environment reported; `independence=UNVERIFIED`.
- Scenario Suite `PASS`; evaluator `DISCOVERY_REQUIRES_REVIEW`; `calibration_claim=NOT_APPLICABLE_NO_ORACLE`.
- Every accepted Product Capability statement in the bounded source document received a model classification: 15 per target, 30 total. No malformed or missing coverage assessments.
- `semantic_applicability_adjudicated=false` and `complete_output_obligation_coverage_established=false`.
- Each target's source scope is grounded in accepted Model Context headings and accepted Domain Strategy headings selected by pilot configuration, not a globally comprehensive generated target contract.

## Results and graph comparison

| Target | Model direct suppliers | Existing direct suppliers | KEEP | ADD / review only | REMOVE_CANDIDATE |
| --- | --- | --- | --- | --- | --- |
| `prep.preparation-information-model` | `prep.model-context-strategy`, `prep.product-capabilities`, `prep.domain-strategy` | `prep.model-context-strategy`, `prep.product-capabilities` | both existing | `prep.domain-strategy` | none |
| `prep.recorded-activity-history-model` | `prep.model-context-strategy`, `prep.product-capabilities`, `prep.domain-strategy` | `prep.model-context-strategy`, `prep.product-capabilities` | both existing | `prep.domain-strategy` | none |

The model's additions are `REVIEW_REQUIRED` only; the deterministic proof check confirms cited source-claim references exist, **not** that the target must depend directly on each source. `automatic_writeback_allowed=false`, and Phase B prevents removal conclusions because target-obligation coverage remains `PARTIAL_BY_CONSTRUCTION`.

### Product applicability judgements

| Case | Accepted product candidates | DIRECT_CONSTRAINT | CONTEXT_ONLY | UNDECIDED | Explicitly traced in Domain Strategy |
| --- | ---: | ---: | ---: | ---: | ---: |
| SNAP-01 Preparation Information | 15 | 4 | 11 | 0 | 4 |
| SNAP-02 Recorded Activity History | 15 | 4 | 11 | 0 | 5 |

For SNAP-01 the four declared direct product constraints were:

- `REQ-CAP-KNOWLEDGE-KINDS`
- `REQ-CAP-RELATIONSHIP-MEANINGS`
- `REQ-CAP-CROSS-INFORMATION-RELATIONSHIPS`
- `REQ-CAP-EXPLORE-PERSPECTIVES`

All four are explicitly traced by DS-01 to accepted Product Capabilities.

For SNAP-02 the four declared direct constraints were:

- `REQ-CAP-RECORD-ACTIVITY`
- `REQ-CAP-RELATE-ACTIVITY`
- `REQ-CAP-PRESERVE-TIME`
- `REQ-CAP-PRESERVE-HISTORY-CONTEXT`

The fifth explicitly traced DS-02 requirement, `REQ-CAP-EXPLORE-HISTORY`, was classified `CONTEXT_ONLY` because inspecting history is an externally visible exploration behavior rather than an independently needed domain-model invariant in the selected target scope. This judgement is intelligible but **not independently expert-certified**. Its exclusion from direct evidence must be reviewed in light of how exploration shapes domain query semantics without prematurely assigning application behavior to the domain.

The model marked all remaining Product Capability requirements `CONTEXT_ONLY`; `UNDECIDED=0` is model confidence behavior, not proof that an independent ambiguity review is unnecessary.

### Strongest observed result

The previously concerning edges to `prep.product-capabilities` were **both retained** by the model once its actual Domain Strategy sources and accepted Product Capability claims were explicitly included in the target discovery context. The two existing target edges to `prep.model-context-strategy` were also retained. Thus the prior pilot's unsupported removal suggestions were eliminated through broader input-context coverage, not by suppressing the model's proposed supplier list.

### Principal confound: prompt-induced Domain Strategy direct edge

Both newly suggested direct dependencies on `prep.domain-strategy` are **not yet established as necessary direct edges**.

The generator added `DS-01` / `DS-02` accepted strategic sections as explicit **target output obligations** and separately listed `prep.domain-strategy` as the supplier of these very same statements. The model's direct consumption evidence consequently cites those same strategic sections. This demonstrates it can link a displayed obligation to its source, but is partially **tautological** and does not independently distinguish a truly necessary immediate upstream prerequisite from:

- relevant strategic background already constrained by the accepted Model Context Strategy;
- legitimate *transitive* knowledge acquired through `prep.model-context-strategy`;
- a directly consumed independent strategic invariant not subsumed by the model-context contract.

The accepted PREP Engineering Graph already has a direct edge `prep.model-context-strategy -> prep.domain-strategy`. Therefore, adding a second direct Tactical Domain edge cannot be justified solely by reachability or repeated subject matter. A source-to-target citation is necessary evidence but **not proof of directness**.

### Next experimental design

1. Create an independent directness test that *does not force each upstream source into its own target obligation*. Construct neutral target-output invariants and present upstream source statements as candidate knowledge only, with clear provenance.
2. Challenge necessity with omission/contrast: for each candidate direct provider, ask which target constraint would be materially unspecified if that provider's meaning were available only through already accepted immediate providers. Do not decide by graph transitive closure alone.
3. Separate accepted requirements intentionally excluded from the scoped model from product constraints still needing review. Require an owner-reviewed disposition before claiming global completeness.
4. In a later version, preserve a per-need source chain and derivation type (direct independent constraint vs inherited contextual support) without creating graph writeback.
5. Add fresh real-project controls; repeatability on this one PREP snapshot is not generic accuracy.

**Disposition:** Both `prep.product-capabilities` direct dependencies remain in the canonical PREP graph; the two `prep.domain-strategy` ADD suggestions remain research hypotheses only. No edits to PREP or `harness/main`.
