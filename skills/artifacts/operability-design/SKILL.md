# Operability Design

Status: experimental reusable artifact-production skill.

## Purpose

Produce the smallest project-specific runtime evidence and diagnosability contract needed before implementation. Derive it from accepted upstream engineering truth; do not turn logging, errors, configuration or observability checklists into new semantics.

## Inputs

Use accepted product/domain/application behavior, system architecture, external interfaces, applicable quality/security decisions, Engineering Policy and any existing runtime/deployment contract.

Do not use current implementation code, logger configuration, exception classes, metrics or deployment scripts as design truth unless the project explicitly declares them canonical inputs.

## Method

1. Enumerate runtime distinctions a coding agent must preserve: accepted outcomes vs failures, dependency failures, timeout/cancellation, lifecycle states and operationally relevant degradation.
2. Identify the owning upstream Authority for each semantic decision. Route gaps upstream instead of deciding them here.
3. Define the minimum runtime evidence required to diagnose those accepted distinctions: correlation identity, event/failure categories, safe diagnostic context, dependency identity and health/readiness evidence when applicable.
4. Apply security/privacy constraints to diagnostic and audit evidence.
5. Include SLI/SLO-derived evidence only when an accepted Product/Quality objective creates the need.
6. Decide explicitly whether configuration sources, runtime reload, feature flags, retries/backoff, background work, health endpoints, metrics and traces are applicable. Absence may be a valid project decision.
7. Separate semantic evidence contracts from implementation mechanics.
8. State implementation freedoms.
9. Derive Verification/Test Design obligations.
10. Register the accepted project artifact as an ordinary CanonicalArtifact providing the project operability capability.

## Stop conditions

Create or preserve a Core Question instead of inventing an answer when:

- required failure/outcome distinctions are missing upstream;
- retryability/idempotency is semantically ambiguous;
- timeout/cancellation/degradation outcome semantics are unspecified;
- configuration precedence or mutability affects behavior but is undecided;
- sensitive-data/audit policy is missing;
- readiness/health meaning is required by deployment but not defined;
- an SLI/SLO target is needed but no Product/Quality owner has accepted it.

## Implementation freedom

Do not fix logging libraries, telemetry SDKs, formatter syntax, private exception classes, context-propagation APIs, helper structure or private metric/span names unless an accepted external operational contract requires them.

## Output contract

The artifact must state responsibility/boundary, upstream ownership retained, runtime evidence/event semantics, correlation, failure diagnostics, sensitive-data rules, applicable lifecycle/configuration/resilience decisions, implementation freedoms, verification obligations and unresolved Questions.
