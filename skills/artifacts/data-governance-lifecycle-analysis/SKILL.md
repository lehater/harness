---
name: data-governance-lifecycle-analysis
description: "Use when persisted, transmitted, derived or operational data has material collection, purpose, sensitivity, retention, deletion, anonymization, archival, disclosure, provenance or lifecycle questions before implementation."
---

# Data Governance Lifecycle Analysis

## Trigger

Use when implementation handles data whose allowed existence/use/lifetime is not completely implied by accepted Product/Domain/Security/Data/Operability/Policy knowledge.

## Inputs

Accepted Product, Domain, Application, Interface, Data, Security, Operability, Quality and Engineering Policy knowledge as applicable.

## Read boundary

Accepted design/policy is authority. Existing tables, ORM models, logs, backups, caches, analytics, framework defaults and production code are not proof that collection, retention or disclosure is intended.

## Procedure

1. Inventory each material data class across authoritative state, derived state, evidence, cache and diagnostics.
2. Identify semantic owner and accepted purpose.
3. Identify whether persistence/derivation is necessary or merely convenient.
4. Identify sensitivity/security handling.
5. Identify domain lifecycle/history requirements.
6. Identify external policy/obligation, applicability and provenance where known.
7. Derive allowed collection, use, disclosure, retention and disposition.
8. Trace material copies: primary store, replicas, cache, exports, logs, backups, analytics.
9. Classify COVERED, NOT_APPLICABLE, DEFERRED_NONBLOCKING or QUESTION.
10. Route missing semantics; do not invent policy.
11. Derive externally visible Interface obligations.
12. Derive Verification/Test and Operability evidence.
13. Only then permit physical purge/archive/redaction mechanics.

## Ownership routing

- product need/purpose -> Product;
- data meaning/history/lifecycle -> Domain/Application;
- sensitivity/access/protection -> Security;
- physical representation/copy/delete/archive realization -> Data/System;
- external disclosure/export/delete behavior -> Interface derived upstream;
- diagnostic evidence and redaction -> Operability constrained by Security/Policy;
- normative engineering/external policy constraint -> Engineering Policy or the applicable semantic Authority;
- proof -> Verification/Test.

## Stop conditions

Create a blocking Question when implementation would otherwise decide:
- whether data is needed;
- whether derived data may be durable;
- secondary use/disclosure;
- history survival after retirement;
- material retention period/event;
- erase/anonymize/archive/tombstone semantics;
- backup/cache/replica disposition;
- provenance lifetime;
- sensitive data in logs/diagnostics;
- external obligation applicability.

## Implementation freedoms

After closure, implementation may choose table/partition layout, purge-job structure, archival technology, batch scheduling inside accepted bounds, permitted tombstone representation, lineage storage format and redaction mechanism satisfying accepted constraints.

## Output contract

Produce the smallest project-native coverage artifact/review containing:
- data class/copy;
- semantic owner;
- accepted purpose;
- authoritative/derived/evidence status;
- sensitivity handling;
- lifecycle/history rule;
- policy/obligation provenance if applicable;
- retention/disposition rule;
- state and reopening condition;
- Questions;
- Interface obligations;
- implementation freedoms;
- Verification/Test obligations;
- Operability obligations.

The analysis artifact is not automatically a Capability.

## Registration

Current evidence rejects generic DATA-GOVERNANCE-DESIGN, PRIVACY-DESIGN and RETENTION-DESIGN Authorities. A future independently owned policy-provenance boundary requires a separate atomicity test.


## Acceptance checks

- every material concern traces to accepted scope and an owning Authority;
- unresolved semantics are routed as Questions rather than invented;
- the analysis/design does not duplicate upstream semantic ownership;
- implementation freedoms remain explicit after closure.


## Human projection

Prefer the smallest project-native coverage/contract view that shows scope, accepted decisions, routed gaps, evidence obligations and implementation freedoms.
