# Runtime / Operational Design Research

Status: experimental research result; not canonicalized.
Baseline: Harness main `fde7658d2b4d332e9b4344f47d5de5a857e1eeff`.
Pilot: Nutrition Management pre-code design only; implementation code was not used as design evidence.

## Research question

Which runtime/operational decisions must be accepted before a coding agent can implement a system without inventing architecturally or semantically significant behavior?

The initial labels logging, error handling, configuration and observability are not atomic ownership boundaries. They mix product semantics, architecture/runtime policy, external interface contracts, security/privacy, quality objectives, operational evidence and implementation mechanics.

## Decision classes and ownership

| Decision class | Natural owner | Examples |
| --- | --- | --- |
| Product/domain semantics | Product / Domain / Application | domain outcome vs failure; infeasible vs partial; semantic time inputs |
| Runtime topology and control policy | System Architecture, Application Design, Quality Design as applicable | process topology; sync/async/background work; transaction lifetime; timeout/cancellation/retry semantics when architecture-significant; graceful degradation |
| External failure/configuration contract | Interface Design | required CLI/API inputs; HTTP/process result classes; stable external error representation |
| Cross-cutting normative constraints | Engineering Policy | fail-fast obligation; no hidden global/default state; general cleanup/retry discipline selected by the project |
| Security/privacy/audit requirements | Security Design / Analysis | secret handling; PII redaction; security/audit events; tamper/access requirements |
| Reliability objectives | Quality Design / Product Requirements | SLI/SLO targets, availability/latency objectives, degradation tolerance |
| Runtime evidence contract | Operability Design | correlation; diagnostic event taxonomy; required runtime distinctions; dependency visibility; health/readiness evidence when applicable |
| Executable evidence | Verification / Test Design | scenarios proving correlation, redaction, failure distinctions, lifecycle/resource behavior |
| Concrete realization | Implementation Design / coding | library, formatter, exception classes, context propagation mechanism, SDK, exact private metric/span names |

## Why Logging / Error / Configuration / Observability are not Authorities

### Logging

Logging is a realization channel. The design-owned knowledge is the event/evidence semantics: what must be distinguishable, correlated and safe to expose. Structured schema stability may be part of the operability contract; a logging library or formatter is implementation freedom.

### Error handling

Failure knowledge is distributed by semantic ownership. Domain outcomes belong to domain/application design; external failure representation belongs to interface design; retry/timeout/degradation policy belongs to architecture/application/quality depending on scope; diagnostic visibility belongs to operability; exception classes and translation code are implementation mechanics.

### Configuration

Configuration is not one coherent decision class. Product-semantic inputs belong to product/interface/application contracts. Deployment/runtime topology and mutability belong to architecture. Secret sources belong to security. Cross-cutting rules such as no hidden defaults may be Engineering Policy. Reading an environment variable or config file is mechanics after the accepted source/precedence contract exists.

A separate Configuration Authority is justified only if a project has an independently changing public configuration model with its own consumers—for example a large platform configuration surface, dynamic control plane or policy distribution system. Nutrition does not.

### Observability

Observability is closest to an atomic residual boundary, but the Authority should own **runtime evidence and diagnosability requirements**, not telemetry products. Logs, metrics and traces are signal projections. Health/readiness, correlation, diagnostic categories and dependency evidence belong here when they have operational consumers.

## Atomicity result: OPERABILITY-DESIGN

### Semantic cohesion

The coherent knowledge is: what evidence a running system must expose so operators/developers can determine what operation occurred, what boundary failed, whether accepted semantic distinctions were preserved, and whether the runtime is able to serve its accepted purpose.

### Independent change

Evidence shape, correlation and health/diagnostic requirements can change without reallocating product/domain/interface semantics and without selecting a concrete logging/telemetry library.

### Public producer/consumer contract

Inputs are accepted product/domain/application/interface/architecture/security/quality decisions. Output is a runtime-evidence contract consumed by Component Design, Verification/Test Design, Implementation Design and ultimately IMPLEMENTATION.

Result: the existing conditional `OPERABILITY-DESIGN` candidate is justified, but its boundary should stay narrow. It must not become a bucket for all runtime concerns.

## Capability model

A project may instantiate one or more capabilities under OPERABILITY-DESIGN when independently useful. The first proven capability shape is:

`<project>.operability` — accepted runtime evidence/diagnosability contract.

Typical prerequisites are the project's architecture, application behavior, external interface, applicable security/privacy truth, applicable quality objectives and selected Engineering Policy. Exact prerequisites remain project-specific.

Typical consumers are Component Design (when diagnostic context changes public component responsibilities), Verification Design, Test Design, Implementation Design and IMPLEMENTATION.

No new Core entity is required. Ordinary Authority, Capability, prerequisite closure, CanonicalArtifact and Question semantics are sufficient.

## Questions that block IMPLEMENTATION

A Question is blocking when a coding agent would otherwise have to choose a material semantic/runtime contract, for example:

- whether two accepted outcomes/failures must remain externally or diagnostically distinguishable;
- whether an operation is retryable/idempotent and what retry changes semantically;
- whether timeout/cancellation/degradation can produce an accepted result;
- which configuration source wins when multiple accepted sources exist;
- whether configuration is startup-immutable or runtime-mutable when behavior depends on it;
- what sensitive data may enter diagnostic/audit evidence;
- which runtime states define readiness/health when a long-running deployment depends on them;
- which operation/dependency identity must propagate for end-to-end diagnosis.

A Question is not required for a private exception class, logger API, formatter, local helper, context-manager syntax, or a metric/span name that has no accepted external operational consumer.

## Nutrition pilot

The accepted Nutrition baseline already fixed several upstream truths: explicit semantic dates/times, one local process, technical failure distinct from domain outcomes, solver timeout/cancellation/unknown/numeric failure distinct from hard infeasibility, deterministic CLI output, fail-fast engineering policy, and privacy constraints on diagnostics.

It still left a coding agent to invent material runtime evidence decisions: whether one invocation is correlatable end-to-end; which failure categories are observable; whether structured event semantics exist; whether persistence vs optimization failure can be located without native-object leakage; whether retries are permitted; and whether metrics/traces/health/config sources should be introduced merely as conventional defaults.

The pilot adds a research `nutrition-management.operability` capability and a pre-code Operability Design artifact. It deliberately decides that the local CLI MVP has no independent env/config-file/feature-flag/reload surface, no continuous health endpoint, no distributed tracing requirement, no SLO-derived alerting requirement and no automatic retry policy. These absences are explicit design decisions, preventing coding-agent invention.

The experiment also shows that exact non-zero CLI exit-code allocation can remain implementation freedom because the accepted interface contract only requires success vs non-success and promises no stable diagnostic text/code taxonomy.

## Standards evidence

External guidance supports the separation rather than a checklist import:

- Twelve-Factor separates deploy-varying configuration from code, treats logs as event streams and emphasizes disposable startup/shutdown behavior. Harness should capture a project's accepted semantics, not mandate Twelve-Factor mechanisms.
- OpenTelemetry defines vendor-neutral logs/metrics/traces and semantic conventions, and emphasizes correlation. This supports signal-neutral evidence semantics while leaving SDK/library choice to implementation.
- OWASP logging guidance requires consistent security/operational logging and exclusion/masking of secrets and sensitive personal data. Those constraints originate in Security/Privacy and are consumed by Operability.
- Google SRE treats SLIs/SLOs as user/service objectives and alerting as an operational consumer of those objectives. Therefore SLO targets belong upstream in Product/Quality; Operability materializes evidence needed to measure/diagnose them.
- NIST log-management guidance treats log management as an organizational/security capability. Harness should not turn those controls into universal project Authorities.

## Universal mechanics vs policy vs skill vs project artifact

**Harness Core:** no change. Capability closure and Questions already express missing runtime knowledge.

**Reference Authority catalog:** retain conditional OPERABILITY-DESIGN, refine its responsibility to runtime evidence/diagnosability and explicitly route configuration/failure/reliability/security semantics to their owners.

**Engineering Policy:** project-selected cross-cutting runtime rules such as fail-fast/no hidden defaults/retry discipline when normative across multiple design Authorities.

**Reusable skill:** an operability-design artifact-production skill that derives evidence requirements from accepted upstream truth and refuses to invent product/domain/interface/security/quality semantics.

**Project Capability/CanonicalArtifact:** project-specific operability contract, such as `nutrition-management.operability` backed by `docs/redesign/operability-design.md`.

## Consequences for the pre-code chain

There is no universal linear stage insertion. The graph is conditional.

For a project where operability is independently valuable, the common shape is:

`Architecture/Application/Interface/Security/Quality/Engineering Policy -> Operability Design -> Component Design and Verification/Test Design -> Implementation Design -> IMPLEMENTATION`.

Some runtime-control decisions remain direct prerequisites of Component/Implementation Design from their existing owners rather than passing through Operability.

## Core-change decision

No Harness Core change is justified by this experiment.

The problem is missing engineering knowledge, not missing graph mechanics. A new RuntimePolicy entity, Logging entity, Error entity, Configuration entity or telemetry-specific Core model would duplicate semantics already expressible as project capabilities and prerequisites.

## Remaining evidence needed before canonicalization

Nutrition is one local synchronous CLI shape. Before changing the reference catalog from experimental to stronger canonical status, validate the refined boundary on a materially different runtime shape: long-running service, background worker or distributed request path. NAPMS is not required yet; another suitable project can provide that evidence.

The Nutrition result is sufficient to keep the work on a research branch and to create a reusable candidate skill, but not sufficient to make broad runtime-control claims universal.
