# Capability Dependency Resolution v1 — research artifact pack

Status: **experimental research**, on `lehater/harness` experimental branch. `lehater/prep` remains unchanged.

## Files

- `SKILL.md` — proposed agent instruction for `skills/agent/capability-dependency-resolution/SKILL.md`.
- `spec/dependency-resolution/calibration-inputs-v1.yaml` — six Phase A discovery cases with target obligations and a bounded provider catalog. It contains **no target requires or expert labels**.
- `spec/dependency-resolution/calibration-oracle-v1.yaml` — **separate scoring-only** baseline requires, candidate expected requires, need-to-obligation-to-provider mappings and expected findings.
- `evals/dependency_resolution_calibration.py` — local deterministic fixture validator and optional scorer for independent agent predictions. No LLM calls or Graph mutations.

## Execution protocol

1. Pin the Harness and PREP source revisions. The PREP source files were read from `mvp-vertical-slice`; before operational use, pin a commit SHA and re-check for drift.
2. Give the evaluated agent exactly one case's `target`, `provider_catalog`, and optional `known_uncertainties` from `spec/dependency-resolution/calibration-inputs-v1.yaml`, plus `SKILL.md` Phase A. Do **not** give it the oracle, current graph or baseline `requires`. The evaluator execution context must not grant tool/repository access that can recover those hidden inputs.
3. Collect Phase A structured predictions and freeze them. The required minimum response fields for scoring are `id`, `status`, `proposed_requires`, `input_needs` (`obligation`, `provider` for each established direct need), and `unresolved_obligations`.
4. Only for Phase B reconciliation reveal that case's `baseline_requires` from the oracle. Do not reveal `expected_requires`, expected findings or `expected_direct_needs`.
5. Score the frozen Phase A predictions with `evals/dependency_resolution_calibration.py`. The deterministic scorer measures edge-set precision/recall, direct-need coverage and status/unresolved correctness. Explanations and soundness of removals require an independent human/semantic review.
6. Treat `PROJECT_HYPOTHESIS` and `AUTHOR_DRAFT` oracles as **unapproved** until independently reviewed. No performance/quality claims are warranted from comparisons to these labels alone.
7. When evaluating actual graph mutation proposals, construct a candidate project graph and pass it to existing Harness graph validators. No canonical write is authorized by this pack.

## Commands

```bash
python evals/dependency_resolution_calibration.py validate spec/dependency-resolution/calibration-inputs-v1.yaml spec/dependency-resolution/calibration-oracle-v1.yaml
python evals/dependency_resolution_calibration.py score spec/dependency-resolution/calibration-inputs-v1.yaml spec/dependency-resolution/calibration-oracle-v1.yaml agent-predictions.yaml
```

An agent prediction file has:

```yaml
version: 1
kind: harness-dependency-resolution-predictions
cases:
  - id: CDR-01
    status: RESOLVED
    proposed_requires: [demo.product-edit-policy, demo.resource-domain]
    input_needs:
      - {obligation: enforce-product-edit-policy, provider: demo.product-edit-policy}
      - {obligation: preserve-domain-validity, provider: demo.resource-domain}
    unresolved_obligations: []
```

This example is illustrative, **not** proof of an agent run. The scorer does not invent missing predictions or infer semantic validity from edge equality.

## Reference files

Harness:
- `docs/design/engineering-graph-v0.md`
- `skills/artifacts/domain-model/SKILL.md`
- `src/harness/application/scenario_suite.py`
- `evals/live_calibration_process_driver.py`

PREP branch `mvp-vertical-slice`:
- `.harness/engineering-graph.yaml`
- `.harness/core.yaml`
- `.harness/knowledge/product-capabilities.yaml`
- `docs/architecture/context-map.md`
- `docs/architecture/model-context-map.md`

## Integration decision

For the first executable Scenario Suite experiment, register an external driver module through the existing `--driver-module` CLI option. Do not add a second runner. The driver must use a label-blind request; expert oracle data remains outside the external evaluator process. The full `requires` reconciliation happens **after** Phase A, and must not overwrite the frozen independent answer.

## Limitations

- PREP excerpt-based source surfaces may omit important accepted semantics; the definitive test should derive those surfaces from pinned canonical source snapshots, not only this explanatory projection.
- No real LLM/agent has been run by this pack.
- A structural match with the oracle does not establish semantic necessity or completeness.
- No existing Harness Scenario Suite driver for Dependency Resolution is claimed by this pack.
- Graph topology publication and Lifecycle revalidation are a separate later integration block.