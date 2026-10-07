---
name: presentation-system-design
description: "Use for shared application-level presentation decisions that screens inherit: visual language, hierarchy, layout/density rules, reusable presentation patterns, feedback conventions, responsive defaults, accessibility defaults and design tokens where material."
---

# Presentation System Design

## Trigger

Use when a user-facing application needs reusable presentation decisions whose absence would force screen implementers to invent inconsistent UI/UX choices.

Owner: HUMAN-INTERFACE-DESIGN.

## Responsibility

Define the application-level presentation contract once and make screen/view contracts inherit it.

This knowledge kind is design knowledge, not a component library and not framework/CSS implementation.

## Inputs

- accepted Product Requirements and users/tasks;
- accepted Task Model and user journeys;
- accepted Conceptual Interface Model;
- accepted Information Architecture, Interaction Design and Interface Topology where material to shared presentation;
- channel/platform constraints;
- branding/content constraints when applicable;
- accessibility/usability obligations and Quality constraints;
- internationalization/localization constraints when applicable.

Missing upstream facts that materially affect presentation become Questions.

## Read boundary

Read accepted project requirements, tasks/journeys, conceptual/IA/interaction/topology semantics, quality/obligation constraints and existing canonical presentation contracts. Existing CSS, component code, screenshots, Figma files and vendor design-system defaults are evidence or implementation context, not authority unless explicitly declared canonical.

## Procedure

1. Identify the user-facing surfaces that share a presentation language.
2. Resolve applicable shared facets only to the depth needed by downstream screens.
3. Define semantic hierarchy, density/layout defaults, action/navigation/feedback conventions and reusable task patterns. When material, explicitly resolve the application-surface archetype (for example document/page flow, bounded application/workbench or step/task flow), viewport/container ownership, navigation persistence and page-scroll versus bounded-region overflow before downstream screens inherit the presentation contract.
4. Define typography/color/spacing/iconography roles and design tokens only when they carry stable reusable decisions.
5. Define responsive/accessibility/localization defaults where applicable.
6. Classify each consequential presentation choice as a material invariant, controlled freedom or ordinary implementation detail.
7. For each material shared presentation decision, use the reusable UI Decision Rule catalog when its predicates apply and record the decision question, accepted basis, applied rule ids, Decision Governance disposition/selection where applicable, required evaluation evidence and residual uncertainty.
8. If semantic constraints and reusable rules cannot discriminate among viable alternatives because the remaining uncertainty is user-empirical, record `EMPIRICAL_VALIDATION_REQUIRED`; do not promote an interim prototype preference into a production-authoritative default. The semantic artifact may still remain accepted for bounded prototype use.
9. For accepted visual/executable references, record their epistemic role and the specific presentation decisions they evidence; never import domain semantics from a picture or legacy implementation.
10. Define inheritance and local-deviation policy. When inheriting an external template/provider, pin its version/ref and treat its optional behavior as disabled unless explicitly authorized by accepted Screen/View semantics.
11. Preserve implementation freedom for framework, CSS mechanics and private component structure.
12. Before semantic admission, identify independently losable user-observable presentation obligations and account each in `semantic_review.independent_obligations`; do not compress separate controls/states/actions into one summary assertion when any can disappear independently.
13. Route missing upstream requirements or obligations as Questions rather than silently selecting material visual choices.
14. Produce the project-native canonical Presentation System contract, accept/register and reevaluate.

## Facets

Resolve only applicable facets, at the minimum depth needed to prevent material downstream invention:

- visual language and semantic emphasis;
- typography roles and hierarchy;
- color roles and non-color semantic redundancy;
- spacing/rhythm and density;
- application-surface archetype and viewport/container/overflow ownership when material;
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

Exact values are canonical when an accepted requirement, platform convention, accessibility criterion or intentional reference/design invariant needs them. Values that do not affect accepted presentation intent remain implementation details.

## Stop conditions

Stop and route a Question when users/tasks, platform/channel, branding/content constraints, accessibility obligations, localization requirements or other upstream facts materially affect a shared presentation decision and are unresolved.

## Output contract

A useful contract includes:
- id/version and applicable platform/surfaces;
- presentation principles/defaults;
- reusable pattern ids, anatomy/slots, states and usage conditions where those details are material;
- semantic token roles or constrained values when material;
- responsive/accessibility defaults;
- reference/evidence links with role and scope when presentation intent was reconstructed from screenshots, design files or executable UI;
- explicit material invariants, controlled freedoms and ordinary implementation details;
- material decision evidence with stable decision id/axis, question, basis refs, applied UI rule ids, disposition/selection, required evaluation levels/evidence, controlled freedom and residual uncertainty;
- deviation policy: local override requires rationale and cannot silently weaken accepted semantics/obligations;
- unresolved Questions.

## Acceptance checks

- screens can inherit common presentation knowledge without copying it;
- equivalent actions/states use equivalent patterns unless a deviation is justified;
- independently losable user-observable obligations have separate semantic accounting before downstream screens inherit the surface;
- design-system/vendor mechanics are not mistaken for project semantics;
- external template/provider features cannot silently introduce product actions, routes, states or data semantics;
- accessibility/usability defaults are represented without treating a component library as proof of conformance;
- downstream screen design can choose local composition without inventing the application's common visual/interaction language or a high-impact application-surface archetype;
- every material presentation decision is constrained by canonical knowledge or explicitly classified as controlled freedom;
- material decisions expose their evidence basis and any required empirical validation instead of hiding unresolved selection behind agent preference;
- references contribute only the presentation facts they can support and cannot silently redefine product/domain semantics.

## Registration

Register under HUMAN-INTERFACE-DESIGN and provide only the presentation-system capabilities actually materialized. Dependencies should reference the granular conceptual/IA/interaction/topology and quality/obligation inputs genuinely consumed; do not require a broad human-interface synthesis capability merely for compatibility.

## Human projection

Style guides, token tables, Figma libraries and Storybook documentation are projections or implementation assets unless the project explicitly grants them canonical contract status.
