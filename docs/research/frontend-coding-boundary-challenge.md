# Frontend Coding-Boundary Challenge

Status: research result / non-canonical  
Date: 2026-09-20

## Purpose

Challenge the experimental frontend knowledge closure as a coding agent: identify any material decision still required after User Journey + Human Interface Design and accepted NAPMS backend/system contracts.

## P0 finding — browser authentication lifecycle is unresolved

The backend security contract defines OIDC bearer JWT validation and trust rules.

The system architecture says NAPMS has a separate browser Web Application consuming the HTTPS/JSON backend API.

Neither accepted input defines the browser credential acquisition/session lifecycle.

A frontend implementation agent would have to choose among materially different security architectures, for example direct browser OIDC Authorization Code + PKCE versus another session mediation design, and would also need to decide token storage/refresh/logout semantics.

That is not private coding freedom.

### Correct Harness behavior

Do not complete Frontend Architecture.

Create a Question addressed to SECURITY-ARCHITECTURE and block affected downstream knowledge.

Expected state:

```
Human Interface Design: SATISFIED
Security Architecture: BLOCKED by semantic gap
Frontend Architecture: WAIT
Frontend Component Design: PENDING/WAIT
Frontend Verification/Test: PENDING
Frontend Implementation Design: PENDING
FRONTEND-IMPLEMENTATION: BLOCKED
```

This is direct evidence that the existing Question mechanism handles frontend feedback exactly as it handles backend/security feedback.

## Why this matters

A naive frontend process would silently choose an OIDC library and storage convention during implementation.

Harness correctly classifies the missing fact as upstream security knowledge because it changes:
- trust boundary;
- credential exposure risk;
- lifecycle/invalidation behavior;
- browser/backend interaction.

The frontend branch therefore demonstrates not only production but also semantic feedback routing.

## Other remaining freedoms are acceptable

The challenge did not find a need to canonicalize:
- framework;
- router library;
- state/query library;
- CSS strategy;
- private component decomposition;
- exact local cache mechanics.

Those can remain implementation choices once the security lifecycle and accepted Interface/Component boundaries are resolved.

## Verdict

The frontend extension preserves the same fundamental Harness invariant as the backend path:

**implementation may choose mechanics, but must not invent upstream semantic or architecture decisions.**
