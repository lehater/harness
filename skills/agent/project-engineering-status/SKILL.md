---
name: project-engineering-status
description: "Use when asked what engineering knowledge is complete, missing, blocked, unassessed or not applicable for a Harness project."
---
# Project Engineering Status

## Trigger
Use when project-wide engineering status, applicability or blocked/missing engineering knowledge is requested.

## Inputs
Current Authority catalog, Project Authority Assessments, Engineering Graph/Core realization, Questions and lifecycle evidence.

## Procedure
1. Validate that the assessment registry covers the current Authority catalog.
2. Interpret applicability independently from operational production state.
3. Keep UNASSESSED, REQUIRED, NOT_APPLICABLE and UNRESOLVED explicit.
4. Derive production status only for REQUIRED Authorities from current project evidence.
5. Require accepted evidence for NOT_APPLICABLE and keep UNRESOLVED visible rather than guessing.
6. Never introduce PARTIALLY_APPLICABLE; surface a possible Authority boundary failure instead.
7. Generate status as a disposable projection and never use it as a source of project truth.
