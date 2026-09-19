# Coding-Agent Boundary Experiment — Nutrition

Status: research evidence.

## Goal

Test the stronger claim behind Component Design: after accepted Engineering Policy + Component Design, can a coding agent implement a bounded slice without making new architecturally significant decomposition decisions?

Consumer experiment: Nutrition Management PR #22, implementing only Component Design / Implementation Plan slice 0.

## Instructions available to implementation

The implementation used the accepted project Engineering Policy and Component Design as the decision boundary. The intended work was deliberately small:

- make the Planning Snapshot dependency an explicit Purchase Planning application port;
- make the solver dependency an explicit application port;
- keep concrete SQLite/SCIP realization outside application;
- preserve existing behavior;
- add structural dependency evidence.

No new product/domain behavior was authorized.

## What implementation did not need to decide

The accepted design already answered:

- which layer owns the ports;
- which dependencies require seams;
- which concrete adapter realizes snapshot capture;
- that the solver seam must not expose SCIP types;
- that composition may coordinate concrete provider repositories;
- that domain/application remain infrastructure-free;
- that generic repositories, DI frameworks, mediators and speculative abstractions are forbidden;
- that stateless function implementations are allowed.

These are exactly the decisions that unconstrained coding agents commonly make inconsistently.

## Feedback discovered while coding

The first implementation represented the solver port as a class with `solve()` and introduced a `ScipOptimizationSolver` wrapper.

CI exposed two important facts:

1. the existing accepted/tested solver adapter is a callable function used directly by multiple behavioral tests;
2. the CLI is the composition root and therefore is legitimately allowed to select concrete infrastructure, so a blanket test forbidding CLI→infrastructure imports contradicted the accepted composition rule.

This was not a missing product/domain decision. It was an over-specific Component Design choice.

The design was repaired to state a callable `OptimizationSolver.__call__` contract and explicitly retain the existing `solve(snapshot)` adapter. The unnecessary wrapper class was removed. The over-broad structural test was removed.

This is positive feedback for the research model: Component Design must constrain **semantic responsibility and dependency ownership**, not force class-shaped implementation.

## Final implementation slice

The successful slice:

- adds typed `PlanningSnapshotSource` and callable `OptimizationSolver` Protocols to Purchase Planning application;
- types `generate_purchase_plan` against those application-owned ports;
- renames the concrete coherent-read implementation to `SqlitePlanningSnapshotSource`;
- keeps existing SCIP `solve(snapshot)` as the concrete callable adapter;
- updates composition/acceptance wiring;
- adds a structural test preventing the solver adapter from importing provider infrastructure.

Existing behavioral tests continue to prove solver/application semantics.

CI passed after the design refinement.

## Assessment

The experiment supports the hypothesis with one qualification.

**Supported:** explicit Engineering Policy + Component Design materially reduces architecturally significant freedom available to the coding agent. The bounded implementation required no new product/domain/architecture decision.

**Qualification:** code design that over-specifies representation (for example "must be a class") can itself create unnecessary churn. The correct contract is responsibility + ownership + dependency/failure semantics; class/function representation should remain free unless construction/lifetime/substitution semantics require one.

## Implication for Harness

The feedback loop should remain:

```text
accepted Component Design
        ↓
coding attempt
        ↓
implementation evidence reveals contradiction
        ↓
is upstream semantics missing?
   yes → Question to owning Authority
   no  → repair over-specific Component Design
        ↓
reevaluate / implement
```

Harness does not need an implementation-progress state to support this. Questions and canonical artifact repair remain sufficient.

## Next research

Before canonicalization:

1. update Component Design skill to explicitly prefer behavioral/ownership contracts over class mandates;
2. repeat on a different Nutrition slice involving provider persistence/application ports, where DIP/ISP pressure is stronger;
3. then test the same Engineering Policy → Component Design mechanism on NAPMS.
