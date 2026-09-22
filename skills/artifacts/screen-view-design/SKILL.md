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
4. bind every server-backed read/query and command to an accepted machine-interface operation id;
5. define the semantic Screen/View Model consumed by the view and map each field to read/command/local/navigation semantics;
6. define allowed user-visible capabilities and the accepted semantics backing each capability; record notable exclusions;
7. define primary/secondary/destructive actions and their placement role;
8. select reusable presentation/interaction patterns by id and explicitly bind only provider/pattern features authorized by the screen capability allowlist;
9. define local list/table/form/detail/search/filter/selection composition only when the capability is accepted upstream;
10. define state variants and map every state/error/outcome to accepted read/command/local semantics;
11. define responsive transformations by semantic effect, not CSS breakpoint mechanics;
12. define focus/read-order consequences where composition changes;
13. define contract, semantic and rendered verification obligations;
14. record local overrides only with rationale;
15. route missing upstream semantics as Questions.

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
- read/query and command operation bindings;
- semantic Screen/View Model fields and source mappings;
- allowed capabilities with semantic backing and notable exclusions;
- presentation pattern feature bindings; provider/template features are deny-by-default unless explicitly bound;
- states/variants and machine/local outcome mappings;
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
- raw transport DTO shape is not used as the screen semantic model by default;
- every enabled presentation-provider feature maps to an explicitly allowed screen capability;
- unbound template/provider features remain disabled, so a template cannot create product behavior;
- contract, semantic and rendered verification obligations are explicit;
- local deviation is explicit and justified;
- composition is concrete enough that implementation does not need to invent material hierarchy/pattern/layout decisions;
- framework/CSS implementation freedom remains.

## Registration

Register under INTERFACE-DESIGN and provide the screen/view capabilities actually materialized. Dependencies include the Human Interface contract, inherited Presentation System and upstream semantic contracts genuinely consumed.

## Human projection

Wireframes, navigation maps, responsive previews, Figma frames and developer handoff documents may be generated from the contract.
