---
name: task-model
description: "Use for actionable CREATE work requiring a canonical intended human-work model between accepted User Requirements/domain semantics and usage scenarios/interface design."
---

# Task Model

## Trigger

Use when actionable work has `knowledge_kind: task-model` and Application Design
must establish intended work required to achieve accepted user goals before
individual journeys or interface structure are selected.

## Responsibility

Own goal-to-task decomposition and responsibility allocation needed for application
support. State what work must be performed and by whom without deciding screens,
navigation, layout or frontend technology.

## Inputs

- accepted User Needs / Context of Use;
- accepted Product/User Requirements;
- accepted Domain Use-Case/tactical semantics needed by selected goals;
- accepted security/policy constraints where they change observable work.

## Procedure

1. Select an accepted user goal and its User Needs/User Requirements.
2. Decompose intended work into tasks/subtasks until each leaf has one clear
   responsibility and observable outcome.
3. Record ordering/plan/dependency semantics where material.
4. Allocate each leaf to USER, SYSTEM or EXTERNAL_ACTOR.
5. For each USER task record required information, decision/selection/input,
   expected observable outcome and required system support or explicit offline disposition.
6. Record alternate/recovery tasks where accepted failure semantics require them.
7. Perform a human sufficiency review: every selected goal and in-scope User
   Requirement has task/support coverage or an explicit disposition/Question.
8. Derive bounded usage scenarios/journeys from this model; do not use one scenario
   as evidence that the task inventory is complete.
9. Route missing Product/Domain/Security semantics to their owner.
10. Register the accepted artifact and reevaluate.

## Stop conditions

Stop when the goal, User Requirement, responsibility allocation or required
information/decision semantics are unresolved. Do not choose screens to fill gaps.

## Output contract

- goal refs;
- User Need/User Requirement refs;
- tasks/subtasks and plans/dependencies;
- responsibility allocation;
- information requirements;
- decisions/selections/inputs;
- expected outcomes;
- required system support;
- alternate/recovery tasks;
- sufficiency-review disposition;
- unresolved Questions.

## Acceptance checks

- all in-scope goals/requirements have task/support coverage or explicit disposition;
- each leaf task has exactly one responsibility owner;
- USER tasks expose enough information/decision/input semantics for downstream
  Interaction Design without inventing behavior;
- journeys can be derived without inventing additional required work;
- no screen/navigation/layout decision is used as task semantics.

## Registration

Register under APPLICATION-DESIGN. Dependencies include accepted User Needs,
Product Requirements and Domain semantics actually consumed.
