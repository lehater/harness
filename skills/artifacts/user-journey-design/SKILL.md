---
name: user-journey-design
description: "Use for actionable CREATE work requiring a canonical user-task/journey contract from accepted product/domain/application semantics before human-interface design. Define goal-oriented interaction and alternate/recovery paths without deciding screens or technical UI realization."
---

# User Journey Design

## Trigger

Use when actionable work has `knowledge_kind: user-journey-design` and Application Design must make user-goal-oriented interaction explicit before Interface Design.

## Inputs

- actionable grouped work and Application Design Authority;
- accepted Product Requirements;
- accepted Domain Use-Case / tactical semantics needed by the selected journey;
- accepted authorization/product-policy semantics that affect observable flow;
- unresolved application-composition Questions.

## Read boundary

Read only accepted canonical sources needed to establish:

- actor and user goal;
- entry conditions;
- meaningful user/system interactions;
- decision and alternate paths;
- externally visible failures/recovery;
- completion conditions and side effects.

Do not read existing screens/routes/components as design authority.

## Procedure

1. Select one bounded user goal or tightly coherent journey scope.
2. Identify actor, trigger, preconditions and accepted completion outcome.
3. Trace meaningful user actions and system responses without assigning them to screens.
4. Preserve owner-defined domain states, identities, rejections and authorization semantics.
5. Make alternate, denied, invalid, unavailable and recovery paths explicit where material.
6. Record externally visible side effects and facts that must remain distinguishable.
7. Keep navigation, screen/view partitioning, layout and frontend technology downstream.
8. Route missing product/domain/security semantics to the owning Authority as Questions.
9. Produce the project-native journey contract, semantically accept/register and reevaluate.

## Stop conditions

Stop when:

- the user goal or completion outcome is not accepted;
- a required domain/application outcome is unresolved;
- authorization semantics needed to describe the journey are unresolved;
- continuing would require choosing screens, routes or technical UI behavior to fill a semantic gap.

## Output contract

A useful journey contract includes:

- actor;
- goal;
- entry condition;
- preconditions;
- ordered meaningful interactions;
- system-visible outcomes;
- alternate/failure/recovery paths;
- completion condition;
- externally visible side effects;
- upstream references and unresolved Questions.

A journey is not a screen flow.

## Acceptance checks

- every journey outcome traces to accepted upstream truth;
- no screen/page/modal decision is used as product semantics;
- alternate and failure paths are represented when materially observable;
- domain and authorization ownership remains upstream;
- the result is sufficient for Interface Design to choose interaction/navigation structure without inventing product behavior.

## Registration

Register under Application Design and provide only the user-journey capability actually established. Dependencies include canonical Product/Domain/Application/Security knowledge consumed.

## Human projection

Prefer a concise goal-oriented journey narrative or state/interaction table. Screen diagrams remain downstream Interface Design projections.
