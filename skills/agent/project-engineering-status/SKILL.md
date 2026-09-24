---
name: project-engineering-status
description: "Use when asked what engineering knowledge is complete, missing, blocked, unassessed or not applicable for a Harness project."
---
# Project Engineering Status

Use the deterministic status projection. Do not manually maintain progress fields.

Inputs are the current Authority catalog, Project Authority Assessments, Engineering Graph/Core realization, Questions and lifecycle evidence.

Interpret applicability independently from operational production state:
- UNASSESSED / REQUIRED / NOT_APPLICABLE / UNRESOLVED are assessment states.
- production status is derived only for REQUIRED Authorities.
- NOT_APPLICABLE requires accepted evidence.
- UNRESOLVED must remain visible rather than being guessed.
- never introduce PARTIALLY_APPLICABLE; report a possible Authority boundary failure instead.

The generated status document is disposable and must not become a source of project truth.
