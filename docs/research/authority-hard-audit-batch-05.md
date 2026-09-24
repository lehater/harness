# Authority hard audit — batch 5

## COMPONENT-DESIGN — KEEP

Decision identity: implementation-facing component responsibilities, ports/contracts, dependency ownership, composition/mapping boundaries.

Knowledge output: component decomposition and dependency contracts.

Consumers: Implementation and Verification/Test.

It is independent from System Architecture when coding would otherwise invent public component boundaries; it is N/A when architecture/application knowledge already constrains code sufficiently.

Verdict: KEEP.

## TEST-DESIGN — KEEP

Decision identity: refine accepted verification obligations into executable precondition/operation/oracle contracts where material semantics would otherwise be invented by test/code agents.

Knowledge output: executable test contract.

Consumers: test implementation and production implementation feedback/verification.

It remains distinct from Verification only when executable oracle semantics have independent pre-code value. Otherwise N/A and Verification owns sufficient evidence semantics.

Verdict: KEEP.

## IMPLEMENTATION-DESIGN — SPLIT/WATCH: transition ownership overlap must be removed

Decision identity: implementation slicing, sequencing, repository realization, toolchain/gate wiring and completion criteria.

Knowledge output: implementation plan/repository realization contract.

Consumers: implementation agents and verification/tooling execution.

Hard conflict: catalog still says IMPLEMENTATION-DESIGN owns “migration concerns”, while CHANGE-TRANSITION-DESIGN now owns material transition validity. This violates ownership encapsulation unless “migration concerns” is narrowed to realization of an accepted transition contract.

The remaining implementation-realization family is coherent. Toolchain/gate wiring may eventually split if it gains independent lifecycle/consumers, but current evidence is insufficient.

Verdict: KEEP only after removing semantic migration ownership; WATCH toolchain subfamily.

## VERIFICATION-DESIGN — KEEP

Decision identity: decide what evidence proves implementation realizes accepted engineering knowledge.

Knowledge output: verification strategy, traceability, scenarios/evidence obligations.

Consumers: Test Design, implementation gates, acceptance/closure.

It must not own product/domain semantics or executable oracle refinements that justify TEST-DESIGN. Those boundaries are expressible through accepted upstream knowledge.

Verdict: KEEP.

## Catalog-wide conclusion

Hard-audited all 20 current Authorities in five batches of four.

Canonicalization blockers:
1. STRATEGIC-DOMAIN-DESIGN — SPLIT required.
2. SYSTEM-ARCHITECTURE — concurrency/consistency split decision unresolved.
3. INTERFACE-DESIGN — machine vs human interface applicability likely non-atomic.
4. DOMAIN-USE-CASE-DESIGN — independent contract/consumer proof insufficient.
5. ENGINEERING-POLICY — generic-bucket risk insufficiently falsified.
6. IMPLEMENTATION-DESIGN — remove overlap with CHANGE-TRANSITION-DESIGN.

Authorities surviving current hard audit:
DISCOVERY, PRODUCT-REQUIREMENTS, TACTICAL-DOMAIN-DESIGN, APPLICATION-DESIGN, SECURITY-ARCHITECTURE, DATA-DESIGN, QUALITY-DESIGN, SECURITY-ANALYSIS, OBLIGATION-ANALYSIS, CHANGE-TRANSITION-DESIGN, OPERABILITY-DESIGN, COMPONENT-DESIGN, TEST-DESIGN, VERIFICATION-DESIGN.

No catalog-wide Project Authority Registry canonicalization until blockers are resolved.
