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
Accepted Task Model, User Journeys, Conceptual Interface Model, Application/Machine Interface outcomes, Security semantics and usability/accessibility constraints.

## Read boundary
Read accepted task/journey/conceptual/application/machine/security knowledge needed to define interaction semantics. Existing screens/routes/components are evidence, not authority.

## Procedure
1. Partition USER work into coherent interaction contexts without final screen boundaries.
2. Trace contexts to Task Model tasks and conceptual refs; leave placement into IA locations to Interface Topology.
3. Define actions/inputs/selections and visible system responses.
4. Define material states/transitions including validation, denied, unavailable, conflict, cancellation and recovery.
5. Define focus/keyboard/input semantics where material.
6. Bind server-backed behavior to accepted operation outcomes.
7. Record explicit `no-ui` dispositions for USER tasks that genuinely need no interface surface.
8. Keep page/view inventory, parent navigation and layout downstream.
9. Before semantic admission, identify independently losable user-observable obligations (for example separate actions, visible states, reversible changes or distinct observable outcomes) and account each in `semantic_review.independent_obligations`; do not let one coarse summary atom stand in for several such obligations.
10. Review whether one conceptual entity participates in multiple user-visible roles with materially different lifecycle, side effects or authority implications. Record the applicability judgement in `semantic_review.interaction_role_requirements`. When REQUIRED, define canonical `interaction_roles` with stable role id, concept ref, meaning, entry/exit, allowed transitions, side effects, forbidden side effects and observable distinction; record which facets/transitions are material. When no material multi-role distinction exists, record an explicit NOT_REQUIRED judgement or an empty reviewed requirement set.
11. Classify independently losable user-facing actions, states and distinctions in `semantic_review.observable_realization_obligations` as ACTION, STATE or DISTINCTION and as REQUIRED, NOT_APPLICABLE or QUESTION. A non-required classification needs rationale; a Question remains blocking.
12. Route missing upstream semantics as Questions.
13. Produce/register and reevaluate.

## Stop conditions
Stop when an action, system response, recovery path, authorization distinction or machine outcome is not accepted upstream and continuing would invent behavior.

## Output contract
Interaction-context ids; task/concept refs; actions/inputs/selections; states/transitions/recovery; operation/outcome bindings where applicable; reviewed cross-context role applicability plus canonical `interaction_roles` when material; observable-realization applicability/category review for user-facing semantic obligations; no-ui task dispositions with rationale; unresolved Questions.

## Acceptance checks
Every USER task has interaction coverage or explicit no-ui disposition; independently losable user-observable obligations have separate semantic accounting rather than a shared coarse summary atom; material cross-context roles are coherently distinguished without inferring applicability from subject strings; materially user-facing actions/states/distinctions have explicit observable-realization applicability/category review; actions/outcomes trace upstream; contexts do not smuggle in page/layout decisions; authorization/recovery are explicit; Topology can map contexts to views without inventing interaction.

## Registration
Register under HUMAN-INTERFACE-DESIGN and provide only interaction-design capabilities actually materialized.

## Human projection
Task flows, state diagrams and behavioral prototypes are projections/evidence.
