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
Read accepted IA/interaction/task/journey/conceptual/security knowledge needed to partition views and navigation. Existing routes, Figma frames, frontend components and site maps are evidence/projections unless explicitly canonical. IA locations and upstream task/application responsibilities are analysis inputs; neither implies a one-to-one view or route partition.

## Procedure
1. Enumerate material interaction contexts, IA locations and candidate task-view/structural-frame boundaries required to realize accepted work. Give each material candidate boundary a stable identity and participating contexts/views.
2. For each material candidate view boundary, review goal/decision continuity, simultaneous or persistent information dependency, transient working-state continuity, commit/cancel/recovery semantics, material mode/role/authorization change, independent revisit/deep-link/resume value, and context-switch/refinding cost.
3. In semantic review, classify each material boundary as contestable or deterministically constrained and classify the rationale bases. Separate task journeys, application capabilities, use cases, feature/component ownership, routes or data ownership are inputs to this review, not independent proof of a separate user-facing destination.
4. A material separate view requires at least one accepted user-facing boundary basis such as a materially different user goal/context, independent addressability/resume value, material mode/authority change, commit/cancel/recovery boundary, incompatible simultaneous information dependency, intentional context switch, or accepted findability/navigation need. Semantic review owns the classification; do not infer it from labels or keywords.
5. For every materially contestable boundary, use Decision Governance for the registered `view-boundaries` axis with that boundary as a decision subject. Challenge at least merge-versus-separate-view and persistent-context-versus-navigation alternatives locally before selecting or escalating. Pane/region/disclosure are evidence for the one-view alternative; their concrete composition stays downstream.
6. A material deterministic boundary may omit alternative exploration only when accepted constraints are cited explicitly with a deterministic rationale. Several boundaries may share one decision only when semantic review establishes that they are genuinely the same decision context with the same material consequences.
7. Give each accepted view one coherent primary responsibility stated in user-semantic terms.
8. Map each task view to interaction contexts and IA locations. Structural frames may omit interaction refs only when explicitly marked structural. Do not infer `one IA location = one view` or `different IA location = separate route`.
9. Define root/parent, canonical entry/direct-link semantics and material exits/cross-links.
10. Prove every interaction context has a view disposition or explicit non-view rationale.
11. Prove USER task coverage transitively through contexts to views.
12. Detect duplicated/mixed responsibilities and unjustified repeated A -> B -> A navigation under one unchanged goal before local screen design.
13. Keep regions/layout/patterns/components/styling downstream.
14. Route missing upstream interaction/information semantics or unresolved boundary choices as Questions.
15. Produce/register and reevaluate.

## Stop conditions
Stop when view identity/responsibility or navigation relationships cannot be chosen without inventing missing task, IA, interaction, authorization or product semantics, or when a material view-boundary choice remains unresolved after required Decision Governance exploration.

## Output contract
Complete task-view and structural-frame ids; a stable material-boundary inventory with participants, materiality, contestability and disposition; accepted user-facing boundary bases; Decision Governance refs or deterministic evidence for material boundaries; one primary responsibility per view; structural marker where applicable; IA-location refs; interaction-context refs for task views; root/parent relationships; entries/exits/cross-links/direct-link semantics where material; non-view dispositions; unresolved Questions.

## Acceptance checks
No interaction context disappears silently; every USER task reaches a task view or accepted no-ui/non-view disposition; structural frames are explicit rather than hidden in projections; parent/exit refs resolve; inventory can derive expected Screen/View subjects; mixed responsibilities are rejected; task/application/component separation alone cannot justify a material separate view; every materially contestable boundary has boundary-local Decision Governance coverage or an explicit blocking Question; deterministic boundaries cite accepted deciding constraints; shared decisions have accepted semantic-equivalence evidence; two tasks/capabilities may remain in one user-facing area and one task may span multiple justified views; IA locations remain conceptual organization rather than page/view semantics; local screen composition remains downstream.

## Registration
Register under HUMAN-INTERFACE-DESIGN and provide only interface-topology capabilities actually materialized.

## Human projection
Site maps, app maps, screen maps and navigation diagrams are generated review projections. Their absence is not a gap when equivalent canonical topology knowledge exists.
