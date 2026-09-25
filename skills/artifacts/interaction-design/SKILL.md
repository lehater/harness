---
name: interaction-design
description: "Define user actions, system responses, interaction contexts, states, transitions and recovery before concrete view topology/composition."
---
# Interaction Design

## Trigger
Use when actionable work has `knowledge_kind: interaction-design`.

Owner: HUMAN-INTERFACE-DESIGN.

## Responsibility
Define how the human acts on the accepted application and how the system responds visibly, without deciding the complete screen inventory or local visual composition.

## Inputs
Accepted Task Model, User Journeys, Conceptual Interface Model, relevant Information Architecture, Application/Machine Interface outcomes, Security semantics and usability/accessibility constraints.

## Procedure
1. Partition USER work into coherent interaction contexts without final screen boundaries.
2. Trace contexts to Task Model tasks and IA/concept refs.
3. Define actions/inputs/selections and visible system responses.
4. Define material states/transitions including validation, denied, unavailable, conflict, cancellation and recovery.
5. Define focus/keyboard/input semantics where material.
6. Bind server-backed behavior to accepted operation outcomes.
7. Record explicit `no-ui` dispositions for USER tasks that genuinely need no interface surface.
8. Keep page/view inventory, parent navigation and layout downstream.
9. Route missing upstream semantics as Questions.
10. Produce/register and reevaluate.

## Acceptance checks
Every USER task has interaction coverage or explicit no-ui disposition; actions/outcomes trace upstream; contexts do not smuggle in page/layout decisions; authorization/recovery are explicit; Topology can map contexts to views without inventing interaction.

## Human projection
Task flows, state diagrams and behavioral prototypes are projections/evidence.
