---
name: information-architecture-design
description: "Organize user-facing information, conceptual locations, grouping, taxonomy and findability before navigation/view topology."
---
# Information Architecture Design

## Trigger
Use when actionable work has `knowledge_kind: information-architecture-design`.

Owner: HUMAN-INTERFACE-DESIGN.

## Responsibility
Define how accepted user-facing concepts/content are organized and found: conceptual locations, grouping, taxonomy/labels, hierarchy/cross-links and global/contextual scope. Do not decide concrete screen composition.

## Inputs
Accepted Conceptual Interface Model, Task Model, User Journeys, exposed content/domain identities, and applicable localization/accessibility constraints.

## Procedure
1. Enumerate information objects and conceptual locations needed for accepted tasks.
2. Define grouping/hierarchy/cross-links from task/conceptual cohesion, not backend resource shape.
3. Define stable labels/terminology where findability depends on them.
4. Identify global versus contextual scope.
5. Record findability assumptions requiring validation.
6. Keep routes, pages, regions and visual layout downstream.
7. Route unresolved terminology/product meaning upstream.
8. Produce/register and reevaluate.

## Output contract
Location ids/purposes; conceptual refs; grouping/hierarchy/cross-links; labels/taxonomy where material; scope; findability assumptions; Questions.

## Acceptance checks
Locations trace to accepted tasks/information needs; grouping is not a backend mirror by default; conceptual refs resolve; page/layout is not IA semantics; downstream interaction/topology can proceed without inventing organization.

## Human projection
Sitemaps, content inventories, card-sort diagrams and taxonomy trees are projections/evidence.
