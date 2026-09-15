---
name: agent-harness-design
description: "Use when designing, reviewing or simplifying reusable Harness methodology, Skills, routing, context loading, validators or evaluation mechanics. Prefer the smallest change that removes a demonstrated Harness problem."
---

# Agent Harness Design

Audit:
- source-of-truth ownership;
- progressive context loading;
- task precedence and recoverability;
- Skill overlap and routing boundaries;
- deterministic validation opportunities;
- stale/duplicated guidance;
- unnecessary process/runtime complexity;
- separation between reusable methodology and target-project truth/state.

Rules:
- target-project truth and durable state never belong in reusable Harness Skills;
- protocols own reusable process semantics; Skills explain judgement-heavy execution;
- deterministic invariants belong in validators when practical;
- do not introduce project bindings, runtime state machines or orchestration machinery without demonstrated need;
- keep the Harness usable independently from any specific target repository.
