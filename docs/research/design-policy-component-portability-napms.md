# Engineering Policy + Component Design Portability — NAPMS

Status: research evidence.

## Goal

Test whether the mechanism derived from Nutrition is project-independent:

```text
project Engineering Policy capability
        ↓
Component Design Authority/capability
        ↓
Implementation Design
        ↓
IMPLEMENTATION
```

NAPMS is deliberately different from Nutrition: it has a larger modular application, HTTP/UI/security/persistence concerns, its own canonical design graph, and a project-owned Harness projection/validator.

## Adaptation

The mechanism was introduced entirely inside NAPMS project-owned truth/projection:

- an ENGINEERING-POLICY Authority and canonical policy artifact;
- a COMPONENT-DESIGN Authority and component-design artifact;
- explicit input contracts;
- component-design prerequisite for Implementation Design and IMPLEMENTATION;
- canonical graph nodes/bindings.

No Harness evaluator code was changed.

## Policy differences

The reusable principles remain Clean Architecture/SOLID/KISS/YAGNI/SoC/CQS/DIP/ISP, but obligations are NAPMS-specific:

- cross-module consumers use provider application/module contracts, not tables/repositories;
- HTTP is an external delivery mechanism, never internal module integration;
- security admission remains at the accepted boundary;
- FastAPI/SQLAlchemy/PostgreSQL/browser representations do not leak inward;
- no internal message bus, CQRS infrastructure, generic repository or service-per-context split without accepted need.

This supports the distinction between reusable method knowledge and project-owned normative policy.

## Component Design differences

NAPMS Component Design does not copy Nutrition's classes/ports. It constrains component **families and ownership**:

- HTTP adapters;
- application command/query operations;
- module domain policy;
- use-case-shaped persistence contracts;
- provider application contracts for cross-module collaboration;
- security admission;
- policy materialization/export;
- composition root and mapping boundaries.

This is the same semantic mechanism with different project realization.

## Project-validator feedback

NAPMS's own vertical validator initially rejected:

1. a policy binding not represented in the canonical routing graph;
2. COMPONENT-DESIGN Authority without a canonical artifact;
3. ENGINEERING-POLICY as a non-root Authority without an input contract;
4. a regression test with a hard-coded set of known engineering Authorities.

Each rejection was a project integration invariant, not a need for project-specific Harness evaluator logic. The research branch was corrected by making policy/component design first-class NAPMS graph nodes/contracts and updating the project regression expectation.

After those corrections, the NAPMS design vertical passes with IMPLEMENTATION-CONSUMER satisfied.

## Portability conclusion

The core mechanism survives a materially different project:

- project owns methodology obligations as canonical knowledge;
- Engineering Graph makes that knowledge a prerequisite;
- Component Design translates accepted architecture/contracts/policy into implementation-facing boundaries;
- Implementation Design depends on Component Design;
- existing project-specific projection machinery can carry the model;
- Harness itself remains project-agnostic.

This is stronger evidence than adding a universal `constraints:` metadata field: ordinary Capability/Authority semantics already model the dependency and invalidation relationship.

## Canonicalization recommendation

Evidence from Nutrition and NAPMS now supports canonicalizing the **conceptual pattern**, with caution:

1. Add ENGINEERING-POLICY and COMPONENT-DESIGN to the Harness reference catalog, not mandatory global stages.
2. Keep Engineering Policy project-owned and optional; only selected policy obligations are normative.
3. Keep reusable principle/method knowledge in artifact skills.
4. Do not add a new DesignConstraint entity/schema in v0.
5. Do not make SOLID/Clean Architecture universal Harness invariants.
6. Component Design acceptance should focus on responsibility/ownership/dependency/contract semantics, not mandatory classes/interfaces.
7. Implementation consumers that aim for coding-agent constraint should explicitly require the relevant component-design capability.

The remaining validation before merging should be a clean review of research branches and, optionally, one NAPMS coding slice. The model-level portability question is already answered positively.
