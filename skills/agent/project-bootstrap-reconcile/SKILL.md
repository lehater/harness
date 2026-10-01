---
name: project-bootstrap-reconcile
description: "Use when starting Harness in a target repository, opening an existing Harness project after Harness changes, or repairing an absent, outdated, incomplete or unknown Harness realization."
---
# Project Bootstrap / Reconcile

## Trigger
Use before substantial Harness-controlled engineering work when the target
project realization is absent, outdated, incomplete or of unknown compatibility
with the current Harness contracts/reference catalog.

This is the public consumer startup entry. Do not route directly to
`bootstrap-existing-project`; that procedure is an internal subprocedure used
only when no directly usable Core/project realization exists.

## Inputs
- selected task/scope and target repository instructions;
- selected Consumer / Design Profile when already known;
- current Authority catalog;
- existing Project Authority Assessments when present;
- existing Core/Engineering Graph truth, canonical artifacts and unresolved Questions.

## Procedure
1. Read the target repository instructions and selected task/scope.
2. Inspect existing project Harness/Core truth and determine whether a directly usable realization exists.
3. If no directly usable Core model/projection exists, invoke the internal `bootstrap-existing-project` procedure with the selected scope/profile. Reuse an existing project-owned canonical graph/projection when available; otherwise build only the smallest scope-driven Core realization. Do not perform a repository-wide inventory.
4. Reconcile the Project Authority Assessment registry against the current reference Authority catalog.
5. Preserve existing accepted assessments.
6. Infer REQUIRED only from existing canonical knowledge owned by the Authority.
7. Surface unresolved existing Questions as UNRESOLVED.
8. Leave absence as UNASSESSED; never infer NOT_APPLICABLE from silence.
9. For retired split Authorities, never copy applicability to all replacements; surface ambiguous legacy state as a migration conflict.
10. Validate the registry and project Harness realization.
11. For each selected/known implementation Consumer, run Engineering Coverage activation as an independent diagnostic lens. This is required especially after Harness reference-policy changes: consumer-driven concerns may surface missing production contracts even when the project Engineering Graph has no corresponding Capability yet.
12. Treat Coverage results such as `MODEL_PRODUCTION_CONTRACT`, `ASSIGN_AUTHORITY`, missing subject inventory or semantic revalidation as reconciliation findings. Do not silently add Capabilities or mutate project-owned topology from reference policy alone.
13. Report semantic conflicts for assessment; do not invent evidence.
14. Regenerate Project Engineering Status after reconciliation.

A structurally valid project graph is not evidence that it contains every
knowledge contract expected by the current Harness concern policy.
Reconciliation therefore combines conservative graph/status preservation with
non-destructive Engineering Coverage diagnostics.

The operation must be idempotent and must not duplicate project-owned canonical
graphs.
