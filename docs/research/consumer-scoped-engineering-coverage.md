# Research — Consumer-scoped Engineering Coverage

Status: research only. No main/canonical changes.

## Problem

A repository can contain several independently selectable implementation targets. Activating concerns from the whole project graph causes unrelated branches to contaminate a selected target.

Example: Nutrition Management contains both backend/CLI and browser frontend design. Backend implementation readiness must not be blocked by frontend-only accessibility/security/latency concerns unless those concerns occur in the backend Consumer closure.

## Rule

Coverage scope is the recursive Engineering Graph closure of the selected Consumer.

~~~text
selected Consumer
  -> required capabilities
  -> recursive production prerequisites
  -> in-scope capabilities / Authorities / knowledge kinds
  -> concern activation
  -> semantic proof
  -> remaining work
  -> completion_ready
~~~

Signals outside that closure are invisible to both activation and coverage proof.

## Explicit project facts

Activation facts and applicability decisions may optionally declare `consumers`.

Example:

~~~yaml
- concern: quality.performance.latency
  consumers: [FRONTEND-IMPLEMENTATION]
  rationale: Interactive browser journeys make response time relevant.
~~~

This prevents a frontend-only concern from blocking the backend Consumer.

## Harness fixture result

A multi-consumer fixture contains:

- shared Product + Architecture;
- backend-only Data Design;
- frontend-only Human Interface + Security;
- separate backend/frontend Implementation Design capabilities.

Validated invariants:

- BACKEND activates persistent-data concerns but not human-interface/security concerns;
- FRONTEND activates human-interface/security concerns but not backend persistence concerns;
- shared architecture concerns occur in both;
- release/transition concerns occur in both;
- shared explicit facts occur in both;
- frontend-scoped explicit facts occur only in FRONTEND.

Coverage proof is also scoped:

- a realized backend data artifact proves `data.model` only for BACKEND;
- a realized frontend human-interface artifact proves `interface.human.accessibility` only for FRONTEND;
- neither artifact may close the same concern for the other Consumer merely because it exists elsewhere in the repository.

## Nutrition implication

For Nutrition Management:

`IMPLEMENTATION` closure contains backend/domain/application/data/CLI/component/verification knowledge but does not include the frontend human-interface or frontend-security branch.

`FRONTEND-IMPLEMENTATION` closure includes frontend journeys, human interface, frontend security, frontend architecture/component/verification/test/implementation knowledge plus their shared upstream dependencies.

Project facts were therefore scoped:

- privacy: backend + frontend;
- data governance: backend + frontend + BLS import;
- interactive latency: frontend only;
- local frontend resource efficiency: frontend only;
- local single-user identity/authorization/accountability N/A decisions: frontend only.

## False-positive removed

`frontend.application-contracts` was previously enough to trigger machine-interface concerns through a naming heuristic. This was rejected: application contracts are not necessarily external machine interfaces. Machine-interface activation now relies on `interface-contract` or explicit machine/HTTP/CLI capability signals.

## Conclusion

Engineering Coverage is not project-global by default.

The correct unit is:

~~~text
Coverage(project, consumer, scope)
~~~

Two Consumers in one repository may legitimately have different activated concerns, different remaining work and different completion state while sharing the same canonical Engineering Graph.