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
3. Before authoring expectations manually, check whether the target repository already owns an explicit consumer/input contract that declares required `capability + authority` pairs for the selected scope. When it does, treat that contract as the policy owner and derive/translate the Design Profile from it rather than maintaining a second independent requirement list.
4. When such a contract declares a requirement `NOT_APPLICABLE` only because another accepted capability proves the non-applicability, translate the expectation to that evidence capability. Do not add a generic N/A status to Design Profile merely to mirror a project-native contract vocabulary.
5. Represent each required knowledge item as `subject + capability + authority`.
6. Add `depends_on` between expectations when downstream knowledge cannot be responsibly formed before upstream knowledge is accepted. Derive ordering from existing canonical dependency/consumer topology when available rather than inventing a parallel workflow.
7. Keep project-level design knowledge separate from change/slice-specific readiness.
8. Prefer existing project vocabulary for capabilities and Authorities.
9. Reuse a starter profile only as a checklist; adapt it to the actual repository.
10. Evaluate the profile against the current Core graph and inspect the resulting frontier.
11. If implementation later exposes a semantic capability that was genuinely required for the selected scope but absent from the profile, add that expectation after the gap is understood. Do not rely only on the historical Question: the refined profile should remember the newly demonstrated knowledge requirement.

## Review questions

Before accepting a profile, ask:

- Is the profile duplicating a canonical consumer/input contract that should remain the single policy owner?
- Is a project-native NOT_APPLICABLE decision already proven by canonical evidence that should be represented as an ordinary evidence capability instead of a new Harness status?
- Could an implementation agent satisfy every expectation and still need to invent a product/domain/architecture decision?
- Does the profile omit a verification strategy needed to know how accepted behavior will be checked?
- Is any expectation really a task, workflow state, approval or implementation step rather than engineering knowledge?
- Is a slice-specific readiness concern being incorrectly promoted to permanent project-level knowledge?
- Are prerequisites explicit enough that Harness exposes only safe `CREATE` actions?

## Important limit

Harness validates a declared profile; it does not prove the profile itself complete. Profile quality remains agent judgement during this phase of the project.
