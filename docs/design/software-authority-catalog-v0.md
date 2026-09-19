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

A domain-heavy product may additionally need strategic/tactical domain design, application composition, interface, data, quality, security and operability Authorities.

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
