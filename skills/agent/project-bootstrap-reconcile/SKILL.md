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
9. Report semantic conflicts for assessment; do not invent evidence.
10. Regenerate Project Engineering Status after reconciliation.

The operation must be idempotent and must not duplicate project-owned canonical graphs.
