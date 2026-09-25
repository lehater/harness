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
9. For user-facing scopes, useful selectable obligations may include task-first information architecture, explicit UI-state modeling, accepted domain language over DTO/framework terminology, recognition over recall, error prevention/recovery, consistency/continuity, progressive disclosure and an explicit accessibility baseline or conformance target. Translate only selected/applicable principles into reviewable obligations.
10. Produce project-native policy, semantically accept/register and reevaluate.

## Reusable engineering-discipline candidates

The following are reusable guidance candidates, not universal project obligations.
Select and translate only the items justified by the target project's actual
boundaries and consumers:

- prefer high cohesion and explicit ownership over shared catch-all modules;
- minimize coupling and keep dependency direction reviewable;
- prefer composition when reuse is collaboration/assembly rather than a true
  substitutable subtype relationship;
- use dependency inversion at meaningful external/replaceable boundaries rather
  than introducing abstractions around every concrete dependency;
- shape ports/contracts from consumer needs and keep them narrower than provider
  APIs when possible;
- isolate framework/vendor/transport representation at boundaries when allowing
  it inward would make replacement or semantic ownership materially harder;
- extract reuse around a stable repeated product/engineering concept, a real
  multiple-consumer need, or a meaningful substitution seam rather than
  speculative future reuse;
- keep shared libraries free of feature-owned mutable state and domain truth
  unless that ownership is explicitly accepted;
- make state ownership/lifetime explicit before promoting state into global or
  cross-feature storage;
- test public/consumer-owned contracts and observable behavior rather than
  private implementation structure by default;
- use KISS/YAGNI as counterweights to SOLID/OCP so architecture discipline does
  not become ceremonial indirection.

For frontend provider replacement, a useful project policy may require
provider-neutral product patterns and public component contracts while allowing
provider primitives locally inside the provider/presentation implementation.
Do not require one project wrapper per vendor primitive. A provider seam is
justified when vendor API leakage would become a cross-feature/public contract
or would force semantic/component changes during replacement.

## Stop conditions

Stop when a proposed obligation would decide missing product/domain/architecture semantics, when applicability cannot be justified from accepted project context, or when named principles conflict without an accepted project priority.

## Output contract

Produce a project-native engineering policy stating selected obligations, forbidden dependencies/patterns, explicit non-rules, applicability and downstream consumers.

## Acceptance checks

- every normative principle is expressed as a concrete reviewable project obligation with stated applicability/rationale;
- no methodology acronym is treated as self-interpreting acceptance evidence;
- optional patterns and abstractions are conditioned on demonstrated need rather than adopted as defaults;
- explicit non-rules prevent guidance from being interpreted as universal mandatory patterns;
- project semantics remain owned by their existing Authorities;
- policy is usable by component/implementation review without evaluator-specific logic.

## Registration

Register the accepted engineering-policy artifact under its owning Authority and make it a Capability prerequisite only for producers/consumers that actually need it.

## Human projection

Prefer a concise project-native policy whose obligations and non-rules are directly reviewable by design and implementation agents.
