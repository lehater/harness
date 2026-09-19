---
name: security-analysis
description: "Use for actionable ANALYZE/CREATE work that evaluates accepted project design for applicable threats and control coverage, records covered/not-applicable/deferred states, and routes material security gaps without silently repairing upstream design."
---

# Security Analysis

## Trigger

Use when accepted design needs threat/control coverage before implementation or when a security review must determine whether a separate Security Architecture contract is applicable.

## Inputs

- accepted product/domain/system/security/interface/data/operability design;
- applicable Engineering/Security Policy;
- relevant external threat/control frameworks as coverage lenses;
- deployment/runtime scope.

## Read boundary

Treat accepted design as authority. Implementation code, current middleware, existing secrets and deployed controls are evidence only when explicitly accepted as canonical inputs. External checklists do not automatically create project requirements.

## Procedure

1. Enumerate trust boundaries, protected actions/data/credentials and credible abuse paths from accepted scope.
2. Use suitable threat/control frameworks to improve recall.
3. For each concern determine applicability before requiring a control.
4. Identify the Authority/artifact that owns each accepted control or missing decision.
5. Record one state: COVERED, NOT_APPLICABLE, DEFERRED_NONBLOCKING with reopening condition, or QUESTION.
6. Never silently repair a QUESTION. Route it to Product/Domain/Security Architecture/System/Interface/Data/Quality/Operability/Engineering Policy as appropriate.
7. Derive security verification obligations from accepted controls.
8. Separate project security requirements from generic secure-development policy and implementation mechanics.
9. Reevaluate implementation closure: material Questions block only dependent consumers.
10. Produce/register the smallest project-native analysis artifact.

## Stop conditions

Stop and preserve a Question whenever implementation would otherwise choose trusted identity, authorization/admission semantics, fail-open/fail-closed behavior, credential/session lifecycle, request-origin trust, required secret/transport/key protection, disclosure semantics or another security-critical upstream decision.

## Output contract

Produce threat/control/applicability coverage with scope/trust boundaries, concerns, owning controls, coverage state, deferred reopening conditions, blocking Questions, verification obligations and explicit non-requirements.

## Acceptance checks

- every required control traces to accepted scope/threat semantics;
- NOT_APPLICABLE and DEFERRED are explicit rather than omitted;
- analysis does not become a second architecture owner;
- external frameworks remain coverage lenses;
- discovered gaps are routed to their actual owners;
- security verification can be derived without implementation-structure assumptions;
- an empty Question set is justified by coverage, not asserted.

## Registration

Register under SECURITY-ANALYSIS when analysis has independent value. It may consume SECURITY-ARCHITECTURE when present, but a separate Security Architecture instance is not mandatory.

## Human projection

Prefer a concise threat/control coverage artifact organized by applicable trust boundaries and routed gaps, not a copied standards checklist.
