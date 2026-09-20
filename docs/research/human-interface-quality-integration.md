# Human Interface Quality Integration Research

Status: research result / non-canonical  
Date: 2026-09-20

## Question

Should accessibility/usability analysis become another frontend capability in the Engineering Graph?

## Result

Not by default.

The existing `human-interface-quality-analysis` is intentionally a cross-Authority analysis:

- Product owns required users/modes/scope;
- Interface owns interaction/presentation semantics;
- Quality owns measurable quality constraints;
- Obligation owns externally imposed conformance;
- Verification/Test owns evidence.

Creating a generic `frontend.interface-quality` production under one of those Authorities would either:
1. make one Authority re-own peer semantics; or
2. create a synthetic Analysis Authority without evidence that it has an independent lifecycle/public contract.

## Integration point

For user-facing surfaces, `human-interface-design` should invoke the analysis before semantic acceptance.

Flow:

```
candidate Human Interface Design
        |
human-interface-quality-analysis
        |
+-------+--------+--------+---------+
|                |        |         |
Product       Interface  Quality  Obligation
Questions / canonical repair as needed
        |
Verification/Test obligations
        |
accepted Human Interface Design
```

The analysis is therefore an acceptance/coverage procedure, not necessarily a persistent CapabilityId.

## When a persistent capability may be justified

Add an explicit capability only when a project demonstrates an independently consumed durable contract, for example:

- a regulated accessibility conformance baseline with versioned applicability;
- a project-wide human-interface quality policy consumed by several interface artifacts;
- an auditable coverage artifact required by Verification or release assurance.

In those cases, ownership must be chosen from the actual semantic source:
- external conformance/applicability -> Obligation Analysis;
- measurable project quality target -> Quality Design;
- interaction semantics -> Interface Design;
- evidence obligation -> Verification Design.

Do not invent `ACCESSIBILITY-DESIGN` or `UX-DESIGN` merely to fit the graph.

## Pilot consequence

The frontend Engineering Graph remains acyclic and unchanged.

The Human Interface artifact skill now requires quality coverage before acceptance, while discovered gaps use normal Questions/canonical repair.

This mirrors Harness's central rule: analysis may discover missing knowledge without becoming owner of the knowledge it inspects.
