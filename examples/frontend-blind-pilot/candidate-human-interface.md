# Candidate Human Interface Design — First-MVP policy export

Status: experimental / non-canonical blind reconstruction  
Owner hypothesis: INTERFACE-DESIGN  
Provides: `napms.mvp.frontend.human-interface`

## Design principle

Organize the UI around the user's semantic progression from description -> business basis -> request/decision -> current desired access -> export. Do not organize primary interaction around database tables or HTTP endpoints.

## Information architecture

Top-level task locations for the selected MVP scope:

1. **Resources** — Resource identity, logical Endpoints and current realization.
2. **Applications** — Applications, Components, Interactions, immutable Interaction revisions and concrete ComponentDeployments.
3. **Business Connectivity** — Business Processes and Connectivity Needs.
4. **Access Requests** — compose a concrete request and observe/record its formal permission outcome.
5. **Current Access** — inspect/manage authoritative PolicyRules and operational/effective state.
6. **Policy Export** — select current desired policy and inspect COMPLETE/UNRESOLVED materialization.

These are interface locations, not new domain owners.

## Navigation model

Primary transition graph:

```
Resources ----+
              |
Applications -+--> Business Connectivity
                       |
                       v
                 Access Request
                       |
              +--------+---------+
              |                  |
         NotAllowed            Allowed
              |                  |
          Request detail     Current Access
                                 |
                                 v
                            Policy Export
```

Cross-links preserve semantic references:
- Resource -> deployments using the Resource;
- Component/Interaction -> concrete deployments/request composition;
- Need -> related request/rule justification;
- Request -> exact subject + decision + resulting Rule when Allowed;
- Rule -> permission provenance + business justification + export inclusion state;
- Export row -> originating Rule and realization/provenance facts.

## View contracts

### Resources collection

Purpose: enter/inspect Resources needed by the selected journey.

Actions:
- create Resource;
- open Resource detail.

States:
- loading;
- loaded;
- empty;
- create-submitting;
- validation-rejected;
- unavailable/unexpected failure.

### Resource detail

Purpose: inspect stable Resource identity and manage logical Endpoints/current realization.

Shows:
- stable Resource reference;
- authority scope reference as identity/context, not an editable authorization assertion;
- Site/responsibility facts when available;
- logical Endpoints;
- current address realization or explicit unresolved/no-current-address state;
- history affordance when supported by the accepted backend surface.

Actions supported by current machine contract:
- add Endpoint;
- set/replace current Endpoint address.

Important state distinction:
- Resource exists with no current address != Resource absent.

### Applications workspace

Purpose: establish reusable communication semantics and concrete deployment references.

Subcontexts:
- Application + Components;
- directed Interactions;
- immutable Interaction revisions;
- ComponentDeployments.

Actions:
- create Application;
- add Component;
- create Interaction;
- publish exact Interaction revision;
- register ComponentDeployment.

UI must permit valid cross-Application Interaction where backend semantics permit it and must not impose a same-Application-only constraint.

### Business Connectivity workspace

Purpose: create the Process-backed business basis independently from permission.

Shows:
- Business Process identity;
- responsibility/criticality when available;
- Connectivity Needs;
- Need -> Interaction and participant/dependent perspective.

Actions:
- create Process;
- update supported criticality;
- declare Need.

Presentation rule:
Business justification must never be displayed as equivalent to security authority or permission.

### Access Request composer

Purpose: compose one exact immutable access subject and submit it.

Required inputs:
- source ComponentDeployment;
- destination ComponentDeployment;
- exact Interaction revision;
- current Need/business basis.

Before submit, show a semantic summary:
- source/destination deployment and their Resources;
- Interaction/revision traffic meaning;
- business Process/Need basis.

States:
- editing;
- validating;
- submitting;
- submitted;
- validation rejection;
- scoped authority denied;
- authentication invalid;
- dependency unavailable;
- unexpected operational failure.

Security representation:
- caller never enters trusted actor or authority evidence;
- 401/403-style machine outcomes are represented as authentication/admission outcomes without exposing protected unrelated data.

### Access Request detail / decision

Purpose: preserve distinction between proposal/request and formal permission outcome.

Shows:
- immutable request subject;
- request provenance;
- formal decision when present.

Decision action is shown only when the current authenticated principal has the relevant accepted instance permission according to available product/API capability; client visibility is convenience only and server remains authoritative.

Decision outcomes:
- NotAllowed -> explicit terminal decision; no PolicyRule link exists;
- Allowed -> resulting stable PolicyRule is linked.

States:
- pending/no formal decision recorded;
- Allowed;
- NotAllowed;
- decision submitting;
- stale/conflict rejection;
- unavailable/failure.

### Current Access

Purpose: inspect authoritative PolicyRules separately from requests/decisions.

Shows per Rule:
- stable identity;
- exact AccessSubject;
- ACTIVE/INACTIVE;
- effective window if present;
- originating permission evidence;
- current/historical business justification references.

Actions:
- toggle ACTIVE <-> INACTIVE;
- attach additional justification when supported;
- open Rule detail;
- select Rule(s) for export.

State transition:
`ACTIVE <-> INACTIVE` is an operational-state transition, not a new permission decision.

### Policy Export

Purpose: obtain a complete vendor-neutral result for all or an explicit selected Rule subset.

Input modes:
- all current desired policy;
- explicit non-empty selected Rule subset.

States:
- selection;
- materializing;
- COMPLETE;
- UNRESOLVED;
- authority denied;
- authentication invalid;
- dependency unavailable;
- unexpected failure.

COMPLETE presentation:
- one evaluation time;
- selected Rule provenance;
- normalized technical rows;
- business/authorization evidence sufficient for explanation.

UNRESOLVED presentation:
- must be visually and semantically distinct from COMPLETE;
- identifies unresolved required realization without presenting partial rows as successful complete policy.

## Global UI state rules

- loading never implies empty;
- unknown/unresolved never implies denied or absent;
- denied never implies NotAllowed business permission decision;
- request admission and permission decision remain visually distinct;
- Allowed decision and ACTIVE current Rule remain visually distinct;
- execution/provider concepts are outside selected MVP non-goals and are not introduced into this UI.

## Validation and conflict behavior

- field/reference validation keeps the user in the current task and associates accepted rejection with the relevant input/summary;
- optimistic concurrency conflict is presented as stale/conflicting state requiring refresh/retry, not as generic validation failure;
- dependency unavailable is retryable operational failure and not interpreted as authorization denial;
- unknown mutation outcome must not be displayed as confirmed success.

## Focus / keyboard baseline

For web interaction:
- all supported actions are keyboard reachable;
- visible focus is maintained;
- dialog/popover-like interaction, if chosen during implementation, must preserve predictable focus entry/return;
- validation failure moves or announces focus/context so the user can find the rejected field/summary;
- status changes such as submit completion or export resolution are exposed semantically, not only by color.

Exact widget mechanics remain downstream implementation choices constrained by accepted accessibility analysis.

## Responsive behavior

No product requirement establishes mobile-specific task semantics. The interface must preserve task/information priority under narrower layouts, but exact breakpoints and mobile navigation pattern remain implementation/design-system freedom until a supported device policy requires stronger constraints.

## Deliberately unconstrained

- exact route URLs;
- framework/router;
- component library;
- CSS/token values;
- modal vs page for create/edit where semantics remain equivalent;
- table vs cards when information/actions remain equivalent;
- client caching/state library;
- visual branding.

## Questions discovered

No blocking upstream semantic Question was required to define the selected interface contract from the allowed inputs.

Potential future product/interface decisions not required for the selected MVP:
- whether search/filter/pagination is required for large collections;
- which device classes are formally supported;
- whether destructive deletion exists (not present in selected machine contract);
- richer historical browsing beyond the current machine-interface surface.

These are not silently promoted to first-MVP requirements.
