# Active Harness work

Current: `reference-engineering-model-promotion-evidence.md`

Goal: determine, through independent evidence, whether the optional Reference Engineering Model should remain a research layer or is strong enough for a later canonical-promotion decision.

State: research planning

## Baseline

- `main` contains the validated Reference Engineering Model v0 research result from PR #114.
- Reference Engineering Model v0 is optional and non-canonical.
- It materializes the existing Engineering Graph and does not extend Harness Core.
- The post-merge `harness core` workflow is green.

## Current research frontier

1. independent frozen external hold-out validation;
2. reference-model version evolution and migration semantics;
3. explicit proof semantics for safety-critical and AI/agentic specializations.

These are separate research questions. Passing one does not imply the others pass.

## Canonical-promotion gate

Do not promote the Reference Engineering Model unless all of the following are supported by evidence:

- independent hold-outs remain compatible with the frozen model;
- version evolution and migration are defined and reproducible;
- known specialization gaps have explicit semantics;
- materialization remains deterministic and fail-closed;
- no new Harness Core concepts are required;
- project-specific truth remains outside the Reference Model;
- generated Engineering Graphs remain valid under existing validators.

## Next

Run the independent external hold-out research first. Keep evolution/migration and specialization semantics as separate follow-up work until that evidence is available.
