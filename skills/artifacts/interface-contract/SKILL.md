---
name: interface-contract
description: "Use for actionable CREATE work requiring a supported external interface contract such as CLI, HTTP/API, file exchange or user interaction. Define representation and interaction semantics from accepted product/domain/architecture truth without becoming domain or persistence authority."
---

# Interface Contract

## Trigger

Use when actionable grouped artifact work has `knowledge_kind:
interface-contract` and the Interface Design Authority must define a supported
external machine/user boundary.

## Inputs

- actionable grouped work and Interface Design Authority;
- accepted Product Requirements/acceptance semantics;
- accepted domain/application semantics needed at the boundary;
- accepted System/Security Architecture constraints.

## Read boundary

Read only canonical sources needed to establish:

- supported operations/interactions;
- input/output representations;
- identities/references crossing the boundary;
- success, rejection, unresolved and operational error semantics;
- compatibility/versioning constraints when material.

## Procedure

1. Confirm upstream behavior and architecture are accepted.
2. Define the supported boundary from consumer-visible needs, not internal object
   structure.
3. Define operations/commands/interactions and required inputs.
4. Define outputs and explicit failure/outcome semantics.
5. Preserve owner-defined identity, time, unknown and provenance semantics where
   they cross the boundary.
6. Define representation/serialization conventions only as needed for an
   interoperable contract.
7. Do not expose peer-private domain models merely because they exist internally.
8. Do not decide persistence or implementation decomposition.
9. Route unresolved product/domain/security semantics to the owning Authority.
10. Produce the project-native contract, validate it when a deterministic
    validator exists, semantically accept and register it.

## Stop conditions

Stop when:

- accepted behavior is insufficient to decide an externally visible outcome;
- a domain identity/invariant is unclear;
- security/admission semantics required by the boundary are unresolved;
- selecting an interface would force an upstream architecture/product decision.

## Output contract

Use the natural target format: OpenAPI, CLI contract, schema, UI interaction
contract, file-format contract or another project-native representation.

Do not force all interface forms into one Harness schema.

## Acceptance checks

- every operation/interaction traces to accepted product behavior;
- domain semantics are preserved rather than reinterpreted;
- error/unresolved outcomes are explicit where material;
- internal implementation details do not leak without contract value;
- supported interface surface is sufficient for downstream implementation and
  verification.
- semantic completeness is subject-aware: every externally required operation/interaction is materialized or explicitly disposed upstream;
- every normative input/output/error/compatibility decision from the accepted interface requirements has a corresponding contract realization or explicit N/A disposition;
- a machine contract consumed by a human-interface contract must be checked for operation/read-model compatibility, not merely co-existence;

## Registration

Register accepted interface artifact(s) under Interface Design and provide all
grouped capabilities genuinely materialized by them.

## Human projection

Depends on project-native format; generated API/UI documentation is a projection,
not a second source of truth.
