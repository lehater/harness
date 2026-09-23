# HCD requirements/task closure v1 experiment

Status: research / branch-only

## Hypothesis

A human-interactive Consumer must not progress from Product Requirements directly
into Journey/Interface work when accepted User Needs or an intended Task Model
are absent.

The experiment keeps Core unchanged and uses existing Engineering Graph production
prerequisites:

```text
Problem Evidence
→ User Needs / Context of Use
→ Product Requirements
→ Domain Use-Case semantics
→ Task Model
→ User Journey
→ Human Interface Design
→ Screen/View Design
```

## Experimental knowledge kinds

- `user-needs`, owned by DISCOVERY: Context of Use, goals, solution-independent
  User Needs, provenance and human sufficiency review.
- `task-model`, owned by APPLICATION-DESIGN: intended goal-to-task decomposition,
  responsibility allocation, information/decision/input needs and system support.

## Required regression behavior

1. empty realization exposes Problem Evidence only;
2. Problem Evidence exposes User Needs only;
3. User Needs exposes Product Requirements only;
4. accepted requirements/domain prerequisites expose Task Model before Journey;
5. Task Model exposes User Journey;
6. an already-materialized Requirements provider cannot bypass missing User Needs;
7. an already-materialized Journey provider cannot bypass missing Task Model;
8. independent branches such as Security/Quality may remain actionable: causal
   blocking applies to dependent downstream knowledge, not to the whole graph.

## Core decision

No Core change is part of the experiment. The derived profile orders each
expectation by production prerequisites before provider satisfaction is evaluated.
A downstream provider therefore cannot make an unmet predecessor disappear from
the selected Consumer closure.

## Success criterion

The complete user-facing fixture remains COMPLETE after materializing the new
knowledge, while deleting User Needs or Task Model routes CREATE to the correct
existing Authority and keeps the dependent Journey/Interface chain pending.
Independent graph branches remain free to progress.
