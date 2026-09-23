---
name: user-needs
description: "Use for actionable CREATE work requiring an accepted Context of Use and consolidated solution-independent User Needs between Problem Evidence and normative Product Requirements."
---

# User Needs

## Trigger

Use when actionable work has `knowledge_kind: user-needs` and Discovery must
materialize accepted problem-space prerequisites before normative requirements.

## Responsibility

Own accepted Context of Use, user goals and solution-independent User Needs.
Do not decide normative product behavior, domain design, application orchestration
or interface structure.

## Inputs

- accepted Problem Evidence;
- explicit user/stakeholder evidence;
- observed current work/tasks where available;
- material physical, technical, social or organizational context.

## Procedure

1. Identify affected users/actors and selected context of use.
2. State user goals as intended outcomes rather than product features.
3. Record relevant observed/current tasks only as evidence about existing work.
4. Derive consolidated User Needs as prerequisites for achieving each accepted goal.
5. Keep every User Need solution-independent and trace it to accepted evidence.
6. State scope assumptions and unresolved research Questions explicitly.
7. Perform a human sufficiency review: every accepted goal has User Need coverage
   or an explicit disposition/Question.
8. Route normative behavior to Product Requirements and intended future work/task
   structure to Application Design.
9. Register the accepted artifact and reevaluate the selected Consumer.

## Stop conditions

Stop when a goal, actor/context or material need lacks accepted evidence or explicit
stakeholder input. Do not infer missing needs from UI, API, domain entities or code.

## Output contract

- users/actors;
- context of use;
- accepted user goals;
- relevant observed/current tasks;
- User Needs with evidence/provenance;
- scope/assumptions;
- sufficiency-review disposition;
- unresolved Questions.

## Acceptance checks

- every User Need identifies user/goal/context;
- every User Need is solution-independent;
- every User Need has evidence/provenance;
- observed tasks are not silently treated as future task design;
- normative requirements are not accepted here;
- missing knowledge remains explicit.

## Registration

Register under DISCOVERY. Dependencies include accepted Problem Evidence and other
canonical evidence actually consumed.
