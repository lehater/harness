# CDR producer-direction contrast — GitHub Copilot experiment, 2026-10-08

Status: **experimentally observed model behavior; not independent expert proof, not Authority acceptance**.

## Run identities and controlled change

Baseline: [GitHub Actions 37833242228](https://github.com/lehater/harness/actions/runs/37833242228); [full evidence ZIP](https://github.com/lehater/harness/actions/runs/37833242228/artifacts/11575005076); branch `experiment/cdr-reference-provider-once-20261008`.

Intervention: [GitHub Actions 37835221464](https://github.com/lehater/harness/actions/runs/37835221464); [full evidence ZIP](https://github.com/lehater/harness/actions/runs/37835221464/artifacts/11575796184); branch `experiment/cdr-direction-one-shot-20261008`.

- Both runs used the same pinned source-only `reference/request.json` and `reference/inputs.json` **with byte-for-byte equal JSON contents**, including the opaque case requests and all 39 candidate providers per target.
- Both resolved GitHub Copilot CLI `auto` to model label `gpt-6-luna`, and neither needed a schema retry. These execution labels are observed provider metadata; model repeatability is **not** assumed.
- The deliberate intervention was adding a general producer/consumer direction test to the experimental `PROTOCOL_INSTRUCTION` in `evals/adapters/copilot_dependency_resolution_evaluator.py`: supplier output must be an independently producible input to target, not a later artifact that consumes target output. It also preserves valid directly used transitive sources.
- Reconciliation remained read-only. The conservative Phase B cycle check had been added between runs; it operates *after* the provider response and was not included in the tool-disabled model context.
- Do not claim a causal efficacy estimate from only one run of each condition. The instruction change is the controlled input intervention; stochastic behavior, provider execution and unreviewed target descriptions remain confounders.

## Reference-model target contrast

| Target | Baseline model-proposed sources | Direction-aware model-proposed sources | Declared overlap before -> after | Model status after |
| --- | ---: | ---: | ---: | --- |
| INTERACTION-DESIGN | 4 | 3 | 1 -> 1 | UNRESOLVED |
| INTERFACE-TOPOLOGY | 4 | 2 | 2 -> 2 | RESOLVED (model's scope-relative claim only) |
| DOMAIN-MODEL | 1 | 2 | 1 -> 2 | UNRESOLVED |
| **Total** | **9** | **7** | **4 -> 5** | **2 unresolved** |

Detailed changes:

- INTERACTION-DESIGN still proposes direct `CONCEPTUAL-INTERFACE-MODEL`, `TASK-MODEL` and `DOMAIN-USE-CASE`. The prior extra `USER-JOURNEY` dropped. Declared `INFORMATION-ARCHITECTURE` is **not suggested** in either trial. This agrees with the earlier source SKILL review hypothesis but cannot alone prove a removable edge.
- INTERFACE-TOPOLOGY now proposes only the two declared providers `INFORMATION-ARCHITECTURE` and `INTERACTION-DESIGN`. Both prior additional proposals (`SCREEN-VIEW-DESIGN` and `USER-JOURNEY`) disappeared. The baseline `INTERFACE-TOPOLOGY -> SCREEN-VIEW-DESIGN` would close a cycle with declared `SCREEN-VIEW-DESIGN -> INTERFACE-TOPOLOGY`; none of the new model proposals is cycle-blocked.
- DOMAIN-MODEL now proposes `MODEL-CONTEXT-STRATEGY` and `DOMAIN-STRATEGY`; previously only Model Context was proposed. Declared `PRODUCT-INTENT` remains unproposed. Neither this omission nor the new strategic proposal resolves directness.
- Both runs cite only unaccepted, reusable research-template outputs (`CONTRACT_ONLY`). Most reference targets remain output-incomplete relative to independent project acceptance. Phase B has no writeback or promotion capability.

Across these three targets, total **new undeclared proposals fell from 5 to 2**, and declared-edge overlap rose from 4 to 5. These are structural correspondence counts, **not precision or recall against expert truth**.

## Pre-existing synthetic holdout

The same direction-aware prompt was evaluated in a separately blinded call against four **pre-existing** synthetic cases from `spec/dependency-resolution/calibration-inputs-v1.yaml`: CDR-01 through CDR-04. Their answer key in `calibration-oracle-v1.yaml` was loaded **only after** the model returned. Those labels are `AUTHOR_DRAFT`, not an independently expert-validated oracle.

Results of [holdout comparison](https://github.com/lehater/harness/actions/runs/37835221464/artifacts/11575796184):
- All 4 model case statuses, unresolved-obligation sets and direct need mappings match the pre-authored expectations.
- 7 draft-expected direct provider edges matched, 0 false-positive and 0 omitted edges; draft-label precision=1.0, recall=1.0 **relative only to this four-case author key**.
- The direct/transitive control CDR-03 retained **both** deletion task and deletion product policy as direct dependencies even though the task source consumes the policy.
- The unrelated telemetry control CDR-02 did not promote an operational measurement source to direct human interaction meaning; CDR-04 preserved the unresolved consent rule.
- Holdout output `evidence_assessment=LEGACY_NOT_EVIDENCE_ASSESSED`, `oracle_is_expert_validated=false`, `calibration_claim=NOT_ESTABLISHED`, `automatic_writeback_allowed=false`. The numerical agreement does not override those limitations.

## Implementation and remaining work

New experimental directional prompt is covered by `tests/test_copilot_dependency_resolution_evaluator.py`. Reusable offline holdout harness `evals/cdr_direction_holdout.py` and `tests/test_cdr_direction_holdout.py` check source-only blinding, stable request identity, fail-closed response binding and non-promotion of draft labels. Both are in the Draft-safe focused CI and full Harness registry. The experimental CDR pilot and reference Cycle Block remain read-only.

**Still required before using CDR for authoritative edge changes:**
1. An independently accepted project-specific target output contract with identifiable output obligations and accepted provider public claims.
2. Owner-reviewed counterfactual mediation and source change sensitivity; graph reachability alone remains insufficient.
3. More independent unseen target/producers, plus repeated provider executions where a stability claim is needed.
4. Fresh full Harness gate on current experiment HEAD: last full PASS predates the direction-prompt and holdout additions.

No changes to `lehater/harness@main`, `lehater/prep`, or the frozen Reference Engineering Model v0. PR #220 stays Draft, and one-shot external workflows live only on disposable non-PR experiment branches.
