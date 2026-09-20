# Candidate Frontend Architecture — blocked by security question

Status: experimental / non-canonical / BLOCKED  
Owner hypothesis: SYSTEM-ARCHITECTURE  
Target capability: `napms.mvp.frontend.architecture`

## Accepted structural inputs

- NAPMS has a separate browser Web Application container.
- Browser consumes one backend HTTPS/JSON application API.
- Backend remains authoritative for product/domain validation and protected admission.
- Human-interface semantics are supplied by the blind candidate Human Interface Design.
- OIDC bearer JWT is the backend authentication contract.
- Trusted actor/authority fields never come from form/query/user-authored headers.

## Architecture that can already be decided

### Runtime boundary

- one browser application;
- one backend API boundary;
- no browser persistence or client state becomes authoritative domain truth;
- frontend models user-visible task/view state, not duplicate domain ownership.

### Dependency direction

```
UI views / interaction components
            |
        feature/application UI controllers
            |
      frontend-owned API ports
            |
        HTTP API adapter
            |
        NAPMS backend
```

Feature UI consumes frontend-owned semantic API adapters rather than raw transport status codes.

### State ownership

- server/domain truth is re-read/reconciled from backend after authoritative mutations;
- form/edit state is local to the task unless cross-view continuity requires a scoped owner;
- navigation selection/context is interface state;
- cached server data is disposable realization state and never new domain truth;
- request admission, permission decision, Rule state and export outcome remain separate state concepts.

### Error mapping

HTTP/transport outcomes are mapped at the API adapter boundary into semantic frontend outcomes such as:
- authentication-required/invalid;
- admission-denied;
- validation-rejected;
- stale/conflict;
- dependency-unavailable;
- unresolved application result;
- unexpected operational failure.

Views do not interpret raw status codes as product semantics.

### Feature boundaries

At minimum:
- Resource Catalogue UI;
- Application Communication/Deployment UI;
- Business Connectivity UI;
- Access Request/Decision UI;
- Current Access UI;
- Policy Export UI;
- shared shell/navigation;
- shared interaction primitives only for presentation semantics with no domain ownership.

Cross-feature collaboration uses stable semantic references or shared application-level contracts; feature internals are not imported as an integration mechanism.

## Blocking security question

The accepted upstream security contract specifies backend validation of OIDC bearer JWT but does not establish the browser-side authentication/session contract needed to implement the Web Application:

- authorization-code/PKCE or another supported browser acquisition flow;
- identity-provider redirect/callback responsibility;
- access-token lifetime/refresh/re-authentication behavior;
- browser credential storage boundary;
- logout/invalidation behavior;
- whether a backend-for-frontend/session-cookie pattern is intentionally excluded.

Choosing these in frontend architecture would create a security trust/credential-lifecycle decision.

Therefore this candidate cannot be accepted as an unblocked frontend-architecture provider.

Required routing:

- addressed Authority: SECURITY-ARCHITECTURE;
- affected existing artifact: NAPMS MVP Security Architecture;
- downstream capability to block: `napms.mvp.frontend.architecture`;
- after canonical security repair, reevaluate this architecture and all downstream Component/Test/Implementation capabilities.

## Intentionally free after resolution

- React/Vue/Svelte or equivalent;
- concrete router/state/query libraries;
- file naming;
- CSS implementation;
- private hooks/helpers;
- exact cache library mechanics, provided accepted freshness/conflict semantics are preserved.
