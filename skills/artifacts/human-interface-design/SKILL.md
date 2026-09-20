---
name: human-interface-design
description: "Use for actionable CREATE work requiring implementation-independent human-interface semantics from accepted journeys. Define information architecture, navigation, views, UI states and transitions without choosing frontend framework/component code."
---

# Human Interface Design

## Trigger

Use when actionable work has `knowledge_kind: human-interface-design` and Interface Design must define a supported human interaction boundary.

## Inputs

- actionable grouped work and Interface Design Authority;
- accepted Product Requirements;
- accepted user-journey/application semantics;
- accepted Domain outcomes used by the interface;
- accepted Security Architecture constraints affecting visible interaction;
- accepted channel/platform constraints where already decided.

## Read boundary

Read canonical sources needed to establish user-visible interaction semantics. Existing frontend code, routes, screenshots and Figma/prototype artifacts are not authority unless the target project explicitly declares them canonical.

## Procedure

1. Enumerate user tasks/journeys covered by the interface scope.
2. Define the information architecture and conceptual navigation locations needed for those tasks.
3. Partition interaction contexts into views/screens only after task and information structure are clear.
4. For each view define purpose, visible information, available actions, entry conditions and exits.
5. Define relevant UI states including loading, loaded, empty, submitting, success, validation rejection, authorization rejection, unavailable/degraded, conflict and recoverable failure where applicable.
6. Define state transitions as `state + event -> next state + visible effect + allowed actions`.
7. Define validation, confirmation, cancellation, retry and destructive-action safeguards where accepted semantics require them.
8. Define semantic interaction patterns and focus/keyboard/input behavior where applicable.
9. Define responsive/adaptive behavior only where supported platform constraints require it.
10. Map machine/application outcomes to user-visible semantic outcomes without exposing transport codes as product meaning.
11. When spatial composition materially constrains implementation, derive a low-fidelity layout/wireframe from accepted semantics:
    - identify primary task and current context;
    - rank information/actions by task importance;
    - group semantically related information/actions;
    - distinguish persistent task-critical content from progressively disclosed secondary/history/provenance detail;
    - sketch relevant non-happy-path states, not only the loaded state;
    - ensure visual order does not contradict keyboard/focus/read order.
    Treat exact pixels, colors, typography, CSS mechanics and framework layout primitives as implementation freedom unless separately accepted.
12. Preserve implementation freedom for framework, CSS mechanics, private component structure, local state library and helper decomposition.
13. Before acceptance, apply `human-interface-quality-analysis` when the selected surface is user-facing. Treat it as a cross-Authority coverage lens: route discovered Product/Interface/Quality/Obligation/Verification gaps to their owners and do not absorb them into Interface Design.
14. Route missing product/domain/security/quality decisions upstream as Questions.
15. Produce the project-native human-interface artifact, semantically accept/register and reevaluate.

## Stop conditions

Stop when:

- an action/outcome is not decided upstream;
- authorization or disclosure semantics are insufficient;
- choosing a view/state would create new product behavior;
- responsive/accessibility constraints require a missing product/quality/obligation decision;
- backend/interface outcomes cannot be mapped without inventing semantic meaning.

## Output contract

A useful human-interface design includes:

- covered tasks/journeys;
- information architecture;
- navigation model;
- view/screen inventory and purpose;
- view states;
- state transitions;
- actions and interaction outcomes;
- validation/error/recovery representation;
- semantic interaction patterns;
- authorization-sensitive visibility/interaction behavior;
- focus/keyboard/input semantics where applicable;
- responsive/adaptive rules where applicable;
- layout/wireframe constraints when spatial composition is material;
- deliberately unconstrained implementation details;
- unresolved Questions.

## Acceptance checks

- every user-visible behavior traces to accepted upstream semantics;
- views/screens are derived from task/context cohesion rather than backend resources alone;
- relevant non-happy-path states are explicit;
- transport/framework details do not become interface semantics;
- Product/Domain/Security ownership is preserved;
- downstream frontend architecture/component/test work can proceed without inventing material user-visible behavior;
- applicable accessibility/usability coverage has been reviewed and material gaps are either accepted by their owning Authority or represented as Questions.

## Registration

Register under Interface Design and provide all grouped human-interface capabilities genuinely materialized. Dependencies include the canonical journeys and upstream semantic/security constraints actually consumed.

## Human projection

The canonical artifact may render flow/state diagrams, wireframes or prototypes, but generated visualizations are projections unless the project explicitly makes them authoritative.
