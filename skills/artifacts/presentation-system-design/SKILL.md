---
name: presentation-system-design
description: "Use for shared application-level presentation decisions that screens inherit: visual language, hierarchy, layout/density rules, reusable presentation patterns, feedback conventions, responsive defaults, accessibility defaults and design tokens where material."
---

# Presentation System Design

## Trigger

Use when a user-facing application needs reusable presentation decisions whose absence would force screen implementers to invent inconsistent UI/UX choices.

Owner: INTERFACE-DESIGN.

## Responsibility

Define the application-level presentation contract once and make screen/view contracts inherit it.

This knowledge kind is design knowledge, not a component library and not framework/CSS implementation.

## Inputs

- accepted Product Requirements and users/tasks;
- accepted user journeys;
- accepted Human Interface semantics where already available;
- channel/platform constraints;
- branding/content constraints when applicable;
- accessibility/usability obligations and Quality constraints;
- internationalization/localization constraints when applicable.

Missing upstream facts that materially affect presentation become Questions.

## Facets

Resolve only applicable facets, at the minimum depth needed to prevent material downstream invention:

- visual language and semantic emphasis;
- typography roles and hierarchy;
- color roles and non-color semantic redundancy;
- spacing/rhythm and density;
- layout/grid/container principles;
- action hierarchy and placement conventions;
- navigation presentation patterns;
- reusable task/interaction patterns such as forms, tables/lists, search/filter/sort, selection, disclosure, overlays and destructive confirmation;
- feedback/status/loading/empty/error conventions;
- responsive/adaptive composition defaults;
- accessibility defaults including focus visibility/order, target sizing and semantic status treatment;
- iconography/motion/data-visualization conventions when they carry product meaning;
- content/microcopy rules when repeated wording behavior is material;
- localization/directionality rules when applicable;
- design tokens when stable named values materially improve reuse and verification.

Do not create a token merely because a CSS value exists.

## Boundary

Canonical:
- semantic roles, reusable presentation choices, allowed variants, invariants, inheritance/default rules and justified deviations.

Implementation freedom:
- CSS Grid/Flexbox choice;
- exact DOM/helper decomposition;
- framework/library selection;
- generated class names;
- internal token serialization;
- private component implementation.

Exact pixel values are canonical only when an accepted requirement, platform convention, accessibility criterion or intentional design invariant needs them.

## Output contract

A useful contract includes:
- id/version and applicable platform/surfaces;
- presentation principles/defaults;
- reusable pattern ids and usage conditions;
- semantic token roles or constrained values when material;
- responsive/accessibility defaults;
- explicitly unconstrained details;
- deviation policy: local override requires rationale and cannot silently weaken accepted semantics/obligations;
- unresolved Questions.

## Acceptance checks

- screens can inherit common presentation knowledge without copying it;
- equivalent actions/states use equivalent patterns unless a deviation is justified;
- design-system/vendor mechanics are not mistaken for project semantics;
- accessibility/usability defaults are represented without treating a component library as proof of conformance;
- downstream screen design can choose composition without inventing the application's common visual/interaction language.

## Human projection

Style guides, token tables, Figma libraries and Storybook documentation are projections or implementation assets unless the project explicitly grants them canonical contract status.
