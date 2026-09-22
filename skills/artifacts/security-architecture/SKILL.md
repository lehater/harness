---
name: security-architecture
description: "Use for actionable CREATE work that defines project-specific security trust, identity, admission, protection and enforcement structure before implementation without taking ownership of product/domain entitlement or downstream representation."
---

# Security Architecture

## Trigger

Use when actionable work has `knowledge_kind: security-architecture` or accepted runtime/interface/data boundaries require an independently valuable security trust/protection/enforcement contract.

## Inputs

- accepted product/domain entitlement and protected-action semantics;
- system/runtime/deployment architecture;
- interface trust boundaries;
- data sensitivity/protection constraints;
- applicable organizational security/engineering policy;
- open Questions from Security Analysis.

## Read boundary

Use accepted design as truth. Do not infer requirements from current authentication middleware, password/session code, deployment secrets, framework defaults or existing implementation.

## Procedure

1. Identify security-relevant trust boundaries and assets/credentials crossing them.
2. Preserve upstream ownership: business entitlement remains Product/Domain; external representation remains Interface; physical storage remains Data.
3. Define trusted identity sources and caller-vs-server ownership of security-critical facts.
4. Define admission/enforcement placement and fail-open/fail-closed behavior where applicable.
5. Define applicable credential/session validity, rotation/invalidation and protection requirements.
6. When an authenticated browser/client consumes a protected API, explicitly define credential acquisition, runtime/storage location, expiry/renewal behavior, logout/invalidation and recovery after credential rejection; if authenticated browser identity is not applicable, state that explicitly with rationale.
7. Define protection requirements for secrets, sensitive data, transport and cryptographic/key boundaries only where an accepted threat/deployment need exists.
8. Route configuration source/topology to System/Deployment while retaining security lifecycle/protection constraints.
9. State NOT_APPLICABLE decisions explicitly; do not manufacture authentication, encryption or secret infrastructure.
10. State implementation freedoms and downstream consumers.
11. Produce/register the smallest project-native artifact and route remaining gaps as Questions.

## Stop conditions

Stop when entitlement semantics are missing; trusted identity source is unresolved; admission can fail open ambiguously; required credential/session lifecycle is undefined; browser/request trust is unresolved; secret/protected-transport/key ownership is required but undefined; or resolving the issue would require inventing Product/Domain/Interface/Data semantics.

## Output contract

Produce a project-native security architecture contract covering applicable trust boundaries, trusted identity, admission/enforcement, credential/session protection, sensitive/secret/transport protection requirements, fail behavior, applicability decisions, implementation freedoms, downstream obligations and unresolved Questions.

## Acceptance checks

- no business entitlement is invented;
- no interface/data/operability representation is re-owned;
- every security control requirement has an accepted threat/trust rationale;
- NOT_APPLICABLE is allowed and justified;
- framework defaults are not treated as accepted security decisions;
- authenticated browser/client identity, when applicable, has explicit acquisition, storage/runtime lifetime, expiry/renewal, logout/invalidation and rejection-recovery semantics;
- coding can proceed without inventing trust, identity, admission or credential/protection semantics.

## Registration

Register under SECURITY-ARCHITECTURE only when the project has an independently valuable contract. Otherwise keep simple security structure in SYSTEM-ARCHITECTURE and let SECURITY-ANALYSIS evaluate coverage.

## Human projection

Prefer a concise trust/protection/enforcement contract, not a generic security checklist.
