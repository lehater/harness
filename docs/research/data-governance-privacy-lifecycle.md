# Data governance / privacy / retention / lifecycle ownership research

Status: research conclusion. No Harness Core or canonical Authority change is made by this document alone.

## Research question

Do data governance, privacy, classification, retention, deletion, provenance and lifecycle form an atomic engineering Authority, or are they policies/constraints owned by existing Product, Domain, Security, Data, Quality and Engineering Policy boundaries?

The study separates:

- **data meaning/ownership** — what information exists and which domain owns it;
- **purpose/allowed use** — why a class of information may be collected, retained, disclosed or derived;
- **classification/sensitivity** — handling category that constrains protection and exposure;
- **retention/disposition** — how long authoritative/derived/evidence data must or may exist and what ends its lifecycle;
- **subject/user lifecycle** — domain meaning of deactivate, erase, anonymize, revoke, archive;
- **physical deletion/archival** — persistence realization of accepted lifecycle;
- **protection/access** — security enforcement;
- **provenance/lineage** — evidence about origin/transformation;
- **legal/regulatory applicability** — external obligation and policy provenance.

## External coverage lenses

Privacy engineering guidance consistently separates purpose and minimization from technical storage. Security classification constrains handling but does not define business meaning. Retention schedules constrain data lifecycle but physical deletion alone cannot decide whether a record must remain for product, audit, safety or legal reasons.

These are coverage lenses, not Harness ontology.

## Decision ownership map

| Decision | Owner |
| --- | --- |
| Whether product needs a datum | Product/Domain |
| Meaning and authoritative owner of datum | Domain |
| Allowed product purpose/use/disclosure | Product/Domain; external policy may constrain |
| Whether data is sensitive/security-relevant | Security Analysis/Architecture using accepted data meaning |
| Access/admission/protection controls | Security Architecture |
| Required minimization of collected/derived data | Product/Domain constrained by Security/Policy |
| Domain lifecycle: active/retired/revoked/deleted/anonymized meaning | Domain/Application |
| Required retention/disposition period | Product/Engineering Policy when policy-driven; Domain where business semantics require history |
| Physical representation of lifecycle/retention | Data Design |
| Backup/archive copy handling | System/Data/Security constrained by retention policy |
| Provenance required for business/evidence semantics | Domain/Product |
| Physical lineage/provenance representation | Data Design |
| Diagnostic data minimization/redaction | Operability constrained by Security/Policy |
| External interface disclosure/export/erase contract | Interface derived from Product/Domain/Policy |
| Regulatory applicability/provenance | Engineering Policy/Security Analysis according to nature of obligation |
| Proof of deletion/retention/access behavior | Verification/Test |

## Key distinctions

### Persistence is not authority for retention

A database table can represent deletion, tombstones or history, but Data Design cannot invent whether information is allowed or required to survive.

### Privacy is not synonymous with security

Confidentiality/access control answers who may access data. Privacy/purpose/minimization additionally asks whether data should be collected, used, derived, retained or disclosed at all. Encryption cannot justify unnecessary collection.

### Domain deletion is not necessarily physical erasure

"Delete account", "retire policy", "revoke authority", "erase personal data" and "purge diagnostic record" have different semantics. The owning domain/product/policy must define the lifecycle outcome before Data/System choose physical realization.

### Provenance has multiple semantic owners

Source provenance can be business/domain evidence, security/audit evidence, or operational diagnostics. A generic governance owner would incorrectly absorb those meanings.

## Atomicity test — candidate DATA-GOVERNANCE-DESIGN

### Semantic cohesion — FAIL

The candidate mixes business purpose, domain lifecycle, external policy, security classification, persistence realization, audit/evidence and operations. They share a subject (data) but not one semantic invariant.

### Independent change — FAIL

Retention policy can change without changing domain meaning. Physical archival can change without changing retention obligation. Security classification can change handling without changing business lifecycle. Domain history requirements can change independently of privacy policy.

### Public producer/consumer contract — FAIL as one Authority

Consumers need distinct accepted contracts: data meaning, allowed purpose, retention constraint, security handling, persistence realization, interface behavior and evidence. A single Governance Design artifact would aggregate rather than own them.

## Verdict

**Do not create DATA-GOVERNANCE-DESIGN, PRIVACY-DESIGN or RETENTION-DESIGN Authorities from current evidence.**

Data governance is a cross-Authority closure problem plus policy provenance.

However, the analysis exposes a separate meta-question already noted in the coverage-gap study: Harness needs a reliable way to represent **externally imposed policy/obligation provenance and applicability**. Existing ENGINEERING-POLICY may own normative engineering constraints, while SECURITY-ANALYSIS owns security-control applicability, but privacy/legal/business retention obligations are broader than security. This does not yet justify a new Authority; it requires a separate policy-provenance atomicity study.

## Pre-code blocking Questions

Implementation must not invent:
- whether a datum is necessary for an accepted product purpose;
- whether derived data may be persisted;
- whether data may be used for a secondary purpose;
- whether history must survive domain retirement;
- retention duration/event when material;
- erase vs anonymize vs archive vs tombstone semantics;
- treatment of backups/caches/replicas after disposition;
- whether provenance itself must be retained;
- disclosure/export semantics;
- whether diagnostic/log data may contain sensitive/business data;
- which external obligation requires the constraint and when it applies.

## Implementation freedoms

After semantic/policy closure:
- table/partition layout;
- purge job implementation;
- archival storage product;
- encryption mechanism within accepted Security constraints;
- batch size/schedule inside accepted retention bounds;
- tombstone representation if lifecycle semantics permit;
- index strategy;
- lineage storage format;
- log redaction implementation satisfying accepted requirements.

## Validation — Nutrition Management

Accepted Nutrition requirements deliberately contain data with potentially sensitive real-world meaning: member date of birth, sex, height, weight and activity inputs. The accepted Product Requirements define why those inputs exist: deriving household nutrition targets.

Accepted Data Design persists the current member profile and explicitly does **not** persist Planning Input Snapshots or plan history for MVP. Introducing saved plans/replay snapshots/planning tables requires an upstream requirement.

This is strong evidence for the ownership split:
- Product/Domain justify collection and meaning;
- Data Design represents accepted state and refuses to manufacture extra durable history;
- any confidentiality/access classification belongs to Security;
- retention/deletion semantics are currently not established by the cited accepted artifacts and must not be invented by SQLite/Alembic implementation.

A generic Data Governance Authority would duplicate Product/Domain/Data rather than own a residual boundary.

Material future Questions include member-profile deletion/retention, source provenance lifetime and whether imported observations/history are retained after replacement.

## Validation — NAPMS

Accepted NAPMS persistence contains several distinct lifecycle classes:
- append-only published InteractionContractRevision;
- retained Policy decision history;
- Active/Retired ComponentDeployment;
- Active/Retired PolicyRule with retirement provenance;
- temporal AuthorityAssignment;
- Actor credentials/state;
- general provenance records.

These retention/lifecycle choices are not one governance policy. They express different domain/application invariants. For example, policy decision history is retained because current effectiveness must not erase RuleChange history, while deployment and policy rules have explicit retirement states.

Therefore:
- Domain/Application own history and retirement meaning;
- Data Design realizes them;
- Security owns password/credential protection and access;
- Operability owns runtime diagnostic evidence;
- external policy may add constraints but cannot replace domain ownership.

Again, no residual Data Governance Authority appears.

## Synthetic case

Assume a SaaS product stores:
- customer profile;
- invoices;
- security audit trail;
- application logs;
- derived recommendation features;
- backups.

A user requests account deletion.

There is no single correct "delete all rows" rule:
- profile may require erase/anonymization;
- invoices may have independently required retention;
- security audit may require integrity-preserving retention with restricted access;
- logs may need redaction/expiry;
- derived features may need deletion/recomputation;
- backups may expire on a bounded schedule rather than immediate mutation.

The decision set decomposes by purpose/owner/obligation and then converges into an executable disposition plan. This strongly rejects a generic data-governance semantic owner while demonstrating the value of a closure analysis.

## Closure algorithm

For each persisted, transmitted, derived or operational data class:

1. identify semantic owner and accepted purpose;
2. identify authoritative vs derived/evidence/cache status;
3. identify applicable sensitivity/security classification;
4. identify domain lifecycle/history requirement;
5. identify external policy/obligation and provenance if any;
6. derive allowed collection/use/disclosure/retention/disposition;
7. identify copies: primary, replicas, cache, export, logs, backups, analytics;
8. classify COVERED, NOT_APPLICABLE, DEFERRED_NONBLOCKING or QUESTION;
9. route missing decisions to Product/Domain/Security/Data/Operability/Engineering Policy;
10. derive Interface behavior where externally observable;
11. derive Verification/Test obligations;
12. allow physical deletion/archive/redaction mechanics only after closure.

## Priority findings

### P0

1. Data Design must not invent retention or purpose.
2. Security protection does not answer whether collection/use/retention is justified.
3. Domain retirement/deletion and physical erasure are different decisions.
4. Durable derived data requires accepted purpose/ownership, not convenience.

### P1

1. Generic DATA-GOVERNANCE-DESIGN fails Authority atomicity.
2. A reusable governance/privacy/lifecycle closure analysis is justified.
3. Policy provenance/applicability remains a distinct unresolved meta-gap and deserves its own research.
4. No Harness Core change is justified by this study.

## Canonicalization recommendation

Add a reusable data-governance-lifecycle analysis skill and catalog principles preventing Data/Security/Implementation defaults from inventing collection, purpose, retention or disposition semantics. Do not add a new Authority.
