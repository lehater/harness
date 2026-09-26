---
name: visual-composition-design
description: "Use when accepted Screen/View semantics need an independent visual realization contract for spatial composition, visual hierarchy and appearance before frontend implementation."
---

# Visual Composition Design

## Trigger

Use when a user-facing implementation has accepted Screen/View semantics but the final visual arrangement or appearance would otherwise be re-invented by the coding agent.

Owner: HUMAN-INTERFACE-DESIGN.

## Responsibility

Define the visual realization of accepted Screen/View semantics: where accepted regions/actions appear, their relative visual weight, alignment, sizing, density, spacing, typography, surfaces and other appearance decisions needed to reproduce an accepted design.

This knowledge kind does not own user tasks, actions, navigation, data semantics, state semantics, component architecture or provider mechanics.

## Inputs

- accepted Screen/View Design;
- accepted Presentation System;
- accepted visual references, sketches, screenshots, prototypes or design-tool frames when they carry intentional visual decisions;
- applicable accessibility/responsive/quality constraints.

Frontend System Architecture is not an input unless a project can demonstrate a specific visual decision that genuinely depends on it.

## Read boundary

Read accepted Screen/View semantics and Presentation System first. Visual references are evidence for visual composition only. Existing component code, framework structure, provider defaults and CSS are implementation context, not visual authority.

Do not infer or add actions, data, permissions, navigation or screen states from a sketch.

## Procedure

1. Select one accepted Screen/View subject.
2. Enumerate the accepted regions/actions/states that must be visually realized.
3. Record a stable visual reference when one exists and state exactly which visual facts it constrains.
4. Define wide/default composition: region placement, grouping, alignment, order, relative visual weight and major sizing/proportion rules.
5. Define appearance: density, spacing rhythm, typography roles, color/surface treatment, borders/elevation and action emphasis where not inherited fully from the Presentation System.
6. Define responsive visual transformations without changing accepted Screen/View semantics.
7. Separate material visual invariants from controlled freedoms and ordinary implementation details.
8. Ensure every visual element maps to accepted Screen/View semantics; visual composition may arrange accepted capabilities but cannot create new ones.
9. Define rendered-conformance obligations sufficient to compare implementation with the accepted visual composition.
10. Route unresolved semantic questions to their owning upstream Authority instead of solving them visually.
11. Produce the project-native canonical Visual Composition contract, accept/register and reevaluate.

## Stop conditions

Stop and route a Question when the desired composition would require inventing a new action, state, data concept, navigation target, permission or other Screen/View semantic decision.

Stop when a visual choice materially depends on an unresolved branding/accessibility/platform constraint.

## Output contract

A useful contract includes:

- id/version and Screen/View subject;
- inherited Presentation System;
- optional accepted visual reference;
- region/action placement and grouping;
- relative visual hierarchy/weight;
- sizing/proportion constraints where material;
- spacing/density and typography roles;
- color/surface/action-emphasis decisions where material;
- responsive visual transformations;
- material visual invariants;
- controlled freedoms and ordinary implementation details;
- rendered-conformance obligations;
- unresolved Questions.

## Acceptance checks

- every visual element maps to an accepted Screen/View region/action/state;
- no product or interaction capability is invented from the reference;
- the contract is sufficient for an implementer to reproduce the material composition without choosing a materially different arrangement;
- shared visual language is inherited from Presentation System rather than copied;
- exact pixels are constrained only when intentionally material;
- visual references state what they constrain and what remains free;
- frontend architecture/provider/component mechanics are not treated as visual authority;
- rendered-conformance obligations can distinguish a materially different composition from the accepted one.

## Registration

Register under HUMAN-INTERFACE-DESIGN and provide only visual-composition capabilities actually materialized. Dependencies should normally include Screen/View Design and Presentation System plus applicable visual quality/accessibility constraints, not Frontend System Architecture.

## Human projection

Accepted mockups, annotated screenshots, Figma frames, Storybook stories or rendered comparison sheets may project this contract. A projection is canonical only to the extent the project explicitly assigns it contract meaning.
