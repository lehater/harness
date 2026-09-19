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
3. Before authoring expectations manually, check whether the target repository already owns explicit policy sources for the selected scope: consumer/input contracts, engineering-completeness rules, coverage declarations or equivalent accepted project policy. Treat those project-owned sources as the policy owners and derive/translate the Design Profile from them rather than maintaining a second independent requirement list.
4. When several independent project-owned policy sources apply, compose their requirements before claiming the selected scope complete. A consumer contract may prove which knowledge classes a downstream responsibility needs while a completeness/coverage policy proves which subjects must be covered; satisfying only one is insufficient.
5. When a consumer contract declares a requirement `NOT_APPLICABLE` only because another accepted capability proves the non-applicability, translate the expectation to that evidence capability. Do not add a generic N/A status to Design Profile merely to mirror a project-native contract vocabulary.
6. Represent each required knowledge item as `subject + capability + authority`. Treat `capability`, not `subject`, as the provider-resolution key.
7. If one broad capability is provided by several same-Authority artifacts for different subjects and the selected policy requires subject-specific coverage, do not assume the `subject` field filters those providers. Reuse the target-owned coverage policy/adapter to derive subject-scoped CapabilityIds, or evaluate the project-specific coverage check alongside the consumer profile, so each required subject can be proven independently.
8. Add `depends_on` between expectations when downstream knowledge cannot be responsibly formed before upstream knowledge is accepted. Derive ordering from existing canonical dependency/consumer topology when available rather than inventing a parallel workflow.
9. Keep project-level design knowledge separate from change/slice-specific readiness.
10. Prefer existing project vocabulary for capabilities and Authorities.
11. Reuse a starter profile only as a checklist; adapt it to the actual repository.
12. Evaluate every applicable derived profile/check against the current Core/project graph and inspect the resulting frontier. Do not report the selected scope COMPLETE while an accepted project-owned completeness/coverage policy remains incomplete.
13. If implementation later exposes a semantic capability that was genuinely required for the selected scope but absent from the profile, add that expectation after the gap is understood. Do not rely only on the historical Question: the refined profile should remember the newly demonstrated knowledge requirement.

## Review questions

Before accepting a profile, ask:

- Is the profile duplicating a canonical consumer/input or completeness/coverage contract that should remain the policy owner?
- Are there multiple accepted project-owned policy sources that all apply to the selected scope, and have they all been included/evaluated before claiming COMPLETE?
- Is a project-native NOT_APPLICABLE decision already proven by canonical evidence that should be represented as an ordinary evidence capability instead of a new Harness status?
- Does any expectation require per-subject coverage while using a broad capability shared by unrelated subject-specific providers? If so, scope the capability or use target-owned coverage evidence before trusting COMPLETE.
- Could an implementation agent satisfy every expectation and still need to invent a product/domain/architecture decision?
- Does the profile omit a verification strategy needed to know how accepted behavior will be checked?
- Is any expectation really a task, workflow state, approval or implementation step rather than engineering knowledge?
- Is a slice-specific readiness concern being incorrectly promoted to permanent project-level knowledge?
- Are prerequisites explicit enough that Harness exposes only safe `CREATE` actions?

## Important limit

Harness validates a declared profile; it does not prove the profile itself complete. Profile quality remains agent judgement during this phase of the project.
