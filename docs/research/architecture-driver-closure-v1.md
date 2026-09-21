# Architecture Driver Closure v1

Status: canonical v1.

## Decision

Do not add a new Authority or a generic NFR document requirement.

Before SYSTEM-ARCHITECTURE may select runtime/topology, the selected scope must have an explicit architecture-driver closure over the small baseline concern set in `spec/architecture-driver-closure/contract-v1.yaml`.

The closure is routing/adequacy knowledge, not a new owner of Product, Quality, Security, Operability or Domain semantics.

## Rule

For every baseline concern, the project records one of:

- `RESOLVED`: a concrete accepted decision/value with canonical source reference;
- `NOT_APPLICABLE`: explicit rationale;
- `DEFERRED`: only when the unknown has no material effect on the current architecture;
- `QUESTION`: unresolved material input; architecture is blocked.

Silence is not `NOT_APPLICABLE`.

## Architecture selection

After closure, SYSTEM-ARCHITECTURE:

1. derives architectural drivers from accepted upstream knowledge;
2. selects the smallest structural/runtime model satisfying all material drivers;
3. records why material complexity is necessary;
4. compares materially different alternatives only when risk/ambiguity justifies it;
5. records reopening conditions for assumptions that can invalidate topology.

A script, service, modular monolith or distributed topology is therefore an architectural conclusion, not an implementation default.

## Interaction with existing Harness mechanisms

- Engineering Coverage discovers whether architecture-relevant subjects/concerns require decisions.
- Questions carry unresolved upstream semantics.
- Architecture Driver Closure is the precondition proving the inputs are explicit enough to select topology.
- SYSTEM-ARCHITECTURE owns the actual structural/runtime decision.
- Verification/Test prove accepted quality/architecture constraints downstream.
- No new Core entity, workflow state or Authority is introduced.

## Anti-overengineering invariant

An architectural element that materially increases runtime, deployment, coordination or operational complexity must trace to an accepted driver, constraint or material risk.

Absence of a driver does not mechanically ban a technology, but semantic acceptance must reject unexplained complexity when a materially simpler candidate satisfies the same accepted drivers.

## User questions

The agent must not present a universal NFR questionnaire. It should derive what is already known and ask only unresolved facts whose plausible answers could materially change the architecture.

Examples include execution mode, external consumers, load/concurrency, freshness/latency, availability/recovery, growth horizon, deployment constraints, persistence/history and trust boundaries.

## Pilot expectation

A simple daily ETL with one local operator, bounded input, no continuous availability, no concurrency and no history may close to a single-process batch/CLI topology.

If a material growth, availability or interaction expectation is unknown, closure must block and route a Question before topology is accepted.
