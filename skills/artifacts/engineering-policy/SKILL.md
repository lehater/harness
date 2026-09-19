---
name: engineering-policy
description: "Use for actionable CREATE work that makes selected engineering principles or architecture/code-design discipline normative for a project. Translate named principles into concrete reviewable obligations without turning methodology into universal Harness semantics."
---

# Engineering Policy

## Trigger

Use when actionable work has `knowledge_kind: engineering-policy` and the project needs accepted cross-cutting design constraints.

## Inputs

- accepted project requirements and architecture relevant to the policy;
- organizational/technology constraints that are actually normative;
- applicable security, quality, interface and data decisions;
- named engineering principles/methods selected by the project.

## Procedure

1. Separate universal Harness invariants from project engineering policy and from artifact-production methods.
2. Select only principles applicable to this project/scope.
3. Translate every selected principle into observable obligations or forbidden dependencies. Do not accept acronym/name-only policy.
4. Resolve overlaps and conflicts. For example, use YAGNI/KISS to prevent speculative abstractions while applying DIP/ISP.
5. State explicit non-rules so optional patterns are not inferred as mandatory (for example CQRS, HATEOAS, event bus, generic repositories).
6. Keep obligations language/framework independent unless the project has already selected that technology.
7. Identify downstream design capabilities that must consume the policy.
8. Route any missing product/domain/architecture decision to its owning Authority rather than deciding it here.
9. Produce project-native policy, semantically accept/register and reevaluate.

## Acceptance checks

- every normative principle is expressed as reviewable project obligation;
- no methodology acronym is treated as self-interpreting acceptance evidence;
- optional patterns are conditioned on demonstrated need;
- project semantics remain owned by their existing Authorities;
- policy is usable by component/implementation review without evaluator-specific logic.

## Output

Prefer a project-native engineering policy artifact. Register it as a Capability prerequisite only for producers/consumers that actually need it.
