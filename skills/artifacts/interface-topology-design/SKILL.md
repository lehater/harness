---
name: interface-topology-design
description: "Define the complete user-facing view/context inventory and navigation relationships before individual Screen/View composition."
---
# Interface Topology Design

## Trigger
Use when actionable work has `knowledge_kind: interface-topology-design`.

Owner: HUMAN-INTERFACE-DESIGN.

## Responsibility
Define the complete topology of user-facing views/contexts: identity, one primary responsibility, task/interaction coverage, parent/root, entry/exit/cross-link relationships and navigation continuity. It answers which views exist and how they connect, not how each view is composed.

## Inputs
Accepted Information Architecture, Interaction Design, Task Model/User Journeys, Conceptual Interface Model and authorization/context constraints affecting reachability.

## Read boundary
Read accepted IA/interaction/task/journey/conceptual/security knowledge needed to partition views and navigation. Existing routes, Figma frames, frontend components and site maps are evidence/projections unless explicitly canonical.

## Procedure
1. Enumerate every material task view and every material structural frame/shell required to realize accepted interaction/navigation context.
2. Give each view one coherent primary responsibility.
3. Map each task view to interaction contexts and IA locations. Structural frames may omit interaction refs only when explicitly marked structural.
4. Define root/parent, canonical entry/direct-link semantics and material exits/cross-links.
5. Prove every interaction context has a view disposition or explicit non-view rationale.
6. Prove USER task coverage transitively through contexts to views.
7. Detect duplicated/mixed responsibilities before local screen design.
8. Keep regions/layout/patterns/components/styling downstream.
9. Route missing upstream interaction/information semantics as Questions.
10. Produce/register and reevaluate.

## Stop conditions
Stop when view identity/responsibility or navigation relationships cannot be chosen without inventing missing task, IA, interaction, authorization or product semantics.

## Output contract
Complete task-view and structural-frame ids; one primary responsibility per view; structural marker where applicable; IA-location refs; interaction-context refs for task views; root/parent relationships; entries/exits/cross-links/direct-link semantics where material; non-view dispositions; unresolved Questions.

## Acceptance checks
No interaction context disappears silently; every USER task reaches a task view or accepted no-ui/non-view disposition; structural frames are explicit rather than hidden in projections; parent/exit refs resolve; inventory can derive expected Screen/View subjects; mixed responsibilities are rejected; local screen composition remains downstream.

## Registration
Register under HUMAN-INTERFACE-DESIGN and provide only interface-topology capabilities actually materialized.

## Human projection
Site maps, app maps, screen maps and navigation diagrams are generated review projections. Their absence is not a gap when equivalent canonical topology knowledge exists.
