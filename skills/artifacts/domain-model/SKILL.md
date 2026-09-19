---
name: domain-model
description: "Use for an actionable CREATE expectation that requires a compact canonical domain model or core domain concepts. Produce domain-model/v1 from accepted project semantics; create Questions instead of inventing missing domain decisions."
---

# Domain Model Artifact

## Trigger

Use when target state exposes an actionable `CREATE` whose required knowledge is a domain model, ubiquitous language, core concepts or domain invariants and `domain-model/v1` is an appropriate representation.

Do not use for Architecture, Verification, Requirements or implementation tasks.

## Inputs

- the `CREATE` expectation;
- its Authority;
- satisfied prerequisite expectations;
- canonical artifacts that supply the domain semantics.

## Read boundary

Read only the canonical sources needed to establish:

- purpose of the selected domain scope;
- accepted terms and meanings;
- concepts and identity where relevant;
- responsibilities owned by those concepts;
- accepted invariants.

Do not mine the whole repository.

## Procedure

1. Confirm the expectation is `CREATE`, not `WAIT` or `PENDING`.
2. Confirm the deciding Authority owns the requested semantics.
3. Extract only accepted semantics from canonical sources.
4. Reconcile repeated wording into one meaning without changing the underlying decision.
5. If canonical sources conflict or a required invariant is undecided, create a Core `Question` and stop acceptance of the affected knowledge.
6. Draft a `harness-knowledge-artifact` using `domain-model/v1`.
7. Run `workspace.py validate-artifact` on the candidate.
8. Apply the common semantic-acceptance checks from `docs/design/agent-artifact-workbench-v0.md`.
9. Register the accepted artifact in the Core graph with dependencies on the canonical sources actually relied upon.
10. Render the human Domain Model and re-evaluate target state.

## Output schema

`domain-model/v1`.

Minimum useful content:

- purpose;
- ubiquitous-language terms when needed;
- domain concepts;
- responsibilities;
- invariants.

Do not add fields merely to make the document look comprehensive.

## Artifact-specific acceptance

- every term reflects accepted project vocabulary;
- concept responsibility does not steal ownership from another Authority;
- invariants are actual accepted constraints, not implementation preferences;
- omitted unknowns are not converted into implied decisions;
- the artifact provides the requested capability, not merely a summary of existing prose.

## Human projection

A generated Domain Model Markdown document under the configured generated-docs directory.
