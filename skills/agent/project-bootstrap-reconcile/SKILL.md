---
name: project-bootstrap-reconcile
description: "Use when starting Harness in a new repository, opening an existing Harness project after Harness changes, or repairing an incomplete Harness realization."
---
# Project Bootstrap / Reconcile

Run the deterministic project bootstrap/reconcile mechanism before manually creating Harness state.

1. Inspect existing project Harness/Core truth.
2. Reconcile the Project Authority Assessment registry against the current reference Authority catalog.
3. Preserve existing accepted assessments.
4. Infer REQUIRED only from existing canonical knowledge owned by the Authority.
5. Surface unresolved existing Questions as UNRESOLVED.
6. Leave absence as UNASSESSED; never infer NOT_APPLICABLE from silence.
7. Validate the registry and project Harness realization.
8. Report semantic conflicts for assessment; do not invent evidence.
9. Regenerate Project Engineering Status after reconciliation.

The operation must be idempotent and must not duplicate project-owned canonical graphs.
