---
name: project-bootstrap-reconcile
description: "Use when starting Harness in a new repository, opening an existing Harness project after Harness changes, or repairing an incomplete Harness realization."
---
# Project Bootstrap / Reconcile

## Trigger
Use before substantial engineering work when project Harness realization is absent, outdated, incomplete or of unknown compatibility with the current reference catalog.

## Inputs
Current Authority catalog, existing Project Authority Assessments when present, Core/Engineering Graph truth, canonical artifacts and unresolved Questions.

## Procedure
1. Inspect existing project Harness/Core truth.
2. Reconcile the Project Authority Assessment registry against the current reference Authority catalog.
3. Preserve existing accepted assessments.
4. Infer REQUIRED only from existing canonical knowledge owned by the Authority.
5. Surface unresolved existing Questions as UNRESOLVED.
6. Leave absence as UNASSESSED; never infer NOT_APPLICABLE from silence.
7. For retired split Authorities, never copy applicability to all replacements; surface ambiguous legacy state as a migration conflict.
8. Validate the registry and project Harness realization.
9. For each selected/known implementation Consumer, run Engineering Coverage activation as an independent diagnostic lens. This is required especially after Harness reference-policy changes: consumer-driven concerns may surface missing production contracts even when the project Engineering Graph has no corresponding Capability yet.
10. Treat Coverage results such as `MODEL_PRODUCTION_CONTRACT`, `ASSIGN_AUTHORITY`, missing subject inventory or semantic revalidation as reconciliation findings. Do not silently add Capabilities or mutate project-owned topology from reference policy alone.
11. Report semantic conflicts for assessment; do not invent evidence.
12. Regenerate Project Engineering Status after reconciliation.

A structurally valid project graph is not evidence that it contains every knowledge contract expected by the current Harness concern policy. Reconciliation therefore combines conservative graph/status preservation with non-destructive Engineering Coverage diagnostics.

The operation must be idempotent and must not duplicate project-owned canonical graphs.
