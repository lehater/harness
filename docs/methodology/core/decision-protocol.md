# Decision and unknown protocol

Every consequential statement used for design is classified along two independent axes.

## Semantic owner

- S0 Problem / Evidence — need, observation, desired outcome, problem boundary.
- S1 Requirement — externally meaningful behavior, constraint or quality expectation.
- S2 Domain Semantics — meaning, identity, lifecycle, invariant and semantic ownership.
- S3 Architecture — realization structure and technical contracts/constraints.
- S4 Implementation — concrete executable detail not already constrained upstream.

## Status

- accepted/known — supported by canonical target-project truth or explicit owner decision;
- constraint — mandatory limitation downstream work must satisfy;
- proposal — candidate choice, not accepted;
- hypothesis — belief to validate;
- unknown — insufficient evidence/decision;
- conflict — authoritative sources disagree.

Stakeholder statements, examples, goals, workarounds and risks are evidence, not automatically requirements or domain truth.

Never represent a proposal, hypothesis or unknown as accepted truth because it makes implementation convenient.

For a material unknown: inspect canonical target-project evidence, identify the owning layer, resolve with evidence/focused owner decision or explicit non-blocking deferral, and keep the affected gate closed while the unknown is blocking.

Put accepted results in the smallest project-local canonical owner. Use a project ADR when consequential rationale/alternatives/supersession need durable history. Chat transcripts are never canonical decisions.
