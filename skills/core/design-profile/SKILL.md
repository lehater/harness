---
name: design-profile
description: "Use when an agent must define or review the engineering knowledge target for a selected project scope. Create the smallest justified Design Profile and explicit prerequisite ordering without claiming that the profile proves its own completeness."
---

# Design Profile

## Trigger

Use before target-state evaluation when no suitable profile exists, or when a consumer failure shows that the current profile omits required engineering knowledge.

## Inputs

- user goal and selected implementation/design scope;
- target repository lifecycle/instruction documents;
- existing accepted requirements/domain/architecture boundaries;
- reusable starter profiles when applicable.

## Procedure

1. State the selected scope in concrete terms.
2. Identify the engineering knowledge that must exist for an agent to implement that scope without inventing Requirements, Domain or Architecture decisions.
3. Represent each required knowledge item as `subject + capability + authority`.
4. Add `depends_on` between expectations when downstream knowledge cannot be responsibly formed before upstream knowledge is accepted.
5. Keep project-level design knowledge separate from change/slice-specific readiness.
6. Prefer existing project vocabulary for capabilities and Authorities.
7. Reuse a starter profile only as a checklist; adapt it to the actual repository.
8. Evaluate the profile against the current Core graph and inspect the resulting frontier.

## Review questions

Before accepting a profile, ask:

- Could an implementation agent satisfy every expectation and still need to invent a product/domain/architecture decision?
- Does the profile omit a verification strategy needed to know how accepted behavior will be checked?
- Is any expectation really a task, workflow state, approval or implementation step rather than engineering knowledge?
- Is a slice-specific readiness concern being incorrectly promoted to permanent project-level knowledge?
- Are prerequisites explicit enough that Harness exposes only safe `CREATE` actions?

## Important limit

Harness validates a declared profile; it does not prove the profile itself complete. Profile quality remains agent judgement during this phase of the project.
