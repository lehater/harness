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

## Read boundary

Read accepted project architecture/requirements and organizational constraints necessary to determine which engineering obligations are actually normative. Existing code and methodology references are evidence/guidance, not independent policy owners.

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

## Stop conditions

Stop when a proposed obligation would decide missing product/domain/architecture semantics, when applicability cannot be justified from accepted project context, or when named principles conflict without an accepted project priority.

## Output contract

Produce a project-native engineering policy stating selected obligations, forbidden dependencies/patterns, explicit non-rules, applicability and downstream consumers.

## Acceptance checks

- every normative principle is expressed as reviewable project obligation;
- no methodology acronym is treated as self-interpreting acceptance evidence;
- optional patterns are conditioned on demonstrated need;
- project semantics remain owned by their existing Authorities;
- policy is usable by component/implementation review without evaluator-specific logic.

## Registration

Register the accepted engineering-policy artifact under its owning Authority and make it a Capability prerequisite only for producers/consumers that actually need it.

## Human projection

Prefer a concise project-native policy whose obligations and non-rules are directly reviewable by design and implementation agents.
