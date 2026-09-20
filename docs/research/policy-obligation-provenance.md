# Policy obligation provenance and applicability research

Status: research conclusion. This study tests the meta-gap exposed by security, data-governance and engineering-policy research.

## Research question

Harness can represent project-selected ENGINEERING-POLICY and security-specific applicability analysis. What owns externally imposed or organizational obligations such as law/regulation, contract, licensing, privacy policy, records retention, accessibility mandate, corporate standard or platform policy?

The key distinction is between:

1. **source obligation** — an authoritative external/internal normative statement;
2. **applicability** — whether and why it applies to this product/scope/data/jurisdiction/runtime;
3. **derived engineering constraint** — the concrete requirement imposed on an existing semantic owner;
4. **realization/control** — how the system satisfies that constraint;
5. **evidence** — how compliance is demonstrated.

## Core observation

An obligation source does not become owner of product/domain/security/data semantics. Conversely, an engineering Authority must not silently reinterpret legal, contractual or organizational text as if it were self-authored product truth.

The missing concern is therefore not "Compliance Design". It is traceable normative input: provenance, applicability, interpretation boundary and routing into existing Authorities.

## Candidate models

### A. Expand ENGINEERING-POLICY to own every obligation

Rejected. ENGINEERING-POLICY currently owns project-selected cross-cutting engineering discipline: dependency rules, SOLID/KISS/YAGNI, architecture/implementation constraints. A tax-retention rule, privacy-purpose restriction, accessibility mandate or third-party license condition is not an engineering-design principle.

Expanding it would destroy semantic cohesion and turn it into a miscellaneous policy bucket.

### B. Create COMPLIANCE-DESIGN

Rejected. "Compliance" aggregates unrelated obligations by their external origin. The actual engineering decisions still belong to Product, Interface, Security, Data, Domain, Quality, Change Transition, etc.

### C. Create POLICY/OBLIGATION-ANALYSIS Authority

Supported conditionally, if the project has material normative sources whose applicability and derivation need independent accepted evidence.

This Authority would not own the downstream requirement. It would own **obligation coverage analysis**:
- source identity/version/provenance;
- applicability/non-applicability/deferment with rationale;
- scoped interpretation/derived constraint;
- routing to semantic owner;
- coverage status/evidence expectation;
- reopening conditions.

This shape is analogous to SECURITY-ANALYSIS: analysis/coverage can have an independent lifecycle without owning the decisions it constrains.

## Atomicity test — OBLIGATION-ANALYSIS

### Semantic cohesion — PASS

All decisions concern one thing: which normative obligations apply to the selected engineering scope, what constrained meaning is derived from them, and where resolution is owned. It does not decide the resolution.

### Independent change — PASS

An obligation source/version, jurisdiction, contract, organizational policy or applicability interpretation can change while product/domain/system design remains temporarily unchanged but becomes stale or blocked. Conversely, downstream realization can change while the obligation analysis remains stable.

### Public producer/consumer contract — PASS

The Authority can provide accepted obligation/applicability coverage to Product, Domain, Security, Interface, Data, Quality, System, Change Transition, Implementation and Verification. Material unresolved derivation is routed as Questions.

## Boundary with ENGINEERING-POLICY

ENGINEERING-POLICY:
- project-selected engineering discipline;
- normative rules for how accepted engineering knowledge may be realized;
- examples: dependency direction, forbidden architectural shortcuts, required design principles.

OBLIGATION-ANALYSIS:
- externally or organizationally imposed normative sources;
- establishes applicability and derives/routs constraints;
- does not own engineering discipline or semantic resolution.

A corporate engineering standard can land in either:
- if the project explicitly adopts it as engineering discipline -> ENGINEERING-POLICY;
- if it is imposed as a separately governed obligation requiring applicability/provenance/coverage -> OBLIGATION-ANALYSIS.

## Boundary with SECURITY-ANALYSIS

SECURITY-ANALYSIS owns threat/control/applicability coverage for security concerns against accepted design.

OBLIGATION-ANALYSIS owns normative-source applicability. If a regulation/contract creates a security requirement:
1. OBLIGATION-ANALYSIS establishes the normative obligation and routes the derived security constraint;
2. SECURITY-ANALYSIS evaluates threat/control coverage against the accepted security design;
3. SECURITY-ARCHITECTURE owns required trust/protection/enforcement changes.

Do not duplicate the same coverage analysis in both.

## Obligation states

Use the same disciplined shape proven by security analysis:
- COVERED — applicable obligation has accepted routed constraint/resolution/evidence;
- NOT_APPLICABLE — explicit rationale;
- DEFERRED_NONBLOCKING — valid reason plus reopening condition;
- QUESTION — material applicability/interpretation/routing gap.

"Unknown" or silence is not NOT_APPLICABLE.

## Required provenance

A material obligation record should identify at minimum:
- source identity;
- source kind;
- version/date/effective period when material;
- authoritative locator/reference;
- applicability scope;
- rationale;
- derived constraint;
- owning Authority;
- status;
- evidence/verification expectation;
- reopening condition where applicable.

Harness Core need not introduce a first-class Obligation entity yet. This can be represented in a CanonicalArtifact owned by the conditional Authority, with Questions and Capabilities using existing Core primitives.

## Validation — Nutrition Management

Accepted Nutrition artifacts contain several policy-like things but they are not the same category.

The Engineering Design Policy is clearly project-selected engineering discipline: Clean Architecture dependency direction, SOLID obligations, KISS/YAGNI, forbidden speculative patterns. This belongs exactly in ENGINEERING-POLICY.

The implementation ADR also records technology/license-relevant choices such as Python, SQLite, SQLAlchemy, Alembic, SCIP/PySCIPOpt and pytest, but accepted design currently contains no independently governed licensing/compliance applicability artifact. The presence of open-source dependencies alone does not authorize Harness to invent license obligations.

If distribution, commercial use, source attribution, nutrition-data licensing or jurisdictional privacy obligations become material, a separate obligation analysis would have independent value and would route resulting constraints to Product/Data/Security/Implementation/Change Transition as appropriate.

Result: OBLIGATION-ANALYSIS is legitimately NOT_APPLICABLE for the current accepted slice unless a material normative source is introduced. This supports conditionality.

## Validation — NAPMS

NAPMS current accepted implementation readiness contains authorization, session, persistence, history and export semantics but does not establish a general legal/compliance owner. Existing design must not infer regulatory requirements from the presence of actors, passwords, provenance or policy history.

Security requirements remain Security-owned. Domain retention such as retained RuleChange history remains Domain/Application/Data-owned.

If an organizational security baseline, records-retention mandate, customer contract, privacy policy, accessibility mandate or deployment-jurisdiction rule is introduced as normative input, its source/applicability lifecycle can change independently from the affected design and needs traceable routing.

Result: again conditional, not baseline.

## Synthetic regulated SaaS case

Assume:
- EU customer personal data;
- contractual 7-year invoice retention;
- corporate security baseline;
- accessibility requirement;
- third-party library license notice obligation.

One generic "Compliance Design" cannot coherently resolve them.

OBLIGATION-ANALYSIS can instead record/rout:
- privacy purpose/erasure constraint -> Product/Domain/Data/Security;
- invoice retention -> Product/Domain/Data;
- security baseline -> Security Analysis/Architecture;
- accessibility -> Product/Interface/Quality/Verification;
- license notice/distribution constraint -> Engineering Policy/Implementation/Release as applicable.

Its independent product is the coverage/routing/provenance matrix, not the resolution itself.

## Failure experiments

1. **Source changes** — regulation v1 -> v2. Obligation analysis becomes stale and identifies affected capabilities without itself editing Product/Data.
2. **Jurisdiction changes** — previously N/A obligation becomes applicable. Applicability change can block downstream work before implementation defaults fill the gap.
3. **Conflicting obligations** — retention requires preservation while privacy request suggests erasure. Analysis must expose conflict as Questions to owners; it must not invent precedence.
4. **Ambiguous legal text** — engineering agent must not make legal interpretation silently. Record a Question requiring authoritative policy/legal resolution.
5. **Control exists accidentally** — current encryption or deletion job does not prove the obligation is COVERED unless traced to accepted requirement/evidence.
6. **Obligation removed** — downstream constraints do not disappear automatically; affected owners decide whether requirements remain product policy.

## Verdict

Create conditional **OBLIGATION-ANALYSIS** Authority.

Proposed responsibility:

> Own provenance, applicability and coverage of externally or organizationally imposed normative obligations against accepted engineering scope, derive and route material constraints to their semantic owners, and expose unresolved interpretation or coverage as Questions without owning the constrained product/design semantics.

Applicability:

> Instantiate when material law, regulation, contract, license, organizational policy, platform mandate or other independently governed normative source must be traced into engineering decisions.

Do not create COMPLIANCE-DESIGN, LEGAL-DESIGN, PRIVACY-POLICY-DESIGN or LICENSE-DESIGN from current evidence.

## Consumers

- Product/Domain consume routed behavioral/lifecycle constraints.
- Security consumes security obligations.
- Interface/Quality consume accessibility/disclosure/quality constraints.
- Data consumes accepted persistence/disposition constraints.
- System/Change Transition consume deployment/jurisdiction/transition constraints.
- Implementation consumes accepted realization constraints only after owner resolution.
- Verification consumes obligation-to-evidence traceability.

## No Core change

Existing primitives are sufficient:
- Authority = OBLIGATION-ANALYSIS;
- CanonicalArtifact = obligation/applicability coverage matrix;
- Question = unresolved applicability/interpretation/routing;
- Capability = accepted obligation coverage when a consumer requires it;
- prerequisites = accepted scope/design/policy sources as applicable.

A first-class Obligation entity is not justified until multiple projects demonstrate consumers needing obligation-level graph operations that CanonicalArtifact + Question + Capability cannot express.
