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
1. Enumerate material interaction contexts, IA locations and candidate task-view/structural-frame boundaries required to realize accepted work.
2. For each material candidate view boundary, review goal/decision continuity, simultaneous or persistent information dependency, transient working-state continuity, commit/cancel/recovery semantics, material mode/role/authorization change, independent revisit/deep-link/resume value, and context-switch/refinding cost.
3. Reject implementation-shaped justification: entity, aggregate, table, endpoint, service, route or component separation is insufficient by itself to require a separate view.
4. When a boundary remains materially contestable, use Decision Governance for the registered `view-boundaries` axis. Challenge at least merge-versus-separate-view and persistent-context-versus-navigation alternatives before selecting or escalating. Pane/region/disclosure are evidence for the one-view alternative; their concrete composition stays downstream.
5. Give each accepted view one coherent primary responsibility stated in user-semantic terms.
6. Map each task view to interaction contexts and IA locations. Structural frames may omit interaction refs only when explicitly marked structural.
7. Define root/parent, canonical entry/direct-link semantics and material exits/cross-links.
8. Prove every interaction context has a view disposition or explicit non-view rationale.
9. Prove USER task coverage transitively through contexts to views.
10. Detect duplicated/mixed responsibilities and unjustified repeated A -> B -> A navigation under one unchanged goal before local screen design.
11. Keep regions/layout/patterns/components/styling downstream.
12. Route missing upstream interaction/information semantics or unresolved boundary choices as Questions.
13. Produce/register and reevaluate.

## Stop conditions
Stop when view identity/responsibility or navigation relationships cannot be chosen without inventing missing task, IA, interaction, authorization or product semantics, or when a material view-boundary choice remains unresolved after required Decision Governance exploration.

## Output contract
Complete task-view and structural-frame ids; one primary responsibility per view; structural marker where applicable; IA-location refs; interaction-context refs for task views; root/parent relationships; entries/exits/cross-links/direct-link semantics where material; non-view dispositions; unresolved Questions.

## Acceptance checks
No interaction context disappears silently; every USER task reaches a task view or accepted no-ui/non-view disposition; structural frames are explicit rather than hidden in projections; parent/exit refs resolve; inventory can derive expected Screen/View subjects; mixed responsibilities are rejected; no material separate view is justified only by implementation/data ownership structure; materially contestable view boundaries have Decision Governance evidence or an explicit blocking Question; local screen composition remains downstream.

## Registration
Register under HUMAN-INTERFACE-DESIGN and provide only interface-topology capabilities actually materialized.

## Human projection
Site maps, app maps, screen maps and navigation diagrams are generated review projections. Their absence is not a gap when equivalent canonical topology knowledge exists.
