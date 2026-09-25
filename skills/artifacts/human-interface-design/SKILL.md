---
name: human-interface-design
description: "Use for actionable CREATE work requiring implementation-independent human-interface semantics from accepted journeys. Define information architecture, navigation, views, UI states and transitions without choosing frontend framework/component code."
---

# Human Interface Design

## Compatibility status

This broad knowledge kind is retained for existing project graphs that intentionally model conceptual structure, information architecture, interaction semantics and interface topology as one public contract.

For new or revalidated non-trivial frontend graphs, prefer the granular HUMAN-INTERFACE-DESIGN knowledge kinds:

- `conceptual-interface-model`;
- `information-architecture-design`;
- `interaction-design`;
- `interface-topology-design`.

Do not require the broad capability downstream in addition to those granular contracts merely as a synthesis layer. A project may keep a human-readable synthesis projection without registering another public CapabilityId.

Use this broad kind only when the project can justify that the bundled knowledge has no independently changing consumers/lifecycle for the selected scope.

## Trigger

Use when actionable work has `knowledge_kind: human-interface-design` and Human Interface Design must define a supported human interaction boundary.

## Inputs

- actionable grouped work and Human Interface Design Authority;
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
11. Identify where shared presentation or concrete screen composition remains materially undecided. Route reusable application-level presentation choices to `presentation-system-design` and concrete view composition to `screen-view-design`; do not silently absorb those decisions into this artifact.
12. Low-fidelity diagrams may illustrate accepted semantics, but presentation hierarchy/layout belongs to the downstream presentation/screen contracts when it is material.
13. Preserve implementation freedom for framework, CSS mechanics, private component structure, local state library and helper decomposition.
14. Before acceptance, apply `human-interface-quality-analysis` when the selected surface is user-facing. Treat it as a cross-Authority coverage lens: route discovered Product/Interface/Quality/Obligation/Verification gaps to their owners and do not absorb them into Human Interface Design.
15. Route missing product/domain/security/quality decisions upstream as Questions.
16. Produce the project-native human-interface artifact, semantically accept/register and reevaluate.

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
- deliberately unconstrained implementation details;
- unresolved Questions.

## Acceptance checks

- every user-visible behavior traces to accepted upstream semantics;
- views/screens are derived from task/context cohesion rather than backend resources alone;
- relevant non-happy-path states are explicit;
- transport/framework details do not become interface semantics;
- Product/Domain/Security ownership is preserved;
- downstream Presentation System and Screen/View Design can proceed without inventing interaction semantics;
- applicable accessibility/usability coverage has been reviewed and material gaps are either accepted by their owning Authority or represented as Questions.
- every displayed/edited domain fact maps to a current accepted provider semantic, not a superseded vocabulary;
- every server-backed user action/read model is realizable by an accepted application/machine interface contract or is blocked as a Question;
- when multiple upstream capabilities are jointly required, their compatibility is explicitly checked rather than inferred from independent existence;

## Registration

Register under HUMAN-INTERFACE-DESIGN and provide all grouped human-interface capabilities genuinely materialized. Dependencies include the canonical journeys and upstream semantic/security constraints actually consumed.

## Human projection

The canonical artifact may render flow/state diagrams, wireframes or prototypes, but generated visualizations are projections unless the project explicitly makes them authoritative.
