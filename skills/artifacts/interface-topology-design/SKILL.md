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

## Procedure
1. Enumerate every material view/context required to realize accepted interaction contexts.
2. Give each view one coherent primary responsibility.
3. Map each view to interaction contexts and IA locations.
4. Define root/parent, canonical entry/direct-link semantics and material exits/cross-links.
5. Prove every interaction context has a view disposition or explicit non-view rationale.
6. Prove USER task coverage transitively through contexts to views.
7. Detect duplicated/mixed responsibilities before local screen design.
8. Keep regions/layout/patterns/components/styling downstream.
9. Route missing upstream interaction/information semantics as Questions.
10. Produce/register and reevaluate.

## Acceptance checks
No interaction context disappears silently; every USER task reaches a view or accepted no-ui/non-view disposition; parent/exit refs resolve; inventory can derive expected Screen/View subjects; mixed responsibilities are rejected; local screen composition remains downstream.

## Human projection
Site maps, app maps, screen maps and navigation diagrams are generated review projections. Their absence is not a gap when equivalent canonical topology knowledge exists.
