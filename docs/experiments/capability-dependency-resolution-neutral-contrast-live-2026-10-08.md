# PREP Capability Dependency Resolution — neutral target contrast evidence

Date: 2026-10-08
Status: **Real blind contrast run completed; directness still NOT independently proven**
Implementation PR: [#220](https://github.com/lehater/harness/pull/220) (Draft)
Execution: [GitHub Actions #37807128717](https://github.com/lehater/harness/actions/runs/37807128717), commit `experiment/cdr-live-run@b225470dca9e118e34429b25b91ceeffc9e68eb1`
Source snapshot: `lehater/prep@c52ff8ec1a4732285b2b299bf11dca9869fb2fee`
Workflow result: **PASS**
Evidence artifact: `dependency-resolution-live-evidence`, artifact id `11563835718`

## What changed in the controlled contrast

Prior real source-bound runs [#37804487025 attempt 1](https://github.com/lehater/harness/actions/runs/37804487025/attempts/1) and [attempt 2](https://github.com/lehater/harness/actions/runs/37804487025/attempts/2) included the accepted MC-01/MC-02/TR-01 and DS-01/DS-02 source sections as target output obligation text, while providing their owning sources as candidate suppliers. Those runs both proposed new direct edges to `prep.domain-strategy`.

This contrast used `--formulation NEUTRAL_CONTRAST`:
- same exact immutable PREP commit and two target Capability identifiers;
- same six accepted, baseline-reviewed candidate providers and their source semantic surfaces;
- same accepted Domain Strategy-to-Product-Requirement trace inventory and full 15 accepted Product Capability candidate statements per target;
- current accepted target `requires` still hidden from the evaluator until Phase B;
- changed **only** the target obligation descriptions, replacing source-bound MC/DS excerpts with short, operator-authored noncanonical paraphrases of tactical semantics. The paraphrases contain no source-provider backpointers and are marked `EXPERIMENTAL_OPERATOR_PARAPHRASE_NOT_ACCEPTED`.

This is a controlled prompt formulation contrast, not a claim that operator-authored descriptions constitute accepted target scope or an impartial oracle. Rephrasing may alter meaning as well as remove direct source-text echo.

## Outcome

Real GitHub Copilot CLI 1.0.86, model requested `auto`, model reported `gpt-6-luna`. One fresh invocation, zero schema retries. The oracle-free Scenario Suite execution passed with `DISCOVERY_REQUIRES_REVIEW` and `calibration_claim=NOT_APPLICABLE_NO_ORACLE`.

| Target | Source-bound #37804487025 attempt 1 | Source-bound attempt 2 | Neutral contrast #37807128717 |
| --- | --- | --- | --- |
| `prep.preparation-information-model` direct source set | model-context-strategy; product-capabilities; **domain-strategy** | same | **model-context-strategy; product-capabilities** |
| `prep.recorded-activity-history-model` direct source set | model-context-strategy; product-capabilities; **domain-strategy** | same | **model-context-strategy; product-capabilities** |
| Graph reconciliation per target | 2 KEEP, 1 ADD, 0 REMOVE | 2 KEEP, 1 ADD, 0 REMOVE | **2 KEEP, 0 ADD, 0 REMOVE** |
| Product candidates assessed per target | 15 | 15 | 15 |
| Current Information direct / context product needs | 4 / 11 | 3 / 12 | 4 / 11 |
| History direct / context product needs | 4 / 11 | 4 / 11 | 4 / 11 |

All 30 product-applicability records in the neutral run were returned and validated; the source-grounding check found no malformed source references. Both target statuses were `RESOLVED` and both unresolved lists empty. Its `ADD_DIRECTNESS_AUDIT=[]` because no ADD edges were proposed; this is not a semantic proof that none is necessary.

### Exact direct product candidates from neutral contrast

SNAP-01 Preparation Information:
- `REQ-CAP-KNOWLEDGE-KINDS`
- `REQ-CAP-RELATIONSHIP-MEANINGS`
- `REQ-CAP-CROSS-INFORMATION-RELATIONSHIPS`
- `REQ-CAP-EXPLORE-PERSPECTIVES`

SNAP-02 Recorded Activity History:
- `REQ-CAP-RECORD-ACTIVITY`
- `REQ-CAP-RELATE-ACTIVITY`
- `REQ-CAP-PRESERVE-TIME`
- `REQ-CAP-PRESERVE-HISTORY-CONTEXT`

`REQ-CAP-EXPLORE-PERSPECTIVES` varied across the earlier two source-bound trials (DIRECT then CONTEXT_ONLY), and is DIRECT again in the neutral contrast. This illustrates unresolved semantic applicability granularity even when the final supplier-edge set is stable.

## Interpretation

**Positive evidence:** The two `prep.domain-strategy` ADD proposals were sensitive to output obligation formulation: both appeared in both source-bound trials, neither appeared when the DS sections were removed as explicit target obligations. This is consistent with the suspected `source echo` mechanism, and supports treating those direct-edge additions as unsubstantiated pending independent direct-consumption review.

**It does not prove causation or correctness:** The contrast removed literal echo but also changed target wording and source-scoping detail; a single neutral run cannot isolate all mechanisms. No independent expert oracle has established the complete tactical model obligation set, nor whether any unique Domain Strategy rule is indispensable beyond the already-accepted Model Context Strategy contract. Likewise, graph reachability through `Tactical -> Model Context Strategy -> Domain Strategy` alone does not establish that an additional direct dependency would be redundant.

The existing direct `prep.model-context-strategy` and `prep.product-capabilities` edges were retained across all three runs. Neither PREP's accepted graph nor `harness/main` was changed. Automated edge writeback remains disabled.

## Engineering disposition

1. **Do not add** direct `prep.domain-strategy` edges based on the two source-bound proposals. Mark their necessity **UNPROVEN**; a source-copy confound is documented.
2. **Do not delete** any accepted PREP edges on the strength of absence in the neutral control. Complete target-obligation coverage is not established and `REMOVE_CANDIDATE=[]` by policy.
3. Require an independent review of direct-vs-inherited strategic semantics, separately from the presentation of source excerpts and model-generated rationales.
4. Preserve the disputed `REQ-CAP-EXPLORE-PERSPECTIVES` classification as an unresolved semantic design question, not a forced one-provider rule.
5. If another controlled test is needed, use multiple new source-neutral target formulations with equivalent reviewed scope and a separate independent reviewer, not repeated same-prompt sampling alone.

This is a successful read-only diagnostic experiment, not production dependency resolution calibration or accepted topology governance.
