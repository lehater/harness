# Component Design Authority Research

Status: research candidate. Not canonical.

## Question

Can Harness drive a project beyond architecture/application design into an explicit code-design contract so that an implementation agent is constrained by Clean Architecture and SOLID-oriented component boundaries rather than being expected to invent them while coding?

Nutrition Management exposed this gap after its existing IMPLEMENTATION consumer became COMPLETE while important component decomposition remained unspecified.

## Working distinction

Architecture answers structural questions such as deployment topology, bounded-context/module ownership, dependency direction, persistence topology and major technical seams.

Application Design answers use-case orchestration and provider/application contracts.

Implementation Plan answers sequencing of coding work.

None of those necessarily answers **how one module is decomposed into implementation components**.

Component Design owns that missing knowledge:

- component/class or equivalent type responsibilities;
- public interfaces/ports and method contracts where semantically important;
- dependency direction between components;
- object/model roles and ownership;
- construction/composition relationships;
- mapping boundaries between domain, application and infrastructure representations;
- extension seams chosen to satisfy known variation;
- explicit prohibitions needed to preserve architecture;
- package/file placement when placement is part of enforceable dependency structure.

It does not own line-by-line algorithms, private helper decomposition, formatting, naming of purely local variables, or speculative abstractions for hypothetical future variation.

## Candidate Authority

```yaml
- id: COMPONENT-DESIGN
  responsibility: Own implementation-facing component decomposition and dependency contracts.
  boundary:
    semantic_cohesion: Decisions that constrain how accepted application behavior is decomposed into code components.
    independent_change: Component decomposition can change behind stable application/domain contracts without changing system architecture.
    public_contract: Produces a code-design contract sufficient for implementation without inventing structural dependencies.
  produces:
    - capability: project.component-design
      knowledge_kind: component-design
      requires:
        - capability: project.application-design
        - capability: project.data-design
        - capability: project.interface-design
        - capability: project.implementation-stack
```

The exact prerequisites are project-specific. The important hypothesis is that Component Design is a separate semantic Authority rather than extra prose inside Implementation Design.

## Clean Architecture interpretation

Clean Architecture is treated as project policy constraining Component Design, not as a universal Harness rule.

For a project choosing that policy, a valid component design should make dependency inversion reviewable:

```text
outer adapters/infrastructure
          ↓ implements
application-owned ports
          ↓ uses
application services/use cases
          ↓
domain model/policy
```

Source dependencies point inward. Framework, database, transport and solver types do not enter domain contracts. Cross-context collaboration targets provider-owned application contracts.

## SOLID interpretation

Harness should not mechanically claim that prose is "SOLID". Component Design makes the decisions inspectable.

Useful review obligations:

- SRP: each public component has one coherent reason to change;
- OCP: known variation points use a stable seam when variation is actually required;
- LSP: alternative implementations of a port preserve the same behavioral contract;
- ISP: consumers depend on the smallest provider contract they require;
- DIP: high-level policy depends on abstractions it owns or on provider-owned semantic contracts, not concrete infrastructure.

These are semantic review criteria, not additional Core states.

## Required artifact shape

A component-design artifact should normally contain:

1. component inventory grouped by architecture/module boundary;
2. responsibility of each public component;
3. public contracts and important input/output types;
4. dependency edges and ownership of every abstraction;
5. construction/composition rules;
6. representation/mapping boundaries;
7. invariants and forbidden dependencies;
8. traceability from use cases to collaborating components;
9. implementation freedoms intentionally left to the coding agent.

A class diagram is optional. The normative information is the responsibility/dependency contract, not diagram syntax.

## Granularity rule

Design enough to prevent the coding agent from making **architecturally or semantically significant decomposition decisions**.

Do not design every private class/function in advance. A proposed component belongs in the canonical artifact only when at least one is true:

- another component depends on its public contract;
- it owns a semantic or architectural responsibility;
- it isolates an accepted external technology;
- it is a known variation/substitution seam;
- its dependency direction is needed to enforce an architecture invariant;
- changing it could otherwise cause the implementation agent to reinterpret upstream design.

This avoids turning Harness into a source-code generator disguised as design.

## Relationship to IMPLEMENTATION

Candidate closure:

```text
Domain / Architecture
        ↓
Application + Data + Interface Design
        ↓
Implementation Stack
        ↓
Component Design
        ↓
Implementation Plan + Verification Design
        ↓
IMPLEMENTATION
```

Implementation Plan may depend on Component Design because slices should name accepted components rather than invent them.

Verification Design may also depend on Component Design when architecture/component boundaries require structural tests.

An IMPLEMENTATION consumer intended for agent coding should require Component Design explicitly.

## Feedback

During Component Design, missing semantic information must become a Question against the Authority that owns the missing decision. Component Design must not silently choose new product/domain behavior merely to make class decomposition convenient.

During coding, discovery that the accepted component design cannot realize upstream contracts should likewise create feedback rather than allowing structural drift.

## Research acceptance test

Use Nutrition Management as the first real consumer.

The experiment succeeds if:

- Harness exposes component design as missing after current accepted upstream knowledge;
- a component design can be produced without changing product/domain semantics;
- the design constrains Clean Architecture dependency direction and known SOLID seams;
- implementation plan/verification can be updated to reference the accepted components;
- IMPLEMENTATION becomes COMPLETE again;
- the resulting artifact is concrete enough that a coding agent need not choose major classes/ports/dependency relationships;
- the artifact does not prescribe trivial private implementation details.

If Nutrition requires project-specific changes inside Harness evaluator semantics, the hypothesis fails.

## Open question

One project is insufficient to make COMPONENT-DESIGN part of the canonical reference catalog. After Nutrition, test at least one structurally different project (NAPMS is a candidate). The Authority should be canonicalized only if the same semantic boundary survives both without project-specific evaluator behavior.
