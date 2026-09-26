---
name: test-design
description: "Use for actionable CREATE work requiring executable observable test contracts before concrete test code. Refine accepted verification obligations into preconditions, operations, oracles, invariants and properties without inventing upstream semantics or test-framework mechanics."
---

# Test Design

## Trigger

Use when actionable work has `knowledge_kind: test-design` and the project requires explicit executable test contracts before implementation/test code.

## Inputs

- actionable Test Design expectation and Authority;
- accepted Verification Design objectives/scenarios/evidence obligations;
- accepted product/domain/application/architecture/interface/data/security/quality/component knowledge needed by the selected scope;
- project engineering policy when it constrains test-first process or allowed dependency/oracle boundaries.

## Read boundary

Read canonical design and verification knowledge in prerequisite closure.

Existing production code and executable tests may describe current state, but they do not override accepted semantic owners. For greenfield/pre-code design they are not required inputs.

## Procedure

1. Confirm the expectation is actionable and prerequisites are accepted.
2. For each selected verification obligation, identify the authoritative behavior/constraint being proven.
3. Specify the minimum executable contract:
   - preconditions/state;
   - controlled operation/stimulus;
   - observable outcome/oracle;
   - invariant/state transition;
   - failure/atomicity distinction where relevant.
4. Identify forbidden/incidental oracles when direct inspection of internals would violate accepted ownership or make a non-authoritative representation semantic truth.
5. Identify property/state-machine/generated-test obligations where examples alone are weak.
6. Preserve substitutability: test consumer-owned/public contracts rather than concrete provider internals unless the verification objective specifically owns an integration boundary.
7. Trace every contract through non-empty `verification_refs` to accepted Verification Design checks; Product Requirement coverage is inherited through those checks rather than re-stating requirement text.
8. Leave framework, fixtures, helper structure, mocks and assertion syntax to test implementation unless project policy makes one architecturally significant.
9. For user-facing scopes, derive tests from accepted interface/policy obligations where applicable: state mapping, journey completion, keyboard reachability/focus restoration, status announcements, validation/error association and recovery, authorization-sensitive actions, responsive/reflow invariants and destructive-action safeguards.
10. When an upstream Screen/View contract intentionally accepts a visual reference/invariant, a visual-regression or rendered-comparison test may use that reference as an oracle only for the presentation facts explicitly constrained there. Preserve declared freedoms; do not turn incidental pixels, provider internals or unaccepted screenshot details into requirements.
11. Route any missing expected behavior to its upstream Authority instead of inventing it.
12. Produce `test-design/v1`, run `workspace.py validate-artifact`, accept/register it and reevaluate.

## Stop conditions

Stop and route a Question when:
- an expected result is not decided by accepted upstream knowledge;
- choosing an oracle would decide a new product/domain/architecture rule;
- a test requires coupling to an internal representation forbidden by accepted design;
- verification intent is too vague to determine what evidence the test must produce.

## Output schema

`test-design/v1`.

Required per test contract:
- stable test-contract `id`;
- non-empty `verification_refs`;
- `precondition`;
- controlled `operation`;
- observable `oracle`.

Additional project-native detail may elaborate invariants, failure/atomicity, properties and implementation freedoms, but must not replace the canonical trace to Verification Design.

## Acceptance checks

- every oracle is grounded in accepted semantic/design truth;
- every contract refines one or more referenced verification obligations rather than adding a requirement;
- every referenced verification id resolves;
- every Verification check with `method: TEST` has at least one Test Design contract;
- public/consumer contracts are preferred over provider internals;
- implementation mechanics remain free unless materially constrained;
- test design can survive reasonable implementation refactoring;
- unresolved semantics are routed upstream;
- visual-regression evidence is admissible only when it traces to an intentionally accepted visual invariant and compares only its declared constraints.

## Registration

Register accepted Test Design under its project Authority and capability. Dependencies should include Verification Design plus the canonical owners actually consumed.

## Human projection

Render a disposable Test Design catalogue from the canonical managed artifact.

## TDD note

If project policy selects TDD, this artifact is the semantic input to RED/GREEN/refactor. Harness does not require TDD universally.
