# Candidate User Journey — First-MVP policy export

Status: experimental / non-canonical blind reconstruction  
Owner hypothesis: APPLICATION-DESIGN  
Provides: `napms.mvp.frontend.user-journeys`

## Actor and goal

Actor: an authenticated NAPMS user who has the instance permissions needed for the selected catalogue/policy actions and, when submitting/exporting, effective scoped authority for every relevant Resource scope.

Goal: establish an explainable desired connectivity rule from accepted semantic inputs and obtain a complete vendor-neutral policy export without losing business, permission or realization provenance.

## Preconditions

- OIDC authentication is valid.
- The user may progressively create the semantic facts required by the journey.
- Missing Resource network realization is a supported semantic state; it must remain explicit rather than being fabricated.
- Request authority and export authority are separately evaluated server-side at their respective logical times.

## Journey

1. **Describe Resources**
   - user creates source/destination Resources;
   - user creates logical Endpoints and may assign current HostAddress or Prefix realization;
   - Resource identity remains stable independently from address changes.

2. **Describe application communication**
   - user creates Application(s) and Components;
   - user defines one directed Interaction for one independently meaningful communication reason;
   - user publishes/chooses the exact immutable Interaction revision carrying complete minimal traffic semantics;
   - cross-Application interaction remains valid when semantic references are valid.

3. **Describe concrete deployment**
   - user registers source and destination ComponentDeployments binding Components to Resources;
   - deployment identity is independent from Resource address.

4. **Provide business basis**
   - user identifies a Business Process;
   - user declares a Process-backed Connectivity Need for the Interaction and dependent participant/component perspective;
   - business justification remains distinct from authorization.

5. **Submit concrete access request**
   - user selects exact source/destination ComponentDeployments, exact Interaction revision and current Need/business basis;
   - system evaluates effective `access.request` authority for all participating Resource scopes at server-owned admission time;
   - denied/unknown admission exposes no successful request mutation;
   - admitted valid submission creates the exact request subject and preserves authority/business evidence.

6. **Record permission decision**
   - an actor with accepted decision permission records Allowed or NotAllowed for the exact immutable request subject;
   - NotAllowed creates no PolicyRule;
   - Allowed resolves one stable current PolicyRule identity for that exact semantic access.

7. **Manage current access state**
   - authorized management action may switch the PolicyRule ACTIVE/INACTIVE without creating a new permission decision;
   - supported effective window may constrain contribution at evaluation time;
   - added current Needs may add justification without duplicating the Rule.

8. **Request vendor-neutral export**
   - user selects all current desired policy or an explicit Rule subset;
   - system evaluates effective `policy.export` authority for all selected Resource scopes at one database-owned evaluation time;
   - selected effective Rules are materialized using one coherent snapshot.

9. **Observe export outcome**
   - COMPLETE: self-contained normalized rows plus authorization/business/source provenance are available;
   - UNRESOLVED: selected effective access lacks required technical realization and is not presented as partial success;
   - non-effective Rules contribute no rows and missing realization for them does not make the export incomplete.

## Alternate / failure paths

- authentication cannot establish trusted identity -> no protected journey action;
- instance permission missing -> relevant protected operation unavailable/rejected;
- scoped request authority denied/unknown -> request is not accepted;
- validation/reference mismatch -> user remains in the task with accepted rejection details;
- permission decision NotAllowed -> journey terminates without authoritative PolicyRule;
- Rule is INACTIVE or outside effective window -> it remains inspectable but contributes no export row;
- scoped export authority denied/unknown -> no protected policy result is disclosed;
- required effective realization missing -> export outcome is UNRESOLVED, not COMPLETE;
- security dependency unavailable -> operation fails as dependency-unavailable rather than false denial/success.

## Completion

The journey completes when the user can observe either:
- a COMPLETE vendor-neutral export traceable to the exact accepted Rule(s), authority, business basis, source realization and evaluation time; or
- an explicit accepted non-success outcome (NotAllowed, denied, unresolved, unavailable) without fabricated policy truth.

## Interface-design freedoms intentionally left open

- number of screens;
- route structure;
- modal/drawer/page choices;
- navigation labels and grouping, while preserving domain language;
- visual hierarchy and layout;
- component framework;
- client state management.
