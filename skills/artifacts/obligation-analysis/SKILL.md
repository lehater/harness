---
name: obligation-analysis
description: "Use when law, regulation, contract, license, organizational policy, platform mandate or another independently governed normative source may impose material engineering constraints."
---

# Obligation Analysis

## Responsibility

Establish normative-source provenance, applicability and coverage, derive constrained engineering meaning, and route resolution to the Authority that owns it. Never become the semantic owner of the routed requirement.

## Trigger

Use only when a material independently governed normative source exists or its applicability is a blocking Question. Do not instantiate merely because software could theoretically be regulated.

## Inputs

Accepted product/design scope; identified normative sources; authoritative policy/legal interpretation where needed; existing Engineering Policy, Security Analysis and semantic design artifacts.

## Procedure

1. Identify source identity, kind, version/effective period and authoritative reference.
2. Define the product/system/data/jurisdiction/distribution scope being tested.
3. Determine applicability using authoritative interpretation; if interpretation is ambiguous, create a Question rather than guessing.
4. For applicable obligations, derive the smallest engineering constraint that can be routed without taking over semantic ownership.
5. Route to Product, Domain, Security, Interface, Data, Quality, System, Change Transition, Engineering Policy or other existing owner.
6. Record COVERED, NOT_APPLICABLE, DEFERRED_NONBLOCKING or QUESTION.
7. For deferred items record reopening condition.
8. Record evidence/verification expectation.
9. Detect conflicts between obligations or between obligation and accepted design; route Questions rather than invent precedence.
10. Re-evaluate affected coverage when source/version/jurisdiction/scope changes.

## Boundaries

- ENGINEERING-POLICY owns project-selected engineering discipline.
- SECURITY-ANALYSIS owns security threat/control coverage.
- OBLIGATION-ANALYSIS owns normative-source applicability and routing.
- Semantic Authorities own the resulting product/domain/security/interface/data/quality decisions.
- Verification owns proof.

## Stop conditions

Do not allow downstream implementation to invent:
- whether an ambiguous obligation applies;
- legal/policy interpretation;
- precedence between conflicting obligations;
- retention/disclosure/accessibility/license/security behavior not accepted by its owner;
- evidence sufficient to claim coverage.

## Output contract

For each material obligation record:
- source identity/kind;
- version/effective period when material;
- authoritative reference;
- applicability scope;
- applicability rationale;
- derived constraint;
- routed owning Authority;
- state;
- evidence expectation;
- reopening condition where applicable;
- Questions/conflicts.

The artifact may provide an obligation-coverage Capability only when a concrete consumer requires independently accepted coverage evidence.

## Core mapping

Use existing Harness primitives: Authority, CanonicalArtifact, Question, Capability and prerequisites. Do not introduce a first-class Obligation entity without demonstrated graph-level consumer need.


## Read boundary

Accepted canonical design is authority. Existing implementation, runtime configuration, tooling defaults and observed realization are evidence only; they do not invent missing engineering semantics.


## Acceptance checks

- every material concern traces to accepted scope and an owning Authority;
- unresolved semantics are routed as Questions rather than invented;
- the analysis/design does not duplicate upstream semantic ownership;
- implementation freedoms remain explicit after closure.


## Registration

Register only according to the boundary established by this skill and its validated research; do not create additional Authorities from mechanism or subject names alone.


## Human projection

Prefer the smallest project-native coverage/contract view that shows scope, accepted decisions, routed gaps, evidence obligations and implementation freedoms.
