# Software Authority Reference Catalog v0

Status: experimental.

The catalog is a reference vocabulary for building an Engineering Graph. It is not a mandatory stage list.

## What is standardized

Every project uses the same definition of an Authority:

> one atomic boundary of engineering decision ownership with semantic cohesion, independent change and a public producer/consumer contract.

The reference catalog supplies proven software-product boundary candidates. Projects instantiate the applicable boundaries and attach project-specific production contracts.

## What is not standardized

The catalog does not require every project to have every Authority.

A small product may legitimately use:

```text
DISCOVERY
PRODUCT-REQUIREMENTS
SYSTEM-ARCHITECTURE
IMPLEMENTATION-DESIGN
VERIFICATION-DESIGN
```

A domain-heavy product may additionally need strategic/tactical domain design, application composition, interface, data, quality, security and operability Authorities. A project that needs explicit cross-cutting design discipline, coding-agent structural constraints, or independently valuable executable pre-code test contracts may also instantiate ENGINEERING-POLICY, COMPONENT-DESIGN and TEST-DESIGN.

Omitting a reference Authority is valid only when its decisions are absent or are coherently owned inside another atomic boundary. A merge is not valid merely to make the graph smaller.

## Atomicity review

For every instantiated Authority, answer:

1. **Semantic cohesion** — do the owned decisions form one coherent kind of engineering knowledge?
2. **Independent change** — can this knowledge change without forcing the neighboring Authority to re-own the same decision?
3. **Public contract** — can upstream inputs and downstream outputs be stated without exposing private internal models?

Failure of one of these questions is evidence to split, merge or reroute the boundary.

## Baseline versus conditional

The v0 catalog marks five boundaries as broadly baseline for software-product work:

- DISCOVERY;
- PRODUCT-REQUIREMENTS;
- SYSTEM-ARCHITECTURE;
- IMPLEMENTATION-DESIGN;
- VERIFICATION-DESIGN.

"Baseline" means they represent distinct responsibilities in the reference model, not that every repository must create five documents.

Conditional boundaries appear only when the corresponding engineering decision class exists independently.

## Relationship to production contracts

The catalog defines **who may own a kind of decision**.

The Engineering Graph defines **which concrete CapabilityIds that Authority produces in this project and what each production requires**.

Therefore the catalog never contains project CapabilityIds.

## Evidence

The catalog is distilled from:

- the NAPMS Authority model and its atomicity metadata;
- Nutrition Management, which demonstrated that several related outputs may remain under one Authority while having different per-capability prerequisites;
- legacy Harness methodology, which independently separates problem evidence, product requirements, domain semantics, architecture, implementation readiness and verification responsibilities.

It remains experimental until exercised by the greenfield pilot and at least one additional project shape that is materially simpler than NAPMS.


## Engineering policy and component design

Two conditional boundaries are supported when implementation agents need stronger constraints than architecture/application knowledge alone provides.

`ENGINEERING-POLICY` owns project-selected normative engineering obligations. It is not a universal SOLID/Clean Architecture checklist. Reusable principles and production methods belong in skills; the project policy selects which obligations are actually normative and translates names such as DIP, ISP, KISS or CQS into reviewable project constraints.

`COMPONENT-DESIGN` owns implementation-facing responsibility, contract ownership, dependency direction, composition and representation-mapping boundaries. It should constrain architecturally significant code decisions while deliberately leaving private helpers, local algorithms and class/function representation free unless those choices carry accepted semantics.

A project may omit either boundary when the same knowledge is coherently owned elsewhere. For implementation consumers intended to hand work to coding agents with little structural freedom, requiring an applicable component-design capability is recommended.

### Evidence

Nutrition Management demonstrated both a solver boundary and persistence boundary. The experiments showed that semantic contracts should not force unnecessary wrapper classes and that consumer-shaped ports can satisfy DIP/ISP without generic repositories.

NAPMS demonstrated the same pattern in a materially different modular application and project-owned graph/projection. Its engineering policy and component design were representable through ordinary Authority/Capability prerequisites without evaluator-specific logic.

The evidence does not justify a new universal DesignConstraint Core entity. Existing Engineering Graph semantics already express policy availability, dependency and invalidation.


## Test design

`TEST-DESIGN` is a conditional boundary between verification intent and concrete test/code realization. It owns executable observable test contracts: preconditions, controlled operations, public or contract-level oracles, invariants/state transitions, failure and atomicity distinctions, and property/state-machine obligations where examples alone are weak.

It does not own product/domain/architecture truth and does not standardize test frameworks, fixtures, mocks, assertion syntax or file layout. When Verification Design already states executable preconditions/operations/oracles and those contracts have no independent lifecycle, Test Design may remain merged into Verification Design.

TDD is not implied. A project may select RED/GREEN/refactor or another test-first process through engineering/process policy. Writing a test first does not make that test semantic authority.

### Evidence

Nutrition Management demonstrated that a design-derived verification strategy still left material observable test contracts unspecified. Its canonicalization validation placed Test Design between Verification Design and terminal Implementation Design, and the project Harness integration evaluated the IMPLEMENTATION consumer COMPLETE with the new capability in closure.

NAPMS, which already had named Test Intent scenarios, independently showed that Test Design adds executable oracle boundaries, atomicity, identity/history preservation, provider substitutability and property/state-machine obligations rather than merely restating verification levels. Its legacy graph also exposed why migration must preserve semantic dependency direction rather than mechanically reorder mixed legacy artifacts.

No new Core entity is required; Test Design uses ordinary Authority/Capability production and prerequisite semantics.
