# Test Design Authority research

Status: research candidate.

## Research question

Should executable test contracts be owned independently from Verification Design and Implementation Design?

Evidence comes from two project experiments:

- Nutrition Management: semantic Test Design was derived without using existing code/tests as authority. It converted verification obligations into observable contracts for target derivation, evidence states, planning snapshots, optimization, persistence and CLI behavior.
- NAPMS: an already strong Test Intent still left material executable-oracle decisions unspecified. Test Design added precondition/operation/oracle boundaries, atomicity, history/identity preservation, substitute/provider expectations, forbidden product oracles and property/state-machine candidates.

## Boundary

### Verification Design

Owns **what evidence is required to prove accepted engineering knowledge**:
- verification levels;
- objectives;
- traceability;
- required evidence classes;
- acceptance/coverage obligations.

It must not invent product/domain/architecture truth.

### Test Design

Owns **the executable behavioral contract of the tests before concrete test code**:
- preconditions and controlled stimuli;
- public operation under test;
- observable oracle/outcome;
- invariants and state-transition properties;
- failure distinctions;
- atomicity/no-mutation expectations;
- generated/property/state-machine obligations when valuable;
- traceability to Verification Design and accepted semantic owners;
- forbidden/incidental oracles when they would couple tests to non-authoritative internals.

It does not own:
- production semantics;
- private implementation structure;
- test framework;
- fixture/helper layout;
- mocking library;
- exact test-file organization;
- assertion syntax.

### Test implementation

Owns concrete executable test code. It is implementation evidence, not automatically CanonicalArtifact or semantic authority.

### Implementation Design

Owns realization slicing, sequencing, migration and completion criteria. It may consume Test Design so slices preserve testability, but it must not redefine test oracles.

## Dependency direction

Recommended semantic ordering when Test Design is applicable:

```text
accepted product/domain/architecture/etc.
              |
      Verification Design
              |
          Test Design
              |
     Implementation Design
              |
      code/test realization
```

This is a dependency graph, not a mandatory waterfall. Independent design work may proceed whenever prerequisites are available.

Technology-specific test realization may be refined after Implementation Design without moving semantic test truth downstream.

## Why Test Design is not merely Verification Design

A verification obligation such as "unauthorized mutation is denied and state remains unchanged" does not fully tell a coding agent:
- which observable state is captured before/after;
- which operation boundary is authoritative;
- whether caller-provided identity is admissible;
- whether database-table inspection is an acceptable product oracle;
- what atomicity means at the public contract.

Those choices can materially change test coupling and can accidentally invent architecture. A Test Design capability can own them explicitly.

## Why it is not Implementation Design

The same behavioral test contract can survive changes in implementation slicing, file layout, concrete classes/functions, frameworks and test mechanics. It therefore passes the independent-change test.

## Applicability

TEST-DESIGN should be conditional.

Apply when:
- coding/test agents would otherwise invent material observable oracles;
- acceptance scenarios need refinement into executable contracts;
- state machines/properties/atomicity/failure distinctions are non-trivial;
- TDD or test-first realization is selected and pre-code test semantics must be explicit.

Merge into VERIFICATION-DESIGN when scenarios already state executable preconditions/operations/oracles with no independent lifecycle.

Merge into IMPLEMENTATION-DESIGN only for technically trivial test realization with no independently valuable semantic test contract.

## TDD

Harness must not make TDD universal.

TDD is a project process/policy choice. When selected, a project can require:

1. select accepted Test Design contract;
2. materialize minimum executable test;
3. establish RED for missing intended behavior;
4. implement minimum behavior;
5. GREEN;
6. refactor;
7. run applicable broader evidence;
8. route new semantic decisions upstream.

The important Harness invariant is ownership: test code cannot silently create product/domain/architecture truth.

## NAPMS ordering finding

The NAPMS portability experiment exposed a cycle because its accepted Test Intent currently depends on Implementation Readiness. This does not refute Test Design; it shows that the existing artifact combines/places verification knowledge downstream of implementation planning.

Canonical guidance should therefore define Authority responsibilities and dependency semantics, not mechanically require projects to rename/reorder legacy documents. Migration may split an existing artifact or project it into multiple capabilities.

## Core impact

No new Core entity is required. Test Design is an ordinary optional Capability/Authority with a reusable artifact skill and `knowledge_kind: test-design`.

## Research conclusion

Two materially different projects support the same independent boundary. Evidence is sufficient to propose TEST-DESIGN as a conditional reference Authority, while keeping TDD optional and project-owned.
