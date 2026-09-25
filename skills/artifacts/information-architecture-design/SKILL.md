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

## Read boundary
Read accepted conceptual/task/journey/content knowledge needed to organize information. Existing site maps, routes, menus and screen layouts are evidence or projections unless explicitly canonical.

## Procedure
1. Enumerate information objects and conceptual locations needed for accepted tasks.
2. Define grouping/hierarchy/cross-links from task/conceptual cohesion, not backend resource shape.
3. Define stable labels/terminology where findability depends on them.
4. Identify global versus contextual scope.
5. Record findability assumptions requiring validation.
6. Keep routes, pages, regions and visual layout downstream.
7. Route unresolved terminology/product meaning upstream.
8. Produce/register and reevaluate.

## Stop conditions
Stop when information grouping or labels would require inventing product/domain meaning, task priority or audience assumptions.

## Output contract
Location ids/purposes; conceptual refs; grouping/hierarchy/cross-links; labels/taxonomy where material; scope; findability assumptions; unresolved Questions.

## Acceptance checks
Locations trace to accepted tasks/information needs; grouping is not a backend mirror by default; conceptual refs resolve; page/layout is not IA semantics; downstream interaction/topology can proceed without inventing organization.

## Registration
Register under HUMAN-INTERFACE-DESIGN and provide only information-architecture capabilities actually materialized.

## Human projection
Sitemaps, content inventories, card-sort diagrams and taxonomy trees are projections/evidence.
