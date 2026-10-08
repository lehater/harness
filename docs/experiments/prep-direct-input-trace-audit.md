# PREP direct-input pilot: real-contract audit

Status: experimental, not a migration authorization.
Source: `lehater/prep` at `mvp-vertical-slice`, candidate evidence:
- `.harness/candidates/task-model-product-evidence.yaml`
- `.harness/candidates/application-design-task-evidence.yaml`
- `.harness/candidates/application-design-product-evidence.yaml`

## Audit method

For each source Product Capability assertion, compose `Product → Task` and
`Task → Application` evidence at assertion IDs. Compare reachable application
assertions to the historical direct `Product → Application` evidence. This
compares *declared trace edges*, not semantic correctness of the artifacts.

All 16 source requirement IDs have paths to at least one application assertion.
Only 11 have all their historic direct application targets reachable by the
two-step chain. Six direct targets are not reachable:

| Product source | Direct application target missing through Task |
|---|---|
| REQ-CAP-EVIDENCE-CONTEXT | AD-EVALUATE-EVIDENCE |
| REQ-CAP-STATE | AD-REVIEW-GAPS |
| REQ-CAP-EVIDENCE-JUSTIFICATION | AD-OUTCOME-MODEL |
| REQ-CAP-ADAPT | AD-CURRENTNESS-BASIS |
| REQ-CAP-BOOTSTRAP | AD-PARTIAL-PREPARATION |
| REQ-CAP-BOOTSTRAP | AD-OUTCOME-MODEL |

The composed trace additionally reaches `REQ-CAP-FOCUS → AD-REVIEW-CHANGE`
and `REQ-CAP-ADAPT → AD-EVALUATE-EVIDENCE`, which are absent from the direct map.
These are differences in declared evidence; they do not alone prove a defect.

## Architecture decision gate

Do **not** remove `prep.product-capabilities` from
`prep.application-design.requires` until:
1. Each mismatch is classified against accepted Task Model and Application
   Design contents. Correct incomplete local derivation evidence where justified.
2. Any source constraint actually consumed by Application Design directly is
   retained as a true direct dependency; no automatic transitive reduction.
3. The composition is checked against the **complete** intended source scope,
   including explicit NOT_APPLICABLE dispositions (not only linked sources).
4. Core `depends_on`, lifecycle accepted prerequisite baseline, derivation
   coverage and publication checks are migrated atomically in PREP.
5. Full Harness Scenario Suite and PREP integration tests pass on proposed changes.

Current `compose_derivations` is a read-only *linked-path projection*.
It does not independently establish semantic truth or completeness of all
relevant source atoms. Its `ACCEPTED` status means only that all mapped
origins have a reachable endpoint through accepted local derivation
evaluations. It is not a replacement for direct-input semantic review.

No PREP canonical artifacts were changed by this audit.
