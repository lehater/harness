---
name: operability-design
description: "Use for actionable CREATE work that defines project-specific runtime evidence and diagnosability requirements before implementation, while routing product, failure, configuration, security and reliability semantics to their existing owners."
---

# Operability Design

## Trigger

Use when actionable work has `knowledge_kind: operability-design` and a coding agent would otherwise have to invent material runtime correlation, diagnostic evidence, health or operational-visibility behavior.

## Inputs

- accepted product/domain/application behavior;
- system architecture and runtime topology;
- external interface contracts;
- applicable quality and security/privacy decisions;
- Engineering Policy;
- accepted runtime/deployment constraints.

## Read boundary

Read only accepted upstream design needed to derive runtime evidence requirements. Do not use current implementation code, logger configuration, exception classes, metrics, deployment scripts or existing telemetry as design truth unless the project explicitly declares them canonical inputs.

## Procedure

1. Enumerate runtime distinctions implementation must preserve: accepted outcomes vs failures, dependency failures, timeout/cancellation, lifecycle states and applicable degradation.
2. Identify the owning upstream Authority for every semantic decision. Route gaps upstream rather than deciding them here.
3. Define the minimum evidence needed to diagnose accepted distinctions: correlation identity, event/failure categories, safe diagnostic context, dependency identity and health/readiness evidence when applicable.
4. Apply accepted security/privacy constraints to diagnostic and audit evidence.
5. Include SLI/SLO-derived evidence only when an accepted Product/Quality objective creates the need.
6. Decide explicitly whether configuration sources, runtime reload, feature flags, retries/backoff, background work, health endpoints, metrics and traces are applicable. Absence may be a valid project decision.
7. Separate semantic evidence contracts from implementation mechanics.
8. State implementation freedoms.
9. Derive Verification/Test Design obligations.
10. Produce the smallest project-native artifact, semantically accept/register it and reevaluate the target consumer.

## Stop conditions

Stop and create or preserve a Core `Question` when required failure/outcome distinctions are missing upstream; retryability/idempotency is semantically ambiguous; timeout/cancellation/degradation outcome semantics are unspecified; configuration precedence or mutability affects behavior but is undecided; sensitive-data/audit policy is missing; readiness/health meaning is required by deployment but undefined; or an SLI/SLO target is needed but no Product/Quality owner has accepted it.

## Output contract

Produce a project-native operability artifact stating responsibility/boundary, upstream ownership retained, runtime evidence/event semantics, correlation, failure diagnostics, sensitive-data rules, applicable lifecycle/configuration/resilience decisions, implementation freedoms, verification obligations and unresolved Questions.

## Acceptance checks

- every runtime evidence requirement traces to accepted upstream semantics or an explicit operational consumer;
- logging, metrics and traces are treated as possible signal projections rather than separate semantic owners;
- no product/domain/interface/security/quality decision is silently invented;
- configuration and retry behavior are explicit when they can change observable semantics;
- sensitive diagnostic data constraints are explicit;
- implementation libraries, formatter syntax, private exception classes and local helper mechanics remain free unless an accepted external contract requires them;
- downstream verification can prove the required runtime distinctions without depending on private implementation structure.

## Registration

Register the accepted artifact under OPERABILITY-DESIGN (or the project's coherently merged owner) as an ordinary CanonicalArtifact providing the project operability capability. Add it as a prerequisite only to component, verification/test, implementation or terminal consumers that actually need the runtime evidence contract.

## Human projection

Prefer a concise project-native runtime evidence contract organized around observable distinctions and operational consumers, not a generic logging/configuration/observability checklist.
