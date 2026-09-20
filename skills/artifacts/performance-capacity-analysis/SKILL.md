---
name: performance-capacity-analysis
description: "Use when latency, throughput, concurrency, data size, saturation, scalability, resource efficiency, operational cost or overload can materially constrain architecture or implementation."
---

# Performance Capacity Analysis

## Trigger

Use when implementation or architecture needs a performance/capacity/resource/cost decision that is not completely derivable from accepted Quality constraints.

## Inputs

Accepted Product, Application, Quality, System, Data, Operability and Verification knowledge as applicable.

## Procedure

1. Identify the journey/operation/resource and externally meaningful consequence.
2. Trace the Product/Domain basis.
3. Define metric and measurement boundary.
4. Define workload, concurrency, data size/cardinality and burst/duration assumptions.
5. Define target/statistic and resource/cost envelope where material.
6. Separate ordinary-load expectation from overload boundary.
7. Route observable rejection/queueing/degradation semantics to Product/Application.
8. Route topology, partitioning, caching, admission and scaling strategy to System.
9. Route query/data-layout concerns to Data and private efficiency choices to Implementation.
10. Classify COVERED, NOT_APPLICABLE, DEFERRED_NONBLOCKING or QUESTION.
11. Derive Verification/Test load/capacity evidence.
12. Derive Operability latency/saturation/headroom/cost evidence.
13. Reject optimizations that weaken accepted correctness/security/consistency without upstream acceptance.

## Stop conditions

Create a blocking Question if architecture/implementation would otherwise invent material:
- latency/throughput/concurrency target;
- workload/data-size envelope;
- burst/headroom expectation;
- queue/reject/drop/degrade behavior;
- resource budget;
- operational cost ceiling;
- timeout that changes product outcome;
- acceptance benchmark environment/measurement boundary.

## Output contract

For each material scenario record:
- journey/resource;
- Product basis;
- metric/target;
- workload/concurrency/data size;
- environment/measurement boundary;
- overload semantics;
- resource/cost envelope;
- owning Authorities;
- state/reopening condition;
- Questions;
- architecture/implementation freedoms;
- Verification/Test obligations;
- Operability obligations.

The analysis is not automatically a Capability.

## Registration

QUALITY-DESIGN owns the atomic measurable quality-constraint contract. Current evidence rejects separate PERFORMANCE-DESIGN, CAPACITY-DESIGN, SCALABILITY-DESIGN, RESOURCE-EFFICIENCY-DESIGN and COST-DESIGN Authorities.
