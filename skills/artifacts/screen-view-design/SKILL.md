---
name: screen-view-design
description: "Use for implementation-independent composition of concrete screens/views after interaction semantics and a shared presentation system are known. Define regions, content hierarchy, actions, reusable patterns, variants and responsive transformations without encoding CSS/framework mechanics."
---

# Screen / View Design

## Trigger

Use when a user-facing implementation needs concrete view composition and Human Interface semantics alone would leave material UI decisions to the implementer.

Owner: INTERFACE-DESIGN.

## Responsibility

Materialize each concrete screen/view as a composition contract that inherits an application Presentation System and supplies only screen-specific structure or justified overrides.

## Inputs

- accepted Human Interface Design;
- accepted Presentation System;
- accepted journeys/tasks;
- domain/application/machine-interface contracts for displayed/edited data and actions;
- security/authorization semantics;
- applicable quality/accessibility/localization constraints.

## Read boundary

Read accepted Human Interface semantics, Presentation System, upstream data/action/security contracts and applicable quality obligations. Existing frontend code, routes, screenshots or design-tool files are not authority unless explicitly declared canonical.

## Procedure

For each required view:

1. state purpose, covered task and entry/exit context;
2. reference the inherited Presentation System;
3. define semantic regions/sections/tabs/disclosures and their hierarchy;
4. map displayed/edited data to accepted providers and, for server-backed behavior, bind reads/commands to stable machine-interface operation ids;
5. define the semantic Screen/View Model consumed by the view when transport/query shape is not itself the intended UI semantic contract;
6. define allowed user-visible capabilities and their backing read/command/navigation/local semantics; record material exclusions;
7. define primary/secondary/destructive actions and their placement role;
8. select reusable presentation/interaction patterns by id and explicitly bind provider/pattern features only when authorized by accepted screen semantics;
9. define local list/table/form/detail/search/filter/selection composition where applicable and backed upstream;
10. define state variants and map every material machine-operation outcome to a user-visible state/transition or an explicit non-applicable rationale; do not let an accepted response disappear into a generic implementation fallback;
11. when a displayed or edited value is an entity reference, define stable identity, human-readable display identity, candidate source/search semantics, dependency semantics for dependent/workflow selection, submitted stable value and owning command;
12. trace the screen to accepted user tasks and require deterministic entry/parent/direct-link semantics from the canonical navigation contract; authoring/workflow routes require explicit success and cancel transitions or justified non-applicability;
13. define responsive transformations by semantic effect, not CSS breakpoint mechanics;
14. define focus/read-order consequences where composition changes;
15. attach accepted reference/evidence anchors to the regions or states they actually constrain;
16. define verification obligations for contract/semantic/rendered realization when material;
17. classify remaining choices as controlled freedom or ordinary implementation detail;
18. record local overrides only with rationale;
19. route missing upstream semantics as Questions.

## Stop conditions

Stop and route a Question when screen purpose, required data/actions, authorization semantics, presentation inheritance, required state behavior or responsive/accessibility constraints are insufficient to choose composition without inventing product/interface meaning.

## Boundary

Canonical examples:
- "detail view has identity/context header, primary facts region, secondary history disclosure and task actions";
- "primary action belongs to the screen action region";
- "table becomes stacked records at narrow width while preserving labels/actions";
- "history remains secondary but inspectable";
- "screen uses pattern TABLE-STANDARD and inherits PRESENTATION-SYSTEM-X".

Implementation freedom examples:
- exact DOM tree;
- CSS Grid/Flexbox;
- exact coordinates;
- internal component split;
- framework-specific routing/layout primitives.

## Output contract

Machine-readable YAML/JSON is preferred when it can express:
- screen id/purpose;
- inherits;
- regions with role, priority and content/action refs;
- read/query and command operation bindings where server-backed;
- semantic Screen/View Model/source mappings when material;
- allowed capabilities with backing semantics and material exclusions;
- patterns plus material nesting/slot composition and authorized feature bindings;
- task references plus canonical navigation entry/parent/direct-link and success/cancel semantics;
- reference interaction contracts for every material displayed/selected entity reference;
- states/variants plus exhaustive material operation-outcome mappings or justified exclusions;
- responsive transformations;
- accessibility/focus semantics affected by composition;
- overrides with rationale;
- unresolved Questions.

The contract should be sufficient to generate review projections such as a screen spec, wireframe skeleton, state matrix or prototype scaffold. Generated visuals are not canonical by default.

## Acceptance checks

- every required user-facing view has a contract or explicit non-applicability;
- every screen references one Presentation System;
- repeated presentation knowledge is inherited, not copied;
- required states/actions/data are covered and trace to accepted operation/local/navigation semantics;
- enabled provider/template features do not create capabilities absent from accepted screen semantics;
- when the inherited Presentation System declares an entity-collection default, each primary entity catalogue follows that general-to-specific model or records an explicit override with rationale;
- primary entity catalogue query controls are backed by accepted read-query semantics whose fields exist in the bound machine-interface operation; client-only search/filter/sort over partial pages is not accepted;
- primary catalogue row opening resolves to a dedicated detail navigation capability by default;
- inline editing in a primary catalogue is accepted only when command-backed and explicitly authorized by a Screen/View override with rationale when the inherited Presentation System requires one;
- declared server-backed states do not reference impossible operation outcomes;
- every accepted machine-operation response has user-visible state/transition semantics or a justified explicit exclusion;
- every selection reference has an authoritative candidate source, explicit search/bounded-set semantics and submitted stable identity; dependent/workflow selections declare their dependencies rather than relying on implementation inference;
- authoring/workflow routes have deterministic parent, direct-link, success and cancel behavior;
- local deviation is explicit and justified;
- composition is concrete enough that implementation does not need to invent material hierarchy/pattern/layout decisions;
- listing a pattern id without the material screen-specific composition it requires is insufficient;
- reference-backed regions/states declare what the reference constrains and what it does not;
- framework/CSS implementation freedom remains.

## Registration

Register under INTERFACE-DESIGN and provide the screen/view capabilities actually materialized. Dependencies include the Human Interface contract, inherited Presentation System and upstream semantic contracts genuinely consumed.

## Human projection

Wireframes, navigation maps, responsive previews, Figma frames and developer handoff documents may be generated from the contract.
